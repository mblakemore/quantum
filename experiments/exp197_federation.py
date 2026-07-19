#!/usr/bin/env python3
"""Exp197 — THE FEDERATION: logical entanglement swapping between three [[4,2,2]] shields. C4889.

Three ships: A (q0-3), relay B (q4-7), C (q8-11). A and C NEVER interact — no gate touches
both. Protocol (all-transversal, all-terminal, corrections in software — Exp192 style):
  1. A=|+bar 0bar>, B=|0bar 0bar>, C=|+bar 0bar>
  2. Transversal CNOT A->B (straight wiring)  -> Bell(L1A, L1B)
  3. Transversal CNOT C->B (PERMUTED wiring, B-side q1<->q2) -> Bell(L1C, L2B).
     SWAP(q1,q2) is a [[4,2,2]] automorphism implementing logical SWAP(L1,L2), so the
     permuted transversal CNOT is CNOT(L1C->L2B) with ZERO extra gates.
  4. Logical Bell measurement on (L1B, L2B): X1bar X2bar = X5X6, Z1bar Z2bar = Z5Z6 — the
     in-block logical Bell basis is a PHYSICAL Bell basis on the relay's middle qubits.
     cx(5,6), h(5), terminal measure: m_x = q5, m_z = q6. Relay X-stabilizer check via
     q4,q7 measured in X: postselect x4^x7^x5parity (XXXX_B eigenvalue +1).
  5. Frame algebra (stabilizer product): XbarA XbarC = (XbarA XbarB1)(XbarC XbarB2) M_x,
     so corrected XX multiplies by sign(m_x); ZZ by sign(m_z). A-C collapse to a Bell pair
     determined by the relay's TWO CLASSICAL BITS.
  6. Certify A-C with Exp196's CHSH machinery: 4 logical basis pairs, settings by linearity,
     S = sqrt2*(ZZ_corr + XX_corr), mixed correlators = preregistered nulls.

In-shot control: L2A-L2C (both |0bar>, never entangled) ride the same shots -> CHSH sqrt2.
In-decode falsifier (free): decode the SAME federation data with the relay bits IGNORED ->
S must die to ~0. The weld lives in two classical bits.
Hardware falsifier: norelay arm (B measured straight in Z, no Bell rotation) -> S ~ 0.
Reference: bare 4-qubit physical swap, same frame algebra.

BUDGET CHECK (C4887 rule): lambda_req = 0.707 for S>2; Exp191/196 measured ~0.985 per
postselected end-correlator x ~0.93 relay-bit conditioning -> predicted S ~ 2.4-2.6. Feasible.

SCOPE: expectation-value CHSH (as Exp196 — no loophole closure, logical-level fair sampling);
relay block gets X-stabilizer check only in the federation arm (Z-check spent by the Bell
readout — partial shield on the relay, stated).

Usage: --selftest | --submit [--backend ibm_fez --shots 8000] | --decode
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

ARMS = ("federation", "norelay", "bare")
BASES = ("ZZ", "ZX", "XZ", "XX")   # (end A basis, end C basis)
SQ2 = float(np.sqrt(2))


def _prep_plus0(qc, q):   # |+bar 0bar> on block starting at q: Bell(q,q+1) (x) Bell(q+2,q+3)
    qc.h(q); qc.cx(q, q + 1); qc.h(q + 2); qc.cx(q + 2, q + 3)


def _prep_00(qc, q):      # |0bar 0bar> = GHZ4
    qc.h(q); qc.cx(q, q + 1); qc.cx(q, q + 2); qc.cx(q, q + 3)


def circuit(arm, bb):
    bA, bC = bb[0], bb[1]
    if arm == "bare":
        qc = QuantumCircuit(4, 4)
        qc.h(0); qc.cx(0, 1)          # Bell(A=q0, relay1=q1)
        qc.h(2); qc.cx(2, 3)          # Bell(relay2=q2, C=q3)
        qc.barrier()
        qc.cx(1, 2); qc.h(1)          # physical Bell measurement on relay pair
        qc.barrier()
        if bA == "X": qc.h(0)
        if bC == "X": qc.h(3)
        for q in range(4): qc.measure(q, q)
        return qc
    qc = QuantumCircuit(12, 12)
    _prep_plus0(qc, 0)                # ship A
    _prep_00(qc, 4)                   # relay B
    _prep_plus0(qc, 8)                # ship C
    qc.barrier()
    for i in range(4): qc.cx(0 + i, 4 + i)                 # tCNOT A->B straight
    perm = {0: 0, 1: 2, 2: 1, 3: 3}                        # B-side q1<->q2
    for i in range(4): qc.cx(8 + i, 4 + perm[i])           # tCNOT C->B permuted
    qc.barrier()
    if arm == "federation":
        qc.cx(5, 6); qc.h(5)          # in-block logical Bell basis = physical Bell on q5,q6
        qc.h(4); qc.h(7)              # relay X-stabilizer check qubits
    # norelay: B measured straight in Z (no Bell rotation; ZZZZ check available)
    qc.barrier()
    if bA == "X":
        for q in range(4): qc.h(q)
    if bC == "X":
        for q in range(8, 12): qc.h(q)
    for q in range(12): qc.measure(q, q)
    return qc


def _stats(counts, bb, arm, corrected=True):
    """Postselect ends (per-block parity, own basis) + relay check; corrected L1A-L1C and
    ride-along L2A-L2C correlators. corrected=False ignores relay bits (in-decode falsifier)."""
    bA, bC = bb[0], bb[1]
    if arm == "bare":
        acc = c = 0
        for s, n in counts.items():
            b = s.replace(" ", "")
            v = [int(b[-1 - i]) for i in range(4)]
            sgn = 1
            if corrected:
                if 1 - 2 * v[2] < 0 and bA == "Z" and bC == "Z": sgn = -1   # m_z corrects ZZ
                if 1 - 2 * v[1] < 0 and bA == "X" and bC == "X": sgn = -1   # m_x corrects XX
            acc += n; c += n * sgn * (1 - 2 * (v[0] ^ v[3]))
        return {"acceptance": 1.0, "corr_L1": c / acc, "corr_L2": None, "n_acc": acc}
    accepted = rej = 0; c1 = c2 = 0
    for s, n in counts.items():
        b = s.replace(" ", "")
        v = [int(b[-1 - i]) for i in range(12)]
        pA = v[0] ^ v[1] ^ v[2] ^ v[3]
        pC = v[8] ^ v[9] ^ v[10] ^ v[11]
        pB = v[4] ^ v[5] ^ v[7] if arm == "federation" else v[4] ^ v[5] ^ v[6] ^ v[7]
        if pA or pC or pB:
            rej += n; continue
        accepted += n
        a1 = (v[0] ^ v[2]) if bA == "Z" else (v[0] ^ v[1])     # L1A
        c1b = (v[8] ^ v[10]) if bC == "Z" else (v[8] ^ v[9])   # L1C
        a2 = (v[0] ^ v[1]) if bA == "Z" else (v[0] ^ v[2])     # L2A (ride-along)
        c2b = (v[8] ^ v[9]) if bC == "Z" else (v[8] ^ v[10])   # L2C (ride-along)
        sgn = 1
        if corrected and arm == "federation":
            if bA == "Z" and bC == "Z" and v[6]: sgn = -1      # m_z = q6 corrects ZZ
            if bA == "X" and bC == "X" and v[5]: sgn = -1      # m_x = q5 corrects XX
        c1 += n * sgn * (1 - 2 * (a1 ^ c1b)); c2 += n * (1 - 2 * (a2 ^ c2b))
    return {"acceptance": accepted / (accepted + rej),
            "corr_L1": c1 / accepted if accepted else 0.0,
            "corr_L2": c2 / accepted if accepted else 0.0,
            "n_acc": accepted}


def _chsh(zz, zx, xz, xx):
    return (zz + zx) / SQ2 + (zz - zx) / SQ2 + (xz + xx) / SQ2 - (xz - xx) / SQ2


def analyze(get, corrected=True):
    r = {}
    for arm in ARMS:
        st = {bb: _stats(get(arm, bb), bb, arm, corrected) for bb in BASES}
        rec = {}
        for L in ("L1", "L2"):
            if arm == "bare" and L == "L2": continue
            cs = {bb: st[bb][f"corr_{L}"] for bb in BASES}
            rec[f"corr_{L}"] = {bb: float(cs[bb]) for bb in BASES}
            rec[f"S_{L}"] = float(_chsh(cs["ZZ"], cs["ZX"], cs["XZ"], cs["XX"]))
        rec["acceptance"] = {bb: float(st[bb]["acceptance"]) for bb in BASES}
        rec["n_acc"] = {bb: int(st[bb]["n_acc"]) for bb in BASES}
        r[arm] = rec
    return r


def selftest():
    from qiskit_aer import AerSimulator
    sim = AerSimulator(); shots = 20000; cache = {}
    def get(arm, bb):
        k = (arm, bb)
        if k not in cache:
            cache[k] = sim.run(circuit(arm, bb), shots=shots).result().get_counts()
        return cache[k]
    r = analyze(get)
    runc = analyze(get, corrected=False)
    print("Exp197 selftest (noiseless Aer) | Tsirelson 2.8284, classical 2, product sqrt2=1.4142")
    for arm in ARMS:
        s2 = f"  S_L2={r[arm]['S_L2']:.3f}" if "S_L2" in r[arm] else ""
        print(f"  {arm:>10}: S_L1={r[arm]['S_L1']:+.4f}{s2}  "
              f"corr={ {b: round(v, 3) for b, v in r[arm]['corr_L1'].items()} }")
    print(f"  federation UNCORRECTED (relay bits ignored): S_L1={runc['federation']['S_L1']:+.4f}")
    # per-sector sign pin: corrected ZZ and XX must be +1 in EVERY relay-outcome sector
    for bb, cl, mbit in (("ZZ", 6, "m_z"), ("XX", 5, "m_x")):
        cnt = {0: [0, 0], 1: [0, 0]}
        for s, n in get("federation", bb).items():
            b = s.replace(" ", "")
            v = [int(b[-1 - i]) for i in range(12)]
            if v[0] ^ v[1] ^ v[2] ^ v[3] or v[8] ^ v[9] ^ v[10] ^ v[11] or v[4] ^ v[5] ^ v[7]: continue
            if bb == "ZZ": a, c = v[0] ^ v[2], v[8] ^ v[10]
            else: a, c = v[0] ^ v[1], v[8] ^ v[9]
            cnt[v[cl]][0] += n * (1 - 2 * (a ^ c)); cnt[v[cl]][1] += n
        for m in (0, 1):
            raw = cnt[m][0] / cnt[m][1]; corr = raw * (1 - 2 * m)
            assert abs(corr - 1) < 0.02, f"{bb} sector {mbit}={m}: corrected {corr} != +1"
        print(f"  sector pin {bb}: {mbit}=0 raw {cnt[0][0]/cnt[0][1]:+.3f}, "
              f"{mbit}=1 raw {cnt[1][0]/cnt[1][1]:+.3f} -> corrected +1/+1")
    assert abs(r["federation"]["S_L1"] - 2 * SQ2) < 0.04, "swapped pair must reach Tsirelson"
    assert abs(r["federation"]["S_L2"] - SQ2) < 0.04, "ride-along product pair must sit at sqrt2"
    assert abs(r["federation"]["corr_L1"]["ZX"]) < 0.03 and abs(r["federation"]["corr_L1"]["XZ"]) < 0.03
    assert abs(runc["federation"]["S_L1"]) < 0.05, "relay bits ignored -> S must die"
    assert abs(r["norelay"]["S_L1"]) < 0.05, "no Bell rotation on relay -> S must die"
    assert abs(r["bare"]["S_L1"] - 2 * SQ2) < 0.04, "bare swap must reach Tsirelson"
    print("SELFTEST PASS: A-C (never interacting) reach Tsirelson via the relay's two classical "
          "bits; ignore the bits or skip the Bell rotation and S dies; ride-along product pair "
          "at sqrt2; sector signs pinned. Cleared to fly.")


def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    circuits, order = [], []
    for arm in ARMS:
        for bb in BASES:
            circuits.append(transpile(circuit(arm, bb), backend=backend, optimization_level=3))
            order.append([arm, bb])
    job = SamplerV2(mode=backend).run(circuits, shots=shots)
    man = {"exp": 197, "slug": "federation", "backend": backend_name, "shots": shots,
           "job_id": job.job_id(), "order": order,
           "prereg": {"primary": "S_L1(federation, corrected) > 2 at >=5 sigma; band [2.10, 2.85] "
                                 "(budget-predicted ~2.4-2.6)",
                      "internal_control": "S_L2(federation) in [1.20, 1.48] (ride-along product pair)",
                      "nulls": "|ZX_L1| and |XZ_L1| (federation, corrected) <= 0.15",
                      "falsifier_decode": "S_L1(federation, relay bits IGNORED) in [-0.25, 0.30]",
                      "falsifier_hw": "S_L1(norelay) in [-0.25, 0.30]",
                      "reference": "S_L1(bare swap) descriptive",
                      "gauges": "end-block acceptance >= 0.60; relay X-check acceptance >= 0.70 "
                                "(joint acceptance is the product, expect ~0.55-0.75)",
                      "budget_check": "lambda_req 0.707; predicted end-to-end ~0.85-0.92 (C4887 rule)"}}
    json.dump(man, open(os.path.join(HERE, "..", "results", "exp197_federation_manifest.json"), "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits, {shots} shots)")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    man = json.load(open(os.path.join(HERE, "..", "results", "exp197_federation_manifest.json")))
    svc = _get_ibm_service(); res = svc.job(man["job_id"]).result()
    raw = {}
    for idx, (arm, bb) in enumerate(man["order"]):
        r0 = res[idx]; regs = list(r0.data.keys())
        if len(regs) != 1: raise RuntimeError(f"multi-register result for {arm}_{bb}: {regs}")
        raw[(arm, bb)] = getattr(r0.data, regs[0]).get_counts()
    get = lambda arm, bb: raw[(arm, bb)]
    r = analyze(get); runc = analyze(get, corrected=False)
    def seS(arm):
        nz = max(r[arm]["n_acc"]["ZZ"], 1); nx = max(r[arm]["n_acc"]["XX"], 1)
        return SQ2 * float(np.sqrt(1 / nz + 1 / nx))
    print(f"Exp197 THE FEDERATION decode | job {man['job_id']} | classical 2 | Tsirelson 2.8284")
    for arm in ARMS:
        s2 = f"  S_L2={r[arm]['S_L2']:+.3f}" if "S_L2" in r[arm] else ""
        c = r[arm]["corr_L1"]
        print(f"  {arm:>10}: ZZ={c['ZZ']:+.3f} ZX={c['ZX']:+.3f} XZ={c['XZ']:+.3f} XX={c['XX']:+.3f} "
              f"-> S_L1={r[arm]['S_L1']:+.4f}{s2}")
    sF = r["federation"]["S_L1"]; z = (sF - 2) / seS("federation")
    sU = runc["federation"]["S_L1"]; cF = r["federation"]["corr_L1"]
    p_ok = 2.10 <= sF <= 2.85 and z >= 5
    ctrl_ok = 1.20 <= r["federation"]["S_L2"] <= 1.48
    null_ok = abs(cF["ZX"]) <= 0.15 and abs(cF["XZ"]) <= 0.15
    fd_ok = -0.25 <= sU <= 0.30
    fh_ok = -0.25 <= r["norelay"]["S_L1"] <= 0.30
    acc = r["federation"]["acceptance"]; acc_ok = all(a >= 0.50 for a in acc.values())
    print(f"\nPRIMARY: S(A,C | relay bits) = {sF:.4f} vs classical bound 2 -> {z:.0f} sigma "
          f"{'HELD — SHIPS THAT NEVER MET, CHSH-ENTANGLED' if p_ok else 'NOT HELD'}")
    print(f"IN-DECODE FALSIFIER: same data, relay bits ignored -> S = {sU:+.4f} "
          f"{'(dies — the weld IS the two bits)' if fd_ok else 'CHECK'}")
    print(f"HW FALSIFIER: norelay S = {r['norelay']['S_L1']:+.4f} {'(dies)' if fh_ok else 'CHECK'}")
    print(f"IN-SHOT CONTROL: ride-along product pair S_L2 = {r['federation']['S_L2']:.4f} "
          f"{'(at sqrt2, below the bound)' if ctrl_ok else 'CHECK'}")
    print(f"NULLS: ZX={cF['ZX']:+.3f} XZ={cF['XZ']:+.3f} {'OK' if null_ok else 'CHECK'}")
    print(f"REFERENCE: bare swap S = {r['bare']['S_L1']:.4f} "
          f"(shielded-vs-bare gap {sF - r['bare']['S_L1']:+.4f}, descriptive)")
    print(f"GAUGES: federation acceptance {['%.2f' % acc[b] for b in BASES]}")
    ok = p_ok and ctrl_ok and null_ok and fd_ok and fh_ok and acc_ok
    print(f"VERDICT: {'THE FEDERATION — three shields, two transversal handshakes, one physical Bell measurement on the relay: ships that never met are CHSH-entangled by two classical bits' if ok else 'NOT HELD (accounting above)'}")
    json.dump({"job_id": man["job_id"], "results": r, "uncorrected_S": float(sU),
               "sigma_primary": float(z), "primary_ok": bool(p_ok), "control_ok": bool(ctrl_ok),
               "null_ok": bool(null_ok), "falsifier_decode_ok": bool(fd_ok),
               "falsifier_hw_ok": bool(fh_ok), "acc_ok": bool(acc_ok), "verdict_ok": bool(ok)},
              open(os.path.join(HERE, "..", "results", "exp197_federation_decode.json"), "w"), indent=1)
    print("-> results/exp197_federation_decode.json")


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
