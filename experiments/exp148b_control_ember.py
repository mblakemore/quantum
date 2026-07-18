#!/usr/bin/env python3
"""Exp148b — generic-noise CONTROL for the Exp148 confident-wrong inversion (Ember). Creator 'fly it'.

THE CONFOUND being resolved: Exp148 dialed depth by injecting identity CX on cx(a, n+a) — the
oracle's OWN copy-CX pairs — so its regime-B finding (past a depth threshold the true-period bias
INVERTS below 0.5 and the decoder returns a CONFIDENTLY WRONG answer) cannot distinguish:
  (i)  a real property of DEPTH / decoherence (important, general), from
  (ii) structured corruption of the oracle's copy channel specifically (an artifact of WHERE I
       injected). c4183_001: no mechanism claim without the isolating control.

THE CONTROL: same Simon n=4, same planted s, same identity-CX depth ladder MATCHED on 2q-gate
count, co-batched in ONE job (same calibration window — removes cross-job drift as a confound),
two injection modes on the SAME 8 qubits:
  - COPY    : cx(a, n+a)            = the oracle copy pairs (reproduces Exp148, same-cal baseline)
  - GENERIC : cx on NON-copy data pairs (input-input + output-output, never an (i,n+i) copy pair)
Both are identity (CX;CX) logical no-ops; both add the same number of noisy 2q gates to the same
data qubits; only the LOCATION relative to the oracle's parity structure differs.

PRE-REGISTERED PREDICTION (conf 0.60, low — quantum is my worst-calibrated domain and I genuinely
don't know): GENERIC does NOT fully reproduce the inversion — at the deep settings p_true stays
>= ~0.45 (decays toward 0.5, graceful) rather than dropping to Exp148's 0.17-0.30. That would mean
regime B was substantially a COPY-CHANNEL artifact and the 'confident-wrong' claim must be narrowed
to 'when noise hammers the signal-bearing channel specifically'. FALSIFIER: generic ALSO inverts
(p_true < 0.4 at deep settings) -> inversion is a generic deep-noise property, and the
confident-wrong failure mode stands as a general caveat.

  python3 exp148b_control_ember.py --gates
  python3 exp148b_control_ember.py --prereg
  python3 exp148b_control_ember.py --submit
  python3 exp148b_control_ember.py --analyze
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
DEPTHS = [0, 8, 14, 20, 28]           # extra_PAIRS -> 2q [4,20,32,44,60], reproducing Exp148's
                                      # exact ladder incl. the inversion regime (ep 14/20/28 = 2q 32/44/60)
SHOTS = 2000
MODES = ["copy", "generic"]


def depth_circuit_mode(n, s, extra_pairs, mode):
    """Simon + `extra_pairs` identity CX, barrier-fenced. mode='copy' -> (a,n+a) oracle pairs;
    mode='generic' -> non-copy data pairs (input-input + output-output), matched count."""
    from qiskit import QuantumCircuit
    qc = QuantumCircuit(2 * n, n)
    qc.h(range(n)); qc.barrier()
    qc.compose(SIMON.simon_oracle(n, s), inplace=True); qc.barrier()
    for p in range(extra_pairs):
        if mode == "copy":
            a, b = p % n, n + (p % n)                       # oracle copy channel
        else:
            # generic non-copy data pairs: alternate input-input and output-output,
            # never an (i, n+i) copy pair.
            if p % 2 == 0:
                a, b = p % n, (p + 1) % n                   # input-input
            else:
                a, b = n + (p % n), n + ((p + 1) % n)       # output-output
        qc.cx(a, b); qc.barrier(); qc.cx(a, b); qc.barrier()
    qc.h(range(n)); qc.measure(range(n), range(n))
    return qc


def _pubs_index():
    return [(m, ep) for m in MODES for ep in DEPTHS]


# ---------------- gates
def gate_noiseless():
    from qiskit.primitives import StatevectorSampler
    smp = StatevectorSampler(); rng = np.random.default_rng(1481); checked = 0
    for m, ep in _pubs_index():
        qc = depth_circuit_mode(N, PLANTED_S, ep, m)
        d = smp.run([(qc, None, 4000)]).result()[0].data
        reg = list(d.keys())[0]
        ys = SIMON._sample_ys(getattr(d, reg).get_counts(), N)
        s_con, _ = E148.consensus_decode(ys, N)
        if s_con != PLANTED_S:
            print(f"  FAIL {m} ep={ep}: consensus={s_con}"); return False
        checked += 1
    print(f"  compared: {checked} (mode,depth) cells, consensus recovers planted s at zero noise")
    return checked > 0


def gate_matched(backend_name):
    """CRITICAL: at each depth the two modes must have the SAME transpiled 2q count (matched
    noise), and 2q must grow with depth (knob real). Otherwise copy-vs-generic isn't a fair test."""
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit import transpile
    be = _get_ibm_service().backend(backend_name)
    ok = True
    counts = {}
    for m in MODES:
        prev = -1
        for ep in DEPTHS:
            t = transpile(depth_circuit_mode(N, PLANTED_S, ep, m), be,
                          optimization_level=1, seed_transpiler=148)
            n2q = sum(t.count_ops().get(g, 0) for g in ("cz", "ecr", "cx"))
            counts[(m, ep)] = (n2q, t.depth())
            if n2q <= prev:
                ok = False
            prev = n2q
    for ep in DEPTHS:
        c, g = counts[("copy", ep)][0], counts[("generic", ep)][0]
        match = abs(c - g) <= max(4, int(0.15 * c))     # within 15% or 4 gates (routing overhead;
                                                         # a few gates is negligible noise, esp. shallow)
        ok &= match
        print(f"  ep={ep:>2}: copy 2q={c} depth={counts[('copy',ep)][1]} | "
              f"generic 2q={g} depth={counts[('generic',ep)][1]} | matched={'OK' if match else 'FAIL'}")
    print(f"  monotone + matched: {'OK' if ok else 'FAIL'}")
    return ok, counts


