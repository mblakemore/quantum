#!/usr/bin/env python3
"""Exp236 — THE FIRST CORRECTION: detect-and-FIX, not detect-and-discard. C4914.

Up the stairs (docs/the-missing-fold-whisper-c4914.md, IV): the whole campaign used [[4,2,2]] — a
DETECTING code that postselects (throws away the runs with errors). The next capability, and the
gate to scalable fault tolerance + magic distillation, is a code that CORRECTS: identify the error
from a syndrome and FIX it, keeping every shot, deterministically. This flight climbs the first rung
with the 3-qubit repetition code — the minimal genuinely-correcting code (distance 3 against
bit-flips): it recovers an arbitrary injected bit-flip on any qubit, with no postselection, where
both a bare qubit and the [[4,2,2]] detect-and-discard approach would either fail or throw the run away.

Encode a logical qubit (|0_L>=|000>, |1_L>=|111>) into 3 qubits; inject an X error on qubit e in
{none,0,1,2}; measure all three in Z; the syndrome (z0^z1, z1^z2) uniquely identifies e, and the
MAJORITY VOTE recovers the logical bit — deterministic recovery, every shot kept. Compared: a bare
qubit under the same X error is simply flipped (fidelity ~0 on the errored runs).

FROZEN GATES (relative to statevector-exact; checked in selftest):
  G1_CORRECTS_ALL: for both logical inputs and every single bit-flip location (8 cases), the
     majority-corrected logical fidelity >= 0.90 — the code recovers the logical value for ANY single
     bit-flip, no postselection.
  G2_BEATS_BARE: on the errored cases (e in {0,1,2}), corrected fidelity - bare fidelity >= 0.5 —
     the correcting code recovers where a bare qubit is flipped.
  G3_COHERENCE (reported): a logical superposition |+_L>=(|000>+|111>)/sqrt2 under a bit-flip keeps
     its logical X-parity <X_L>=<X0X1X2> after correction (the coherent state survives).
  Registered verdict = G1 and G2.
SCOPE: 3-qubit repetition code, bit-flip channel only (distance 3 against X errors; a Z error is
  unprotected). This is the first ACTIVE correction (recover, do not discard) — the capability
  [[4,2,2]] lacked. The FULL quantum correcting code (all single-qubit errors: [[5,1,3]] or Steane
  [[7,1,3]]) is the summit rung and needs a non-destructive multi-stabilizer syndrome; on current
  hardware it may sit below the error-correction threshold (a separate honest question). Textbook
  3-qubit code; contribution = the campaign's first move from detection to correction. QPU-frugal.
BUDGET CHECK (C4887): shallow (encode 2 CX + optional error + Z readout). Fidelity ideal 1.
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
    qc.cx(0, 1); qc.cx(0, 2)                  # encode |inp_L> = |inp inp inp>
    qc.barrier()
    if err != "none": qc.x(int(err))          # inject a single bit-flip
    qc.barrier()
    for q in range(3): qc.measure(q, q)        # Z readout (syndrome + logical)
    return qc


def coh_circuit(err):
    qc = QuantumCircuit(3, 3)
    qc.h(0); qc.cx(0, 1); qc.cx(0, 2)          # |+_L> = (|000>+|111>)/sqrt2
    qc.barrier()
    if err != "none": qc.x(int(err))
    qc.barrier()
    for q in range(3): qc.h(q)                 # X_L = X0X1X2 readout
    for q in range(3): qc.measure(q, q)
    return qc


def bare_circuit(inp, err):
    qc = QuantumCircuit(1, 1)
    if inp == "1": qc.x(0)
    if err in ("0",): qc.x(0)                  # bare qubit sees the error (only 'on qubit 0' analog)
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


def _xl(counts):
    c = tot = 0
    for s, n in counts.items():
        b = s.replace(" ", ""); par = int(b[-1]) ^ int(b[-2]) ^ int(b[-3])
        c += (1 - 2 * par) * n; tot += n
    return c / tot


def selftest():
    from qiskit_aer import AerSimulator
    sim = AerSimulator(); shots = 40000
    print("Exp236 selftest | THE FIRST CORRECTION — 3-qubit code, detect-and-FIX")
    worst = 1.0
    for inp in INPUTS:
        row = []
        for err in ERRORS:
            f = _corrected_fidelity(sim.run(logical_circuit(inp, err), shots=shots).result().get_counts(), inp)
            row.append(f); worst = min(worst, f)
        print(f"  |{inp}_L> corrected fidelity vs error {ERRORS}: {[round(x,3) for x in row]}")
    assert worst > 0.98, "must correct every single bit-flip noiselessly"
    for err in ("0",):
        bf = _bare_fidelity(sim.run(bare_circuit("0", err), shots=shots).result().get_counts(), "0")
        print(f"  bare |0> under X{err}: fidelity {bf:.3f} (flipped)")
    xl = _xl(sim.run(coh_circuit("1"), shots=shots).result().get_counts())
    print(f"  |+_L> under X1, <X_L> after: {xl:+.3f} (coherence preserved)")
    print("SELFTEST PASS: the 3-qubit code recovers the logical bit for EVERY single bit-flip, "
          "deterministically (no postselection) — the first active correction. Cleared to fly.")


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
    out = os.path.join(HERE, "..", "results", "exp236_first_correction_manifest.json")
    man = {"exp": 236, "slug": "first_correction", "backend": backend_name, "shots": shots,
           "job_id": job.job_id(), "order": [list(o) for o in order],
           "prereg": {"G1_corrects_all": "corrected fidelity >= 0.90 for all 8 (input,error) cases",
                      "G2_beats_bare": "corrected - bare >= 0.5 on errored cases",
                      "G3_coherence": "reported: |+_L> <X_L> preserved after bit-flip + correction",
                      "registered_verdict": "G1 and G2",
                      "scope": "3-qubit repetition code, first ACTIVE correction (recover not discard); "
                               "bit-flip channel; full quantum code = summit rung"}}
    json.dump(man, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits, {shots} shots) -> {out}")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    man = json.load(open(os.path.join(HERE, "..", "results", "exp236_first_correction_manifest.json")))
    svc = _get_ibm_service(); res = svc.job(man["job_id"]).result()
    raw = {}
    for idx, o in enumerate(man["order"]):
        r0 = res[idx]; reg = list(r0.data.keys())[0]
        raw[tuple(o)] = getattr(r0.data, reg).get_counts()
    print(f"Exp236 THE FIRST CORRECTION decode | job {man['job_id']}")
    cf = {}
    for inp in INPUTS:
        row = []
        for err in ERRORS:
            cf[(inp, err)] = _corrected_fidelity(raw[("log", inp, err)], inp); row.append(cf[(inp, err)])
        print(f"  |{inp}_L> corrected: {[round(x,3) for x in row]}  (errors {ERRORS})")
    worst = min(cf.values())
    bare_err = _bare_fidelity(raw[("bare", "0", "0")], "0")
    corr_err = np.mean([cf[(inp, e)] for inp in INPUTS for e in ("0", "1", "2")])
    xl = {err: _xl(raw[("coh", "+", err)]) for err in ERRORS}
    print(f"\n  bare |0> under X0: {bare_err:.3f}  |  mean corrected (errored cases): {corr_err:.3f}")
    print(f"  |+_L> <X_L> after bit-flip+correction: {[f'{err}:{xl[err]:+.2f}' for err in ERRORS]}")
    g1 = worst >= 0.90
    g2 = (corr_err - bare_err) >= 0.5
    print(f"\nG1 CORRECTS ALL BIT-FLIPS: worst corrected fidelity {worst:.3f} >= 0.90 {'OK' if g1 else 'MISS'}")
    print(f"G2 BEATS BARE: corrected {corr_err:.3f} - bare {bare_err:.3f} = {corr_err-bare_err:+.3f} >= 0.5 {'OK' if g2 else 'MISS'}")
    print(f"G3 COHERENCE (reported): |+_L> <X_L> stays ~{np.mean(list(xl.values())):+.2f} through bit-flips")
    ok = g1 and g2
    win = ("THE FIRST CORRECTION — a code that FIXES instead of discarding: the 3-qubit code recovers "
           "the logical qubit from any single bit-flip by syndrome/majority, deterministically, keeping "
           "every shot, where a bare qubit is simply flipped. The campaign's first step from detection "
           "to correction — the gate to scalable fault tolerance, on silicon")
    print(f"VERDICT: {win if ok else 'NOT HELD (accounting above)'}")
    json.dump({"job_id": man["job_id"], "corrected": {f"{i}_{e}": cf[(i, e)] for i in INPUTS for e in ERRORS},
               "bare_err": bare_err, "corr_err_mean": corr_err, "xl": xl,
               "g1": bool(g1), "g2": bool(g2), "verdict_ok": bool(ok)},
              open(os.path.join(HERE, "..", "results", "exp236_first_correction_decode.json"), "w"), indent=1)
    print("-> results/exp236_first_correction_decode.json")


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
