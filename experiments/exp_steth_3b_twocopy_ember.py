#!/usr/bin/env python3
"""Exp-STETH annex §3(b) retrofit — two-copy destructive-overlap REPLACING a tomography block.

Creator directive (2026-07-21, general): "Fly the §3(b) retrofit (two-copy overlap replacing a
tomography block)." Whisper offered it as the safer lower-SPAM first flight of the stethoscope annex.

WHAT THIS MEASURES (a RESOURCE comparison, NOT a quantum-advantage claim — classical shadows estimate
purity with no 2nd copy; this compares the two-copy PRIMITIVE against the TOMOGRAPHY BLOCK it
replaces): the state property Tr[rho^2] (purity) of an ENTANGLED mixed state rho, two ways, on the
SAME hardware, at n=1,2,3 system qubits:
  * TWO-COPY arm: two independent copies of rho, transversal destructive SWAP test (Cincio et al.):
      per pair i: CX(a_i -> b_i), H(a_i), measure -> bits (u_i, v_i);  per-shot estimator
      P2 = (-1)^(sum_i u_i AND v_i),  E[P2] = Tr[rho^2].  ONE measurement setting, any n.
  * TOMOGRAPHY arm: 3^n Pauli-basis settings on the n system qubits; UNBIASED (variance-subtracted)
      purity  Tr[rho^2] = (1/2^n) sum_P ( <P_hat>^2 - Var_hat(<P_hat>) ).  The naive sum <P_hat>^2 is
      biased HIGH by finite-shot variance (advisor) -> variance subtraction makes the baseline fair.

DELIVERABLE: the MEASURED shot-bill delta = shots_tomo / shots_twocopy to reach a MATCHED SE on
Tr[rho^2], computed from the EMPIRICAL per-shot variances of each arm (measured, not assumed), and the
n=1,2,3 SCALING TREND (settings 3^n -> O(1)). Pre-committed: the delta may be modest or NEGATIVE at
small n (two-copy pays an entangling layer + double qubits); the deliverable is the trend, not a win
at every rung. Under the <=0.6 quantum-confidence cap.

SCOPE (stated, per advisor): primitive-level head-to-head (two-copy vs a fair standalone tomography
block), NOT a retrofit of a named existing grader. rho is ENTANGLED (fixed shallow circuit on
system+bath, bath traced out) so the 3^n-setting baseline cannot be factorized away.

EXACTNESS GATE (pre-submit kill): noiseless two-copy purity == noiseless tomography purity ==
statevector Tr[rho^2] within tol, for n=1,2,3. A rung that fails never flies.

Substrate stamped at runtime. Reuses run_exp66_qpu_partb._get_ibm_service + SamplerV2.
"""
import os, sys, json, math, argparse, itertools
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Statevector, partial_trace, DensityMatrix

NS = [1, 2, 3]
STATE_SEED = 3210
SHOTS = 4000
TOL = 1e-9
PAULI_AXES = ["X", "Y", "Z"]


# ---------- state preparation: entangled mixed rho on n system qubits (bath = n qubits) ----------
def prep(qc, n, sys, bath, seed):
    """Fixed shallow entangler on (system, bath) so the reduced system state is a generic ENTANGLED
    mixed state (not a product) -> the 3^n-setting tomography baseline cannot be factorized."""
    rng = np.random.default_rng(seed)
    for i in range(n):
        qc.ry(float(rng.uniform(0.6, 1.2)), sys[i])       # partial rotation
        qc.cx(sys[i], bath[i])                              # entangle each sys with its bath -> mixed
    for i in range(n - 1):
        qc.cx(sys[i], sys[i + 1])                           # correlate system qubits -> non-product
    for i in range(n):
        qc.rz(float(rng.uniform(0.3, 0.9)), sys[i])


def noiseless_rho_sys(n, seed):
    qc = QuantumCircuit(2 * n)
    prep(qc, n, list(range(n)), list(range(n, 2 * n)), seed)
    sv = Statevector(qc)
    rho = partial_trace(sv, list(range(n, 2 * n)))         # trace out bath
    return DensityMatrix(rho)


def true_purity(n, seed):
    rho = noiseless_rho_sys(n, seed).data
    return float(np.real(np.trace(rho @ rho)))


