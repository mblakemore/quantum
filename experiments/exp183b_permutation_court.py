#!/usr/bin/env python3
"""
Exp183b — THE PERMUTATION COURT (H14 cell A3, exp183 cold case)

Prereg: docs/exp183b-permutation-court-preregistration-whisper-c5065.md (FROZEN before flight).
Tests the C5057 one-coherent-phase-error model of exp183's sift-sector residual two ways in one job:
  Arm A: all THREE single-Y permutations (XXY, XYX, YXX) + YYY + Mermin set  -> D1 chi-square
  Arm B: same prep with rz(-phi_hat) on q2 (phi_hat DERIVED from frozen banked inputs) -> D3
Layout pinned across all circuits (the discriminand is "does WHICH qubit carries Y matter").

  python3 exp183b_permutation_court.py --selftest          # positive controls P1+P2 (must pass to fly)
  QPU_ACCOUNT_VAR=IBMQ_ALT4 python3 exp183b_permutation_court.py --submit
  python3 exp183b_permutation_court.py --decode
"""
import argparse, json, math, os, sys

import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
RESULTS = os.path.join(HERE, "..", "results")

# ---- frozen constants (prereg) ----
SHOTS = 8000
SEED_TRANSPILER = 1837
ALPHA_CRIT_DF2 = 9.210          # chi-square, df=2, alpha=0.01
BAND = 0.05                     # exp183's original sift-sector band, reused for D3(i)
# phi_hat DERIVED from frozen banked inputs (never transcribed):
BANKED_E_XXY, BANKED_E_YYY, BANKED_M = 0.0955, -0.10075, 3.3695
S_BANKED = (BANKED_E_XXY - BANKED_E_YYY) / 2.0
PHI_HAT = math.atan2(S_BANKED, BANKED_M / 4.0)   # ~0.11597 rad = 6.644 deg

MERMIN = ["XXX", "XYY", "YXY", "YYX"]
MERMIN_SIGN = {"XXX": +1, "XYY": -1, "YXY": -1, "YYX": -1}
SINGLE_Y = ["XXY", "XYX", "YXX"]                 # Y on Charlie / Bob / Alice
ARM_A = MERMIN + SINGLE_Y + ["YYY"]
ARM_B = MERMIN + ["XXY", "YYY"]
ORDER = [["base", c] for c in ARM_A] + [["corr", c] for c in ARM_B]


def circuit(arm, combo, planted_phi=None, planted_asym=None):
    qc = QuantumCircuit(3, 3)
    qc.h(0); qc.cx(0, 1); qc.cx(1, 2)
    if planted_phi is not None:
        qc.rz(planted_phi, 2)                    # selftest: plant |111> phase
    if arm == "corr":
        qc.rz(-PHI_HAT, 2)                       # the intervention: dial the fitted phase away
    if planted_asym is not None:
        # selftest P2: qubit-SPECIFIC perturbation — a small extra phase applied only when
        # the Y lands on qubit 0 (Alice). Breaks permutation symmetry by construction.
        if combo == "YXX":
            qc.rz(planted_asym, 2)
    for q, b in enumerate(combo):
        if b == "X":
            qc.h(q)
        elif b == "Y":
            qc.sdg(q); qc.h(q)
    qc.measure(range(3), range(3))
    return qc


def e3_from_counts(counts, shots):
    acc = 0
    for b, n in counts.items():
        b = b.replace(" ", "")
        va, vb, vc = 1 - 2 * int(b[-1]), 1 - 2 * int(b[-2]), 1 - 2 * int(b[-3])
        acc += n * va * vb * vc
    return acc / shots


def mermin(e3):
    return sum(MERMIN_SIGN[c] * e3[c] for c in MERMIN)


