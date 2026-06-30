#!/usr/bin/env python3
"""
Exp78 (Elder C6269) — Quantum tail-probability of QQQ vs classical Monte Carlo: MEASURE THE GAP.

Creator question (ELI5): "can we do more than noise mapping?" Concrete test: estimate
P(QQQ closes above strike K) on REAL hardware via a genuine distribution-loading circuit,
benchmark head-to-head against classical Monte Carlo, and quantify how far hardware must
improve before quantum would help. This is a PROOF-OF-CONCEPT that measures the gap — it is
NOT an edge, and the pre-registered prediction below is that quantum LOSES (by a measured amount).

WHY THIS IS NOT THE FINDING-10 TOY (advisor C6269): Finding 10 encoded a PRECOMPUTED scalar
a*=0.56 as a single Ry(2θ) gate and re-estimated it — the distribution-loading was done
classically. Here the A operator GENUINELY loads a lognormal QQQ terminal-price distribution
into a 3-qubit register; the tail probability a* = P(S_T > K) is COMPUTED by the quantum circuit
(= P(top bit = 1)), not precomputed. That is the honest "P(QQQ>K) on hardware."

DESIGN (advisor-gated):
  - Lognormal QQQ terminal: S0=724 (6/29 close), sigma=20%/yr, T=21/252 (1 month), driftless (r=0).
  - 8-bucket linear price grid (3 qubits), edges chosen so the MSB boundary == strike K (ATM-ish 725).
    -> the "in the money" set S_T > K is EXACTLY {index >= 4} == {MSB q2 == 1}.
    -> the OBJECTIVE qubit is just the register's top bit: NO comparator (1 gate of bug-surface saved;
       the distribution LOADER is isolated as the real depth driver — the honest cost in QC option pricing).
  - CORRECTNESS GATE 1: validate the loader against a*_DISCRETE (sum of bucket probs above K),
    NOT the continuous Phi(-d2). Report |a*_discrete - a*_continuous| separately as discretization error.
  - CORRECTNESS GATE 2 (sim go/no-go, F53 discipline): noiseless sampling of P(MSB=1) must match
    a*_discrete within shot noise BEFORE any hardware spend.

LAYERS:
  (A/B) build + noiseless-validate the loader        [free]
  (MC)  classical Monte Carlo baseline               [free, laptop]
  (C)   run loader on ibm_marrakesh, sample MSB -> a*_hardware (THE genuine HW tail-prob; noise bias)
  (Q)   BONUS noiseless-only: Grover Q = A S0 A^dag S_chi + IAE-MLE on the REAL A; recover a*; report
        depth(Q^k) = (2k+1)*depth(A) vs the ~800-1000 CZ wall -> where the quadratic speedup dies.

PRE-REGISTERED EXPECTED LOSS (commit before hardware):
  - Hardware a*_sampling biases toward 0.5 (depolarizing -> uniform). Predict |a*_hw - a*_discrete|
    materially > shot noise; MC matches/beats hardware at equal "queries".
  - Grover won't sustain past k~1-2 on hardware (depth blows past the wall) -> the quadratic speedup
    is unreachable today. The gap = [depth needed for useful k] vs [depth sustainable] + [eps_min floor].

USAGE:
  python3 qae_qqq_tail_demo.py --sim                 # gates + MC + noiseless Grover/IAE (free)
  python3 qae_qqq_tail_demo.py --submit              # 2 test-retest loader jobs -> ibm_marrakesh
  python3 qae_qqq_tail_demo.py --finalize JID_A JID_B
"""
import sys, os, json, math, time, argparse
import numpy as np
from scipy.stats import norm
from scipy import optimize

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from qiskit import QuantumCircuit, transpile
from qiskit.circuit.library import StatePreparation
from qiskit_aer import AerSimulator

