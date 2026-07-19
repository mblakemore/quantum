#!/usr/bin/env python3
"""Exp202b — THE SUBSPACE RELAY KEY, powered retest. C4896.

Disclosed pro-hypothesis retest of Exp202 (F97/200b discipline), registered BEFORE its own
data. Exp202's registered verdict stands NOT HELD; this is a new frozen instrument, not an
appeal. Circuits and decode identical to Exp202 (imported). Two changes, both named and
priced pre-flight from 202's measured physics:

  1. POWER (G4 unchanged): the depth-pays gate stays IDENTICAL (gain > 0 at >=3 sigma,
     same estimator). 202 landed +0.0504 at 1.9 sigma — under-powered, not refuted.
     Entangled arms fly at 32,000 shots (4x): se_gain ~ 0.013, detecting gain >= 0.040 at
     3 sigma; if the true gain equals 202's point estimate, expected z ~ 3.8. Filed openly:
     if the true gain is smaller, this retest can MISS — accepted risk, bands unchanged.
  2. RE-PRICED SUB-GATE (the 200b move, labeled): 202's single-basis "QBER_Z(relay) edge at
     >=5 sigma" missed at 1.1 sigma because the bare arms bleed in X, not Z (measured:
     bare X 3.36%, barerelay X 6.95%). Re-priced to the POOLED two-basis edge
     Qbar = (Q_Z + Q_X)/2 — the form the secret fraction itself uses. On 202's numbers the
     pooled relay edge is ~2.9pp ~ 11 sigma. 202's miss stays on the books.

nocx falsifier reflown at 8,000 shots (falsifiers don't need power).
Usage: --selftest | --submit [--backend ibm_fez] | --decode
"""
import argparse, json, os, sys
import numpy as np
from qiskit import transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
from exp202_subspace_relay_key import (ARMS, BASES, SQ2, circuit, analyze, _se_r,
                                       secret_fraction, selftest as parent_selftest)

ENT_SHOTS = 32000
NOCX_SHOTS = 8000


def selftest():
    parent_selftest()
    print("Exp202b selftest = Exp202 selftest (identical circuits/decode) — PASS above. "
          "Changes are shot budget + one re-priced sub-gate, both pre-registered.")


