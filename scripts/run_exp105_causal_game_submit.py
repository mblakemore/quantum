#!/usr/bin/env python3
"""
Exp105 — Causal Discrimination Game: HARDWARE SUBMIT (Ember C4117)
Pre-reg: experiments/exp105-causal-game-preregistration.md (FROZEN before this runs --submit)
Sim:     experiments/exp105_causal_game_feasibility.py (both gates PASS; skeleton {4:52};
         FakeMarrakesh q* success 0.9820 vs bound 0.8690 / grade constant 0.8695)
Cross-check: Whisper C4525 APPROVE — required skeleton padding implemented, recs 1+2 adopted.

ONE SamplerV2 job (single calibration window):
  51 game circuits (padded uniform 4-CZ skeleton) x 2000 shots,
  51 definite-order null circuits x 1000 shots,
  6 sentinel PUBs (F77 (X,X)/(X,Z) switch pair x 3 replicates at START/MID/END) x 2000 shots.
Game+null order shuffled with pre-registered seed 4117; sentinels pinned.

Usage:
  python3 run_exp105_causal_game_submit.py --scan     # FREE: pick pair, live re-audit, no spend
  python3 run_exp105_causal_game_submit.py --submit   # spends QPU (shared budget)
"""
import os, sys, json, argparse
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
sys.path.insert(0, os.path.join(HERE, '..', 'experiments'))
from run_exp66_qpu_partb import _get_ibm_service
from exp105_causal_game_feasibility import (
    UNITARIES, parse_pair, commutes, build_game_circuit, QIJ_PATH)

BACKEND = "ibm_marrakesh"
SHOTS_GAME, SHOTS_NULL, SHOTS_SENT = 2000, 1000, 2000
SHUFFLE_SEED = 4117            # pre-registered
GRADE_CONSTANT = 0.8695        # bound 0.869028 rounded UP (pre-reg rule 2)
SENTINEL_MIN_DISC = 1.60       # pre-reg abort gate on MIN of 3 replicates
NULL_GATE_MAX = 0.70


def pick_pair(backend):
    """Calibration-gated: min (2q error + both readouts) over coupled edges (exp91 logic)."""
    target = backend.target
    twoq_name = 'cz' if 'cz' in target.operation_names else (
        'ecr' if 'ecr' in target.operation_names else None)
    best, best_cost = None, 1e9
    for (a, b), inst in (target[twoq_name] if twoq_name else {}).items():
        err2 = getattr(inst, 'error', None)
        if err2 is None:
            continue
        try:
            roa = target['measure'][(a,)].error
            rob = target['measure'][(b,)].error
        except Exception:
            roa = rob = 0.0
        cost = err2 + (roa or 0) + (rob or 0)
        if cost < best_cost:
            best_cost, best = cost, (a, b)
    return best, best_cost, twoq_name


def build_all():
    """Return list of (label, kind, circuit, shots, meta) in FINAL pub order."""
    with open(QIJ_PATH) as f:
        qij = json.load(f)
    qpairs = {}
    for key, w in qij['q_star_commuting'].items():
        qpairs[key] = (float(w), True)
    for key, w in qij['q_star_anticommuting'].items():
        qpairs[key] = (float(w), False)

    entries = []
    for key, (w, is_comm) in sorted(qpairs.items()):
        a, b = parse_pair(key)
        assert commutes(a, b) == is_comm
        entries.append((f"game{key}", 'game', build_game_circuit(a, b), SHOTS_GAME,
                        {'pair': key, 'q': w, 'commuting': is_comm}))
        entries.append((f"null{key}", 'null', build_game_circuit(a, b, definite=True), SHOTS_NULL,
                        {'pair': key, 'q': w, 'commuting': is_comm}))

    rng = np.random.default_rng(SHUFFLE_SEED)
    order = rng.permutation(len(entries))
    shuffled = [entries[i] for i in order]

    def sentinel_block(tag):
        return [(f"sent_{tag}_commute", 'sentinel', build_game_circuit('X', 'X'), SHOTS_SENT,
                 {'pair': '(X,X)', 'commuting': True, 'replicate': tag}),
                (f"sent_{tag}_anticommute", 'sentinel', build_game_circuit('X', 'Z'), SHOTS_SENT,
                 {'pair': '(X,Z)', 'commuting': False, 'replicate': tag})]

    mid = len(shuffled) // 2
    final = (sentinel_block('start') + shuffled[:mid]
             + sentinel_block('mid') + shuffled[mid:] + sentinel_block('end'))
    return final


