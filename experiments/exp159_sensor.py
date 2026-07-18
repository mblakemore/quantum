#!/usr/bin/env python3
"""Exp159 — QUANTUM SENSOR: measure a hidden field, blind, and call the shot.
Creator directive C4848: fly the metrology sensor. Successor to the GHZ Sextant exhibit —
the Sextant proved the RESOURCE (entangled probes beat the SQL); this flies the INSTRUMENT.

THE AHA. A sensor is only as honest as its error bar. We draw a secret field strength theta*,
COMMIT sha256(theta*||salt) in the manifest before flight (the seal), then two sensors read the
field at identical interrogation budget and publish estimate ± CI from the data alone. Only then
does the seal open. The instrument must (a) contain the truth in its interval (COVERAGE — a wrong
error bar fails the flight even if the point lands close) and (b) show the entangled strategy
beating the classical one head-to-head at matched budget.

TWO SENSORS, matched budget (5 qubits × 4096 shots of field interrogation each):
  PRODUCT — five independent Ramsey probes: |+>, field Rz(theta*), measure X. Slope 1,
            M = 5×4096 independent trials. The best classical-strategy scaling (SQL).
  GHZ     — one GHZ-5 probe: entangle, every qubit feels the field, disentangling readout
            (mirror CX ladder + H) concentrates the fringe on one qubit. Slope 5 (the phase
            accumulates N times), M = 4096 trials. Heisenberg strategy.
  Ideal variance ratio GHZ/product = (M_p/M_g)·(1/N²) = 5/25 = 0.20; contrast degradation
  moves it toward ~0.3. Pre-registered gate: ratio < 0.5. Coverage gate: both 95% CIs cover
  the revealed theta*.

CALIBRATION WITHIN-JOB (C4199 baseline-to-qubits): each sensor gets a theta=0 arm in the SAME
job; its measured contrast C enters the estimator p = (1 + C·cos(k·theta))/2 and the CI. No
borrowed numbers; drift cannot split calibration from measurement (C4847 non-stationarity).

FENCE (headline): a phase sensor on 5 qubits with the classic GHZ tradeoff — dynamic range
2π/5, theta* committed inside the unambiguous window [0.15, 0.55] rad (range fenced in the
commit, value sealed). A demonstration of blind entanglement-enhanced estimation with honest
intervals, not a field-deployed magnetometer.

Usage:
  python3 exp159_sensor.py --selftest
  python3 exp159_sensor.py --submit [--backend ibm_fez --shots 4096]
  python3 exp159_sensor.py --decode --manifest ../results/exp159_sensor_manifest.json
"""
import argparse, hashlib, json, os, secrets, sys
import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

N = 5                      # probe qubits
THETA_WINDOW = (0.15, 0.55)   # committed unambiguous window (5*theta in (0.75, 2.75) ⊂ (0, π))
ARMS = ("prod_cal", "ghz_cal", "prod_field", "ghz_field")


def product_circuit(theta):
    """Five parallel Ramsey probes: |+> , Rz(theta), X-basis measure. Slope 1 per qubit."""
    qc = QuantumCircuit(N, N)
    for q in range(N):
        qc.h(q)
    qc.barrier()
    if theta:
        for q in range(N):
            qc.rz(theta, q)
    qc.barrier()
    for q in range(N):
        qc.h(q)
    qc.measure(range(N), range(N))
    return qc


def ghz_circuit(theta):
    """GHZ-5 probe with disentangling readout: fringe cos(5*theta) on qubit 0."""
    qc = QuantumCircuit(N, 1)
    qc.h(0)
    for q in range(N - 1):
        qc.cx(q, q + 1)
    qc.barrier()
    if theta:
        for q in range(N):
            qc.rz(theta, q)
    qc.barrier()
    for q in range(N - 1, 0, -1):
        qc.cx(q - 1, q)
    qc.h(0)
    qc.measure(0, 0)
    return qc


def _p_zero_bits(counts, shots, nbits):
    """Per-shot fraction of 0s pooled over nbits classical bits (product arm pooling)."""
    zeros = 0
    for b, c in counts.items():
        b = b.replace(" ", "")[-nbits:]
        zeros += b.count("0") * c
    return zeros / (shots * nbits)