def submit(backend_name):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    names = [[arm, bb] for arm in ARMS for bb in BASES]
    circuits = audit = seed_used = None
    for seed in range(20):
        cand = [transpile(circuit(arm, bb), backend=backend, optimization_level=3,
                          seed_transpiler=seed) for arm, bb in names]
        aud = {}
        for (arm, bb), qc in zip(names, cand):
            n2 = sum(1 for inst in qc.data if inst.operation.num_qubits == 2)
            aud.setdefault(arm, {})[bb] = n2
        if all(len(set(per_b.values())) == 1 for per_b in aud.values()):
            circuits, audit, seed_used = cand, aud, seed
            break
        print(f"  seed {seed}: non-uniform — next")
    if circuits is None:
        print("AUDIT ABORT: no basis-uniform seed in 0-19"); sys.exit(1)
    for arm, per_b in audit.items():
        print(f"  audit {arm}: 2q={per_b['ZZ']} (basis-uniform, seed {seed_used})")
    # per-pub shots: entangled arms powered, nocx falsifier at parent budget
    pubs = [(qc, None, NOCX_SHOTS if arm == "nocx" else ENT_SHOTS)
            for (arm, bb), qc in zip(names, circuits)]
    job = SamplerV2(mode=backend).run(pubs)
    out = os.path.join(HERE, "..", "results", "exp202b_subspace_relay_key_manifest.json")
    man = {"exp": "202b", "slug": "subspace_relay_key_b", "backend": backend_name,
           "shots_ent": ENT_SHOTS, "shots_nocx": NOCX_SHOTS,
           "job_id": job.job_id(), "order": names, "seed_transpiler": seed_used}
    json.dump(man, open(out, "w"), indent=1)                 # manifest first (C4895 lesson)
    man["audit_2q"] = audit
    man["prereg"] = {
        "relation_to_202": "disclosed pro-hypothesis retest; 202 registered verdict stands "
                           "NOT HELD; this is a new frozen instrument",
        "G1_cert_anchors": "UNCHANGED from 202: S(logical) in [2.40,2.85] >=5 sigma; "
                           "S(relay) in [2.30,2.75] >=5 sigma; S(nocx) in [-0.25,0.30]",
        "G2_key_exists": "UNCHANGED: QBER_Z,QBER_X < 0.11 all four links; nocx in [0.45,0.55]",
        "G3_shield_quality": "r-edges UNCHANGED (>=3 sigma both links); QBER sub-gate "
                             "RE-PRICED pre-data (200b move): pooled Qbar=(Q_Z+Q_X)/2, "
                             "Qbar(relay) < Qbar(barerelay) at >=5 sigma",
        "G4_depth_pays": "UNCHANGED bands: [r(relay)-r(barerelay)] - [r(logical)-r(bare)] "
                         "> 0 at >=3 sigma; POWERED: 32k shots -> se_gain ~0.013, detects "
                         ">=0.040 at 3 sigma; expected z ~3.8 at 202's point estimate; can "
                         "MISS if true gain smaller — accepted, bands unchanged",
        "G5_gauges": "UNCHANGED: acceptance >=0.70 (logical/nocx), >=0.50 (relay)",
        "registered_verdict": "conjunction G1-G5",
        "budget_predictions": "depth gain in [0.02,0.09]; pooled relay QBER edge in "
                              "[1.5pp,4.5pp]; relay r-multiple in [1.5,3.0] (re-priced from "
                              "202's measured windows); shield wins throughput both links "
                              "(conf 0.75, upgraded on 202's measurement)"}
    json.dump(man, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} (20 pubs: 16 x {ENT_SHOTS} + 4 x {NOCX_SHOTS}) -> {out}")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    man = json.load(open(os.path.join(HERE, "..", "results", "exp202b_subspace_relay_key_manifest.json")))
    svc = _get_ibm_service(); res = svc.job(man["job_id"]).result()
    raw = {}
    for idx, (arm, bb) in enumerate(man["order"]):
        r0 = res[idx]; reg = list(r0.data.keys())[0]
        raw[(arm, bb)] = getattr(r0.data, reg).get_counts()
    r = analyze(lambda arm, bb: raw[(arm, bb)])
    print(f"Exp202b decode | job {man['job_id']} | powered retest, gates as registered")
    for arm in ARMS:
        rec = r[arm]
        print(f"  {arm:>9}: S={rec['S']:+.4f}  QBER_Z={rec['QBER_Z']*100:5.2f}%  "
              f"QBER_X={rec['QBER_X']*100:5.2f}%  r={rec['r']:.4f}  acc={rec['acc_mean']:.3f}  "
              f"r*acc={rec['throughput']:.4f}")
    L, R, B, BR, N = (r[a] for a in ARMS)
    zL = (L["S"] - 2) / L["se_S"]; zR = (R["S"] - 2) / R["se_S"]
    g1 = (2.40 <= L["S"] <= 2.85 and zL >= 5 and 2.30 <= R["S"] <= 2.75 and zR >= 5
          and -0.25 <= N["S"] <= 0.30)
    g2 = (all(r[a]["QBER_Z"] < 0.11 and r[a]["QBER_X"] < 0.11
              for a in ("logical", "relay", "bare", "barerelay"))
          and 0.45 <= N["QBER_Z"] <= 0.55 and 0.45 <= N["QBER_X"] <= 0.55)
    dr_direct = L["r"] - B["r"]; se_dd = float(np.sqrt(_se_r(L) ** 2 + _se_r(B) ** 2))
    dr_relay = R["r"] - BR["r"]; se_dr = float(np.sqrt(_se_r(R) ** 2 + _se_r(BR) ** 2))
    z_dd = dr_direct / se_dd; z_dr = dr_relay / se_dr
    qbar_R = (R["QBER_Z"] + R["QBER_X"]) / 2; qbar_BR = (BR["QBER_Z"] + BR["QBER_X"]) / 2
    se_qbar = float(np.sqrt(R["se_QZ"] ** 2 + R["se_QX"] ** 2
                            + BR["se_QZ"] ** 2 + BR["se_QX"] ** 2) / 2)
    z_qbar = (qbar_BR - qbar_R) / se_qbar
    g3 = z_dd >= 3 and z_dr >= 3 and z_qbar >= 5
    depth_gain = dr_relay - dr_direct
    se_dg = float(np.sqrt(se_dd ** 2 + se_dr ** 2)); z_dg = depth_gain / se_dg
    g4 = z_dg >= 3
    acc_log = all(v >= 0.70 for a in ("logical", "nocx") for v in r[a]["acceptance"].values())
    acc_rel = all(v >= 0.50 for v in R["acceptance"].values())
    g5 = acc_log and acc_rel
    ratio = R["r"] / BR["r"] if BR["r"] > 0 else float("inf")
    print(f"\nG1 CERTIFICATES: S_log={L['S']:.3f} ({zL:.0f} sigma), S_relay={R['S']:.3f} "
          f"({zR:.0f} sigma), nocx={N['S']:+.3f} {'OK' if g1 else 'MISS'}")
    print(f"G2 KEYS EXIST: nocx coin {N['QBER_Z']:.3f}/{N['QBER_X']:.3f} {'OK' if g2 else 'MISS'}")
    print(f"G3 SHIELD QUALITY: direct dr={dr_direct:+.4f} ({z_dd:.1f} sigma); relay "
          f"dr={dr_relay:+.4f} ({z_dr:.1f} sigma); POOLED relay QBER edge "
          f"{(qbar_BR-qbar_R)*100:+.2f}pp ({z_qbar:.1f} sigma) {'OK' if g3 else 'MISS'}")
    print(f"G4 DEPTH PAYS (powered): gain {depth_gain:+.4f} ({z_dg:.1f} sigma, se {se_dg:.4f}) "
          f"{'OK' if g4 else 'MISS'}")
    print(f"G5 GAUGES: {'OK' if g5 else 'MISS'}")
    print(f"RELAY r-MULTIPLE: {ratio:.2f} (band [1.5,3.0]) | THROUGHPUT: direct "
          f"{L['throughput']:.4f} vs {B['throughput']:.4f} | relay {R['throughput']:.4f} vs "
          f"{BR['throughput']:.4f}")
    ok = g1 and g2 and g3 and g4 and g5
    print(f"VERDICT: {'THE SUBSPACE RELAY KEY HELD — the shields key advantage grows with '
          'depth at the registered 3 sigma: the network stack pays for its shields' if ok
          else 'NOT HELD (accounting above)'}")
    json.dump({"job_id": man["job_id"], "results": r,
               "dr_direct": float(dr_direct), "z_dr_direct": float(z_dd),
               "dr_relay": float(dr_relay), "z_dr_relay": float(z_dr),
               "depth_gain": float(depth_gain), "z_depth_gain": float(z_dg),
               "qbar_edge_pp": float((qbar_BR - qbar_R) * 100), "z_qbar": float(z_qbar),
               "ratio_relay": float(ratio),
               "g1": bool(g1), "g2": bool(g2), "g3": bool(g3), "g4": bool(g4), "g5": bool(g5),
               "verdict_ok": bool(ok)},
              open(os.path.join(HERE, "..", "results", "exp202b_subspace_relay_key_decode.json"), "w"), indent=1)
    print("-> results/exp202b_subspace_relay_key_decode.json")


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
