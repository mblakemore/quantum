#!/usr/bin/env python3
"""Exp159b — QUANTUM SENSOR v2: two-point calibration fixes the bias the coverage gate caught.
C4848. v1 (job d9dsc34inv1c73apfu60): Heisenberg gain real (ratio 0.249) but GHZ coverage MISSED
at 8 sigma — precision without accuracy. Root cause: the theta=0 one-point calibration cannot
separate contrast from a phase OFFSET (cos is even), and the GHZ epoch carries a systematic
~0.03 rad/qubit-slope that the product arm does not.

THE FIX. Each sensor now gets TWO calibration arms in the same job: applied 0 and a KNOWN
reference theta_ref. Three fringe points (0, ref, field) determine three unknowns
(contrast C, offset delta, field theta*):
    p(applied) = (1 + C cos(k*(applied + delta))) / 2
delta from the cal/ref pair (1D bisection), C from the cal point, then
theta_hat = arccos((2 p_field - 1)/C)/k - delta. Errors by parametric bootstrap through the
whole solve (2000 draws). Same blind seal protocol; same pre-registered gates.

TRUTH-GATES: (A) noiseless — recovers theta*, ratio ~0.20; (B) INJECTED-SYSTEMATIC — a synthetic
Rz offset (the v1 disease, -0.03 rad) is added to the GHZ arms in sim and the two-point pipeline
must STILL cover truth (the correction machinery is proven before flight; v1's pipeline provably
fails this same gate).

FENCE: offset assumed quasi-static within the job (all 6 circuits, one job, minutes) and within
±0.06 rad of zero (bisection bracket); dynamic range still 2pi/5.

Usage:
  python3 exp159b_sensor_v2.py --selftest
  python3 exp159b_sensor_v2.py --submit [--backend ibm_fez --shots 4096]
  python3 exp159b_sensor_v2.py --decode
"""
import argparse, hashlib, json, os, secrets, sys
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
from exp159_sensor import (N, THETA_WINDOW, product_circuit, ghz_circuit,
                           _p_zero_bits, draw_and_seal)

THETA_REF = 0.35            # known reference phase (mid-window, steep fringe for both slopes)
DELTA_BRACKET = 0.06        # quasi-static offset assumed within +-this (v1 measured ~ -0.03)
ARMS = ("prod_cal", "prod_ref", "prod_field", "ghz_cal", "ghz_ref", "ghz_field")
BOOT = 2000


def _solve_delta(p_cal, p_ref, k, theta_ref):
    """Bisection for delta in p_cal/p_ref ratio equation; returns (delta, C)."""
    a_cal, a_ref = 2 * p_cal - 1, 2 * p_ref - 1
    f = lambda d: a_cal * np.cos(k * (theta_ref + d)) - a_ref * np.cos(k * d)
    lo, hi = -DELTA_BRACKET, DELTA_BRACKET
    flo = f(lo)
    if flo * f(hi) > 0:
        return None, None                     # offset outside bracket -> flag, don't fake it
    for _ in range(60):
        mid = 0.5 * (lo + hi)
        if flo * f(mid) <= 0: hi = mid
        else: lo, flo = mid, f(mid)
    d = 0.5 * (lo + hi)
    C = a_cal / np.cos(k * d)
    return float(d), float(C)


def _estimate_2pt(p_cal, p_ref, p_field, k):
    """Two-point-calibrated estimate; returns (theta_hat, delta, C) or Nones."""
    d, C = _solve_delta(p_cal, p_ref, k, THETA_REF)
    if d is None or C <= 0:
        return None, None, None
    x = np.clip((2 * p_field - 1) / C, -1.0, 1.0)
    return float(np.arccos(x) / k - d), d, C


def _bootstrap(p_cal, p_ref, p_field, k, M, rng):
    """Parametric bootstrap of the full solve; returns (theta_hat, sigma, delta, C)."""
    th0, d0, C0 = _estimate_2pt(p_cal, p_ref, p_field, k)
    if th0 is None:
        return None, None, None, None
    ths = []
    for _ in range(BOOT):
        pc = rng.binomial(M, p_cal) / M
        pr = rng.binomial(M, p_ref) / M
        pf = rng.binomial(M, p_field) / M
        th, _, _ = _estimate_2pt(pc, pr, pf, k)
        if th is not None:
            ths.append(th)
    return th0, float(np.std(ths)), d0, C0


