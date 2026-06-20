#!/usr/bin/env python3
"""
Exp59: x0-Selection — does the opt-seed gate warm-start LIFT via p3-anchor quality
or via cold-baseline luck?   Elder C6017 (pre-reg + build)

Pre-registration: /droid/repos/quantum/experiments/exp59-x0-selection-preregistration.md
                  DC1.5 state/experiments/c6017-exp59-x0-selection.json

THE GAP THIS CLOSES
  Finding 29 (Exp57, C6011) established that warm-start lift is x0-GATED: the opt-seed
  explains ~69.7% of lift variance (graph only 8.4%). One "warm-unfriendly" seed (44)
  produced NEGATIVE lift on all four instances. But lift = r_warm_p5 - r_cold_p5
  CONFLATES two mechanisms:
    (A) warm-anchor path : the seed's p3 optimization lands a BAD anchor (low r_p3_base)
                           -> padded p5 warm-start inherits a poor floor -> low r_warm.
    (B) cold-luck path   : the seed's cold p5 x0 happens to land an unusually GOOD
                           cold baseline -> lift is negative even though warm is fine.
  C6011 could not separate these (3 seeds, lift only). This experiment varies x0 across
  N=12 seeds on the FIXED reference instance (graph held constant — justified by C6011's
  8.4% graph share) and DECOMPOSES the gating path. It also tests whether any CHEAP
  a-priori x0 statistic predicts anchor quality (=> an a-priori selection filter), vs the
  fallback empirical rule (multi-start p3, keep the best anchor, then pad to p5).

  Mechanistically this UNIFIES three threads:
    - C6011  : x0 gates lift  (the WHAT)
    - C5980  : p5 escape is INHERITED from the p3 anchor (monotone floor) — the candidate WHY
    - Whisper P-C4208-a : p3-anchor quality = the joint lever
  If path (A) dominates, "x0 selection" reduces to "p3-anchor selection" — and the actionable
  rule is best-of-k p3 multi-start (cheaper than p5) before the single p5 warm-start.

DESIGN
  Instance = EDGES_20 (the reference; every prior escape/warm-start finding lives here).
  Per opt-seed (np.random.seed(seed) reproduces BOTH x0 draws, matching Exp54/57):
    cold_p5 : COBYLA p=5 from random x0_cold (len 10)            -> r_cold,  x0_cold
    p3_base : COBYLA p=3 from random x0_p3   (len 6)             -> r_p3,    x0_p3
    warm_p5 : pad best p3 params to p5 (zeros = identity) -> COBYLA -> r_warm
  lift = r_warm - r_cold.
  Record x0_cold / x0_p3 vectors + cheap a-priori stats (mean, std, min, max, |x-pi| mean).

  Fidelity matches the Exp57 EDGES_20 pilot cells (256 shots, maxiter 20, FakeMarrakesh)
  so seeds 42/43/44 cross-check against the pilot's EDGES_20_ref column.

HYPOTHESES (named observables, pre-disclosed; graded against these — no post-hoc threshold)
  H1 (MEDIATION, PRIMARY): warm-anchor quality drives lift.
      Spearman rho(r_p3_base, r_warm_p5) > 0  AND  rho(r_p3_base, lift) > +0.30.
      REFUTE if rho(r_p3_base, lift) <= 0  (=> lift gating is NOT via anchor quality).
  H2 (PATH DOMINANCE): report |corr(r_warm, lift)| vs |corr(r_cold, lift)| and the
      variance decomposition Var(lift) = Var(r_warm)+Var(r_cold)-2Cov. Classify the
      dominant path (warm-anchor vs cold-luck). Pre-disclosed DIRECTION: expect warm-anchor.
  H3 (A-PRIORI x0 STAT): does any cheap stat of x0_p3 (mean / std / |x-pi| mean) predict
      r_p3_base at |rho| > 0.30?  Pre-disclosed PRIOR: NULL (COBYLA from any uniform x0 in
      a multi-modal landscape reaches varied local optima with no simple a-priori map).
      A NULL here is the INFORMATIVE result: it means the x0-selection rule must be the
      empirical best-of-k p3 multi-start, not an a-priori filter.

SCOPE / HONESTY
  - PILOT fidelity (256 sh / maxiter 20). Establishes SIGN and rough magnitude of the
    mediation, not a definitive 1024sh campaign. N=12 is a real distribution (vs C6011's 3)
    but still small; Spearman on N=12 is reported with its caveat, no p-value fishing.
  - Single instance by DESIGN (isolates the dominant knob); cross-instance is C6011-settled
    (graph 8.4%). Generalization of the MEDIATION across instances = a separate future arm.
  - seeds retained as drawn; no dropping of inconvenient seeds (C5923 flattering-result
    discipline — Exp57 retained seed44).

USAGE
  python3 run_exp59_x0_selection.py --smoke   # 3 seeds, 128sh, maxiter 8 — plumbing/timing
  python3 run_exp59_x0_selection.py --run      # 12 seeds, 256sh, maxiter 20 — the real run (~13h, background)
"""
import sys, os, json, time, argparse
import numpy as np
from scipy.optimize import minimize

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_exp46_fast import (
    EDGES_20, N_QUBITS_20,
    brute_force_max_cut,
    build_parameterized_xbasis_qaoa,
    evaluate_with_transpiled,
)
from run_exp54_warmstart import optimize_cobyla_ws, pad_params
from qiskit import transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel
from qiskit_ibm_runtime.fake_provider import FakeMarrakesh