# ---------- two-copy destructive SWAP circuit (one setting) ----------
def two_copy_circuit(n, seed):
    # copy1: sys 0..n-1, bath n..2n-1 ; copy2: sys 2n..3n-1, bath 3n..4n-1
    qc = QuantumCircuit(4 * n, 2 * n)
    s1, b1 = list(range(0, n)), list(range(n, 2 * n))
    s2, b2 = list(range(2 * n, 3 * n)), list(range(3 * n, 4 * n))
    prep(qc, n, s1, b1, seed)
    prep(qc, n, s2, b2, seed)
    for i in range(n):                                     # transversal destructive SWAP on sys pairs
        qc.cx(s1[i], s2[i]); qc.h(s1[i])
    for i in range(n):
        qc.measure(s1[i], i)                              # u_i
        qc.measure(s2[i], n + i)                          # v_i
    return qc


def two_copy_estimator(bitstrings, n):
    """bitstrings: list of measured strings (qiskit order, len 2n over classical bits 0..2n-1).
    per-shot P2 = (-1)^(sum_i u_i & v_i). Returns per-shot +-1 array."""
    vals = []
    for bs in bitstrings:
        # classical bit c -> char; qiskit string is c(2n-1)..c0 left-to-right
        b = bs.replace(" ", "")
        bits = [int(b[len(b) - 1 - c]) for c in range(2 * n)]  # bits[c] = classical bit c
        s = sum(bits[i] & bits[n + i] for i in range(n))
        vals.append(1 if s % 2 == 0 else -1)
    return np.array(vals, dtype=float)


# ---------- tomography circuits (3^n settings) ----------
def tomo_circuits(n, seed):
    circs, settings = [], list(itertools.product(PAULI_AXES, repeat=n))
    for axes in settings:
        qc = QuantumCircuit(2 * n, n)
        prep(qc, n, list(range(n)), list(range(n, 2 * n)), seed)
        for i, ax in enumerate(axes):
            if ax == "X": qc.h(i)
            elif ax == "Y": qc.sdg(i); qc.h(i)
        for i in range(n):
            qc.measure(i, i)
        circs.append(qc)
    return circs, settings


def _pauli_from_axes_and_mask(axes, mask):
    return "".join(axes[i] if mask[i] else "I" for i in range(len(axes)))


def tomo_purity_unbiased(counts_per_setting, settings, n):
    """Unbiased (variance-subtracted) purity. Each Pauli P is estimated by POOLING all settings whose
    axes match P on non-I positions; <P_hat> = pooled mean of eigenvalues, Var_hat = (1-<P>^2)/Neff.
    Tr[rho^2] = (1/2^n) sum_P (<P_hat>^2 - Var_hat)."""
    # gather per-setting eigenvalue means/counts for each Pauli
    # For each setting (axes), its counts give, for any mask, the eigenvalue mean of the Pauli
    # P(axes,mask) = product over masked qubits of (+-1 by measured bit).
    from collections import defaultdict
    pool = defaultdict(lambda: [0.0, 0])   # pauli-string -> [sum_eigen, total_shots]
    for axes, counts in zip(settings, counts_per_setting):
        N = sum(counts.values())
        for mask in itertools.product([0, 1], repeat=n):
            if not any(mask):
                continue
            P = _pauli_from_axes_and_mask(axes, mask)
            se = 0.0
            for bs, c in counts.items():
                b = bs.replace(" ", "")
                bits = [int(b[len(b) - 1 - i]) for i in range(n)]
                par = 0
                for i in range(n):
                    if mask[i]:
                        par ^= bits[i]
                se += (1 if par == 0 else -1) * c
            pool[P][0] += se
            pool[P][1] += N
    total = 0.0
    for P, (se, N) in pool.items():
        if N == 0:
            continue
        mean = se / N
        var_of_mean = max(0.0, (1.0 - mean * mean)) / max(1, N - 1)
        total += mean * mean - var_of_mean          # unbiased <P>^2
    # identity Pauli contributes <I>^2 - 0 = 1
    return (1.0 + total) / (2 ** n)


