#!/usr/bin/env python3
"""CEILING HUNT — SAME-CALIBRATION PAIR FLIGHTS (Whisper C5013). Amendment 1 Item 8,
ADOPTED 2-of-2 (Ember #2910, Elder #2921).

TWO pair-jobs, each carrying BOTH rungs (n=10 and n=14) at m=2040/rung in ONE job —
same-calibration by construction. Analysis is pre-registered and frozen BEFORE this flight
existed (exp142_p1_day_effect_estimator_elder_c6575.py, quantum@737cd90 ff).

ITEM 8 SPEC COMPLIANCE:
(i)  PUBLIC-P: both Paulis are read from the PUBLIC reveal artifacts (n=10 IYZZXYYIXY,
     n=14 IYZYYXYIZYXIIX) — nothing sealed, no secret store touched, and correctly so.
(ii) EVIDENCE-CLASS TAGGING IS STRUCTURAL: every manifest row-group carries
     evidence_class = "calibration-control (public-P, NOT a blind identification)" and NO
     commitment_hash field — the arc's rung tally is computed from rows WITH a
     commitment_hash, so these rows can never be counted as identification rungs.
(iii) SAME P as the original flights (P-controlled comparison; fresh draws would
     reintroduce the nuisance this flight removes).
(iv) RATE COMPUTATION, PRE-REGISTERED HERE BEFORE THE DATA EXISTS: rates are computed
     IDENTICALLY to the sealed rungs — frozen constraint_rate (G2 mapping + csign) for the
     flown P, i.e. fraction of Bell samples whose symplectic constraint matches
     csign[#Y(P) mod 2]; equivalently the FWHT agreement count at P divided by m (the two
     are bit-identical, proven at rung 14). No other statistic is computed from these rows.
(v)  The diff-of-diffs identifies the day term UNDER the declared assumption that the
     n-effect is day-independent; the two pairs' mutual difference is the (under-powered,
     power-reported) check on the catastrophic violation of that assumption.

Usage: python3 exp142_p1_daypair_flight_whisper_c5013.py [--backend ibm_fez] [--dry-run]
"""
import argparse, json, os, sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import exp142_flight_kit as K
from exp142_p1_flight_scaffold_whisper_c5003 import q_arm_rows

FREEZE = "2adf197ff7e472683e7aefd60ea46b307fa1a4e4"
AMENDMENT = "41a6bb7 (ADOPTED 2-of-2)"
M_PER_RUNG = 2040
PAIR = (10, 14)
ALT_CRN = ("crn:v1:bluemix:public:quantum-computing:us-east:"
           "a/1e9b7ff09baf49ef875846a9eb696283:44cfd6bd-c143-4ed4-8bc0-9d560992006f::")


def revealed_P(n):
    r = json.load(open(os.path.join(HERE, "exp142_commitments",
                                    f"reveal_p1_allpaulis_n{n}.json")))
    P = r["P"]
    assert len(P) == n and all(c in "IXYZ" for c in P)
    return P


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", default="ibm_fez")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args()

    Ps = {n: revealed_P(n) for n in PAIR}
    print(f"  public P: n=10 {Ps[10]} | n=14 {Ps[14]} (from reveal artifacts)")

    token = None
    for line in open("/mnt/droid/repos/DC15W/.env"):
        if line.startswith("IBMQ_ALT"):
            token = line.strip().split("=", 1)[1]
    if not token:
        sys.exit("IBMQ_ALT token not found. ABORT.")

    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
    from qiskit import transpile as _t
    svc = QiskitRuntimeService(channel="ibm_quantum_platform", token=token, instance=ALT_CRN)
    backend = svc.backend(a.backend)
    tsent = _t(K.sentinel_circuit(), backend, optimization_level=1, seed_transpiler=142)

    rng = np.random.default_rng()
    pair_pubs, layouts = [tsent and (tsent, None, K.SENT_SHOTS)], {}
    pubs = [(tsent, None, K.SENT_SHOTS)]
    for n in PAIR:
        q_layout, _c, _b = K.pick_layouts(backend, n)
        layouts[n] = q_layout
        qqc, qparams = K.quantum_template(n)
        rows = q_arm_rows(n, Ps[n], rng, M_PER_RUNG)
        tq = _t(qqc, backend, initial_layout=q_layout, optimization_level=1, seed_transpiler=142)
        pubs.append((tq, K.named_rows(qparams, rows), 1))
    pubs.append((tsent, None, K.SENT_SHOTS))
    print(f"  built pair job: sentinel + q10({M_PER_RUNG}) + q14({M_PER_RUNG}) + sentinel")

    if a.dry_run:
        print("  DRY-RUN: no submission.")
        return 0

    sampler = SamplerV2(mode=backend)
    jobs = []
    for pair_idx in (1, 2):
        # fresh prep randomness per pair: rebuild the quantum pubs with new rows
        pubs_i = [(tsent, None, K.SENT_SHOTS)]
        for n in PAIR:
            qqc, qparams = K.quantum_template(n)
            rows = q_arm_rows(n, Ps[n], rng, M_PER_RUNG)
            tq = _t(qqc, backend, initial_layout=layouts[n], optimization_level=1,
                    seed_transpiler=142)
            pubs_i.append((tq, K.named_rows(qparams, rows), 1))
        pubs_i.append((tsent, None, K.SENT_SHOTS))
        job = sampler.run(pubs_i)
        jobs.append({"pair": pair_idx, "job_id": job.job_id(),
                     "pubs": ["sentinel", f"q10_m{M_PER_RUNG}", f"q14_m{M_PER_RUNG}", "sentinel"]})
        print(f"  PAIR {pair_idx} SUBMITTED: {job.job_id()}")

    manifest = {
        "experiment": "exp142_p1_day_effect_pairs", "cycle": "C5013",
        "evidence_class": "calibration-control (public-P, NOT a blind identification)",
        "NOTE_NO_commitment_hash": "by design — these rows must never enter the rung tally",
        "prereg_freeze_commit": FREEZE, "amendment": AMENDMENT,
        "estimator": "exp142_p1_day_effect_estimator_elder_c6575.py (pre-registered @737cd90)",
        "rate_computation_preregistered": "frozen constraint_rate (G2/csign) == FWHT count / m; "
                                          "identical to sealed rungs; no other statistic",
        "P_used": {"10": Ps[10], "14": Ps[14], "provenance": "public reveal artifacts, same-P rule"},
        "m_per_rung": M_PER_RUNG, "backend": a.backend, "instance": "ALT open-instance",
        "layouts": {str(n): layouts[n] for n in PAIR}, "jobs": jobs,
        "committer": "Whisper (DC15W)"}
    outp = os.path.join(HERE, "..", "results", "exp142_p1_day_effect_pairs_manifest.json")
    json.dump(manifest, open(outp, "w"), indent=1)
    print(f"  manifest -> {outp}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
