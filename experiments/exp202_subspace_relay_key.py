#!/usr/bin/env python3
"""Exp202 — THE SUBSPACE RELAY KEY: logical E91 between [[4,2,2]] shields. C4896.

Horizons-4 Invention 1, flight 1 (docs/star-trek-horizons-4-the-starship-whisper-c4894.md),
flown on Creator go. The network stack's key layer, run at the LOGICAL level: an
entanglement-based E91/BBM92 key between two error-detecting shields — direct, and through
an UNTRUSTED relay shield (197's Federation weld: A and C never interact; the key rides on
the relay's two classical bits).

THE LINEARITY DUALITY (the design's spine): at the logical level the key bases Zbar-Zbar and
Xbar-Xbar are TRANSVERSAL, and 196's CHSH-by-linearity uses exactly those plus the mixed
pairs. So the SAME four basis measurements are simultaneously
    * the key generator:  QBER_Z = (1 - ZZ_corr)/2,  QBER_X = (1 - XX_corr)/2
    * the certificate:    S = sqrt2*(ZZ_corr + XX_corr), mixed correlators = nulls.
The key and its quantum certificate are one dataset — nothing is measured twice.

Secret fraction (asymptotic BBM92, one-way EC bound): r = max(0, 1 - h2(Q_Z) - h2(Q_X)).
Throughput column: secret bits per RAW pair = r x acceptance (shields pay the postselection
toll; bare pairs pay none). Both columns reported — the shield trades throughput for quality
and the depth-trend of that trade is gated (G4), not assumed.

THE INVENTION THESIS UNDER TEST (191->196->197 measured trend: shield advantage grows with
depth): at relay depth, the binary-entropy nonlinearity should AMPLIFY 197's +0.24 CHSH edge
into a multiple on the secret fraction — priced pre-flight at r_relay/r_barerelay in
[1.8, 5.0] from the parents' certified correlators.

Arms (4 basis pairs ZZ/ZX/XZ/XX each; parent circuits verbatim, credited):
  logical    2 shields, tCNOT weld               (Exp196 'logical', 8q)
  relay      3 shields, untrusted middle         (Exp197 'federation', 12q)
  bare       2 physical qubits, direct           (Exp196 'bare')
  barerelay  4 physical qubits, physical swap    (Exp197 'bare')
  nocx       2 shields, NO weld — executed null  (Exp196 'nocx'): no entanglement -> the
             "key" is a coin (QBER ~ 0.5) and S ~ 0. Without the weld there is no secret.

SCOPE (F115 trust-ladder discipline, stated plainly): TRUSTED-DEVICE entanglement-based key.
The CHSH value is the in-protocol quantum-health certificate (tier-2), NOT device-independent
— no-signaling is unenforceable on one chip and the DI number would evaporate (F115). Raw
sifted bits + asymptotic secret fraction; deterministic per-circuit settings (no per-shot
QRNG basis choice — sifting fraction excluded from accounting); no EC/PA/authentication
(Exp180 scope). Expectation-value correlators, logical-level fair sampling via stabilizer
postselection (196/197 scope).

BUDGET CHECK (C4887 rule): key thresholds need lambda ~ 0.79 (QBER<0.11 <=> corr>0.78);
parents measured 0.98 (196 direct) and 0.92 (197 relay). Ample.
Usage: --selftest | --submit [--backend ibm_fez --shots 8000] | --decode
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

ARMS = ("logical", "relay", "bare", "barerelay", "nocx")
BASES = ("ZZ", "ZX", "XZ", "XX")
SQ2 = float(np.sqrt(2))


def h2(q):
    q = min(max(float(q), 1e-12), 1 - 1e-12)
    return float(-q * np.log2(q) - (1 - q) * np.log2(1 - q))


def secret_fraction(qz, qx):
    return float(max(0.0, 1.0 - h2(qz) - h2(qx)))


# ---------- circuits: parents verbatim (196: logical/nocx/bare; 197: federation/bare) ----------

def _prep_plus0(qc, q):
    qc.h(q); qc.cx(q, q + 1); qc.h(q + 2); qc.cx(q + 2, q + 3)


def _prep_00(qc, q):
    qc.h(q); qc.cx(q, q + 1); qc.cx(q, q + 2); qc.cx(q, q + 3)


def circuit(arm, bb):
    bA, bB = bb[0], bb[1]
    if arm == "bare":                                       # Exp196 bare
        qc = QuantumCircuit(2, 2)
        qc.h(0); qc.cx(0, 1)
        qc.barrier()
        if bA == "X": qc.h(0)
        if bB == "X": qc.h(1)
        qc.measure(0, 0); qc.measure(1, 1)
        return qc
    if arm == "barerelay":                                  # Exp197 bare (physical swap)
        qc = QuantumCircuit(4, 4)
        qc.h(0); qc.cx(0, 1)
        qc.h(2); qc.cx(2, 3)
        qc.barrier()
        qc.cx(1, 2); qc.h(1)
        qc.barrier()
        if bA == "X": qc.h(0)
        if bB == "X": qc.h(3)
        for q in range(4): qc.measure(q, q)
        return qc
    if arm == "relay":                                      # Exp197 federation
        qc = QuantumCircuit(12, 12)
        _prep_plus0(qc, 0)
        _prep_00(qc, 4)
        _prep_plus0(qc, 8)
        qc.barrier()
        for i in range(4): qc.cx(0 + i, 4 + i)              # tCNOT A->B straight
        perm = {0: 0, 1: 2, 2: 1, 3: 3}
        for i in range(4): qc.cx(8 + i, 4 + perm[i])        # tCNOT C->B permuted (automorphism)
        qc.barrier()
        qc.cx(5, 6); qc.h(5)                                # relay logical-Bell = physical Bell
        qc.h(4); qc.h(7)                                    # relay X-stabilizer check
        qc.barrier()
        if bA == "X":
            for q in range(4): qc.h(q)
        if bB == "X":
            for q in range(8, 12): qc.h(q)
        for q in range(12): qc.measure(q, q)
        return qc
    qc = QuantumCircuit(8, 8)                               # Exp196 logical / nocx
    qc.h(0); qc.cx(0, 1)
    qc.h(2); qc.cx(2, 3)
    _prep_00(qc, 4)
    qc.barrier()
    if arm != "nocx":
        for i in range(4): qc.cx(i, i + 4)                  # transversal logical CNOT
    qc.barrier()
    if bA == "X":
        for q in range(4): qc.h(q)
    if bB == "X":
        for q in range(4, 8): qc.h(q)
    for q in range(8): qc.measure(q, q)
    return qc


# ---------- stats: parents' postselection + corrections, returning corr/acceptance ----------

def _stats(counts, bb, arm):
    bA, bB = bb[0], bb[1]
    if arm == "bare":
        acc = c = 0
        for s, n in counts.items():
            b = s.replace(" ", "")
            acc += n; c += n * (1 - 2 * (int(b[-1]) ^ int(b[-2])))
        return {"acceptance": 1.0, "corr": c / acc, "n_acc": acc}
    if arm == "barerelay":
        acc = c = 0
        for s, n in counts.items():
            b = s.replace(" ", "")
            v = [int(b[-1 - i]) for i in range(4)]
            sgn = 1
            if bA == "Z" and bB == "Z" and v[2]: sgn = -1    # m_z corrects ZZ
            if bA == "X" and bB == "X" and v[1]: sgn = -1    # m_x corrects XX
            acc += n; c += n * sgn * (1 - 2 * (v[0] ^ v[3]))
        return {"acceptance": 1.0, "corr": c / acc, "n_acc": acc}
    if arm == "relay":
        accepted = rej = 0; c1 = 0
        for s, n in counts.items():
            b = s.replace(" ", "")
            v = [int(b[-1 - i]) for i in range(12)]
            pA = v[0] ^ v[1] ^ v[2] ^ v[3]
            pC = v[8] ^ v[9] ^ v[10] ^ v[11]
            pB = v[4] ^ v[5] ^ v[7]
            if pA or pC or pB:
                rej += n; continue
            accepted += n
            a1 = (v[0] ^ v[2]) if bA == "Z" else (v[0] ^ v[1])
            c1b = (v[8] ^ v[10]) if bB == "Z" else (v[8] ^ v[9])
            sgn = 1
            if bA == "Z" and bB == "Z" and v[6]: sgn = -1    # m_z = q6
            if bA == "X" and bB == "X" and v[5]: sgn = -1    # m_x = q5
            c1 += n * sgn * (1 - 2 * (a1 ^ c1b))
        return {"acceptance": accepted / (accepted + rej),
                "corr": c1 / accepted if accepted else 0.0, "n_acc": accepted}
    accepted = rej = 0; c1 = 0                               # logical / nocx (196)
    for s, n in counts.items():
        b = s.replace(" ", "")
        v = [int(b[-1 - i]) for i in range(8)]
        pA = v[0] ^ v[1] ^ v[2] ^ v[3]; pB = v[4] ^ v[5] ^ v[6] ^ v[7]
        if pA or pB:
            rej += n; continue
        accepted += n
        a1 = (v[0] ^ v[2]) if bA == "Z" else (v[0] ^ v[1])
        b1 = (v[4] ^ v[6]) if bB == "Z" else (v[4] ^ v[5])
        c1 += n * (1 - 2 * (a1 ^ b1))
    return {"acceptance": accepted / (accepted + rej),
            "corr": c1 / accepted if accepted else 0.0, "n_acc": accepted}


def analyze(get):
    r = {}
    for arm in ARMS:
        st = {bb: _stats(get(arm, bb), bb, arm) for bb in BASES}
        zz, xx = st["ZZ"]["corr"], st["XX"]["corr"]
        qz, qx = (1 - zz) / 2, (1 - xx) / 2
        S = SQ2 * (zz + xx)
        se_c = {bb: float(np.sqrt(max(1 - st[bb]["corr"] ** 2, 1e-9) / max(st[bb]["n_acc"], 1)))
                for bb in BASES}
        acc = float(np.mean([st[bb]["acceptance"] for bb in BASES]))
        rsec = secret_fraction(qz, qx)
        r[arm] = {"corr": {bb: float(st[bb]["corr"]) for bb in BASES},
                  "se": se_c,
                  "n_acc": {bb: int(st[bb]["n_acc"]) for bb in BASES},
                  "acceptance": {bb: float(st[bb]["acceptance"]) for bb in BASES},
                  "S": float(S), "se_S": float(SQ2 * np.sqrt(se_c["ZZ"] ** 2 + se_c["XX"] ** 2)),
                  "QBER_Z": float(qz), "QBER_X": float(qx),
                  "se_QZ": se_c["ZZ"] / 2, "se_QX": se_c["XX"] / 2,
                  "r": rsec, "acc_mean": acc, "throughput": float(rsec * acc)}
    return r


def _se_r(rec):
    """SE of the secret fraction by the delta method: dr/dQ = -h2'(Q) = -log2((1-Q)/Q)."""
    tot = 0.0
    for q, se in ((rec["QBER_Z"], rec["se_QZ"]), (rec["QBER_X"], rec["se_QX"])):
        qc = min(max(q, 1e-6), 0.5 - 1e-6)
        tot += (np.log2((1 - qc) / qc) * se) ** 2
    return float(np.sqrt(tot))


