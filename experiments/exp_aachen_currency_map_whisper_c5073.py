#!/usr/bin/env python3
"""AACHEN CURRENCY-MAP REPLICATION — three axes, one job, a virgin die (Whisper C5073,
Creator GO in-terminal "run the aachen currency-map replication").

The marrakesh/kingston currency map (C5072-73): POPULATION quiet within jobs (Lock 6) ·
PHASE turbulent within jobs (GEAR 1, repeats z=79) · coherent NON-DIAGONAL component present
(GEAR 3, 33 sigma). ibm_aachen has never been measured by this campaign. One combined job
asks all three axes at once; marrakesh values are PRIORS, not bars - each axis gets its own
presence/absence verdict.

BLOCKS (in submission order - the order IS the instrument for the stability axes):
  sentinel_early (Bell pair, 400 shots)                     | population axis, t=start
  cal0, cal1 (whole-chip readout, 8000)                     | corrections
  rider block (GEAR-1 design verbatim: 16 calibration-picked disjoint edges, self-inverse
    CZ trains 2k in {0,4,16,64}, ctrl |0>/|1>, X/Y bases = 16 pubs, 8000 each)
  rider repeats (2k=16, c=1, X/Y)                           | phase-stability, t=late
  switch block (GEAR-3 circuits IMPORTED from exp_gear3 module: floor/science/polarity, 8000)
  sentinel_late (identical transpiled Bell object)          | population axis, t=end
PRE-REGISTERED (per axis, all at 3 sigma):
  A-PHASE-FIELD: conditional riders resolvable (per-edge |cond| > 3 se on >= 4 edges).
  A-PHASE-STAB: repeat pubs vs early twins - REPLICATES marrakesh if worst z > 10
    (turbulent); DIFFERS if worst z <= 3 (stable phases on aachen would be a real map
    difference, reported as such; 3 < z <= 10 = intermediate, reported).
  A-NONDIAG: switch science deficit vs depth-normalized floor at 3 sigma (GEAR-3 rule
    verbatim, gate-count normalization included); polarity gate <= -0.5 must pass.
  A-POP: |delta eps| between sentinel_early/late within 3 binomial se = quiet (Lock 6
    analog, single-job paired form); beyond = population motion, reported.
Fences: one die, one epoch, one job; N=1 job for the population axis (a weaker form than
Lock 6's N=49 - stated); device-characterized. Account IBMQ_TOKEN (sole route to aachen;
registry advisory noted, runtime fit gate is the wall).
"""
import argparse, json, os, sys, math
import numpy as np
from qiskit import QuantumCircuit, transpile
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import exp142_flight_kit as K
from exp_gear3_switch_gearbox_whisper_c5073 import switch_circuit

BACKEND = "ibm_aachen"
NPHYS = 156
DEPTHS_2K = [0, 4, 16, 64]
N_EDGES = 16
OUT = os.path.join(HERE, "..", "results", "exp_aachen_currency_map_c5073_manifest.json")


def main():
    ap = argparse.ArgumentParser(); ap.add_argument("--submit", action="store_true")
    a = ap.parse_args()
    from qiskit_ibm_runtime import SamplerV2
    from ibm_multi_account import service_for_submission
    svc = service_for_submission("IBMQ_TOKEN")
    backend = svc.backend(BACKEND)
    props = backend.properties()
    print(f"aachen cal epoch: {props.last_update_date}")

    q_layout, _c, _b = K.pick_layouts(backend, N_EDGES)
    edges = [tuple(q_layout[2*i:2*i+2]) for i in range(N_EDGES)]
    print(f"[$0-validate] {len(edges)} disjoint edges on aachen: {edges[:4]}...")

    pubs, meta = [], []
    # sentinel early (transpiled once, reused at end - same-edge pairing by construction)
    sent = QuantumCircuit(2, 2); sent.h(0); sent.cx(0, 1); sent.measure([0, 1], [0, 1])
    tsent = transpile(sent, backend, optimization_level=1, seed_transpiler=142)
    pubs.append((tsent, None, 400)); meta.append({"block": "sentinel_early", "shots": 400})
    for state, tag in ((0, "cal0"), (1, "cal1")):
        qc = QuantumCircuit(NPHYS)
        if state: qc.x(range(NPHYS))
        qc.measure_all()
        pubs.append((transpile(qc, backend, optimization_level=0), None, 8000))
        meta.append({"block": tag, "shots": 8000})

    def add_rider(twok, ctrl_one, basis, tag_extra=""):
        qc = QuantumCircuit(NPHYS)
        for i, (aa, bb) in enumerate(edges):
            r, c = (aa, bb) if i % 2 == 0 else (bb, aa)
            if ctrl_one: qc.x(c)
            qc.h(r)
            for _ in range(twok): qc.cz(aa, bb)
            if basis == "Y": qc.sdg(r)
            qc.h(r)
        qc.measure_all()
        tqc = transpile(qc, backend, optimization_level=0, initial_layout=list(range(NPHYS)))
        pubs.append((tqc, None, 8000))
        meta.append({"block": f"rider_2k{twok}_c{int(ctrl_one)}_{basis}{tag_extra}",
                     "twok": twok, "ctrl_one": ctrl_one, "basis": basis, "shots": 8000})

    for twok in DEPTHS_2K:
        for ctrl_one in (False, True):
            for basis in ("X", "Y"):
                add_rider(twok, ctrl_one, basis)
    add_rider(16, True, "X", "_repeat")
    add_rider(16, True, "Y", "_repeat")

    for arm in ("floor", "science", "polarity"):
        qc = switch_circuit(arm)
        tqc = transpile(qc, backend, optimization_level=1, seed_transpiler=3)
        pubs.append((tqc, None, 8000))
        meta.append({"block": f"switch_{arm}", "shots": 8000,
                     "cz_count": sum(1 for i in tqc.data if i.operation.num_qubits == 2)})
    pubs.append((tsent, None, 400)); meta.append({"block": "sentinel_late", "shots": 400})
    print(f"[$0-validate] {len(pubs)} pubs built")

    man = {"card": "exp_aachen_currency_map", "cycle": "C5073", "substrate": "claude-fable-5",
           "backend": BACKEND, "cal_epoch": str(props.last_update_date),
           "edges": [list(e) for e in edges], "depths_2k": DEPTHS_2K,
           "account": "IBMQ_TOKEN",
           "purpose": "Currency-map replication on a virgin die: phase field + phase stability + non-diagonal + population, one job",
           "prereg": "A-PHASE-FIELD / A-PHASE-STAB / A-NONDIAG / A-POP with bands + fences in docstring",
           "pubs_meta": meta}
    if a.submit:
        man["pending_jobs_at_submit"] = backend.status().pending_jobs
        job = SamplerV2(mode=backend).run(pubs)
        man["job_id"] = job.job_id()
        print(f"SUBMITTED {man['job_id']} to {BACKEND} (pending at submit: {man['pending_jobs_at_submit']})")
    else:
        print("[dry] not submitted")
    json.dump(man, open(OUT, "w"), indent=1)
    print(f"manifest -> {OUT}")


if __name__ == "__main__":
    main()
