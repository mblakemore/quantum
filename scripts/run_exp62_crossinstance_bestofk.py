#!/usr/bin/env python3
"""
Exp62: Cross-instance best-of-k anchor selection — does the best-of-k warm-start lift
validated ON EDGES_20 (Exp61/Finding 36, mean Dlift=+0.049, H1 SUPPORTED) GENERALIZE to
DIFFERENT random MaxCut instances, or is the +0.049 an EDGES_20 artifact?
Elder C6102 (pre-reg + build).

Pre-registration: /droid/repos/quantum/experiments/exp62-crossinstance-bestofk-preregistration.md
                  DC1.5 state/experiments/c6102-exp62-crossinstance-bestofk.json

THE GAP THIS CLOSES (the named future arm of Finding 36)
  Finding 36 (C6084) closed the single-instance EDGES_20 warm-start program: best-of-k p3
  anchor selection RECOVERS warm-start lift (H1 interventional SUPPORTED, paired t~3.43,
  mean Dlift=+0.049). Its forward section names ONE open arm explicitly:
    "cross-instance best-of-k remains the named future arm."
  Distinct from Exp60/F35 (C6061), which KILLED cross-instance anchor-VALUE TRANSFER (taking
  instance A's tuned p3 anchor and applying it to instance B — the anchor value is instance-
  LOCAL). Best-of-k is NOT a transfer: it draws k FRESH anchors FOR EACH instance and selects
  the best EMPIRICALLY. So a-priori it SHOULD be instance-agnostic (it is a procedure, not a
  cached value). This experiment TESTS that: run the identical Exp61 paired best-of-k procedure
  on EDGES_20 + 3 fresh random instances and ask whether Dlift>0 replicates off EDGES_20.

  Action it changes (EVI gate, C6044): whether "ADOPT best-of-k p3 pre-selection" (Finding 36's
  decision) is a GENERAL warm-start protocol rule or an EDGES_20-specific result. A REFUTE
  (Dlift<=0 on the majority of new instances) would scope Finding 36's adoption to EDGES_20
  and re-open whether the lift is landscape-specific.

DESIGN (instance-AGNOSTIC by construction; paired; reuses Exp61 run_seed verbatim)
  Instances: EDGES_20_ref (Exp61/57 reference) + 3 fresh random graphs (gen_instance from
  Exp57: same family — 20 nodes / 30 edges, uniform over C(20,2), seeds 101/202/303). All
  instances run at the IDENTICAL pilot budget (k=3, 256sh, maxiter 20) — apples-to-apples; a
  lift on EDGES_20 but not the new instances is interpretable as instance-dependence, not noise.
  Per (instance, seed) we call Exp61.run_seed VERBATIM (no re-derivation):
    Dlift = lift_best - lift_single  (paired; r_cold cancels = r_warm_best - r_warm_single)
  EDGES_20 seeds 42-44 REPRODUCE the first 3 Exp61 RUN cells (regression check: same numbers).

HYPOTHESES (named, pre-disclosed; graded against these — no post-hoc threshold)
  H1 (PRIMARY, generalization): best-of-k Dlift>0 replicates OFF EDGES_20.
     mean(Dlift) > 0 on a MAJORITY of the 3 NEW instances (>=2/3).
     REFUTE if mean(Dlift) <= 0 on the majority of new instances (=> best-of-k lift is an
     EDGES_20 artifact, Finding 36 adoption scoped to EDGES_20). Mirrors Exp57 H1 framing.
  H2 (magnitude): pooled new-instance mean(Dlift) is the SAME ORDER as EDGES_20's Exp61
     +0.049, i.e. within [0.33x, 3x] -> [+0.016, +0.148]. Outside that band = different regime.
  H3 (rescue structure replicates): pooled rho(r_p3_single, Dlift) < 0 across ALL cells
     (worse single anchor -> bigger best-of-k rescue), the H3 found on EDGES_20 (C5980
     monotone-floor). Tests whether the rescue MECHANISM is instance-agnostic.
  (H2/H3 are direction/order tests at this n; |rho| bars flagged NULL-consistent per C6051.)

SCOPE/HONESTY
  - PILOT fidelity (256 sh / maxiter 20), per-instance N=3 (pooled new-instance N=9). SIGN +
    rough magnitude pilot, NOT a 1024sh campaign. Per-instance N=3 mirrors the Exp57 pilot grid.
  - Same family of instances (uniform random 20n/30e); does NOT test STRUCTURED graphs
    (planted/regular) — that is a separate named arm (Elder C5972 structure-vs-landscape).
  - seeds retained as drawn; NO dropping (C5923; Exp57/59/61 retained seed44).
  - n=9 pooled two-sided a=.05 Spearman sig crit ~0.666; n=3 per-instance is direction-only.
  - reuses Exp61.run_seed -> the per-cell numbers are produced by the SAME validated code path.

USAGE
  python3 run_exp62_crossinstance_bestofk.py --smoke  # ref + 1 new, 2 seeds, 128sh, maxiter 8 — plumbing/timing
  python3 run_exp62_crossinstance_bestofk.py --run     # ref + 3 new, 3 seeds (42-44), k=3, 256sh, maxiter 20 — real (background)
"""
import sys, os, json, time, argparse
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_exp46_fast import EDGES_20, N_QUBITS_20, brute_force_max_cut
# reuse the VALIDATED Exp61 per-seed best-of-k procedure + helpers verbatim
from run_exp61_bestofk_anchor import (
    run_seed, build_for_p, _spearman, _rho_flag, SIG_CRIT_N12,
)
# reuse the Exp57 instance generator (same 20n/30e family)
from run_exp57_instance_generalization import gen_instance
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel
from qiskit_ibm_runtime.fake_provider import FakeMarrakesh

