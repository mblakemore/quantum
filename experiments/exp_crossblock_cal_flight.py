#!/usr/bin/env python3
"""Cross-block CAL BLOCK flight — G3'' (lambda_hold on the witness subspace + fold gate).

Whisper C4998 (substrate claude-fable-5). Card: docs/exp-crossblock-overlap-prereg-DRAFT-whisper-c4998.md
+ docs/exp-crossblock-flightspec-addendum-whisper-c4998.md. Creator GO general#860.
Elder's null-validity gate (general#865): the cal must measure the HOLD register's off-diagonal
coherence decay THROUGH the pad (witness subspace), echo on — not generic T1.

Circuits (ibm_kingston, ~52k shots total, est <10 QPU-s):
  cal_all0 / cal_all1   : readout cal on the cal+probe qubits (10k each).
  ramsey_pad            : cal qubits {74,79,22,44,6,8} in |+>, XY4 echo interleaved at quarter points
                          of the EXACT twin_220 pad running on the flown 40q register, H, measure.
                          -> lambda_hold,witness per cal qubit WITH pad crosstalk.
  ramsey_idle           : same skeleton, pad replaced by equivalent-duration delays -> intrinsic T2
                          component (separates crosstalk from idle decay).
  bell_pad              : Bell pairs (73-74, 23-22, 45-46, 7-6; all direct) prepared PRE-pad, twin_220
                          runs, Bell-basis (CNOT,H) measure -> joint probe-channel x ancilla
                          survival per site (margin input for adaptive-N).
  bell_idle             : Bell pairs + equivalent delay (no pad) -> Bell-survival baseline.

Reconstruction: twin_220 rebuilt from the curve flight's own builders (SEED 2026072307, original
seals file present), manifest layout pinned. EPOCH NOTE: today's routing adds actives {16,46} vs the
flown twin register (calibration-aware transpile drift) — the REBUILT circuit is the canonical
context for the whole flight (cal + main block use the same build); whether today's context still
drifts is measured by bell_pad itself (the card's calibration-epoch re-scout rule, discharged here).
Exactness gate: the composition logic is validated end-to-end on a small mock pad with Aer
(deterministic outcomes), plus structural asserts on the real 156q circuits. Fold gate (frozen):
lambda_hold,witness < 0.6 on the best hold candidate per site -> MAIN BLOCK FOLDS.
"""
import json, os, sys, math
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
QROOT = os.path.join(HERE, "..")

from exp_hss_race_flight import fold_circuit, d2q_of, to_basis_only
from exp_hss_race3_flight import two_q_layers
from exp_hss_generator import make_g_spec, build_hss_circuit
from exp_rhot_curve_flight import verify_seals, build_twin, pad_to
from qiskit import QuantumCircuit, transpile
from qiskit.circuit import Delay

SEED = 2026072307
BACKEND_NAME = "ibm_kingston"
NPHYS = 156
MANIFEST = json.load(open(os.path.join(QROOT, "results", "exp_rhot_curve_flight_manifest.json")))
REGISTER = set(MANIFEST["layouts"]["twin_src"]["final"])   # the TWIN register (the race layout was the wrong set — caught by the drift assert)
CAL_QUBITS = [74, 79, 22, 44, 6, 8]  # hold candidates outside the REBUILT active set (16,46 taken by today's routing — epoch drift, logged)
BELL_PAIRS = [(73, 74, []), (23, 22, []), (45, 44, []), (7, 6, [])]  # all DIRECT; 26/53 landlocked -> dropped; 46->44 per epoch routing drift
D2Q_TARGET = 220
T_2Q_NS = 68.0                                     # cz gate_length (calib snapshot c4998)
OUT_MANIFEST = os.path.join(QROOT, "results", "exp_crossblock_cal_manifest.json")


def rebuild_twin220(backend):
    """Rebuild the d2q=220 twin on the flown register (manifest layout pinned)."""
    seals = verify_seals()
    qc0 = build_hss_circuit(20, np.asarray(seals["rung0_n40"]["s_bits"]),
                            make_g_spec(20, 0, SEED), measure=False)
    race_final = MANIFEST["layouts"]["race_n40"]["final"]
    best_s = MANIFEST["twin_plans"]["160"]["seed_off"]      # flown twin source seed
    t0 = transpile(qc0, backend, optimization_level=3, seed_transpiler=SEED + best_s,
                   initial_layout=race_final)
    assert all(i.operation.name == "cz" for i in t0.data if i.operation.num_qubits == 2)
    twin_base, plan0 = build_twin({best_s: t0}, 160)
    twin_220, plan = pad_to(twin_base.copy(), D2Q_TARGET, {"from": "twin_base"})
    reg_now = set(int(x) for x in twin_220.layout.final_index_layout(filter_ancillas=True)) \
        if twin_220.layout else set(q._index for inst in twin_220.data for q in inst.qubits
                                    if inst.operation.num_qubits == 2)
    # register drift check (cal fidelity requirement): active 2q qubits within flown register
    active = set()
    for inst in twin_220.data:
        if inst.operation.num_qubits == 2:
            for q in inst.qubits:
                active.add(twin_220.find_bit(q).index)
    drift = active - REGISTER
    return twin_220, plan, {"active_2q_qubits": sorted(active), "outside_flown_register": sorted(drift)}


