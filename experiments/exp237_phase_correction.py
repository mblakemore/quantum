#!/usr/bin/env python3
"""Exp237 — THE PHASE CORRECTION: fix a Z error, the dual of the bit-flip code. C4915.

Rung 2 of the correcting-code stair (exp236-STATUS-certified.md, docs/the-missing-fold IV). Exp236
corrected BIT-flips (X) with the 3-qubit repetition code. Phase (Z) errors are the OTHER single-qubit
error channel — and on real silicon they are the DOMINANT one (dephasing / T2 < T1). This flight
climbs the dual rung: the 3-qubit PHASE-flip code, the H-conjugate of the repetition code, which
detects-and-FIXES an arbitrary single Z error, keeping every shot.

Logical |0_L>=|+++>, |1_L>=|--->. Encode = (bit-flip repetition) then H^3, so a physical Z error is
carried by H^3 back to an X error on |ppp>, where the MAJORITY VOTE recovers the logical bit — the
same syndrome correction as 236, now for the phase channel. A bare qubit in |+> under the same Z is
simply flipped to |-> (fidelity ~0 in the X readout).

Together with 236 this closes the pair: X-errors AND Z-errors both actively corrected. The SUMMIT rung
(a single code that corrects an ARBITRARY single-qubit error at once — X, Y and Z — the Shor 9-qubit
or Steane [[7,1,3]] code, which folds THIS rung and 236 into one) is the next climb and poses the real
open question: is current hardware above the QEC threshold?

FROZEN GATES (relative to statevector-exact; checked in selftest):
  G1_CORRECTS_ALL: for both logical inputs and every single Z-flip location (8 cases), the
     majority-corrected logical fidelity >= 0.90 — the code recovers the logical value for ANY single
     phase-flip, no postselection.
  G2_BEATS_BARE: on the errored cases (e in {0,1,2}), corrected fidelity - bare fidelity >= 0.5 — the
     phase-correcting code recovers where a bare |+> qubit is dephased/flipped.
  G3_STABILITY (reported): the complementary logical coherence <Z0Z1Z2> (the logical X-parity, which
     Z-errors leave untouched) stays ~+1 through correction — the fix does not disturb it.
  Registered verdict = G1 and G2.
SCOPE: 3-qubit phase-flip code, phase (Z) channel only (distance 3 against Z; an X error is
  unprotected — the exact dual of 236's bit-flip-only scope). Active correction (recover, not discard).
  The FULL quantum code (all single-qubit errors at once) = summit rung, needs a non-destructive
  multi-stabilizer syndrome and may sit below the hardware threshold (a separate honest question).
  Textbook phase-flip code; contribution = the campaign's second correcting rung, closing X+Z. Frugal.
BUDGET CHECK (C4887): shallow (encode 2 CX + H^3 + optional Z + H^3 + Z readout). Fidelity ideal 1.
Usage: --selftest | --submit [--backend ibm_fez --shots 8000] | --decode
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
INPUTS = ("0", "1")
ERRORS = ("none", "0", "1", "2")


def logical_circuit(inp, err):
    qc = QuantumCircuit(3, 3)
    if inp == "1": qc.x(0)
    qc.cx(0, 1); qc.cx(0, 2)                  # |ppp>
    qc.h(0); qc.h(1); qc.h(2)                 # -> phase-flip code |0_L>=|+++>, |1_L>=|--->
    qc.barrier()
    if err != "none": qc.z(int(err))          # inject a single PHASE flip
    qc.barrier()
    qc.h(0); qc.h(1); qc.h(2)                 # decode: H^3 carries Z_e -> X_e on |ppp>
    for q in range(3): qc.measure(q, q)        # Z readout -> majority vote recovers p
    return qc


def coh_circuit(err):
    # logical |+_L> = (|0_L>+|1_L>)/sqrt2 = (|+++>+|--->)/sqrt2 ; read logical X-parity <Z0Z1Z2>
    qc = QuantumCircuit(3, 3)
    qc.h(0); qc.cx(0, 1); qc.cx(0, 2)          # (|000>+|111>)/sqrt2
    qc.h(0); qc.h(1); qc.h(2)                  # H^3 -> (|+++>+|--->)/sqrt2
    qc.barrier()
    if err != "none": qc.z(int(err))
    qc.barrier()
    for q in range(3): qc.measure(q, q)         # <Z0Z1Z2> = logical X-parity (Z-error commutes)
    return qc


def bare_circuit(inp, err):
    qc = QuantumCircuit(1, 1)
    if inp == "1": qc.x(0)
    qc.h(0)                                     # bare |+> (the state a Z error attacks)
    if err in ("0",): qc.z(0)                   # the 'on qubit 0' analog phase flip
    qc.h(0)                                      # X-basis readout
    qc.measure(0, 0)
    return qc


def _corrected_fidelity(counts, inp):
    """majority-vote decode -> logical bit; fidelity to inp. Deterministic (all shots kept)."""
    want = int(inp); ok = tot = 0
    for s, n in counts.items():
        b = s.replace(" ", ""); v = [int(b[-1 - i]) for i in range(3)]
        logical = 1 if (v[0] + v[1] + v[2]) >= 2 else 0     # majority vote = syndrome correction
        tot += n
        if logical == want: ok += n
    return ok / tot


def _bare_fidelity(counts, inp):
    want = int(inp); ok = tot = 0
    for s, n in counts.items():
        tot += n
        if int(s.replace(" ", "")[-1]) == want: ok += n
    return ok / tot


def _zparity(counts):
    c = tot = 0
    for s, n in counts.items():
        b = s.replace(" ", ""); par = int(b[-1]) ^ int(b[-2]) ^ int(b[-3])
        c += (1 - 2 * par) * n; tot += n
    return c / tot


def selftest():
    from qiskit_aer import AerSimulator
    sim = AerSimulator(); shots = 40000
    print("Exp237 selftest | THE PHASE CORRECTION — 3-qubit phase-flip code, detect-and-FIX (Z)")
    worst = 1.0
    for inp in INPUTS:
        row = []
        for err in ERRORS:
            f = _corrected_fidelity(sim.run(logical_circuit(inp, err), shots=shots).result().get_counts(), inp)
            row.append(f); worst = min(worst, f)
        print(f"  |{inp}_L> corrected fidelity vs Z-error {ERRORS}: {[round(x,3) for x in row]}")
    assert worst > 0.98, "must correct every single phase-flip noiselessly"
    for err in ("0",):
        bf = _bare_fidelity(sim.run(bare_circuit("0", err), shots=shots).result().get_counts(), "0")
        print(f"  bare |+> under Z{err}: X-readout fidelity {bf:.3f} (flipped to |->)")
    zp = _zparity(sim.run(coh_circuit("1"), shots=shots).result().get_counts())
    print(f"  |+_L> under Z1, <Z0Z1Z2> after: {zp:+.3f} (complementary coherence undisturbed)")
    print("SELFTEST PASS: the 3-qubit phase-flip code recovers the logical bit for EVERY single "
          "Z-flip, deterministically (no postselection) — the dual of 236, closing X+Z. Cleared to fly.")


def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    order = ([("log", inp, err) for inp in INPUTS for err in ERRORS]
             + [("bare", "0", "0"), ("bare", "0", "none")]
             + [("coh", "+", err) for err in ERRORS])
    def build(k, inp, err):
        if k == "log": return logical_circuit(inp, err)
        if k == "bare": return bare_circuit(inp, err)
        return coh_circuit(err)
    builds = [build(*o) for o in order]
    circuits = [transpile(qc, backend=backend, optimization_level=3, seed_transpiler=0) for qc in builds]
    n2s = [sum(1 for i in c.data if i.operation.num_qubits == 2) for c in circuits]
    print(f"  DEPTH CHECK: {len(circuits)} circuits, 2q {min(n2s)}-{max(n2s)}")
    job = SamplerV2(mode=backend).run(circuits, shots=shots)
    out = os.path.join(HERE, "..", "results", "exp237_phase_correction_manifest.json")
    man = {"exp": 237, "slug": "phase_correction", "backend": backend_name, "shots": shots,
           "job_id": job.job_id(), "order": [list(o) for o in order],
           "prereg": {"G1_corrects_all": "corrected fidelity >= 0.90 for all 8 (input,Z-error) cases",
                      "G2_beats_bare": "corrected - bare >= 0.5 on errored cases",
                      "G3_stability": "reported: <Z0Z1Z2> (logical X-parity) undisturbed by correction",
                      "registered_verdict": "G1 and G2",
                      "scope": "3-qubit phase-flip code, phase (Z) channel; dual of 236; active "
                               "correction (recover not discard); full quantum code = summit rung"}}
    json.dump(man, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits, {shots} shots) -> {out}")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    man = json.load(open(os.path.join(HERE, "..", "results", "exp237_phase_correction_manifest.json")))
    svc = _get_ibm_service(); res = svc.job(man["job_id"]).result()
    raw = {}
    for idx, o in enumerate(man["order"]):
        r0 = res[idx]; reg = list(r0.data.keys())[0]
        raw[tuple(o)] = getattr(r0.data, reg).get_counts()
    print(f"Exp237 THE PHASE CORRECTION decode | job {man['job_id']}")
    cf = {}
    for inp in INPUTS:
        row = []
        for err in ERRORS:
            cf[(inp, err)] = _corrected_fidelity(raw[("log", inp, err)], inp); row.append(cf[(inp, err)])
        print(f"  |{inp}_L> corrected: {[round(x,3) for x in row]}  (Z-errors {ERRORS})")
    worst = min(cf.values())
    bare_err = _bare_fidelity(raw[("bare", "0", "0")], "0")
    corr_err = np.mean([cf[(inp, e)] for inp in INPUTS for e in ("0", "1", "2")])
    zp = {err: _zparity(raw[("coh", "+", err)]) for err in ERRORS}
    print(f"\n  bare |+> under Z0: {bare_err:.3f}  |  mean corrected (errored cases): {corr_err:.3f}")
    print(f"  |+_L> <Z0Z1Z2> through Z-errors: {[f'{err}:{zp[err]:+.2f}' for err in ERRORS]}")
    g1 = worst >= 0.90
    g2 = (corr_err - bare_err) >= 0.5
    print(f"\nG1 CORRECTS ALL PHASE-FLIPS: worst corrected fidelity {worst:.3f} >= 0.90 {'OK' if g1 else 'MISS'}")
    print(f"G2 BEATS BARE: corrected {corr_err:.3f} - bare {bare_err:.3f} = {corr_err-bare_err:+.3f} >= 0.5 {'OK' if g2 else 'MISS'}")
    print(f"G3 STABILITY (reported): <Z0Z1Z2> stays ~{np.mean(list(zp.values())):+.2f} through Z-errors")
    ok = g1 and g2
    win = ("THE PHASE CORRECTION — the dual of 236: the 3-qubit phase-flip code recovers the logical "
           "qubit from any single Z (phase) error by syndrome/majority in the X basis, deterministically, "
           "keeping every shot, where a bare |+> is dephased. With 236 the campaign now actively corrects "
           "BOTH single-qubit error channels — X and Z — the two halves the full quantum code folds into one")
    print(f"VERDICT: {win if ok else 'NOT HELD (accounting above)'}")
    json.dump({"job_id": man["job_id"], "corrected": {f"{i}_{e}": cf[(i, e)] for i in INPUTS for e in ERRORS},
               "bare_err": bare_err, "corr_err_mean": corr_err, "zparity": zp,
               "g1": bool(g1), "g2": bool(g2), "verdict_ok": bool(ok)},
              open(os.path.join(HERE, "..", "results", "exp237_phase_correction_decode.json"), "w"), indent=1)
    print("-> results/exp237_phase_correction_decode.json")


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
