#!/usr/bin/env python3
"""TRICORDER Diff-Mode — SAME-EPOCH graduation flight on MARRAKESH (Whisper C5004, Creator directive).

The H9B#1 follow-on: one wide-depth sweep (160→400) that captures BOTH the drift fingerprint
(|<Z>| decay 160→280) AND the coherence character (revival past the node) in a SINGLE calibration
window — so the coherent/decoherent MECHANISM pins to the fingerprint it labels, fixing the
cross-epoch asterisk Elder #1423 raised on the original (kingston, 3h-split) scan.

NOT the n=8 court: different chip (marrakesh, idle queue), no sealed P, a physics/instrument flight.

PRE-REGISTERED SCOPE (written BEFORE decode — advisor #4, my failure-family lives here):
  This flight GRADUATES the INSTRUMENT on a fresh chip: same-epoch, mechanism-pinned Diff-Mode scan.
  It does NOT:
    • claim the two-copy quantum-memory SAMPLE-ADVANTAGE (still SEPARATION-OWED; this is single-copy
      |<Z>| depth-sweep data, not the F119 two-copy Bell channel);
    • confirm marrakesh REPLICATES kingston's drift — it characterizes marrakesh FRESH (discovery,
      not confirmation; marrakesh has its own drifters, if any);
    • retroactively fix the original KINGSTON scan's cross-epoch asterisk (that needs a same-epoch
      KINGSTON pass — a separate flight).
  VALID OUTCOMES (both are a clean instrument demo, stated before seeing numbers):
    (A) drifters found → flag them with same-epoch-pinned coherent/decoherent verdicts;
    (B) NO dramatic drifters / stable population → the instrument reports "stable, nothing to flag" —
        equally valid; the same-epoch scan works either way. No post-hoc pull toward finding drama.

REUSE-MAX: imports build_twins from the widesweep (the exact same observable), only changes backend +
drops the hardcoded kingston DRIFTERS (drifter-ID moves into the decode, vs the marrakesh population).
$0 PRE-FLIGHT: build + assert d2q>=D at every depth + register check, WITHOUT submit; fly only if clean.
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
QROOT = os.path.join(HERE, "..")
from exp_crossblock_widesweep import build_twins, SEED, DEPTHS   # reuse the exact widesweep observable
from exp_hss_race_flight import d2q_of
from qiskit import QuantumCircuit, transpile
import numpy as np

BACKEND = "ibm_marrakesh"
NPHYS = 156
OUT = os.path.join(QROOT, "results", "exp_tricorder_sameepoch_marrakesh_manifest.json")


def main(submit=False):
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
    svc = QiskitRuntimeService(); backend = svc.backend(BACKEND)
    props = backend.properties()
    print(f"marrakesh cal epoch: {props.last_update_date}")

    # ---- $0 PRE-FLIGHT VALIDATE (advisor #1): build for marrakesh, assert no pad-cancel, check register ----
    twins, active = build_twins(backend)              # transpiles the twin for marrakesh (race_final ports iff same heavy-hex)
    print(f"[$0-validate] twin register (active 2q qubits): {len(active)} on marrakesh")
    pubs, meta = [], []
    # readout cal (whole-chip 0/1) for per-qubit marginal correction — SAME job window as the sweep
    for state, tag in ((0, "cal0"), (1, "cal1")):
        qc = QuantumCircuit(NPHYS)
        if state:
            qc.x(range(NPHYS))
        qc.measure_all()
        pubs.append((transpile(qc, backend, optimization_level=0), None, 8000))
        meta.append({"block": tag, "shots": 8000})
    ok = True
    for D, tw in twins.items():
        mc = tw.copy(); mc.measure_all()
        tqc = transpile(mc, backend, optimization_level=0, initial_layout=list(range(NPHYS)),
                        seed_transpiler=SEED)
        real_d = d2q_of(tqc)
        good = real_d >= D
        ok &= good
        pubs.append((tqc, None, 12000))
        meta.append({"block": f"twin_d{D}", "d2q": D, "shots": 12000})
        print(f"  [$0-validate] twin_d{D}: routed d2q={real_d} (>= {D}? {'OK' if good else 'PAD-CANCEL FAIL'})")
    assert ok, "pad cancelled at some depth on marrakesh — design needs a fresh probe, do NOT submit"
    print("[$0-validate] all depths clean on marrakesh; register valid. Safe to fly.")

    man = {"card": "exp_tricorder_sameepoch_marrakesh", "cycle": "C5004", "substrate": "claude-fable-5",
           "backend": BACKEND, "cal_epoch": str(props.last_update_date), "depths": DEPTHS,
           "register": active, "seed": SEED,
           "purpose": "Tricorder Diff-Mode SAME-EPOCH graduation: drift (160->280) + coherence (revival) in one window -> mechanism pinned to fingerprint",
           "prereg_scope": {
               "graduates": "the instrument on a fresh chip (same-epoch, mechanism-pinned)",
               "does_not_claim": ["two-copy sample-advantage (SEPARATION-OWED, single-copy data)",
                                  "marrakesh replicates kingston (this is FRESH characterization)",
                                  "fix the kingston scan's cross-epoch asterisk (needs same-epoch KINGSTON pass)"],
               "valid_outcomes": ["drifters found + same-epoch-pinned coherence verdicts",
                                  "NO drifters / stable population (equally valid instrument demo)"],
               "drifter_id": "IN DECODE vs the marrakesh population (NOT the kingston {73,26,53,23})"},
           "pubs_meta": meta}
    if submit:
        job = SamplerV2(mode=backend).run(pubs)
        man["job_id"] = job.job_id()
        print(f"SUBMITTED {man['job_id']} to {BACKEND}")
    else:
        print("[dry] not submitted (pass --submit to fly)")
    json.dump(man, open(OUT, "w"), indent=1)
    print(f"manifest -> {OUT}")


if __name__ == "__main__":
    main(submit="--submit" in sys.argv)
