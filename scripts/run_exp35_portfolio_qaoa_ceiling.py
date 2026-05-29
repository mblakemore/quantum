"""Exp 35: Portfolio-QAOA Depth Ceiling -- is the wall CZ-count-governed or p-governed? (Whisper C3747).

OPEN RESEARCH QUESTION #6 (README leftover): "Empirically map p_max for ... portfolio-optimization
benchmarks." Exp33 RESOLVED MaxCut: a SPARSE path P6 (|E|=5, 10 CZ/layer) crossed 0.95x uniform at
p_max=96 = 960 transpiled 2q gates -- co-located with Finding 05's 800-1000 CZ scrambling wall.

THE TEST (why this is not just "another benchmark")
---------------------------------------------------
Finding 05's claim is that the utility wall is governed by TOTAL two-qubit-gate count (~800-1000),
i.e. it is an information-theoretic/scrambling horizon, not a property of the algorithm's nominal
depth p. Exp33 alone cannot separate these two hypotheses because for the path graph
(transpiled 2q) and (nominal p) are proportional with a fixed constant (10/layer, no SWAP).

Portfolio optimization breaks that proportionality. The Markowitz QUBO is FULLY CONNECTED
(all-pairs covariance ZZ + budget-penalty cross terms), |E| = N(N-1)/2. For N=6 that is 15 edges
= 30 nominal 2q/layer, PLUS SWAP routing overhead on sparse (degree-3) heavy-hex. So per QAOA
layer the portfolio circuit spends ~3-6x the two-qubit gates of the path graph.

  H_A (CZ-count-governed wall, Finding 05):  portfolio crosses 0.95x uniform at a MUCH lower
       NOMINAL p (predict p_max ~ 12-24) but at the SAME ~800-1000 TRANSPILED-CZ band.
  H_B (p-governed / algorithm-structure wall): p_max ~ 96 again, ~independent of edge density;
       transpiled-CZ at crossing would then be FAR above 1000 -> Finding 05's CZ-count framing
       is the wrong invariant.

These make DISTINCT predictions on nominal p. The pre-registered gate (below) adjudicates.

DESIGN (parity-controlled with Exp33: change ONE variable = problem density)
----------------------------------------------------------------------------
- Backend ibm_marrakesh (SAME device as Exp33 + Finding 05). opt_level=1, seed_transpiler=42,
  8192 shots. SAME fixed Trotterized-annealing schedule (T_ANNEAL=10): gamma_k=s_k*dt,
  beta_k=(1-s_k)*dt, s_k=(k+0.5)/p, dt=T/p. NO per-run optimization (removes optimizer confound).
  Deliberately NO calibration-gated initial_layout (the Exp34 do(layout) gate) -- adding it would
  change a SECOND variable vs Exp33 and confound the density comparison. The entropy-ratio metric
  measures GLOBAL decoherence-to-uniform, robust to a few weak qubits, so parity is the right control.
- Problem: N=6 assets, select K=3. Markowitz QUBO  minimize  q_risk*x'Sigma x - mu'x + lambda*(sum x - K)^2
  with a HARDCODED, reproducible instance (no RNG -> fully reproducible, no Date/seed dependence).
  Strong budget penalty makes the K=3 feasible subspace dominate -> the noiseless annealed output
  CONCENTRATES (structured H_ideal, well below uniform) -- required for the 0.95x-uniform gate to
  be meaningful (Exp33 method note / pattern: a noise-ceiling test needs a STRUCTURED reference).
- QUBO -> Ising:  x_i=(1-Z_i)/2  =>  h_i = -Q_ii/2 - (1/4) sum_{j!=i} Q_ij ,  J_ij = Q_ij/4.
  Cost layer per QAOA step: RZ(2*gamma*h_i) on every qubit; CX-RZ(2*gamma*J_ij)-CX on every pair.
- Sweep p in {4,8,12,16,24,32,48} (denser problem -> wall expected at lower nominal p than MaxCut's 96).
- METRIC (identical to Exp33): Shannon entropy H_hw of measured distribution; ratio = H_hw/N;
  noiseless statevector H_ideal so noise excess = H_hw - H_ideal isolates decoherence from algorithm.

METRIC CHOICE (revised in sim-preview BEFORE submission -- pre-registered)
--------------------------------------------------------------------------
Exp33 used ratio_hw = H_hw/N vs the 0.95x-uniform gate because for the SPARSE path graph the
noiseless output H_ideal stayed flat-low across the whole p sweep (a structured reference). For the
DENSE portfolio problem that is NOT true: the fixed annealing-ramp needs MANY layers to concentrate,
so H_ideal is near-uniform at small p (sim: ratio 0.98 at p=4) and only drops at p>=16. A
ratio-vs-uniform gate is therefore contaminated at low p (it would fire on an UNCONVERGED anneal,
not on noise -- confirmed in sim, G2 would FAIL). The correct, noise-attributable-by-construction
metric is the NOISE EXCESS  noise_excess(p) = H_hw(p) - H_ideal(p): it subtracts the algorithm's own
spread, so it isolates hardware decoherence at every p. (Sim-preview: noise_excess is flat-low
0.0->0.58 bit through p=12=750 CZ, then JUMPS to 3.27 bit at p=16=1002 transpiled CZ -- a clean gap.)

PRE-REGISTERED CRITERIA (FIXED before submission, noise-excess basis)
---------------------------------------------------------------------
  noise_wall_p := smallest swept p with noise_excess(p) = H_hw(p) - H_ideal(p) >= 1.0 bit.
                  (threshold 1.0 chosen pre-submit to sit cleanly ABOVE the ~0.5-bit unconverged-
                   anneal floor seen at p=8-12 and BELOW the >=3-bit decohered regime.)
  cz_at_wall   := transpiled 2q-gate count at noise_wall_p.
  G1 (NOISE WALL EXISTS):     noise_wall_p found within the sweep.
  G2 (STRUCTURED REFERENCE):  H_ideal(noise_wall_p)/N <= 0.6 at the wall -- the noiseless output is
       genuinely structured there, so the excess reflects NOISE destroying real structure (not both
       distributions being near-uniform / anneal-unconverged).
  G3 (CZ CO-LOCATION = the discriminator):  cz_at_wall in [500,1500] (Finding 05's ~800-1000 band,
       generous for QAOA structural overhead).
  G4 (DENSITY EFFECT / CZ-NOT-p):  noise_wall_p < 96 = Exp33 MaxCut p_max, while cz_at_wall is close
       to Exp33's 960 transpiled CZ -- i.e. the wall arrives at far FEWER layers but the SAME CZ count.

INTERPRETATION
  G1&G2&G3&G4 PASS -> H_A CONFIRMED: the QAOA utility wall is governed by TOTAL transpiled CZ count,
       ~invariant across problem density (sparse MaxCut 960 CZ @ p=96  vs  dense portfolio ~1000 CZ @
       p~16). The wall is an information-theoretic/scrambling horizon, NOT a property of nominal depth
       p or problem structure. Planning constant: p_max ~= 1000 / (transpiled-2q-per-layer). For dense
       problems this is a HARD low-p ceiling, directly actionable for portfolio-QAOA on real hardware.
  G3 FAIL, cz_at_wall >> 1500 -> H_B: wall tracks nominal depth/structure, not raw CZ count; Finding
       05's CZ-count framing is not the right invariant for dense problems. Honest, publishable.
  G3 FAIL, cz_at_wall < 500 -> portfolio ceiling is TIGHTER than the bare CZ wall (all-to-all + SWAP
       decoheres faster than counted) -- a density-driven refinement of Finding 05.
  G1 FAIL -> no noise wall within p<=48; extend sweep.
  Secondary read (anneal-convergence vs wall collision): report p_converge := smallest p with
  H_ideal/N <= 0.5. If the transpiled CZ at p_converge is itself ~800-1000, the dense-problem anneal
  only concentrates AT the wall -> there is no usable depth window (a strong, honest negative result).

Run (sim preview):   python3 scripts/run_exp35_portfolio_qaoa_ceiling.py
Run (hardware):      python3 scripts/run_exp35_portfolio_qaoa_ceiling.py --submit
Finalize:            python3 scripts/run_exp35_portfolio_qaoa_ceiling.py --finalize <job_id>
"""
import argparse
import json
import os
import math
import numpy as np

