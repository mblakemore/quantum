#!/usr/bin/env python3
"""Exp201 — THE LEDGER OF TIME: objectivity and irreversibility as one bookkeeping. C4895.

Horizons-4 U1 (docs/star-trek-horizons-4-the-starship-whisper-c4894.md), flown on Creator go.
The unification conjecture: quantum Darwinism's objectivity (Exp198) and the thermodynamic
arrow's irreversibility (Exp200b) are the SAME bath-record bookkeeping. Both certified
instruments share one mechanism — a record of strength theta in an environment qubit, with
overlap factor kappa(theta) = cos(theta/2):

  Exp198 measured  S_facts(theta) = 1.75 + 0.75 * kappa^2   (two records, one per wing)
  Exp200b measured C_bend(theta)  = C_base * kappa           (one record)

TWO TESTABLE FACES, ONE SWEEP (same job, same window, same compilation):

  FACE 1 — THE ONE-CURVE LAW (parametric, cross-observable): define from in-job data
      x(t) = C_cb(t) / C_cb(0)                        (the arrow's observable, normalized)
      y(t) = [S_fb(t) - S_fb(1)] / [S_fb(0) - S_fb(1)] (Darwinism's observable, normalized)
  Prediction: y = x^2 at the interior doses (endpoints are the normalization). The exponent
  2 is the falsifiable content — it counts the records (one per wing). If facts decayed as
  x^1 or x^3 the gate fails.

  FACE 2 — OBJECTIVITY IS BOOKKEEPING (the new arm neither parent had): UNBEND THE FACT.
  In the facts apparatus, uncompute the environmental record (cry(-theta) friend->dump,
  both wings) before the late choice. Prediction: S returns to the quantum curve at EVERY
  dose including full copy — the fact that had become absolute (198: S=1.575) violates
  observer-independence again once the universe's receipt is erased. Mirrors 200b's
  bend-back gate exactly, one observable up: revival >= 0.5*(S_fb(0)-S_fb(1)) at >=5 sigma,
  dose-independent. The coherence arms (cb/cu) run the 200b logic on the gate-matched wing
  (no delays — dose physics isolated from idle physics by design).

Arms (5 doses theta/pi in {0, 1/4, 1/2, 3/4, 1}; within-arm gate-identical, C4891 rule):
  fb: facts-bend   = Exp198's certified circuit verbatim (4 settings x 5 doses = 20)
  fu: facts-unbend = fb + cry(-theta) both wings after a barrier         (20)
  cb: coh-bend     = single wing: h, cx(sys->friend), cry(friend->dump),
                     cx undo, h, measure                                  (5)
  cu: coh-unbend   = cb + cry(-theta, friend->dump) before the undo       (5)
Burden bias runs AGAINST both headlines (unbend arms carry MORE gates yet must show MORE
quantum behavior — 200b's burden note, inherited).

BUDGET CHECK (C4887 rule, 6-for-6): S_fb anchors need lambda ~0.80; 198 measured 0.94 on
this exact circuit family and backend. Predicted landings filed in the manifest: S_fu(1)
in [2.15, 2.32]; rev_f in [0.55, 0.72]; law residuals <= 0.08; C_cb(0) in [0.93, 0.98].
Bands priced from the flying compilation via in-job anchors (200's lesson); per-arm gauge
budgets from each arm's own physics (200b's lesson).
Usage: --selftest | --submit [--backend ibm_fez --shots 8000] | --decode
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
PI = np.pi
SETT = ["FF", "FB", "AF", "AB"]
DOSES = (0.0, 0.25, 0.5, 0.75, 1.0)
INTERIOR = (0.25, 0.5, 0.75)
A1, B1 = PI / 3, -PI / 3


def facts_circuit(t, s, unbend, measured=True):
    th = t * PI
    qc = QuantumCircuit(6, 6 if measured else 0)
    qc.h(0); qc.cx(0, 3)                      # Bell(a,b)
    qc.barrier()
    qc.cx(0, 1); qc.cx(3, 4)                  # friends record the facts
    qc.cry(th, 1, 2); qc.cry(th, 4, 5)        # the dial: partial copy into the environment
    qc.barrier()
    if unbend:
        qc.cry(-th, 1, 2); qc.cry(-th, 4, 5)  # UNBEND THE FACT: uncompute the record
        qc.barrier()
    if s[0] == "A": qc.cx(0, 1); qc.ry(-A1, 0)
    if s[1] == "B": qc.cx(3, 4); qc.ry(-B1, 3)
    qc.barrier()
    if measured:
        for q in range(6): qc.measure(q, q)
    return qc


def coh_circuit(t, unbend):
    th = t * PI
    qc = QuantumCircuit(3, 3)
    qc.h(0)
    qc.cx(0, 1)                               # friend records
    qc.cry(th, 1, 2)                          # dump copies (the same dial, one wing)
    qc.barrier()
    if unbend:
        qc.cry(-th, 1, 2)                     # uncompute the record
        qc.barrier()
    qc.cx(0, 1)                               # overrule: undo the friend
    qc.h(0)
    for q in range(3): qc.measure(q, q)
    return qc


def circ_name(arm, t, s=None):
    return f"{arm}_{t}" + (f"_{s}" if s else "")


def all_circuits():
    names, builds = [], []
    for t in DOSES:
        for s in SETT:
            names.append(circ_name("fb", t, s)); builds.append(facts_circuit(t, s, False))
        for s in SETT:
            names.append(circ_name("fu", t, s)); builds.append(facts_circuit(t, s, True))
        names.append(circ_name("cb", t)); builds.append(coh_circuit(t, False))
        names.append(circ_name("cu", t)); builds.append(coh_circuit(t, True))
    return names, builds


def _facts_terms(counts, s):
    acc = eff = rda = d2 = d5 = tot = 0
    for bstr, n in counts.items():
        b = bstr.replace(" ", "")
        va = int(b[-2]) if s[0] == "F" else int(b[-1])
        vb = int(b[-5]) if s[1] == "F" else int(b[-4])
        acc += (1 - 2 * va) * (1 - 2 * vb) * n
        eff += (1 - 2 * int(b[-2])) * (1 - 2 * int(b[-5])) * n
        rda += (1 if int(b[-2]) == int(b[-3]) else -1) * n
        d2 += int(b[-3]) * n; d5 += int(b[-6]) * n
        tot += n
    return acc / tot, eff / tot, rda / tot, d2 / tot, d5 / tot


def _coh_stats(counts):
    cx = d = tot = 0
    for bstr, n in counts.items():
        b = bstr.replace(" ", "")
        cx += (1 - 2 * int(b[-1])) * n; d += int(b[-3]) * n; tot += n
    return {"C": cx / tot, "dump_p1": d / tot}


def analyze(get):
    r = {}
    for arm in ("fb", "fu"):
        r[arm] = {}
        for t in DOSES:
            E = {}; eff_ff = rd_ff = None; dmax = 0.0
            for s in SETT:
                e, eff, rd, d2, d5 = _facts_terms(get(circ_name(arm, t, s)), s)
                E[s] = e; dmax = max(dmax, d2, d5)
                if s == "FF": eff_ff, rd_ff = eff, rd
            r[arm][t] = {"E": {k: float(v) for k, v in E.items()},
                         "S": float(E["FF"] + E["FB"] + E["AF"] - E["AB"]),
                         "EFF_rec": float(eff_ff), "R_fd": float(rd_ff),
                         "dump_p1_max": float(dmax)}
    for arm in ("cb", "cu"):
        r[arm] = {t: _coh_stats(get(circ_name(arm, t))) for t in DOSES}
    return r


def derive():
    """Exact statevector values for every arm and dose."""
    from qiskit.quantum_info import Statevector, SparsePauliOp
    out = {"fb": {}, "fu": {}, "cb": {}, "cu": {}}
    for arm, unbend in (("fb", False), ("fu", True)):
        for t in DOSES:
            E = {}
            for s in SETT:
                sv = Statevector(facts_circuit(t, s, unbend, measured=False))
                qa = 1 if s[0] == "F" else 0
                qb = 4 if s[1] == "F" else 3
                lab = ["I"] * 6; lab[5 - qa] = "Z"; lab[5 - qb] = "Z"
                E[s] = float(np.real(sv.expectation_value(SparsePauliOp("".join(lab)))))
            out[arm][t] = {"S": float(E["FF"] + E["FB"] + E["AF"] - E["AB"])}
    for t in DOSES:
        out["cb"][t] = {"C": float(np.cos(t * PI / 2)), "dump_p1": float(np.sin(t * PI / 2) ** 2 / 2)}
        out["cu"][t] = {"C": 1.0, "dump_p1": 0.0}
    return out


def law_points(r):
    """The one-curve law from in-job data: x = normalized coherence, y = normalized facts."""
    S0, S1 = r["fb"][0.0]["S"], r["fb"][1.0]["S"]
    C0 = r["cb"][0.0]["C"]
    pts = {}
    for t in DOSES:
        x = r["cb"][t]["C"] / C0
        y = (r["fb"][t]["S"] - S1) / (S0 - S1)
        pts[t] = {"x": float(x), "y": float(y), "resid": float(y - x * x)}
    return pts


def selftest():
    d = derive()
    print("Exp201 selftest | exact curves:")
    print("  S_fb:", {t: round(d["fb"][t]["S"], 4) for t in DOSES})
    print("  S_fu:", {t: round(d["fu"][t]["S"], 4) for t in DOSES})
    for t in DOSES:
        ex = 1.75 + 0.75 * np.cos(t * PI / 2) ** 2
        assert abs(d["fb"][t]["S"] - ex) < 1e-6, f"fb must reproduce 198's exact curve at t={t}"
        assert abs(d["fu"][t]["S"] - 2.5) < 1e-6, f"fu must fully revive the fact at t={t}"
    # the exact one-curve law: y = x^2 with residual 0
    exact_pts = {t: (np.cos(t * PI / 2),
                     (1.75 + 0.75 * np.cos(t * PI / 2) ** 2 - 1.75) / 0.75) for t in DOSES}
    for t in DOSES:
        x, y = exact_pts[t]
        assert abs(y - x * x) < 1e-9, "the one-curve law must be exact noiselessly"
    print("  one-curve law y = x^2: exact residual 0 at every dose (exponent 2 = two records)")
    from qiskit_aer import AerSimulator
    sim = AerSimulator(); shots = 60000; cache = {}
    names, builds = all_circuits(); by = dict(zip(names, builds))
    def get(name):
        if name not in cache: cache[name] = sim.run(by[name], shots=shots).result().get_counts()
        return cache[name]
    r = analyze(get)
    pts = law_points(r)
    for t in DOSES:
        print(f"  t={t:4}: S_fb={r['fb'][t]['S']:+.3f} S_fu={r['fu'][t]['S']:+.3f} "
              f"C_cb={r['cb'][t]['C']:+.3f} C_cu={r['cu'][t]['C']:+.3f} "
              f"law resid={pts[t]['resid']:+.3f} R_fd={r['fb'][t]['R_fd']:+.3f}")
        assert abs(r["fb"][t]["S"] - d["fb"][t]["S"]) < 0.05
        assert abs(r["fu"][t]["S"] - 2.5) < 0.05
        assert abs(r["cb"][t]["C"] - d["cb"][t]["C"]) < 0.02
        assert abs(r["cu"][t]["C"] - 1.0) < 0.02
        assert abs(pts[t]["resid"]) < 0.05, "law must hold in Aer"
        assert r["fb"][t]["EFF_rec"] > 0.99 and r["fu"][t]["EFF_rec"] > 0.99
        assert r["cu"][t]["dump_p1"] < 0.02, "coh record must be returned"
        assert r["fu"][t]["dump_p1_max"] < 0.02, "facts record must be returned"
        assert abs(r["cb"][t]["dump_p1"] - np.sin(t * PI / 2) ** 2 / 2) < 0.02, "bend coin gauge"
    print("SELFTEST PASS: fb reproduces 198 exactly, fu revives the fact to 2.5 at every dose, "
          "cb follows cos(theta/2), cu revives to 1.0, one-curve law y=x^2 exact, records "
          "returned in both unbend arms. Cleared to fly.")


def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    d = derive()
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    names, builds = all_circuits()
    circuits = [transpile(qc, backend=backend, optimization_level=3) for qc in builds]
    # pre-flight skeleton audit (197 lesson): within each arm, 2q count must be dose-uniform
    # for t>0 (cry(0) may be folded by the transpiler at t=0 — the known 198 convention).
    audit = {}
    for name, qc in zip(names, circuits):
        arm = name.split("_")[0]; t = float(name.split("_")[1])
        n2 = sum(1 for inst in qc.data if inst.operation.num_qubits == 2)
        audit.setdefault(arm, {}).setdefault(t, []).append(n2)
    for arm, per_t in audit.items():
        sets = {t: sorted(set(v)) for t, v in per_t.items() if t > 0}
        uniq = set()
        for v in sets.values(): uniq.update(v)
        if len(uniq) > 3:
            print(f"AUDIT ABORT: arm {arm} 2q counts vary across doses: {sets}"); sys.exit(1)
        print(f"  audit {arm}: 2q counts t>0 {sets} | t=0 {sorted(set(per_t[0.0]))}")
    job = SamplerV2(mode=backend).run(circuits, shots=shots)
    man = {"exp": 201, "slug": "ledger_of_time", "backend": backend_name, "shots": shots,
           "job_id": job.job_id(), "order": names,
           "exact": {arm: {str(t): d[arm][t] for t in DOSES} for arm in d},
           "audit_2q": {arm: {str(t): sorted(set(v)) for t, v in per_t.items()}
                        for arm, per_t in audit.items()},
           "prereg": {
               "G1_anchors": "S_fb(0) in [2.05,2.45] and >2 at >=5 sigma (198 certified band, "
                             "same backend); S_fb(1) in [1.40,1.90]; C_cb(0) >= 0.80",
               "G2_one_curve_law": "x=C_cb(t)/C_cb(0), y=(S_fb(t)-S_fb(1))/(S_fb(0)-S_fb(1)); "
                                   "|y - x^2| <= 0.12 at each interior dose (0.25/0.5/0.75); "
                                   "y non-increasing within 2 sigma_pair; x strictly decreasing",
               "G3_facts_revival": "rev_f = S_fu(1)-S_fb(1) >= 0.5*(S_fb(0)-S_fb(1)) at >=5 "
                                   "sigma; S_fu(1) > 2 at >=3 sigma (the revived fact violates "
                                   "observer-independence again); max-min S_fu over doses <= 0.25",
               "G4_coh_revival": "rev_c = C_cu(1)-C_cb(1) >= 0.5*C_cb(0) at >=5 sigma; "
                                 "max-min C_cu over doses <= 0.15 (200b's relative gates)",
               "G5_record_gauges": "R_fd(fb) non-decreasing within 0.02, total rise > 0.5; "
                                   "cb dump P1 tracks sin^2(theta/2)/2 within 0.06; "
                                   "cu dump P1 <= 0.15; fu dump P1 (max over wings) <= 0.15",
               "G6_records_record": "E(F_A,F_B) >= 0.85 at every dose in BOTH facts arms",
               "registered_verdict": "conjunction G1-G6; U1 claim proper = G2+G3+G4",
               "budget_predictions": "S_fu(1) in [2.15,2.32]; rev_f in [0.55,0.72]; interior "
                                     "law residuals <= 0.08; C_cb(0) in [0.93,0.98]"}}
    json.dump(man, open(os.path.join(HERE, "..", "results", "exp201_ledger_of_time_manifest.json"), "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits, {shots} shots)")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    man = json.load(open(os.path.join(HERE, "..", "results", "exp201_ledger_of_time_manifest.json")))
    svc = _get_ibm_service(); res = svc.job(man["job_id"]).result()
    shots = man["shots"]; raw = {}
    for idx, name in enumerate(man["order"]):
        r0 = res[idx]; reg = list(r0.data.keys())[0]
        raw[name] = getattr(r0.data, reg).get_counts()
    r = analyze(lambda n: raw[n])
    seS = {arm: {t: float(np.sqrt(sum((1 - r[arm][t]["E"][k] ** 2) / shots for k in r[arm][t]["E"])))
                 for t in DOSES} for arm in ("fb", "fu")}
    seC = 1 / np.sqrt(shots)
    pts = law_points(r)
    S0, S1 = r["fb"][0.0]["S"], r["fb"][1.0]["S"]
    print(f"Exp201 THE LEDGER OF TIME decode | job {man['job_id']} | 198 anchors 2.343/1.575")
    for t in DOSES:
        print(f"  t={t:4}: S_fb={r['fb'][t]['S']:+.4f} (se {seS['fb'][t]:.3f})  "
              f"S_fu={r['fu'][t]['S']:+.4f}  C_cb={r['cb'][t]['C']:+.4f}  "
              f"C_cu={r['cu'][t]['C']:+.4f}  x={pts[t]['x']:+.3f} y={pts[t]['y']:+.3f} "
              f"law resid={pts[t]['resid']:+.3f}")
    # G1 anchors
    z0 = (S0 - 2) / seS["fb"][0.0]
    g1 = 2.05 <= S0 <= 2.45 and z0 >= 5 and 1.40 <= r["fb"][1.0]["S"] <= 1.90 and r["cb"][0.0]["C"] >= 0.80
    # G2 one-curve law
    resid_int = {t: pts[t]["resid"] for t in INTERIOR}
    Sfb = [r["fb"][t]["S"] for t in DOSES]
    sep = [np.sqrt(seS["fb"][DOSES[i]] ** 2 + seS["fb"][DOSES[i + 1]] ** 2) for i in range(4)]
    y_mono = all(Sfb[i + 1] - Sfb[i] <= 2 * sep[i] for i in range(4))
    xs = [r["cb"][t]["C"] for t in DOSES]
    x_mono = all(xs[i] > xs[i + 1] for i in range(4))
    g2 = all(abs(v) <= 0.12 for v in resid_int.values()) and y_mono and x_mono
    # G3 facts revival
    rev_f = r["fu"][1.0]["S"] - r["fb"][1.0]["S"]
    se_rev = float(np.sqrt(seS["fu"][1.0] ** 2 + seS["fb"][1.0] ** 2))
    z_rev = rev_f / se_rev
    z_fu = (r["fu"][1.0]["S"] - 2) / seS["fu"][1.0]
    Sfu = [r["fu"][t]["S"] for t in DOSES]
    g3 = rev_f >= 0.5 * (S0 - S1) and z_rev >= 5 and z_fu >= 3 and (max(Sfu) - min(Sfu)) <= 0.25
    # G4 coherence revival
    rev_c = r["cu"][1.0]["C"] - r["cb"][1.0]["C"]; z_revc = rev_c / (seC * np.sqrt(2))
    Ccu = [r["cu"][t]["C"] for t in DOSES]
    g4 = rev_c >= 0.5 * r["cb"][0.0]["C"] and z_revc >= 5 and (max(Ccu) - min(Ccu)) <= 0.15
    # G5 gauges
    Rf = [r["fb"][t]["R_fd"] for t in DOSES]
    dial = all(Rf[i] < Rf[i + 1] + 0.02 for i in range(4)) and Rf[-1] - Rf[0] > 0.5
    cb_g = all(abs(r["cb"][t]["dump_p1"] - np.sin(t * PI / 2) ** 2 / 2) <= 0.06 for t in DOSES)
    cu_g = all(r["cu"][t]["dump_p1"] <= 0.15 for t in DOSES)
    fu_g = all(r["fu"][t]["dump_p1_max"] <= 0.15 for t in DOSES)
    g5 = dial and cb_g and cu_g and fu_g
    # G6 records record
    g6 = all(r[a][t]["EFF_rec"] >= 0.85 for a in ("fb", "fu") for t in DOSES)
    print(f"\nG1 ANCHORS: S_fb(0)={S0:.3f} ({z0:.0f} sigma), S_fb(1)={S1:.3f}, "
          f"C_cb(0)={r['cb'][0.0]['C']:.3f} {'OK' if g1 else 'MISS'}")
    print(f"G2 ONE-CURVE LAW y=x^2: interior residuals "
          + " ".join(f"{t}:{v:+.3f}" for t, v in resid_int.items())
          + f" | y-mono {y_mono} x-mono {x_mono} {'OK' if g2 else 'MISS'}")
    print(f"G3 UNBEND THE FACT: S_fu(1)={r['fu'][1.0]['S']:.3f} — revival {rev_f:+.3f} "
          f"({z_rev:.0f} sigma; needs >= {0.5 * (S0 - S1):.3f}); above bound at {z_fu:.1f} sigma; "
          f"S_fu spread {max(Sfu) - min(Sfu):.3f} {'OK' if g3 else 'MISS'}")
    print(f"G4 COH REVIVAL: C_cu(1)-C_cb(1) = {rev_c:+.3f} ({z_revc:.0f} sigma); "
          f"C_cu spread {max(Ccu) - min(Ccu):.3f} {'OK' if g4 else 'MISS'}")
    print(f"G5 GAUGES: R_fd {['%.2f' % v for v in Rf]} dial={dial}; cb-track {cb_g}; "
          f"records returned cu={cu_g} fu={fu_g} {'OK' if g5 else 'MISS'}")
    print(f"G6 RECORDS RECORD: min E(F,F) = "
          f"{min(r[a][t]['EFF_rec'] for a in ('fb', 'fu') for t in DOSES):.3f} {'OK' if g6 else 'MISS'}")
    ok = g1 and g2 and g3 and g4 and g5 and g6
    u1 = g2 and g3 and g4
    print(f"U1 CLAIM (G2+G3+G4): {'HELD — objectivity and irreversibility are the same '
          'bath-record bookkeeping: one overlap factor drives both curves (y=x^2), and '
          'uncomputing the record revives BOTH the coherence and the fact, dose-independent'
          if u1 else 'NOT HELD'}")
    print(f"REGISTERED VERDICT (G1-G6): {'HELD' if ok else 'NOT HELD (accounting above)'}")
    json.dump({"job_id": man["job_id"],
               "results": {a: {str(t): r[a][t] for t in DOSES} for a in r},
               "law_points": {str(t): pts[t] for t in DOSES},
               "rev_f": float(rev_f), "sigma_rev_f": float(z_rev), "sigma_fu_above2": float(z_fu),
               "rev_c": float(rev_c), "sigma_rev_c": float(z_revc),
               "g1": bool(g1), "g2": bool(g2), "g3": bool(g3), "g4": bool(g4),
               "g5": bool(g5), "g6": bool(g6), "u1_held": bool(u1), "verdict_ok": bool(ok)},
              open(os.path.join(HERE, "..", "results", "exp201_ledger_of_time_decode.json"), "w"), indent=1)
    print("-> results/exp201_ledger_of_time_decode.json")


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
