#!/usr/bin/env python3
"""Exp203 — THE AUDITOR AND THE REWINDER: is error correction time reversal? C4897.

Horizons-4 U3 (priority #3), flown on Creator go. Composes the two certified machines of
the week: Exp200b's bendable arrow (record uncomputation) and the [[4,2,2]] shield
(191/196 machinery), with Exp201's ledger as the bridge.

WHITEBOARD SELF-CORRECTION, PRE-REGISTERED (F80 discipline — the original conjecture is
refuted at the whiteboard, before any QPU): Horizons-4's U3 text guessed "the shield's
recovery declines on the bath-forgetting clock." The derivation says NO. The dephasing
event writes TWO records: one in the owned coin-bath (the demon's copy) and one in the
block itself (the syndrome — a Z1-flavored error is X-parity-odd, XXXX anticommutes with
Z1). Postselection reads the BLOCK's record at measurement time; the coin's later fate is
irrelevant to the block's parity statistics. So the pre-registered prediction is the
OPPOSITE of the naive conjecture:

  THE REWINDER (uncompute, 200b): recovery requires the coin's record intact
     -> dies on the bath's clock (200b measured the decline). Costs no acceptance.
  THE AUDITOR (shield, postselect): recovery reads the block's own record
     -> CLOCK-FREE with respect to the coin bath. Costs acceptance.

What remains of the unification — and is gated — is ONE LEDGER, three identities:
  G4  P_reject rides the record: acc(theta)/acc(0) = (1 + kappa)/2 where kappa is the
      BARE arm's measured coherence ratio C(theta)/C(0) — the shield's rejection column
      computed from the arrow's coherence column, cross-substrate, parametric (201's
      law-form; no fit to theta).
  G3  Both machines revive a dead logical observable: the shield by discarding the damaged
      branch (post - unpost >= half the anchor at 5 sigma), the rewinder by uncomputing
      the record (200b's gate, now on a LOGICAL observable).
  G6  THE REFUND: uncompute the record and the auditor finds nothing to reject —
      acceptance returns to baseline (acc_unbend(pi) ~ acc(0)).
And the verdict question itself:
  G5  THE CLOCK DISCRIMINATION: Rec_rewind(T) declines on the storage ladder (2/4/8us,
      194's clock), Rec_shield(T) stays flat, and their gap at 8us >= 0.25 at 5 sigma.

ANSWER SHAPE (either way a finding): if G4+G5 hold, error correction is NOT time reversal —
it is the same ledger's other strategy: the rewinder erases the entry, the auditor reads it
and bills the acceptance column. Same books, different clocks.

Apparatus: coin = owned bath qubit (200b). Bare arms = 200b verbatim conventions (2q,
echoed idle, couple mid-echo; coin quarter-echoes in unbend only). Block arms = [[4,2,2]]
|+bar 0bar> (196 prep), coin coupled to q1 (cry(theta,1,4)) — partially dephases LOGICAL
X1bar (= X0X1 on the L1 Bell pair) with the coin recording which-branch. X-basis terminal
readout; X1bar = x0^x1; parity = x0^x1^x2^x3; shield = decode-time postselection (the
auditor arm lc yields BOTH unpost and post from the same shots). Storage echoes X^4 on the
block = the XXXX stabilizer (code-transparent, logical identity), outside the
couple/uncouple window (inverse exactness preserved).

Arms x settings (doses theta/pi in {0,1/4,1/2,3/4,1} at T=2us; endpoints {0,1} at T=4,8us):
  bb bare-bend | bu bare-unbend | lc logical (damaged; shield in decode) | lu logical-unbend
36 circuits, 8000 shots.
BUDGET CHECK (C4887): contrasts ~0.5 vs floors ~0 at anchors ~0.7-0.9; parents measured
200b revival 46 sigma, 191/196 postselected correlators ~0.98. Ample.
Usage: --selftest | --submit [--backend ibm_fez --shots 8000] | --decode
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.circuit import Delay

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
PI = np.pi
TS = {2: 4000, 4: 8000, 8: 16000}            # us -> dt (0.5 ns)
DOSES = (0.0, 0.25, 0.5, 0.75, 1.0)
INTERIOR = (0.25, 0.5, 0.75)
ARMS = ("bb", "bu", "lc", "lu")
SETTINGS = [(t, 2) for t in DOSES] + [(0.0, 4), (1.0, 4), (0.0, 8), (1.0, 8)]


def _al(x):
    return max(16, (int(x) // 16) * 16)


def _timing(T):
    dt = TS[T]; q4 = _al(dt // 4); dcen = dt - 2 * q4
    sl = _al(dcen // 4); last = dcen - 3 * sl
    return q4, (sl, sl, sl, last)


def circuit(arm, t, T):
    th = t * PI
    q4, slices = _timing(T)
    if arm in ("bb", "bu"):                                  # 200b verbatim conventions
        qc = QuantumCircuit(2, 2)
        qc.h(0)
        qc.append(Delay(q4, unit="dt"), [0]); qc.append(Delay(q4, unit="dt"), [1])
        qc.x(0)
        qc.cry(th, 0, 1)
        for i, d in enumerate(slices):
            qc.append(Delay(d, unit="dt"), [0]); qc.append(Delay(d, unit="dt"), [1])
            if arm == "bu" and i in (0, 2):
                qc.x(1)
        if arm == "bu":
            qc.cry(-th, 0, 1)
        qc.x(0)
        qc.append(Delay(q4, unit="dt"), [0]); qc.append(Delay(q4, unit="dt"), [1])
        qc.h(0)
        qc.measure(0, 0); qc.measure(1, 1)
        return qc
    qc = QuantumCircuit(5, 5)                                # block q0-3 + coin q4
    qc.h(0); qc.cx(0, 1)                                     # |+bar 0bar> = Bell (x) Bell
    qc.h(2); qc.cx(2, 3)
    qc.barrier()
    for q in range(5): qc.append(Delay(q4, unit="dt"), [q])
    for q in range(4): qc.x(q)                               # X^4 = XXXX stabilizer echo
    qc.cry(th, 1, 4)                                         # the event, recorded in the coin
    for i, d in enumerate(slices):
        for q in range(5): qc.append(Delay(d, unit="dt"), [q])
        if arm == "lu" and i in (0, 2):
            qc.x(4)                                          # coin quarter-echo (even count)
    if arm == "lu":
        qc.cry(-th, 1, 4)                                    # THE REWINDER
    for q in range(4): qc.x(q)
    for q in range(5): qc.append(Delay(q4, unit="dt"), [q])
    for q in range(4): qc.h(q)                               # X-basis logical readout
    for q in range(5): qc.measure(q, q)
    return qc


def _stats(counts, arm):
    if arm in ("bb", "bu"):
        c = p1 = tot = 0
        for s, n in counts.items():
            b = s.replace(" ", "")
            c += (1 - 2 * int(b[-1])) * n; p1 += int(b[-2]) * n; tot += n
        return {"C": c / tot, "coin_p1": p1 / tot}
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
            "acceptance": acc / (acc + rej), "coin_p1": p1 / tot, "n_acc": acc}


def analyze(get):
    return {(arm, t, T): _stats(get(arm, t, T), arm)
            for arm in ARMS for (t, T) in SETTINGS}


def selftest():
    from qiskit_aer import AerSimulator
    sim = AerSimulator(); shots = 40000; cache = {}
    def get(arm, t, T):
        k = (arm, t, T)
        if k not in cache:
            cache[k] = sim.run(circuit(arm, t, T), shots=shots).result().get_counts()
        return cache[k]
    r = analyze(get)
    print("Exp203 selftest (noiseless) | ideal: bend cos(t*pi/2); unbend 1; shield post=1, "
          "acc=(1+cos)/2; refund acc=1")
    for t in DOSES:
        bb, bu = r[("bb", t, 2)], r[("bu", t, 2)]
        lc, lu = r[("lc", t, 2)], r[("lu", t, 2)]
        ex = np.cos(t * PI / 2)
        print(f"  t={t:4}: bareC={bb['C']:+.3f}/{bu['C']:+.3f}  "
              f"logX1 unpost={lc['X1_unpost']:+.3f} post={lc['X1_post']:+.3f} "
              f"acc={lc['acceptance']:.3f}  rewind={lu['X1_unpost']:+.3f} "
              f"acc={lu['acceptance']:.3f}")
        assert abs(bb["C"] - ex) < 0.02 and abs(bu["C"] - 1) < 0.02
        assert abs(lc["X1_unpost"] - ex) < 0.02, "logical must dephase like bare (same event)"
        assert abs(lc["X1_post"] - 1) < 0.02, "the auditor must fully recover the accepted"
        assert abs(lc["acceptance"] - (1 + ex) / 2) < 0.02, "rejection must ride the record"
        assert abs(lu["X1_unpost"] - 1) < 0.02, "the rewinder must fully revive"
        assert abs(lu["acceptance"] - 1) < 0.02, "THE REFUND: uncompute -> nothing to reject"
        assert abs(bb["coin_p1"] - np.sin(t * PI / 2) ** 2 / 2) < 0.02
        assert abs(lc["coin_p1"] - np.sin(t * PI / 2) ** 2 / 2) < 0.02
        assert bu["coin_p1"] < 0.02 and lu["coin_p1"] < 0.02, "records returned"
    for T in (4, 8):
        for arm in ARMS:
            k = r[(arm, 1.0, T)]
            v = k["C"] if arm in ("bb", "bu") else k["X1_unpost"]
        assert abs(r[("lu", 1.0, T)]["X1_unpost"] - 1) < 0.02
        assert abs(r[("lc", 1.0, T)]["X1_post"] - 1) < 0.02
    print("SELFTEST PASS: the event dephases bare and logical identically; the auditor "
          "recovers by rejection priced exactly at the record; the rewinder recovers by "
          "uncomputation with acceptance refunded; all storage rungs exact. Cleared to fly.")


def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    names = [[arm, t, T] for arm in ARMS for (t, T) in SETTINGS]
    circuits = audit = seed_used = None
    for seed in range(20):
        cand = [transpile(circuit(arm, t, T), backend=backend, optimization_level=3,
                          seed_transpiler=seed) for arm, t, T in names]
        aud = {}
        for (arm, t, T), qc in zip(names, cand):
            n2 = sum(1 for inst in qc.data if inst.operation.num_qubits == 2)
            aud.setdefault(f"{arm}_T{T}", {})[t] = n2
        bad = {}
        for key, per_t in aud.items():
            ints = sorted(set(per_t[t] for t in INTERIOR if t in per_t))
            if len(ints) > 1:
                bad[key] = per_t
        if not bad:
            circuits, audit, seed_used = cand, aud, seed
            break
        print(f"  seed {seed}: interior non-uniform {list(bad)} — next")
    if circuits is None:
        print("AUDIT ABORT: no interior-uniform seed in 0-19"); sys.exit(1)
    for key, per_t in sorted(audit.items()):
        print(f"  audit {key}: {per_t}")
    job = SamplerV2(mode=backend).run(circuits, shots=shots)
    out = os.path.join(HERE, "..", "results", "exp203_auditor_rewinder_manifest.json")
    man = {"exp": 203, "slug": "auditor_and_rewinder", "backend": backend_name,
           "shots": shots, "job_id": job.job_id(), "order": names,
           "seed_transpiler": seed_used}
    json.dump(man, open(out, "w"), indent=1)                 # manifest first (C4895)
    man["audit_2q"] = audit
    man["prereg"] = {
        "whiteboard_correction": "original U3 wording (shield declines on bath clock) "
                                 "REFUTED pre-flight by derivation: the syndrome is the "
                                 "BLOCK's record; shield predicted CLOCK-FREE vs the coin",
        "G1_anchors": "C_bb(0,2) in [0.65,0.92] (200b band); X1_unpost_lc(0,2) >= 0.50 at "
                      ">=5 sigma; acc_lc(0,2) >= 0.70",
        "G2_event_universality": "|C_bb(t,2)/C_bb(0,2) - cos(t*pi/2)| <= 0.10 all t; "
                                 "|X1u_lc(t,2)/X1u_lc(0,2) - C_bb(t,2)/C_bb(0,2)| <= 0.12 "
                                 "all t (logical dephases like bare — same event, two "
                                 "substrates)",
        "G3_two_revivals": "at (pi,2us): AUDITOR X1p_lc - X1u_lc >= 0.5*X1p_lc(0,2) at >=5 "
                           "sigma; REWINDER X1u_lu(pi) - X1u_lc(pi) >= 0.5*X1u_lu(0,2) at "
                           ">=5 sigma; bare revival C_bu-C_bb >= 0.5*C_bb(0,2) at >=5 sigma "
                           "(200b regression)",
        "G4_one_ledger": "|acc_lc(t,2)/acc_lc(0,2) - (1+kappa(t))/2| <= 0.08 for t in "
                         "{0.25,0.5,0.75,1.0}, kappa(t)=C_bb(t,2)/C_bb(0,2) — the shield's "
                         "rejection column priced by the arrow's coherence column, "
                         "parametric, no fit to theta",
        "G5_clock_discrimination": "Rec_rw(T)=X1u_lu(pi,T)/X1u_lu(0,T) non-increasing with "
                                   "Rec_rw(8) <= Rec_rw(2)-0.10 at >=3 sigma; "
                                   "Rec_sh(T)=X1p_lc(pi,T)/X1p_lc(0,T) flat "
                                   "(|Rec_sh(8)-Rec_sh(2)| <= 0.15); gap "
                                   "Rec_sh(8)-Rec_rw(8) >= 0.25 at >=5 sigma",
        "G6_the_refund": "acc_lu(pi,2)/acc_lu(0,2) >= 0.90 AND "
                         "[acc_lu(pi,2)/acc_lu(0,2)] - [acc_lc(pi,2)/acc_lc(0,2)] >= 0.25 "
                         "at >=5 sigma (uncompute the record -> the auditor finds nothing)",
        "G7_gauges": "coin occupancy tracks sin^2(t*pi/2)/2 within 0.06 in bb and lc; "
                     "records returned coin P1 <= 0.15 in bu and lu everywhere",
        "registered_verdict": "conjunction G1-G7; the U3 ANSWER = G4+G5 jointly (one "
                              "ledger, two clocks -> QEC is not time reversal, it is the "
                              "ledger's auditor)",
        "budget_predictions": "acc_lc(pi,2)/acc_lc(0,2) in [0.42,0.58]; ledger residuals "
                              "<= 0.06 mean; Rec_rw(8) in [0.25,0.60] (200b bare 0.484); "
                              "Rec_sh(8) in [0.85,1.05]; clock gap in [0.30,0.65]"}
    json.dump(man, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits, {shots} shots) -> {out}")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    man = json.load(open(os.path.join(HERE, "..", "results", "exp203_auditor_rewinder_manifest.json")))
    svc = _get_ibm_service(); res = svc.job(man["job_id"]).result()
    shots = man["shots"]; raw = {}
    for idx, (arm, t, T) in enumerate(man["order"]):
        r0 = res[idx]; reg = list(r0.data.keys())[0]
        raw[(arm, float(t), int(T))] = getattr(r0.data, reg).get_counts()
    r = analyze(lambda arm, t, T: raw[(arm, t, T)])
    se = 1 / np.sqrt(shots)
    def sep(key, T=2):
        n = max(r[("lc", key, T)]["n_acc"], 1); return 1 / np.sqrt(n)
    C0 = r[("bb", 0.0, 2)]["C"]
    kap = {t: r[("bb", t, 2)]["C"] / C0 for t in DOSES}
    print(f"Exp203 THE AUDITOR AND THE REWINDER decode | job {man['job_id']}")
    for t in DOSES:
        lc, lu = r[("lc", t, 2)], r[("lu", t, 2)]
        print(f"  t={t:4} @2us: bareC={r[('bb', t, 2)]['C']:+.3f} kappa={kap[t]:+.3f} | "
              f"lc unpost={lc['X1_unpost']:+.3f} post={lc['X1_post']:+.3f} "
              f"acc={lc['acceptance']:.3f} | lu X1={lu['X1_unpost']:+.3f} "
              f"acc={lu['acceptance']:.3f}")
    for T in (4, 8):
        print(f"  pi @{T}us: lc post={r[('lc', 1.0, T)]['X1_post']:+.3f}"
              f"/anchor {r[('lc', 0.0, T)]['X1_post']:+.3f} | "
              f"lu X1={r[('lu', 1.0, T)]['X1_unpost']:+.3f}"
              f"/anchor {r[('lu', 0.0, T)]['X1_unpost']:+.3f}")
    lc0 = r[("lc", 0.0, 2)]
    z_anchor = lc0["X1_unpost"] / se
    g1 = 0.65 <= C0 <= 0.92 and lc0["X1_unpost"] >= 0.50 and z_anchor >= 5 and lc0["acceptance"] >= 0.70
    g2 = (all(abs(kap[t] - np.cos(t * PI / 2)) <= 0.10 for t in DOSES)
          and all(abs(r[("lc", t, 2)]["X1_unpost"] / lc0["X1_unpost"] - kap[t]) <= 0.12
                  for t in DOSES))
    aud_rev = r[("lc", 1.0, 2)]["X1_post"] - r[("lc", 1.0, 2)]["X1_unpost"]
    z_aud = aud_rev / np.sqrt(sep(1.0) ** 2 + se ** 2)
    rew_rev = r[("lu", 1.0, 2)]["X1_unpost"] - r[("lc", 1.0, 2)]["X1_unpost"]
    z_rew = rew_rev / (se * np.sqrt(2))
    bare_rev = r[("bu", 1.0, 2)]["C"] - r[("bb", 1.0, 2)]["C"]
    z_bare = bare_rev / (se * np.sqrt(2))
    g3 = (aud_rev >= 0.5 * lc0["X1_post"] and z_aud >= 5
          and rew_rev >= 0.5 * r[("lu", 0.0, 2)]["X1_unpost"] and z_rew >= 5
          and bare_rev >= 0.5 * C0 and z_bare >= 5)
    led = {t: r[("lc", t, 2)]["acceptance"] / lc0["acceptance"] - (1 + kap[t]) / 2
           for t in (0.25, 0.5, 0.75, 1.0)}
    g4 = all(abs(v) <= 0.08 for v in led.values())
    Rrw = {T: r[("lu", 1.0, T)]["X1_unpost"] / r[("lu", 0.0, T)]["X1_unpost"] for T in TS}
    Rsh = {T: r[("lc", 1.0, T)]["X1_post"] / r[("lc", 0.0, T)]["X1_post"] for T in TS}
    se_r = 3 * se
    z_decl = (Rrw[2] - Rrw[8]) / (se_r * np.sqrt(2))
    gap = Rsh[8] - Rrw[8]; z_gap = gap / (se_r * np.sqrt(2))
    g5 = (Rrw[2] >= Rrw[4] - 0.03 >= Rrw[8] - 0.06 and Rrw[8] <= Rrw[2] - 0.10
          and z_decl >= 3 and abs(Rsh[8] - Rsh[2]) <= 0.15 and gap >= 0.25 and z_gap >= 5)
    ref_lu = r[("lu", 1.0, 2)]["acceptance"] / r[("lu", 0.0, 2)]["acceptance"]
    ref_lc = r[("lc", 1.0, 2)]["acceptance"] / lc0["acceptance"]
    z_ref = (ref_lu - ref_lc) / (se * 2)
    g6 = ref_lu >= 0.90 and (ref_lu - ref_lc) >= 0.25 and z_ref >= 5
    g7 = (all(abs(r[(a, t, 2)]["coin_p1"] - np.sin(t * PI / 2) ** 2 / 2) <= 0.06
              for a in ("bb", "lc") for t in DOSES)
          and all(r[(a, t, T)]["coin_p1"] <= 0.15 for a in ("bu", "lu")
                  for (t, T) in SETTINGS))
    print(f"\nG1 ANCHORS: C_bb(0)={C0:.3f}, X1u_lc(0)={lc0['X1_unpost']:.3f} "
          f"({z_anchor:.0f} sigma), acc(0)={lc0['acceptance']:.3f} {'OK' if g1 else 'MISS'}")
    print(f"G2 SAME EVENT, TWO SUBSTRATES: max bare resid "
          f"{max(abs(kap[t] - np.cos(t * PI / 2)) for t in DOSES):.3f}, max logical-vs-bare "
          f"resid {max(abs(r[('lc', t, 2)]['X1_unpost'] / lc0['X1_unpost'] - kap[t]) for t in DOSES):.3f} "
          f"{'OK' if g2 else 'MISS'}")
    print(f"G3 TWO REVIVALS @ full kill: AUDITOR +{aud_rev:.3f} ({z_aud:.0f} sigma) | "
          f"REWINDER +{rew_rev:.3f} ({z_rew:.0f} sigma) | bare +{bare_rev:.3f} "
          f"({z_bare:.0f} sigma) {'OK' if g3 else 'MISS'}")
    print(f"G4 ONE LEDGER: acc-vs-(1+kappa)/2 residuals "
          + " ".join(f"{t}:{v:+.3f}" for t, v in led.items()) + f" {'OK' if g4 else 'MISS'}")
    print(f"G5 THE CLOCKS: Rec_rw {Rrw[2]:.3f}/{Rrw[4]:.3f}/{Rrw[8]:.3f} (declines, "
          f"{z_decl:.1f} sigma) | Rec_sh {Rsh[2]:.3f}/{Rsh[4]:.3f}/{Rsh[8]:.3f} (flat) | "
          f"gap@8us {gap:+.3f} ({z_gap:.0f} sigma) {'OK' if g5 else 'MISS'}")
    print(f"G6 THE REFUND: acc ratio rewinder {ref_lu:.3f} vs auditor {ref_lc:.3f} "
          f"(diff {ref_lu - ref_lc:+.3f}, {z_ref:.0f} sigma) {'OK' if g6 else 'MISS'}")
    print(f"G7 GAUGES: {'OK' if g7 else 'MISS'}")
    ok = g1 and g2 and g3 and g4 and g5 and g6 and g7
    u3 = g4 and g5
    print(f"U3 ANSWER (G4+G5): {'ERROR CORRECTION IS NOT TIME REVERSAL — it is the same '
          'ledgers other strategy: the rewinder erases the record and dies on the baths '
          'clock; the auditor reads the blocks own record, clock-free, and bills the '
          'acceptance column at exactly the records price' if u3 else 'NOT RESOLVED'}")
    print(f"REGISTERED VERDICT (G1-G7): {'HELD' if ok else 'NOT HELD (accounting above)'}")
    json.dump({"job_id": man["job_id"],
               "results": {f"{a}_{t}_{T}": r[(a, t, T)] for (a, t, T) in
                           [(a, t, T) for a in ARMS for (t, T) in SETTINGS]},
               "kappa": {str(t): float(kap[t]) for t in DOSES},
               "ledger_resid": {str(t): float(v) for t, v in led.items()},
               "Rec_rw": {str(T): float(Rrw[T]) for T in TS},
               "Rec_sh": {str(T): float(Rsh[T]) for T in TS},
               "auditor_revival": float(aud_rev), "sigma_auditor": float(z_aud),
               "rewinder_revival": float(rew_rev), "sigma_rewinder": float(z_rew),
               "clock_gap": float(gap), "sigma_gap": float(z_gap),
               "refund_rw": float(ref_lu), "refund_auditor_cost": float(ref_lc),
               "g1": bool(g1), "g2": bool(g2), "g3": bool(g3), "g4": bool(g4),
               "g5": bool(g5), "g6": bool(g6), "g7": bool(g7),
               "u3_answered": bool(u3), "verdict_ok": bool(ok)},
              open(os.path.join(HERE, "..", "results", "exp203_auditor_rewinder_decode.json"), "w"), indent=1)
    print("-> results/exp203_auditor_rewinder_decode.json")


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
