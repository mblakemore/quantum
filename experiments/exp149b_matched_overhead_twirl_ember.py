#!/usr/bin/env python3
"""Exp149b — MATCHED-OVERHEAD twirl re-test (Ember, C4196; Creator queue directive; frontier Q6).

WHY: Exp149 (C4195) tried to test whether the copy-channel confident-wrong inversion is COHERENT by
asking if Pauli-twirling removes it. It FALSIFIED its own prediction, but CONFOUNDED: the twirled
arm wrapped each block in barrier-fenced Pauli frames that added idle/scheduling overhead the BARE
(untwirled) arm never paid. "Twirl helped the deepest case" conflated randomization with overhead.
So the coherence question stayed OPEN.

THE FIX (advisor-hardened): a THREE-arm design at MATCHED SCHEDULED DURATION, isolating the ONE
variable Exp149 confounded — randomization — from overhead.
  • Arm A  BARE      : copy block, no frame. The inversion ANCHOR (is the phenomenon present this
                       calibration window at all?). Not duration-matched — it is the NO-TEST probe.
  • Arm B  FROZEN    : ONE fixed Pauli frame reused every rep. Full frame overhead, NO twirling.
  • Arm C  TWIRLED   : random Pauli frame PER rep. Same frame overhead, WITH twirling.
Compare B vs C at identical scheduled duration:
  C recovers where B still inverts  => the inversion is COHERENT (randomization removed it).
  B and C invert together           => randomization does nothing; Exp149's "twirl helped" was
                                        overhead, coherence NOT established (prediction falsified).
  B recovers too (matched overhead alone removes it) => it was idle/overhead, not coherence.

DURATION-MATCH IS THE LOAD-BEARING GATE (advisor pt.1 — what let the confound through last time).
Exp149's matched-gate summed only 2q gates; twirl adds only 1q Paulis so 2q matched while DURATION
diverged. Here EVERY frame slot is made fixed-duration D = t_x(qubit) regardless of which Pauli is
drawn (I/Z are ~0-pulse, X/Y are ~1-pulse -> compensating delay pads each to D). Then B and C, which
have the SAME slot count per depth, have IDENTICAL scheduled duration BY CONSTRUCTION — and the gate
SCHEDULES both and asserts equality (belt and suspenders). The full {I,X,Y,Z} twirl is preserved.

NO-TEST is PRE-REGISTERED (advisor pt.2): if Arm A does not invert this window (window-lottery,
F81), B-vs-C is VOID — reported NO-TEST, never read as falsification either way.

ARM B IS A SINGLE FROZEN FRAME (advisor pt.3): pooling several distinct fixed frames IS a twirl.
B uses one frozen draw. Caveat stated: a fixed P conjugates E->P.E.P (still coherent), so B's
inversion magnitude may differ from bare A — the clean signature (C recovers where B inverts) is
unaffected.

PRE-REGISTERED (0.55; quantum 0.50-0.65 bucket is well-calibrated, pre-check C4196): at matched
duration, TWIRLED C recovers (p_true>0.5) where FROZEN B still inverts (p_true<0.4).

  python3 exp149b_matched_overhead_twirl_ember.py --gates   --backend ibm_kingston
  python3 exp149b_matched_overhead_twirl_ember.py --prereg
  python3 exp149b_matched_overhead_twirl_ember.py --submit  --backend ibm_kingston
  python3 exp149b_matched_overhead_twirl_ember.py --analyze
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
DEPTHS = [8, 14, 20, 28]        # ep -> copy blocks; ladder matched to Exp148/149 (one anchor + 3 inversion)
K_TWIRL = 12                    # random-frame circuits for Arm C per depth
SHOTS_TW = 167                  # per twirled circuit (K*SHOTS ~ 2000)
SHOTS_FLAT = 2000              # per bare (A) and frozen (B) circuit
FROZEN_SEED = 91010            # Arm B's single frozen frame draw (never varied)


def _pauli(qc, q, p):
    if p == "X": qc.x(q)
    elif p == "Y": qc.y(q)
    elif p == "Z": qc.z(q)
    # "I": no gate (duration equalized by the delay pad below)


def _slot(qc, q, p, dt_x):
    """One fixed-DURATION frame slot: apply Pauli p on q, then pad with a delay so the slot is
    always duration dt_x regardless of which Pauli (I/Z ~0-pulse get full pad; X/Y get less).
    dt_x in `dt` units (backend); if dt_x is None (noiseless/analysis), skip padding."""
    _pauli(qc, q, p)
    if dt_x is not None:
        pad = dt_x if p in ("I", "Z") else max(dt_x - dt_x, 0)  # X/Y ~ one x-pulse ~= dt_x -> pad 0
        # NOTE: X and Y each compile to ~one x-pulse (Y = virtual-Z sandwiched x) ~= dt_x; I,Z ~ 0.
        if pad > 0:
            qc.delay(pad, q)


def build_circuit(n, s, extra_pairs, mode, rng=None, dt_x=None):
    """Simon + copy-channel identity-CX injection with a fixed-duration Pauli frame.
    mode: 'bare' (no frame), 'frozen' (one fixed frame), 'twirl' (random frame per call).
    Returns (qc, pauli_log)."""
    from qiskit import QuantumCircuit
    qc = QuantumCircuit(2 * n, n)
    qc.h(range(n)); qc.barrier()
    qc.compose(SIMON.simon_oracle(n, s), inplace=True); qc.barrier()
    log = []
    fr = np.random.default_rng(FROZEN_SEED) if mode == "frozen" else rng
    for p in range(extra_pairs):
        a, b = p % n, n + (p % n)
        if mode == "bare":
            qc.cx(a, b); qc.barrier(); qc.cx(a, b); qc.barrier()
        else:
            pa, pb = "IXYZ"[fr.integers(4)], "IXYZ"[fr.integers(4)]
            log.append(pa + pb)
            _slot(qc, a, pa, dt_x); _slot(qc, b, pb, dt_x); qc.barrier()
            qc.cx(a, b); qc.barrier(); qc.cx(a, b); qc.barrier()
            _slot(qc, a, pa, dt_x); _slot(qc, b, pb, dt_x); qc.barrier()   # P = P^dagger
    qc.h(range(n)); qc.measure(range(n), range(n))
    return qc, log


def _ys(counts, n):
    return [tuple(y) for y in SIMON._sample_ys(counts, n)]


def _dt_x(backend_name):
    """x-gate duration (in dt) on a representative qubit, for the slot pad. None if unavailable."""
    try:
        from run_exp66_qpu_partb import _get_ibm_service
        be = _get_ibm_service().backend(backend_name)
        tgt = be.target
        for q in range(be.num_qubits):
            props = tgt["x"].get((q,)) if "x" in tgt else None
            if props and props.duration:
                # convert seconds -> dt
                dt = tgt.dt or 1e-9
                return int(round(props.duration / dt))
    except Exception as ex:
        print(f"  (dt_x lookup failed: {ex})")
    return None


# ---------------- gates
def gate_noiseless():
    """Truth gate: every arm recovers planted s at zero noise (bare, frozen, twirl)."""
    from qiskit.primitives import StatevectorSampler
    smp = StatevectorSampler(); rng = np.random.default_rng(1491); checked = 0
    for ep in DEPTHS:
        for mode in ("bare", "frozen", "twirl"):
            qc, _ = build_circuit(N, PLANTED_S, ep, mode, rng if mode == "twirl" else None, dt_x=None)
            d = smp.run([(qc, None, 4000)]).result()[0].data
            reg = list(d.keys())[0]
            s_hat, _ = E148.consensus_decode(_ys(getattr(d, reg).get_counts(), N), N)
            if s_hat != PLANTED_S:
                print(f"  FAIL {mode} ep={ep}: {s_hat}"); return False
            checked += 1
    print(f"  {checked} (mode,depth) cells recover planted s at zero noise (bare+frozen+twirl)")
    return checked > 0


def gate_nonvacuous_and_frozen():
    """(a) Arm C twirl is non-vacuous: K circuits differ, >50% non-I. (b) Arm B frozen is INVARIANT:
    the same frame every rep (else B is accidentally a twirl, advisor pt.3)."""
    rng = np.random.default_rng(14910)
    logsC = [tuple(build_circuit(N, PLANTED_S, DEPTHS[-1], "twirl", rng)[1]) for _ in range(K_TWIRL)]
    distinctC = len(set(logsC))
    allp = [c for log in logsC for pair in log for c in pair]
    fracC = sum(1 for c in allp if c != "I") / max(len(allp), 1)
    logsB = [tuple(build_circuit(N, PLANTED_S, DEPTHS[-1], "frozen")[1]) for _ in range(5)]
    frozen_invariant = len(set(logsB)) == 1
    ok = distinctC >= max(2, K_TWIRL // 2) and fracC > 0.5 and frozen_invariant
    print(f"  Arm C: distinct={distinctC}/{K_TWIRL} non-I={fracC:.2f} | "
          f"Arm B frozen-invariant across reps={frozen_invariant}")
    print(f"  non-vacuous twirl + frozen-B: {'OK' if ok else 'FAIL — DO NOT FLY'}")
    return ok


def gate_duration_matched(backend_name):
    """LOAD-BEARING (advisor pt.1): SCHEDULE Arm B and Arm C and assert EQUAL total duration per
    depth. This is what Exp149's 2q-only gate missed."""
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit import transpile
    from qiskit.transpiler import PassManager
    from qiskit.transpiler.passes import ASAPScheduleAnalysis, PadDelay
    be = _get_ibm_service().backend(backend_name)
    dt_x = _dt_x(backend_name)
    print(f"  dt_x (x-gate duration, dt units) = {dt_x}")
    if dt_x is None:
        print("  FAIL: cannot read x-gate duration -> cannot certify duration match. DO NOT FLY.")
        return False
    rng = np.random.default_rng(33)
    ok = True
    for ep in DEPTHS:
        b, _ = build_circuit(N, PLANTED_S, ep, "frozen", dt_x=dt_x)
        c, _ = build_circuit(N, PLANTED_S, ep, "twirl", rng, dt_x=dt_x)
        durs = []
        for qc in (b, c):
            tq = transpile(qc, be, optimization_level=1, seed_transpiler=149,
                           scheduling_method="asap")
            durs.append(tq.duration)
        d_b, d_c = durs
        rel = abs(d_b - d_c) / max(d_b, 1)
        m = rel <= 0.02        # 2% scheduled-duration tolerance
        ok &= m
        print(f"  ep={ep:>2}: frozen dur={d_b} twirl dur={d_c} rel_diff={rel:.4f} "
              f"matched={'OK' if m else 'FAIL'}")
    return ok


