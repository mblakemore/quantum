#!/usr/bin/env python3
"""PROBE A — drift-mechanism purity-vs-depth (Whisper C5010, Creator "Start A and B when possible").

Elder's named cheap next step (crossblock-depthsweep grade C6567): all our drift data is <Z>-only, so a
monotone <Z> decay can't separate coherent from decoherent. This sweeps the SAME widesweep drift circuit
in ALL THREE bases (X,Y,Z) on the drifter register → full Bloch vector r(depth) → purity(depth)=(1+r^2)/2.

Elegant same-epoch design: the Z-basis rows ARE the drift RE-DETECTION (|<Z>| decay identifies the
CURRENT drifters, epoch-volatile per C5002), and the X,Y rows add the purity — one flight, one calibration
window, so re-detection and mechanism share an epoch (advisor caveat satisfied automatically).

PRE-REGISTERED SCOPE (before any data — the session's discipline; bounds match the observable):
  * A purity REVIVAL with depth = clean COHERENCE signature (inhomogeneous shot-to-shot phase-spread
    cannot revive). Resolves the coherent case.
  * A monotone purity DECAY stays AMBIGUOUS — Markovian decoherence and inhomogeneous coherent dephasing
    both shrink ensemble |r| monotonically. A does NOT resolve this case; it still beats <Z>-only.
  * A pins the MECHANISM this EPOCH. It does NOT resolve clock-vs-coin (cross-epoch predictability,
    multi-epoch). Necessary INPUT to B-side #2 Fingerprint Lock / #4 Sundial, not by itself an unblock.
  * Drifter set is epoch-volatile: the Z re-detection rows define the CURRENT drifters; purity is read
    on whoever is actually drifting THIS epoch, not a stale {26,53,73}.

$0 build + $0-validate (build, assert depths/register, optional noise-model), NO submit (QPU floored).
REUSE-MAX: imports the widesweep drift circuit verbatim; only adds pre-measurement basis rotations.
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
QROOT = os.path.join(HERE, "..")
from exp_crossblock_widesweep import build_twins, DEPTHS, DRIFTERS, SEED, NPHYS
from qiskit import QuantumCircuit, transpile
import numpy as np

BACKEND = "ibm_kingston"   # the census chip; re-detection rows re-confirm current drifters this epoch
OUT = os.path.join(QROOT, "results", "exp_drift_purity_probe_manifest.json")


def add_basis(twin, drifters_active, basis):
    """Rotate the drifter qubits into measurement basis B (X: H ; Y: S^dag then H ; Z: none), measure all."""
    qc = twin.copy()
    for q in drifters_active:
        if basis == "X":
            qc.h(q)
        elif basis == "Y":
            qc.sdg(q); qc.h(q)
        # Z: no rotation
    qc.measure_all()
    return qc


def main(submit=False):
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
    import sys as _sys, os as _os; _sys.path.insert(0, _os.path.join(_os.path.dirname(_os.path.abspath(__file__)), "..", "scripts"))
    from ibm_multi_account import service_for_submission
    svc = service_for_submission("IBMQ_ALT")  # c4217_018: named account, no fallback (was bare default)
    backend = svc.backend(BACKEND)
    props = backend.properties()
    print(f"{BACKEND} cal epoch: {props.last_update_date}")

    twins, active = build_twins(backend)
    drifters_active = [q for q in DRIFTERS if q in active]
    print(f"[build] twin register {len(active)} active; census drifters present: {drifters_active}")
    print(f"[design] Z rows = re-detection (current drifters); X,Y rows = purity. depths={DEPTHS}")

    pubs, meta = [], []
    # readout cal (whole-chip 0/1) for per-qubit marginal correction, SAME window
    for state, tag in ((0, "cal0"), (1, "cal1")):
        qc = QuantumCircuit(NPHYS)
        if state:
            qc.x(range(NPHYS))
        qc.measure_all()
        pubs.append((transpile(qc, backend, optimization_level=0), None, 8000))
        meta.append({"block": tag, "shots": 8000})

    ok = True
    for D in DEPTHS:
        for B in ("Z", "X", "Y"):
            circ = add_basis(twins[D], drifters_active, B)
            tqc = transpile(circ, backend, optimization_level=0,
                            initial_layout=list(range(NPHYS)), seed_transpiler=SEED)
            # $0-validate: the twin depth must survive routing (no pad-cancel)
            d2q = sum(1 for i in tqc.data if i.operation.num_qubits == 2)
            good = d2q > 0
            ok &= good
            pubs.append((tqc, None, 12000))
            meta.append({"block": f"d{D}_{B}", "depth": D, "basis": B, "shots": 12000})
        print(f"  [$0-validate] depth {D}: 3 bases built (Z/X/Y), routed 2q>0 = {ok}")
    assert ok, "a depth routed to 0 two-qubit gates — pad-cancel; do NOT submit"
    print("[$0-validate] all depths x 3 bases clean; register valid. Safe to fly when QPU time returns.")

    man = {"card": "exp_drift_purity_probe", "cycle": "C5010", "substrate": "claude-fable-5",
           "backend": BACKEND, "cal_epoch": str(props.last_update_date), "depths": DEPTHS,
           "census_drifters": DRIFTERS, "drifters_active": drifters_active, "register": active,
           "seed": SEED,
           "purpose": "3-basis purity-vs-depth: pin drift mechanism coherent-vs-decoherent (Elder cheap next step)",
           "prereg_scope": {
               "resolves": "coherent case via purity REVIVAL (phase-spread cannot revive)",
               "ambiguous": "monotone purity DECAY (decoherence vs inhomogeneous coherent dephasing)",
               "pins": "mechanism THIS EPOCH, NOT clock-vs-coin (multi-epoch); necessary input to B-side #2/#4",
               "re_detection": "Z rows identify CURRENT drifters same-epoch (set is volatile, C5002)",
               "analysis": "per drifter, per depth: r=|(<X>,<Y>,<Z>)| readout-corrected; purity=(1+r^2)/2; "
                           "classify REVIVAL(coherent) vs MONOTONE-DECAY(ambiguous)"},
           "single_copy": "single-qubit 3-basis tomography — NOT the two-copy kit (that is probe B's scale)",
           "pubs_meta": meta}
    if submit:
        job = SamplerV2(mode=backend).run(pubs)
        man["job_id"] = job.job_id(); print(f"SUBMITTED {man['job_id']}")
    else:
        print("[dry] not submitted (QPU floored; pass --submit when time returns)")
    json.dump(man, open(OUT, "w"), indent=1)
    print(f"manifest -> {OUT}  ({len(pubs)} pubs: 2 cal + {len(DEPTHS)}x3 basis rows)")


if __name__ == "__main__":
    main(submit="--submit" in sys.argv)
