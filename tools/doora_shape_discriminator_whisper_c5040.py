#!/usr/bin/env python3
"""SHAPE vs TIME/BOUNDARY — one job, two shapes, equal samples. PUBLIC-A ONLY.

WHY. Tonight door (a)'s threshold missed the delivered signal by one part in 350 because a
1-shot-per-row anchor read u=0.2480 and the 316-shot-per-row flight delivered u=0.1228 — a 2.02x
gap. Three candidate causes were confounded in every pair we hold: elapsed TIME, the JOB
BOUNDARY, and SHOTS PER ROW. Ember's pilot held shape AND time fixed together (ratio 1.039), so
it settles the design fix and isolates nothing.

MY FIRST PROPOSAL WAS A SEPARATE 316-SHOT JOB. That leaves time and boundary confounded with
shape — the same defect I criticised in the k=0.48 fit. This design fixes it: BOTH BLOCKS IN ONE
PUB, one job, one epoch. Only shots-per-row differs.

  block A   2,000 rows x   1 shot   = 2,000 samples
  block B       6 rows x 333 shots  = 1,998 samples   (equal samples -> equal error bars)

PRE-REGISTERED PREDICTIONS, filed before flight:
  SHAPE model          block B reads ~2x LOWER than block A
  TIME/BOUNDARY model  both blocks read THE SAME

Nothing sealed exists in this experiment. A is drawn publicly and the seeds are printed.

Substrate: claude-opus-5, Whisper C5040.
"""
import datetime, importlib.util, json, os, sys, time
import numpy as np
from qiskit import transpile
from dotenv import load_dotenv

N = 8
ROWS_A, SHOTS_A = 2000, 1
ROWS_B, SHOTS_B = 6, 333
REPO = "/droid/repos/quantum"
WHISPERPAID = ("crn:v1:bluemix:public:quantum-computing:us-east:"
               "a/65155eedeb8b464eadf55d101fb3c931:27609585-d5b2-43cb-808d-2d47aeb87c05::")


def q_accept_bit(raw, n):
    """FROZEN grader rule (doora_grader_elder.py:165, 'halves')."""
    if len(raw) != 2 * n or any(c not in "01" for c in raw):
        raise ValueError(f"raw must be {2*n} bits, got {len(raw)}")
    sing = sum(1 for i in range(n) if raw[i] == "1" and raw[n + i] == "1")
    return 1 - (sing & 1)


def u_of(raws):
    acc = [q_accept_bit(r, N) for r in raws]
    f = sum(acc) / len(acc)
    se = np.sqrt(f * (1 - f) / len(acc))
    return 2 * f - 1, 2 * se, len(acc)