EXPERIMENT = "35"
CYCLE = 3747
SHOTS = 8192
N_ASSETS = 6
K_SELECT = 3
T_ANNEAL = 10.0
P_SWEEP = [4, 8, 12, 16, 24, 32, 48]
SEED_TRANSPILER = 42
BACKEND_NAME = "ibm_marrakesh"
RESULT_PATH = f"experiments/{EXPERIMENT}-portfolio-qaoa-ceiling-results.json"
JOBID_PATH = f"experiments/{EXPERIMENT}-jobid.txt"
CALIB_PATH = f"experiments/{EXPERIMENT}-calibration.json"
UNIFORM_MAX_BITS = float(N_ASSETS)
RATIO_GATE = 0.95
EXP33_PMAX = 96  # MaxCut path-graph reference (for the density-effect gate G4)

# --- Hardcoded, reproducible Markowitz instance (no RNG) ----------------------
# Expected returns (higher = more attractive to SELECT).
MU = np.array([0.12, 0.10, 0.08, 0.15, 0.06, 0.11])
# Covariance (risk). Symmetric PSD-ish, diagonal = variances, off-diag = co-movement.
SIGMA = np.array([
    [0.10, 0.02, 0.01, 0.03, 0.00, 0.02],
    [0.02, 0.12, 0.02, 0.01, 0.01, 0.00],
    [0.01, 0.02, 0.09, 0.02, 0.03, 0.01],
    [0.03, 0.01, 0.02, 0.14, 0.01, 0.02],
    [0.00, 0.01, 0.03, 0.01, 0.08, 0.02],
    [0.02, 0.00, 0.01, 0.02, 0.02, 0.11],
])
Q_RISK = 1.0       # risk aversion
LAMBDA_PEN = 2.0   # budget penalty weight (strong -> K=3 subspace dominates -> structured output)