def chunk_indices(circ, n_chunks=4):
    """Split instruction indices into n_chunks with ~equal 2q-gate counts."""
    idx2q = [i for i, inst in enumerate(circ.data) if inst.operation.num_qubits == 2]
    total = len(idx2q)
    bounds, per = [], total / n_chunks
    for c in range(1, n_chunks):
        bounds.append(idx2q[min(int(c * per), total - 1)])
    return bounds  # instruction indices where echo pulses go BEFORE


def compose_ramsey(pad_circ, cal_qubits, idle_mode=False, nphys=NPHYS):
    """156q circuit: |+> prep on cal qubits, pad (or matched delay) with XY4 interleave, H, measure."""
    qc = QuantumCircuit(nphys, len(cal_qubits))
    for q in cal_qubits:
        qc.h(q)
    bounds = chunk_indices(pad_circ) if not idle_mode else None
    pulses = ["x", "y", "x", "y"]
    if idle_mode:
        # matched wall-duration: d2q layers * (t2q + ~1q overhead); split in 4 delay chunks
        n2q_layers = d2q_of(pad_circ)
        chunk_ns = n2q_layers * (T_2Q_NS + 16.0) / 4.0
        for p in pulses:
            for q in cal_qubits:
                qc.delay(int(chunk_ns), q, unit="ns")
                getattr(qc, p)(q)
    else:
        b_iter, next_b = iter(bounds), None
        next_b = next(b_iter, None)
        pulse_i = 0
        for i, inst in enumerate(pad_circ.data):
            if next_b is not None and i == next_b and pulse_i < 3:
                for q in cal_qubits:
                    getattr(qc, pulses[pulse_i])(q)
                pulse_i += 1
                next_b = next(b_iter, None)
            qs = [pad_circ.find_bit(q).index for q in inst.qubits]
            qc.append(inst.operation, [qc.qubits[x] for x in qs])
        for q in cal_qubits:   # final pulse closes XY4
            getattr(qc, pulses[3])(q)
    for q in cal_qubits:
        qc.h(q)
    for ci, q in enumerate(cal_qubits):
        qc.measure(q, ci)
    return qc


def compose_bell(pad_circ, pairs, idle_mode=False, nphys=NPHYS):
    """Bell pairs pre-pad (routed), pad (or delay), Bell-basis measure."""
    qc = QuantumCircuit(nphys, 2 * len(pairs))
    for probe, anc, via in pairs:
        qc.h(probe)
        if not via:
            qc.cx(probe, anc)
        else:
            # relay: CX(p,v), CX(v,a), CX(p,v) leaves a clean Bell on (probe,anc), v back to |0>
            # (verified in the exactness gate: routed pair must measure deterministic '00')
            v = via[0]
            qc.cx(probe, v)
            qc.cx(v, anc)
            qc.cx(probe, v)
    if idle_mode:
        n2q_layers = d2q_of(pad_circ)
        for probe, anc, via in pairs:
            qc.delay(int(n2q_layers * (T_2Q_NS + 16.0)), anc, unit="ns")
            qc.delay(int(n2q_layers * (T_2Q_NS + 16.0)), probe, unit="ns")
    else:
        for inst in pad_circ.data:
            qs = [pad_circ.find_bit(q).index for q in inst.qubits]
            qc.append(inst.operation, [qc.qubits[x] for x in qs])
    ci = 0
    for probe, anc, via in pairs:
        qc.cx(probe, anc)
        qc.h(probe)
        qc.measure(probe, ci); qc.measure(anc, ci + 1)
        ci += 2
    return qc


