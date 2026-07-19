#!/usr/bin/env python3
"""Exp198 — THE DIAL OF FACTS: the quantum->classical transition as a measured curve. C4891.

Perturbation instrument built on Exp193 (certified: uncopied facts violate observer-
independence at 20 sigma, S=2.346; fully copied facts obey it, S=1.556). The binary copy
becomes a DIAL: the friends' records couple to the environment through a partial-copy gate
cry(theta) — copy strength sin^2(theta/2), friend-coherence survival cos(theta/2) — swept
over theta/pi in {0, 1/4, 1/2, 3/4, 1}. Deliverables:
  * facts-CHSH S(theta): the descent from quantum (2.5 ideal) to absolute (1.75 ideal)
  * theta* — THE HALF-FACT POINT where S crosses the observer-independence bound 2
  * S vs record-redundancy R(theta) = friend-dump agreement: the objectivity tradeoff
    (quantum Darwinism's claim as a plotted curve)

DESIGN RULE (C4887/195c lesson): the dial changes INFORMATION FLOW, not circuit burden —
cry(theta) transpiles to the same gate count at every angle, so the partial-copy gate stays
in circuit at ALL doses including theta=0. Sweep arms are gate-identical; only the coupling
strength varies. Cost: the theta=0 anchor sits slightly below 193's live 2.346 (it carries
the copy gates' burden); band widened accordingly.

BUDGET CHECK (C4887 rule): S(0)>2 needs lambda > 0.80; Exp193 measured lambda ~ 0.94 on
this exact circuit family (2.346/2.5). Margin holds even with the extra copy-gate burden.

Qubits (as 193): a=q0, F_A=q1, dump_A=q2, b=q3, F_B=q4, dump_B=q5. Bell(a,b); friends
record (CX sys->friend); partial copy cry(theta) friend->dump both sides; per side, late
choice TRUST (read friend) or OVERRULE (undo + measure sys at +-pi/3).
Usage: --selftest | --submit [--backend ibm_fez --shots 8000] | --decode
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
PI = np.pi
SETT = ["FF", "FB", "AF", "AB"]
DOSES = (0.0, 0.25, 0.5, 0.75, 1.0)          # theta / pi
A1, B1 = PI/3, -PI/3


def circuit(t, s, measured=True):
    th = t * PI
    qc = QuantumCircuit(6, 6 if measured else 0)
    qc.h(0); qc.cx(0, 3)                      # Bell(a,b)
    qc.barrier()
    qc.cx(0, 1); qc.cx(3, 4)                  # friends record the facts
    qc.cry(th, 1, 2); qc.cry(th, 4, 5)        # THE DIAL: partial copy, both sides, ALL doses
    qc.barrier()
    if s[0] == "A": qc.cx(0, 1); qc.ry(-A1, 0)
    if s[1] == "B": qc.cx(3, 4); qc.ry(-B1, 3)
    qc.barrier()
    if measured:
        for q in range(6): qc.measure(q, q)
    return qc


def _terms(counts, s):
    acc = tot = 0; eff = 0; rda = 0
    for bstr, n in counts.items():
        b = bstr.replace(" ", "")
        va = int(b[-2]) if s[0] == "F" else int(b[-1])     # A outcome: friend or system
        vb = int(b[-5]) if s[1] == "F" else int(b[-4])     # B outcome
        acc += (1 - 2 * va) * (1 - 2 * vb) * n; tot += n
        eff += (1 - 2 * int(b[-2])) * (1 - 2 * int(b[-5])) * n     # E(F_A, F_B)
        rda += (1 if int(b[-2]) == int(b[-3]) else -1) * n         # friend_A vs dump_A agree
    return acc / tot, eff / tot, rda / tot


def analyze(get):
    r = {}
    for t in DOSES:
        E = {}; effs = []; rds = []
        for s in SETT:
            e, eff, rd = _terms(get(t, s), s)
            E[s] = e; effs.append(eff); rds.append(rd)
        S = E["FF"] + E["FB"] + E["AF"] - E["AB"]
        r[t] = {"E": {k: float(v) for k, v in E.items()}, "S": float(S),
                "EFF": float(E["FF"]), "EFF_rec": float(effs[0]),
                "R": float((rds[0] + 1) / 2 * 2 - 1)}   # friend-dump agreement in FF setting, [-1,1]
    return r


def derive():
    """Exact statevector S(theta) and redundancy per dose."""
    from qiskit.quantum_info import Statevector, SparsePauliOp
    out = {}
    for t in DOSES:
        E = {}
        for s in SETT:
            sv = Statevector(circuit(t, s, measured=False))
            qa = 1 if s[0] == "F" else 0
            qb = 4 if s[1] == "F" else 3
            lab = ["I"] * 6; lab[5 - qa] = "Z"; lab[5 - qb] = "Z"
            E[s] = float(np.real(sv.expectation_value(SparsePauliOp("".join(lab)))))
        sv = Statevector(circuit(t, "FF", measured=False))
        zz_fd = float(np.real(sv.expectation_value(SparsePauliOp("IIIZZI"))))  # q1,q2 agree
        out[t] = {"E": E, "S": float(E["FF"] + E["FB"] + E["AF"] - E["AB"]),
                  "R_fd": zz_fd}
    return out


def selftest():
    d = derive()
    print("Exp198 selftest | exact S(theta):", {t: round(d[t]["S"], 4) for t in DOSES})
    assert abs(d[0.0]["S"] - 2.5) < 1e-6, "theta=0 must reproduce Exp193 live (2.5)"
    assert abs(d[1.0]["S"] - 1.75) < 1e-6, "theta=pi must reproduce Exp193 copied (1.75)"
    Ss = [d[t]["S"] for t in DOSES]
    assert all(Ss[i] > Ss[i + 1] for i in range(len(Ss) - 1)), "exact curve must be strictly decreasing"
    lo = max(t for t in DOSES if d[t]["S"] > 2); hi = min(t for t in DOSES if d[t]["S"] < 2)
    print(f"  exact half-fact crossing between theta/pi = {lo} and {hi}")
    from qiskit_aer import AerSimulator
    sim = AerSimulator(); shots = 100000; cache = {}
    def get(t, s):
        k = (t, s)
        if k not in cache: cache[k] = sim.run(circuit(t, s), shots=shots).result().get_counts()
        return cache[k]
    r = analyze(get)
    for t in DOSES:
        print(f"  t={t:4}: S={r[t]['S']:+.4f} (exact {d[t]['S']:+.4f})  E(F,F)={r[t]['EFF_rec']:+.3f}  "
              f"R_fd={r[t]['R']:+.3f} (exact {d[t]['R_fd']:+.3f})")
        assert abs(r[t]["S"] - d[t]["S"]) < 0.04, f"Aer/exact mismatch at t={t}"
        assert r[t]["EFF_rec"] > 0.99, "records must record at every dose"
    print("SELFTEST PASS: dial anchors reproduce Exp193 exactly (2.5 / 1.75), descent strictly "
          "monotone, records record at every dose, circuit matches exact curve. Cleared to fly.")


def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    d = derive()
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    circuits, order = [], []
    for t in DOSES:
        for s in SETT:
            circuits.append(transpile(circuit(t, s), backend=backend, optimization_level=3))
            order.append([t, s])
    job = SamplerV2(mode=backend).run(circuits, shots=shots)
    man = {"exp": 198, "slug": "dial_of_facts", "backend": backend_name, "shots": shots,
           "job_id": job.job_id(), "order": order,
           "exact": {str(t): d[t] for t in DOSES},
           "prereg": {"anchor_live": "S(0) > 2 at >=5 sigma; band [2.05, 2.45] (193 measured "
                                     "2.346; widened for dose-independent copy-gate burden)",
                      "anchor_copied": "S(1) in [1.40, 1.90] (193 measured 1.556)",
                      "monotone": "S non-increasing across all consecutive doses within 2 "
                                  "sigma_pair tolerance (no significant increase)",
                      "crossing": "at least one dose >2 at >=3 sigma and one <2 at >=3 sigma; "
                                  "theta* reported by linear interpolation with CI",
                      "gauges": "E(F_A,F_B) >= 0.85 at every dose (records record); "
                                "R_fd strictly increasing (the dial actually dials)",
                      "budget_check": "lambda_req 0.80 vs 193-measured 0.94 (C4887 rule)"}}
    json.dump(man, open(os.path.join(HERE, "..", "results", "exp198_dial_of_facts_manifest.json"), "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits, {shots} shots)")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    man = json.load(open(os.path.join(HERE, "..", "results", "exp198_dial_of_facts_manifest.json")))
    svc = _get_ibm_service(); res = svc.job(man["job_id"]).result()
    shots = man["shots"]; raw = {}
    for idx, (t, s) in enumerate(man["order"]):
        r0 = res[idx]; reg = list(r0.data.keys())[0]
        raw[(float(t), s)] = getattr(r0.data, reg).get_counts()
    r = analyze(lambda t, s: raw[(t, s)])
    seS = {t: float(np.sqrt(sum((1 - r[t]["E"][k] ** 2) / shots for k in r[t]["E"]))) for t in DOSES}
    print(f"Exp198 THE DIAL OF FACTS decode | job {man['job_id']} | absolute-facts bound 2")
    for t in DOSES:
        ex = man["exact"][str(t)]["S"]
        print(f"  t={t:4}: S={r[t]['S']:+.4f} (exact {ex:+.3f}, se {seS[t]:.3f})  "
              f"E(F,F)={r[t]['EFF_rec']:+.3f}  R_fd={r[t]['R']:+.3f}")
    Ss = [r[t]["S"] for t in DOSES]
    z0 = (r[0.0]["S"] - 2) / seS[0.0]
    a_ok = 2.05 <= r[0.0]["S"] <= 2.45 and z0 >= 5
    c_ok = 1.40 <= r[1.0]["S"] <= 1.90
    se_pair = [np.sqrt(seS[DOSES[i]] ** 2 + seS[DOSES[i + 1]] ** 2) for i in range(4)]
    mono_ok = all(Ss[i + 1] - Ss[i] <= 2 * se_pair[i] for i in range(4))
    above = [t for t in DOSES if (r[t]["S"] - 2) / seS[t] >= 3]
    below = [t for t in DOSES if (2 - r[t]["S"]) / seS[t] >= 3]
    x_ok = bool(above) and bool(below)
    theta_star = None
    if x_ok:
        lo = max(above); hi = min(t for t in below if t > lo) if any(t > lo for t in below) else None
        if hi is not None:
            slo, shi = r[lo]["S"], r[hi]["S"]
            theta_star = lo + (slo - 2) / (slo - shi) * (hi - lo)
    rec_ok = all(r[t]["EFF_rec"] >= 0.85 for t in DOSES)
    Rs = [r[t]["R"] for t in DOSES]
    dial_ok = all(Rs[i] < Rs[i + 1] + 0.02 for i in range(4)) and Rs[-1] - Rs[0] > 0.5
    print(f"\nANCHORS: S(0)={r[0.0]['S']:.3f} ({z0:.0f} sigma above bound) "
          f"{'OK' if a_ok else 'CHECK'} | S(1)={r[1.0]['S']:.3f} {'OK' if c_ok else 'CHECK'}")
    print(f"MONOTONE DESCENT: {'OK' if mono_ok else 'VIOLATED'} | "
          f"steps: {[round(Ss[i+1]-Ss[i], 3) for i in range(4)]}")
    print(f"CROSSING: above-bound doses {above}, below-bound doses {below} "
          f"{'OK' if x_ok else 'NOT RESOLVED'}")
    if theta_star is not None:
        print(f"THE HALF-FACT POINT: theta* = {theta_star:.3f} pi — at copy strength "
              f"sin^2(theta*/2) = {np.sin(theta_star * PI / 2) ** 2:.3f}, facts cross into absoluteness")
    print(f"RECORDS RECORD: min E(F,F) = {min(r[t]['EFF_rec'] for t in DOSES):.3f} "
          f"{'OK' if rec_ok else 'CHECK'}")
    print(f"THE DIAL DIALS: R_fd {['%.2f' % v for v in Rs]} {'OK' if dial_ok else 'CHECK'}")
    ok = a_ok and c_ok and mono_ok and x_ok and rec_ok and dial_ok
    print(f"VERDICT: {'THE DIAL OF FACTS — objectivity is a dial, not a switch: facts-CHSH descends the copy-strength curve and crosses the absolute-facts bound at theta* = ' + format(theta_star, '.3f') + ' pi' if ok and theta_star else 'NOT HELD (accounting above)'}")
    json.dump({"job_id": man["job_id"], "results": {str(t): r[t] for t in DOSES},
               "se": {str(t): seS[t] for t in DOSES}, "sigma_anchor": float(z0),
               "theta_star_pi": float(theta_star) if theta_star else None,
               "anchor_ok": bool(a_ok), "copied_ok": bool(c_ok), "monotone_ok": bool(mono_ok),
               "crossing_ok": bool(x_ok), "records_ok": bool(rec_ok), "dial_ok": bool(dial_ok),
               "verdict_ok": bool(ok)},
              open(os.path.join(HERE, "..", "results", "exp198_dial_of_facts_decode.json"), "w"), indent=1)
    print("-> results/exp198_dial_of_facts_decode.json")


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
