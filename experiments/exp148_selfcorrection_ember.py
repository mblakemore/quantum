#!/usr/bin/env python3
"""Exp148 — SELF-CORRECTION SURVIVAL LAW (Ember). Creator 'fly it'; parallel to Whisper Exp147.

THE QUESTION, honestly posed (advisor-hardened): is Simon's survival of deep-circuit noise
"algorithmic self-correction" (something the algorithm does), or is it just OPTIMAL STATISTICAL
DETECTION of a persistent-but-shrinking bias (mundane matched-filter / ML)? "Redundancy helps"
is sampling statistics; a naive-vs-consensus decoder gap cannot tell the two apart. So this does
NOT demonstrate self-correction — it TESTS my own headline, the discipline I put on the
Even-Mansour result tonight.

THE DISCRIMINATOR (free — I hold planted s):
  - p_true(depth)  = fraction of measured y's orthogonal to the TRUE s.
  - p_comp(depth)  = max over the 2^n-2 WRONG s' of (fraction of y's orthogonal to s').
  - Delta(depth)   = p_true - p_comp  (the self-correction "signal" that noise shrinks).
  - R*(depth)      = reps a weak-signal ML detector needs to resolve Delta at significance
                     alpha, Bonferroni-corrected for the 2^n-2 competitors.
Then compare ACTUAL consensus-decoder recovery-vs-reps to R*(depth).

PRE-REGISTERED PREDICTION (~0.75, written to disk BEFORE decode): actual recovery TRACKS R*
=> the mechanism is optimal detection of a bias noise shrinks but does not erase, and the "wall"
is a statistical-power threshold that MOVES WITH REPS (spend reps -> go deeper). Honest headline
then = "optimal persistent-bias detection", NOT "self-healing". FALSIFIER: recovery consistently
BEATS R* (recovers at fewer reps than optimal detection permits) => genuinely algorithm-specific,
earns the name.

DESIGN (advisor fixes folded in):
  - FIXED n (holds the competitor count 2^n-2 constant, so Delta's decay is pure noise, not
    more-competitors) — complementary to Whisper's n-sweep (Exp145b), not a redo.
  - identity-CX depth knob: dials NOISE as a depth PROXY (not a deeper oracle), gated on the
    injected CX actually SURVIVING transpilation (count 2q gates per setting; opt cancels pairs).
  - naive baseline = average over RANDOM independent (n-1)-subsets (not "first n-1" = selection
    bias, c4194_006).
  - the (depth x reps) frontier is reported WITHIN the flown rep budget — no extrapolating a wall.

  python3 exp148_selfcorrection_ember.py --gates          # noiseless truth + transpile-survive + falsifiability
  python3 exp148_selfcorrection_ember.py --prereg         # write the pre-registered prediction
  python3 exp148_selfcorrection_ember.py --submit
  python3 exp148_selfcorrection_ember.py --analyze --manifest ...
"""
import argparse
import importlib.util
import itertools
import json
import math
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
RESULTS = os.path.join(HERE, "..", "results")

# reuse Whisper's verified Simon kit
_spec = importlib.util.spec_from_file_location("simon", os.path.join(HERE, "exp145_simon_race.py"))
SIMON = importlib.util.module_from_spec(_spec); _spec.loader.exec_module(SIMON)

N = 4                                   # fixed rung: competitor count 2^4-2 = 14 held constant
PLANTED_S = [1, 0, 1, 0]                # fixed planted period (weight-2, i0=0)
EXTRA_PAIRS = [0, 4, 8, 14, 20, 28]     # identity-CX pairs injected -> physical depth ladder
SHOTS = 2000                            # per depth setting; subsampled for the reps sweep
ALPHA = 0.05


def depth_circuit(n, s, extra_pairs):
    """Simon circuit + `extra_pairs` identity CX pairs (CX;CX=I) on the input register,
    barrier-fenced so the transpiler cannot cancel them. Logical problem is UNCHANGED
    (s invariant); only physical depth/noise grows. Verified by the noiseless gate."""
    from qiskit import QuantumCircuit
    qc = SIMON.simon_circuit(n, s)
    # rebuild with injection before the final H: easiest is to construct fresh
    qc = QuantumCircuit(2 * n, n)
    qc.h(range(n)); qc.barrier()
    qc.compose(SIMON.simon_oracle(n, s), inplace=True); qc.barrier()
    for p in range(extra_pairs):
        a = p % n
        b = n + (p % n)
        qc.cx(a, b); qc.barrier(); qc.cx(a, b); qc.barrier()   # identity, fence-protected
    qc.h(range(n))
    qc.measure(range(n), range(n))
    return qc