def prereg():
    doc = {"exp": "149b", "author": "Ember", "cycle": 4196, "written": "pre-decode",
           "question": "At MATCHED SCHEDULED DURATION, does randomization (twirl) — not overhead — "
                       "remove the copy-channel confident-wrong inversion?",
           "arms": {"A_bare": "no frame; inversion ANCHOR / NO-TEST probe",
                    "B_frozen": f"one frozen Pauli frame (seed {FROZEN_SEED}); overhead, no twirl",
                    "C_twirl": "random Pauli frame per rep; overhead + twirl"},
           "prediction": "Arm C recovers (p_true>0.5) where Arm B still inverts (p_true<0.4) — "
                         "isolating randomization => the inversion is COHERENT.",
           "prediction_confidence": 0.55,
           "falsifier": "B and C invert together -> randomization inert, coherence NOT established "
                        "(Exp149's 'twirl helped' was overhead).",
           "NO_TEST": "if Arm A does NOT invert this window (no depth with A p_true<0.4), B-vs-C is "
                      "VOID — reported NO-TEST, not falsification (window-lottery F81).",
           "load_bearing_gate": "SCHEDULED-DURATION match B==C per depth (<=2%), not 2q-count "
                                "(the Exp149 confound). Every frame slot fixed-duration D=t_x.",
           "n": N, "planted_s": PLANTED_S, "depths_ep": DEPTHS, "k_twirl": K_TWIRL,
           "shots_twirl_each": SHOTS_TW, "shots_flat": SHOTS_FLAT, "frozen_seed": FROZEN_SEED}
    json.dump(doc, open(os.path.join(RESULTS, "exp149b_prereg.json"), "w"), indent=1)
    print("pre-registered -> results/exp149b_prereg.json (0.55: twirl removes inversion at matched duration)")