OPT_LEVEL = 1
EDGES_20_THRESHOLD = 0.640   # reported for context only; NOT the metric

CKPT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "..", "results", "exp59_checkpoint.json")
RESULTS = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "experiments", "exp59_results.json")


def x0_stats(x):
    """Cheap a-priori statistics of an init vector (computable BEFORE any optimization)."""
    x = np.asarray(x, dtype=float)
    return {
        "mean": float(np.mean(x)),
        "std": float(np.std(x)),
        "min": float(np.min(x)),
        "max": float(np.max(x)),
        "abs_dist_pi_mean": float(np.mean(np.abs(x - np.pi))),
    }


def _load_ckpt():
    if os.path.exists(CKPT):
        try:
            return json.load(open(CKPT))
        except (json.JSONDecodeError, OSError):
            return {}
    return {}


def _save_ckpt(c):
    os.makedirs(os.path.dirname(CKPT), exist_ok=True)
    tmp = CKPT + ".tmp"
    json.dump(c, open(tmp, "w"), indent=2)
    os.replace(tmp, CKPT)


def build_for_p(p, sim, n_qubits, edges):
    qc, gp, bp = build_parameterized_xbasis_qaoa(p, n_qubits, edges)
    tqc = transpile(qc, backend=sim, optimization_level=OPT_LEVEL)
    return tqc, gp, bp


def run_seed(seed, edges, max_cut, shots, maxiter, sim, n_qubits, circuits):
    """cold-p5, p3-base, warm(p3->p5) for one opt-seed on the fixed instance.
    Captures the x0 vectors + a-priori stats so anchor-vs-cold-luck can be decomposed."""
    np.random.seed(seed)
    t0 = time.time()

    # ---- cold-start p5 (random x0 at p=5) ----
    tqc5, gp5, bp5 = circuits[5]
    x0_cold = np.random.uniform(0, 2 * np.pi, 10)
    r_cold, _ = optimize_cobyla_ws(x0_cold, tqc5, gp5, bp5, 5, sim, edges, max_cut,
                                   n_qubits, shots, maxiter)

    # ---- warm-start p5 (p3 base -> pad -> p5) ----
    tqc3, gp3, bp3 = circuits[3]
    x0_p3 = np.random.uniform(0, 2 * np.pi, 6)
    r3, x3 = optimize_cobyla_ws(x0_p3, tqc3, gp3, bp3, 3, sim, edges, max_cut,
                                n_qubits, shots, maxiter)
    x0_warm = pad_params(x3, 3, 5)
    r_warm, _ = optimize_cobyla_ws(x0_warm, tqc5, gp5, bp5, 5, sim, edges, max_cut,
                                   n_qubits, shots, maxiter)

    rec = {"seed": seed,
           "r_cold_p5": r_cold, "r_p3_base": r3, "r_warm_p5": r_warm,
           "lift": r_warm - r_cold,
           "x0_cold": x0_cold.tolist(), "x0_p3": x0_p3.tolist(),
           "x0_cold_stats": x0_stats(x0_cold), "x0_p3_stats": x0_stats(x0_p3),
           "elapsed_s": time.time() - t0}
    print(f"  seed={seed}  cold={r_cold:.4f}  p3={r3:.4f}  warm={r_warm:.4f}"
          f"  lift={r_warm - r_cold:+.4f}  ({rec['elapsed_s']:.0f}s)", flush=True)
    return rec