def selftest():
    from qiskit_aer import AerSimulator
    sim = AerSimulator(); shots = 20000; cache = {}
    def get(arm, bb):
        k = (arm, bb)
        if k not in cache:
            cache[k] = sim.run(circuit(arm, bb), shots=shots).result().get_counts()
        return cache[k]
    r = analyze(get)
    print("Exp202 selftest (noiseless Aer) | ideal: S=2.828, QBER=0, r=1 (entangled); "
          "nocx QBER=0.5, r=0")
    for arm in ARMS:
        print(f"  {arm:>9}: S={r[arm]['S']:+.3f}  QBER_Z={r[arm]['QBER_Z']:.3f} "
              f"QBER_X={r[arm]['QBER_X']:.3f}  r={r[arm]['r']:.3f}  acc={r[arm]['acc_mean']:.3f}")
    for arm in ("logical", "relay", "bare", "barerelay"):
        assert abs(r[arm]["S"] - 2 * SQ2) < 0.05, f"{arm} must hit Tsirelson noiselessly"
        assert r[arm]["QBER_Z"] < 0.01 and r[arm]["QBER_X"] < 0.01, f"{arm} key must be clean"
        assert r[arm]["r"] > 0.9, f"{arm} secret fraction must be ~1"
    assert abs(r["nocx"]["S"]) < 0.06, "nocx certificate must be dead"
    assert abs(r["nocx"]["QBER_Z"] - 0.5) < 0.03 and abs(r["nocx"]["QBER_X"] - 0.5) < 0.03, \
        "nocx key must be a coin"
    assert r["nocx"]["r"] == 0.0, "nocx secret fraction must be zero"
    print("SELFTEST PASS: all four entangled links deliver clean keys at Tsirelson-certificate; "
          "the unwelded arm's key is a coin with a dead certificate. Cleared to fly.")


