#!/usr/bin/env python3
"""Exp188 — THE LIVE CHOICE: the quartet's late choices made by in-circuit quantum coins. C4879.
Upgrades Exp184 + Exp187b, closing their compiled-choice fence: a fresh |+> ancilla is measured
MID-CIRCUIT, strictly AFTER the early record closes, and a dynamic if_test applies the
choice-dependent operation. Per-shot sort by the coin:
  184live — heads: Bell-measure the middles (swap) -> early A-record certifies entangled with D;
            tails: product-measure them -> the same-circuit records sort separable (~0.25).
  187live — heads: control X-basis (coherence between orders) -> ensembles off the equator;
            tails: control Z-basis -> the two definite orders reconstructed.
Free audits (within-circuit, no compilation confound): coin fairness; no-signaling-FROM-THE-
FUTURE (early marginal split by the coin must be flat).
Usage: --selftest | --submit [--backend ibm_fez --shots 8000] | --decode
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
from exp162_swap import fidelity

PI = np.pi
SETTINGS_184 = ("ZZ", "XX", "YY")
SETTINGS_187 = ("X", "Y", "Z")
# 187 analytic references (Exp187, sim-verified)
BLOCH_AB = (1.0, 0.0, 0.0); BLOCH_BA = (0.0, -1.0, 0.0)


def circ_184live(setting):
    """A=q0,B=q1,C=q2,D=q3,coin=q4. c0,c1=middles; c2=A; c3=D; c4=coin."""
    qc = QuantumCircuit(5, 5)
    qc.h(0); qc.cx(0, 1)                      # Bell(A,B)
    qc.barrier()
    if setting == "XX": qc.h(0)
    elif setting == "YY": qc.sdg(0); qc.h(0)
    qc.measure(0, 2)                          # A measured — record CLOSED
    qc.barrier()
    qc.h(2); qc.cx(2, 3)                      # Bell(C,D): D born after A died
    qc.barrier()
    qc.h(4); qc.measure(4, 4)                 # THE COIN — flipped after the record closed
    with qc.if_test((qc.clbits[4], 0)):       # heads: Bell measurement (the swap)
        qc.cx(1, 2); qc.h(1)
    qc.measure(1, 0); qc.measure(2, 1)        # (tails: bare product measurement)
    qc.barrier()
    if setting == "XX": qc.h(3)
    elif setting == "YY": qc.sdg(3); qc.h(3)
    qc.measure(3, 3)
    return qc


def circ_187live(tbasis):
    """control=q0, target=q1, coin=q2. c0=target; c1=control; c2=coin."""
    qc = QuantumCircuit(3, 3)
    qc.h(0)
    qc.barrier()
    qc.x(0)
    qc.crx(PI / 2, 0, 1); qc.cp(PI / 2, 0, 1)
    qc.x(0)
    qc.cp(PI / 2, 0, 1); qc.crx(PI / 2, 0, 1)
    qc.barrier()
    if tbasis == "X": qc.h(1)
    elif tbasis == "Y": qc.sdg(1); qc.h(1)
    qc.measure(1, 0)                          # target measured — record CLOSED
    qc.barrier()
    qc.h(2); qc.measure(2, 2)                 # THE COIN
    with qc.if_test((qc.clbits[2], 0)):       # heads: X-sort (coherence question)
        qc.h(0)
    qc.measure(0, 1)                          # (tails: Z-sort — which order)
    return qc


def analyze(get, shots):
    r = {"184": {}, "187": {}}
    # --- 184live: per-coin parities of (A=c2, D=c3) with swap-frame on heads
    for coin_val, key in ((0, "heads_bell"), (1, "tails_product")):
        par = {}
        fair = {}
        marg = {}
        for s in SETTINGS_184:
            acc = n = 0; heads = tot = 0; am = an = 0
            for bstr, cnt in get("184", s).items():
                b = bstr.replace(" ", "")
                coin = int(b[-5]); a = int(b[-3]); d = int(b[-4])
                tot += cnt
                if coin == 0: heads += cnt
                if coin != coin_val: continue
                if coin_val == 0:                     # frame sift (Exp162 rules)
                    c0, c1 = int(b[-1]), int(b[-2])
                    if s == "ZZ": d ^= c1
                    elif s == "XX": d ^= c0
                    else: d ^= c0 ^ c1
                acc += (1 - 2 * a) * (1 - 2 * d) * cnt; n += cnt
                am += (1 - 2 * a) * cnt; an += cnt
            par[s] = acc / n if n else 0.0
            fair[s] = heads / tot
            marg[s] = am / an if an else 0.0
        r["184"][key] = {"F": float(fidelity(par)), **{k: float(v) for k, v in par.items()},
                         "A_marginal": {k: float(v) for k, v in marg.items()}}
        r["184"]["fair"] = {k: float(v) for k, v in fair.items()}
    # --- 187live: per-coin sorted target Bloch
    for coin_val, key in ((0, "heads_X"), (1, "tails_Z")):
        sort = {0: {}, 1: {}}; nn = {0: 0, 1: 0}
        fair = {}; marg = {}
        for tb in SETTINGS_187:
            acc = {0: 0, 1: 0}; n = {0: 0, 1: 0}; heads = tot = 0; tm = tn = 0
            for bstr, cnt in get("187", tb).items():
                b = bstr.replace(" ", "")
                coin = int(b[-3]); t = int(b[-1]); c = int(b[-2])
                tot += cnt
                if coin == 0: heads += cnt
                if coin != coin_val: continue
                acc[c] += (1 - 2 * t) * cnt; n[c] += cnt
                tm += (1 - 2 * t) * cnt; tn += cnt
            for c in (0, 1):
                sort[c][tb] = acc[c] / n[c] if n[c] else 0.0
                nn[c] += n[c]
            fair[tb] = heads / tot
            marg[tb] = tm / tn if tn else 0.0
        r["187"][key] = {"sorted": {c: {k: float(v) for k, v in sort[c].items()} for c in (0, 1)},
                         "p1": float(nn[1] / (nn[0] + nn[1])),
                         "T_marginal": {k: float(v) for k, v in marg.items()}}
        r["187"]["fair"] = {k: float(v) for k, v in fair.items()}
    return r


def _fid(bloch, ref):
    return (1 + bloch["X"] * ref[0] + bloch["Y"] * ref[1] + bloch["Z"] * ref[2]) / 2


def selftest():
    from qiskit_aer import AerSimulator
    sim = AerSimulator(); shots = 20000
    cache = {}
    def get(fam, s):
        k = (fam, s)
        if k not in cache:
            qc = circ_184live(s) if fam == "184" else circ_187live(s)
            cache[k] = sim.run(qc, shots=shots).result().get_counts()
        return cache[k]
    r = analyze(get, shots)
    hb, tp = r["184"]["heads_bell"], r["184"]["tails_product"]
    hx, tz = r["187"]["heads_X"], r["187"]["tails_Z"]
    print("Exp188 selftest (noiseless Aer)")
    print(f"  184live heads(Bell): F={hb['F']:.3f} | tails(product): F={tp['F']:.3f}")
    print(f"  187live heads(X-sort): W+<Z>={hx['sorted'][0]['Z']:+.3f}  W-<Z>={hx['sorted'][1]['Z']:+.3f}")
    print(f"  187live tails(Z-sort): F(A->B)={_fid(tz['sorted'][0], BLOCH_AB):.3f}  "
          f"F(B->A)={_fid(tz['sorted'][1], BLOCH_BA):.3f}")
    assert hb["F"] > 0.99, "heads must certify the across-time handshake"
    assert abs(tp["F"] - 0.25) < 0.04, "tails must sort separable at 0.25"
    assert abs(hx["sorted"][0]["Z"] - 1/3) < 0.04 and abs(hx["sorted"][1]["Z"] + 1) < 0.03, "X-sort off equator"
    assert _fid(tz["sorted"][0], BLOCH_AB) > 0.99 and _fid(tz["sorted"][1], BLOCH_BA) > 0.99, "Z-sort orders"
    for fam in ("184", "187"):
        for v in r[fam]["fair"].values():
            assert 0.47 < v < 0.53, "coin must be fair"
    aspread = max(abs(hb["A_marginal"][s] - tp["A_marginal"][s]) for s in SETTINGS_184)
    tspread = max(abs(hx["T_marginal"][s] - tz["T_marginal"][s]) for s in SETTINGS_187)
    assert aspread < 0.04 and tspread < 0.04, "closed records must not depend on the future coin"
    print(f"  future-blindness: A-split {aspread:.3f}, T-split {tspread:.3f} (must be ~0)")
    print("SELFTEST PASS: live quantum coins flipped after the records close retro-sort them "
          "exactly as the compiled choices did; coins fair; closed records blind to the future. "
          "Cleared to fly.")


def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    circuits, order = [], []
    for s in SETTINGS_184:
        circuits.append(transpile(circ_184live(s), backend=backend, optimization_level=3))
        order.append(["184", s])
    for tb in SETTINGS_187:
        circuits.append(transpile(circ_187live(tb), backend=backend, optimization_level=3))
        order.append(["187", tb])
    sampler = SamplerV2(mode=backend); job = sampler.run(circuits, shots=shots)
    manifest = {"exp": 188, "slug": "live_choice", "backend": backend_name, "shots": shots,
                "job_id": job.job_id(), "order": order,
                "prereg": {"p184": "F(heads) > 1/2 at >=5 sigma, band 0.72-0.86; F(tails) 0.18-0.32",
                           "p187": "heads: W+ > 0 at >=3 sigma (band +0.05..+0.28), W- < 0 at >=5 sigma "
                                   "(band -0.80..-0.40); tails: definite orders F >= 0.80",
                           "coin": "P(heads) 0.46-0.54 every circuit",
                           "future_blindness": "closed-record marginal split by coin < 0.03 per basis"}}
    out = os.path.join(HERE, "..", "results", "exp188_live_choice_manifest.json")
    json.dump(manifest, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits, {shots} shots) -> {out}")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    mp = os.path.join(HERE, "..", "results", "exp188_live_choice_manifest.json")
    svc = _get_ibm_service(); man = json.load(open(mp)); res = svc.job(man["job_id"]).result()
    shots = man["shots"]
    raw = {}
    for idx, (fam, s) in enumerate(man["order"]):
        r0 = res[idx]; reg = list(r0.data.keys())[0]
        raw[(fam, s)] = getattr(r0.data, reg).get_counts()
    r = analyze(lambda fam, s: raw[(fam, s)], shots)
    hb, tp = r["184"]["heads_bell"], r["184"]["tails_product"]
    hx, tz = r["187"]["heads_X"], r["187"]["tails_Z"]
    se_h = 0.75 / np.sqrt(shots * 0.5)
    seW = 1.0 / np.sqrt(shots * 0.5 * 0.75); seWm = 1.0 / np.sqrt(shots * 0.5 * 0.25)
    nsig184 = (hb["F"] - 0.5) / se_h
    fAB, fBA = _fid(tz["sorted"][0], BLOCH_AB), _fid(tz["sorted"][1], BLOCH_BA)
    aspread = max(abs(hb["A_marginal"][s] - tp["A_marginal"][s]) for s in SETTINGS_184)
    tspread = max(abs(hx["T_marginal"][s] - tz["T_marginal"][s]) for s in SETTINGS_187)
    fair_all = list(r["184"]["fair"].values()) + list(r["187"]["fair"].values())
    print(f"Exp188 THE LIVE CHOICE decode | job {man['job_id']} | backend {man['backend']}")
    print(f"  184live — the coin flipped AFTER A's record closed:")
    print(f"    heads (live Bell choice): F = {hb['F']:.3f} ({nsig184:.0f} sigma over 1/2)")
    print(f"    tails (live product choice): F = {tp['F']:.3f}")
    print(f"  187live — the coin flipped AFTER the target's record closed:")
    print(f"    heads (live X-sort): W+<Z> = {hx['sorted'][0]['Z']:+.3f} ({hx['sorted'][0]['Z']/seW:+.0f} sigma) | "
          f"W-<Z> = {hx['sorted'][1]['Z']:+.3f} ({abs(hx['sorted'][1]['Z'])/seWm:.0f} sigma)")
    print(f"    tails (live Z-sort): F(A->B) = {fAB:.3f}  F(B->A) = {fBA:.3f}")
    print(f"  COINS: P(heads) = " + " ".join(f"{v:.3f}" for v in fair_all))
    print(f"  FUTURE-BLINDNESS: closed-record splits by coin — 184: {aspread:.4f}, 187: {tspread:.4f}")
    p184 = hb["F"] > 0.5 and nsig184 >= 5 and 0.18 <= tp["F"] <= 0.32
    p187 = (hx["sorted"][0]["Z"] > 0 and hx["sorted"][0]["Z"] / seW >= 3
            and hx["sorted"][1]["Z"] < 0 and abs(hx["sorted"][1]["Z"]) / seWm >= 5
            and fAB >= 0.80 and fBA >= 0.80)
    coin_ok = all(0.46 <= v <= 0.54 for v in fair_all)
    blind_ok = aspread < 0.03 and tspread < 0.03
    print(f"\n184-LIVE: {'HELD' if p184 else 'NOT HELD'} | 187-LIVE: {'HELD' if p187 else 'NOT HELD'} | "
          f"COINS: {'fair' if coin_ok else 'BIASED'} | FUTURE-BLINDNESS: {'clean' if blind_ok else 'CHECK'}")
    ok = p184 and p187 and coin_ok and blind_ok
    print(f"VERDICT: {'THE CHOICES WERE LIVE — quantum coins flipped after the records closed still decided what the past was' if ok else 'NOT HELD (honest accounting above)'}")
    out = {"job_id": man["job_id"], "results": r, "sigma_184": float(nsig184),
           "zsort_fids": {"AB": float(fAB), "BA": float(fBA)},
           "future_blindness": {"a184": float(aspread), "t187": float(tspread)},
           "p184": bool(p184), "p187": bool(p187), "coin_ok": bool(coin_ok),
           "blind_ok": bool(blind_ok), "verdict_ok": bool(ok)}
    json.dump(out, open(os.path.join(HERE, "..", "results", "exp188_live_choice_decode.json"), "w"), indent=1)
    print("-> results/exp188_live_choice_decode.json")


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
