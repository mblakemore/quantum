#!/usr/bin/env python3
"""GEAR 1 STEP A — THE RIDER SURVEY (Whisper C5073, Creator GO general#11463 on the lane).

The coherent error field, measured: the conditional-phase rider on native CZ, per edge,
in-window. CZ is self-inverse, so a run of 2k CZs is ideal identity — any phase left on a
Ramsey spectator IS the rider, and coherent riders accumulate LINEARLY in k while stochastic
noise does not.

DESIGN (one flight, marrakesh, 16 calibration-picked DISJOINT edges in parallel — kit
pick_layouts, F57/F58 lineage):
  Per edge (a,b), per setting: H(a); [CZ(a,b)] x 2k; then measure a in X or Y basis
  (phase = atan2(<Y>,<X>)), with b prepared in |0> or |1>. Depths 2k in {0,4,16,64};
  2 control states x 2 bases; plus 2 REPEAT pubs (setting 2k=16, b=|1>, both bases, flown
  again at the END of the job) for the within-job stability check.
  Roles then swapped (b the Ramsey qubit) in the same pubs on the OTHER half of the 16 edges
  (disjoint edges = both role assignments covered across the edge set).
  Whole-chip cal0/cal1 as always. ~18 pubs x 8000 shots.

PRE-REGISTERED PREDICTIONS:
  P-A (existence/coherence): on >= half the edges, extracted phase grows LINEARLY in k
    (r^2 >= 0.9 across the 3 nonzero depths) with per-CZ conditional rider |dphi| resolvable
    above its propagated shot-noise se — the field is coherent and per-edge stable, as
    Finding 04's error taxonomy predicts (mrad-class expected).
  P-B (in-window quiet, the Lock 6 echo): the END-of-job repeat pubs reproduce their
    early twins within 3 se — the field is STABLE across the job (this is what makes it
    a usable gear rather than noise).
  NO-TEST branches: visibility at 2k=64 below 0.2 on an edge -> that edge's fit drops to
    {4,16} (T2 wall, reported); riders below resolution everywhere -> honest upper bound on
    the field (a null that prices the gear as too fine to mesh at this cal quality).
STEP B (fold-in demo: computation calibrated to the measured field vs uncalibrated twin)
freezes SEPARATELY once these numbers exist.
Account IBMQ_ALT4; pending_jobs at submit; joules/claim fences standing.
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
QROOT = os.path.join(HERE, "..")
import exp142_flight_kit as K
from qiskit import QuantumCircuit, transpile
import numpy as np

BACKEND = "ibm_marrakesh"
NPHYS = 156
DEPTHS_2K = [0, 4, 16, 64]
N_EDGES = 16
OUT = os.path.join(QROOT, "results", "exp_gear1_rider_survey_c5073_manifest.json")


def ramsey_pub(edges, ramsey_first, twok, ctrl_one, basis):
    """One circuit: on each disjoint edge, Ramsey qubit r, control c."""
    qc = QuantumCircuit(NPHYS)
    for (a, b) in edges:
        r, c = (a, b) if ramsey_first else (b, a)
        if ctrl_one:
            qc.x(c)
        qc.h(r)
        for _ in range(twok):
            qc.cz(a, b)
        if basis == "Y":
            qc.sdg(r)
        qc.h(r)
    qc.measure_all()
    return qc


def main(submit=False):
    from qiskit_ibm_runtime import SamplerV2
    sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
    from ibm_multi_account import service_for_submission
    svc = service_for_submission("IBMQ_ALT4")
    backend = svc.backend(BACKEND)
    props = backend.properties()
    print(f"marrakesh cal epoch: {props.last_update_date}")

    q_layout, _c, _b = K.pick_layouts(backend, N_EDGES)
    edges = [tuple(q_layout[2*i:2*i+2]) for i in range(N_EDGES)]
    print(f"[$0-validate] {len(edges)} disjoint calibration-picked edges: {edges}")

    pubs, meta = [], []
    for state, tag in ((0, "cal0"), (1, "cal1")):
        qc = QuantumCircuit(NPHYS)
        if state:
            qc.x(range(NPHYS))
        qc.measure_all()
        pubs.append((transpile(qc, backend, optimization_level=0), None, 8000))
        meta.append({"block": tag, "shots": 8000})

    def add(twok, ctrl_one, basis, tag_extra=""):
        # half the edges Ramsey-on-first, half Ramsey-on-second (role coverage across set)
        qc = QuantumCircuit(NPHYS)
        for i, (a, b) in enumerate(edges):
            r, c = (a, b) if i % 2 == 0 else (b, a)
            if ctrl_one:
                qc.x(c)
            qc.h(r)
            for _ in range(twok):
                qc.cz(a, b)
            if basis == "Y":
                qc.sdg(r)
            qc.h(r)
        qc.measure_all()
        tqc = transpile(qc, backend, optimization_level=0, initial_layout=list(range(NPHYS)))
        pubs.append((tqc, None, 8000))
        meta.append({"block": f"rider_2k{twok}_c{int(ctrl_one)}_{basis}{tag_extra}",
                     "twok": twok, "ctrl_one": ctrl_one, "basis": basis, "shots": 8000})

    for twok in DEPTHS_2K:
        for ctrl_one in (False, True):
            for basis in ("X", "Y"):
                add(twok, ctrl_one, basis)
    # within-job stability repeats at the END (P-B)
    add(16, True, "X", "_repeat")
    add(16, True, "Y", "_repeat")
    print(f"[$0-validate] {len(pubs)} pubs built ({len(pubs)-2} rider + 2 cal)")

    man = {"card": "exp_gear1_rider_survey", "cycle": "C5073", "substrate": "claude-fable-5",
           "backend": BACKEND, "cal_epoch": str(props.last_update_date),
           "edges": [list(e) for e in edges], "depths_2k": DEPTHS_2K, "account": "IBMQ_ALT4",
           "ramsey_role_rule": "edge index even -> Ramsey on first qubit; odd -> on second",
           "purpose": "GEAR 1 step A (Creator GO general#11463): per-edge coherent conditional-phase rider on native CZ, in-window, with within-job stability repeats",
           "prereg": "predictions P-A/P-B + NO-TEST branches in docstring, committed pre-flight",
           "pubs_meta": meta}
    if submit:
        man["pending_jobs_at_submit"] = backend.status().pending_jobs
        job = SamplerV2(mode=backend).run(pubs)
        man["job_id"] = job.job_id()
        print(f"SUBMITTED {man['job_id']} to {BACKEND} (pending at submit: {man['pending_jobs_at_submit']})")
    else:
        print("[dry] not submitted (pass --submit to fly)")
    json.dump(man, open(OUT, "w"), indent=1)
    print(f"manifest -> {OUT}")


if __name__ == "__main__":
    main(submit="--submit" in sys.argv)
