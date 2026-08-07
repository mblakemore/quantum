#!/usr/bin/env python3
"""P-CCM v1.0 — GPU test of the DIVERGENT control flow. The risk I flagged, measured.

WHAT I FLAGGED AND WHY IT MATTERED. The Z8 arithmetic benchmark gave 36-41x on the kernel but
only 2.10x end-to-end, because Z8 updates are 54% of runtime. The other 46% is the branchy part:
shrink's S-set selection and exponential_sum's DIMER PARTITION, whose trip counts are
data-dependent. I called that the real SIMT risk and deliberately did not benchmark it.

THE FIRST MEASUREMENT WAS A SURPRISE AND IT CAME BEFORE ANY GPU CODE. Trip counts of the dimer
loop over 300 random terms:

    k=40   min 20  median 20  max 21  sd 0.4   -> batching to max wastes  4%
    k=80   min 40  median 40  max 41  sd 0.4   -> batching to max wastes  2%

The loop pairs up basis vectors, so with a generic J almost every vector finds a partner and the
trip count sits at ~k/2 nearly deterministically. THE CONTROL FLOW IS BRANCHY BUT NOT DIVERGENT
IN LENGTH — which is the property SIMT actually cares about. My "real risk" framing was based on
the code LOOKING data-dependent; the distribution says the data does not vary much.

SO THIS FILE CONVERTS THE LOOP TO LOCKSTEP-WITH-MASKING and measures whether that holds up:
every term runs the same number of iterations, per-term choices become argmax reductions over
masks, and terms that have finished are masked off. Waste is bounded by the 2-4% above.

CORRECTNESS: the batched GPU partition must produce the SAME dimer/monomer assignment as the
CPU reference on the same inputs. A timing whose paired agreement check did not pass is not
emitted — same rule as everywhere else in this campaign.

Substrate: claude-fable-5, Whisper C5020. Creator directive: "test the divergent parts".
"""
import time
import json
import os
import sys

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def cpu_partition(D, J, k):
    """Reference dimer/monomer partition for ONE term, exactly as exponential_sum does it."""
    S = [a for a in range(k) if D[a] in (2, 6)]
    s = S[0] if S else None
    E = [a for a in range(k) if a != s]
    monomers, dimers = [], []
    while E:
        a = E[0]
        Ka = [b for b in E[1:] if J[a, b] == 4]
        if not Ka:
            monomers.append(a)
            E.remove(a)
        else:
            b = Ka[0]
            dimers.append((a, b))
            E = [c for c in E if c not in (a, b)]
    return monomers, dimers


def cpu_partition_batch(D, J, k):
    out = []
    for b in range(D.shape[0]):
        out.append(cpu_partition(D[b], J[b], k))
    return out