def consensus_decode(ys, n, s_true=None):
    """ML/argmax: the nonzero s' orthogonal to the MOST y's. Returns (s_hat, counts_dict)."""
    counts = {}
    for sc in itertools.product((0, 1), repeat=n):
        if not any(sc):
            continue
        counts[sc] = sum(1 for y in ys if np.dot(y, sc) % 2 == 0)
    s_hat = list(max(counts, key=counts.get))
    return s_hat, counts


def naive_decode_avg(ys, n, s_true, rng, trials=200):
    """Naive baseline: random INDEPENDENT (n-1)-subset -> GF(2) nullspace, averaged (NOT
    'first n-1' = selection bias, c4194_006). A rank-deficient draw is an INVALID sample
    (nullspace not 1-dim), not a recovery failure — redraw it. So at zero noise this is 1.0;
    under noise it fails only when an independent subset includes a corrupted y (naive has no
    way to reject it — that gap vs consensus is the whole point). Returns recovery fraction
    over valid independent draws."""
    if len(ys) < n - 1:
        return 0.0
    succ = valid = 0
    attempts = 0
    while valid < trials and attempts < trials * 40:
        attempts += 1
        idx = rng.choice(len(ys), size=n - 1, replace=False)
        s_hat = SIMON.gf2_nullspace_vector([list(ys[i]) for i in idx], n)
        if s_hat is None:                       # dependent subset — invalid, not a miss
            continue
        valid += 1
        succ += int(s_hat == s_true)
    return succ / valid if valid else 0.0


def bias(ys, n, s_true):
    """p_true, p_comp, Delta from a set of y's."""
    if not ys:
        return 0.0, 0.0, 0.0
    _, counts = consensus_decode(ys, n)
    tot = len(ys)
    p_true = counts[tuple(s_true)] / tot
    p_comp = max(v for k, v in counts.items() if list(k) != s_true) / tot
    return p_true, p_comp, p_true - p_comp


def ml_threshold_reps(delta, n, alpha=ALPHA):
    """Reps a weak-signal detector needs to resolve a bias `delta` between two ~0.5 fractions,
    Bonferroni-corrected for C=2^n-2 competitors. R* = (z_corr * sqrt(2*0.25) / delta)^2.
    delta<=0 -> unresolvable (inf)."""
    if delta <= 0:
        return math.inf
    C = 2 ** n - 2
    from statistics import NormalDist
    z = NormalDist().inv_cdf(1 - alpha / C)     # Bonferroni two-fraction selection
    return (z * math.sqrt(2 * 0.25) / delta) ** 2


# ---------------------------------------------------------------- gates
def gate_noiseless(n, s):
    """Both decoders MUST recover planted s at zero noise, every depth setting (identity CX
    cannot change the logical answer). Non-vacuous: asserts trials>0."""
    from qiskit.primitives import StatevectorSampler
    smp = StatevectorSampler(); rng = np.random.default_rng(148)
    checked = 0
    for ep in EXTRA_PAIRS:
        qc = depth_circuit(n, s, ep)
        res = smp.run([(qc, None, 4000)]).result()[0].data
        reg = list(res.keys())[0] if hasattr(res, "keys") else "meas"
        counts = getattr(res, reg).get_counts() if hasattr(res, reg) else res.meas.get_counts()
        ys = SIMON._sample_ys(counts, n)
        s_con, _ = consensus_decode(ys, n)
        nav = naive_decode_avg(ys, n, s, rng, trials=50)
        ok_con = (s_con == s)
        ok_nav = nav > 0.99
        checked += 1
        print(f"  extra_pairs={ep:>3}: consensus={'OK' if ok_con else 'FAIL '+str(s_con)} | "
              f"naive avg recovery={nav:.2f} {'OK' if ok_nav else 'FAIL'}")
        if not (ok_con and ok_nav):
            return False
    print(f"  compared: {checked} depth settings, both decoders recover planted s at zero noise")
    return checked > 0