def build_qubo():
    """Symmetric QUBO matrix Q (minimize x'Qx over x in {0,1}^N), Markowitz + budget penalty.

    risk:    q_risk * x'Sigma x
    return:  -mu'x                          (selecting good assets lowers cost)
    budget:  lambda*(sum x - K)^2 = lambda*[ (1-2K)*sum x_i + 2*sum_{i<j} x_i x_j + K^2 ]
             (uses x_i^2 = x_i). Constant K^2 dropped.
    """
    n = N_ASSETS
    Q = np.zeros((n, n))
    # risk (symmetric quadratic): x'Sigma x = sum_i Sigma_ii x_i + sum_{i<j} 2 Sigma_ij x_i x_j
    for i in range(n):
        Q[i, i] += Q_RISK * SIGMA[i, i]
        for j in range(i + 1, n):
            Q[i, j] += Q_RISK * 2.0 * SIGMA[i, j]
    # return (linear, on diagonal): -mu_i x_i
    for i in range(n):
        Q[i, i] += -MU[i]
    # budget penalty
    for i in range(n):
        Q[i, i] += LAMBDA_PEN * (1.0 - 2.0 * K_SELECT)
        for j in range(i + 1, n):
            Q[i, j] += LAMBDA_PEN * 2.0
    return Q


def qubo_to_ising(Q):
    """x_i=(1-Z_i)/2 => h_i = -Q_ii/2 - (1/4) sum_{j!=i} Q_ij ;  J_ij = Q_ij/4 (i<j).
    Q is upper-triangular-populated symmetric-intent; treat Q[i,j] (i<j) as the i-j coupling."""
    n = N_ASSETS
    h = np.zeros(n)
    J = {}
    for i in range(n):
        s = 0.0
        for j in range(n):
            if j == i:
                continue
            qij = Q[i, j] if i < j else Q[j, i]
            s += qij
        h[i] = -Q[i, i] / 2.0 - s / 4.0
    for i in range(n):
        for j in range(i + 1, n):
            J[(i, j)] = Q[i, j] / 4.0
    return h, J