# ---------- exactness gate ----------
def selftest():
    from qiskit_aer import AerSimulator
    sim = AerSimulator()
    print("=" * 80)
    print("Exp-STETH §3(b) exactness gate — noiseless two-copy & tomography must recover Tr[rho^2]")
    print("=" * 80)
    ok_all = True
    for n in NS:
        pt = true_purity(n, STATE_SEED)
        # two-copy noiseless
        tc = two_copy_circuit(n, STATE_SEED)
        r = sim.run(transpile(tc, sim), shots=40000, seed_simulator=7).result().get_counts()
        bs = []
        for k, c in r.items():
            bs += [k] * c
        p2 = two_copy_estimator(bs, n).mean()
        # tomography noiseless
        circs, settings = tomo_circuits(n, STATE_SEED)
        cps = [sim.run(transpile(c, sim), shots=8000, seed_simulator=11).result().get_counts()
               for c in circs]
        pt_tomo = tomo_purity_unbiased(cps, settings, n)
        d2, dt = abs(p2 - pt), abs(pt_tomo - pt)
        ok = d2 < 0.02 and dt < 0.02   # finite-shot noiseless tolerance
        ok_all &= ok
        print(f"[{'PASS' if ok else 'FAIL'}] n={n}: true Tr[rho^2]={pt:.4f} | two-copy={p2:.4f} "
              f"(d{d2:.4f}) | tomo_unbiased={pt_tomo:.4f} (d{dt:.4f}) | settings 3^{n}={3**n}")
    print("-" * 80)
    print(f"{'ALL PASS' if ok_all else 'FAIL'} — noiseless arms recover purity")
    return 0 if ok_all else 1


# ---------- submit ----------
def submit(backend_name):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service()
    backend = svc.backend(backend_name)
    circs, index = [], []
    for n in NS:
        tc = two_copy_circuit(n, STATE_SEED)
        circs.append(tc); index.append({"kind": "twocopy", "n": n, "settings": 1})
        tomos, settings = tomo_circuits(n, STATE_SEED)
        for c, ax in zip(tomos, settings):
            circs.append(c); index.append({"kind": "tomo", "n": n, "axes": "".join(ax)})
    tqc = transpile(circs, backend=backend, optimization_level=3, seed_transpiler=3211)
    depths = [t.depth() for t in tqc]
    print(f"transpiled {len(tqc)} circuits; max depth={max(depths)}, "
          f"max 2q≈{max(t.count_ops().get('cz',0)+t.count_ops().get('cx',0)+t.count_ops().get('ecr',0) for t in tqc)}")
    sampler = SamplerV2(mode=backend)
    job = sampler.run(tqc, shots=SHOTS)
    manifest = {"exp": "steth_3b", "backend": backend_name, "state_seed": STATE_SEED, "shots": SHOTS,
                "ns": NS, "job_id": job.job_id(), "index": index,
                "true_purity": {str(n): true_purity(n, STATE_SEED) for n in NS},
                "note": "two-copy vs tomography-block purity; shot-bill delta from empirical variances"}
    out = os.path.join(HERE, "..", "results", "exp_steth_3b_manifest.json")
    json.dump(manifest, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(tqc)} circuits, {SHOTS} shots) -> {os.path.relpath(out)}")
    return job.job_id()