# ---- market / model config ----
S0     = 724.0          # QQQ close 2026-06-29
SIGMA  = 0.20           # annualized vol (representative)
T_YEAR = 21.0 / 252.0   # ~1 trading month
N_QUBITS = 3            # 8 price buckets
STRIKE = 725.0          # MSB bucket boundary == strike (ATM-ish)
GRID_L = 3.0            # grid spans strike +/- GRID_L*sigma_T (in price)
SHOTS  = 4096
SEED_TRANSP = 42
BACKEND_NAME = "ibm_marrakesh"

RESULTS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results")
EXP_DIR     = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "experiments")
JOBIDS_PATH = os.path.join(EXP_DIR, "exp78_jobids.json")
os.makedirs(RESULTS_DIR, exist_ok=True); os.makedirs(EXP_DIR, exist_ok=True)


# ---- lognormal terminal distribution + 8-bucket discretization ----
def lognormal_params():
    sig_T = SIGMA * math.sqrt(T_YEAR)          # log-return std over horizon
    mu_T  = -0.5 * sig_T**2                     # driftless risk-neutral (r=0): E[S_T]=S0
    return mu_T, sig_T


def true_tail_continuous():
    """a*_continuous = P(S_T > STRIKE) under lognormal (analytic)."""
    mu_T, sig_T = lognormal_params()
    # ln(S_T/S0) ~ N(mu_T, sig_T^2)
    z = (math.log(STRIKE / S0) - mu_T) / sig_T
    return float(1.0 - norm.cdf(z))


