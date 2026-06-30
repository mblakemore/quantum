#!/usr/bin/env python3
"""
Exp79 (Elder C6270) — CONFIRM-OR-KILL the NOISE-INVERSION PARADOX (Finding 10 / Exp17).

CREATOR HYPOTHESIS (the live one, per advisor C6270): can noise ADD computational value /
be a resource? The corpus's own positive evidence is Finding 10's "noise-inversion paradox":
NISQ noise NARROWED IQAE confidence intervals by 34-63% at P=0.3/0.4/0.7 — claimed as
"noise functioning as beneficial oracle-call pressure."

THE TWO CONTROLS FINDING 10 DID NOT APPLY (the artifact explanations):
  (1) QUERY CONFOUND: the paradox table shows NOISY k HIGHER than IDEAL k (8.6 vs 7, etc.).
      More oracle calls -> narrower CI is EXPECTED. The honest comparison is CI at MATCHED
      oracle budget, NOT CI-at-whatever-k-each-stopped.
  (2) COVERAGE: a narrower CI is only real if it still CONTAINS the truth at the nominal 95%.
      Finding 10 itself flags coverage failure (87.5%) at P=0.9. A narrow-but-overconfident CI
      is FALSE PRECISION, not a benefit. Data-processing inequality: noise cannot ADD Fisher
      information; it can only change the adaptive stopping (double-edged).

THIS TEST (controlled, cheap, sim-only — the mechanism is what's under test, so a controlled
depth-dependent DEPOLARIZING model isolates it more cleanly than FakeMarrakesh's confounds):
  - IAE-MLE (validated engine, Exp10/Exp78) at a* in {0.30, 0.40, 0.56, 0.70}.
  - Per Grover power m=2k+1: ideal P(1)=sin^2(m*theta); depth-depolarizing pulls toward 0.5:
        lambda_k = 1 - (1-lambda1)^(2k+1)         (more Grover power = more depth = more depol)
        P_noisy = (1-lambda_k)*P_ideal + lambda_k*0.5,  then binomial(shots).
    lambda1 ~ 0.10 (Heron-r2: ~24 two-qubit gates/Grover power x ~0.5% CZ err -> ~0.11/power; from Exp78).
  - Sweep oracle BUDGET (cumulative k-schedules {0},{0,1},...,{0..K}) so CI-vs-budget is explicit.
  - MANY seeds/condition. Per seed record: bootstrap CI width, coverage (CI contains a*?), |err|,
    total oracle calls = shots*sum(2k+1).
  - DECISIVE COMPARISON: noiseless vs noisy AT MATCHED BUDGET (same k-schedule == same queries).

GRADES (pre-registered):
  CONFIRM (noise is a resource) iff at MATCHED budget noisy CI is NARROWER AND coverage >= ~0.93
    AND |err| not worse. (Would be genuinely surprising.)
  KILL-via-CONFOUND iff narrowing only appears when noisy spends MORE queries (vanishes/reverses at
    matched budget) -> the paradox was a budget artifact.
  KILL-via-COVERAGE iff noisy CI is narrower at matched budget BUT coverage < 0.90 -> false precision.

USAGE: python3 run_exp79_noise_inversion_killtest.py [--seeds 300] [--lambda1 0.10] [--shots 1024]
"""
import sys, os, json, math, argparse
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_experiment_10_financial_qae import mle_recovery, bootstrap_ci

A_VALUES = [0.30, 0.40, 0.56, 0.70]
K_MAX = 6
SEED0 = 79


def sample_counts(a_true, k_schedule, lambda1, shots, rng):
    """Return [(k, m_ones, shots)] under depth-depolarizing noise (lambda1=0 -> noiseless)."""
    theta = math.asin(math.sqrt(a_true))
    data = []
    for k in k_schedule:
        m = 2 * k + 1
        p_ideal = math.sin(m * theta) ** 2
        lam = 1.0 - (1.0 - lambda1) ** m
        p_noisy = (1 - lam) * p_ideal + lam * 0.5
        ones = int(rng.binomial(shots, min(max(p_noisy, 0.0), 1.0)))
        data.append((k, ones, shots))
    return data


