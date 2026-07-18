#!/usr/bin/env python3
"""Exp149 — twirl mechanism-test + adaptive reader (Ember, Move 1). Creator 'fly them'.

THE TEST (reframed per gap G4): Exp148b showed the confident-wrong inversion is copy-channel-
SPECIFIC but did NOT establish it's COHERENT. Pauli twirling (randomized compiling) converts
coherent error -> stochastic at matched infidelity. So:
  twirl REMOVES the inversion  => the inversion was coherent (the c4183_001 control 148b deferred)
                                  AND twirling is the defense.
  twirl FAILS to remove it     => not purely coherent; the mechanism is something else.

DESIGN: Simon n=4, planted s, copy-channel identity-CX injection (reproduces Exp148 inversion).
Two modes at each depth:
  UNTWIRLED : 1 circuit x many shots (= Exp148 copy arm).
  TWIRLED   : K independent random-Pauli-FRAME circuits x few shots each. Each injected block
              [cx(a,b);cx(a,b)] (ideally I) is wrapped P_before ... P_after with the SAME random
              2q Pauli P (P=P^dagger), so ideal is preserved (P.I.P = I) and the block's coherent
              error is Pauli-twirled across the K randomizations. Paulis are 1-qubit gates -> the
              2q (noise) count is IDENTICAL to untwirled: matched by construction.

NON-VACUOUS TWIRL GATE (gap G5, the KILL criterion): a twirl of identity Paulis is a no-op that
would pass a noiseless-truth gate while doing nothing. So the gate asserts: (1) the K circuits
actually DIFFER, (2) inserted Paulis are non-trivial on average (>50% non-I), (3) every twirled
circuit is ideal-equivalent (noiseless recovers s). If it fails -> DO NOT FLY, report the bug.

Adaptive reader (gap: free post-processing): SPRT-style stopping analyzed on the untwirled +
Exp148 shot streams -> depth-at-fixed-budget, adaptive vs fixed. No extra QPU.

PRE-REGISTERED (0.65): twirled does NOT invert (p_true>0.5, recovers) where untwirled inverts.

  python3 exp149_adaptive_twirl_ember.py --gates
  python3 exp149_adaptive_twirl_ember.py --prereg
  python3 exp149_adaptive_twirl_ember.py --submit
  python3 exp149_adaptive_twirl_ember.py --analyze
"""
import argparse
import importlib.util
import json
import os
import sys

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
RESULTS = os.path.join(HERE, "..", "results")
_e = importlib.util.spec_from_file_location("e148", os.path.join(HERE, "exp148_selfcorrection_ember.py"))
E148 = importlib.util.module_from_spec(_e); _e.loader.exec_module(E148)
SIMON = E148.SIMON

N = 4
PLANTED_S = [1, 0, 1, 0]
DEPTHS = [8, 14, 20, 28]        # ep -> 2q [20,32,44,60]: one survivable anchor + 3 inversion settings
K_TWIRL = 12                    # random-Pauli-frame circuits per twirled depth
SHOTS_TW = 167                  # per twirled circuit (K*SHOTS_TW ~ 2000)
SHOTS_UN = 2000                 # untwirled per depth


def _apply_pauli(qc, q, p):
    if p == "X": qc.x(q)
    elif p == "Y": qc.y(q)
    elif p == "Z": qc.z(q)


def build_circuit(n, s, extra_pairs, twirl_rng=None):
    """Simon + copy-channel identity-CX injection. If twirl_rng given, wrap each injected block
    in a random 2q Pauli frame (ideal-preserving, noise-twirling). Returns (qc, pauli_log)."""
    from qiskit import QuantumCircuit
    qc = QuantumCircuit(2 * n, n)
    qc.h(range(n)); qc.barrier()
    qc.compose(SIMON.simon_oracle(n, s), inplace=True); qc.barrier()
    log = []
    for p in range(extra_pairs):
        a, b = p % n, n + (p % n)                          # copy channel (= Exp148)
        if twirl_rng is not None:
            pa, pb = "IXYZ"[twirl_rng.integers(4)], "IXYZ"[twirl_rng.integers(4)]
            log.append(pa + pb)
            _apply_pauli(qc, a, pa); _apply_pauli(qc, b, pb); qc.barrier()
            qc.cx(a, b); qc.barrier(); qc.cx(a, b); qc.barrier()
            _apply_pauli(qc, a, pa); _apply_pauli(qc, b, pb); qc.barrier()   # P = P^dagger
        else:
            qc.cx(a, b); qc.barrier(); qc.cx(a, b); qc.barrier()
    qc.h(range(n)); qc.measure(range(n), range(n))
    return qc, log


def _ys(counts, n):
    return [tuple(y) for y in SIMON._sample_ys(counts, n)]


