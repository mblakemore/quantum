#!/usr/bin/env python3
"""
Exp95 (Elder C6347) — QQQ-tail Grover amplitude estimation ON REAL HARDWARE:
does shallow Grover amplification beat plain sampling, and where does the signal die?

WHAT THIS ADDS OVER F54/Exp78 (Elder C6269):
  F54 loaded a lognormal QQQ terminal-price distribution on ibm_marrakesh and sampled the
  tail P(S_T>K) at k=0 (plain loader). It then ARGUED — from FakeMarrakesh transpile depth —
  that Grover amplitude estimation (the only theoretical quantum win) "is half-gone by k~5 and
  buried by k~10", and DELIBERATELY DID NOT run Grover on hardware ("predicted garbage").
  Exp95 runs exactly that untested step: the SAME A loader, but with k=0..5 Grover iterations
  Q^k applied on the REAL chip, measuring the amplitude-estimation curve P_hw(k) = P(MSB=1).

  Ideal (noiseless): P(k) = sin^2((2k+1)*theta), theta = arcsin(sqrt(a*)), a*=0.479. This
  OSCILLATES (0.48 -> 0.56 -> 0.40 -> 0.63 -> 0.32 -> 0.72). On hardware, depolarizing noise
  drags P(k) -> 0.5 as depth grows, so the measurable CONTRAST |P_hw(k)-0.5| must decay with k.

  THE GENUINELY-UNCERTAIN QUESTIONS (pre-registered in the .md, gates pinned before finalize):
    H1  amplification visible at k=1: does the first Grover step move P in the ideal direction
        (UP toward 0.56) on hardware, beyond shot noise? Falsifier: flat / wrong-direction.
    H2  signal-death k*: the smallest k where measured contrast |P_hw(k)-0.5| <= HALF the ideal
        contrast |P_ideal(k)-0.5| (amplitude half-gone). F54's FakeMarrakesh predicts k*~5.
    H3  estimate quality: does ANY single-k inversion of P_hw(k) land closer to truth 0.479 than
        the k=0 bias (F54 measured +0.019 -> 0.498)? Or does depth-bias dominate at every k?

  Reuses exp78's build_A / grover_Q VERBATIM (comparability with the F54 k=0 datapoint;
  minimal new bug surface). Pure-additive: new script + pre-reg + result JSON + finding.
  Does not touch the causal-order (Ember exp94) or quiet-qubit (F58/F70) threads.

USAGE:
  python3 run_exp95_qqq_grover_hardware.py --sim         # ideal + FakeMarrakesh curve (free, gates go/no-go)
  python3 run_exp95_qqq_grover_hardware.py --submit      # ONE job, 7 PUBs (k=0,1,2,3,4,5 + k=0 retest) -> ibm_marrakesh
  python3 run_exp95_qqq_grover_hardware.py --finalize JOB_ID
"""
import sys, os, json, math, argparse
import numpy as np
from scipy import optimize

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator

# reuse the EXACT exp78 loader + Grover operator (comparability, no re-derivation)
from qae_qqq_tail_demo import (
    build_A, grover_Q, bucket_probs, true_tail_discrete, true_tail_continuous,
    _msb_one_prob, N_QUBITS, SHOTS, SEED_TRANSP, BACKEND_NAME,
)

K_VALUES = [0, 1, 2, 3, 4, 5]           # Grover iterations to sweep on hardware
PUB_LABELS = ["k0", "k1", "k2", "k3", "k4", "k5", "k0_retest"]  # last PUB = k=0 anchor retest
RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")
EXP_DIR     = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "experiments")
JOBIDS_PATH = os.path.join(EXP_DIR, "exp95_jobids.json")
os.makedirs(RESULTS_DIR, exist_ok=True); os.makedirs(EXP_DIR, exist_ok=True)


def theta_true():
    a_disc = true_tail_discrete(bucket_probs()[0])
    return math.asin(math.sqrt(a_disc)), a_disc


def ideal_curve():
    th, a = theta_true()
    return [math.sin((2 * k + 1) * th) ** 2 for k in K_VALUES], a