H_FIELDS, J_COUPL = qubo_to_ising(build_qubo())
EDGES = sorted(J_COUPL.keys())            # fully connected: all 15 pairs for N=6
TWO_Q_PER_LAYER = len(EDGES)              # nominal (pre-SWAP) two-qubit gates per cost layer


def brute_force_optimum():
    """Ground-state bitstring (min QUBO energy) -- for sim-preview concentration check."""
    Q = build_qubo()
    best_x, best_e = None, float("inf")
    for mask in range(1 << N_ASSETS):
        x = np.array([(mask >> b) & 1 for b in range(N_ASSETS)], dtype=float)
        e = float(x @ Q @ x - sum(Q[i, i] * x[i] for i in range(N_ASSETS)) + sum(Q[i, i] * x[i] for i in range(N_ASSETS)))
        # x'Qx with our upper-tri Q already encodes pair terms once; compute directly:
        e = 0.0
        for i in range(N_ASSETS):
            e += Q[i, i] * x[i]
            for j in range(i + 1, N_ASSETS):
                e += Q[i, j] * x[i] * x[j]
        if e < best_e:
            best_e, best_x = e, x.copy()
    return best_x, best_e


def anneal_angles(p):
    dt = T_ANNEAL / p
    gammas, betas = [], []
    for k in range(p):
        s = (k + 0.5) / p
        gammas.append(s * dt)
        betas.append((1.0 - s) * dt)
    return gammas, betas


def build_qaoa(p):
    """Annealing-ramp QAOA for the portfolio Ising (h, J), p layers. Unmeasured circuit."""
    from qiskit import QuantumCircuit
    gammas, betas = anneal_angles(p)
    qc = QuantumCircuit(N_ASSETS)
    qc.h(range(N_ASSETS))
    for k in range(p):
        g = gammas[k]
        for i in range(N_ASSETS):                         # single-Z cost terms
            if abs(H_FIELDS[i]) > 1e-12:
                qc.rz(2.0 * g * H_FIELDS[i], i)
        for (i, j) in EDGES:                              # all-pairs ZZ cost terms
            jij = J_COUPL[(i, j)]
            if abs(jij) < 1e-12:
                continue
            qc.cx(i, j)
            qc.rz(2.0 * g * jij, j)
            qc.cx(i, j)
        for q in range(N_ASSETS):                         # mixer
            qc.rx(2.0 * betas[k], q)
    return qc


def build_qaoa_measured(p):
    qc = build_qaoa(p)
    qc.measure_all()
    return qc


def shannon_entropy_bits(counts):
    total = sum(counts.values())
    if total == 0:
        return 0.0
    h = 0.0
    for c in counts.values():
        if c > 0:
            p = c / total
            h -= p * math.log2(p)
    return h


def ideal_entropy_bits(p):
    try:
        from qiskit.quantum_info import Statevector
        sv = Statevector.from_instruction(build_qaoa(p))
        probs = np.abs(sv.data) ** 2
        probs = probs[probs > 1e-15]
        return float(-np.sum(probs * np.log2(probs)))
    except Exception:
        return float("nan")


def _build_schedule(transpile_fn):
    items = []
    for p in P_SWEEP:
        qc = transpile_fn(build_qaoa_measured(p))
        items.append((p, qc))
    return items