def grade(e3_base, e3_corr, shots, out_path=None, job_id=None, backend=None, raw=None):
    """The frozen decision rules, one code path (selftest and flight both come through here)."""
    se = 1.0 / math.sqrt(shots)
    se_m = 2.0 / math.sqrt(shots)
    M_A, M_B = mermin(e3_base), mermin(e3_corr)
    g1 = M_A >= 3.0
    anomaly_mag = (abs(e3_base["XXY"]) + abs(e3_base["YYY"])) / 2.0
    g2 = anomaly_mag >= 0.05
    ys = [e3_base[c] for c in SINGLE_Y]
    ybar = float(np.mean(ys))
    chi2 = float(sum(((y - ybar) / se) ** 2 for y in ys))
    d1 = "SYMMETRIC" if chi2 <= ALPHA_CRIT_DF2 else "QUBIT-SPECIFIC"
    signs_ok = len({np.sign(y) for y in ys}) == 1
    yyy_ok = (np.sign(e3_base["YYY"]) == -np.sign(ybar)) and \
             abs(abs(e3_base["YYY"]) - abs(ybar)) <= 3 * se * math.sqrt(2)
    d2 = "PASS" if (signs_ok and yyy_ok) else "FAIL"
    if not g2:
        d3 = "NO-TEST (G2: anomaly not present in-window; drift filed to A1 census)"
    else:
        bx, by = abs(e3_corr["XXY"]), abs(e3_corr["YYY"])
        ax, ay = abs(e3_base["XXY"]), abs(e3_base["YYY"])
        if bx < BAND and by < BAND:
            d3 = "MECHANISM CONFIRMED (i): phase dialed away, sign as modeled"
        elif bx > 1.5 * ax and by > 1.5 * ay:
            d3 = "MECHANISM CONFIRMED (ii): sign convention inverted (correction doubled the phase)"
        elif abs(bx - ax) <= 3 * se and abs(by - ay) <= 3 * se:
            d3 = "CORRECTION INERT (iii): mechanism NOT confirmed"
        else:
            d3 = "UNDERDETERMINED: per-sector numbers published, no verdict forced"
    d4 = M_B - M_A
    lines = []
    lines.append(f"Exp183b PERMUTATION COURT | job {job_id} | backend {backend} | phi_hat = {math.degrees(PHI_HAT):.3f} deg")
    lines.append(f"  Arm A: M = {M_A:+.4f} (se {se_m:.4f})   Arm B: M = {M_B:+.4f}")
    for c in SINGLE_Y:
        lines.append(f"  A {c} (Y on {'Charlie' if c=='XXY' else 'Bob' if c=='XYX' else 'Alice'}): E3 = {e3_base[c]:+.4f}  (z vs mean: {(e3_base[c]-ybar)/se:+.2f})")
    lines.append(f"  A YYY: E3 = {e3_base['YYY']:+.4f}   |  B XXY: E3 = {e3_corr['XXY']:+.4f}   B YYY: E3 = {e3_corr['YYY']:+.4f}")
    lines.append(f"G1 health (M_A >= 3.0):            {'PASS' if g1 else 'FAIL -> NO-TEST'}")
    lines.append(f"G2 anomaly present (mean >= 0.05): {'PASS' if g2 else 'FAIL'} (mean |sector| = {anomaly_mag:.4f})")
    lines.append(f"D1 permutation chi2 = {chi2:.2f} vs {ALPHA_CRIT_DF2} -> {d1}")
    lines.append(f"D2 sign structure: {d2}")
    lines.append(f"D3 intervention: {d3}")
    lines.append(f"D4 M recovery (pre-declared UNDERPOWERED): dM = {d4:+.4f} (se {se_m*math.sqrt(2):.4f}, predicted +0.023)")
    text = "\n".join(lines)
    print(text)
    if out_path:
        payload = {"job_id": job_id, "backend": backend, "phi_hat_rad": PHI_HAT,
                   "e3_base": e3_base, "e3_corr": e3_corr, "M_A": M_A, "M_B": M_B,
                   "chi2": chi2, "verdicts": {"G1": g1, "G2": g2, "D1": d1, "D2": d2, "D3": d3, "D4_dM": d4},
                   "report": text}
        if raw is not None:
            payload["raw_counts"] = raw    # custody upgrade: raw counts ON DISK this time
        json.dump(payload, open(out_path, "w"), indent=1)
        print(f"-> {out_path}")
    return {"G1": g1, "G2": g2, "D1": d1, "D2": d2, "D3": d3, "chi2": chi2}


def _synth_counts(qc_nomeas, shots):
    from qiskit.quantum_info import Statevector
    probs = Statevector(qc_nomeas).probabilities_dict()
    return {b: int(round(p * shots)) for b, p in probs.items() if p > 1e-12}


def _ideal_e3(arm, combo, planted_phi=None, planted_asym=None):
    qc = circuit(arm, combo, planted_phi, planted_asym)
    qc.remove_final_measurements()
    counts = _synth_counts(qc, 10**8)   # high-N synthesis: kills count quantization (1/N << 1e-6)
    n = sum(counts.values())
    # 3-char keys from Statevector are q2q1q0; e3_from_counts indexes from the right = q0,q1,q2 — same product either way
    return e3_from_counts(counts, n)


def selftest():
    phi_t = PHI_HAT   # plant exactly the fitted phase
    # P1: planted uniform phase -> all single-Y equal +sin(phi), YYY = -sin(phi), corr arm zeroes it
    base = {c: _ideal_e3("base", c, planted_phi=phi_t) for c in ARM_A}
    corr = {c: _ideal_e3("corr", c, planted_phi=phi_t) for c in ARM_B}
    s = math.sin(phi_t)
    for c in SINGLE_Y:
        assert abs(base[c] - s) < 1e-6, f"P1: {c} reads {base[c]:.6f}, expected +{s:.6f}"
    assert abs(base["YYY"] + s) < 1e-6, "P1: YYY must read -sin(phi)"
    assert abs(corr["XXY"]) < 1e-9 and abs(corr["YYY"]) < 1e-9, \
        "P1: corrected arm must zero the sectors (pins the rz sign convention)"
    v = grade(base, corr, SHOTS)
    assert v["D1"] == "SYMMETRIC" and "CONFIRMED (i)" in v["D3"], f"P1 grade wrong: {v}"
    # P2: qubit-specific perturbation -> D1 must FIRE (the gate can block)
    base2 = {c: _ideal_e3("base", c, planted_phi=phi_t, planted_asym=0.35) for c in ARM_A}
    ys = [base2[c] for c in SINGLE_Y]
    chi2 = sum(((y - np.mean(ys)) / (1 / math.sqrt(SHOTS))) ** 2 for y in ys)
    assert chi2 > ALPHA_CRIT_DF2, f"P2: asymmetric plant must trip chi2 (got {chi2:.1f})"
    print(f"SELFTEST PASS: P1 planted phi={math.degrees(phi_t):.2f}deg -> sectors +/-{s:.4f}, "
          f"correction zeroes them, D1 SYMMETRIC, D3 CONFIRMED(i). P2 asymmetric plant trips chi2={chi2:.0f}. "
          f"Sign convention pinned. Cleared to fly.")


