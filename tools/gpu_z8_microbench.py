#!/usr/bin/env python3
"""P-CCM v1.0 — GPU micro-benchmark of the Z8 hot spot. MEASURED, on the real operation.

WHY THIS OPERATION AND NOT THE F2 LAYER. My profile of the bit-packed kernel says the dominant
cost is Z8 quadratic-form arithmetic on k x k matrices, NOT the F2 linear algebra. I had
predicted the opposite this morning ("GF(2) word-packing is worth ~64x") and packing measured
1.28x end-to-end. So this benchmarks what the profiler named, not what I guessed.

WHY BATCHED. The classical arm is chi = 2^(0.23t) INDEPENDENT stabilizer terms — at t=80,
chi = 345,901. Each term carries its own (D, J). The CPU loops over them; a GPU's only real
advantage here is doing B of them at once as a (B, k, k) tensor. THAT is the comparison that
decides whether the card helps, so that is what this measures.

WHAT IT DOES NOT SETTLE, stated up front: the DIVERGENT parts of the algorithm — shrink's
S-set selection and exponential_sum's dimer partition — have data-dependent trip counts and are
the real SIMT risk. This benchmark measures the ARITHMETIC that dominates, under the optimistic
assumption that the control flow can be batched. A good result here is necessary, not sufficient.

DTYPE NOTE: all Z8 values are 0-7, so int32 is ample and is far friendlier to a GPU than int64.
The CPU side uses the same dtype so the comparison is like-for-like.

Substrate: claude-fable-5, Whisper C5020. Creator directive: "install cupy-rocm and run the
micro-benchmark".
"""
import time
import json
import os
import sys

import numpy as np


def cpu_batched_addrow(D, J, tgt_mask, src, reps=1):
    """CPU reference: loop over the batch, apply the sparse add-row update to each term.
    D (B,k) int32, J (B,k,k) int32, tgt_mask (B,k) bool."""
    B, k = D.shape
    for _ in range(reps):
        for b in range(B):
            T = np.nonzero(tgt_mask[b])[0]
            if T.size == 0:
                continue
            Jb = J[b]
            jss = Jb[src, src]
            row_s = Jb[src, :].copy()
            col_s = Jb[:, src].copy()
            D[b, T] = (D[b, T] + D[b, src] + Jb[T, src]) % 8
            Jb[T, :] = (Jb[T, :] + row_s) % 8
            Jb[:, T] = (Jb[:, T] + col_s[:, None]) % 8
            Jb[np.ix_(T, T)] = (Jb[np.ix_(T, T)] + jss) % 8
    return D, J


def cpu_batched_vectorised(D, J, tgt_mask, src, reps=1):
    """FAIR CPU BASELINE. The same tensor formulation as the GPU path, in numpy — NO Python
    loop over terms. My first version looped, which would have flattered the GPU by comparing
    a batched implementation against an unbatched one. That is precisely the weak-baseline
    error the campaign's x1000 turned out to be, and it would have been mine."""
    for _ in range(reps):
        M = tgt_mask.astype(J.dtype)
        jss = J[:, src, src][:, None, None]
        row_s = J[:, src, :][:, None, :]
        col_s = J[:, :, src][:, :, None]
        D += M * (D[:, src][:, None] + J[:, :, src]); D %= 8
        J += M[:, :, None] * row_s; J %= 8
        J += M[:, None, :] * col_s; J %= 8
        J += (M[:, :, None] * M[:, None, :]) * jss; J %= 8
    return D, J


def gpu_batched_addrow(D, J, tgt_mask, src, reps=1):
    """GPU: the whole batch as one set of tensor ops. Same maths, no Python loop over terms."""
    import torch
    for _ in range(reps):
        M = tgt_mask.to(J.dtype)                       # (B,k) 1 where the row is a target
        jss = J[:, src, src].view(-1, 1, 1)            # (B,1,1)
        row_s = J[:, src, :].unsqueeze(1)              # (B,1,k)
        col_s = J[:, :, src].unsqueeze(2)              # (B,k,1)
        D.add_(M * (D[:, src].unsqueeze(1) + J[:, :, src])).remainder_(8)
        J.add_(M.unsqueeze(2) * row_s).remainder_(8)   # E J
        J.add_(M.unsqueeze(1) * col_s).remainder_(8)   # J E^T
        J.add_((M.unsqueeze(2) * M.unsqueeze(1)) * jss).remainder_(8)  # E J E^T
    torch.cuda.synchronize()
    return D, J