# ---------- decode ----------
def decode(manifest_path):
    from run_exp66_qpu_partb import _get_ibm_service
    svc = _get_ibm_service()
    man = json.load(open(manifest_path))
    res = svc.job(man["job_id"]).result()
    idx = man["index"]; shots = man["shots"]
    # gather counts back per (n, kind)
    def counts_of(i):
        d = res[i].data
        reg = list(d.__dict__.keys())[0] if hasattr(d, "__dict__") else None
        bitarray = getattr(d, reg) if reg else d.meas
        return bitarray.get_counts()
    out_rows = []
    tomo_by_n = {}
    twocopy_by_n = {}
    for i, meta in enumerate(idx):
        c = counts_of(i)
        if meta["kind"] == "twocopy":
            twocopy_by_n[meta["n"]] = c
        else:
            tomo_by_n.setdefault(meta["n"], []).append((meta["axes"], c))
    summary = {}
    for n in man["ns"]:
        pt = man["true_purity"][str(n)]
        # two-copy
        c = twocopy_by_n[n]
        bs = []
        for k, v in c.items():
            bs += [k] * v
        vals = two_copy_estimator(bs, n)
        p2 = float(vals.mean()); var2 = float(vals.var(ddof=1)); M2 = len(vals)
        se2 = math.sqrt(var2 / M2)
        # tomography
        axes_counts = tomo_by_n[n]
        settings = [tuple(a) for a, _ in axes_counts]
        cps = [cc for _, cc in axes_counts]
        p_tomo = tomo_purity_unbiased(cps, settings, n)
        Mtomo = sum(sum(cc.values()) for cc in cps)
        # empirical SE of tomography purity via bootstrap over settings' shots (per-shot variance proxy)
        se_tomo = _tomo_bootstrap_se(cps, settings, n, reps=200)
        # shot-bill delta at matched SE: pick target = two-copy's se2; M_needed_tomo for that SE
        # tomography variance scales ~1/Mtomo -> var_tomo_perTotalshot = se_tomo^2 * Mtomo
        v2_per = var2                                   # two-copy per-shot variance
        vt_per = se_tomo * se_tomo * Mtomo              # tomography variance * total shots (per-shot)
        target_se = se2
        M2_need = v2_per / (target_se ** 2)
        Mt_need = vt_per / (target_se ** 2)
        delta = Mt_need / M2_need if M2_need > 0 else float("nan")
        summary[str(n)] = {
            "true_purity": round(pt, 4),
            "twocopy": {"estimate": round(p2, 4), "se": round(se2, 4), "shots": M2,
                        "per_shot_var": round(v2_per, 4), "settings": 1},
            "tomography": {"estimate": round(p_tomo, 4), "se": round(se_tomo, 4), "shots": Mtomo,
                           "per_shot_var": round(vt_per, 4), "settings": 3 ** n},
            "shot_bill_delta_matched_se": round(delta, 2),
            "settings_ratio": 3 ** n,
        }
        print(f"n={n}: true={pt:.4f} | twocopy={p2:.4f}±{se2:.4f} (1 setting) | "
              f"tomo={p_tomo:.4f}±{se_tomo:.4f} ({3**n} settings) | shot-bill Δ={delta:.2f}× "
              f"(settings {3**n}×)")
    card = {"card": "exp_steth_3b_twocopy_ember", "annex_section": "3(b)",
            "backend": man["backend"], "job_id": man["job_id"], "state_seed": man["state_seed"],
            "shots_per_circuit": shots, "summary": summary,
            "frame": "RESOURCE comparison (two-copy primitive vs the tomography block it replaces), NOT "
                     "a quantum-advantage claim; classical shadows estimate purity with no 2nd copy.",
            "scope": "primitive-level head-to-head, not a named-grader retrofit.",
            "estimators": "two-copy: unbiased per-shot (-1)^(sum u&v); tomography: unbiased "
                          "variance-subtracted (1/2^n)sum(<P>^2 - Var).",
            "confidence_cap": "<=0.6 (quantum behavioral cap)"}
    out = os.path.join(HERE, "..", "results", "exp_steth_3b_decode.json")
    json.dump(card, open(out, "w"), indent=1)
    print(f"card -> {os.path.relpath(out)}")
    return card


def _tomo_bootstrap_se(cps, settings, n, reps=200):
    """Bootstrap SE of the unbiased tomography purity by resampling each setting's shots."""
    rng = np.random.default_rng(99)
    # expand each setting to arrays of outcome strings
    setting_shots = []
    for cc in cps:
        arr = []
        for k, v in cc.items():
            arr += [k] * v
        setting_shots.append(arr)
    ests = []
    for _ in range(reps):
        resampled = []
        for arr in setting_shots:
            idx = rng.integers(0, len(arr), len(arr))
            from collections import Counter
            resampled.append(Counter(arr[i] for i in idx))
        ests.append(tomo_purity_unbiased(resampled, settings, n))
    return float(np.std(ests, ddof=1))


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--submit", metavar="BACKEND")
    ap.add_argument("--decode", metavar="MANIFEST")
    a = ap.parse_args()
    if a.selftest:
        sys.exit(selftest())
    elif a.submit:
        submit(a.submit)
    elif a.decode:
        decode(a.decode)
    else:
        ap.print_help()
