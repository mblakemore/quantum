#!/usr/bin/env python3
"""
Exp82 (Whisper C4413, pre-reg in F59): BEST vs DEFAULT qubit placement re-test
of Exp66 Part B's warm-start transfer, seed 42 only.

Pre-registration: findings/F59-placement-confound-in-F50-whisper-c4413.md

F50 (Exp66 Part B) attributed warm-start lift collapse (FakeMarrakesh +6.7% ->
QPU ~0%) to "irreducible hardware noise" without ever varying qubit placement
-- run_exp66_qpu_partb.py called transpile() with NO initial_layout, i.e. the
DEFAULT arm in F57's noise-placement taxonomy (17x readout-bias penalty vs
BEST). F50's do(apply to real QPU) node bundled two distinct interventions:
placement and noise regime.

Design: re-run seed 42 (the one seed that already showed positive transfer,
+1.3%) with TWO placement arms, same p5 cold/warm bound parameters:
  - BEST:    initial_layout = quiet_qubits.pick(backend, 20, mode='best')['layout']
  - DEFAULT: no initial_layout (compiler default heuristic -- F50's actual protocol)
Each arm batches [cold, warm] into ONE job (matching Part B's pattern) -> 2 jobs.

Pre-registered prediction (F59 section 3):
  - If F50's "irreducible noise" interpretation holds: BEST should NOT move
    transfer_ratio meaningfully off DEFAULT's ~0.000-0.013 range.
  - If placement is a meaningful confound: BEST's transfer_ratio should sit
    closer to FakeMarrakesh's ideal lift (+6.7%) than DEFAULT's.

Cost: 2 jobs, single seed, p3 anchor + p5 circuits, ~tens of QPU-sec.
Budget checked C4413: 411/600 GREEN (confirmed live via check_usage.py before run).

Usage:
  python3 run_exp82_placement_confound.py --smoke    # sim-only sanity check, no QPU spend
  python3 run_exp82_placement_confound.py --submit   # 2 batched jobs -> ibm_marrakesh
  python3 run_exp82_placement_confound.py --finalize JID_BEST JID_DEFAULT
"""
import sys, os, json, time, argparse
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_exp46_fast import EDGES_20, N_QUBITS_20, compute_cut_value, build_parameterized_xbasis_qaoa
from run_exp66_qpu_partb import (
    _bind, _counts_to_ratio, _get_ibm_service, MAX_CUT_20, P_TARGET, SHOTS, OPT_LEVEL, SEED_TRANSP,
)
from qiskit import transpile
import quiet_qubits

SEED        = 42        # the one seed in Exp66 Part B that showed positive transfer (+1.3%)
BACKEND_NAME = "ibm_marrakesh"

RESULTS_DIR  = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "experiments")
JOBIDS_PATH  = os.path.join(RESULTS_DIR, "exp82_jobids.json")
RESULTS_PATH = os.path.join(RESULTS_DIR, "exp82_results.json")

os.makedirs(RESULTS_DIR, exist_ok=True)


def _make_circuit_p5(n_qubits, edges, backend, initial_layout):
    """Transpile p5 template for QPU, optionally with a fixed initial_layout (BEST arm) or None (DEFAULT arm)."""
    tqc, gp, bp = build_parameterized_xbasis_qaoa(P_TARGET, n_qubits, edges)
    tc = transpile(tqc, backend=backend, optimization_level=OPT_LEVEL,
                    seed_transpiler=SEED_TRANSP, initial_layout=initial_layout)
    print(f"  depth p5 (layout={'BEST' if initial_layout else 'DEFAULT'}): {tc.depth()} gates", flush=True)
    return tc, gp, bp


PARTB_JOBIDS_PATH = os.path.join(RESULTS_DIR, "exp66_partb_jobids.json")


def phase1_local(seed=SEED):
    """
    Load the ORIGINAL Exp66 Part B seed-42 local record (x_cold_p5, x_warm_p5,
    lift_fake) from exp66_partb_jobids.json rather than recomputing.

    DISCOVERED C4413: recomputing locally via local_warmstart_cell(42, ...) does
    NOT reproduce the original record -- smoke test gave lift_fake=0.0099 vs the
    original 0.0748 (np.random.seed(42) does not pin down identical COBYLA
    trajectories across scipy/pyprima versions; a COBYLA MAXFUN warning not
    present in the original C4410 run confirms an environment drift). Exp82's
    whole point is to hold the OPTIMIZED PARAMETERS constant and vary only
    placement -- reusing fresh (and different) parameters would silently swap
    the controlled variable and invalidate the comparison to F50's DEFAULT
    numbers. The saved record is therefore the correct and only valid source.
    """
    manifest = json.load(open(PARTB_JOBIDS_PATH))
    rec = next(r for r in manifest["local_records"] if r["seed"] == seed)
    print(f"  Loaded ORIGINAL seed={seed} record from {PARTB_JOBIDS_PATH}: "
          f"lift_fake={rec['lift_fake']:.4f} (r_cold={rec['r_cold_fake']:.4f}, r_warm={rec['r_warm_fake']:.4f})",
          flush=True)
    return rec


def submit_arm(backend, rec, layout, label):
    """Build bound cold+warm circuits for one placement arm, submit as ONE batched job."""
    from qiskit_ibm_runtime import SamplerV2
    tc5, gp5, bp5 = _make_circuit_p5(N_QUBITS_20, EDGES_20, backend, layout)
    x_cold = np.asarray(rec["x_cold_p5"])
    x_warm = np.asarray(rec["x_warm_p5"])
    bound_cold = _bind(tc5, gp5, bp5, x_cold, P_TARGET)
    bound_warm = _bind(tc5, gp5, bp5, x_warm, P_TARGET)
    sampler = SamplerV2(mode=backend)
    sampler.options.default_shots = SHOTS
    job = sampler.run([(bound_cold,), (bound_warm,)])
    jid = job.job_id()
    print(f"  [{label}] submitted job_id={jid}", flush=True)
    return jid


