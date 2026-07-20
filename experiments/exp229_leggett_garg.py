#!/usr/bin/env python3
"""Exp229 — THE PAST IS NOT WRITTEN: the Leggett-Garg temporal-Bell inequality. C4913.

A new wild one, chosen on Creator review of the H5 results ("anything new? wild stuff?"). Where the
Bell/CHSH inequality asks whether reality is definite across SPACE, the Leggett-Garg inequality asks
whether it is definite across TIME — macrorealism: does a system have a definite value between
measurements (is the moon there when nobody looks, in time?). It is the temporal sibling of the P3
arrow-of-time work.

A single qubit precesses under Rx(omega*tau) per step (omega*tau = pi/3), dichotomic observable
Q = sigma_z in {+1,-1}. Two-time correlators C_ij = <Q(t_i)Q(t_j)> are measured (a mid-circuit
projective measurement at the earlier time, then evolve, then measure). The LG quantity
  K3 = C12 + C23 - C13
obeys K3 <= 1 for any MACROREALIST (definite-value, non-invasively-measurable) theory; quantum
mechanics reaches K3 = 1.5. Initial state |+bar> (Xbar-eigenstate) so every first measurement is
genuinely uncertain (a real 2-time correlator, NOT a trivial/tautological readout — the P7 lesson).

VALIDITY NOTE (post-Exp228): each correlator has genuine shot-noise variance (the measured Q(t_i)
is a real projective outcome, ~50/50 at t1), so K3 is a physical quantity that CAN fall below 1.5 —
unlike a bit-identity. The classical bound 1 is violable and the test is real.

FROZEN GATES (relative to statevector-exact; checked in selftest):
  G1_MACROREALISM_VIOLATION: K3 > 1.0 at >= 5 sigma — the temporal-Bell / macrorealist bound is
     violated (the past is not definite-and-noninvasive).
  G2_QUANTUM_VALUE: K3 >= 1.30 — a strong fraction of the ideal 1.5.
  G3_CORRELATORS (reported): C12,C23 ~ cos(pi/3)=+0.5, C13 ~ cos(2pi/3)=-0.5.
  Registered verdict = G1 and G2.
SCOPE: single qubit, projective mid-circuit measurement (dynamic circuit). Standard LG protocol;
  the macrorealist bound assumes non-invasive measurability, tested here by projective measurement
  (the clumsiness/invasiveness loophole is the standard LG caveat, stated). Textbook Leggett-Garg
  (1985); new to the campaign — the temporal complement to CHSH (F-series) and the P3 arrow of time.
  KILL K1: trivial depth.
BUDGET CHECK (C4887): shallow (Rx + 2 measures). K3 ideal 1.5; hardware readout+measurement haircut
  -> predict K3 in [1.3, 1.48]; G1 needs only >1.
Usage: --selftest | --submit [--backend ibm_fez --shots 8000] | --decode
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
PI = np.pi
STEP = PI / 3        # omega*tau; K3 max at pi/3


def circ(pair):
    """two-time correlator circuit. Initial |+> (H); Q=sigma_z; precession Rx(STEP)."""
    qc = QuantumCircuit(1, 2)
    qc.h(0)                                       # |+> — first measurement genuinely uncertain
    if pair == "12":                              # measure t1, evolve, measure t2
        qc.measure(0, 0); qc.rx(STEP, 0); qc.measure(0, 1)
    elif pair == "23":                            # evolve to t2, measure, evolve, measure t3
        qc.rx(STEP, 0); qc.measure(0, 0); qc.rx(STEP, 0); qc.measure(0, 1)
    elif pair == "13":                            # measure t1, evolve 2 steps, measure t3
        qc.measure(0, 0); qc.rx(2 * STEP, 0); qc.measure(0, 1)
    return qc


def _corr(counts):
    num = den = 0
    for s, n in counts.items():
        b = s.replace(" ", ""); c0 = int(b[-1]); c1 = int(b[-2])
        num += (1 - 2 * c0) * (1 - 2 * c1) * n; den += n
    return (num / den if den else 0.0), den


def selftest():
    from qiskit_aer import AerSimulator
    sim = AerSimulator(); shots = 200000
    Cs = {}; spread_ok = True
    print("Exp229 selftest | THE PAST IS NOT WRITTEN — Leggett-Garg temporal-Bell inequality")
    for p in ("12", "23", "13"):
        ct = sim.run(circ(p), shots=shots).result().get_counts()
        Cs[p], _ = _corr(ct)
        # validity: outcome distribution must have >=3 distinct outcomes (genuine variance, not tautology)
        if len([k for k, v in ct.items() if v > shots * 0.01]) < 3: spread_ok = False
        print(f"  C{p} = {Cs[p]:+.3f}  (ideal {np.cos((1 if p!='13' else 2)*STEP):+.3f})")
    K3 = Cs["12"] + Cs["23"] - Cs["13"]
    print(f"  K3 = {K3:.3f}  (macrorealist bound 1, quantum max 1.5)")
    assert abs(K3 - 1.5) < 0.03, "K3 must reach the quantum value 1.5"
    assert spread_ok, "correlators must have genuine shot-noise variance (not a tautology)"
    print("SELFTEST PASS: K3 = 1.5 > 1, with genuine measurement variance. The temporal-Bell / "
          "macrorealist bound is violated — the past is not definite-and-noninvasive. Cleared to fly.")


def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    order = ["12", "23", "13"]
    circuits = [transpile(circ(p), backend=backend, optimization_level=3, seed_transpiler=0) for p in order]
    n2s = [sum(1 for i in c.data if i.operation.num_qubits == 2) for c in circuits]
    print(f"  DEPTH CHECK: {len(circuits)} circuits, 2q {min(n2s)}-{max(n2s)}")
    job = SamplerV2(mode=backend).run(circuits, shots=shots)
    out = os.path.join(HERE, "..", "results", "exp229_leggett_garg_manifest.json")
    man = {"exp": 229, "slug": "leggett_garg", "backend": backend_name, "shots": shots,
           "job_id": job.job_id(), "order": order,
           "prereg": {"G1_macrorealism_violation": "K3 > 1.0 at >=5 sigma",
                      "G2_quantum_value": "K3 >= 1.30 (fraction of ideal 1.5)",
                      "G3_correlators": "reported: C12,C23~+0.5, C13~-0.5",
                      "registered_verdict": "G1 and G2",
                      "scope": "single-qubit Leggett-Garg temporal-Bell; projective mid-circuit "
                               "measurement; macrorealism violated K3->1.5 (invasiveness loophole stated)"}}
    json.dump(man, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits, {shots} shots) -> {out}")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    man = json.load(open(os.path.join(HERE, "..", "results", "exp229_leggett_garg_manifest.json")))
    svc = _get_ibm_service(); res = svc.job(man["job_id"]).result()
    raw = {}
    for idx, p in enumerate(man["order"]):
        r0 = res[idx]; reg = list(r0.data.keys())[0]
        raw[p] = getattr(r0.data, reg).get_counts()
    Cs = {}; ns = {}
    for p in man["order"]:
        Cs[p], ns[p] = _corr(raw[p])
    K3 = Cs["12"] + Cs["23"] - Cs["13"]
    se = float(np.sqrt(sum((1 - Cs[p] ** 2) / max(1, ns[p]) for p in man["order"])))
    print(f"Exp229 THE PAST IS NOT WRITTEN — Leggett-Garg decode | job {man['job_id']}")
    for p in man["order"]:
        print(f"  C{p} = {Cs[p]:+.3f}  (ideal {np.cos((1 if p!='13' else 2)*STEP):+.3f})")
    print(f"\n  K3 = {K3:.3f} ± {se:.3f}   (macrorealist bound 1, quantum max 1.5)")
    g1 = K3 > 1.0 and (K3 - 1.0) / se >= 5
    g2 = K3 >= 1.30
    print(f"G1 MACROREALISM VIOLATION: K3={K3:.3f} > 1 at {(K3-1.0)/se:.0f} sigma {'OK' if g1 else 'MISS'}")
    print(f"G2 QUANTUM VALUE: K3={K3:.3f} >= 1.30 {'OK' if g2 else 'MISS'}")
    ok = g1 and g2
    win = ("THE PAST IS NOT WRITTEN — the Leggett-Garg temporal-Bell inequality is violated: K3 beats "
           "the macrorealist bound of 1, reaching toward the quantum 1.5. A qubit has no definite, "
           "non-invasively-knowable value between measurements — reality is indefinite in TIME, on silicon")
    print(f"VERDICT: {win if ok else 'NOT HELD (accounting above)'}")
    json.dump({"job_id": man["job_id"], "correlators": Cs, "K3": K3, "se": se,
               "g1": bool(g1), "g2": bool(g2), "verdict_ok": bool(ok)},
              open(os.path.join(HERE, "..", "results", "exp229_leggett_garg_decode.json"), "w"), indent=1)
    print("-> results/exp229_leggett_garg_decode.json")


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