def _pick_triple(backend):
    """Linear connected triple (a-b, b-c) minimizing summed readout + 2q error, from live properties."""
    props = backend.properties()
    cmap = {tuple(sorted(e)) for e in backend.configuration().coupling_map}
    nq = backend.configuration().n_qubits
    adj = {q: set() for q in range(nq)}
    for a, b in cmap:
        adj[a].add(b); adj[b].add(a)
    def ro(q):
        try: return props.readout_error(q)
        except Exception: return 1.0
    def g2(a, b):
        for name in ("cz", "ecr", "cx"):
            try: return props.gate_error(name, [a, b])
            except Exception:
                try: return props.gate_error(name, [b, a])
                except Exception: continue
        return 1.0
    best, best_score = None, 1e9
    for b in range(nq):
        for a in adj[b]:
            for c in adj[b]:
                if c <= a: continue
                score = ro(a) + ro(b) + ro(c) + g2(a, b) + g2(b, c)
                if score < best_score:
                    best, best_score = [a, b, c], score
    return best, best_score


def submit(backend_name):
    sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
    from ibm_multi_account import assert_explicit_account, service_for_submission
    from qiskit_ibm_runtime import SamplerV2
    acct = assert_explicit_account()
    svc = service_for_submission(acct)
    names = [b.name for b in svc.backends()]
    if backend_name not in names:
        sys.exit(f"ABORT (fail closed): {acct} cannot see {backend_name}. Visible: {names}. "
                 f"The anomaly under test is fez-specific — not flying elsewhere silently.")
    backend = svc.backend(backend_name)
    layout, score = _pick_triple(backend)
    print(f"[account: {acct}] backend {backend_name}, pinned layout {layout} (score {score:.4f})")
    circs = [transpile(circuit(arm, c), backend=backend, optimization_level=1,
                       initial_layout=layout, seed_transpiler=SEED_TRANSPILER)
             for arm, c in ORDER]
    sampler = SamplerV2(mode=backend)
    job = sampler.run(circs, shots=SHOTS)
    try:
        pending = svc.backend(backend_name).status().pending_jobs
    except Exception:
        pending = None
    manifest = {"exp": "183b", "slug": "permutation_court", "backend": backend_name, "shots": SHOTS,
                "pending_jobs_at_submit": pending,
                "account": acct, "job_id": job.job_id(), "order": ORDER, "initial_layout": layout,
                "seed_transpiler": SEED_TRANSPILER, "phi_hat_rad": PHI_HAT,
                "prereg": "docs/exp183b-permutation-court-preregistration-whisper-c5065.md",
                "authorization": "Creator 'fly on alt4 if you can' (single-use, consumed here)"}
    out = os.path.join(RESULTS, "exp183b_permutation_court_manifest.json")
    json.dump(manifest, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circs)} circuits x {SHOTS} shots) -> {out}")
    print("submit-and-exit: completion via ship-computer watch; decode separately.")


def decode():
    sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
    from ibm_multi_account import service_for_job
    mp = os.path.join(RESULTS, "exp183b_permutation_court_manifest.json")
    man = json.load(open(mp))
    svc, acct = service_for_job(man["job_id"])
    print(f"[account: {acct}]")
    res = svc.job(man["job_id"]).result()
    raw = {}
    for idx, (arm, c) in enumerate(man["order"]):
        r0 = res[idx]; reg = list(r0.data.keys())[0]
        raw[f"{arm}:{c}"] = getattr(r0.data, reg).get_counts()
    e3_base = {c: e3_from_counts(raw[f"base:{c}"], man["shots"]) for c in ARM_A}
    e3_corr = {c: e3_from_counts(raw[f"corr:{c}"], man["shots"]) for c in ARM_B}
    grade(e3_base, e3_corr, man["shots"],
          out_path=os.path.join(RESULTS, "exp183b_permutation_court_decode.json"),
          job_id=man["job_id"], backend=man["backend"], raw=raw)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--submit", action="store_true")
    ap.add_argument("--decode", action="store_true")
    ap.add_argument("--backend", default="ibm_fez")
    a = ap.parse_args()
    if a.selftest: selftest()
    elif a.submit: submit(a.backend)
    elif a.decode: decode()
    else: ap.print_help()