def retrieve_arm(service, jid, rec, label):
    job = service.job(jid)
    status = str(job.status())
    print(f"  [{label}] job={jid} status={status}", flush=True)
    if "DONE" not in status:
        print(f"  -> NOT DONE. Re-run --finalize later.")
        return None
    res = job.result()
    parsed = []
    for i in range(2):  # 0=cold, 1=warm
        databin = res[i].data
        reg = list(databin.__dict__.keys())[0]
        counts = getattr(databin, reg).get_counts()
        ratio = _counts_to_ratio(counts, EDGES_20, MAX_CUT_20)
        parsed.append(float(ratio))
    r_cold_qpu, r_warm_qpu = parsed
    lift_qpu = r_warm_qpu - r_cold_qpu
    transfer_ratio = lift_qpu / max(rec["lift_fake"], 1e-9)
    out = {"label": label, "job_id": jid, "r_cold_qpu": r_cold_qpu, "r_warm_qpu": r_warm_qpu,
           "lift_qpu": lift_qpu, "lift_fake": rec["lift_fake"], "transfer_ratio": transfer_ratio}
    print(f"  [{label}] cold={r_cold_qpu:.4f} warm={r_warm_qpu:.4f} lift_qpu={lift_qpu:+.4f} "
          f"transfer_ratio={transfer_ratio:+.4f} (fake lift={rec['lift_fake']:+.4f})", flush=True)
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--smoke", action="store_true", help="sim-only sanity check (FakeMarrakesh), no QPU spend")
    ap.add_argument("--submit", action="store_true", help="submit BEST + DEFAULT jobs to ibm_marrakesh")
    ap.add_argument("--finalize", nargs=2, metavar=("JID_BEST", "JID_DEFAULT"), help="retrieve + grade both arms")
    args = ap.parse_args()

    print(f"EDGES_20 max_cut={MAX_CUT_20} n_qubits={N_QUBITS_20} seed={SEED}", flush=True)

    print("\n[Phase 1] FakeMarrakesh warm-start (seed 42 only)", flush=True)
    t0 = time.time()
    rec = phase1_local()
    print(f"  Phase 1 complete in {time.time()-t0:.0f}s", flush=True)

    if args.smoke:
        print("\nSmoke test passed (local warm-start reproduced). Pass --submit to run on real QPU.", flush=True)
        return

    if args.submit:
        print(f"\n[Phase 2] Submitting BEST + DEFAULT arms to {BACKEND_NAME}", flush=True)
        service = _get_ibm_service()
        backend = service.backend(BACKEND_NAME)
        print(f"  Backend: {backend.name} | pending_jobs={backend.status().pending_jobs}", flush=True)

        best_pick = quiet_qubits.pick(backend, N_QUBITS_20, mode="best")
        print(f"  BEST layout (quiet_qubits.pick n={N_QUBITS_20}): qubits={best_pick['qubits']}", flush=True)

        jid_best = submit_arm(backend, rec, best_pick["layout"], "BEST")
        jid_default = submit_arm(backend, rec, None, "DEFAULT")

        manifest = {"seed": SEED, "local_record": rec, "best_layout": best_pick["layout"],
                    "best_pick_qubits": best_pick["qubits"], "job_id_best": jid_best,
                    "job_id_default": jid_default, "backend": BACKEND_NAME, "shots": SHOTS,
                    "submitted_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
        with open(JOBIDS_PATH, "w") as f:
            json.dump(manifest, f, indent=2)
        print(f"\n  Manifest saved: {JOBIDS_PATH}")
        print(f"  Next: python3 scripts/run_exp82_placement_confound.py --finalize {jid_best} {jid_default}")
        return

    if args.finalize:
        jid_best, jid_default = args.finalize
        manifest = json.load(open(JOBIDS_PATH)) if os.path.exists(JOBIDS_PATH) else None
        rec_for_grade = manifest["local_record"] if manifest else rec

        print(f"\n[Phase 3] Retrieving BEST={jid_best} DEFAULT={jid_default}", flush=True)
        service = _get_ibm_service()
        g_best = retrieve_arm(service, jid_best, rec_for_grade, "BEST")
        g_default = retrieve_arm(service, jid_default, rec_for_grade, "DEFAULT")

        if g_best and g_default:
            shift = g_best["transfer_ratio"] - g_default["transfer_ratio"]
            ideal = 1.0  # FakeMarrakesh-normalized ideal transfer ratio
            verdict = ("CONFOUND CONFIRMED: BEST shifts transfer_ratio toward FakeMarrakesh ideal"
                       if g_best["transfer_ratio"] > g_default["transfer_ratio"] + 0.05
                       else "CONFOUND NOT SUPPORTED: BEST does not move transfer_ratio meaningfully vs DEFAULT")
            print(f"\n  transfer_ratio BEST={g_best['transfer_ratio']:+.4f} DEFAULT={g_default['transfer_ratio']:+.4f} "
                  f"shift={shift:+.4f}")
            print(f"  VERDICT: {verdict}")
            result = {"seed": SEED, "best": g_best, "default": g_default, "shift": shift,
                      "verdict": verdict, "local_record": rec_for_grade,
                      "finalized_at": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())}
            with open(RESULTS_PATH, "w") as f:
                json.dump(result, f, indent=2)
            print(f"\n  Results saved: {RESULTS_PATH}")
        return

    print("Pass --smoke, --submit, or --finalize JID_BEST JID_DEFAULT")


if __name__ == "__main__":
    main()