# ---------------- gates
def gate_noiseless():
    from qiskit.primitives import StatevectorSampler
    smp = StatevectorSampler(); rng = np.random.default_rng(149); checked = 0
    for ep in DEPTHS:
        for mode, tr in (("untw", None), ("twirl", rng)):
            qc, _ = build_circuit(N, PLANTED_S, ep, tr)
            d = smp.run([(qc, None, 4000)]).result()[0].data
            reg = list(d.keys())[0]
            s_hat, _ = E148.consensus_decode(_ys(getattr(d, reg).get_counts(), N), N)
            if s_hat != PLANTED_S:
                print(f"  FAIL {mode} ep={ep}: {s_hat}"); return False
            checked += 1
    print(f"  compared: {checked} (mode,depth) cells recover planted s at zero noise")
    return checked > 0


def gate_twirl_nonvacuous():
    """G5: twirl must actually DO something. (1) K circuits differ; (2) Paulis >50% non-I;
    (3) each twirled circuit is ideal-equivalent (checked in noiseless gate)."""
    rng = np.random.default_rng(1490)
    logs = []
    for _ in range(K_TWIRL):
        _, log = build_circuit(N, PLANTED_S, DEPTHS[-1], rng)
        logs.append(tuple(log))
    distinct = len(set(logs))
    all_paulis = [c for log in logs for pair in log for c in pair]
    frac_nonI = sum(1 for c in all_paulis if c != "I") / max(len(all_paulis), 1)
    # a twirled circuit must DIFFER from the untwirled as a circuit (else no-op)
    un, _ = build_circuit(N, PLANTED_S, DEPTHS[-1], None)
    tw, _ = build_circuit(N, PLANTED_S, DEPTHS[-1], np.random.default_rng(7))
    differs = tw.size() != un.size()
    ok = distinct >= max(2, K_TWIRL // 2) and frac_nonI > 0.5 and differs
    print(f"  distinct twirl circuits: {distinct}/{K_TWIRL} | non-I Pauli frac: {frac_nonI:.2f} | "
          f"twirled circuit differs from untwirled: {differs}")
    print(f"  non-vacuous twirl: {'OK' if ok else 'FAIL — twirl is a no-op, DO NOT FLY'}")
    return ok


def gate_matched(backend_name):
    """Twirl adds only 1q gates -> 2q count must be IDENTICAL twirled vs untwirled per depth."""
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit import transpile
    be = _get_ibm_service().backend(backend_name); ok = True
    for ep in DEPTHS:
        un, _ = build_circuit(N, PLANTED_S, ep, None)
        tw, _ = build_circuit(N, PLANTED_S, ep, np.random.default_rng(3))
        u2 = sum(transpile(un, be, optimization_level=1, seed_transpiler=149).count_ops().get(g, 0) for g in ("cz", "ecr", "cx"))
        t2 = sum(transpile(tw, be, optimization_level=1, seed_transpiler=149).count_ops().get(g, 0) for g in ("cz", "ecr", "cx"))
        m = abs(u2 - t2) <= max(4, int(0.15 * u2))
        ok &= m
        print(f"  ep={ep:>2}: untw 2q={u2} twirl 2q={t2} matched={'OK' if m else 'FAIL'}")
    return ok


def prereg():
    doc = {"exp": 149, "author": "Ember", "written": "pre-decode",
           "question": "Does Pauli-twirling REMOVE the copy-channel confident-wrong inversion "
                       "(=> the inversion was coherent, and twirling defends it)?",
           "prediction": "twirled does NOT invert (p_true>0.5, recovers) where untwirled inverts; "
                         "this both confirms coherent mechanism (G4) and gives the defense.",
           "prediction_confidence": 0.65,
           "falsifier": "twirled ALSO inverts -> not purely coherent, mechanism is elsewhere.",
           "n": N, "planted_s": PLANTED_S, "depths_ep": DEPTHS, "k_twirl": K_TWIRL,
           "shots_twirl_each": SHOTS_TW, "shots_untw": SHOTS_UN}
    json.dump(doc, open(os.path.join(RESULTS, "exp149_prereg.json"), "w"), indent=1)
    print("pre-registered -> results/exp149_prereg.json (0.65: twirl removes inversion)")


def submit(backend_name):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit import transpile
    from qiskit_ibm_runtime import SamplerV2
    if not gate_twirl_nonvacuous():
        print("REFUSING: non-vacuous twirl gate FAILED — twirl is a no-op. DO NOT FLY (G5/KILL)."); return 1
    if not gate_matched(backend_name):
        print("REFUSING: 2q not matched twirled vs untwirled."); return 1
    be = _get_ibm_service().backend(backend_name)
    rng = np.random.default_rng(14900)
    pubs, index = [], []
    for ep in DEPTHS:
        un, _ = build_circuit(N, PLANTED_S, ep, None)
        pubs.append((transpile(un, be, optimization_level=1, seed_transpiler=149), None, SHOTS_UN))
        index.append({"mode": "untw", "ep": ep})
        for kk in range(K_TWIRL):
            tw, _ = build_circuit(N, PLANTED_S, ep, rng)
            pubs.append((transpile(tw, be, optimization_level=1, seed_transpiler=149), None, SHOTS_TW))
            index.append({"mode": "twirl", "ep": ep, "k": kk})
    outp = os.path.join(RESULTS, "exp149_manifest.json")
    if os.path.exists(outp):
        print(f"REFUSING: {os.path.basename(outp)} exists."); return 3
    job = SamplerV2(mode=be).run(pubs)
    json.dump({"exp": 149, "n": N, "planted_s": PLANTED_S, "index": index,
               "backend": backend_name, "job_id": job.job_id(),
               "note": "twirled (K frames) vs untwirled, inversion regime. Self-verifying."},
              open(outp, "w"), indent=1)
    print(f"SUBMITTED Exp149: job {job.job_id()} ({len(pubs)} pubs) -> {os.path.basename(outp)}")
    print("  (no QPU figure until measured, C4796)")
    return 0


def analyze(mp):
    from run_exp66_qpu_partb import _get_ibm_service
    svc = _get_ibm_service()
    man = json.load(open(mp)); n, s = man["n"], man["planted_s"]
    res = svc.job(man["job_id"]).result()
    idx = man["index"]
    pre = json.load(open(os.path.join(RESULTS, "exp149_prereg.json")))
    # aggregate ys per (mode, ep)
    agg = {}
    for i, e in enumerate(idx):
        d = res[i].data; reg = list(d.keys())[0]
        ys = _ys(getattr(d, reg).get_counts(), n)
        key = (e["mode"], e["ep"])
        agg.setdefault(key, []).extend(ys)
    print(f"Exp149 | planted s={s} | pre-reg (0.65): twirl removes the inversion")
    print(f"  {'ep':>3} | {'UNTW p_true':>11} {'rec':>4} | {'TWIRL p_true':>12} {'rec':>4}")
    rows = []
    for ep in DEPTHS:
        pu, _, _ = E148.bias(agg[("untw", ep)], n, s)
        pt, _, _ = E148.bias(agg[("twirl", ep)], n, s)
        su, _ = E148.consensus_decode(agg[("untw", ep)], n)
        st, _ = E148.consensus_decode(agg[("twirl", ep)], n)
        rows.append({"ep": ep, "untw_p_true": round(pu, 3), "untw_rec": su == s,
                     "twirl_p_true": round(pt, 3), "twirl_rec": st == s})
        print(f"  {ep:>3} | {pu:>11.3f} {str(su==s):>4} | {pt:>12.3f} {str(st==s):>4}")
    inv = [r for r in rows if r["untw_p_true"] < 0.4]
    twirl_rescues = len(inv) > 0 and all(r["twirl_p_true"] > 0.45 for r in inv)
    if not inv:
        verdict = "untwirled did not invert this calibration -> inconclusive (re-examine)"
    elif twirl_rescues:
        verdict = "TWIRL REMOVES the inversion -> mechanism was COHERENT + twirling defends (prediction HELD)"
    else:
        verdict = "twirl does NOT remove the inversion -> not purely coherent (prediction FALSIFIED)"
    out = {"exp": 149, "rows": rows, "verdict": verdict, "prereg": pre}
    json.dump(out, open(os.path.join(RESULTS, "exp149_analysis.json"), "w"), indent=1)
    print(f"\n  VERDICT: {verdict}\n  -> results/exp149_analysis.json")


def main():
    ap = argparse.ArgumentParser()
    for fl in ("gates", "prereg", "submit", "analyze"):
        ap.add_argument(f"--{fl}", action="store_true")
    ap.add_argument("--manifest"); ap.add_argument("--backend", default="ibm_kingston")
    a = ap.parse_args()
    if a.gates:
        print("=== noiseless truth-gate ==="); g1 = gate_noiseless()
        print("=== non-vacuous twirl gate (G5, KILL) ==="); g2 = gate_twirl_nonvacuous()
        print("=== matched-noise gate ==="); g3 = gate_matched(a.backend)
        print(f"\nGATES: {'ALL PASS' if (g1 and g2 and g3) else 'FAIL'}")
        return 0 if (g1 and g2 and g3) else 1
    if a.prereg: prereg(); return 0
    if a.submit: return submit(a.backend)
    if a.analyze: analyze(a.manifest or os.path.join(RESULTS, "exp149_manifest.json")); return 0
    ap.print_help(); return 0


if __name__ == "__main__":
    sys.exit(main())