def estimate(p, C, k, M):
    """Invert p = (1 + C cos(k theta))/2 -> theta_hat with binomial-propagated sigma.
    Returns (theta_hat, sigma_theta). k = slope (1 or N), M = independent trials."""
    x = np.clip((2 * p - 1) / C, -1.0, 1.0)
    th = float(np.arccos(x) / k)
    sig_p = np.sqrt(max(p * (1 - p), 1e-12) / M)
    denom = max(C * abs(np.sin(k * th)) * k / 2, 1e-9)   # |dp/dtheta|
    return th, float(sig_p / denom)


def _contrast_cal(p0):
    """theta=0 calibration: p0 = (1+C)/2 -> C = 2 p0 - 1."""
    return max(2 * p0 - 1, 1e-6)


def draw_and_seal():
    theta = float(np.round(THETA_WINDOW[0] + secrets.randbelow(10**6) / 10**6
                           * (THETA_WINDOW[1] - THETA_WINDOW[0]), 6))
    salt = secrets.token_hex(16)
    commit = hashlib.sha256(f"theta={theta:.6f}|salt={salt}".encode()).hexdigest()
    return theta, salt, commit


def selftest():
    """P3 TRUTH-GATE (noiseless Aer): both sensors recover a drawn theta* within CI, coverage
    holds, and the variance ratio sits near the ideal 0.20. The test can fail: a wrong slope,
    wrap, or broken CI propagation misses truth or the ratio."""
    from qiskit_aer import AerSimulator
    sim = AerSimulator(); shots = 4096
    rng_theta, _, _ = draw_and_seal()
    print(f"Exp159 selftest (noiseless Aer) | secret theta* = {rng_theta:.4f} rad")
    counts = {}
    for arm, qc in (("prod_cal", product_circuit(0)), ("ghz_cal", ghz_circuit(0)),
                    ("prod_field", product_circuit(rng_theta)), ("ghz_field", ghz_circuit(rng_theta))):
        counts[arm] = sim.run(qc, shots=shots).result().get_counts()
    Cp = _contrast_cal(_p_zero_bits(counts["prod_cal"], shots, N))
    Cg = _contrast_cal(_p_zero_bits(counts["ghz_cal"], shots, 1))
    th_p, s_p = estimate(_p_zero_bits(counts["prod_field"], shots, N), Cp, 1, N * shots)
    th_g, s_g = estimate(_p_zero_bits(counts["ghz_field"], shots, 1), Cg, N, shots)
    ratio = (s_g / s_p) ** 2
    print(f"  contrasts: product {Cp:.3f}, GHZ {Cg:.3f}")
    print(f"  PRODUCT sensor: {th_p:.4f} ± {s_p:.4f}  (err {abs(th_p-rng_theta):.4f})")
    print(f"  GHZ sensor:     {th_g:.4f} ± {s_g:.4f}  (err {abs(th_g-rng_theta):.4f})")
    print(f"  variance ratio GHZ/product = {ratio:.3f} (ideal 0.20)")
    assert abs(th_p - rng_theta) < 2.5 * s_p and abs(th_g - rng_theta) < 2.5 * s_g, "coverage FAIL"
    assert ratio < 0.35, "Heisenberg gain FAIL in noiseless sim"
    print("SELFTEST PASS: both sensors cover truth, GHZ variance ~1/5 of product. Cleared to fly.")


def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    theta, salt, commit = draw_and_seal()
    circuits = []
    for arm in ARMS:
        th = 0.0 if arm.endswith("cal") else theta
        qc = product_circuit(th) if arm.startswith("prod") else ghz_circuit(th)
        circuits.append(transpile(qc, backend=backend, optimization_level=3))
    sampler = SamplerV2(mode=backend); job = sampler.run(circuits, shots=shots)
    # seal file (private until reveal) + public manifest with the commitment only
    seal = {"theta_star": theta, "salt": salt}
    json.dump(seal, open(os.path.join(HERE, "..", "results", "exp159_sensor_SEAL.json"), "w"), indent=1)
    manifest = {"exp": 159, "slug": "sensor", "backend": backend_name, "shots": shots,
                "job_id": job.job_id(), "order": list(ARMS), "n_probes": N,
                "theta_window": THETA_WINDOW, "commitment_sha256": commit,
                "prereg": {"coverage": "both 95% CIs (1.96 sigma) must contain revealed theta*",
                           "head_to_head": "var_GHZ / var_product < 0.5 at matched budget (ideal 0.20)",
                           "calibration": "within-job theta=0 arms; per-sensor contrast into estimator+CI",
                           "prediction": "ratio 0.25-0.45 (2x-wide band); coverage holds both arms; "
                                         "GHZ contrast 0.75-0.92, product 0.90-0.98"},
                "note": "blind sealed-phase sensing: product vs GHZ-5 at matched budget; "
                        "seal opens only at decode"}
    out = os.path.join(HERE, "..", "results", "exp159_sensor_manifest.json")
    json.dump(manifest, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} (4 circuits, {shots} shots) -> {out}")
    print(f"COMMITTED sha256 = {commit}  (theta* sealed; window {THETA_WINDOW})")