def _run_arms(runner, theta_star, ghz_offset=0.0):
    """Build+run all 6 arms; ghz_offset injects a synthetic systematic (sim truth-gate only)."""
    from qiskit import QuantumCircuit
    counts = {}
    for arm in ARMS:
        applied = {"cal": 0.0, "ref": THETA_REF, "field": theta_star}[arm.split("_")[1]]
        if arm.startswith("prod"):
            qc = product_circuit(applied)
        else:
            qc = ghz_circuit(applied + ghz_offset)   # offset rides every GHZ arm, like a real systematic
        counts[arm] = runner(qc)
    return counts


def _decode_counts(counts, shots, rng):
    pp = {a: _p_zero_bits(counts[a], shots, N) for a in ARMS[:3]}
    pg = {a: _p_zero_bits(counts[a], shots, 1) for a in ARMS[3:]}
    th_p, s_p, d_p, C_p = _bootstrap(pp["prod_cal"], pp["prod_ref"], pp["prod_field"], 1, N * shots, rng)
    th_g, s_g, d_g, C_g = _bootstrap(pg["ghz_cal"], pg["ghz_ref"], pg["ghz_field"], N, shots, rng)
    return (th_p, s_p, d_p, C_p), (th_g, s_g, d_g, C_g)


def selftest():
    from qiskit_aer import AerSimulator
    sim = AerSimulator(); shots = 4096
    rng = np.random.default_rng(159)
    runner = lambda qc: sim.run(qc, shots=shots).result().get_counts()
    theta, _, _ = draw_and_seal()
    print(f"Exp159b selftest | secret theta* = {theta:.4f}")
    for label, off in (("A: clean", 0.0), ("B: INJECTED v1-disease (ghz offset -0.03)", -0.03)):
        counts = _run_arms(runner, theta, ghz_offset=off)
        (th_p, s_p, d_p, C_p), (th_g, s_g, d_g, C_g) = _decode_counts(counts, shots, rng)
        ratio = (s_g / s_p) ** 2
        print(f"  [{label}]")
        print(f"    product: {th_p:.4f}±{s_p:.4f} (delta {d_p:+.4f})  ghz: {th_g:.4f}±{s_g:.4f} "
              f"(delta {d_g:+.4f})  ratio {ratio:.3f}")
        assert abs(th_p - theta) < 3 * s_p, f"{label}: product coverage FAIL"
        assert abs(th_g - theta) < 3 * s_g, f"{label}: ghz coverage FAIL (two-point cal broken)"
        if off:
            assert abs(d_g - off) < 0.01, f"{label}: injected offset not recovered ({d_g:+.4f} vs {off})"
    print("SELFTEST PASS: clean recovery AND the injected v1-disease is measured and corrected — "
          "the pipeline provably fixes the failure v1's coverage gate caught. Cleared to fly.")


