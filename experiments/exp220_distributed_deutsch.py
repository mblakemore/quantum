#!/usr/bin/env python3
"""Exp220 — THE DISTRIBUTED ORACLE: Deutsch's algorithm across a shielded cut. C4908.

Horizons-5 P6 flight 4 — the first quantum algorithm, run distributed and error-corrected.

Deutsch's algorithm decides whether a one-bit function f is CONSTANT or BALANCED with a SINGLE
query, via phase kickback: query |+bar>, ancilla |-bar>, apply the oracle, measure the query in
X-bar. Constant -> <Xbar_q> = +1; balanced -> the kickback flips it to <Xbar_q> = -1.

THE TWIST: the query lives in shield A and the function's target (ancilla) lives in shield C — two
[[4,2,2]] error-corrected nodes that share NO gate. The BALANCED oracle is a DISTRIBUTED logical
CNOT welded across the cut by one classical bit (217/218 machinery, physical relay e_A=q8,e_B=q9).
So the algorithm's oracle is itself distributed: one query across the network decides the function.

Four oracles (all of Deutsch's f:{0,1}->{0,1}):
  f0 constant-0: identity                         -> <Xbar_q> = +1
  f1 constant-1: Xbar on ancilla (global phase)   -> <Xbar_q> = +1
  f2 balanced  f=x: distributed CNOT(q->a)        -> <Xbar_q> = -1
  f3 balanced  f=~x: distributed CNOT + Xbar on a -> <Xbar_q> = -1
Query result <Xbar_q>: +1 = constant, -1 = balanced. The distributed oracle across the cut flips it.

H-free: |+bar> and |-bar>=|+bar>+Zbar (Z0Z2) are direct preps; Xbar readout is a measurement.
Frame: the balanced oracle's distributed CNOT puts Z^z on the query (z=e_B in X); applied at decode
(flips the query's X-value). Query read Xbar1A=X0X1; per-block XXXX partial shield.

FROZEN GATES (relative to statevector-exact; checked in selftest):
  G1_CONSTANT: <Xbar_q> for BOTH constant oracles (f0,f1) >= +0.55, each >= 5 sigma over 0.
  G2_BALANCED: <Xbar_q> for BOTH balanced oracles (f2,f3) <= -0.55, each >= 5 sigma (magnitude).
  G3_SEPARATION: mean(constant) - mean(balanced) >= 1.1 at >= 5 sigma — the distributed algorithm
     resolves the two function classes (ideal 2.0).
  G4_FRAME_OFF: in-decode falsifier — the balanced oracles with the frame bit IGNORED lose the
     kickback (|<Xbar_q>| <= 0.30). The distributed weld is what carries the oracle across the cut.
  Registered verdict = G1 and G2 and G3.
SCOPE: encoded query + ancilla (2 [[4,2,2]] blocks) + physical relay (transient); per-block XXXX
  partial shield. New content: Deutsch's algorithm — the first quantum algorithm — with the oracle
  DISTRIBUTED across a shielded cut (query and target in different shields, welded by a classical
  bit). Textbook Deutsch + the campaign's 217/218 distributed CNOT; contribution = a shielded
  distributed algorithm resolving a global function property. KILL K1: depth/width over band ->
  simplify or defer.
BUDGET CHECK (C4887): 10q, one distributed CNOT (balanced arms). Predictions filed at freeze.
Usage: --selftest | --submit [--backend ibm_fez --shots 8000] | --decode
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

ORACLES = ["f0_const0", "f1_const1", "f2_bal_x", "f3_bal_nx"]
IDEAL = {"f0_const0": +1, "f1_const1": +1, "f2_bal_x": -1, "f3_bal_nx": -1}


def _p_p0(qc, o): qc.h(o); qc.cx(o, o + 1); qc.h(o + 2); qc.cx(o + 2, o + 3)     # |+bar0bar>
def _Zbar1(qc, o): qc.z(o); qc.z(o + 2)                                          # Zbar1 = Z0Z2
def _Xbar1(qc, o): qc.x(o); qc.x(o + 1)                                          # Xbar1 = X0X1


def circuit(oracle):
    """10 qubits: query = block A q0-3 (L1A), ancilla = block C q4-7 (L1C), relay e_A=q8,e_B=q9."""
    balanced = oracle in ("f2_bal_x", "f3_bal_nx")
    qc = QuantumCircuit(10, 10)
    _p_p0(qc, 0)                          # query q = |+bar>
    _p_p0(qc, 4); _Zbar1(qc, 4)           # ancilla a = |-bar> = |+bar> + Zbar
    if balanced:
        qc.h(8); qc.cx(8, 9)              # relay Bell
        qc.barrier()
        qc.cx(0, 8); qc.cx(2, 8)          # distributed CNOT(q->a): CNOT(q->e_A) from Zbar1A=Z0Z2
        qc.cx(9, 4); qc.cx(9, 5)          # CNOT(e_B->a) into Xbar1C=X4X5
    if oracle in ("f1_const1", "f3_bal_nx"):
        _Xbar1(qc, 4)                     # extra X on ancilla (global phase on |-bar>)
    qc.barrier()
    for q in range(8): qc.h(q)            # Xbar readout on the data blocks
    if balanced:
        qc.h(9)                           # read e_B in X for the Z^z frame on the query
    for q in range(10): qc.measure(q, q)
    return qc


def _acc(v):  # query-block XXXX partial shield (query is what we read; ancilla discarded)
    return (v[0] ^ v[1] ^ v[2] ^ v[3]) == 0


def _xq(counts, oracle, frame_on=True):
    """<Xbar_q> = <X0 X1> with the Z^z frame (z=e_B=q9 in X) flipping the query's X-value."""
    balanced = oracle in ("f2_bal_x", "f3_bal_nx")
    num = den = 0
    for s, n in counts.items():
        b = s.replace(" ", ""); v = [int(b[-1 - i]) for i in range(10)]
        if not _acc(v): continue
        q = v[0] ^ v[1]
        if balanced and frame_on: q ^= v[9]      # Z^z frame on the query
        num += n * (1 - 2 * q); den += n
    return (num / den if den else 0.0), den