def main(fly):
    load_dotenv("/mnt/droid/repos/DC15W/.env")
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
    s = importlib.util.spec_from_file_location(
        "kit", f"{REPO}/experiments/exp_door_a_flight_kit_v2_whisper_c5027.py")
    kit = importlib.util.module_from_spec(s)
    try: s.loader.exec_module(kit)
    except SystemExit: pass

    svc = QiskitRuntimeService(channel="ibm_quantum_platform",
                               token=os.environ["IBMQ_TOKEN"], instance=WHISPERPAID)
    bk = svc.backend("ibm_marrakesh")
    twoq = "cz" if "cz" in bk.target.operation_names else "ecr"
    lay = kit.line_layout(bk.target.build_coupling_map(), 2 * N)
    if not lay or len(lay) != 2 * N: sys.exit("REFUSE: no line layout")

    qc, hA, hB = kit.q_circuit_unbound(N)
    t = transpile(qc, backend=bk, initial_layout=lay, optimization_level=1)
    isa = t.count_ops().get(twoq, 0)
    if t.num_parameters == 0: sys.exit("REFUSE: object has no free parameters")
    print(f"  ISA 2q={isa}  free params={t.num_parameters}  (G-C' retired: bind cannot alter gates)")

    u = svc.usage(); rem = u["usage_remaining_seconds"]
    print(f"  COUNTER {u['usage_consumed_seconds']}/{u['usage_limit_seconds']}  "
          f"remaining {rem}s = ${rem*1.6:,.2f}   flagged={u['usage_limit_reached']}")
    if u["usage_limit_reached"]: sys.exit("REFUSE: instance limit reached")
    if rem < 15: sys.exit(f"REFUSE: only {rem}s left")

    order = list(t.parameters)
    def rows_ordered(k, seed0):
        out = []
        for i in range(k):
            bd = kit.q_bindings(1, kit.random_A(N, np.random.default_rng(seed0 + i)),
                                np.random.default_rng(seed0 + 500000 + i), hA, hB)
            out.append([float(bd[p]) for p in order])
        return out

    A = rows_ordered(ROWS_A, 88000)
    B = rows_ordered(ROWS_B, 99000)
    print(f"  block A {ROWS_A:,} rows x {SHOTS_A} shot  = {ROWS_A*SHOTS_A:,} samples  seeds 88000+")
    print(f"  block B {ROWS_B:,} rows x {SHOTS_B} shots = {ROWS_B*SHOTS_B:,} samples  seeds 99000+")
    print("  BOTH IN ONE JOB — time and job boundary held EXACTLY; only shape differs.")

    if not fly:
        print("\n  DRY — nothing submitted. Pass --fly.")
        return 0

    t0 = datetime.datetime.now(datetime.timezone.utc)
    job = SamplerV2(mode=bk).run([(t, A, SHOTS_A), (t, B, SHOTS_B)])
    print(f"\n  SUBMITTED  job {job.job_id()}  {t0.isoformat()}", flush=True)
    for _ in range(90):
        st = str(job.status())
        if st in ("DONE", "ERROR", "CANCELLED"): break
        time.sleep(5)
    print(f"  status {st}")
    if st != "DONE": sys.exit(f"job ended {st}")

    res = job.result()
    ua, sea, na = u_of(res[0].data.c.get_bitstrings())
    ub, seb, nb = u_of(res[1].data.c.get_bitstrings())
    ratio = ua / ub if ub else float("inf")
    z = (ua - ub) / np.sqrt(sea**2 + seb**2)
    print(f"\n  block A ({SHOTS_A} shot/row) : u = {ua:.4f} +/- {sea:.4f}   n={na:,}")
    print(f"  block B ({SHOTS_B} shots/row): u = {ub:.4f} +/- {seb:.4f}   n={nb:,}")
    print(f"  ratio A/B = {ratio:.3f}    z = {z:.2f}")
    verdict = ("SHAPE — shots-per-row drives the gap" if z > 3 else
               "TIME/BOUNDARY — shape is NOT the cause" if abs(z) <= 3 else
               "ANOMALOUS — B exceeds A, neither model predicted this")
    print(f"\n  VERDICT: {verdict}")

    out = {"cycle": 5040, "seat": "whisper", "job_id": job.job_id(),
           "submitted_utc": t0.isoformat(), "isa_2q": isa,
           "block_A": {"rows": ROWS_A, "shots": SHOTS_A, "u": ua, "se": sea, "n": na},
           "block_B": {"rows": ROWS_B, "shots": SHOTS_B, "u": ub, "se": seb, "n": nb},
           "ratio_A_over_B": ratio, "z": z, "verdict": verdict,
           "usage_seconds": (job.usage() if hasattr(job, "usage") else None),
           "prereg": {"SHAPE": "B reads ~2x lower than A", "TIME_BOUNDARY": "A and B equal"},
           "note": "PUBLIC A only; one job so time and boundary are held exactly."}
    p = f"{REPO}/results/doora_shape_discriminator_n8_whisper_c5040.json"
    json.dump(out, open(p, "w"), indent=1)
    print(f"  WROTE {p}")
    return 0


if __name__ == "__main__":
    sys.exit(main("--fly" in sys.argv))