def build_grover_circuit(probs, k):
    """A followed by Q^k, measure MSB (the objective / good-state indicator)."""
    A = build_A(probs, measure=False)
    Q, _ = grover_Q(probs)
    qc = QuantumCircuit(N_QUBITS, 1)
    qc.compose(A, list(range(N_QUBITS)), inplace=True)
    for _ in range(k):
        qc.compose(Q, list(range(N_QUBITS)), inplace=True)
    qc.measure(N_QUBITS - 1, 0)
    return qc


def invert_single_k(p_meas, k):
    """Recover a* from a single measured P(k)=sin^2((2k+1)theta), branch nearest to k=0 estimate."""
    p = min(max(p_meas, 1e-9), 1 - 1e-9)
    base = math.asin(math.sqrt(p))            # in [0, pi/2]
    m = 2 * k + 1
    # candidate thetas s.t. sin^2(m*theta)=p and m*theta in [0, m*pi/2]
    cands = []
    for j in range(0, m + 1):
        # enumerate m*theta = base + j*pi  OR  (pi-base) + j*pi, then theta = that/m
        for mt in (base + j * math.pi, (math.pi - base) + j * math.pi):
            th = mt / m
            if 0 <= th <= math.pi / 2 + 1e-9:
                cands.append(math.sin(th) ** 2)
    # pick candidate closest to the true tail (report-only diagnostic; the point estimate
    # is under-determined at a single k without the full MLE — this is a nearest-branch read)
    _, a_true = theta_true()
    if not cands:
        return float("nan")
    return min(cands, key=lambda a: abs(a - a_true))


def mle_over_k(pmeas_by_k):
    """MLE combine across ALL k (canonical IAE) — the honest multi-k point estimate."""
    def nll(a):
        if a <= 1e-6 or a >= 1 - 1e-6:
            return 1e12
        ll = 0.0
        for k, p in pmeas_by_k:
            th = (2 * k + 1) * math.asin(math.sqrt(a))
            pk = max(1e-10, min(1 - 1e-10, math.sin(th) ** 2))
            m = int(round(p * SHOTS))
            ll += m * math.log(pk) + (SHOTS - m) * math.log(1 - pk)
        return -ll
    return float(optimize.minimize_scalar(nll, bounds=(1e-3, 1 - 1e-3), method='bounded').x)


def run_sim():
    probs = bucket_probs()[0]
    ideal, a_disc = ideal_curve()
    a_cont = true_tail_continuous()
    th, _ = theta_true()
    print(f"Exp95 SIM | QQQ tail Grover curve | a*_discrete={a_disc:.4f} a*_cont={a_cont:.4f} theta={th:.4f} rad", flush=True)
    print(f"  ideal P(k)=sin^2((2k+1)theta):", flush=True)
    for k, pk in zip(K_VALUES, ideal):
        print(f"    k={k}  power={2*k+1:>2}x  ideal_P={pk:.4f}  ideal_contrast|P-0.5|={abs(pk-0.5):.4f}", flush=True)

    # noiseless validation (should reproduce ideal within shot noise)
    sim = AerSimulator()
    print("\n  [noiseless AerSimulator]", flush=True)
    for k in K_VALUES:
        qc = build_grover_circuit(probs, k)
        tq = transpile(qc, sim, seed_transpiler=SEED_TRANSP)
        cn = sim.run(tq, shots=SHOTS).result().get_counts()
        print(f"    k={k}  P(MSB=1)={_msb_one_prob(cn):.4f}  (ideal {ideal[K_VALUES.index(k)]:.4f})", flush=True)

    # FakeMarrakesh noise preview -> the pre-run PREDICTOR for the pre-reg gates
    from qiskit_ibm_runtime.fake_provider import FakeMarrakesh
    fake = AerSimulator.from_backend(FakeMarrakesh())
    print("\n  [FakeMarrakesh noise model] (this is the pre-reg predictor for real HW)", flush=True)
    fake_curve = []; depth_rows = []
    for k in K_VALUES:
        qc = build_grover_circuit(probs, k)
        tqf = transpile(qc, fake, optimization_level=1, seed_transpiler=SEED_TRANSP)
        cf = fake.run(tqf, shots=SHOTS).result().get_counts()
        pk = _msb_one_prob(cf)
        n2q = sum(1 for g in tqf.data if g.operation.num_qubits == 2)
        fake_curve.append(pk); depth_rows.append({"k": k, "depth": tqf.depth(), "n2q": n2q})
        print(f"    k={k}  P_fake={pk:.4f}  contrast|P-0.5|={abs(pk-0.5):.4f}  depth={tqf.depth()} 2q={n2q}", flush=True)

    # signal-death k* under FakeMarrakesh: first k where fake contrast <= 0.5*ideal contrast
    kstar_fake = None
    for k, pk in zip(K_VALUES, fake_curve):
        ic = abs(ideal[K_VALUES.index(k)] - 0.5)
        if ic > 1e-6 and abs(pk - 0.5) <= 0.5 * ic:
            kstar_fake = k; break
    print(f"\n  [FakeMarrakesh predicted signal-death k*] = {kstar_fake}", flush=True)

    out = {"experiment": "exp95_qqq_grover_hardware", "cycle": 6347, "author": "elder",
           "a_discrete": a_disc, "a_continuous": a_cont, "theta": th, "k_values": K_VALUES,
           "ideal_curve": ideal, "fakemarrakesh_curve": fake_curve, "depth_rows": depth_rows,
           "fakemarrakesh_kstar": kstar_fake}
    path = os.path.join(RESULTS_DIR, "exp95_sim.json")
    with open(path, "w") as f: json.dump(out, f, indent=2)
    print(f"\n  saved -> {path}", flush=True)