def gate_transpile_survive(n, s, backend_name):
    """The injected CX must SURVIVE transpilation — 2q count must grow with extra_pairs, or the
    depth knob is a no-op. Advisor fix #3."""
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit import transpile
    be = _get_ibm_service().backend(backend_name)
    prev = -1; ok = True; rows = []
    for ep in EXTRA_PAIRS:
        t = transpile(depth_circuit(n, s, ep), be, optimization_level=1, seed_transpiler=148)
        n2q = sum(t.count_ops().get(g, 0) for g in ("cz", "ecr", "cx"))
        rows.append((ep, n2q, t.depth()))
        if n2q <= prev:
            ok = False
        prev = n2q
    for ep, n2q, d in rows:
        print(f"  extra_pairs={ep:>3}: 2q-gates={n2q:>3} depth={d:>3}")
    print(f"  monotone 2q growth: {'OK — depth knob real' if ok else 'FAIL — injection cancelled'}")
    return ok, rows


def gate_falsifiability(n, s):
    """A deliberately wrong s_hat must fail verify (the falsifier must be able to fire)."""
    wrong = s[:]; wrong[0] ^= 1
    ok_true, _ = SIMON.verify(s, s, [s])            # a y=s is trivially ⊥? verify uses dot%2
    bad, _ = SIMON.verify(wrong, s, [[0] * n])
    print(f"  wrong s_hat rejected by verify: {'OK' if not bad else 'FAIL'}")
    return not bad


# ---------------------------------------------------------------- prereg / submit / analyze
def prereg():
    doc = {
        "exp": 148, "author": "Ember", "written": "pre-decode",
        "question": "Is Simon deep-noise survival algorithmic self-correction, or optimal "
                    "statistical detection of a persistent shrinking bias?",
        "discriminator": "compare actual consensus recovery-vs-reps to ML threshold R*(depth) "
                         "computed from measured p_true, p_comp (Bonferroni over 2^n-2).",
        "prediction": "recovery TRACKS R* -> optimal-detection, wall = statistical-power "
                      "threshold movable with reps. NOT self-healing.",
        "prediction_confidence": 0.75,
        "falsifier": "recovery consistently BEATS R* (recovers at fewer reps than optimal "
                     "detection permits) -> genuinely algorithm-specific.",
        "n": N, "planted_s": PLANTED_S, "extra_pairs_ladder": EXTRA_PAIRS,
        "shots_per_depth": SHOTS, "alpha": ALPHA,
        "honest_label_if_tracks": "optimal detection of a persistent bias noise shrinks but "
                                  "does not erase; carries as far as reps resolve the bias.",
    }
    p = os.path.join(RESULTS, "exp148_prereg.json")
    json.dump(doc, open(p, "w"), indent=1)
    print(f"pre-registered -> {p}\n  prediction (0.75): recovery tracks the ML bound (optimal "
          f"detection, not self-healing); falsifier = recovery beats the bound.")


def submit(backend_name):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit import transpile
    from qiskit_ibm_runtime import SamplerV2
    ok, rows = gate_transpile_survive(N, PLANTED_S, backend_name)
    if not ok:
        print("REFUSING: depth knob cancelled in transpile — no QPU on a no-op ladder."); return 1
    be = _get_ibm_service().backend(backend_name)
    tqcs = [transpile(depth_circuit(N, PLANTED_S, ep), be, optimization_level=1,
                      seed_transpiler=148) for ep in EXTRA_PAIRS]
    outp = os.path.join(RESULTS, "exp148_manifest.json")
    if os.path.exists(outp):
        print(f"REFUSING: {os.path.basename(outp)} exists."); return 3
    job = SamplerV2(mode=be).run([(t, None, SHOTS) for t in tqcs])
    man = {"exp": 148, "n": N, "planted_s": PLANTED_S, "extra_pairs": EXTRA_PAIRS,
           "shots_per_depth": SHOTS, "backend": backend_name, "job_id": job.job_id(),
           "transpiled_2q": [r[1] for r in rows], "transpiled_depth": [r[2] for r in rows],
           "note": "Self-verifying (planted_s). Depth ladder co-batched, 1 pub/setting. "
                   "Analysis compares recovery-vs-reps to the pre-registered ML threshold."}
    json.dump(man, open(outp, "w"), indent=1)
    print(f"SUBMITTED Exp148: job {job.job_id()} ({len(tqcs)} depth settings x {SHOTS} shots) "
          f"-> {os.path.basename(outp)}")
    print("  (no QPU figure until measured, C4796)")
    return 0