def submit(backend_name):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit import transpile
    from qiskit_ibm_runtime import SamplerV2
    print("=== gate: non-vacuous twirl + frozen-B ===")
    if not gate_nonvacuous_and_frozen():
        print("REFUSING (KILL)."); return 1
    print("=== gate: SCHEDULED-DURATION match (load-bearing) ===")
    if not gate_duration_matched(backend_name):
        print("REFUSING: scheduled durations not matched -> would reproduce the Exp149 confound. "
              "DO NOT FLY."); return 1
    be = _get_ibm_service().backend(backend_name)
    dt_x = _dt_x(backend_name)
    rng = np.random.default_rng(149000)
    pubs, index = [], []
    for ep in DEPTHS:
        a, _ = build_circuit(N, PLANTED_S, ep, "bare", dt_x=dt_x)
        pubs.append((transpile(a, be, optimization_level=1, seed_transpiler=149, scheduling_method="asap"), None, SHOTS_FLAT))
        index.append({"mode": "bare", "ep": ep})
        b, _ = build_circuit(N, PLANTED_S, ep, "frozen", dt_x=dt_x)
        pubs.append((transpile(b, be, optimization_level=1, seed_transpiler=149, scheduling_method="asap"), None, SHOTS_FLAT))
        index.append({"mode": "frozen", "ep": ep})
        for kk in range(K_TWIRL):
            c, _ = build_circuit(N, PLANTED_S, ep, "twirl", rng, dt_x=dt_x)
            pubs.append((transpile(c, be, optimization_level=1, seed_transpiler=149, scheduling_method="asap"), None, SHOTS_TW))
            index.append({"mode": "twirl", "ep": ep, "k": kk})
    outp = os.path.join(RESULTS, "exp149b_manifest.json")
    if os.path.exists(outp):
        print(f"REFUSING: {os.path.basename(outp)} exists."); return 3
    job = SamplerV2(mode=be).run(pubs)
    json.dump({"exp": "149b", "n": N, "planted_s": PLANTED_S, "index": index,
               "backend": backend_name, "job_id": job.job_id(),
               "note": "bare(anchor)+frozen(overhead)+twirl(overhead+random) at matched duration"},
              open(outp, "w"), indent=1)
    print(f"SUBMITTED Exp149b: job {job.job_id()} ({len(pubs)} pubs) -> {os.path.basename(outp)}")
    return 0


