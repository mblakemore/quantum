#!/usr/bin/env python3
"""Exp238 — THE FULL CODE: one code that corrects an ARBITRARY single-qubit error. C4916.

The summit of the correcting-code stair (exp236 bit-flip, exp237 phase-flip). The 9-qubit SHOR code
literally folds those two rungs into one: an inner bit-flip repetition inside an outer phase-flip
repetition, so a single X, Y OR Z error on ANY of the 9 qubits is identified and FIXED. This is the
CAPABILITY demo — "the code corrects any single-qubit error, at X% on silicon" — NOT a QEC-threshold
claim (the injected error is recovered in software essentially for free; the hardware number is set by
the ~16-CNOT encode+decode, not by the error). The threshold question — does the code's own machinery
fix more than it introduces — is a SEPARATE flight (logical memory vs bare over matched wall-clock).

METHOD (coherent decode + syndrome recovery, calibrated on the statevector so it cannot be wired
wrong silently): encode |psi_L>; inject a known Pauli P on qubit e; apply the INVERSE encoder (which
returns the logical qubit to q0 and writes the error's syndrome onto q1..8); measure; a software
recovery table (built from the noiseless simulator) reads the syndrome and fixes q0 — deterministic,
every shot kept. Two logical bases are flown so every error type is genuinely EXERCISED, not waved at:
  TEST A (Z basis, |0_L>/|1_L>): sensitive to BIT-flip damage — catches X and Y errors.
  TEST B (X basis, |+_L>/|-_L>): sensitive to PHASE damage — catches Z and Y errors.
Together: X caught in A, Z caught in B, Y in both -> arbitrary single-qubit error corrected.

BASELINES (what makes HELD mean something — advisor C4916):
  - NO-ERROR coded floor: encode+decode with zero injected error. The protocol's own noise floor and
    the honest headline (how far ibm_fez sits from a clean logical qubit). Corrected can't beat this.
  - UNCORRECTED-after-decode: same counts, skip the software recovery. Proves the recovery is
    load-bearing. Below threshold, a NOISY syndrome mis-corrects good shots and corrected can fall
    BELOW uncorrected — that crossover is pre-registered as an informative result, not a failure.
  - BARE qubit under the error (~0): kept for continuity with 236/237 (the weak baseline).

FROZEN GATES (margins, NOT an absolute-fidelity cliff — the 237 lesson; checked in selftest):
  G1_RECOVERY_LOAD_BEARING: over the damaging errors (X,Y in A; Z,Y in B), mean corrected - mean
     uncorrected >= 0.15 — the syndrome recovery actively fixes the damage.
  G2_RECOVERS_TO_FLOOR: mean corrected (damaging errors) >= no-error floor - 0.15 — the error is
     genuinely fixed back toward the clean-logical floor, not merely improved.
  Registered verdict = G1 and G2. CAPABILITY claim only; explicitly NOT a threshold claim.
  REPORTED: no-error floor (headline), crossover count (corrected<uncorrected = below-threshold
     mis-correction), bare (~0).
SCOPE: Shor [[9,1,3]], one representative error qubit per block {0,3,6} x {X,Y,Z} (+none) — the
  frugal set that still substantiates "arbitrary single-qubit" (each block + each Pauli type). Coherent
  decode is destructive (single shot per prep); the code corrects, it does not yet run FT gates or
  distill. Textbook Shor code; contribution = the campaign's first code correcting an ARBITRARY
  single-qubit error, folding 236+237, with honest capability-not-threshold framing. QPU-frugal.
BUDGET CHECK (C4887): deep (16-CNOT encode + 16 decode). No-error floor reported, not assumed 1.
Usage: --selftest | --submit [--backend ibm_fez --shots 8000] | --decode
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

ERR_QUBITS = (0, 3, 6)                 # one representative per Shor block
PAULIS = ("none", "X", "Y", "Z")
# (test, logical inputs, readout basis, calibration input, damaging Paulis)
TESTS = {
    "A": {"inputs": ("0", "1"), "basis": "Z", "calib": "0", "damaging": ("X", "Y")},
    "B": {"inputs": ("+", "-"), "basis": "X", "calib": "+", "damaging": ("Z", "Y")},
}


def _prep(qc, inp):
    if inp == "1": qc.x(0)
    elif inp == "+": qc.h(0)
    elif inp == "-": qc.x(0); qc.h(0)


def _encode(qc):
    qc.cx(0, 3); qc.cx(0, 6)                       # outer phase-flip repetition
    qc.h(0); qc.h(3); qc.h(6)
    qc.cx(0, 1); qc.cx(0, 2)                        # inner bit-flip repetition (per block)
    qc.cx(3, 4); qc.cx(3, 5)
    qc.cx(6, 7); qc.cx(6, 8)


def _decode(qc):                                    # exact inverse of _encode
    qc.cx(6, 7); qc.cx(6, 8)
    qc.cx(3, 4); qc.cx(3, 5)
    qc.cx(0, 1); qc.cx(0, 2)
    qc.h(0); qc.h(3); qc.h(6)
    qc.cx(0, 3); qc.cx(0, 6)


def _apply(qc, pauli, e):
    if pauli == "X": qc.x(e)
    elif pauli == "Y": qc.y(e)
    elif pauli == "Z": qc.z(e)


def circuit(inp, pauli, e, basis):
    qc = QuantumCircuit(9, 9)
    _prep(qc, inp)
    _encode(qc); qc.barrier()
    if pauli != "none": _apply(qc, pauli, e); qc.barrier()
    _decode(qc); qc.barrier()
    if basis == "X": qc.h(0)                        # logical q0 X-basis readout
    for q in range(9): qc.measure(q, q)
    return qc


def bare_circuit(basis):
    qc = QuantumCircuit(1, 1)
    if basis == "X":
        qc.h(0); qc.z(0); qc.h(0)                   # |+> under Z -> flips in X readout
    else:
        qc.x(0)                                     # |0> under X -> flips in Z readout
    qc.measure(0, 0)
    return qc


def _q0_syn(bitstr):
    b = bitstr.replace(" ", "")
    q0 = int(b[-1]); syn = tuple(int(b[-1 - q]) for q in range(1, 9))
    return q0, syn


def _want(inp):
    return 1 if inp in ("1", "-") else 0


def _bare_fid(counts):
    """single-qubit bare readout: fidelity to the intended (unflipped) value 0."""
    ok = tot = 0
    for s, n in counts.items():
        tot += n
        if int(s.replace(" ", "")[-1]) == 0: ok += n
    return ok / tot


def _uncorr_fid(counts, inp):
    want = _want(inp); ok = tot = 0
    for s, n in counts.items():
        q0, _ = _q0_syn(s); tot += n
        if q0 == want: ok += n
    return ok / tot


def _corr_fid(counts, inp, table):
    want = _want(inp); ok = tot = 0
    for s, n in counts.items():
        q0, syn = _q0_syn(s); tot += n
        logical = q0 ^ table.get(syn, 0)            # unseen syndrome -> no correction (honest)
        if logical == want: ok += n
    return ok / tot


def _calibrate(sim, test):
    """On the noiseless statevector: build the syndrome->recovery table AND determine which errors
    are DAMAGING to this test's observable (uncorrected readout flipped). Both are deterministic and
    frozen (hardware-independent), so 'damaging' is a legitimate pre-registered set, not fit to data."""
    cfg = TESTS[test]; ci = cfg["calib"]; w = _want(ci); table = {}; damaging = []
    for pauli in PAULIS:
        for e in (ERR_QUBITS if pauli != "none" else (0,)):
            c = sim.run(circuit(ci, pauli, e, cfg["basis"]), shots=4000).result().get_counts()
            for s, _ in c.items():
                q0, syn = _q0_syn(s)
                table[syn] = q0 ^ w                 # flip that maps q0 back to want
            if pauli != "none" and _uncorr_fid(c, ci) < 0.5:
                damaging.append((pauli, e))          # this error corrupts the uncorrected observable
    return table, damaging


def selftest():
    from qiskit_aer import AerSimulator
    sim = AerSimulator(); shots = 8000
    print("Exp238 selftest | THE FULL CODE — Shor [[9,1,3]], arbitrary single-qubit error")
    dmg_paulis = set()
    for test in ("A", "B"):
        cfg = TESTS[test]; table, damaging = _calibrate(sim, test)
        worst_c = 1.0; worst_dmg_uncorr = 1.0
        for inp in cfg["inputs"]:                    # cross-check: table (from calib inp) fixes BOTH
            for pauli in PAULIS:
                for e in (ERR_QUBITS if pauli != "none" else (0,)):
                    c = sim.run(circuit(inp, pauli, e, cfg["basis"]), shots=shots).result().get_counts()
                    cf = _corr_fid(c, inp, table); worst_c = min(worst_c, cf)
                    if (pauli, e) in damaging:
                        worst_dmg_uncorr = min(worst_dmg_uncorr, 1 - _uncorr_fid(c, inp))
        dmg_paulis |= {p for p, _ in damaging}
        print(f"  TEST {test} ({cfg['basis']} basis): worst corrected {worst_c:.3f}; damaging errors "
              f"{sorted(set(damaging))}; worst damaging UNcorrected error-rate {worst_dmg_uncorr:.3f}")
        assert worst_c > 0.98, f"test {test}: code must correct EVERY single-qubit error noiselessly"
        assert damaging, f"test {test}: must have errors that actually corrupt the observable"
        assert worst_dmg_uncorr > 0.98, (f"test {test}: damaging errors must FLIP the uncorrected "
                                         "readout (recovery must do real work — not a tautology)")
    assert dmg_paulis == {"X", "Y", "Z"}, (f"the two tests must together exercise ALL of X,Y,Z to "
                                           f"substantiate 'arbitrary single-qubit'; got {dmg_paulis}")
    print("SELFTEST PASS: the Shor code recovers the logical qubit from EVERY single-qubit Pauli (X,Y,Z "
          f"on any block) deterministically; the two bases together exercise all of {sorted(dmg_paulis)}; "
          "recovery is load-bearing (damaging errors flip uncorrected). Claim lives in the hardware numbers.")


def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    order = []
    for test in ("A", "B"):
        cfg = TESTS[test]
        for inp in cfg["inputs"]:
            for pauli in PAULIS:
                for e in (ERR_QUBITS if pauli != "none" else (0,)):
                    order.append(["log", test, inp, pauli, str(e)])
        order.append(["bare", test, cfg["basis"], "-", "-"])
    def build(o):
        if o[0] == "log":
            _, test, inp, pauli, e = o; return circuit(inp, pauli, int(e), TESTS[test]["basis"])
        return bare_circuit(TESTS[o[1]]["basis"])
    builds = [build(o) for o in order]
    circuits = [transpile(qc, backend=backend, optimization_level=3, seed_transpiler=0) for qc in builds]
    n2s = [sum(1 for i in c.data if i.operation.num_qubits == 2) for c in circuits]
    print(f"  DEPTH CHECK: {len(circuits)} circuits, 2q {min(n2s)}-{max(n2s)}")
    job = SamplerV2(mode=backend).run(circuits, shots=shots)
    out = os.path.join(HERE, "..", "results", "exp238_the_full_code_manifest.json")
    man = {"exp": 238, "slug": "the_full_code", "backend": backend_name, "shots": shots,
           "job_id": job.job_id(), "order": order,
           "prereg": {"G1_recovery_load_bearing": "mean corrected - mean uncorrected >= 0.15 over damaging errors",
                      "G2_recovers_to_floor": "mean corrected (damaging) >= no-error floor - 0.15",
                      "registered_verdict": "G1 and G2 — CAPABILITY (arbitrary single-qubit error), NOT threshold",
                      "reported": "no-error floor (headline), crossover count (corrected<uncorrected), bare(~0)",
                      "scope": "Shor [[9,1,3]], errors {X,Y,Z} x {0,3,6} + none, two logical bases; "
                               "coherent decode + sim-calibrated syndrome recovery; capability not threshold"}}
    json.dump(man, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits, {shots} shots) -> {out}")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_aer import AerSimulator
    man = json.load(open(os.path.join(HERE, "..", "results", "exp238_the_full_code_manifest.json")))
    svc = _get_ibm_service(); res = svc.job(man["job_id"]).result()
    sim = AerSimulator()
    cal = {t: _calibrate(sim, t) for t in ("A", "B")}
    raw = {}
    for idx, o in enumerate(man["order"]):
        r0 = res[idx]; reg = list(r0.data.keys())[0]
        raw[tuple(o)] = getattr(r0.data, reg).get_counts()
    print(f"Exp238 THE FULL CODE decode | job {man['job_id']}")
    corr_dmg, uncorr_dmg, floors, crossover = [], [], {}, 0
    for test in ("A", "B"):
        cfg = TESTS[test]; table, damaging = cal[test]
        f_no = []
        for inp in cfg["inputs"]:
            f_no.append(_corr_fid(raw[("log", test, inp, "none", "0")], inp, table))
        floors[test] = float(np.mean(f_no))
        print(f"  TEST {test} ({cfg['basis']} basis) no-error coded FLOOR: {floors[test]:.3f}; "
              f"damaging errors {sorted(set(damaging))}")
        for inp in cfg["inputs"]:
            for (pauli, e) in damaging:
                c = raw[("log", test, inp, pauli, str(e))]
                cf = _corr_fid(c, inp, table); uf = _uncorr_fid(c, inp)
                corr_dmg.append(cf); uncorr_dmg.append(uf)
                if cf < uf: crossover += 1
        bare = _bare_fid(raw[("bare", test, cfg["basis"], "-", "-")])
        print(f"  TEST {test} bare-under-error fidelity: {bare:.3f}")
    mc, mu = float(np.mean(corr_dmg)), float(np.mean(uncorr_dmg))
    floor = float(np.mean(list(floors.values())))
    g1 = (mc - mu) >= 0.15
    g2 = mc >= (floor - 0.15)
    print(f"\n  mean corrected (damaging) {mc:.3f} | mean uncorrected {mu:.3f} | no-error floor {floor:.3f}")
    print(f"  crossover (corrected<uncorrected, below-threshold mis-correction): {crossover}/{len(corr_dmg)} cases")
    print(f"\nG1 RECOVERY LOAD-BEARING: corrected - uncorrected = {mc-mu:+.3f} >= 0.15 {'OK' if g1 else 'MISS'}")
    print(f"G2 RECOVERS TO FLOOR: corrected {mc:.3f} >= floor-0.15 = {floor-0.15:.3f} {'OK' if g2 else 'MISS'}")
    ok = g1 and g2
    win = ("THE FULL CODE — the Shor [[9,1,3]] corrects an ARBITRARY single-qubit error (X, Y and Z on "
           "any block), folding the bit-flip (236) and phase-flip (237) rungs into one code, recovery "
           "load-bearing and returning to the protocol floor, on silicon. CAPABILITY demonstrated — the "
           "QEC-threshold question (does the code's own machinery fix more than it introduces) is the "
           "separate next flight")
    print(f"VERDICT: {win if ok else 'NOT HELD (accounting above; capability-not-threshold framing stands either way)'}")
    json.dump({"job_id": man["job_id"], "floors": floors, "mean_corrected": mc, "mean_uncorrected": mu,
               "no_error_floor": floor, "crossover": crossover, "n_damaging": len(corr_dmg),
               "g1": bool(g1), "g2": bool(g2), "verdict_ok": bool(ok)},
              open(os.path.join(HERE, "..", "results", "exp238_the_full_code_decode.json"), "w"), indent=1)
    print("-> results/exp238_the_full_code_decode.json")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true"); ap.add_argument("--submit", action="store_true")
    ap.add_argument("--decode", action="store_true")
    ap.add_argument("--backend", default="ibm_fez"); ap.add_argument("--shots", type=int, default=8000)
    a = ap.parse_args()
    if a.selftest: selftest()
    elif a.submit: submit(a.backend, a.shots)
    elif a.decode: decode()
    else: ap.print_help()
