#!/usr/bin/env python3
"""NON-DIAGONAL GRADIENT — grind as a function of path quality, both dies (Whisper C5073,
Creator GO in-terminal; upgrades the resolved 2x2 into a dose-response).

DESIGN: per die, the switch instrument (floor/science/polarity, one code path) flies on
2 additional path-quality rungs targeting ~2x and ~3x the die's best-path score, chosen from
the full linear-4-path enumeration. ALIVE-BAND GUARD (frozen): predicted floor visibility
V_f_pred = exp(-26 * score) must be >= 0.3 (k=26 is the CONSERVATIVE constant fitted from the
two banked best-path floors: marrakesh 0.0246->0.533 gives k~25.6; aachen 0.0162->0.834 gives
k~11.2); rungs beyond score ~0.046 are SKIPPED AND NAMED, never flown dead. Combined with the
two banked best-path cells, each die gets a 3-point grind-vs-score curve.

REGISTERED READINGS (either pays):
  MONOTONE-GRADED: deficit grows with score across rungs (both dies consistent) -> the grind
    is aggregate-quality-driven; threshold score estimated by interpolation to deficit=3se.
  NON-GRADED: flat-then-jump or noisy -> discrete-defect mechanism (specific bad couplers,
    not aggregate quality) - localizes the mechanism, equally a result.
  ALL-CLEAN: no rung grinds inside the alive band -> threshold > 0.046 bound; the grind
    lives only on silicon too weak to host the instrument (consistent with marrakesh-auto).
Gates per rung: polarity <= -0.5, floor >= 0.3 (measured; a dead rung despite the guard is
reported as guard-model error). Same P-G3 deficit rule, depth-normalized per rung.
Accounts: aachen IBMQ_TOKEN, marrakesh IBMQ_ALT4. ~6 pubs x 8000 per die.
"""
import argparse, json, os, sys, math
import numpy as np
from qiskit import transpile
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
from exp_gear3_switch_gearbox_whisper_c5073 import switch_circuit
from exp_aachen_nondiag_refly_whisper_c5073 import best_path

SHOTS = 8000
K_ALIVE = 26.0
V_MIN = 0.3
BEST = {"ibm_aachen": 0.0162, "ibm_marrakesh": 0.0246}
ACCT = {"ibm_aachen": "IBMQ_TOKEN", "ibm_marrakesh": "IBMQ_ALT4"}


def all_paths_scored(backend, length=4):
    target = backend.target
    twoq = "cz" if "cz" in target.operation_names else "ecr"
    err2 = {}
    for (a, b) in target[twoq]:
        e = target[twoq][(a, b)].error
        err2[(a, b)] = err2[(b, a)] = (e if e is not None else 0.05)
    ro = {}
    for (q,) in target["measure"]:
        e = target["measure"][(q,)].error
        ro[q] = e if e is not None else 0.05
    adj = {}
    for (a, b) in err2:
        adj.setdefault(a, set()).add(b)
    out = []
    def extend(path):
        if len(path) == length:
            s = sum(err2[(path[i], path[i+1])] for i in range(length-1)) + sum(ro[q] for q in path)
            out.append((s, list(path)))
            return
        for nxt in adj.get(path[-1], ()):
            if nxt not in path:
                path.append(nxt); extend(path); path.pop()
    for q in adj:
        extend([q])
    return sorted(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--backend", required=True)
    ap.add_argument("--submit", action="store_true")
    a = ap.parse_args()
    from qiskit_ibm_runtime import SamplerV2
    from ibm_multi_account import service_for_submission
    svc = service_for_submission(ACCT[a.backend])
    backend = svc.backend(a.backend)
    props = backend.properties()
    print(f"{a.backend} cal epoch: {props.last_update_date}")
    paths = all_paths_scored(backend)
    base = BEST[a.backend]
    # AMENDMENT (pre-flight, declared): fixed 2x/3x multipliers overshoot marrakesh's
    # razor-thin alive band (2x best = 0.0493 -> predicted floor 0.28, guard refuses).
    # Rung targets now FILL THE ALIVE BAND: base + (band_edge - base) * {1/3, 2/3},
    # band_edge = ln(1/V_MIN)/K_ALIVE. Guard unchanged and still dominates.
    band_edge = math.log(1.0 / V_MIN) / K_ALIVE
    rungs = []
    for frac in (1/3, 2/3):
        tgt = base + (band_edge - base) * frac
        cand = min(paths, key=lambda sp: abs(sp[0] - tgt))
        vpred = math.exp(-K_ALIVE * cand[0])
        if vpred < V_MIN:
            print(f"  rung f{frac:.2f}: SKIPPED-AND-NAMED (score {cand[0]:.4f}, predicted floor {vpred:.2f} < {V_MIN})")
            continue
        rungs.append((frac, cand[0], cand[1], vpred))
        print(f"  rung f{frac:.2f}: path {cand[1]} score {cand[0]:.4f} predicted floor {vpred:.2f}")
    if not rungs:
        print("NO-TEST: no rungs inside the alive band"); return

    pubs, meta = [], []
    for mult, score, path, vpred in rungs:
        layout = [path[1], path[0], path[2], path[3]]
        for arm in ("floor", "science", "polarity"):
            qc = switch_circuit(arm)
            tqc = transpile(qc, backend, optimization_level=1, seed_transpiler=3,
                            initial_layout=layout)
            pubs.append((tqc, None, SHOTS))
            meta.append({"block": f"f{mult:.2f}_{arm}", "frac": mult, "score": score,
                         "path": path, "vpred": vpred, "arm": arm, "shots": SHOTS,
                         "cz_count": sum(1 for i in tqc.data if i.operation.num_qubits == 2)})
            print(f"  [$0-validate] f{mult:.2f}/{arm}: depth {tqc.depth()}, 2q {meta[-1]['cz_count']}")

    out = os.path.join(HERE, "..", "results",
                       f"exp_nondiag_gradient_{a.backend.replace('ibm_','')}_c5073_manifest.json")
    man = {"card": "exp_nondiag_gradient", "cycle": "C5073", "substrate": "claude-fable-5",
           "backend": a.backend, "cal_epoch": str(props.last_update_date), "shots": SHOTS,
           "account": ACCT[a.backend], "rungs": [{"frac": m, "score": s, "path": p, "vpred": v}
                                                  for m, s, p, v in rungs],
           "best_cell_banked": {"score": base,
                                "decoded": "exp_aachen_nondiag_refly_decoded_c5073.json" if a.backend == "ibm_aachen"
                                           else "exp_nondiag_bestpath_marrakesh_decoded_c5073.json"},
           "prereg": "registered readings MONOTONE-GRADED / NON-GRADED / ALL-CLEAN + alive-band guard in docstring",
           "pubs_meta": meta}
    if a.submit:
        man["pending_jobs_at_submit"] = backend.status().pending_jobs
        job = SamplerV2(mode=backend).run(pubs)
        man["job_id"] = job.job_id()
        print(f"SUBMITTED {man['job_id']} to {a.backend} (pending: {man['pending_jobs_at_submit']})")
    else:
        print("[dry] not submitted")
    json.dump(man, open(out, "w"), indent=1)
    print(f"manifest -> {out}")


if __name__ == "__main__":
    main()