def analyze(mp):
    from run_exp66_qpu_partb import _get_ibm_service
    svc = _get_ibm_service()
    man = json.load(open(mp)); n, s = man["n"], man["planted_s"]
    res = svc.job(man["job_id"]).result()
    idx = man["index"]
    pre = json.load(open(os.path.join(RESULTS, "exp149b_prereg.json")))
    agg = {}
    for i, e in enumerate(idx):
        d = res[i].data; reg = list(d.keys())[0]
        ys = _ys(getattr(d, reg).get_counts(), n)
        agg.setdefault((e["mode"], e["ep"]), []).extend(ys)
    print(f"Exp149b | planted s={s} | pre-reg (0.55): twirl removes inversion at matched duration")
    print(f"  {'ep':>3} | {'BARE p_t':>8} | {'FROZEN p_t':>10} {'rec':>4} | {'TWIRL p_t':>9} {'rec':>4}")
    rows = []
    for ep in DEPTHS:
        pa, _, _ = E148.bias(agg[("bare", ep)], n, s)
        pb, _, _ = E148.bias(agg[("frozen", ep)], n, s)
        pc, _, _ = E148.bias(agg[("twirl", ep)], n, s)
        sb, _ = E148.consensus_decode(agg[("frozen", ep)], n)
        sc, _ = E148.consensus_decode(agg[("twirl", ep)], n)
        rows.append({"ep": ep, "bare_p": round(pa, 3), "frozen_p": round(pb, 3),
                     "frozen_rec": sb == s, "twirl_p": round(pc, 3), "twirl_rec": sc == s})
        print(f"  {ep:>3} | {pa:>8.3f} | {pb:>10.3f} {str(sb==s):>4} | {pc:>9.3f} {str(sc==s):>4}")
    # NO-TEST: bare must invert somewhere
    inv_depths = [r["ep"] for r in rows if r["bare_p"] < 0.4]
    if not inv_depths:
        verdict = "NO-TEST: bare arm did not invert this window (window-lottery) — B-vs-C VOID"
    else:
        # among depths where bare inverts, does twirl recover where frozen inverts?
        both = [r for r in rows if r["ep"] in inv_depths and r["frozen_p"] < 0.4]
        if both and all(r["twirl_p"] > 0.5 for r in both):
            verdict = ("TWIRL RECOVERS where FROZEN inverts at matched duration -> inversion is "
                       "COHERENT, randomization removes it (prediction HELD, 0.55)")
        elif both and all(r["twirl_p"] < 0.4 for r in both):
            verdict = ("B and C invert together at matched duration -> randomization inert; "
                       "Exp149's 'twirl helped' was overhead (prediction FALSIFIED)")
        else:
            verdict = "mixed / frozen did not invert where bare did -> inconclusive, see rows"
    out = {"exp": "149b", "rows": rows, "inv_depths_bare": inv_depths, "verdict": verdict, "prereg": pre}
    json.dump(out, open(os.path.join(RESULTS, "exp149b_analysis.json"), "w"), indent=1)
    print(f"\n  VERDICT: {verdict}\n  -> results/exp149b_analysis.json")


def main():
    ap = argparse.ArgumentParser()
    for fl in ("gates", "prereg", "submit", "analyze"):
        ap.add_argument(f"--{fl}", action="store_true")
    ap.add_argument("--manifest"); ap.add_argument("--backend", default="ibm_kingston")
    a = ap.parse_args()
    if a.gates:
        print("=== noiseless truth-gate ==="); g1 = gate_noiseless()
        print("=== non-vacuous twirl + frozen-B gate ==="); g2 = gate_nonvacuous_and_frozen()
        print("=== SCHEDULED-DURATION match gate (load-bearing) ==="); g3 = gate_duration_matched(a.backend)
        print(f"\nGATES: {'ALL PASS' if (g1 and g2 and g3) else 'FAIL'}")
        return 0 if (g1 and g2 and g3) else 1
    if a.prereg: prereg(); return 0
    if a.submit: return submit(a.backend)
    if a.analyze: analyze(a.manifest or os.path.join(RESULTS, "exp149b_manifest.json")); return 0
    ap.print_help(); return 0


if __name__ == "__main__":
    sys.exit(main())