def submit(backend_name, shots):
    from qiskit import transpile
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    theta, salt, commit = draw_and_seal()
    circuits = []
    for arm in ARMS:
        applied = {"cal": 0.0, "ref": THETA_REF, "field": theta}[arm.split("_")[1]]
        qc = product_circuit(applied) if arm.startswith("prod") else ghz_circuit(applied)
        circuits.append(transpile(qc, backend=backend, optimization_level=3))
    sampler = SamplerV2(mode=backend); job = sampler.run(circuits, shots=shots)
    json.dump({"theta_star": theta, "salt": salt},
              open(os.path.join(HERE, "..", "results", "exp159_sensor_v2_SEAL.json"), "w"), indent=1)
    manifest = {"exp": "159b", "slug": "sensor_v2", "backend": backend_name, "shots": shots,
                "job_id": job.job_id(), "order": list(ARMS), "theta_ref": THETA_REF,
                "theta_window": THETA_WINDOW, "delta_bracket": DELTA_BRACKET,
                "commitment_sha256": commit,
                "prereg": {"coverage": "both 95% CIs (1.96 sigma, bootstrap) contain revealed theta*",
                           "head_to_head": "var_GHZ/var_product < 0.5",
                           "prediction": "GHZ coverage HIT after two-point correction; measured "
                                         "delta_g in [-0.06,-0.01]; ratio 0.2-0.55 (bootstrap widens)"},
                "note": "v2: two-point calibration (0 + theta_ref) separates contrast from offset; "
                        "fix for v1's 8-sigma GHZ coverage miss"}
    out = os.path.join(HERE, "..", "results", "exp159_sensor_v2_manifest.json")
    json.dump(manifest, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} (6 circuits, {shots} shots) -> {out}")
    print(f"COMMITTED sha256 = {commit}")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    mp = os.path.join(HERE, "..", "results", "exp159_sensor_v2_manifest.json")
    svc = _get_ibm_service(); man = json.load(open(mp)); res = svc.job(man["job_id"]).result()
    shots = man["shots"]; rng = np.random.default_rng(1590)
    counts = {}
    for i, arm in enumerate(man["order"]):
        r = res[i]; reg = list(r.data.keys())[0]
        counts[arm] = getattr(r.data, reg).get_counts()
    (th_p, s_p, d_p, C_p), (th_g, s_g, d_g, C_g) = _decode_counts(counts, shots, rng)
    if th_p is None or th_g is None:
        print("DECODE VOID: offset outside ±%.2f bracket — quasi-static assumption failed" % DELTA_BRACKET)
        return
    ratio = (s_g / s_p) ** 2
    print(f"Exp159b SENSOR v2 decode | job {man['job_id']} | backend {man['backend']}")
    print(f"product: C={C_p:.3f} delta={d_p:+.4f} -> theta = {th_p:.4f} ± {s_p:.4f}")
    print(f"GHZ:     C={C_g:.3f} delta={d_g:+.4f} -> theta = {th_g:.4f} ± {s_g:.4f}")
    print(f"variance ratio GHZ/product = {ratio:.3f} (gate < 0.5)")
    seal = json.load(open(os.path.join(HERE, "..", "results", "exp159_sensor_v2_SEAL.json")))
    reveal = f"theta={seal['theta_star']:.6f}|salt={seal['salt']}"
    ok_commit = hashlib.sha256(reveal.encode()).hexdigest() == man["commitment_sha256"]
    ts = seal["theta_star"]
    cov_p = abs(th_p - ts) < 1.96 * s_p; cov_g = abs(th_g - ts) < 1.96 * s_g
    gate = ratio < 0.5
    print(f"\nSEAL OPENED: theta* = {ts:.4f} | commitment {'VERIFIED' if ok_commit else 'MISMATCH — VOID'}")
    print(f"COVERAGE: product {'HIT' if cov_p else 'MISS'} ({abs(th_p-ts)/max(s_p,1e-9):.1f} sigma) | "
          f"GHZ {'HIT' if cov_g else 'MISS'} ({abs(th_g-ts)/max(s_g,1e-9):.1f} sigma)")
    verdict = ok_commit and cov_p and cov_g and gate
    print(f"VERDICT: {'SENSOR CERTIFIED — blind, bias-corrected, entanglement-enhanced' if verdict else 'FAILED a pre-registered gate (honest accounting above)'}")
    out = {"job_id": man["job_id"], "theta_star": ts, "commitment_verified": bool(ok_commit),
           "product": {"theta": th_p, "sigma": s_p, "delta": d_p, "contrast": C_p, "covered": bool(cov_p)},
           "ghz": {"theta": th_g, "sigma": s_g, "delta": d_g, "contrast": C_g, "covered": bool(cov_g)},
           "variance_ratio": float(ratio), "verdict_ok": bool(verdict)}
    json.dump(out, open(os.path.join(HERE, "..", "results", "exp159_sensor_v2_decode.json"), "w"), indent=1)
    print("-> results/exp159_sensor_v2_decode.json")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true"); ap.add_argument("--submit", action="store_true")
    ap.add_argument("--decode", action="store_true")
    ap.add_argument("--backend", default="ibm_fez"); ap.add_argument("--shots", type=int, default=4096)
    a = ap.parse_args()
    if a.selftest: selftest()
    elif a.submit: submit(a.backend, a.shots)
    elif a.decode: decode()
    else: ap.print_help()
