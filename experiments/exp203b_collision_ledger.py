#!/usr/bin/env python3
"""Exp203b — THE COLLISION LEDGER, flown: XOR law + the non-Pauli deviation as instrument. C4899.

Flies the prediction set FROZEN in docs/collision-corrected-ledger-whisper-c4898.md (P1-P4),
on Creator go. Exp203's registered NOT HELD stands; this is a new instrument, not an appeal.

Apparatus = Exp203's lc arm (block [[4,2,2]] |+bar 0bar> + coin, cry(theta,1,4) mid-storage,
2us echoed idle, X-basis readout, shield = decode-time postselection), with two structural
changes, both pre-registered:
  * ANTI-FOLDING (the 203 G2 artifact fix): cry decomposed manually as
    ry(th/2,coin); cx(1,coin); BARRIER; ry(-th/2,coin); cx(1,coin) — 2 CX at EVERY dose
    including theta=0, so all doses carry the same layout constraint and the skeleton audit
    demands FULL dose uniformity (not just interior).
  * TWO COMPILATION ARMS: plain vs TWIRLED (Exp199 doctrine). Twirl = per-slice {I,X}
    frames on the 4 block qubits during the storage window (P ... P net identity around
    each slice), K=8 deterministic instances per dose (seeded RNG), 1500 shots each,
    POOLED at decode -> the pooled channel is Pauli-twirled in the parity-relevant sector.
    Each arm is graded against its OWN in-arm theta=0 anchors (p_n, c0, m_odd), so the
    twirl's extra 1q burden is absorbed by construction.

FROZEN PREDICTIONS (C4898 sec.4, verbatim):
  P1 (both arms):   XOR law |acc - [(1-p_n)(1-e_r)+p_n*e_r]| <= 0.03 every dose;
                    checkpoint acc(pi) in [0.47,0.53].
  P2 (twirled arm): static-Pauli collision model FITS: |post - model| <= 0.06 every dose.
  P3 (plain arm):   model under-predicts, residual monotonically non-decreasing (0.04 tol)
                    and resid(pi) >= +0.10.
  P4:               resid_plain(pi) - resid_twirled(pi) >= 0.10 at >=5 sigma.
G0 (anchors, gauge-tier): acc(0) >= 0.55 and X1_post(0) >= 0.55 at >=5 sigma, both arms;
coin occupancy tracks sin^2(th/2)/2 within 0.06, both arms, every dose.
Registered verdict = G0 AND P1 AND P2 AND P3 AND P4.
Outcome meanings fixed in C4898: all hold -> collision ledger is law + deviation certified
as coherent-noise metrology; P2 fails -> the MODEL is wrong (twirled data localizes the
missing term); P1 fails -> flip independence breaks (F111 spatial tail in the ledger).

SCOPE NOTE (pre-registered): C4898's place-by-measured-coin fix applies to REWINDER
flights; 203b has no unbend arm and never consults the coin's fate — not applied here.
Model: post(t) = [(1-p_n)(1-e_r)c0 - p_n*e_r*m_odd]/acc_meas(t), all parameters in-arm.
BUDGET CHECK (C4887): effects ~0.1-0.2 vs se ~0.01-0.02; P4 expected ~7 sigma at the
C4898-measured deviation (+0.199). Feasible.
Usage: --selftest | --submit [--backend ibm_fez] | --decode
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.circuit import Delay

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
PI = np.pi
DOSES = (0.0, 0.25, 0.5, 0.75, 1.0)
T_DT = 4000                                   # 2us storage (Exp203's TS[2])
K_TWIRL = 8
SHOTS_TW = 1500                               # x8 instances = 12000 pooled per dose
SHOTS_PL = 12000


def _al(x):
    return max(16, (int(x) // 16) * 16)


def _timing():
    q4 = _al(T_DT // 4); dcen = T_DT - 2 * q4
    sl = _al(dcen // 4); last = dcen - 3 * sl
    return q4, (sl, sl, sl, last)


def _manual_cry(qc, th, ctrl, targ):
    """cry(th) as ry-cx-BARRIER-ry-cx: 2 CX at every dose; barrier blocks theta=0 fold."""
    qc.ry(th / 2, targ)
    qc.cx(ctrl, targ)
    qc.barrier(ctrl, targ)
    qc.ry(-th / 2, targ)
    qc.cx(ctrl, targ)


def _frames(t, inst):
    """Deterministic per-instance twirl frames: [slice][qubit] in {0,1} (I or X)."""
    rng = np.random.default_rng([203, int(round(t * 100)), inst])
    return rng.integers(0, 2, size=(4, 4))


def circuit(arm, t, inst=0):
    th = t * PI
    q4, slices = _timing()
    qc = QuantumCircuit(5, 5)
    qc.h(0); qc.cx(0, 1)                      # |+bar 0bar> = Bell (x) Bell
    qc.h(2); qc.cx(2, 3)
    qc.barrier()
    for q in range(5): qc.append(Delay(q4, unit="dt"), [q])
    for q in range(4): qc.x(q)                # X^4 = XXXX stabilizer echo
    _manual_cry(qc, th, 1, 4)                 # the event, anti-folding form
    fr = _frames(t, inst) if arm == "twirled" else None
    for i, d in enumerate(slices):
        if fr is not None:
            for q in range(4):
                if fr[i][q]: qc.x(q)          # twirl frame in
        for q in range(5): qc.append(Delay(d, unit="dt"), [q])
        if fr is not None:
            for q in range(4):
                if fr[i][q]: qc.x(q)          # frame out (net identity)
    for q in range(4): qc.x(q)
    for q in range(5): qc.append(Delay(q4, unit="dt"), [q])
    for q in range(4): qc.h(q)                # X-basis logical readout
    for q in range(5): qc.measure(q, q)
    return qc


def _stats(counts):
    acc = rej = xu = xp = p1 = tot = 0
    for s, n in counts.items():
        b = s.replace(" ", "")
        v = [int(b[-1 - i]) for i in range(5)]
        x1 = 1 - 2 * (v[0] ^ v[1])
        xu += x1 * n; p1 += v[4] * n; tot += n
        if (v[0] ^ v[1] ^ v[2] ^ v[3]) == 0:
            acc += n; xp += x1 * n
        else:
            rej += n
    return {"X1_unpost": xu / tot, "X1_post": xp / acc if acc else 0.0,
            "acceptance": acc / (acc + rej), "coin_p1": p1 / tot,
            "n_acc": acc, "n_tot": tot}


def _pool(list_of_counts):
    tot = {}
    for c in list_of_counts:
        for k, n in c.items():
            tot[k] = tot.get(k, 0) + n
    return tot


def arm_model(r_arm):
    """In-arm anchors -> XOR + collision-model predictions per dose."""
    acc0 = r_arm[0.0]["acceptance"]; c0 = r_arm[0.0]["X1_post"]
    u0 = r_arm[0.0]["X1_unpost"]
    p_n = 1 - acc0
    m_odd = (u0 - acc0 * c0) / p_n if p_n > 1e-9 else 0.0
    out = {"p_n": p_n, "c0": c0, "m_odd": m_odd, "per_dose": {}}
    for t in DOSES:
        e = (1 - np.cos(t * PI / 2)) / 2
        acc_xor = (1 - p_n) * (1 - e) + p_n * e
        acc_m = r_arm[t]["acceptance"]
        post_model = ((1 - p_n) * (1 - e) * c0 - p_n * e * m_odd) / acc_m if acc_m else 0.0
        out["per_dose"][t] = {
            "e_r": float(e), "acc_meas": float(acc_m), "acc_xor": float(acc_xor),
            "acc_resid": float(acc_m - acc_xor),
            "post_meas": float(r_arm[t]["X1_post"]), "post_model": float(post_model),
            "post_resid": float(r_arm[t]["X1_post"] - post_model)}
    return out


def selftest():
    from qiskit.quantum_info import Statevector
    # 1) manual cry == cry (statevector, theta=0.6pi, on the un-measured core)
    def core(use_manual, th):
        qc = QuantumCircuit(5)
        qc.h(0); qc.cx(0, 1); qc.h(2); qc.cx(2, 3)
        if use_manual:
            qc.ry(th / 2, 4); qc.cx(1, 4); qc.ry(-th / 2, 4); qc.cx(1, 4)
        else:
            qc.cry(th, 1, 4)
        return Statevector(qc)
    th = 0.6 * PI
    assert core(True, th).equiv(core(False, th)), "manual cry must equal cry"
    # 2) twirl instances are net identity (statevector equivalence to plain)
    for inst in (0, 3, 7):
        a = Statevector(circuit("plain", 0.5).remove_final_measurements(inplace=False))
        b = Statevector(circuit("twirled", 0.5, inst).remove_final_measurements(inplace=False))
        assert a.equiv(b), f"twirl instance {inst} must be net identity"
    print("manual-cry == cry (statevector); twirl frames net-identity: PASS")
    # 3) Aer: both arms reproduce lc ideals; XOR/model close with p_n ~ 0
    from qiskit_aer import AerSimulator
    sim = AerSimulator(); cache = {}
    def get(arm, t):
        k = (arm, t)
        if k not in cache:
            if arm == "plain":
                cache[k] = sim.run(circuit("plain", t), shots=24000).result().get_counts()
            else:
                cache[k] = _pool([sim.run(circuit("twirled", t, i), shots=3000)
                                  .result().get_counts() for i in range(K_TWIRL)])
        return cache[k]
    r = {arm: {t: _stats(get(arm, t)) for t in DOSES} for arm in ("plain", "twirled")}
    for arm in ("plain", "twirled"):
        for t in DOSES:
            ex = np.cos(t * PI / 2)
            s = r[arm][t]
            assert abs(s["X1_unpost"] - ex) < 0.03, f"{arm} t={t} unpost"
            assert abs(s["X1_post"] - 1) < 0.03, f"{arm} t={t} post"
            assert abs(s["acceptance"] - (1 + ex) / 2) < 0.03, f"{arm} t={t} acc"
            assert abs(s["coin_p1"] - np.sin(t * PI / 2) ** 2 / 2) < 0.03
        m = arm_model(r[arm])
        for t in DOSES:
            assert abs(m["per_dose"][t]["acc_resid"]) < 0.03, f"{arm} XOR noiseless"
        print(f"  {arm:>7}: ideals reproduced (acc=(1+cos)/2, post=1); XOR residuals "
              f"{max(abs(m['per_dose'][t]['acc_resid']) for t in DOSES):.3f}")
    print("SELFTEST PASS: anti-folding cry exact, twirl net-identity, both arms reproduce "
          "the lc ideals, XOR law exact noiselessly. P2-P4 are noise-dependent claims — "
          "they can only be graded on hardware. Cleared to fly.")


def submit(backend_name):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    names, builds, shots_list = [], [], []
    for t in DOSES:
        names.append(["plain", t, 0]); builds.append(circuit("plain", t))
        shots_list.append(SHOTS_PL)
    for t in DOSES:
        for i in range(K_TWIRL):
            names.append(["twirled", t, i]); builds.append(circuit("twirled", t, i))
            shots_list.append(SHOTS_TW)
    circuits = audit = seed_used = None
    for seed in range(20):
        cand = [transpile(qc, backend=backend, optimization_level=3, seed_transpiler=seed)
                for qc in builds]
        aud = {}
        for (arm, t, i), qc in zip(names, cand):
            n2 = sum(1 for inst in qc.data if inst.operation.num_qubits == 2)
            aud.setdefault(arm, {}).setdefault(t, set()).add(n2)
        # FULL dose uniformity per arm (the anti-folding fix's whole point)
        if all(len(set.union(*per.values())) == 1 for per in aud.values()):
            circuits, seed_used = cand, seed
            audit = {a: {str(t): sorted(v) for t, v in per.items()} for a, per in aud.items()}
            break
        print(f"  seed {seed}: 2q counts "
              f"{ {a: {t: sorted(v) for t, v in per.items()} for a, per in aud.items()} } — next")
    if circuits is None:
        print("AUDIT ABORT: no fully dose-uniform seed in 0-19"); sys.exit(1)
    for a, per in audit.items():
        print(f"  audit {a}: 2q={sorted(set(x for v in per.values() for x in v))} "
              f"(uniform across ALL doses, seed {seed_used})")
    pubs = [(qc, None, s) for qc, s in zip(circuits, shots_list)]
    job = SamplerV2(mode=backend).run(pubs)
    out = os.path.join(HERE, "..", "results", "exp203b_collision_ledger_manifest.json")
    man = {"exp": "203b", "slug": "collision_ledger", "backend": backend_name,
           "shots_plain": SHOTS_PL, "shots_twirl": SHOTS_TW, "k_twirl": K_TWIRL,
           "job_id": job.job_id(), "order": names, "seed_transpiler": seed_used}
    json.dump(man, open(out, "w"), indent=1)                 # manifest first (C4895)
    man["audit_2q"] = audit
    man["prereg"] = {
        "frozen_in": "docs/collision-corrected-ledger-whisper-c4898.md sec.4 (P1-P4 "
                     "verbatim, frozen BEFORE this flight was authorized)",
        "G0_anchors": "acc(0) >= 0.55 and X1_post(0) >= 0.55 at >=5 sigma, both arms; "
                      "coin occupancy tracks sin^2/2 within 0.06 both arms every dose",
        "P1": "XOR law |resid| <= 0.03 every dose both arms; acc(pi) in [0.47,0.53] both",
        "P2": "twirled arm: |post - model| <= 0.06 every dose (in-arm anchors)",
        "P3": "plain arm: post_resid non-decreasing (0.04 tol) and resid(pi) >= +0.10",
        "P4": "resid_plain(pi) - resid_twirled(pi) >= 0.10 at >=5 sigma",
        "registered_verdict": "G0 and P1 and P2 and P3 and P4",
        "scope": "no unbend arm -> coin quality non-critical (place-by-measured deferred "
                 "to rewinder flights); twirl scope = storage-idle {I,X} frames on block "
                 "qubits (gate-coherent errors outside twirl scope — if P2 fails, scope "
                 "is part of the diagnosis); arms graded against their OWN anchors",
        "budget_predictions": "plain resid(pi) in [0.12,0.28] (C4898 measured +0.199); "
                              "twirled resid(pi) in [-0.06,+0.06]; P4 sigma ~7; "
                              "acc(pi) within 0.02 of 0.50 both arms"}
    json.dump(man, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} pubs: 5x{SHOTS_PL} plain + "
          f"{5*K_TWIRL}x{SHOTS_TW} twirled) -> {out}")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    man = json.load(open(os.path.join(HERE, "..", "results", "exp203b_collision_ledger_manifest.json")))
    svc = _get_ibm_service(); res = svc.job(man["job_id"]).result()
    raw = {}
    for idx, (arm, t, i) in enumerate(man["order"]):
        r0 = res[idx]; reg = list(r0.data.keys())[0]
        raw.setdefault((arm, float(t)), []).append(getattr(r0.data, reg).get_counts())
    r = {arm: {t: _stats(_pool(raw[(arm, t)])) for t in DOSES}
         for arm in ("plain", "twirled")}
    M = {arm: arm_model(r[arm]) for arm in ("plain", "twirled")}
    print(f"Exp203b THE COLLISION LEDGER decode | job {man['job_id']}")
    for arm in ("plain", "twirled"):
        m = M[arm]
        print(f"  {arm} (p_n={m['p_n']:.3f} c0={m['c0']:.3f} m_odd={m['m_odd']:+.3f}):")
        for t in DOSES:
            d = m["per_dose"][t]
            print(f"    t={t:4}: acc={d['acc_meas']:.4f} (XOR {d['acc_xor']:.4f}, "
                  f"resid {d['acc_resid']:+.4f}) | post={d['post_meas']:.4f} "
                  f"(model {d['post_model']:.4f}, resid {d['post_resid']:+.4f})")
    def se_post(arm, t):
        s = r[arm][t]
        return float(np.sqrt(max(1 - s["X1_post"] ** 2, 1e-9) / max(s["n_acc"], 1)))
    # G0
    g0 = True
    for arm in ("plain", "twirled"):
        s0 = r[arm][0.0]
        z = s0["X1_post"] / se_post(arm, 0.0)
        g0 = g0 and s0["acceptance"] >= 0.55 and s0["X1_post"] >= 0.55 and z >= 5
        g0 = g0 and all(abs(r[arm][t]["coin_p1"] - np.sin(t * PI / 2) ** 2 / 2) <= 0.06
                        for t in DOSES)
    # P1
    p1 = all(abs(M[arm]["per_dose"][t]["acc_resid"]) <= 0.03
             for arm in ("plain", "twirled") for t in DOSES) \
         and all(0.47 <= M[arm]["per_dose"][1.0]["acc_meas"] <= 0.53
                 for arm in ("plain", "twirled"))
    # P2
    p2 = all(abs(M["twirled"]["per_dose"][t]["post_resid"]) <= 0.06 for t in DOSES)
    # P3
    rp = [M["plain"]["per_dose"][t]["post_resid"] for t in DOSES]
    p3 = all(rp[i + 1] >= rp[i] - 0.04 for i in range(4)) and rp[-1] >= 0.10
    # P4 (se: post SEs + anchor-parameter propagation, conservative 1.5x)
    d4 = M["plain"]["per_dose"][1.0]["post_resid"] - M["twirled"]["per_dose"][1.0]["post_resid"]
    se4 = 1.5 * float(np.sqrt(se_post("plain", 1.0) ** 2 + se_post("twirled", 1.0) ** 2
                              + se_post("plain", 0.0) ** 2 + se_post("twirled", 0.0) ** 2))
    z4 = d4 / se4
    p4 = d4 >= 0.10 and z4 >= 5
    print(f"\nG0 ANCHORS+GAUGES: {'OK' if g0 else 'MISS'}")
    print(f"P1 XOR LAW: max|resid| "
          f"{max(abs(M[a]['per_dose'][t]['acc_resid']) for a in M for t in DOSES):.4f} "
          f"(<=0.03); acc(pi) {M['plain']['per_dose'][1.0]['acc_meas']:.4f}/"
          f"{M['twirled']['per_dose'][1.0]['acc_meas']:.4f} {'OK' if p1 else 'MISS'}")
    print(f"P2 TWIRLED FITS: max|resid| "
          f"{max(abs(M['twirled']['per_dose'][t]['post_resid']) for t in DOSES):.4f} "
          f"(<=0.06) {'OK' if p2 else 'MISS'}")
    print(f"P3 PLAIN DEVIATES: residuals {['%+.3f' % v for v in rp]}, resid(pi)="
          f"{rp[-1]:+.4f} (>=+0.10) {'OK' if p3 else 'MISS'}")
    print(f"P4 DISCRIMINATION: {d4:+.4f} ({z4:.1f} sigma, needs >=0.10 at >=5) "
          f"{'OK' if p4 else 'MISS'}")
    ok = g0 and p1 and p2 and p3 and p4
    print(f"VERDICT: {'THE COLLISION LEDGER IS LAW — XOR arithmetic holds in both '
          'compilations, the twirled arm obeys the static-Pauli collision model, and the '
          'plain arms deviation reproduces: the ledgers coherence column reads the chips '
          'own non-Pauli noise' if ok else 'NOT HELD (accounting above)'}")
    json.dump({"job_id": man["job_id"],
               "results": {a: {str(t): r[a][t] for t in DOSES} for a in r},
               "models": {a: {"p_n": M[a]["p_n"], "c0": M[a]["c0"], "m_odd": M[a]["m_odd"],
                              "per_dose": {str(t): M[a]["per_dose"][t] for t in DOSES}}
                          for a in M},
               "p4_diff": float(d4), "p4_sigma": float(z4),
               "g0": bool(g0), "p1": bool(p1), "p2": bool(p2), "p3": bool(p3),
               "p4": bool(p4), "verdict_ok": bool(ok)},
              open(os.path.join(HERE, "..", "results", "exp203b_collision_ledger_decode.json"), "w"), indent=1)
    print("-> results/exp203b_collision_ledger_decode.json")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true"); ap.add_argument("--submit", action="store_true")
    ap.add_argument("--decode", action="store_true")
    ap.add_argument("--backend", default="ibm_fez")
    a = ap.parse_args()
    if a.selftest: selftest()
    elif a.submit: submit(a.backend)
    elif a.decode: decode()
    else: ap.print_help()
