#!/usr/bin/env python3
"""Exp204 — THE JURY: how many observers make a fact, how many must forget to unmake one. C4900.

Horizons-4 U5 + U7 in one flight, on Creator standing go ("U5 and U7 go! Keep flying H4 in
order"). The N-scaling faces of the certified Exp201 ledger:

  U5 (THE EXPONENT LAW): Exp201 measured y = x^2 with the exponent counting the two records.
  Generalize: system coherence with N observers at per-record strength theta obeys
      C(N,theta)/C(N,0) = kappa(theta)^N,   kappa = cos(theta/2)
  — each added observer MULTIPLIES the suppression. Gated in relative cross-arm form:
  kappa measured on the N=1 arm predicts N=2,3 parametrically (no fit).

  U7 (THE JURY RULE): at full per-record strength every record is a complete witness.
  Uncompute k of N=3 records:  C proportional to kappa^(N-k) -> at theta=pi: 0,0,0,FULL for
  k=0,1,2,3. Two of three observers may forget and the fact stays absolute; only when the
  LAST record is returned does the event revive. Unanimity of forgetting. At partial
  strength (theta=pi/2) the ladder is graded: kappa^(3-k) — the quantitative form of "how
  many observers must forget before the past is negotiable."

  U5 CONSENSUS: pairwise record agreement A(theta) = 1 - s^2 + s^4 (s^2 = sin^2(theta/2)):
  0.75 at half-strength, 1.0 at full — observers disagree most at half-fact, agree
  perfectly when the fact is objective. (Exp198's half-fact point from the jury's side.)

Apparatus: system q0 (h -> |+>), records q1..qN via manual anti-folding cry (203b doctrine:
ry-cx-BARRIER-ry-cx = 2 CX at EVERY dose incl 0, one layout for the whole sweep). Barrier
between write and unwrite blocks (prevents cross-block cancellation; the record exists).
System read in X; records read in Z. No delays — dose/N physics isolated from idle physics.

Settings (28 circuits, 8000 shots):
  bend:    N in {1,2,3} x theta/pi in {0, 1/4, 1/2, 3/4, 1}        (15)
  ladder half-strength: N=3, theta=pi/2, k in {1,2,3} uncomputed    (3)
  ladder full-strength (THE JURY): N=3, theta=pi, k in {1,2,3}      (3)
  anchors for ladders ride on bend (k=0 points).
  ladder order: records uncomputed in reverse write order (r3 first).

FROZEN GATES:
  G1 ANCHORS: C(N,0) >= 0.75 for each N at >=5 sigma.
  G2 EXPONENT LAW (U5): with kappa(t) = C(1,t)/C(1,0), |C(N,t)/C(N,0) - kappa(t)^N| <= 0.10
     at every interior dose for N=2,3; C(N,t)/C(N,0) strictly decreasing in N at t=1/2, 3/4.
  G3 THE JURY (U7): at theta=pi, C(3,k)/C(3,0) <= 0.15 for k in {0,1,2} AND >= 0.50 at
     >=5 sigma for k=3; the k=2 -> 3 jump >= 0.40 at >=5 sigma.
  G4 PARTIAL LADDER: at theta=pi/2, |C(3,k)/C(3,0) - kappa(pi/2)^(3-k)| <= 0.12, k=0..3.
  G5 CONSENSUS: N=3 bend arm, pooled pairwise agreement |A(t) - (1 - s^2 + s^4)| <= 0.06
     every dose; A(pi) >= 0.90.
  G6 GAUGES: record p1 tracks sin^2(t pi/2)/2 within 0.06 (bend, every record); uncomputed
     records p1 <= 0.10; skeleton audit 2q uniform across theta within every (N,k) family.
Registered verdict = G1-G6. U5 = G2+G5; U7 = G3+G4.

BUDGET CHECK (C4887): shallow no-delay circuits (2N CX + ladder), contrasts O(1) vs se
0.011; parents 201/203b measured this circuit class at kappa ~0.93-0.98 per record.
Filed predictions: C(1,0) in [0.85,0.98]; kappa(pi/2) in [0.63,0.73]; jury jump in
[0.50,0.85]; exponent-law residuals <= 0.06; A(pi/2) in [0.69,0.80].
Usage: --selftest | --submit [--backend ibm_fez --shots 8000] | --decode
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
PI = np.pi
DOSES = (0.0, 0.25, 0.5, 0.75, 1.0)
INTERIOR = (0.25, 0.5, 0.75)
NS = (1, 2, 3)
SETTINGS = ([("bend", N, t, 0) for N in NS for t in DOSES]
            + [("ladder", 3, 0.5, k) for k in (1, 2, 3)]
            + [("ladder", 3, 1.0, k) for k in (1, 2, 3)])


def _manual_cry(qc, th, ctrl, targ):
    qc.ry(th / 2, targ)
    qc.cx(ctrl, targ)
    qc.barrier(ctrl, targ)
    qc.ry(-th / 2, targ)
    qc.cx(ctrl, targ)


def circuit(kind, N, t, k):
    th = t * PI
    qc = QuantumCircuit(N + 1, N + 1)
    qc.h(0)
    qc.barrier()
    for r in range(1, N + 1):                 # write N records
        _manual_cry(qc, th, 0, r)
    qc.barrier()
    if k > 0:                                 # uncompute k records, reverse write order
        for r in range(N, N - k, -1):
            _manual_cry(qc, -th, 0, r)
        qc.barrier()
    qc.h(0)                                   # system X readout
    for q in range(N + 1): qc.measure(q, q)
    return qc


def _stats(counts, N, k):
    c = tot = 0
    p1 = [0] * N
    agree = pairs = 0
    for s, n in counts.items():
        b = s.replace(" ", "")
        v = [int(b[-1 - i]) for i in range(N + 1)]
        c += (1 - 2 * v[0]) * n; tot += n
        for r in range(N): p1[r] += v[1 + r] * n
        if N >= 2:
            for i in range(1, N + 1):
                for j in range(i + 1, N + 1):
                    agree += n * (1 if v[i] == v[j] else 0); pairs += n
    return {"C": c / tot, "rec_p1": [p / tot for p in p1],
            "agree": agree / pairs if pairs else None, "n": tot}


def analyze(get):
    return {(kind, N, t, k): _stats(get(kind, N, t, k), N, k)
            for (kind, N, t, k) in SETTINGS}


def selftest():
    from qiskit_aer import AerSimulator
    sim = AerSimulator(); shots = 40000; cache = {}
    def get(kind, N, t, k):
        key = (kind, N, t, k)
        if key not in cache:
            cache[key] = sim.run(circuit(kind, N, t, k), shots=shots).result().get_counts()
        return cache[key]
    r = analyze(get)
    print("Exp204 selftest (noiseless) | C(N,t)=kappa^N; ladder kappa^(N-k); jury 0,0,0,1")
    for N in NS:
        for t in DOSES:
            s = r[("bend", N, t, 0)]
            ex = np.cos(t * PI / 2) ** N
            assert abs(s["C"] - ex) < 0.02, f"bend N={N} t={t}: {s['C']} vs {ex}"
            for p in s["rec_p1"]:
                assert abs(p - np.sin(t * PI / 2) ** 2 / 2) < 0.02
        print(f"  N={N}: C(t) = " + " ".join(f"{r[('bend', N, t, 0)]['C']:+.3f}" for t in DOSES))
    for t in (0.5, 1.0):
        row = [r[("bend", 3, t, 0)]["C"]] + [r[("ladder", 3, t, k)]["C"] for k in (1, 2, 3)]
        ex = [np.cos(t * PI / 2) ** (3 - k) for k in (0, 1, 2, 3)]
        print(f"  ladder t={t}: " + " ".join(f"{v:+.3f}" for v in row)
              + "  (exact " + " ".join(f"{v:+.3f}" for v in ex) + ")")
        for v, e in zip(row, ex):
            assert abs(v - e) < 0.02, f"ladder t={t}"
    a = {t: r[("bend", 3, t, 0)]["agree"] for t in DOSES}
    for t in DOSES:
        s2 = np.sin(t * PI / 2) ** 2
        assert abs(a[t] - (1 - s2 + s2 ** 2)) < 0.02, f"consensus t={t}"
    print(f"  consensus A(t): " + " ".join(f"{a[t]:.3f}" for t in DOSES)
          + "  (0.75 at half-fact, 1.0 at full)")
    for t in (0.5, 1.0):
        for k in (1, 2, 3):
            s = r[("ladder", 3, t, k)]
            for ri in range(3 - k, 3):        # uncomputed records (written last)
                assert s["rec_p1"][ri] < 0.02, "uncomputed records must return to 0"
    print("SELFTEST PASS: exponent law exact (each observer multiplies suppression by "
          "kappa), jury rule exact (0,0,0,1 at full strength — unanimity required), "
          "partial ladder kappa^(3-k), consensus curve exact, records returned. "
          "Cleared to fly.")


def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    names = list(SETTINGS)
    circuits = audit = seed_used = None
    for seed in range(20):
        cand = [transpile(circuit(*s), backend=backend, optimization_level=3,
                          seed_transpiler=seed) for s in names]
        aud = {}
        for (kind, N, t, k), qc in zip(names, cand):
            n2 = sum(1 for inst in qc.data if inst.operation.num_qubits == 2)
            aud.setdefault(f"{kind}_N{N}_k{k}", {})[t] = n2
        if all(len(set(per.values())) == 1 for per in aud.values()):
            circuits, seed_used = cand, seed
            audit = {fam: {str(t): n for t, n in per.items()} for fam, per in aud.items()}
            break
        print(f"  seed {seed}: non-uniform — next")
    if circuits is None:
        print("AUDIT ABORT: no theta-uniform seed in 0-19 per family"); sys.exit(1)
    for fam, per in sorted(audit.items()):
        print(f"  audit {fam}: 2q={sorted(set(per.values()))} (theta-uniform, seed {seed_used})")
    job = SamplerV2(mode=backend).run(circuits, shots=shots)
    out = os.path.join(HERE, "..", "results", "exp204_the_jury_manifest.json")
    man = {"exp": 204, "slug": "the_jury", "backend": backend_name, "shots": shots,
           "job_id": job.job_id(), "order": [list(s) for s in names],
           "seed_transpiler": seed_used}
    json.dump(man, open(out, "w"), indent=1)                 # manifest first (C4895)
    man["audit_2q"] = audit
    man["prereg"] = {
        "G1_anchors": "C(N,0) >= 0.75 each N at >=5 sigma",
        "G2_exponent_law": "kappa(t)=C(1,t)/C(1,0); |C(N,t)/C(N,0) - kappa^N| <= 0.10 at "
                           "interior doses for N=2,3; ratios strictly decreasing in N at "
                           "t=0.5,0.75",
        "G3_the_jury": "theta=pi: C(3,k)/C(3,0) <= 0.15 for k=0,1,2 AND >= 0.50 at >=5 "
                       "sigma for k=3; jump k2->k3 >= 0.40 at >=5 sigma",
        "G4_partial_ladder": "theta=pi/2: |C(3,k)/C(3,0) - kappa(pi/2)^(3-k)| <= 0.12, k=0..3",
        "G5_consensus": "N=3 bend pooled pairwise agreement |A - (1-s2+s2^2)| <= 0.06 every "
                        "dose; A(pi) >= 0.90",
        "G6_gauges": "record p1 tracks sin^2/2 within 0.06 (bend); uncomputed <= 0.10; "
                     "2q theta-uniform per family (anti-folding, 203b doctrine)",
        "registered_verdict": "G1-G6; U5 = G2+G5; U7 = G3+G4",
        "budget_predictions": "C(1,0) in [0.85,0.98]; kappa(pi/2) in [0.63,0.73]; jury "
                              "jump in [0.50,0.85]; exponent residuals <= 0.06; "
                              "A(pi/2) in [0.69,0.80]"}
    json.dump(man, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits, {shots} shots) -> {out}")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    man = json.load(open(os.path.join(HERE, "..", "results", "exp204_the_jury_manifest.json")))
    svc = _get_ibm_service(); res = svc.job(man["job_id"]).result()
    shots = man["shots"]; raw = {}
    for idx, (kind, N, t, k) in enumerate(man["order"]):
        r0 = res[idx]; reg = list(r0.data.keys())[0]
        raw[(kind, int(N), float(t), int(k))] = getattr(r0.data, reg).get_counts()
    r = analyze(lambda kind, N, t, k: raw[(kind, N, t, k)])
    se = 1 / np.sqrt(shots)
    C = {(N, t): r[("bend", N, t, 0)]["C"] for N in NS for t in DOSES}
    kap = {t: C[(1, t)] / C[(1, 0.0)] for t in DOSES}
    print(f"Exp204 THE JURY decode | job {man['job_id']}")
    for N in NS:
        print(f"  N={N}: C = " + " ".join(f"{C[(N, t)]:+.4f}" for t in DOSES)
              + f"  | ratios " + " ".join(f"{C[(N, t)]/C[(N, 0.0)]:+.3f}" for t in INTERIOR))
    lad = {t: [C[(3, t)]] + [r[("ladder", 3, t, k)]["C"] for k in (1, 2, 3)] for t in (0.5, 1.0)}
    for t in (0.5, 1.0):
        print(f"  ladder t={t}: " + " ".join(f"{v:+.4f}" for v in lad[t]))
    A = {t: r[("bend", 3, t, 0)]["agree"] for t in DOSES}
    print(f"  consensus A: " + " ".join(f"{A[t]:.4f}" for t in DOSES))
    g1 = all(C[(N, 0.0)] >= 0.75 and C[(N, 0.0)] / se >= 5 for N in NS)
    ex_res = {(N, t): C[(N, t)] / C[(N, 0.0)] - kap[t] ** N for N in (2, 3) for t in INTERIOR}
    mono = all(C[(2, t)] / C[(2, 0.0)] < C[(1, t)] / C[(1, 0.0)]
               and C[(3, t)] / C[(3, 0.0)] < C[(2, t)] / C[(2, 0.0)] for t in (0.5, 0.75))
    g2 = all(abs(v) <= 0.10 for v in ex_res.values()) and mono
    jr = [v / C[(3, 0.0)] for v in lad[1.0]]
    jump = jr[3] - jr[2]; z_jump = jump * C[(3, 0.0)] / (se * np.sqrt(2))
    z_k3 = jr[3] * C[(3, 0.0)] / se
    g3 = all(v <= 0.15 for v in jr[:3]) and jr[3] >= 0.50 and z_k3 >= 5 and jump >= 0.40 and z_jump >= 5
    pl = [v / C[(3, 0.0)] for v in lad[0.5]]
    pl_res = [pl[k] - kap[0.5] ** (3 - k) for k in range(4)]
    g4 = all(abs(v) <= 0.12 for v in pl_res)
    g5 = all(abs(A[t] - (1 - np.sin(t * PI / 2) ** 2 + np.sin(t * PI / 2) ** 4)) <= 0.06
             for t in DOSES) and A[1.0] >= 0.90
    rec_ok = all(abs(p - np.sin(t * PI / 2) ** 2 / 2) <= 0.06
                 for N in NS for t in DOSES for p in r[("bend", N, t, 0)]["rec_p1"])
    unc_ok = all(r[("ladder", 3, t, k)]["rec_p1"][ri] <= 0.10
                 for t in (0.5, 1.0) for k in (1, 2, 3) for ri in range(3 - k, 3))
    g6 = rec_ok and unc_ok
    print(f"\nG1 ANCHORS: " + " ".join(f"C({N},0)={C[(N, 0.0)]:.3f}" for N in NS)
          + f" {'OK' if g1 else 'MISS'}")
    print(f"G2 EXPONENT LAW: max|resid| {max(abs(v) for v in ex_res.values()):.4f} "
          f"(<=0.10), N-monotone {mono} {'OK' if g2 else 'MISS'}")
    print(f"G3 THE JURY: ratios {['%.3f' % v for v in jr]} — jump k2->k3 {jump:+.3f} "
          f"({z_jump:.0f} sigma) {'OK' if g3 else 'MISS'}")
    print(f"G4 PARTIAL LADDER: resids {['%+.3f' % v for v in pl_res]} {'OK' if g4 else 'MISS'}")
    print(f"G5 CONSENSUS: A(pi/2)={A[0.5]:.3f} (ideal 0.75), A(pi)={A[1.0]:.3f} "
          f"{'OK' if g5 else 'MISS'}")
    print(f"G6 GAUGES: records track {rec_ok}, returned {unc_ok} {'OK' if g6 else 'MISS'}")
    ok = g1 and g2 and g3 and g4 and g5 and g6
    u5 = g2 and g5; u7 = g3 and g4
    print(f"U5 (G2+G5): {'ANSWERED — objectivity scales as kappa^N: each observer '
          'multiplies the suppression, and consensus is worst at the half-fact, perfect at '
          'the full fact' if u5 else 'NOT RESOLVED'}")
    print(f"U7 (G3+G4): {'ANSWERED — the past is negotiable only by unanimity: revival '
          'requires every record returned, and partial forgetting buys exactly '
          'kappa^(N-k)' if u7 else 'NOT RESOLVED'}")
    print(f"REGISTERED VERDICT (G1-G6): {'HELD' if ok else 'NOT HELD (accounting above)'}")
    json.dump({"job_id": man["job_id"],
               "C": {f"{N}_{t}": float(C[(N, t)]) for N in NS for t in DOSES},
               "kappa": {str(t): float(kap[t]) for t in DOSES},
               "exponent_resid": {f"{N}_{t}": float(v) for (N, t), v in ex_res.items()},
               "jury_ratios": [float(v) for v in jr], "jury_jump": float(jump),
               "sigma_jump": float(z_jump),
               "partial_ladder": [float(v) for v in pl], "partial_resid": [float(v) for v in pl_res],
               "consensus": {str(t): float(A[t]) for t in DOSES},
               "g1": bool(g1), "g2": bool(g2), "g3": bool(g3), "g4": bool(g4),
               "g5": bool(g5), "g6": bool(g6), "u5": bool(u5), "u7": bool(u7),
               "verdict_ok": bool(ok)},
              open(os.path.join(HERE, "..", "results", "exp204_the_jury_decode.json"), "w"), indent=1)
    print("-> results/exp204_the_jury_decode.json")


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