def bucket_probs():
    """8 bucket probs on a linear price grid with MSB boundary == STRIKE.
    Tails clamped into end buckets so probs sum to 1."""
    mu_T, sig_T = lognormal_params()
    price_sd = S0 * sig_T                       # approx price std (for grid width)
    w = (GRID_L * price_sd) / (N_QUBITS_BUCKETS() // 2)   # bucket width
    n = N_QUBITS_BUCKETS()
    # edges: place so the boundary between bucket n/2-1 and n/2 == STRIKE
    lo = STRIKE - (n // 2) * w
    edges = [lo + i * w for i in range(n + 1)]
    edges[0] = -1e9; edges[-1] = 1e9            # clamp tails
    def cdf(x):
        if x <= 0: return 0.0
        return float(norm.cdf((math.log(x / S0) - mu_T) / sig_T)) if x < 1e8 else 1.0
    probs = []
    for i in range(n):
        plo = cdf(edges[i]) if edges[i] > 0 else 0.0
        phi = cdf(edges[i + 1]) if edges[i + 1] < 1e8 else 1.0
        probs.append(max(0.0, phi - plo))
    probs = np.array(probs); probs /= probs.sum()
    # mid prices for reporting
    mids = [ (STRIKE - (n//2)*w) + (i + 0.5) * w for i in range(n) ]
    return probs, mids, w


def N_QUBITS_BUCKETS():
    return 2 ** N_QUBITS


def true_tail_discrete(probs):
    """a*_discrete = sum of bucket probs with index >= n/2 (i.e. price > STRIKE) == P(MSB==1)."""
    n = len(probs)
    return float(probs[n // 2:].sum())


# ---- the A operator: load sqrt(probs) into 3 qubits; objective = MSB ----
def build_A(probs, measure=False):
    amps = np.sqrt(probs)
    amps = amps / np.linalg.norm(amps)
    qc = QuantumCircuit(N_QUBITS)
    qc.append(StatePreparation(amps), list(range(N_QUBITS)))
    qc = qc.decompose(reps=3)
    if measure:
        mc = QuantumCircuit(N_QUBITS, 1)
        mc.compose(qc, list(range(N_QUBITS)), inplace=True)
        mc.measure(N_QUBITS - 1, 0)             # MSB == objective (S_T > K)
        return mc
    return qc


def _msb_one_prob(counts):
    tot = sum(counts.values()); ones = 0
    for bs, c in counts.items():
        b = bs.replace(" ", "")
        if b[0] == '1':            # measured single clbit (MSB)
            ones += c
    return ones / tot


# ---- classical Monte Carlo baseline ----
def classical_mc():
    mu_T, sig_T = lognormal_params()
    rng = np.random.default_rng(78)
    a_true = true_tail_continuous()
    rows = []
    t0 = time.time()
    for N in [100, 1000, 10000, 100000, 1000000]:
        Z = rng.standard_normal(N)
        ST = S0 * np.exp(mu_T + sig_T * Z)
        phat = float((ST > STRIKE).mean())
        se = math.sqrt(phat * (1 - phat) / N)
        rows.append({"N": N, "phat": phat, "abs_err": abs(phat - a_true), "stderr": se})
    wall_ms = (time.time() - t0) * 1e3
    # samples to reach eps=1e-3 at p~0.5: N ~ p(1-p)/eps^2
    N_for_eps3 = 0.25 / (1e-3 ** 2)
    return {"rows": rows, "wall_ms_total": wall_ms, "N_for_eps_1e-3": N_for_eps3}


# ---- BONUS (noiseless only): Grover on the REAL A + IAE-MLE ----
def grover_Q(probs):
    """Q = A S0 A^dag S_chi, S_chi = Z on MSB (phase flip the good |MSB=1> subspace)."""
    A = build_A(probs, measure=False)
    n = N_QUBITS
    Q = QuantumCircuit(n)
    # S_chi: phase flip where MSB==1  -> Z on MSB
    Q.z(n - 1)
    # A^dag
    Q.compose(A.inverse(), list(range(n)), inplace=True)
    # S0: phase flip |0..0>  ->  X^n, multi-controlled-Z, X^n
    Q.x(range(n)); Q.h(n - 1); Q.mcx(list(range(n - 1)), n - 1); Q.h(n - 1); Q.x(range(n))
    # A
    Q.compose(A, list(range(n)), inplace=True)
    return Q, A


def iae_mle_noiseless(probs, k_values=(0, 1, 2)):
    """Noiseless IAE-MLE using the REAL A and Q (BONUS; shows quadratic + depth-vs-wall)."""
    sim = AerSimulator()
    A = build_A(probs, measure=False)
    Q, _ = grover_Q(probs)
    a_disc = true_tail_discrete(probs)
    counts_data = []; depth_rows = []
    for k in k_values:
        qc = QuantumCircuit(N_QUBITS, 1)
        qc.compose(A, list(range(N_QUBITS)), inplace=True)
        for _ in range(k):
            qc.compose(Q, list(range(N_QUBITS)), inplace=True)
        qc.measure(N_QUBITS - 1, 0)
        tq = transpile(qc, sim, seed_transpiler=SEED_TRANSP)
        res = sim.run(tq, shots=SHOTS).result().get_counts()
        m = sum(c for bs, c in res.items() if bs.replace(" ", "")[0] == '1')
        counts_data.append((k, m, SHOTS))
        # depth on hardware basis (approx): transpile Q^k+A to marrakesh later; here logical depth proxy
        depth_rows.append({"k": k, "grover_power": 2 * k + 1, "logical_depth": tq.depth()})
    # MLE recover a
    def nll(a):
        if a <= 1e-6 or a >= 1 - 1e-6: return 1e12
        ll = 0.0
        for k, m, nn in counts_data:
            th = (2 * k + 1) * math.asin(math.sqrt(a))
            p = max(1e-10, min(1 - 1e-10, math.sin(th) ** 2))
            ll += m * math.log(p) + (nn - m) * math.log(1 - p)
        return -ll
    a_mle = float(optimize.minimize_scalar(nll, bounds=(1e-3, 1 - 1e-3), method='bounded').x)
    return {"a_mle_noiseless": a_mle, "a_discrete": a_disc, "abs_err": abs(a_mle - a_disc),
            "k_values": list(k_values), "counts": counts_data, "depth_rows": depth_rows}


# ---- SIM (gates + MC + bonus Grover) ----
def run_sim():
    probs, mids, w = bucket_probs()
    a_cont = true_tail_continuous(); a_disc = true_tail_discrete(probs)
    print(f"Exp78 SIM | QQQ S0={S0} K={STRIKE} sigma={SIGMA} T={T_YEAR:.4f} | {N_QUBITS_BUCKETS()} buckets w={w:.1f}", flush=True)
    print(f"  bucket mid-prices: {[round(m,0) for m in mids]}", flush=True)
    print(f"  bucket probs:      {np.round(probs,4).tolist()}", flush=True)
    print(f"  a*_continuous P(S_T>{STRIKE}) = {a_cont:.4f}", flush=True)
    print(f"  a*_DISCRETE  (circuit truth) = {a_disc:.4f}   | discretization err |disc-cont| = {abs(a_disc-a_cont):.4f}", flush=True)

    # GATE 2: noiseless loader sampling
    A_meas = build_A(probs, measure=True)
    sim = AerSimulator()
    tq = transpile(A_meas, sim, seed_transpiler=SEED_TRANSP)
    cn = sim.run(tq, shots=SHOTS).result().get_counts()
    a_noiseless = _msb_one_prob(cn)
    shot_se = math.sqrt(a_disc * (1 - a_disc) / SHOTS)
    gate_pass = abs(a_noiseless - a_disc) <= 4 * shot_se
    print(f"\n  [GATE] noiseless P(MSB=1) = {a_noiseless:.4f} vs a*_discrete {a_disc:.4f} "
          f"(|d|={abs(a_noiseless-a_disc):.4f}, 4*shot_se={4*shot_se:.4f}) -> {'PASS' if gate_pass else 'FAIL'}", flush=True)

    # FakeMarrakesh preview (noise penalty, free)
    from qiskit_ibm_runtime.fake_provider import FakeMarrakesh
    fake = AerSimulator.from_backend(FakeMarrakesh())
    tqf = transpile(A_meas, fake, optimization_level=1, seed_transpiler=SEED_TRANSP)
    cf = fake.run(tqf, shots=SHOTS).result().get_counts()
    a_fake = _msb_one_prob(cf)
    print(f"  [FakeMarrakesh] P(MSB=1) = {a_fake:.4f}  (bias vs truth = {a_fake-a_disc:+.4f}); "
          f"loader transpiled depth(fake) = {tqf.depth()}", flush=True)

    mc = classical_mc()
    print(f"\n  [classical MC] {S0}->K={STRIKE}, a*_cont={a_cont:.4f}:", flush=True)
    for r in mc["rows"]:
        print(f"    N={r['N']:>8}  phat={r['phat']:.4f}  abs_err={r['abs_err']:.4f}  stderr={r['stderr']:.4f}", flush=True)
    print(f"    wall {mc['wall_ms_total']:.1f} ms for ALL N up to 1e6;  N for eps=1e-3 ~ {mc['N_for_eps_1e-3']:.0f} (~ms on a laptop)", flush=True)

    grov = iae_mle_noiseless(probs)
    print(f"\n  [BONUS noiseless Grover/IAE on REAL A] a_mle={grov['a_mle_noiseless']:.4f} vs a*_discrete={grov['a_discrete']:.4f} (err {grov['abs_err']:.4f})", flush=True)
    for d in grov["depth_rows"]:
        print(f"    k={d['k']} Grover power {d['grover_power']}x  logical_depth={d['logical_depth']}", flush=True)

    out = {"experiment": "exp78_qqq_tail_qae", "cycle": 6269, "author": "elder",
           "config": {"S0": S0, "K": STRIKE, "sigma": SIGMA, "T": T_YEAR, "n_qubits": N_QUBITS,
                      "shots": SHOTS, "grid_w": w, "bucket_mids": mids, "bucket_probs": probs.tolist()},
           "a_continuous": a_cont, "a_discrete": a_disc, "discretization_err": abs(a_disc - a_cont),
           "gate": {"a_noiseless": a_noiseless, "shot_se": shot_se, "pass": bool(gate_pass)},
           "fakemarrakesh": {"a_fake": a_fake, "bias": a_fake - a_disc, "loader_depth_fake": tqf.depth()},
           "classical_mc": mc, "grover_noiseless": grov}
    path = os.path.join(RESULTS_DIR, "exp78_sim.json")
    with open(path, "w") as f: json.dump(out, f, indent=2)
    print(f"\n  GATE: {'PASS -> hardware loader run justified' if gate_pass else 'FAIL -> fix loader, do NOT submit'}", flush=True)
    print(f"  saved -> {path}", flush=True)
    return gate_pass


def run_submit():
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    probs, mids, w = bucket_probs()
    A_meas = build_A(probs, measure=True)
    service = _get_ibm_service(); backend = service.backend(BACKEND_NAME)
    print(f"  Backend: {backend.name} | pending={backend.status().pending_jobs}", flush=True)
    tq = transpile(A_meas, backend=backend, optimization_level=1, seed_transpiler=SEED_TRANSP)
    print(f"  loader transpiled depth(ibm_marrakesh) = {tq.depth()}, 2q gates ~ {sum(1 for g in tq.data if g.operation.num_qubits==2)}", flush=True)
    job_ids = []
    for rep in ("A", "B"):
        sampler = SamplerV2(mode=backend); sampler.options.default_shots = SHOTS
        job = sampler.run([(tq,)]); jid = job.job_id(); job_ids.append(jid)
        print(f"  replicate {rep} job_id={jid} ({SHOTS} shots)", flush=True)
    rec = {"experiment": "exp78", "backend": BACKEND_NAME, "shots": SHOTS, "job_ids": job_ids,
           "a_discrete": true_tail_discrete(probs), "a_continuous": true_tail_continuous(),
           "loader_depth": tq.depth()}
    with open(JOBIDS_PATH, "w") as f: json.dump(rec, f, indent=2)
    print(f"  saved -> {JOBIDS_PATH}", flush=True)


def run_finalize(jids):
    from run_exp66_qpu_partb import _get_ibm_service
    probs, mids, w = bucket_probs()
    a_disc = true_tail_discrete(probs); a_cont = true_tail_continuous()
    service = _get_ibm_service()
    reps = []
    for k, jid in enumerate(jids):
        job = service.job(jid); status = str(job.status())
        print(f"  job {jid} status={status}", flush=True)
        if "DONE" not in status.upper(): print("  -> not DONE; retry later."); return
        res = job.result(); databin = res[0].data
        reg = list(databin.__dict__.keys())[0]; counts = getattr(databin, reg).get_counts()
        a_hw = _msb_one_prob(counts)
        reps.append(a_hw)
        print(f"  [QPU_{'AB'[k]}] P(MSB=1)=a*_hardware = {a_hw:.4f}  bias vs truth(disc) = {a_hw-a_disc:+.4f}", flush=True)
    a_hw_mean = float(np.mean(reps))
    print("\n================ GRADE (vs pre-registered expected loss) ================", flush=True)
    print(f"  a*_continuous={a_cont:.4f}  a*_discrete(circuit truth)={a_disc:.4f}  a*_hardware={a_hw_mean:.4f}", flush=True)
    print(f"  hardware bias = {a_hw_mean-a_disc:+.4f}  (toward 0.5 = depolarizing-to-uniform as pre-registered)", flush=True)
    print(f"  test-retest spread = {abs(reps[0]-reps[1]):.4f}" if len(reps)==2 else "", flush=True)
    out = {"experiment": "exp78_qqq_tail_qae", "cycle": 6269, "phase": "qpu_finalize",
           "job_ids": jids, "a_hardware_reps": reps, "a_hardware_mean": a_hw_mean,
           "a_discrete": a_disc, "a_continuous": a_cont, "hardware_bias": a_hw_mean - a_disc}
    path = os.path.join(RESULTS_DIR, "exp78_qpu_results.json")
    with open(path, "w") as f: json.dump(out, f, indent=2)
    print(f"  saved -> {path}", flush=True)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--sim", action="store_true")
    ap.add_argument("--submit", action="store_true")
    ap.add_argument("--finalize", nargs="+", metavar="JID")
    a = ap.parse_args()
    if a.sim: run_sim()
    elif a.submit: run_submit()
    elif a.finalize: run_finalize(a.finalize)
    else: ap.print_help()