def main():
    import torch
    dev = torch.device("cuda:0")
    p = torch.cuda.get_device_properties(0)
    print(f"GPU Z8 MICRO-BENCHMARK\n")
    print(f"  device: {p.name}  {p.total_memory/2**30:.1f} GB  {p.multi_processor_count} CUs")
    print(f"  free VRAM now: {torch.cuda.mem_get_info(0)[0]/2**30:.2f} GB\n")
    print("  operation: the SPARSE add-row Z8 update — the profiler's dominant cost")
    print("  batched over independent stabilizer terms, which is chi's natural shape\n")

    rng = np.random.default_rng(20260807)
    rows = []
    print(f"  {'k':>4} {'batch':>8} {'CPU loop':>11} {'CPU vec':>11} {'GPU':>10} "
          f"{'vs vec':>10} {'vs loop':>10}")
    for k in (40, 80):
        for B in (256, 2048, 16384):
            Dn = rng.integers(0, 8, size=(B, k)).astype(np.int32)
            Jn = rng.integers(0, 8, size=(B, k, k)).astype(np.int32)
            Jn = ((Jn + Jn.transpose(0, 2, 1)) % 8).astype(np.int32)
            Mn = (rng.random((B, k)) < 0.5)
            src = 0

            dc, jc, mc = Dn.copy(), Jn.copy(), Mn.copy()
            t0 = time.perf_counter()
            cpu_batched_addrow(dc, jc, mc, src)
            tcpu_loop = (time.perf_counter() - t0) * 1000
            dv, jv = Dn.copy(), Jn.copy()
            t0 = time.perf_counter()
            cpu_batched_vectorised(dv, jv, Mn, src)
            tcpu = (time.perf_counter() - t0) * 1000

            dg = torch.from_numpy(Dn.copy()).to(dev)
            jg = torch.from_numpy(Jn.copy()).to(dev)
            mg = torch.from_numpy(Mn.copy()).to(dev)
            gpu_batched_addrow(dg, jg, mg, src)                  # warm-up / autotune
            dg = torch.from_numpy(Dn.copy()).to(dev)
            jg = torch.from_numpy(Jn.copy()).to(dev)
            torch.cuda.synchronize()
            t0 = time.perf_counter()
            gpu_batched_addrow(dg, jg, mg, src)
            tgpu = (time.perf_counter() - t0) * 1000

            rows.append({"k": k, "batch": B, "cpu_loop_ms": tcpu_loop, "cpu_vec_ms": tcpu,
                         "gpu_ms": tgpu, "speedup_vs_vectorised": tcpu / tgpu,
                         "speedup_vs_loop": tcpu_loop / tgpu})
            print(f"  {k:>4} {B:>8} {tcpu_loop:>11.2f} {tcpu:>11.2f} {tgpu:>10.2f} "
                  f"{tcpu/tgpu:>9.1f}x {tcpu_loop/tgpu:>9.1f}x")
            del dg, jg, mg
            torch.cuda.empty_cache()

    best = max(rows, key=lambda r: r["speedup_vs_vectorised"])
    print(f"\n  BEST vs a FAIR (vectorised) CPU baseline: {best['speedup_vs_vectorised']:.1f}x "
          f"at k={best['k']}, batch={best['batch']}")
    print(f"  (vs the Python-loop CPU it would read {best['speedup_vs_loop']:.1f}x — "
          f"that comparison is NOT fair and is shown only to expose the difference)")
    print("\n  ⚠️ NECESSARY, NOT SUFFICIENT. This is the ARITHMETIC only. shrink's S-set and")
    print("     exponential_sum's dimer partition have data-dependent trip counts and are the")
    print("     real SIMT risk; a good number here does not settle them.")

    dst = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results",
                       "gpu_z8_microbench_v1.json")
    with open(dst, "w") as fh:
        json.dump({"card": "gpu_z8_microbench", "version": "1.0", "cycle": "C5020",
                   "substrate": "claude-fable-5",
                   "device": {"name": p.name, "cus": p.multi_processor_count,
                              "total_gb": p.total_memory / 2**30},
                   "rows": rows, "best": best,
                   "scope": ("Z8 sparse add-row arithmetic only, batched over independent terms. "
                             "Does NOT cover the divergent control flow (shrink S-set, dimer "
                             "partition), which is the real SIMT risk.")}, fh, indent=2)
    print(f"\n  written: results/{os.path.basename(dst)}")


if __name__ == "__main__":
    main()