def analyze(mp):
    from run_exp66_qpu_partb import _get_ibm_service
    svc = _get_ibm_service()
    man = json.load(open(mp)); n, s = man["n"], man["planted_s"]
    res = svc.job(man["job_id"]).result()
    rng = np.random.default_rng(1480)
    prereg_doc = json.load(open(os.path.join(RESULTS, "exp148_prereg.json")))
    print(f"Exp148 analysis | planted s={s} | pre-registered prediction (0.75): "
          f"recovery tracks the ML bound (optimal detection)")
    rows = []
    R_GRID = [8, 16, 24, 32, 48, 64, 96, 128, 192, 256]
    for i, ep in enumerate(man["extra_pairs"]):
        d = res[i].data; reg = list(d.keys())[0]
        counts = getattr(d, reg).get_counts()
        ys_all = [tuple(y) for y in SIMON._sample_ys(counts, n)]
        p_true, p_comp, delta = bias(ys_all, n, s)
        Rstar = ml_threshold_reps(delta, n)
        # actual consensus recovery vs reps (subsample within the flown budget)
        rec_at = {}
        for R in R_GRID:
            if R > len(ys_all):
                break
            succ = 0
            for _ in range(60):
                sub = [ys_all[j] for j in rng.choice(len(ys_all), size=R, replace=False)]
                s_hat, _ = consensus_decode(sub, n)
                succ += int(s_hat == s)
            rec_at[R] = succ / 60
        R_actual = next((R for R in R_GRID if rec_at.get(R, 0) >= 0.9), None)
        naive_full = naive_decode_avg(ys_all, n, s, rng, trials=300)
        n2q = man["transpiled_2q"][i]
        rows.append({"extra_pairs": ep, "n2q": n2q, "p_true": round(p_true, 3),
                     "p_comp": round(p_comp, 3), "delta": round(delta, 3),
                     "R_star_ML": None if Rstar == math.inf else round(Rstar, 1),
                     "R_actual_90": R_actual, "naive_full_recovery": round(naive_full, 3),
                     "recovery_curve": rec_at})
        print(f"  2q={n2q:>3} d={delta:+.3f} (pT={p_true:.3f} pC={p_comp:.3f}) | "
              f"R*_ML={'inf' if Rstar==math.inf else round(Rstar,0)} R_actual@90%="
              f"{R_actual} | naive_full={naive_full:.2f}")
    # verdict: does R_actual track R*_ML?
    comp = [(r["R_star_ML"], r["R_actual_90"]) for r in rows
            if r["R_star_ML"] and r["R_actual_90"]]
    verdict = "insufficient points"
    if comp:
        ratios = [a / m for m, a in comp]
        gm = math.exp(sum(math.log(x) for x in ratios) / len(ratios))
        if 0.5 <= gm <= 2.0:
            verdict = f"TRACKS the ML bound (geomean R_actual/R* = {gm:.2f}) -> OPTIMAL DETECTION, prediction HELD"
        elif gm < 0.5:
            verdict = f"BEATS the ML bound (geomean {gm:.2f}) -> algorithm-specific, prediction FALSIFIED"
        else:
            verdict = f"WORSE than ML bound (geomean {gm:.2f}) -> decoder suboptimal, not self-correction"
    out = {"exp": 148, "planted_s": s, "rows": rows, "verdict": verdict,
           "prereg": prereg_doc}
    json.dump(out, open(os.path.join(RESULTS, "exp148_analysis.json"), "w"), indent=1)
    print(f"\n  VERDICT: {verdict}")
    print(f"  -> results/exp148_analysis.json")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gates", action="store_true")
    ap.add_argument("--prereg", action="store_true")
    ap.add_argument("--submit", action="store_true")
    ap.add_argument("--analyze", action="store_true")
    ap.add_argument("--manifest")
    ap.add_argument("--backend", default="ibm_kingston")
    a = ap.parse_args()
    if a.gates:
        print("=== noiseless truth-gate (both decoders recover planted s, every depth) ===")
        g1 = gate_noiseless(N, PLANTED_S)
        print("=== transpile-survive gate (injected CX must not cancel) ===")
        g2, _ = gate_transpile_survive(N, PLANTED_S, a.backend)
        print("=== falsifiability gate ===")
        g3 = gate_falsifiability(N, PLANTED_S)
        print(f"\nGATES: {'ALL PASS' if (g1 and g2 and g3) else 'FAIL'}")
        return 0 if (g1 and g2 and g3) else 1
    if a.prereg:
        prereg(); return 0
    if a.submit:
        return submit(a.backend)
    if a.analyze:
        analyze(a.manifest or os.path.join(RESULTS, "exp148_manifest.json")); return 0
    ap.print_help(); return 0


if __name__ == "__main__":
    sys.exit(main())