def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    names, circuits = [], []
    for arm in ARMS:
        for bb in BASES:
            names.append([arm, bb])
            circuits.append(transpile(circuit(arm, bb), backend=backend, optimization_level=3))
    # skeleton audit: bases differ only by 1q H layers -> per-arm 2q counts must be basis-uniform
    audit = {}
    for (arm, bb), qc in zip(names, circuits):
        n2 = sum(1 for inst in qc.data if inst.operation.num_qubits == 2)
        audit.setdefault(arm, {})[bb] = n2
    for arm, per_b in audit.items():
        if len(set(per_b.values())) != 1:
            print(f"AUDIT ABORT: arm {arm} 2q counts vary across bases: {per_b}"); sys.exit(1)
        print(f"  audit {arm}: 2q={per_b['ZZ']} (basis-uniform)")
    job = SamplerV2(mode=backend).run(circuits, shots=shots)
    out = os.path.join(HERE, "..", "results", "exp202_subspace_relay_key_manifest.json")
    man = {"exp": 202, "slug": "subspace_relay_key", "backend": backend_name, "shots": shots,
           "job_id": job.job_id(), "order": names}
    json.dump(man, open(out, "w"), indent=1)                # C4895 lesson: manifest FIRST,
    man["audit_2q"] = audit                                 # derived fields after
    man["prereg"] = {
        "G1_cert_anchors": "S(logical) in [2.40,2.85] & >2 at >=5 sigma (196 band); S(relay) "
                           "in [2.30,2.75] & >2 at >=5 sigma (197 measured 2.6046); "
                           "S(nocx) in [-0.25,0.30]",
        "G2_key_exists": "QBER_Z and QBER_X < 0.11 in logical, relay, bare, barerelay; "
                         "nocx QBER_Z and QBER_X in [0.45,0.55] (executed no-entanglement "
                         "null: no weld, no secret)",
        "G3_shield_quality": "r(logical) > r(bare) at >=3 sigma AND r(relay) > r(barerelay) "
                             "at >=3 sigma (delta-method SE); QBER_Z(relay) < "
                             "QBER_Z(barerelay) at >=5 sigma",
        "G4_depth_pays": "[r(relay)-r(barerelay)] > [r(logical)-r(bare)] at >=3 sigma — the "
                         "shield's key advantage GROWS with depth (the invention thesis; "
                         "a miss is a finding against Invention 1, kept)",
        "G5_gauges": "acceptance >= 0.70 every basis (logical/nocx, 196 gate); >= 0.50 every "
                     "basis (relay, 12q/3-block); throughput column reported both links "
                     "(reported, not gated — the honest toll)",
        "registered_verdict": "conjunction G1-G5",
        "budget_predictions": "QBER_Z(logical) in [0.005,0.025]; QBER_Z(relay) in "
                              "[0.025,0.060]; r(relay)/r(barerelay) in [1.8,5.0]; crossover "
                              "pattern (conf 0.6): bare wins throughput on the direct link, "
                              "logical wins throughput on the relay link",
        "scope": "trusted-device BBM92; CHSH = tier-2 health certificate NOT DI (F115); raw "
                 "sifted + asymptotic r; no EC/PA/auth; deterministic settings"}
    json.dump(man, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits, {shots} shots) -> {out}")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    man = json.load(open(os.path.join(HERE, "..", "results", "exp202_subspace_relay_key_manifest.json")))
    svc = _get_ibm_service(); res = svc.job(man["job_id"]).result()
    raw = {}
    for idx, (arm, bb) in enumerate(man["order"]):
        r0 = res[idx]; reg = list(r0.data.keys())[0]
        raw[(arm, bb)] = getattr(r0.data, reg).get_counts()
    r = analyze(lambda arm, bb: raw[(arm, bb)])
    print(f"Exp202 THE SUBSPACE RELAY KEY decode | job {man['job_id']} | "
          f"abort threshold QBER 0.11 | classical S bound 2")
    for arm in ARMS:
        rec = r[arm]
        print(f"  {arm:>9}: S={rec['S']:+.4f} (se {rec['se_S']:.3f})  "
              f"QBER_Z={rec['QBER_Z']*100:5.2f}%  QBER_X={rec['QBER_X']*100:5.2f}%  "
              f"r={rec['r']:.4f}  acc={rec['acc_mean']:.3f}  r*acc={rec['throughput']:.4f}")
    L, R, B, BR, N = (r[a] for a in ARMS)
    # G1
    zL = (L["S"] - 2) / L["se_S"]; zR = (R["S"] - 2) / R["se_S"]
    g1 = (2.40 <= L["S"] <= 2.85 and zL >= 5 and 2.30 <= R["S"] <= 2.75 and zR >= 5
          and -0.25 <= N["S"] <= 0.30)
    # G2
    g2 = (all(r[a]["QBER_Z"] < 0.11 and r[a]["QBER_X"] < 0.11
              for a in ("logical", "relay", "bare", "barerelay"))
          and 0.45 <= N["QBER_Z"] <= 0.55 and 0.45 <= N["QBER_X"] <= 0.55)
    # G3
    dr_direct = L["r"] - B["r"]; se_dd = float(np.sqrt(_se_r(L) ** 2 + _se_r(B) ** 2))
    dr_relay = R["r"] - BR["r"]; se_dr = float(np.sqrt(_se_r(R) ** 2 + _se_r(BR) ** 2))
    z_dd = dr_direct / se_dd; z_dr = dr_relay / se_dr
    dq = BR["QBER_Z"] - R["QBER_Z"]
    z_dq = dq / float(np.sqrt(R["se_QZ"] ** 2 + BR["se_QZ"] ** 2))
    g3 = z_dd >= 3 and z_dr >= 3 and z_dq >= 5
    # G4
    depth_gain = dr_relay - dr_direct
    se_dg = float(np.sqrt(se_dd ** 2 + se_dr ** 2))
    z_dg = depth_gain / se_dg
    g4 = z_dg >= 3
    # G5
    acc_log = all(v >= 0.70 for a in ("logical", "nocx") for v in r[a]["acceptance"].values())
    acc_rel = all(v >= 0.50 for v in R["acceptance"].values())
    g5 = acc_log and acc_rel
    ratio = R["r"] / BR["r"] if BR["r"] > 0 else float("inf")
    print(f"\nG1 CERTIFICATES: S_log={L['S']:.3f} ({zL:.0f} sigma), S_relay={R['S']:.3f} "
          f"({zR:.0f} sigma), nocx={N['S']:+.3f} {'OK' if g1 else 'MISS'}")
    print(f"G2 KEYS EXIST: all links under abort threshold; nocx coin "
          f"{N['QBER_Z']:.3f}/{N['QBER_X']:.3f} {'OK' if g2 else 'MISS'}")
    print(f"G3 SHIELD QUALITY: direct dr={dr_direct:+.4f} ({z_dd:.1f} sigma); relay "
          f"dr={dr_relay:+.4f} ({z_dr:.1f} sigma); relay QBER edge {dq*100:+.2f}pp "
          f"({z_dq:.1f} sigma) {'OK' if g3 else 'MISS'}")
    print(f"G4 DEPTH PAYS: advantage grows {dr_direct:+.4f} -> {dr_relay:+.4f} "
          f"(gain {depth_gain:+.4f}, {z_dg:.1f} sigma) {'OK' if g4 else 'MISS'}")
    print(f"G5 GAUGES: logical acc >=0.70 {acc_log}; relay acc >=0.50 {acc_rel} "
          f"{'OK' if g5 else 'MISS'}")
    print(f"SECRET-FRACTION MULTIPLE (relay link): r_shielded/r_bare = {ratio:.2f} "
          f"(budget band [1.8, 5.0])")
    print(f"THROUGHPUT (r*acc, the honest toll): direct {L['throughput']:.4f} shielded vs "
          f"{B['throughput']:.4f} bare | relay {R['throughput']:.4f} shielded vs "
          f"{BR['throughput']:.4f} bare")
    ok = g1 and g2 and g3 and g4 and g5
    print(f"VERDICT: {'THE SUBSPACE RELAY KEY — a physics-certified logical key, direct and '
          'through an untrusted relay shield, with the shields key advantage growing with '
          'depth: the network stack pays for its shields' if ok
          else 'NOT HELD (accounting above)'}")
    json.dump({"job_id": man["job_id"], "results": r,
               "dr_direct": float(dr_direct), "z_dr_direct": float(z_dd),
               "dr_relay": float(dr_relay), "z_dr_relay": float(z_dr),
               "depth_gain": float(depth_gain), "z_depth_gain": float(z_dg),
               "ratio_relay": float(ratio),
               "g1": bool(g1), "g2": bool(g2), "g3": bool(g3), "g4": bool(g4), "g5": bool(g5),
               "verdict_ok": bool(ok)},
              open(os.path.join(HERE, "..", "results", "exp202_subspace_relay_key_decode.json"), "w"), indent=1)
    print("-> results/exp202_subspace_relay_key_decode.json")


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
