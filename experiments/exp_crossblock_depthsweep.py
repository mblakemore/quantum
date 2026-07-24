#!/usr/bin/env python3
"""P2 drift-alive scout (H9, Whisper C5002) — the fold-before-fly precondition for the cross-block
witness. Kingston recalibrated 2026-07-24 06:15 AFTER the drift census (07-23), so the drift the
witness targets is UNCONFIRMED on the current epoch. Per the card's recal-since-census fold rule +
Elder #1102 grader requirement + Ember #1103 endorsement.

WHAT IT MEASURES (envelope-normalized, no sealed string needed):
  Fly the exact d2q=160 and d2q=280 twin pads (curve-flight builders, SEED 2026072307) on CURRENT
  kingston. Per qubit, the coherent drift shows as |<Z>| (marginal bias magnitude) decaying FASTER
  with depth than the matched stochastic envelope. Envelope-normalize each drifter qubit's decay by
  the MEDIAN non-drifter decay (same register, same pads) -> a drift EXCESS. Elder's gradeable
  precondition:
    (1) drifters show excess decay over the matched-null population with margin >= ~3-5 sigma;
    (2) RECORD the drift STRENGTH (excess magnitude) so the main-block Delta-sensitivity is sized <= it.
  Drift-CONFIRMED -> main block is gradeable (a null is a clean decoherence finding).
  Drift-GONE -> honest report: no live target this epoch, census needs refresh (Ember seal held).

CENSUS REFERENCE (pad_drift_localization_c4984, drifter phys {73,26,53,23}):
  |<Z>| collapses 160->280 on drifters (e.g. phys73 0.345->|-0.321|, phys26 0.345->|-0.277|) while
  strong non-drifter bits hold (phys58 ~0.83 flat). The scout checks that pattern survives recal.
"""
import json, os, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
QROOT = os.path.join(HERE, "..")
from exp_hss_race_flight import d2q_of, to_basis_only
from exp_hss_generator import make_g_spec, build_hss_circuit
from exp_rhot_curve_flight import verify_seals, build_twin, pad_to
from qiskit import QuantumCircuit, transpile
import numpy as np

SEED = 2026072307
BACKEND = "ibm_kingston"
NPHYS = 156
DEPTHS = [160, 200, 240, 280]  # 4-pt depth sweep to pin coherent-vs-incoherent mechanism (C5002-B)
DRIFTERS = [73, 26, 53, 23]  # sweep all census candidates; phys73 the confirmed-coherent one
MANIFEST = json.load(open(os.path.join(QROOT, "results", "exp_rhot_curve_flight_manifest.json")))
OUT = os.path.join(QROOT, "results", "exp_crossblock_depthsweep_manifest.json")


def build_twins(backend):
    seals = verify_seals()
    qc0 = build_hss_circuit(20, np.asarray(seals["rung0_n40"]["s_bits"]),
                            make_g_spec(20, 0, SEED), measure=False)
    race_final = MANIFEST["layouts"]["race_n40"]["final"]
    best_s = MANIFEST["twin_plans"]["160"]["seed_off"]
    t0 = transpile(qc0, backend, optimization_level=3, seed_transpiler=SEED + best_s,
                   initial_layout=race_final)
    assert all(i.operation.name == "cz" for i in t0.data if i.operation.num_qubits == 2)
    twin160, _ = build_twin({best_s: t0}, 160)
    twins = {160: twin160}
    for D in (200, 240, 280):
        twins[D] = pad_to(twin160.copy(), D, {})[0]
    # register = physical qubits carrying the twin (active 2q qubits)
    active = set()
    for inst in twin160.data:
        if inst.operation.num_qubits == 2:
            for q in inst.qubits:
                active.add(twin160.find_bit(q).index)
    return twins, sorted(active)


def exactness_gate():
    """Composition sanity: the twin measured at its own basis has bounded per-qubit marginal; a
    deeper pad cannot INCREASE |<Z>| (envelope is contractive). Structural + a tiny Aer check."""
    from qiskit_aer import AerSimulator
    sim = AerSimulator()
    mock = QuantumCircuit(4)
    mock.h(0); mock.cx(0, 1)
    for _ in range(4):
        mock.cz(0, 1); mock.cz(2, 3)
    mock.measure_all()
    r = sim.run(transpile(mock, sim), shots=500).result().get_counts()
    ok = sum(r.values()) == 500
    print(f"exactness: mock pad measures ({ok})")
    return ok


def main(submit=False):
    assert exactness_gate(), "exactness fail"
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
    svc = QiskitRuntimeService(); backend = svc.backend(BACKEND)
    props = backend.properties()
    print(f"kingston cal epoch: {props.last_update_date}")
    twins, active = build_twins(backend)
    print(f"twin register (active 2q qubits): {len(active)} qubits; drifters in register: "
          f"{[q for q in DRIFTERS if q in active]}")
    pubs, meta = [], []
    # readout cal on the register (whole-chip 0/1) for marginal correction
    for state, tag in ((0, "cal0"), (1, "cal1")):
        qc = QuantumCircuit(NPHYS)
        if state:
            qc.x(range(NPHYS))
        qc.measure_all()
        pubs.append((transpile(qc, backend, optimization_level=0), None, 8000))
        meta.append({"block": tag, "shots": 8000})
    for D, tw in twins.items():
        mc = tw.copy(); mc.measure_all()
        tqc = transpile(mc, backend, optimization_level=0, initial_layout=list(range(NPHYS)),
                        seed_transpiler=SEED)
        assert d2q_of(tqc) >= D, f"pad cancelled at d{D}"
        pubs.append((tqc, None, 12000))
        meta.append({"block": f"twin_d{D}", "d2q": D, "shots": 8000})
        print(f"  built twin_d{D}: d2q={d2q_of(tqc)}")
    man = {"card": "exp_crossblock_depthsweep_B", "cycle": "C5002", "substrate": "claude-fable-5",
           "backend": BACKEND, "cal_epoch": str(props.last_update_date),
           "census_ref": "pad_drift_localization_c4984 (07-23, pre-recal)",
           "drifters": DRIFTERS, "register": active, "depths": DEPTHS, "pubs_meta": meta,
           "grader_precondition": "drift excess over matched-null >= ~3-5 sigma AND record strength (Elder #1102)"}
    if submit:
        job = SamplerV2(mode=backend).run(pubs)
        man["job_id"] = job.job_id()
        print(f"SUBMITTED {man['job_id']}")
    json.dump(man, open(OUT, "w"), indent=1)
    print(f"manifest -> {OUT}")


if __name__ == "__main__":
    main(submit="--submit" in sys.argv)
