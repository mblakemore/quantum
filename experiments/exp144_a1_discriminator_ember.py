#!/usr/bin/env python3
"""Exp144 A1(0) DISCRIMINATOR (Ember) — which noise ate wave 1: idle or CX?

Wave 1 halted on §10: off-group Bell mass 0.36-0.38 / 0.52-0.61 / 0.86-0.88 at n=4/6/8.
Two hypotheses, no control:
  * IDLE dephasing during the 4.5-8us V gadget (Ember; Exp143 measured 5us idle at +19.8%)
  * CX errors in the deep gadget (Elder; 26/42/58 CX — a channel Exp143 NEVER measured)
Both scale with n, so the wave-1 numbers bracket BOTH. The frozen §8 clause is explicit:
"any post-hoc 'outlier X explains result Y' requires a CONTROL ARM." This is that arm.

THREE ARMS, same 6 pairs, n=6-class:
  ARM-IDLE : Bell -> delay(6.3us) -> Bell measure.        Duration-matched, ZERO gates.
  ARM-CX   : Bell -> 42 CX (identity) -> Bell measure.    CX-matched, MINIMAL duration.
  ARM-DD   : Bell -> delay(6.3us) w/ XY4 DD -> measure.   The actionable one.

TWO DESIGN POINTS THAT DECIDE WHETHER THIS WORKS AT ALL:

1. IDENTITY-EQUIVALENCE. Each arm's ideal output MUST be the untouched Bell state, or the
   arm measures its own logic instead of its noise. CX.CX = I, so each pair needs an EVEN
   count. The spec's "42 CX / 6 pairs" = 7 each = ODD. Fixed: 3 pairs x 6 + 3 pairs x 8
   = 42 exactly, every pair even.

2. PARALLEL, NOT SERIAL. 42 CX x 68ns = 2.86us SERIAL — which would drag 2.9us of idle
   along beside the CX and re-confound the two channels the arm exists to separate. On 6
   DISJOINT pairs the CX run in parallel: 8 deep = 0.54us. That holds CX count at 42 while
   collapsing duration, so the channels actually come apart.

PRE-STATED PREDICTIONS (on the record before submission):
  ARM-IDLE : 0.58 (Ember, fingerprint) / 0.50-0.65 (Elder) — calibration anchor, both camps
  ARM-CX   : ~0.07 (Ember, duration-share) / 0.04-0.08 (Whisper, from kingston's PUBLISHED
             2q calibration — an independent source neither camp used)
             >= 0.25 FALSIFIES idle-dominance. Ember's line, moved against himself.
  ARM-DD   : <=0.25 if idle is quasi-static | ~0.58 if fast Markovian | worse if CX-dominant

  python3 exp144_a1_discriminator_ember.py --dry-run
  python3 exp144_a1_discriminator_ember.py --fly --backend ibm_kingston
"""
import argparse
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
RESULTS = os.path.join(HERE, "..", "results")

SHOTS = 4096
IDLE_US = 6.3          # duration-matched to the real n=6 V gadget (Elder C6512 --scan)
CX_PER_PAIR = [6, 6, 6, 8, 8, 8]     # = 42 total, every entry EVEN => identity


def eligible_pairs(n=6):
    """The pairs my §8 gate selected — same cohort wave 1 flew, so the answer applies."""
    with open(os.path.join(RESULTS, "exp144_layout_gated_ember.json")) as f:
        g = json.load(f)
    return [tuple(e["pair"]) for e in g["eligible"][:n]]