def exactness_gate():
    """Composition logic end-to-end on a small mock pad, noiseless Aer: deterministic outcomes."""
    from qiskit_aer import AerSimulator
    sim = AerSimulator()
    mock = QuantumCircuit(9)
    for _ in range(8):                       # mock pad: CZ layers on qubits 0-4
        mock.cz(0, 1); mock.cz(2, 3)
        mock.rz(0.3, 4)
    # Ramsey skeleton on cal qubits 5,6 (outside mock register 0-4)
    r = compose_ramsey(mock, [5, 6], idle_mode=False, nphys=9)
    res = sim.run(transpile(r, sim), shots=400).result().get_counts()
    ok1 = set(res.keys()) == {"00"}
    r2 = compose_ramsey(mock, [5, 6], idle_mode=True, nphys=9)
    res2 = sim.run(transpile(r2, sim), shots=400).result().get_counts()
    ok2 = set(res2.keys()) == {"00"}
    # Bell skeleton: direct pair (0->skip register: use 5,6) and routed pair (5,7 via 6)
    b = compose_bell(mock, [(5, 6, []), (7, 8, [])], idle_mode=True, nphys=9)
    resb = sim.run(transpile(b, sim), shots=400).result().get_counts()
    ok3 = set(resb.keys()) == {"0000"}
    mockR = QuantumCircuit(9)
    bR = compose_bell(mockR, [(5, 8, [6])], idle_mode=True, nphys=9)
    resR = sim.run(transpile(bR, sim), shots=400).result().get_counts()
    ok4 = set(resR.keys()) == {"00"}
    print(f"exactness: ramsey_pad={ok1} ramsey_idle={ok2} bell_direct={ok3} bell_routed={ok4}")
    return ok1 and ok2 and ok3 and ok4


def main(submit=False):
    assert exactness_gate(), "EXACTNESS GATE FAIL — no submission"
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
    svc = QiskitRuntimeService()
    backend = svc.backend(BACKEND_NAME)
    twin_220, plan, drift = rebuild_twin220(backend)
    print(f"twin_220 rebuilt: d2q={d2q_of(twin_220)} pad_plan={plan} "
          f"register drift={drift['outside_flown_register']}")
    assert d2q_of(twin_220) == D2Q_TARGET
    for cq in CAL_QUBITS:
        assert cq not in drift["active_2q_qubits"], f"cal qubit {cq} collides with active register!"

    pubs, meta = [], []
    ro0 = QuantumCircuit(NPHYS); ro0.measure_all()
    ro1 = QuantumCircuit(NPHYS); ro1.x(range(NPHYS)); ro1.measure_all()
    for qc, tag in ((ro0, "cal_all0"), (ro1, "cal_all1")):
        pubs.append((transpile(qc, backend, optimization_level=0), None, 10000))
        meta.append({"block": tag, "shots": 10000})
    builds = [
        ("ramsey_pad", compose_ramsey(twin_220, CAL_QUBITS, idle_mode=False), 8000),
        ("ramsey_idle", compose_ramsey(twin_220, CAL_QUBITS, idle_mode=True), 8000),
        ("bell_pad", compose_bell(twin_220, BELL_PAIRS, idle_mode=False), 8000),
        ("bell_idle", compose_bell(twin_220, BELL_PAIRS, idle_mode=True), 8000),
    ]
    for tag, qc, shots in builds:
        # optimization_level=0: BASIS TRANSLATION ONLY — any optimizer cancels the L.L=I pad
        # (caught in dry-run: opt=1 collapsed d2q 220->66 by CZ.CZ cancellation)
        tqc = transpile(qc, backend, optimization_level=0, seed_transpiler=SEED,
                        initial_layout=list(range(NPHYS)))
        if tag.endswith("_pad"):
            assert d2q_of(tqc) >= D2Q_TARGET, f"{tag}: pad cancelled in transpile (d2q={d2q_of(tqc)})"
        pubs.append((tqc, None, shots))
        meta.append({"block": tag, "shots": shots, "d2q": d2q_of(tqc)})
        print(f"  built {tag}: d2q={d2q_of(tqc)}")
    man = {"card": "exp_crossblock_cal", "cycle": "C4998", "substrate": "claude-fable-5",
           "backend": BACKEND_NAME, "register_drift": drift, "pad_plan": plan,
           "cal_qubits": CAL_QUBITS, "bell_pairs": [list(p[:2]) + [p[2]] for p in BELL_PAIRS],
           "pubs_meta": meta, "fold_gate": "lambda_hold_witness < 0.6 -> main block folds",
           "seed": SEED}
    if submit:
        sampler = SamplerV2(mode=backend)
        job = sampler.run(pubs)
        man["job_id"] = job.job_id()
        print(f"SUBMITTED {man['job_id']}")
    json.dump(man, open(OUT_MANIFEST, "w"), indent=1)
    print(f"manifest -> {OUT_MANIFEST}")


if __name__ == "__main__":
    main(submit="--submit" in sys.argv)