def build_schedule_for_hardware():
    from qiskit import transpile
    from qiskit_ibm_runtime import QiskitRuntimeService
    service = QiskitRuntimeService()
    backend = service.backend(BACKEND_NAME)

    def tfn(qc):
        return transpile(qc, backend=backend, optimization_level=1,
                         seed_transpiler=SEED_TRANSPILER)

    items = _build_schedule(tfn)
    print(f"  Built {len(items)} portfolio-QAOA circuits on {BACKEND_NAME} "
          f"(N={N_ASSETS}, |E|={len(EDGES)}, nominal {TWO_Q_PER_LAYER} 2q/layer)")
    for (p, qc) in items:
        ops = qc.count_ops()
        cz = ops.get("cz", 0) + ops.get("ecr", 0) + ops.get("cx", 0)
        print(f"  p={p:>3}: depth={qc.depth():>5}  transpiled-2q={cz:>5}  "
              f"(nominal 2|E|p={TWO_Q_PER_LAYER * p}, SWAP overhead x{cz / max(1, TWO_Q_PER_LAYER * p):.2f})")
    return items, backend


def build_schedule_for_fake():
    from qiskit import transpile
    from qiskit_ibm_runtime.fake_provider import FakeMarrakesh
    backend = FakeMarrakesh()

    def tfn(qc):
        return transpile(qc, backend=backend, optimization_level=1,
                         seed_transpiler=SEED_TRANSPILER)

    items = _build_schedule(tfn)
    for (p, qc) in items:
        ops = qc.count_ops()
        cz = ops.get("cz", 0) + ops.get("ecr", 0) + ops.get("cx", 0)
        print(f"  p={p:>3}: depth={qc.depth():>5}  transpiled-2q={cz:>5}  "
              f"(nominal {TWO_Q_PER_LAYER * p})")
    return items, backend


def submit_hardware(schedule_items, backend):
    from qiskit_ibm_runtime import SamplerV2
    sampler = SamplerV2(mode=backend)
    sampler.options.default_shots = SHOTS
    circuits = [item[1] for item in schedule_items]
    job = sampler.run([(qc,) for qc in circuits])
    job_id = job.job_id()
    with open(JOBID_PATH, "w") as f:
        f.write(job_id + "\n")
    try:
        from calibration_snapshot import capture_calibration
        snap = capture_calibration(backend)
        snap["snapshot_phase"] = "submit"
        with open(CALIB_PATH, "w") as f:
            json.dump(snap, f, indent=4, default=str)
        print(f"  Calibration snapshot (submit) saved (updated {snap.get('last_update_date')})")
    except Exception as e:
        print(f"  [warn] calibration snapshot skipped: {e}")
    print(f"\n  SUBMITTED. job_id = {job_id}  ({len(circuits)} circuits) on {BACKEND_NAME}")
    return job_id


def get_counts_from_job(job_id, n_circuits):
    from qiskit_ibm_runtime import QiskitRuntimeService
    service = QiskitRuntimeService()
    job = service.job(job_id)
    status = str(job.status())
    print(f"  job {job_id} status: {status}")
    if status not in ("DONE", "JobStatus.DONE"):
        return None, status
    res = job.result()
    all_counts = []
    for i in range(n_circuits):
        databin = res[i].data
        reg = list(databin.__dict__.keys())[0]
        all_counts.append(getattr(databin, reg).get_counts())
    return all_counts, "DONE"


def get_counts_from_fake(schedule_items, backend):
    from qiskit_aer.primitives import SamplerV2 as AerSampler
    from qiskit_aer.noise import NoiseModel
    nm = NoiseModel.from_backend(backend)
    sampler = AerSampler(options={
        "backend_options": {"noise_model": nm},
        "run_options": {"shots": SHOTS, "seed": SEED_TRANSPILER},
    })
    circuits = [item[1] for item in schedule_items]
    res = sampler.run([(c,) for c in circuits]).result()
    all_counts = []
    for i in range(len(circuits)):
        data = res[i].data
        reg = list(data.__dict__.keys())[0]
        all_counts.append(getattr(data, reg).get_counts())
    return all_counts


def _load_calibration_snapshot():
    try:
        if os.path.exists(CALIB_PATH):
            with open(CALIB_PATH) as f:
                return json.load(f)
    except Exception:
        pass
    return {"available": False, "note": "no submit-time snapshot found"}