def build_arms(pairs):
    from qiskit import QuantumCircuit
    from qiskit.circuit import Delay

    n = len(pairs)
    lpairs = [(2 * i, 2 * i + 1) for i in range(n)]   # logical: (0,1),(2,3),...
    flat = [q for p in lpairs for q in p]
    qmax = 2 * n

    def bell_prep(qc):
        for a, b in lpairs:
            qc.h(a)
            qc.cx(a, b)

    def bell_measure(qc):
        # Undo the Bell prep: ideal output is |00..0>. Any other bitstring = off-group.
        for a, b in lpairs:
            qc.cx(a, b)
            qc.h(a)
        qc.measure(flat, range(len(flat)))

    arms = {}

    # ARM-IDLE: pure duration, zero gates.
    qc = QuantumCircuit(qmax, len(flat))
    bell_prep(qc)
    qc.barrier(flat)
    for q in flat:
        qc.delay(int(IDLE_US * 1000), q, unit="ns")
    qc.barrier(flat)
    bell_measure(qc)
    arms["idle"] = qc

    # ARM-CX: CX count matched, duration minimal (parallel across disjoint pairs).
    qc = QuantumCircuit(qmax, len(flat))
    bell_prep(qc)
    qc.barrier(flat)
    for (a, b), cnt in zip(lpairs, CX_PER_PAIR):
        for _ in range(cnt):
            qc.cx(a, b)          # even count per pair => identity
    qc.barrier(flat)
    bell_measure(qc)
    arms["cx"] = qc

    # ARM-DD: same idle window, XY4 refocusing.
    qc = QuantumCircuit(qmax, len(flat))
    bell_prep(qc)
    qc.barrier(flat)
    slot = int(IDLE_US * 1000 / 6)     # this loop emits 6 delay slots; /6 keeps the
                                       # DD window duration-MATCHED to ARM-IDLE (6.3us).
                                       # Sized /8 it idled only 4.7us and would have
                                       # "beaten" ARM-IDLE by idling less — a confound,
                                       # not a result.
    for q in flat:
        qc.delay(slot, q, unit="ns")
    for gate in ("x", "y", "x", "y"):
        for q in flat:
            getattr(qc, gate)(q)
        for q in flat:
            qc.delay(slot, q, unit="ns")
    for q in flat:
        qc.delay(slot, q, unit="ns")
    qc.barrier(flat)
    bell_measure(qc)
    arms["dd"] = qc

    return arms


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    ap.add_argument("--fly", action="store_true")
    ap.add_argument("--backend", default="ibm_kingston")
    a = ap.parse_args()
    if not (a.dry_run or a.fly):
        ap.print_help()
        return 0

    # Import what the flight needs on BOTH paths — a dry-run that skips the submit-only
    # imports proves nothing about the flight (C4194, learned at the wave-1 flight).
    try:
        from run_exp66_qpu_partb import _get_ibm_service
        from qiskit import transpile
        from qiskit_ibm_runtime import SamplerV2
        print("submit imports: resolved ✓")
    except Exception as e:
        print(f"REFUSING: submit deps do not import ({type(e).__name__}: {e})")
        return 2

    pairs = eligible_pairs(6)
    print(f"pairs (from my §8-gated cohort — same one wave 1 flew): {pairs}")
    arms = build_arms(pairs)

    # IDENTITY CHECK: every arm's ideal output must be all-zeros. If an arm is not
    # identity-equivalent it measures its own logic and its number is meaningless.
    from qiskit.quantum_info import Statevector
    print("\n=== identity-equivalence (ideal output must be |0...0>) ===")
    bad = 0
    for name, qc in arms.items():
        probe = qc.remove_final_measurements(inplace=False)
        # delays/barriers are no-ops for the ideal statevector
        sv = Statevector.from_instruction(probe)
        p0 = abs(sv.data[0]) ** 2
        ok = p0 > 0.999
        bad += (not ok)
        print(f"  [{'PASS' if ok else 'FAIL'}] ARM-{name.upper():5s} P(|0..0>) = {p0:.4f}")
    if bad:
        print("REFUSING: an arm is not identity-equivalent — it would measure logic, not noise.")
        return 1

    if a.dry_run:
        for name, qc in arms.items():
            print(f"  ARM-{name.upper():5s}: depth {qc.depth():4d}  ops {dict(qc.count_ops())}")
        print("\nDRY-RUN: 3 arms built, identity-verified, nothing submitted.")
        return 0

    svc = _get_ibm_service()
    backend = svc.backend(a.backend)
    st = backend.status()
    print(f"\n{backend.name}: operational={st.operational} pending={st.pending_jobs}")

    tpubs, order = [], []
    for name, qc in arms.items():
        layout = [q for p in pairs for q in p]   # logical i -> physical layout[i]
        t = transpile(qc, backend, initial_layout=layout,
                      optimization_level=0, seed_transpiler=144)
        tpubs.append((t, None, SHOTS))
        order.append(name)
    job = SamplerV2(mode=backend).run(tpubs)
    man = {"exp": "144-A1(0)", "arms": order, "pairs": [list(p) for p in pairs],
           "shots": SHOTS, "idle_us": IDLE_US, "cx_per_pair": CX_PER_PAIR,
           "job_id": job.job_id(), "backend": a.backend,
           "predictions": {"idle": "0.58 (Ember) / 0.50-0.65 (Elder)",
                           "cx": "~0.07 (Ember) / 0.04-0.08 (Whisper, calibration) "
                                 "| >=0.25 FALSIFIES idle-dominance",
                           "dd": "<=0.25 quasi-static | ~0.58 Markovian"}}
    outp = os.path.join(RESULTS, "exp144_a1_discriminator_manifest.json")
    with open(outp, "w") as f:
        json.dump(man, f, indent=1)
    print(f"SUBMITTED A1(0): job {job.job_id()} (3 arms co-batched, one window) -> {outp}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