def _spearman(a, b):
    """Spearman rho via rank-Pearson (no scipy.stats dep). Returns None if degenerate."""
    a = np.asarray(a, dtype=float); b = np.asarray(b, dtype=float)
    if len(a) < 3:
        return None
    ra = np.argsort(np.argsort(a)).astype(float)
    rb = np.argsort(np.argsort(b)).astype(float)
    if np.std(ra) == 0 or np.std(rb) == 0:
        return None
    return float(np.corrcoef(ra, rb)[0, 1])


def summarize(results):
    rs = sorted(results, key=lambda r: r["seed"])
    cold = [r["r_cold_p5"] for r in rs]
    p3 = [r["r_p3_base"] for r in rs]
    warm = [r["r_warm_p5"] for r in rs]
    lift = [r["lift"] for r in rs]

    print("\n" + "=" * 70)
    print(f"SUMMARY — Exp59 x0-selection, N={len(rs)} seeds on EDGES_20")
    print("=" * 70)
    print(f"  cold  mean={np.mean(cold):.4f} std={np.std(cold):.4f}")
    print(f"  p3    mean={np.mean(p3):.4f} std={np.std(p3):.4f}")
    print(f"  warm  mean={np.mean(warm):.4f} std={np.std(warm):.4f}")
    print(f"  lift  mean={np.mean(lift):+.4f} std={np.std(lift):.4f}  "
          f"(pos {sum(1 for l in lift if l>0)}/{len(lift)})")

    # H1 mediation
    rho_p3_warm = _spearman(p3, warm)
    rho_p3_lift = _spearman(p3, lift)
    # H2 path dominance
    rho_warm_lift = _spearman(warm, lift)
    rho_cold_lift = _spearman(cold, lift)
    var_lift = float(np.var(lift)); var_warm = float(np.var(warm)); var_cold = float(np.var(cold))
    cov_wc = float(np.cov(warm, cold)[0, 1]) if len(rs) > 1 else 0.0
    # H3 a-priori
    h3 = {}
    for stat in ("mean", "std", "abs_dist_pi_mean"):
        xs = [r["x0_p3_stats"][stat] for r in rs]
        h3[stat] = _spearman(xs, p3)

    print("\n  -- H1 MEDIATION (warm-anchor drives lift) --")
    print(f"     rho(r_p3_base, r_warm_p5) = {rho_p3_warm}")
    print(f"     rho(r_p3_base, lift)      = {rho_p3_lift}")
    h1 = (rho_p3_warm is not None and rho_p3_warm > 0
          and rho_p3_lift is not None and rho_p3_lift > 0.30)
    print(f"     H1 verdict: {'SUPPORTED' if h1 else 'REFUTED / MIXED'}")

    print("\n  -- H2 PATH DOMINANCE (warm-anchor vs cold-luck) --")
    # NOTE: classification uses the VARIANCE SHARE, not |corr| with lift. Both r_warm and
    # r_cold mechanically correlate with their own difference (lift = warm - cold), so |corr|
    # is not a reliable discriminator (smoke-test C6017 confirmed it mis-classified). The
    # marginal-variance share is the principled first-order answer to "which side's variation
    # drives lift variation". corr(.,lift) kept as a secondary diagnostic only.
    denom = var_warm + var_cold
    share_warm = float(var_warm / denom) if denom > 0 else None
    share_cold = float(var_cold / denom) if denom > 0 else None
    dom = None if share_warm is None else ("warm-anchor" if var_warm >= var_cold else "cold-luck")
    print(f"     Var(lift)={var_lift:.5f}  Var(warm)={var_warm:.5f}  Var(cold)={var_cold:.5f}  Cov(w,c)={cov_wc:.5f}")
    print(f"     variance share: warm={share_warm}  cold={share_cold}  -> dominant path: {dom}")
    print(f"     (secondary diag) |rho(r_warm,lift)|={abs(rho_warm_lift) if rho_warm_lift is not None else None}  "
          f"|rho(r_cold,lift)|={abs(rho_cold_lift) if rho_cold_lift is not None else None}")

    print("\n  -- H3 A-PRIORI x0 STAT predicts r_p3_base? --")
    for stat, rho in h3.items():
        print(f"     rho(x0_p3.{stat}, r_p3_base) = {rho}")
    h3_any = any(rho is not None and abs(rho) > 0.30 for rho in h3.values())
    print(f"     H3 verdict: {'A-PRIORI SIGNAL FOUND' if h3_any else 'NULL -> use empirical best-of-k p3 multi-start'}")

    return {
        "n": len(rs),
        "mean": {"cold": float(np.mean(cold)), "p3": float(np.mean(p3)),
                 "warm": float(np.mean(warm)), "lift": float(np.mean(lift))},
        "std": {"cold": float(np.std(cold)), "p3": float(np.std(p3)),
                "warm": float(np.std(warm)), "lift": float(np.std(lift))},
        "lift_pos": sum(1 for l in lift if l > 0),
        "H1": {"rho_p3_warm": rho_p3_warm, "rho_p3_lift": rho_p3_lift, "supported": bool(h1)},
        "H2": {"rho_warm_lift": rho_warm_lift, "rho_cold_lift": rho_cold_lift,
               "var_lift": var_lift, "var_warm": var_warm, "var_cold": var_cold,
               "cov_warm_cold": cov_wc, "var_share_warm": share_warm,
               "var_share_cold": share_cold, "dominant_path": dom},
        "H3": {"rho_by_stat": h3, "a_priori_signal": bool(h3_any)},
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--run", action="store_true")
    args = ap.parse_args()
    if not (args.smoke or args.run):
        print("Specify --smoke | --run. Refusing to guess.")
        sys.exit(2)

    if args.smoke:
        opt_seeds, shots, maxiter, mode = [42, 43, 44], 128, 8, "SMOKE"
    else:
        # 42/43/44 reproduce the Exp57 EDGES_20 pilot column (cross-check); 45-53 are new.
        opt_seeds, shots, maxiter, mode = list(range(42, 54)), 256, 20, "RUN"

    edges, n_qubits = EDGES_20, N_QUBITS_20
    print("=" * 70)
    print(f"Exp59 x0-Selection — {mode}")
    print(f"instance=EDGES_20  opt_seeds={opt_seeds}  shots={shots}  maxiter={maxiter}")
    print(f"metric = lift = r_warm_p5 - r_cold_p5 ; decompose anchor(p3) vs cold-luck")
    print("=" * 70, flush=True)

    fake = FakeMarrakesh()
    sim = AerSimulator(noise_model=NoiseModel.from_backend(fake))

    ckpt = _load_ckpt()
    if ckpt.get("mode") and ckpt.get("mode") != mode:
        bak = CKPT + f".stale-{ckpt.get('mode')}.bak"
        os.replace(CKPT, bak)
        print(f"  [reset] checkpoint mode {ckpt.get('mode')} != {mode}; backed up to {bak}", flush=True)
        ckpt = {}
    done = {r["seed"]: r for r in ckpt.get("data", [])}
    if done:
        print(f"  [resume] {len(done)} seed(s) done: {sorted(done)}", flush=True)
    results = list(ckpt.get("data", []))

    max_cut = brute_force_max_cut(n_qubits, edges)
    circuits = {p: build_for_p(p, sim, n_qubits, edges) for p in (3, 5)}
    print(f"--- EDGES_20: max_cut={max_cut}, "
          f"p3depth={circuits[3][0].depth()} p5depth={circuits[5][0].depth()} ---", flush=True)

    for seed in opt_seeds:
        if seed in done:
            continue
        rec = run_seed(seed, edges, max_cut, shots, maxiter, sim, n_qubits, circuits)
        rec["max_cut"] = max_cut
        results.append(rec)
        ck = _load_ckpt()
        ck["mode"] = mode
        ck["data"] = results
        _save_ckpt(ck)

    summary = summarize(results)
    out = {"experiment": "Exp59", "title": "x0-Selection (anchor-vs-cold-luck mediation)",
           "author": "Elder", "cycle": "C6017", "mode": mode, "instance": "EDGES_20",
           "opt_seeds": opt_seeds, "shots": shots, "maxiter": maxiter,
           "edges20_threshold_context": EDGES_20_THRESHOLD,
           "summary": summary, "data": sorted(results, key=lambda r: r["seed"])}
    json.dump(out, open(RESULTS, "w"), indent=2)
    print(f"\n  Wrote {RESULTS}")


if __name__ == "__main__":
    main()