def run_condition(a_true, k_schedule, lambda1, shots, seeds):
    widths, covered, errs = [], 0, []
    oracle_calls = shots * sum(2 * k + 1 for k in k_schedule)
    for s in range(seeds):
        rng = np.random.default_rng(SEED0 + s * 100003 + int(a_true * 1e4) + len(k_schedule))
        data = sample_counts(a_true, k_schedule, lambda1, shots, rng)
        a_hat = mle_recovery(data)
        lo, hi, w = bootstrap_ci(data, n_bootstrap=400)
        widths.append(w)
        if lo <= a_true <= hi:
            covered += 1
        errs.append(abs(a_hat - a_true))
    return {"mean_ci_width": float(np.mean(widths)), "coverage": covered / seeds,
            "mean_abs_err": float(np.mean(errs)), "oracle_calls": oracle_calls}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--seeds", type=int, default=300)
    ap.add_argument("--lambda1", type=float, default=0.10)
    ap.add_argument("--shots", type=int, default=1024)
    args = ap.parse_args()

    print(f"Exp79 noise-inversion KILL-TEST | seeds={args.seeds} lambda1={args.lambda1} shots={args.shots}", flush=True)
    print(f"  depth-depolarizing: lambda_k = 1-(1-{args.lambda1})^(2k+1); noiseless = lambda1=0\n", flush=True)

    out = {"experiment": "exp79_noise_inversion_killtest", "cycle": 6270, "author": "elder",
           "seeds": args.seeds, "lambda1": args.lambda1, "shots": args.shots, "results": {}}

    verdicts = {}
    for a in A_VALUES:
        print(f"=== a*={a} ===", flush=True)
        print(f"  {'budget(k)':<12}{'oracle':>9} | {'NOISELESS ci/cov/err':>30} | {'NOISY ci/cov/err':>30} | matched-budget verdict", flush=True)
        rows = []
        for K in range(0, K_MAX + 1):
            ks = list(range(0, K + 1))
            clean = run_condition(a, ks, 0.0, args.shots, args.seeds)
            noisy = run_condition(a, ks, args.lambda1, args.shots, args.seeds)
            narrower = noisy["mean_ci_width"] < clean["mean_ci_width"]
            cov_ok = noisy["coverage"] >= 0.90
            tag = ("NARROWER" if narrower else "wider") + ("/" ) + ("cov_ok" if cov_ok else "UNDER-COVERS")
            print(f"  k=0..{K:<8}{clean['oracle_calls']:>9} | "
                  f"{clean['mean_ci_width']:.4f}/{clean['coverage']:.2f}/{clean['mean_abs_err']:.4f}      | "
                  f"{noisy['mean_ci_width']:.4f}/{noisy['coverage']:.2f}/{noisy['mean_abs_err']:.4f}      | {tag}", flush=True)
            rows.append({"k_max": K, "oracle_calls": clean["oracle_calls"],
                         "noiseless": clean, "noisy": noisy,
                         "noisy_narrower_at_matched_budget": bool(narrower),
                         "noisy_coverage_ok": bool(cov_ok)})
        out["results"][str(a)] = rows
        # verdict for this a*: across budgets, is noisy ever narrower-AND-covered at matched budget?
        any_real_benefit = any(r["noisy_narrower_at_matched_budget"] and r["noisy_coverage_ok"]
                               and r["noisy"]["mean_abs_err"] <= r["noiseless"]["mean_abs_err"] for r in rows)
        ever_narrower = any(r["noisy_narrower_at_matched_budget"] for r in rows)
        undercover = any(r["noisy_narrower_at_matched_budget"] and not r["noisy_coverage_ok"] for r in rows)
        verdicts[str(a)] = {"real_benefit_at_matched_budget": any_real_benefit,
                            "ever_narrower_matched": ever_narrower,
                            "narrower_but_undercovers": undercover}
        print(f"  -> a*={a}: real_benefit_at_matched_budget={any_real_benefit} "
              f"(narrower-but-undercovers={undercover})\n", flush=True)

    out["verdicts"] = verdicts
    overall_confirm = any(v["real_benefit_at_matched_budget"] for v in verdicts.values())
    out["overall_verdict"] = ("CONFIRM: noise is a resource at matched budget" if overall_confirm
                              else "KILL: no matched-budget+covered narrowing -> paradox was a query/coverage artifact")
    print("================ OVERALL ================", flush=True)
    print(f"  {out['overall_verdict']}", flush=True)
    print("  (If KILL: the Finding-10 'narrowing' came from noisy runs spending MORE oracle calls", flush=True)
    print("   and/or under-covering — controlling for budget+coverage removes the benefit.)", flush=True)

    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results", "exp79_noise_inversion_killtest.json")
    with open(path, "w") as f:
        json.dump(out, f, indent=2)
    print(f"\n  saved -> {path}", flush=True)


if __name__ == "__main__":
    main()