def prereg():
    doc = {"exp": "148b", "author": "Ember", "written": "pre-decode",
           "question": "Does Exp148's confident-wrong inversion (p_true<0.5 at depth) reproduce "
                       "under GENERIC data-qubit noise, or was it specific to injecting on the "
                       "oracle's copy channel?",
           "control": "copy vs generic injection, matched 2q count, same 8 qubits, co-batched "
                      "(same calibration window). Both self-verifying (planted s).",
           "prediction": "GENERIC does NOT fully reproduce the inversion (p_true stays >=~0.45 at "
                         "deep settings, graceful decay) -> regime B was substantially a copy-channel "
                         "artifact; narrow the confident-wrong claim.",
           "prediction_confidence": 0.60,
           "falsifier": "generic ALSO inverts (p_true<0.4 deep) -> inversion is generic deep-noise; "
                        "confident-wrong stands as a general caveat.",
           "n": N, "planted_s": PLANTED_S, "depths": DEPTHS, "shots": SHOTS, "modes": MODES}
    json.dump(doc, open(os.path.join(RESULTS, "exp148b_prereg.json"), "w"), indent=1)
    print("pre-registered -> results/exp148b_prereg.json\n  prediction (0.60): generic does NOT "
          "fully reproduce the inversion (regime B partly copy-artifact); falsifier = generic also inverts.")


def submit(backend_name):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit import transpile
    from qiskit_ibm_runtime import SamplerV2
    ok, _ = gate_matched(backend_name)
    if not ok:
        print("REFUSING: modes not matched / knob cancelled — copy-vs-generic would be unfair."); return 1
    be = _get_ibm_service().backend(backend_name)
    idx = _pubs_index()
    tqcs = [transpile(depth_circuit_mode(N, PLANTED_S, ep, m), be, optimization_level=1,
                      seed_transpiler=148) for m, ep in idx]
    outp = os.path.join(RESULTS, "exp148b_manifest.json")
    if os.path.exists(outp):
        print(f"REFUSING: {os.path.basename(outp)} exists."); return 3
    job = SamplerV2(mode=be).run([(t, None, SHOTS) for t in tqcs])
    man = {"exp": "148b", "n": N, "planted_s": PLANTED_S, "index": idx,
           "shots": SHOTS, "backend": backend_name, "job_id": job.job_id(),
           "note": "copy-vs-generic control, co-batched same calibration. Self-verifying."}
    json.dump(man, open(outp, "w"), indent=1)
    print(f"SUBMITTED Exp148b: job {job.job_id()} ({len(tqcs)} pubs = {len(MODES)} modes x "
          f"{len(DEPTHS)} depths x {SHOTS}) -> {os.path.basename(outp)}")
    print("  (no QPU figure until measured, C4796)")
    return 0


