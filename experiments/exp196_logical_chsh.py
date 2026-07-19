#!/usr/bin/env python3
"""Exp196 — THE SHIELDED VERDICT: logical CHSH between two [[4,2,2]] shields. C4888.

Upgrade of Exp191's separable-bound witness (S = ZZ+XX <= 1) to the full CHSH bound:
settings A in {Zbar, Xbar} on block A, B in {(Zbar+Xbar)/sqrt2, (Zbar-Xbar)/sqrt2} on block B,
reconstructed by linearity from the four transversally-measured logical basis pairs
(ZZ, ZX, XZ, XX at the logical level):
  E00=(ZZ+ZX)/sqrt2  E01=(ZZ-ZX)/sqrt2  E10=(XZ+XX)/sqrt2  E11=(XZ-XX)/sqrt2
  S_CHSH = E00+E01+E10-E11 = sqrt2*(ZZ+XX)   [mixed terms cancel exactly -> preregistered NULLS]
Classical bound S<=2 (i.e. ZZ+XX > sqrt2 = 1.414, strictly past Exp191's bound 1);
Tsirelson 2*sqrt2 = 2.828.

SCOPE (stated plainly): expectation-value CHSH — settings reconstructed by linearity, no
locality/detection loophole closed (none ever is on a QPU); fair sampling at the logical level
via stabilizer-parity postselection. The claim is about the shielded logical pair's
correlations, not a loophole-free Bell test.

HARDWARE-BUDGET CHECK (C4887 standing rule, first application): absolute threshold S>2 needs
contrast survival lambda > 0.707; Exp191 measured lambda ~ 0.985 postselected on this fabric.
Margin ~40x the 195b failure's. Feasible.

In-shot control: L2 rides along in a product state — its CHSH must sit at sqrt2 = 1.414,
BELOW the classical bound, in the SAME shots where L1 crosses it.
Arms: logical | nocx (transversal CNOT removed: L1 dead, L2 still at sqrt2) | bare (2 physical
qubits, same 4-basis reconstruction — the unshielded reference).

Usage: --selftest | --submit [--backend ibm_fez --shots 8000] | --decode
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

ARMS = ("logical", "nocx", "bare")
BASES = ("ZZ", "ZX", "XZ", "XX")   # (block A basis, block B basis)
SQ2 = float(np.sqrt(2))


def circuit(arm, bb):
    bA, bB = bb[0], bb[1]
    if arm == "bare":
        qc = QuantumCircuit(2, 2)
        qc.h(0); qc.cx(0, 1)
        qc.barrier()
        if bA == "X": qc.h(0)
        if bB == "X": qc.h(1)
        qc.measure(0, 0); qc.measure(1, 1)
        return qc
    qc = QuantumCircuit(8, 8)
    qc.h(0); qc.cx(0, 1)          # block A: |+bar 0bar> = Bell(0,1) (x) Bell(2,3)
    qc.h(2); qc.cx(2, 3)
    qc.h(4); qc.cx(4, 5); qc.cx(4, 6); qc.cx(4, 7)   # block B: |0bar 0bar> = GHZ4
    qc.barrier()
    if arm != "nocx":
        for i in range(4): qc.cx(i, i + 4)           # TRANSVERSAL logical CNOT
    qc.barrier()
    if bA == "X":
        for q in range(4): qc.h(q)
    if bB == "X":
        for q in range(4, 8): qc.h(q)
    for q in range(8): qc.measure(q, q)
    return qc


def _stats(counts, bb, arm):
    """Per-block stabilizer-parity postselection; logical correlators for L1 and L2.
    Logical readout per block/basis (Exp191 map): block A: Z1=z0^z2, X1=x0^x1, Z2=z0^z1,
    X2=x0^x2; block B: Z1=z4^z6, X1=x4^x5, Z2=z4^z5, X2=x4^x6."""
    bA, bB = bb[0], bb[1]
    if arm == "bare":
        acc = c = 0
        for s, n in counts.items():
            b = s.replace(" ", "")
            acc += n; c += n * (1 - 2 * (int(b[-1]) ^ int(b[-2])))
        return {"acceptance": 1.0, "corr_L1": c / acc, "corr_L2": None, "n_acc": acc}
    accepted = rej = 0; c1 = c2 = 0
    for s, n in counts.items():
        b = s.replace(" ", "")
        v = [int(b[-1 - i]) for i in range(8)]
        pA = v[0] ^ v[1] ^ v[2] ^ v[3]; pB = v[4] ^ v[5] ^ v[6] ^ v[7]
        if pA or pB:
            rej += n; continue
        accepted += n
        a1 = (v[0] ^ v[2]) if bA == "Z" else (v[0] ^ v[1])   # L1 half, block A
        b1 = (v[4] ^ v[6]) if bB == "Z" else (v[4] ^ v[5])   # L1 half, block B
        a2 = (v[0] ^ v[1]) if bA == "Z" else (v[0] ^ v[2])   # L2 half, block A
        b2 = (v[4] ^ v[5]) if bB == "Z" else (v[4] ^ v[6])   # L2 half, block B
        c1 += n * (1 - 2 * (a1 ^ b1)); c2 += n * (1 - 2 * (a2 ^ b2))
    return {"acceptance": accepted / (accepted + rej),
            "corr_L1": c1 / accepted if accepted else 0.0,
            "corr_L2": c2 / accepted if accepted else 0.0,
            "n_acc": accepted}


def _chsh(zz, zx, xz, xx):
    E00 = (zz + zx) / SQ2; E01 = (zz - zx) / SQ2
    E10 = (xz + xx) / SQ2; E11 = (xz - xx) / SQ2
    return E00 + E01 + E10 - E11        # algebraically sqrt2*(zz+xx); mixed terms cancel


def analyze(get):
    r = {}
    for arm in ARMS:
        st = {bb: _stats(get(arm, bb), bb, arm) for bb in BASES}
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
    print("Exp196 selftest (noiseless Aer) | Tsirelson 2.8284, classical 2, product-pair sqrt2=1.4142")
    for arm in ARMS:
        s2 = f"  S_L2={r[arm]['S_L2']:.3f}" if "S_L2" in r[arm] else ""
        print(f"  {arm:>8}: S_L1={r[arm]['S_L1']:.4f}{s2}  corr_L1={ {b: round(v,3) for b,v in r[arm]['corr_L1'].items()} }")
    assert abs(r["logical"]["S_L1"] - 2 * SQ2) < 0.04, "logical L1 must reach Tsirelson"
    assert abs(r["logical"]["S_L2"] - SQ2) < 0.04, "L2 product pair must sit at sqrt2"
    assert abs(r["logical"]["corr_L1"]["ZX"]) < 0.03 and abs(r["logical"]["corr_L1"]["XZ"]) < 0.03, "nulls"
    assert abs(r["nocx"]["S_L1"]) < 0.05 and abs(r["nocx"]["S_L2"] - SQ2) < 0.04, "nocx: L1 dead, L2 sqrt2"
    assert abs(r["bare"]["S_L1"] - 2 * SQ2) < 0.04, "bare must reach Tsirelson"
    print("SELFTEST PASS: logical CHSH hits Tsirelson exactly, mixed-basis nulls are 0, the product "
          "logical pair sits at sqrt2 in the same shots, nocx kills L1 only. Cleared to fly.")


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
    man = {"exp": 196, "slug": "logical_chsh", "backend": backend_name, "shots": shots,
           "job_id": job.job_id(), "order": order,
           "prereg": {"primary": "S_L1(logical) > 2 at >=5 sigma; band [2.40, 2.85] "
                                 "(Exp191 contrast predicts ~2.79; >2.8284 excess flags systematics)",
                      "internal_control": "S_L2(logical) in [1.20, 1.48] (product pair AT sqrt2, "
                                          "BELOW classical bound, same shots)",
                      "nulls": "|ZX_L1| and |XZ_L1| (logical) <= 0.15",
                      "falsifier": "S_L1(nocx) in [-0.25, 0.30] AND S_L2(nocx) in [1.20, 1.48]",
                      "reference": "S_L1(bare) in [2.45, 2.80]",
                      "gauges": "per-basis block-pair acceptance >= 0.70",
                      "budget_check": "lambda_req 0.707 vs Exp191 measured ~0.985 (C4887 rule)"}}
    json.dump(man, open(os.path.join(HERE, "..", "results", "exp196_logical_chsh_manifest.json"), "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits, {shots} shots)")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    man = json.load(open(os.path.join(HERE, "..", "results", "exp196_logical_chsh_manifest.json")))
    svc = _get_ibm_service(); res = svc.job(man["job_id"]).result()
    raw = {}
    for idx, (arm, bb) in enumerate(man["order"]):
        r0 = res[idx]; reg = list(r0.data.keys())[0]
        raw[(arm, bb)] = getattr(r0.data, reg).get_counts()
    r = analyze(lambda arm, bb: raw[(arm, bb)])
    def seS(arm):
        # S = sqrt2*(ZZ+XX); conservative per-correlator SE 1/sqrt(n_acc)
        nz = max(r[arm]["n_acc"]["ZZ"], 1); nx = max(r[arm]["n_acc"]["XX"], 1)
        return SQ2 * float(np.sqrt(1 / nz + 1 / nx))
    print(f"Exp196 THE SHIELDED VERDICT decode | job {man['job_id']} | classical 2 | Tsirelson 2.8284")
    for arm in ARMS:
        s2 = f"  S_L2={r[arm]['S_L2']:+.3f}" if "S_L2" in r[arm] else ""
        c = r[arm]["corr_L1"]
        print(f"  {arm:>8}: ZZ={c['ZZ']:+.3f} ZX={c['ZX']:+.3f} XZ={c['XZ']:+.3f} XX={c['XX']:+.3f} "
              f"-> S_L1={r[arm]['S_L1']:+.4f}{s2}")
    sL = r["logical"]["S_L1"]; z = (sL - 2) / seS("logical")
    cL = r["logical"]["corr_L1"]
    p_ok = 2.40 <= sL <= 2.85 and z >= 5
    ctrl_ok = 1.20 <= r["logical"]["S_L2"] <= 1.48
    null_ok = abs(cL["ZX"]) <= 0.15 and abs(cL["XZ"]) <= 0.15
    f_ok = -0.25 <= r["nocx"]["S_L1"] <= 0.30 and 1.20 <= r["nocx"]["S_L2"] <= 1.48
    ref_ok = 2.45 <= r["bare"]["S_L1"] <= 2.80
    acc_ok = all(a >= 0.70 for a in r["logical"]["acceptance"].values())
    print(f"\nPRIMARY: S_L1(logical) = {sL:.4f} vs classical bound 2 -> {z:.0f} sigma "
          f"{'HELD — THE SHIELDED PAIR VIOLATES CHSH' if p_ok else 'NOT HELD'}")
    print(f"INTERNAL CONTROL: S_L2 = {r['logical']['S_L2']:.4f} (product pair, must sit at sqrt2 "
          f"BELOW the bound, same shots) {'OK' if ctrl_ok else 'CHECK'}")
    print(f"NULLS: ZX={cL['ZX']:+.3f}, XZ={cL['XZ']:+.3f} {'OK' if null_ok else 'CHECK'}")
    print(f"FALSIFIER: nocx S_L1={r['nocx']['S_L1']:+.3f}, S_L2={r['nocx']['S_L2']:.3f} "
          f"{'(L1 dead, L2 at sqrt2)' if f_ok else 'CHECK'}")
    print(f"REFERENCE: bare S_L1 = {r['bare']['S_L1']:.4f} "
          f"(shield vs bare gap: {sL - r['bare']['S_L1']:+.4f}, descriptive)")
    print(f"GAUGES: acceptance {['%.2f' % r['logical']['acceptance'][b] for b in BASES]} "
          f"{'OK' if acc_ok else 'CHECK'}")
    ok = p_ok and ctrl_ok and null_ok and f_ok and acc_ok
    print(f"VERDICT: {'THE SHIELDED VERDICT — logical qubits in two shields violate the CHSH bound, with the product logical pair pinned below it in the same shots' if ok else 'NOT HELD (accounting above)'}")
    json.dump({"job_id": man["job_id"], "results": r, "sigma_primary": float(z),
               "primary_ok": bool(p_ok), "control_ok": bool(ctrl_ok), "null_ok": bool(null_ok),
               "falsifier_ok": bool(f_ok), "reference_ok": bool(ref_ok), "acc_ok": bool(acc_ok),
               "verdict_ok": bool(ok)},
              open(os.path.join(HERE, "..", "results", "exp196_logical_chsh_decode.json"), "w"), indent=1)
    print("-> results/exp196_logical_chsh_decode.json")


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