def transpile_and_audit(backend, layout, entries):
    from qiskit import transpile
    tqcs, metas, ok = [], [], True
    for label, kind, qc, shots, meta in entries:
        tqc = transpile(qc, backend=backend, initial_layout=list(layout),
                        optimization_level=1, seed_transpiler=42)
        twoq = sum(1 for i in tqc.data
                   if i.operation.num_qubits == 2 and i.operation.name != 'barrier')
        # LIVE RE-AUDIT (pre-reg kill condition): game + sentinel circuits exactly 4,
        # null arm exactly 0 (locals only)
        want = 4 if kind in ('game', 'sentinel') else 0
        good = (twoq == want)
        ok &= good
        if not good:
            print(f"  AUDIT FAIL {label}: twoq={twoq} want={want}")
        tqcs.append(tqc)
        metas.append({'label': label, 'kind': kind, 'shots': shots,
                      'depth': tqc.depth(), 'twoq': twoq, **meta})
    return tqcs, metas, ok


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--scan", action="store_true")
    ap.add_argument("--submit", action="store_true")
    args = ap.parse_args()

    svc = _get_ibm_service()
    backend = svc.backend(BACKEND)
    st = backend.status()
    print(f"Backend {backend.name}: operational={st.operational} pending={st.pending_jobs}", flush=True)
    try:
        u = svc.usage()
        print(f"QPU budget: {u.get('usage_remaining_seconds')}s remaining / limit {u.get('usage_limit_seconds')}s", flush=True)
    except Exception as e:
        print("usage probe:", e)

    pair, cost, twoq_name = pick_pair(backend)
    print(f"Calibration-gated pair {pair} (2q={twoq_name}, cost={cost:.5f})", flush=True)

    entries = build_all()
    n_game = sum(1 for e in entries if e[1] == 'game')
    n_null = sum(1 for e in entries if e[1] == 'null')
    n_sent = sum(1 for e in entries if e[1] == 'sentinel')
    total_shots = sum(e[3] for e in entries)
    print(f"PUBs: {len(entries)} (game {n_game} / null {n_null} / sentinel {n_sent}), "
          f"total shots {total_shots}, shuffle seed {SHUFFLE_SEED}", flush=True)

    print("Transpiling + LIVE re-audit on real target...", flush=True)
    tqcs, metas, audit_ok = transpile_and_audit(backend, pair, entries)
    hist = {}
    for m in metas:
        if m['kind'] == 'game':
            hist[m['twoq']] = hist.get(m['twoq'], 0) + 1
    print(f"  game-circuit 2q histogram on LIVE target: {hist}")
    print(f"  LIVE AUDIT: {'PASS' if audit_ok else 'FAIL'}", flush=True)
    if not audit_ok:
        print("ABORT per pre-reg: live target drifted from audited skeleton. "
              "Re-audit/re-solve before any spend.")
        return 1

    if args.scan or not args.submit:
        print("\n--scan complete (FREE). Re-run with --submit to spend QPU.")
        return 0

    from qiskit_ibm_runtime import SamplerV2
    sampler = SamplerV2(mode=backend)
    pubs = [(tqc, None, m['shots']) for tqc, m in zip(tqcs, metas)]
    job = sampler.run(pubs)
    jid = job.job_id()
    manifest = {
        "experiment": "exp105-causal-game",
        "cycle": "C4117-ember", "backend": BACKEND,
        "prereg": "experiments/exp105-causal-game-preregistration.md",
        "grade_constant": GRADE_CONSTANT,
        "sentinel_min_disc": SENTINEL_MIN_DISC, "null_gate_max": NULL_GATE_MAX,
        "shuffle_seed": SHUFFLE_SEED,
        "shots": {"game": SHOTS_GAME, "null": SHOTS_NULL, "sentinel": SHOTS_SENT},
        "pair": list(pair), "pair_cost": cost, "twoq_gate": twoq_name,
        "job_id": jid, "metas": metas,
    }
    outp = os.path.join(HERE, '..', 'results', 'exp105_jobids.json')
    with open(outp, 'w') as f:
        json.dump(manifest, f, indent=1)
    print(f"\nSubmitted ONE job, {len(pubs)} PUBs -> job_id={jid}")
    print(f"Manifest -> {os.path.abspath(outp)}")
    print("Grade after drain per FROZEN rule: sentinel min-DISC gate, null gate, "
          f"WIN = p_hat - 5*SE_w > {GRADE_CONSTANT}.")
    return 0


if __name__ == '__main__':
    sys.exit(main())
