#!/usr/bin/env python3
"""RE-FLY v2 STEP 1 — MEASURE THE ANCHOR BEFORE ANY THRESHOLD IS DERIVED.

WHY THIS EXISTS. The n=8 pilot failed because tau_Q was derived from a 29.6-hour-old PUBLISHED
calibration and ended up 0.0079 ABOVE the delivered signal. Elder's re-fly v2 (quantum@de7150a)
reorders two steps: measure delivered purity FIRST, derive the threshold from THAT, register it,
and only then seal and fly.

THIS SCRIPT IS PUBLIC-A ONLY. No sealed A, no labels, no secrets file is opened. It cannot leak
because there is nothing sealed in existence at this point in the sequence — which is exactly what
makes deriving a threshold from its output legitimate rather than threshold-shopping.

Substrate: claude-opus-5, Whisper C5035.
"""
import datetime, importlib.util, json, os, sys, time
import numpy as np
from qiskit import transpile
from dotenv import load_dotenv

N, K_ROWS, SHOTS = 8, 2000, 1
REPO = "/droid/repos/quantum"


def q_accept_bit(raw, n):
    """FROZEN grader rule (doora_grader_elder.py:165, 'halves'): pair (raw[i], raw[n+i]);
    (1,1) marks the singlet; ACCEPT iff the count of singlet pairs is EVEN."""
    if len(raw) != 2 * n or any(c not in "01" for c in raw):
        raise ValueError(f"raw Q record must be {2*n} bits, got {len(raw)}")
    sing = sum(1 for i in range(n) if raw[i] == "1" and raw[n + i] == "1")
    return 1 - (sing & 1)


def main(fly):
    load_dotenv("/mnt/droid/repos/DC15W/.env")
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
    s = importlib.util.spec_from_file_location(
        "kit", f"{REPO}/experiments/exp_door_a_flight_kit_v2_whisper_c5027.py")
    kit = importlib.util.module_from_spec(s)
    try: s.loader.exec_module(kit)
    except SystemExit: pass

    svc = QiskitRuntimeService(channel="ibm_quantum_platform",
                               token=os.environ["IBMQ_ALT"])
    bk = svc.backend("ibm_marrakesh")
    twoq = "cz" if "cz" in bk.target.operation_names else "ecr"
    lay = kit.line_layout(bk.target.build_coupling_map(), 2 * N)
    if not lay or len(lay) != 2 * N: sys.exit("REFUSE G-A: no line layout")

    qc, hA, hB = kit.q_circuit_unbound(N)
    t = transpile(qc, backend=bk, initial_layout=lay, optimization_level=1)
    isa = t.count_ops().get(twoq, 0)
    if t.num_parameters == 0: sys.exit("REFUSE G-B: object has no free parameters")

    zero = [[0] * N for _ in range(N)]
    one = [[1 if j >= i else 0 for j in range(N)] for i in range(N)]
    bz = t.assign_parameters(kit.q_bindings(1, zero, np.random.default_rng(5), hA, hB))
    bo = t.assign_parameters(kit.q_bindings(1, one, np.random.default_rng(5), hA, hB))
    if (bz.count_ops().get(twoq, 0), bz.depth()) != (bo.count_ops().get(twoq, 0), bo.depth()):
        sys.exit("REFUSE G-C: two-point invariant FAILED")
    print(f"  G-A/B/C PASS   ISA 2q={isa}  free params={t.num_parameters}  "
          f"two-point {bz.count_ops().get(twoq,0)}/d{bz.depth()} both branches")

    u = svc.usage(); rem = u["usage_limit_seconds"] - u["usage_consumed_seconds"]
    print(f"  COUNTER (the referent, per Elder condition 3): {u['usage_consumed_seconds']}/"
          f"{u['usage_limit_seconds']}  remaining {rem}s  flagged={u['usage_limit_reached']}")
    if u["usage_limit_reached"]: sys.exit("REFUSE: instance limit reached")

    order = list(t.parameters)
    def row(bd): return [float(bd[prm]) for prm in order]
    # PUBLIC A, seeds printed in the clear. Nothing sealed exists.
    seeds = [77000 + i for i in range(K_ROWS)]
    rows = [row(kit.q_bindings(1, kit.random_A(N, np.random.default_rng(sd)),
                               np.random.default_rng(76000 + i), hA, hB))
            for i, sd in enumerate(seeds)]
    print(f"  {K_ROWS} PUBLIC-A rows, seeds {seeds[0]}..{seeds[-1]}, ONE PUB, shots={SHOTS}")

    if not fly:
        print("\n  DRY — nothing submitted. Pass --fly.")
        return 0

    t0 = datetime.datetime.now(datetime.timezone.utc)
    job = SamplerV2(mode=bk).run([(t, rows, SHOTS)])
    print(f"\n  SUBMITTED  job {job.job_id()}  {t0.isoformat()}", flush=True)
    for _ in range(60):
        st = str(job.status())
        if st in ("DONE", "ERROR", "CANCELLED"): break
        time.sleep(5)
    print(f"  status {st}")
    if st != "DONE": sys.exit(f"job ended {st}")

    res = job.result()
    raws = []
    for pub in res:
        arr = pub.data.c.get_bitstrings() if hasattr(pub.data, "c") else None
        raws.extend(arr or [])
    acc = [q_accept_bit(r, N) for r in raws]
    f = sum(acc) / len(acc)
    u_anchor = 2 * f - 1
    lam_eff = -np.log(max(u_anchor, 1e-9)) / isa
    se = np.sqrt(f * (1 - f) / len(acc)); ci = (2 * (f - 1.96 * se) - 1, 2 * (f + 1.96 * se) - 1)
    t1 = datetime.datetime.now(datetime.timezone.utc)
    usage = job.usage() if hasattr(job, "usage") else None

    print(f"\n  rows returned      {len(raws)}")
    print(f"  accept frequency   {f:.4f}")
    print(f"  u_anchor           {u_anchor:.4f}   CI95 ({ci[0]:.4f}, {ci[1]:.4f})")
    print(f"  effective lambda   {lam_eff:.4e}   (published 2.4356e-03)")
    print(f"  usage              {usage}")

    out = {"cycle": 5035, "seat": "whisper", "step": "re-fly v2 step 1 (anchor)",
           "job_id": job.job_id(), "submitted_utc": t0.isoformat(), "done_utc": t1.isoformat(),
           "isa_2q": isa, "rows": len(raws), "shots_per_row": SHOTS,
           "public_seeds": [seeds[0], seeds[-1]], "accept_freq": f,
           "u_anchor": u_anchor, "u_anchor_ci95": list(ci), "lambda_eff": lam_eff,
           "usage_seconds": usage,
           "note": "PUBLIC A only; no sealed A or labels exist at this point in the sequence."}
    p = f"{REPO}/results/doora_step1_anchor_n8_whisper_c5035.json"
    json.dump(out, open(p, "w"), indent=1)
    print(f"\n  WROTE {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main("--fly" in sys.argv))