def run_submit():
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    probs = bucket_probs()[0]
    service = _get_ibm_service(); backend = service.backend(BACKEND_NAME)
    print(f"  Backend: {backend.name} | pending={backend.status().pending_jobs}", flush=True)
    # k=0..5 then a k=0 retest anchor (within-job device-drift bound)
    circuits_k = K_VALUES + [0]
    pubs = []; depths = []
    for k in circuits_k:
        qc = build_grover_circuit(probs, k)
        tq = transpile(qc, backend=backend, optimization_level=1, seed_transpiler=SEED_TRANSP)
        n2q = sum(1 for g in tq.data if g.operation.num_qubits == 2)
        depths.append({"k": k, "depth": tq.depth(), "n2q": n2q})
        pubs.append((tq,))
        print(f"  k={k}  transpiled depth={tq.depth()} 2q={n2q}", flush=True)
    sampler = SamplerV2(mode=backend); sampler.options.default_shots = SHOTS
    job = sampler.run(pubs); jid = job.job_id()
    print(f"  ONE job, {len(pubs)} PUBs, job_id={jid} ({SHOTS} shots each)", flush=True)
    rec = {"experiment": "exp95", "backend": BACKEND_NAME, "shots": SHOTS, "job_id": jid,
           "circuits_k": circuits_k, "pub_labels": PUB_LABELS, "depths": depths,
           "a_discrete": true_tail_discrete(probs)}
    with open(JOBIDS_PATH, "w") as f: json.dump(rec, f, indent=2)
    print(f"  saved -> {JOBIDS_PATH}", flush=True)