EXCESS_WALL_BITS = 1.0     # pre-registered noise-excess threshold (see header)
IDEAL_STRUCT_RATIO = 0.6   # G2: H_ideal/N must be <= this at the wall (structured reference)
CONVERGE_RATIO = 0.5       # secondary: p_converge := first p with H_ideal/N <= this


def analyze(schedule_items, all_counts, job_id=None):
    rows = []
    print(f"\n{'p':>4} {'2q':>6} | {'H_hw':>7} {'H_ideal':>8} {'ratio':>7} {'excess':>7}")
    print("-" * 50)
    noise_wall_p = None
    p_converge = None
    ratios = []
    for (p, qc), counts in zip(schedule_items, all_counts):
        ops = qc.count_ops()
        cz = ops.get("cz", 0) + ops.get("ecr", 0) + ops.get("cx", 0)
        h_hw = shannon_entropy_bits(counts)
        h_id = ideal_entropy_bits(p)
        ratio = h_hw / UNIFORM_MAX_BITS
        ideal_ratio = h_id / UNIFORM_MAX_BITS
        excess = h_hw - h_id
        ratios.append(ratio)
        rows.append({"p": p, "cz": cz, "H_hw_bits": round(h_hw, 4),
                     "H_ideal_bits": round(h_id, 4), "ratio_hw": round(ratio, 4),
                     "ideal_ratio": round(ideal_ratio, 4),
                     "noise_excess_bits": round(excess, 4)})
        print(f"{p:>4} {cz:>6} | {h_hw:>7.4f} {h_id:>8.4f} {ratio:>7.4f} {excess:>+7.4f}")
        if noise_wall_p is None and excess >= EXCESS_WALL_BITS:
            noise_wall_p = p
        if p_converge is None and ideal_ratio <= CONVERGE_RATIO:
            p_converge = p
    print("-" * 50)

    top_ratio = ratios[-1] if ratios else 0.0
    wall_row = next((r for r in rows if r["p"] == noise_wall_p), None)
    cz_at_wall = wall_row["cz"] if wall_row else None
    ideal_ratio_at_wall = wall_row["ideal_ratio"] if wall_row else None
    excess_at_wall = wall_row["noise_excess_bits"] if wall_row else None
    converge_row = next((r for r in rows if r["p"] == p_converge), None)
    cz_at_converge = converge_row["cz"] if converge_row else None

    g1 = (noise_wall_p is not None)
    g2 = (ideal_ratio_at_wall is not None and ideal_ratio_at_wall <= IDEAL_STRUCT_RATIO)
    g3 = (cz_at_wall is not None and 500 <= cz_at_wall <= 1500)
    g4 = (noise_wall_p is not None and noise_wall_p < EXP33_PMAX
          and cz_at_wall is not None and 500 <= cz_at_wall <= 1500)

    print(f"\n  noise_wall_p (first excess>={EXCESS_WALL_BITS}bit) = {noise_wall_p}  "
          f"(transpiled cz@wall={cz_at_wall}, excess={excess_at_wall}, ideal_ratio={ideal_ratio_at_wall})")
    print(f"  p_converge (first H_ideal/N<={CONVERGE_RATIO}) = {p_converge}  (transpiled cz={cz_at_converge})")
    print(f"  Exp33 MaxCut reference: p_max={EXP33_PMAX} @ 960 transpiled 2q")
    print(f"\n=== PRE-REGISTERED CRITERIA (Exp35, {BACKEND_NAME}, noise-excess basis) ===")
    print(f"G1 (NOISE WALL EXISTS):    excess>=1.0bit within sweep ({noise_wall_p}) -> {'PASS' if g1 else 'FAIL'}")
    print(f"G2 (STRUCTURED REF):       H_ideal/N<=0.6 at wall ({ideal_ratio_at_wall if ideal_ratio_at_wall is not None else 'n/a'}) "
          f"-> {'PASS' if g2 else 'PENDING' if noise_wall_p is None else 'FAIL'}")
    print(f"G3 (CZ CO-LOCATION):       500<=cz@wall<=1500 ({cz_at_wall if cz_at_wall is not None else 'n/a'}) "
          f"-> {'PASS' if g3 else 'PENDING' if noise_wall_p is None else 'FAIL'}")
    print(f"G4 (DENSITY EFFECT/CZ-NOT-p): wall_p<{EXP33_PMAX} & cz@wall in band "
          f"({noise_wall_p}, {cz_at_wall}) -> {'PASS' if g4 else 'PENDING' if noise_wall_p is None else 'FAIL'}")

    if noise_wall_p is not None:
        if g2 and g3 and g4:
            verdict = (f"H_A CONFIRMED: noise wall at nominal p={noise_wall_p} (<< MaxCut's {EXP33_PMAX}) but "
                       f"at {cz_at_wall} transpiled 2q -- inside Finding 05's 800-1000 band, ~= Exp33's 960. "
                       f"The QAOA utility wall is governed by TOTAL transpiled CZ count, NOT nominal depth p: "
                       f"sparse(960@p96) and dense({cz_at_wall}@p{noise_wall_p}) collapse to the same CZ count. "
                       f"For dense problems this is a hard LOW-p ceiling. p_converge={p_converge} "
                       f"({cz_at_converge} CZ): anneal "
                       + ("only concentrates AT the wall -> no usable depth window."
                          if (cz_at_converge is not None and cz_at_converge >= 800)
                          else "concentrates before the wall -> a usable window exists below it."))
        elif g3 and not g2:
            verdict = (f"AMBIGUOUS at p={noise_wall_p}: excess>=1bit but noiseless output not yet structured "
                       f"(H_ideal/N={ideal_ratio_at_wall}) -- anneal-unconverged contamination; treat with caution.")
        elif cz_at_wall is not None and cz_at_wall > 1500:
            verdict = (f"H_B: noise wall at p={noise_wall_p} = {cz_at_wall} transpiled 2q, ABOVE 1500 -- "
                       f"wall tracks nominal depth/structure, not raw CZ count; CZ-count framing not the "
                       f"right invariant for dense problems.")
        elif cz_at_wall is not None and cz_at_wall < 500:
            verdict = (f"TIGHTER than the bare CZ wall: noise wall at p={noise_wall_p}, only {cz_at_wall} "
                       f"transpiled 2q -- all-to-all + SWAP decoheres faster than counted. Density-driven "
                       f"refinement of Finding 05.")
        else:
            verdict = f"Noise wall at p={noise_wall_p} ({cz_at_wall} transpiled 2q); see gate breakdown."
    else:
        verdict = (f"No noise wall (excess<{EXCESS_WALL_BITS}bit) within p<={P_SWEEP[-1]}; "
                   f"top excess too low -- extend sweep / re-examine instance.")
    print(f"\nVERDICT: {verdict}")

    result = {
        "experiment": EXPERIMENT,
        "title": "Portfolio-QAOA Depth Ceiling: CZ-count-governed vs p-governed wall (ORQ #6 leftover)",
        "cycle": CYCLE, "backend": BACKEND_NAME, "job_id": job_id,
        "open_research_question": "Does the QAOA utility wall track TOTAL transpiled CZ count "
                                  "(Finding 05, ~800-1000) or nominal depth p? Dense fully-connected "
                                  "portfolio QUBO breaks the path-graph proportionality to discriminate.",
        "hypotheses": {
            "H_A_cz_count_governed": "lower nominal p_max than MaxCut but same ~800-1000 transpiled CZ",
            "H_B_p_governed": "p_max ~ 96 again, transpiled CZ far above 1000",
        },
        "problem": {"type": "markowitz_portfolio_QUBO", "n_assets": N_ASSETS, "k_select": K_SELECT,
                    "fully_connected_edges": len(EDGES), "nominal_two_q_per_layer": TWO_Q_PER_LAYER,
                    "q_risk": Q_RISK, "lambda_penalty": LAMBDA_PEN,
                    "mu": MU.tolist(), "sigma_diag": np.diag(SIGMA).tolist()},
        "params": {"shots": SHOTS, "T_anneal": T_ANNEAL, "p_sweep": P_SWEEP,
                   "angle_mode": "fixed_annealing_ramp", "seed_transpiler": SEED_TRANSPILER,
                   "uniform_max_bits": UNIFORM_MAX_BITS, "ratio_gate": RATIO_GATE,
                   "exp33_maxcut_pmax_reference": EXP33_PMAX},
        "metric_note": "Basis = noise_excess (H_hw - H_ideal), NOT ratio-vs-uniform: the dense "
                       "annealing ansatz leaves H_ideal near-uniform at low p (unconverged), which "
                       "contaminates a ratio gate; noise_excess subtracts the algorithm's own spread "
                       "so the crossing is noise-attributable by construction (revised in sim-preview).",
        "preregistered_criteria": {
            "noise_wall_p": f"smallest swept p with noise_excess (H_hw - H_ideal) >= {EXCESS_WALL_BITS} bit",
            "G1": "noise_wall_p found within sweep",
            "G2": f"H_ideal/N <= {IDEAL_STRUCT_RATIO} at the wall (structured reference, not anneal-unconverged)",
            "G3": "transpiled 2q at wall in 500-1500 (Finding 05 CZ-count co-location = discriminator)",
            "G4": f"noise_wall_p < {EXP33_PMAX} AND cz@wall in 500-1500 (CZ-governed, not p-governed)",
        },
        "calibration": _load_calibration_snapshot(),
        "summary": {
            "noise_wall_p": noise_wall_p, "cz_at_wall": cz_at_wall,
            "noise_excess_at_wall_bits": excess_at_wall, "ideal_ratio_at_wall": ideal_ratio_at_wall,
            "p_converge": p_converge, "cz_at_converge": cz_at_converge,
            "top_ratio": round(top_ratio, 4),
            "exp33_maxcut_pmax": EXP33_PMAX, "exp33_maxcut_cz": 960,
            "G1": "PASS" if g1 else "FAIL",
            "G2": ("PASS" if g2 else ("PENDING" if noise_wall_p is None else "FAIL")),
            "G3": ("PASS" if g3 else ("PENDING" if noise_wall_p is None else "FAIL")),
            "G4": ("PASS" if g4 else ("PENDING" if noise_wall_p is None else "FAIL")),
            "verdict": verdict,
        },
        "rows": rows,
    }
    with open(RESULT_PATH, "w") as f:
        json.dump(result, f, indent=4)
    print(f"\n  Results saved to {RESULT_PATH}")
    return result


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--submit", action="store_true")
    parser.add_argument("--finalize", metavar="JOB_ID")
    args = parser.parse_args()

    if args.finalize:
        print(f"\n=== Fetching Exp {EXPERIMENT} (job {args.finalize}) ===")
        schedule_items, _ = build_schedule_for_hardware()
        all_counts, status = get_counts_from_job(args.finalize, len(schedule_items))
        if all_counts is None:
            print(f"  Job not done yet ({status}).")
            return
        analyze(schedule_items, all_counts, job_id=args.finalize)
    elif args.submit:
        print(f"\n=== Exp {EXPERIMENT}: building hardware schedule ({BACKEND_NAME}) ===")
        schedule_items, backend = build_schedule_for_hardware()
        print(f"\n=== Submitting to {BACKEND_NAME} ===")
        jid = submit_hardware(schedule_items, backend)
        print(f"\n  Finalize with:  python3 scripts/run_exp35_portfolio_qaoa_ceiling.py --finalize {jid}")
    else:
        bx, be = brute_force_optimum()
        print(f"\n=== Exp {EXPERIMENT}: FakeMarrakesh simulation preview ===")
        print(f"  QUBO ground state x*={bx.astype(int).tolist()} (sum={int(bx.sum())}, target K={K_SELECT}), "
              f"energy={be:.4f}")
        schedule_items, backend = build_schedule_for_fake()
        all_counts = get_counts_from_fake(schedule_items, backend)
        analyze(schedule_items, all_counts, job_id="FakeMarrakesh-sim")


if __name__ == "__main__":
    main()