EDGES20_EXP61_DLIFT = 0.0492   # Exp61 RUN mean Dlift on EDGES_20 (Finding 36); H2 reference

CKPT = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                    "..", "results", "exp62_checkpoint.json")
RESULTS = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                       "..", "experiments", "exp62_results.json")


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


def summarize(results, k, ref_label):
    rs = sorted(results, key=lambda r: (r["instance"], r["seed"]))
    insts = sorted(set(r["instance"] for r in rs))
    new_insts = [i for i in insts if i != ref_label]

    print("\n" + "=" * 70)
    print(f"SUMMARY — Exp62 cross-instance best-of-{k}, instances={insts}")
    print("=" * 70)

    per_inst = {}
    for inst in insts:
        cells = [r for r in rs if r["instance"] == inst]
        dlift = [r["d_lift"] for r in cells]
        lift_b = [r["lift_best"] for r in cells]
        lift_s = [r["lift_single"] for r in cells]
        n_inert = sum(1 for r in cells if r["selection_inert"])
        per_inst[inst] = {
            "n": len(cells),
            "mean_d_lift": float(np.mean(dlift)),
            "std_d_lift": float(np.std(dlift)),
            "d_lift_pos": sum(1 for d in dlift if d > 0),
            "mean_lift_best": float(np.mean(lift_b)),
            "mean_lift_single": float(np.mean(lift_s)),
            "selection_inert": n_inert,
        }
        print(f"  {inst:<16} N={len(cells)} meanDlift={np.mean(dlift):+.4f} "
              f"(pos {sum(1 for d in dlift if d>0)}/{len(cells)}) "
              f"liftB={np.mean(lift_b):+.4f} liftS={np.mean(lift_s):+.4f} inert={n_inert}")

    # H1 PRIMARY: Dlift>0 on a majority of NEW instances
    new_pos = [i for i in new_insts if per_inst[i]["mean_d_lift"] > 0]
    h1_need = int(np.ceil(0.5 * len(new_insts))) + (1 if len(new_insts) % 2 == 0 else 0)
    # strict majority: > half
    h1_need = (len(new_insts) // 2) + 1
    h1 = len(new_pos) >= h1_need
    print(f"\n  -- H1 PRIMARY (best-of-k lift generalizes off {ref_label}) --")
    print(f"     NEW instances with mean Dlift>0: {len(new_pos)}/{len(new_insts)} "
          f"(need majority >= {h1_need}) -> {sorted(new_pos)}")
    print(f"     H1 verdict: {'SUPPORTED' if h1 else 'REFUTED (EDGES_20-specific)'}")

    # H2 magnitude: pooled new-instance mean Dlift in [0.33x, 3x] of EDGES_20 Exp61
    new_cells = [r for r in rs if r["instance"] != ref_label]
    pooled_new_dlift = float(np.mean([r["d_lift"] for r in new_cells])) if new_cells else 0.0
    lo, hi = 0.33 * EDGES20_EXP61_DLIFT, 3.0 * EDGES20_EXP61_DLIFT
    h2 = lo <= pooled_new_dlift <= hi
    print(f"\n  -- H2 MAGNITUDE (new-instance Dlift same order as EDGES_20 +{EDGES20_EXP61_DLIFT:.3f}) --")
    print(f"     pooled new-instance mean Dlift = {pooled_new_dlift:+.4f}; band [{lo:+.4f},{hi:+.4f}]")
    print(f"     H2 verdict: {'SUPPORTED (same order)' if h2 else 'OUTSIDE BAND (different regime)'}")

    # H3 rescue structure replicates (pooled across ALL cells)
    p3_single_all = [r["r_p3_single"] for r in rs]
    dlift_all = [r["d_lift"] for r in rs]
    rho_rescue = _spearman(p3_single_all, dlift_all)
    n_all = len(rs)
    h3 = rho_rescue is not None and rho_rescue < -0.30
    print(f"\n  -- H3 RESCUE STRUCTURE replicates (pooled, worse single -> bigger rescue) --")
    print(f"     rho(r_p3_single, Dlift) pooled N={n_all} = {rho_rescue}  [{_rho_flag(rho_rescue, n_all)}]")
    print(f"     H3 verdict: {'SUPPORTED (direction)' if h3 else 'REFUTED / MIXED'}")

    return {
        "n_total": n_all, "k": k, "ref_label": ref_label,
        "instances": insts, "new_instances": new_insts,
        "per_instance": per_inst,
        "edges20_exp61_dlift_ref": EDGES20_EXP61_DLIFT,
        "H1": {"new_pos": sorted(new_pos), "new_total": len(new_insts),
               "need": h1_need, "supported": bool(h1)},
        "H2": {"pooled_new_mean_d_lift": pooled_new_dlift,
               "band": [lo, hi], "supported": bool(h2)},
        "H3": {"rho_single_dlift_pooled": rho_rescue,
               "flag": _rho_flag(rho_rescue, n_all), "supported": bool(h3)},
        "sig_crit_n12": SIG_CRIT_N12,
    }


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true")
    ap.add_argument("--run", action="store_true")
    args = ap.parse_args()
    if not (args.smoke or args.run):
        print("Specify --smoke | --run. Refusing to guess.")
        sys.exit(2)

    ref_label = "EDGES_20_ref"
    if args.smoke:
        new_seeds_for_inst, opt_seeds, k, shots, maxiter, mode = [101], [42, 43], 3, 128, 8, "SMOKE"
    else:
        # ref + 3 new instances, 3 opt-seeds each (42-44). 12 cells x ~58min (Exp61 EDGES_20
        # per-seed) ~= 11.6h background, checkpoint-resumable per cell. Mirrors Exp57 pilot grid.
        new_seeds_for_inst, opt_seeds, k, shots, maxiter, mode = [101, 202, 303], [42, 43, 44], 3, 256, 20, "RUN"

    n_qubits = N_QUBITS_20
    instances = [(ref_label, EDGES_20)]
    for s in new_seeds_for_inst:
        instances.append((f"rand_seed{s}", gen_instance(s)))

    print("=" * 70)
    print(f"Exp62 Cross-instance Best-of-{k} Anchor Selection — {mode}")
    print(f"instances={[lbl for lbl, _ in instances]} opt_seeds={opt_seeds} "
          f"k={k} shots={shots} maxiter={maxiter}")
    print(f"metric = paired Dlift = lift_best - lift_single (reuses Exp61.run_seed verbatim)")
    print(f"H2 ref = EDGES_20 Exp61 mean Dlift +{EDGES20_EXP61_DLIFT:.3f}")
    print("=" * 70, flush=True)

    fake = FakeMarrakesh()
    sim = AerSimulator(noise_model=NoiseModel.from_backend(fake))

    ckpt = _load_ckpt()
    if ckpt.get("mode") and ckpt.get("mode") != mode:
        bak = CKPT + f".stale-{ckpt.get('mode')}.bak"
        os.replace(CKPT, bak)
        print(f"  [reset] checkpoint mode {ckpt.get('mode')} != {mode}; backed up to {bak}", flush=True)
        ckpt = {}
    done = {(r["instance"], r["seed"]): r for r in ckpt.get("data", [])}
    if done:
        print(f"  [resume] {len(done)} (instance,seed) cell(s) done", flush=True)
    results = list(ckpt.get("data", []))

    for inst_label, edges in instances:
        max_cut = brute_force_max_cut(n_qubits, edges)
        circuits = {p: build_for_p(p, sim, n_qubits, edges) for p in (3, 5)}
        print(f"--- {inst_label}: max_cut={max_cut}, "
              f"p3depth={circuits[3][0].depth()} p5depth={circuits[5][0].depth()} ---", flush=True)
        for seed in opt_seeds:
            if (inst_label, seed) in done:
                continue
            rec = run_seed(seed, k, edges, max_cut, shots, maxiter, sim, n_qubits, circuits)
            rec["instance"] = inst_label
            rec["max_cut"] = max_cut
            results.append(rec)
            ck = _load_ckpt()
            ck["mode"] = mode
            ck["data"] = results
            _save_ckpt(ck)

    summary = summarize(results, k, ref_label)
    out = {"experiment": "Exp62",
           "title": "Cross-instance best-of-k p3 anchor selection generalization",
           "author": "Elder", "cycle": "C6102", "mode": mode,
           "instances": [lbl for lbl, _ in instances],
           "opt_seeds": opt_seeds, "k": k, "shots": shots, "maxiter": maxiter,
           "summary": summary,
           "data": sorted(results, key=lambda r: (r["instance"], r["seed"]))}
    json.dump(out, open(RESULTS, "w"), indent=2)
    print(f"\n  Wrote {RESULTS}")


if __name__ == "__main__":
    main()