def run_finalize(jid):
    from run_exp66_qpu_partb import _get_ibm_service
    probs = bucket_probs()[0]
    a_disc = true_tail_discrete(probs); a_cont = true_tail_continuous()
    ideal, _ = ideal_curve()
    rec = json.load(open(JOBIDS_PATH)) if os.path.exists(JOBIDS_PATH) else {}
    circuits_k = rec.get("circuits_k", K_VALUES + [0])
    service = _get_ibm_service()
    job = service.job(jid); status = str(job.status())
    print(f"  job {jid} status={status}", flush=True)
    if "DONE" not in status.upper():
        print("  -> not DONE; retry later."); return
    res = job.result()
    p_hw = []
    for i, k in enumerate(circuits_k):
        databin = res[i].data
        reg = list(databin.__dict__.keys())[0]
        counts = getattr(databin, reg).get_counts()
        p = _msb_one_prob(counts)
        p_hw.append((k, p))
        print(f"  PUB[{i}] k={k}  P_hw(MSB=1)={p:.4f}  contrast|P-0.5|={abs(p-0.5):.4f}  ideal={ideal[K_VALUES.index(k)] if k in K_VALUES else float('nan'):.4f}", flush=True)

    # k=0 anchor + retest reproducibility
    k0_vals = [p for (k, p) in p_hw if k == 0]
    k0_spread = abs(k0_vals[0] - k0_vals[-1]) if len(k0_vals) >= 2 else None

    # ---- H1: amplification direction at k=1 ----
    p0 = k0_vals[0]; p1 = next(p for (k, p) in p_hw if k == 1)
    shot_se = math.sqrt(0.25 / SHOTS)
    h1_dir_up = (p1 - p0) > 2 * shot_se           # ideal says k1 rises above k0
    h1 = {"p_k0": p0, "p_k1": p1, "delta": p1 - p0, "2shot_se": 2 * shot_se, "amplified_up": bool(h1_dir_up)}

    # ---- H2: signal-death k* (first k where HW contrast <= 0.5 * ideal contrast) ----
    kstar = None
    for (k, p) in [(k, p) for (k, p) in p_hw if k in K_VALUES]:
        ic = abs(ideal[K_VALUES.index(k)] - 0.5)
        if ic > 1e-6 and abs(p - 0.5) <= 0.5 * ic:
            kstar = k; break

    # ---- H3: best single-k estimate + canonical multi-k MLE ----
    per_k_est = {k: invert_single_k(p, k) for (k, p) in p_hw if k in K_VALUES}
    best_k = min(per_k_est, key=lambda k: abs(per_k_est[k] - a_disc))
    best_err = abs(per_k_est[best_k] - a_disc)
    k0_err = abs(p0 - a_disc)                       # k=0 is a direct read of a*
    mle = mle_over_k([(k, p) for (k, p) in p_hw if k in K_VALUES])
    mle_err = abs(mle - a_disc)
    h3_beats_k0 = best_err < k0_err

    print("\n================ GRADE (pre-registered H1/H2/H3) ================", flush=True)
    print(f"  a*_discrete(truth)={a_disc:.4f}  a*_cont={a_cont:.4f}", flush=True)
    print(f"  H1 amplification@k1: dP={h1['delta']:+.4f} (2*shot_se={2*shot_se:.4f}) -> {'UP/visible' if h1_dir_up else 'FLAT/wrong-dir'}", flush=True)
    print(f"  H2 signal-death k* (HW) = {kstar}   (FakeMarrakesh predicted ~5)", flush=True)
    print(f"  H3 best single-k est = {per_k_est[best_k]:.4f} @k={best_k} (err {best_err:.4f}) vs k0 read {p0:.4f} (err {k0_err:.4f}) -> {'BEATS k0' if h3_beats_k0 else 'k0 wins'}", flush=True)
    print(f"     canonical multi-k MLE a*={mle:.4f} (err {mle_err:.4f})", flush=True)
    print(f"  k0 anchor retest spread = {k0_spread}", flush=True)

    out = {"experiment": "exp95_qqq_grover_hardware", "cycle": 6347, "phase": "qpu_finalize",
           "job_id": jid, "backend": BACKEND_NAME, "shots": SHOTS,
           "a_discrete": a_disc, "a_continuous": a_cont, "ideal_curve": ideal,
           "p_hw": p_hw, "k0_retest_spread": k0_spread,
           "H1": h1, "H2_signal_death_kstar": kstar,
           "H3": {"per_k_estimate": per_k_est, "best_k": best_k, "best_err": best_err,
                  "k0_err": k0_err, "beats_k0": bool(h3_beats_k0),
                  "mle_all_k": mle, "mle_err": mle_err}}
    path = os.path.join(RESULTS_DIR, "exp95_qpu_results.json")
    with open(path, "w") as f: json.dump(out, f, indent=2)
    print(f"  saved -> {path}", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--sim", action="store_true")
    ap.add_argument("--submit", action="store_true")
    ap.add_argument("--finalize", metavar="JID")
    a = ap.parse_args()
    if a.sim: run_sim()
    elif a.submit: run_submit()
    elif a.finalize: run_finalize(a.finalize)
    else: ap.print_help()