def selftest():
    from qiskit_aer import AerSimulator
    sim = AerSimulator()
    print("Exp220 selftest | THE DISTRIBUTED ORACLE — Deutsch across a shielded cut")
    res = {}
    for orc in ORACLES:
        ct = sim.run(circuit(orc), shots=40000).result().get_counts()
        xq, _ = _xq(ct, orc); off, _ = _xq(ct, orc, False)
        res[orc] = (xq, off)
        print(f"  {orc:12s}: <Xbar_q>={xq:+.3f} (ideal {IDEAL[orc]:+d})  frame-off={off:+.3f}")
        assert abs(xq - IDEAL[orc]) < 0.05, f"{orc} must match ideal Deutsch"
    bal_off = [res[o][1] for o in ("f2_bal_x", "f3_bal_nx")]
    assert max(abs(x) for x in bal_off) < 0.15, "balanced frame-off must lose the kickback"
    print("SELFTEST PASS: constant oracles give <Xbar_q>=+1, balanced (distributed CNOT across the "
          "cut) give -1; ignore the weld bit and the balanced kickback dies. Deutsch, distributed. "
          "Cleared to fly.")


def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    builds = [circuit(o) for o in ORACLES]
    circuits = [transpile(qc, backend=backend, optimization_level=3, seed_transpiler=0) for qc in builds]
    n2s = [sum(1 for i in c.data if i.operation.num_qubits == 2) for c in circuits]
    print(f"  DEPTH CHECK: {len(circuits)} circuits, 2q {min(n2s)}-{max(n2s)}")
    job = SamplerV2(mode=backend).run(circuits, shots=shots)
    out = os.path.join(HERE, "..", "results", "exp220_distributed_deutsch_manifest.json")
    man = {"exp": 220, "slug": "distributed_deutsch", "backend": backend_name, "shots": shots,
           "job_id": job.job_id(), "order": ORACLES,
           "prereg": {"G1_constant": "<Xq>(f0,f1) >= +0.55, each >=5 sigma over 0",
                      "G2_balanced": "<Xq>(f2,f3) <= -0.55, each >=5 sigma magnitude",
                      "G3_separation": "mean(const) - mean(bal) >= 1.1 at >=5 sigma (ideal 2.0)",
                      "G4_frame_off": "balanced frame-ignored |<Xq>| <= 0.30 (weld carries the oracle)",
                      "registered_verdict": "G1 and G2 and G3",
                      "scope": "Deutsch's algorithm with the oracle DISTRIBUTED across a shielded cut; "
                               "query and target in different [[4,2,2]] shields; per-block partial shield"}}
    json.dump(man, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits, {shots} shots) -> {out}")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    man = json.load(open(os.path.join(HERE, "..", "results", "exp220_distributed_deutsch_manifest.json")))
    svc = _get_ibm_service(); res = svc.job(man["job_id"]).result()
    raw = {}
    for idx, orc in enumerate(man["order"]):
        r0 = res[idx]; reg = list(r0.data.keys())[0]
        raw[orc] = getattr(r0.data, reg).get_counts()
    print(f"Exp220 THE DISTRIBUTED ORACLE — Deutsch across a shielded cut | job {man['job_id']}")
    xq = {}; se = {}
    for orc in ORACLES:
        x, nn = _xq(raw[orc], orc); off, _ = _xq(raw[orc], orc, False)
        s = float(np.sqrt(max(1e-9, 1 - x ** 2) / max(1, nn)))
        xq[orc] = x; se[orc] = s
        tag = "constant" if IDEAL[orc] > 0 else "balanced"
        acc = nn / sum(raw[orc].values())
        print(f"  {orc:12s} ({tag}): <Xbar_q>={x:+.3f}±{s:.3f} (ideal {IDEAL[orc]:+d})  off={off:+.3f}  acc={acc:.3f}")
    c_vals = [xq["f0_const0"], xq["f1_const1"]]; b_vals = [xq["f2_bal_x"], xq["f3_bal_nx"]]
    b_off = [_xq(raw["f2_bal_x"], "f2_bal_x", False)[0], _xq(raw["f3_bal_nx"], "f3_bal_nx", False)[0]]
    g1 = all(v >= 0.55 and v / se[o] >= 5 for v, o in zip(c_vals, ("f0_const0", "f1_const1")))
    g2 = all(v <= -0.55 and abs(v) / se[o] >= 5 for v, o in zip(b_vals, ("f2_bal_x", "f3_bal_nx")))
    sep = float(np.mean(c_vals) - np.mean(b_vals))
    se_sep = float(np.sqrt(sum(se[o] ** 2 for o in ORACLES)) / 2)
    g3 = sep >= 1.1 and sep / se_sep >= 5
    g4 = max(abs(x) for x in b_off) <= 0.30
    print(f"\nG1 CONSTANT: <Xq>={[round(v,3) for v in c_vals]} (both>=+0.55) {'OK' if g1 else 'MISS'}")
    print(f"G2 BALANCED: <Xq>={[round(v,3) for v in b_vals]} (both<=-0.55) {'OK' if g2 else 'MISS'}")
    print(f"G3 SEPARATION: const-bal = {sep:.3f} at {sep/se_sep:.0f} sigma (>=1.1) {'OK' if g3 else 'MISS'}")
    print(f"G4 FRAME-OFF: balanced off {[round(v,3) for v in b_off]} (<=0.30) {'OK' if g4 else 'MISS'}")
    ok = g1 and g2 and g3
    win = ("THE DISTRIBUTED ORACLE — Deutsch's algorithm with its oracle split across a shielded "
           "cut: the query in one shield and the function's target in another decide CONSTANT vs "
           "BALANCED in a single distributed query, welded by one classical bit. The first quantum "
           "algorithm, distributed and error-corrected, on silicon")
    print(f"VERDICT: {win if ok else 'NOT HELD (accounting above)'}")
    json.dump({"job_id": man["job_id"], "xq": xq, "separation": sep, "balanced_frameoff": b_off,
               "g1": bool(g1), "g2": bool(g2), "g3": bool(g3), "g4": bool(g4), "verdict_ok": bool(ok)},
              open(os.path.join(HERE, "..", "results", "exp220_distributed_deutsch_decode.json"), "w"), indent=1)
    print("-> results/exp220_distributed_deutsch_decode.json")


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