def analyze(mp):
    from run_exp66_qpu_partb import _get_ibm_service
    svc = _get_ibm_service()
    man = json.load(open(mp)); n, s = man["n"], man["planted_s"]
    res = svc.job(man["job_id"]).result()
    idx = [tuple(x) for x in man["index"]]
    pre = json.load(open(os.path.join(RESULTS, "exp148b_prereg.json")))
    print(f"Exp148b | planted s={s} | pre-reg (0.60): generic does NOT fully reproduce the inversion")
    table = {}
    for i, (m, ep) in enumerate(idx):
        d = res[i].data; reg = list(d.keys())[0]
        ys = [tuple(y) for y in SIMON._sample_ys(getattr(d, reg).get_counts(), n)]
        p_true, p_comp, delta = E148.bias(ys, n, s)
        s_hat, _ = E148.consensus_decode(ys, n)
        table[(m, ep)] = {"p_true": round(p_true, 3), "delta": round(delta, 3),
                          "recovered": s_hat == s}
    print(f"  {'depth(ep)':>9} | {'COPY p_true':>11} {'rec':>4} | {'GENERIC p_true':>14} {'rec':>4}")
    rows = []
    for ep in DEPTHS:
        c, g = table[("copy", ep)], table[("generic", ep)]
        rows.append({"ep": ep, "copy_p_true": c["p_true"], "copy_rec": c["recovered"],
                     "generic_p_true": g["p_true"], "generic_rec": g["recovered"]})
        print(f"  {ep:>9} | {c['p_true']:>11} {str(c['recovered']):>4} | "
              f"{g['p_true']:>14} {str(g['recovered']):>4}")
    # verdict: DATA-DRIVEN — compare the arms at the settings where COPY actually inverts
    # (copy_p_true < 0.4), not a hardcoded ep threshold (ep != 2q — the units bug I keep hitting).
    inv = [r for r in rows if r["copy_p_true"] < 0.4]
    copy_inverts = len(inv) > 0
    gen_inverts = copy_inverts and all(r["generic_p_true"] < 0.4 for r in inv)
    if copy_inverts and gen_inverts:
        verdict = "GENERIC ALSO INVERTS -> inversion is a GENERIC deep-noise property; confident-wrong stands (prediction FALSIFIED)"
    elif copy_inverts and not gen_inverts:
        verdict = "GENERIC does NOT invert while COPY does -> regime B was largely a COPY-CHANNEL artifact; narrow the claim (prediction HELD)"
    else:
        verdict = "copy did not reproduce its own inversion this calibration -> inconclusive (drift?), re-examine"
    out = {"exp": "148b", "rows": rows, "verdict": verdict, "prereg": pre}
    json.dump(out, open(os.path.join(RESULTS, "exp148b_analysis.json"), "w"), indent=1)
    print(f"\n  VERDICT: {verdict}\n  -> results/exp148b_analysis.json")


def main():
    ap = argparse.ArgumentParser()
    for fl in ("gates", "prereg", "submit", "analyze"):
        ap.add_argument(f"--{fl}", action="store_true")
    ap.add_argument("--manifest"); ap.add_argument("--backend", default="ibm_kingston")
    a = ap.parse_args()
    if a.gates:
        print("=== noiseless truth-gate (both modes recover s) ===")
        g1 = gate_noiseless()
        print("=== matched-noise gate (copy vs generic same 2q count) ===")
        g2, _ = gate_matched(a.backend)
        print(f"\nGATES: {'ALL PASS' if (g1 and g2) else 'FAIL'}")
        return 0 if (g1 and g2) else 1
    if a.prereg:
        prereg(); return 0
    if a.submit:
        return submit(a.backend)
    if a.analyze:
        analyze(a.manifest or os.path.join(RESULTS, "exp148b_manifest.json")); return 0
    ap.print_help(); return 0


if __name__ == "__main__":
    sys.exit(main())