def decode(mp):
    from run_exp66_qpu_partb import _get_ibm_service
    svc = _get_ibm_service(); man = json.load(open(mp)); res = svc.job(man["job_id"]).result()
    shots = man["shots"]
    counts = {}
    for i, arm in enumerate(man["order"]):
        r = res[i]; reg = list(r.data.keys())[0]
        counts[arm] = getattr(r.data, reg).get_counts()
    Cp = _contrast_cal(_p_zero_bits(counts["prod_cal"], shots, N))
    Cg = _contrast_cal(_p_zero_bits(counts["ghz_cal"], shots, 1))
    th_p, s_p = estimate(_p_zero_bits(counts["prod_field"], shots, N), Cp, 1, N * shots)
    th_g, s_g = estimate(_p_zero_bits(counts["ghz_field"], shots, 1), Cg, N, shots)
    ratio = (s_g / s_p) ** 2
    print(f"Exp159 QUANTUM SENSOR decode | job {man['job_id']} | backend {man['backend']}")
    print(f"calibration (within-job): product contrast {Cp:.3f} | GHZ contrast {Cg:.3f}")
    print(f"PRODUCT sensor reads: theta = {th_p:.4f} ± {s_p:.4f} rad  (95% CI ±{1.96*s_p:.4f})")
    print(f"GHZ sensor reads:     theta = {th_g:.4f} ± {s_g:.4f} rad  (95% CI ±{1.96*s_g:.4f})")
    print(f"variance ratio GHZ/product = {ratio:.3f}  (ideal 0.20 | pre-reg gate < 0.5)")
    # ---- REVEAL ----
    seal = json.load(open(os.path.join(HERE, "..", "results", "exp159_sensor_SEAL.json")))
    reveal = f"theta={seal['theta_star']:.6f}|salt={seal['salt']}"
    ok_commit = hashlib.sha256(reveal.encode()).hexdigest() == man["commitment_sha256"]
    ts = seal["theta_star"]
    cov_p = abs(th_p - ts) < 1.96 * s_p
    cov_g = abs(th_g - ts) < 1.96 * s_g
    gate = ratio < 0.5
    print(f"\nSEAL OPENED: theta* = {ts:.4f} rad | commitment {'VERIFIED' if ok_commit else 'MISMATCH — VOID'}")
    print(f"COVERAGE: product {'HIT' if cov_p else 'MISS'} (off by {abs(th_p-ts)/max(s_p,1e-9):.1f} sigma) | "
          f"GHZ {'HIT' if cov_g else 'MISS'} (off by {abs(th_g-ts)/max(s_g,1e-9):.1f} sigma)")
    verdict = ok_commit and cov_p and cov_g and gate
    print(f"VERDICT: {'SENSOR CERTIFIED — blind estimate covered truth in both arms and the entangled strategy beat the classical head-to-head' if verdict else 'FAILED a pre-registered gate (honest accounting above)'}")
    out = {"job_id": man["job_id"], "backend": man["backend"], "theta_star": ts,
           "commitment_verified": bool(ok_commit),
           "product": {"theta": th_p, "sigma": s_p, "contrast": Cp, "covered": bool(cov_p)},
           "ghz": {"theta": th_g, "sigma": s_g, "contrast": Cg, "covered": bool(cov_g)},
           "variance_ratio": float(ratio), "gate_ratio_lt_05": bool(gate), "verdict_ok": bool(verdict)}
    fn = os.path.join(HERE, "..", "results", "exp159_sensor_decode.json")
    json.dump(out, open(fn, "w"), indent=1)
    print(f"-> {fn}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true"); ap.add_argument("--submit", action="store_true")
    ap.add_argument("--decode", action="store_true"); ap.add_argument("--manifest")
    ap.add_argument("--backend", default="ibm_fez"); ap.add_argument("--shots", type=int, default=4096)
    a = ap.parse_args()
    if a.selftest: selftest()
    elif a.submit: submit(a.backend, a.shots)
    elif a.decode: decode(a.manifest or os.path.join(HERE, "..", "results", "exp159_sensor_manifest.json"))
    else: ap.print_help()