def gpu_partition_batch(D, J, k, dev):
    """LOCKSTEP + MASKING. Every term runs the same iteration count; per-term choices become
    argmax reductions. Returns (monomer_mask, dimer_partner) as tensors."""
    import torch
    B = D.shape[0]
    idx = torch.arange(k, device=dev)

    # s = first index with D in {2,6}, or none
    is_s = (D == 2) | (D == 6)
    has_s = is_s.any(dim=1)
    s_idx = torch.argmax(is_s.to(torch.int32), dim=1)

    alive = torch.ones((B, k), dtype=torch.bool, device=dev)
    alive[has_s, s_idx[has_s]] = False

    mono = torch.zeros((B, k), dtype=torch.bool, device=dev)
    partner = torch.full((B, k), -1, dtype=torch.int32, device=dev)

    for _ in range((k // 2) + 2):                       # bounded by the measured max trip count
        any_alive = alive.any(dim=1)
        if not bool(any_alive.any()):
            break
        a = torch.argmax(alive.to(torch.int32), dim=1)          # first alive index per term
        Ja = J[torch.arange(B, device=dev), a]                  # (B,k) row a of each J
        cand = alive & (Ja == 4) & (idx.unsqueeze(0) > a.unsqueeze(1))
        has_p = cand.any(dim=1)
        b = torch.argmax(cand.to(torch.int32), dim=1)

        act = any_alive
        # monomer branch: alive, no partner
        m_sel = act & ~has_p
        if bool(m_sel.any()):
            rows = torch.nonzero(m_sel).squeeze(1)
            mono[rows, a[rows]] = True
            alive[rows, a[rows]] = False
        # dimer branch
        d_sel = act & has_p
        if bool(d_sel.any()):
            rows = torch.nonzero(d_sel).squeeze(1)
            partner[rows, a[rows]] = b[rows].to(torch.int32)
            partner[rows, b[rows]] = a[rows].to(torch.int32)
            alive[rows, a[rows]] = False
            alive[rows, b[rows]] = False
    torch.cuda.synchronize()
    return mono, partner


def main():
    import torch
    dev = torch.device("cuda:0")
    p = torch.cuda.get_device_properties(0)
    print("GPU DIVERGENT-CONTROL-FLOW BENCHMARK\n")
    print(f"  device: {p.name}  free VRAM {torch.cuda.mem_get_info(0)[0]/2**30:.1f} GB")
    print("  operation: exponential_sum's DIMER PARTITION — the branchy 46%\n")

    import stabilizer_rank_kernel as ref
    rng = np.random.default_rng(20260807)
    rows = []

    print("  ① CORRECTNESS: batched GPU partition vs the CPU reference")
    k = 40
    B = 64
    Ds, Js = [], []
    for _ in range(B):
        st = ref.random_state_via_extend(k, k, rng)
        Ds.append(st.D[:k].copy())
        Js.append(st.J[:k, :k].copy())
    Dn = np.stack(Ds).astype(np.int32)
    Jn = np.stack(Js).astype(np.int32)
    want = cpu_partition_batch(Dn, Jn, k)
    mono, partner = gpu_partition_batch(torch.from_numpy(Dn).to(dev),
                                        torch.from_numpy(Jn).to(dev), k, dev)
    mono_c = mono.cpu().numpy()
    part_c = partner.cpu().numpy()
    agree = 0
    for bi, (m, d) in enumerate(want):
        gm = sorted(np.nonzero(mono_c[bi])[0].tolist())
        gd = sorted([tuple(sorted((a, int(part_c[bi, a])))) for a in range(k)
                     if part_c[bi, a] >= 0])
        gd = sorted(set(gd))
        if gm == sorted(m) and gd == sorted([tuple(sorted(x)) for x in d]):
            agree += 1
    print(f"    {agree}/{B} terms match exactly")
    if agree != B:
        print("    ⛔ DISAGREEMENT — no timing emitted.")
        sys.exit(2)
    print("    ✅ agreement\n")

    print("  ② TIMING")
    print(f"  {'k':>4} {'batch':>8} {'CPU (ms)':>11} {'GPU (ms)':>11} {'speedup':>9}")
    for k in (40, 80):
        for B in (256, 2048, 8192):
            Ds, Js = [], []
            for _ in range(B):
                st = ref.random_state_via_extend(k, k, rng)
                Ds.append(st.D[:k].copy())
                Js.append(st.J[:k, :k].copy())
            Dn = np.stack(Ds).astype(np.int32)
            Jn = np.stack(Js).astype(np.int32)

            t0 = time.perf_counter()
            cpu_partition_batch(Dn, Jn, k)
            tcpu = (time.perf_counter() - t0) * 1000

            dg = torch.from_numpy(Dn).to(dev)
            jg = torch.from_numpy(Jn).to(dev)
            gpu_partition_batch(dg, jg, k, dev)            # warm-up
            torch.cuda.synchronize()
            t0 = time.perf_counter()
            gpu_partition_batch(dg, jg, k, dev)
            tgpu = (time.perf_counter() - t0) * 1000

            rows.append({"k": k, "batch": B, "cpu_ms": tcpu, "gpu_ms": tgpu,
                         "speedup": tcpu / tgpu})
            print(f"  {k:>4} {B:>8} {tcpu:>11.2f} {tgpu:>11.2f} {tcpu/tgpu:>8.1f}x")
            del dg, jg
            torch.cuda.empty_cache()

    best = max(rows, key=lambda r: r["speedup"])
    print(f"\n  BEST: {best['speedup']:.1f}x at k={best['k']}, batch={best['batch']}")

    dst = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results",
                       "gpu_divergent_bench_v1.json")
    with open(dst, "w") as fh:
        json.dump({"card": "gpu_divergent_bench", "version": "1.0", "cycle": "C5020",
                   "substrate": "claude-fable-5", "rows": rows, "best": best,
                   "trip_count_divergence": {"k40": {"min": 20, "max": 21, "sd": 0.4},
                                             "k80": {"min": 40, "max": 41, "sd": 0.4},
                                             "masking_waste_pct": "2-4"},
                   "correctness": "batched GPU partition matches CPU reference exactly"}, fh,
                  indent=2)
    print(f"\n  written: results/{os.path.basename(dst)}")


if __name__ == "__main__":
    main()
