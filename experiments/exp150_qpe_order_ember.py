#!/usr/bin/env python3
"""Exp150 — QFT order-recovery (the Shor kernel, toy) (Ember, Move 2). Creator 'fly them'.

ADDS THE QFT — the ingredient Simon (Hadamard-only) doesn't have. Quantum phase estimation of a
planted phase phi = s/r: controlled-P(2^j * 2pi phi) + INVERSE QFT on t counting qubits, measure,
recover r by continued fractions. This IS the Shor back-end (QPE + iQFT + continued fractions).

FENCE (state with any headline, G-plan): this is the QFT/QPE ORDER-RECOVERY back-end — it recovers
the denominator r of a hidden phase. It is NOT factoring RSA: that needs the modular-exponentiation
FRONT-END, fault tolerance, and t of hundreds. This is the kernel at toy size, on real hardware.

REGIMES (gap G2, both flown + LABELED):
  DIVISOR  r | 2^t  : exact peak, clean but a WEAK QFT test (period fits the register).
  NON-DIV  r not| 2^t: approximate peak, continued-fractions recovery — the REAL Shor regime.

SELF-VERIFICATION (gap G3, QPE form): planted phi=s/r; recovered r (CF-majority over shots) ==
planted r; AND the phase estimate m/2^t is near s/r. Submitter holds s/r (ground truth).

QFT-CORRECTNESS GATE (gap G6, the KILL criterion): noiseless recovery must return planted r for
EVERY (t,r) flown — this catches qubit-order / controlled-phase / bit-reversal bugs. One WAS caught
pre-flight: recovery read int(bit[::-1]) (double bit-reversal vs QFT do_swaps) -> fixed to int(bit,2).
If this gate fails for a setting, that setting is NOT flown.

SURVIVAL GATE (Move 3 predictor, applicable here): QPE is controlled-phase-only (shallow); predict
which t survives before flying.

  python3 exp150_qpe_order_ember.py --gates
  python3 exp150_qpe_order_ember.py --prereg
  python3 exp150_qpe_order_ember.py --submit
  python3 exp150_qpe_order_ember.py --analyze
"""
import argparse
import importlib.util
import json
import math
import os
import sys
from collections import Counter
from fractions import Fraction

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
RESULTS = os.path.join(HERE, "..", "results")
_p = importlib.util.spec_from_file_location("pred", os.path.join(HERE, "exp_survival_predictor_ember.py"))
PRED = importlib.util.module_from_spec(_p); _p.loader.exec_module(PRED)

# (t, s, r, Nmax, regime). Divisor = exact; non-divisor = real Shor regime.
SETTINGS = [
    (4, 1, 4, 6, "divisor"),      # exact
    (5, 1, 3, 6, "non-divisor"),  # real Shor regime (headline)
    (5, 1, 5, 7, "non-divisor"),
    (5, 2, 5, 7, "non-divisor"),
]
SHOTS = 4000


def qpe_circuit(t, s, r):
    from qiskit import QuantumCircuit
    from qiskit.circuit.library import QFT
    phi = s / r
    qc = QuantumCircuit(t + 1, t)
    qc.x(t)                                    # |1>: eigenstate of P(theta)
    for q in range(t):
        qc.h(q)
    for j in range(t):
        qc.cp(2 * math.pi * phi * (2 ** j), j, t)     # controlled-U^{2^j}, U=P(2pi phi)
    qc.append(QFT(t, inverse=True, do_swaps=True).to_gate(), range(t))
    qc.measure(range(t), range(t))
    return qc


def recover_votes(counts, t, Nmax):
    """Continued-fractions recovery, vote weighted by counts. m read straight (QFT do_swaps
    already reverses; int(bit[::-1]) would double-flip — the G6 bug caught pre-flight)."""
    v = Counter()
    for bit, c in counts.items():
        m = int(bit, 2)
        q = Fraction(m, 2 ** t).limit_denominator(Nmax).denominator
        if q > 1:
            v[q] += c
    return v


# ---------------- gates
def gate_qft_correct():
    """G6/KILL: noiseless recovery must return planted r for EVERY setting."""
    from qiskit.primitives import StatevectorSampler
    smp = StatevectorSampler(); ok = True
    for t, s, r, Nmax, reg in SETTINGS:
        d = smp.run([(qpe_circuit(t, s, r), None, 4000)]).result()[0].data
        rg = list(d.keys())[0]
        v = recover_votes(getattr(d, rg).get_counts(), t, Nmax)
        rmaj = v.most_common(1)[0][0] if v else None
        good = rmaj == r
        ok &= good
        print(f"  t={t} phi={s}/{r} ({reg}): noiseless CF-recovers r={rmaj} vs planted {r} "
              f"-> {'OK' if good else 'FAIL — DO NOT FLY this setting'}")
    return ok


def gate_survival(backend_name):
    """Move-3 predictor on each setting's transpiled 2q count."""
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit import transpile
    be = _get_ibm_service().backend(backend_name); allok = True
    for t, s, r, Nmax, reg in SETTINGS:
        tq = transpile(qpe_circuit(t, s, r), be, optimization_level=1, seed_transpiler=150)
        n2q = sum(tq.count_ops().get(g, 0) for g in ("cz", "ecr", "cx"))
        pred = PRED.survives(n2q, t, t, SHOTS)
        allok &= pred["survives"]
        print(f"  t={t} r={r}: transpiled 2q={n2q} depth={tq.depth()} | pred p_true={pred['p_true_pred']} "
              f"survives={pred['survives']}")
    return allok


def prereg():
    doc = {"exp": 150, "author": "Ember", "written": "pre-decode",
           "question": "Does QFT-based QPE order-recovery run on kingston, recovering hidden r?",
           "regimes": "divisor (exact, weak test) + non-divisor (approximate, real Shor regime)",
           "prediction": "recover r for the divisor setting and the non-divisor settings the "
                         "survival predictor passes; the QPE circuit is shallow so all should survive.",
           "prediction_confidence": 0.6,
           "falsifier": "fails to recover r at a setting the predictor passed -> QPE too noisy on "
                        "kingston (or predictor over-optimistic; log which).",
           "fence": "QFT/QPE ORDER-RECOVERY back-end, NOT factoring RSA (no modular-exp front-end).",
           "settings": [{"t": t, "s": s, "r": r, "Nmax": N, "regime": g} for t, s, r, N, g in SETTINGS],
           "shots": SHOTS}
    json.dump(doc, open(os.path.join(RESULTS, "exp150_prereg.json"), "w"), indent=1)
    print("pre-registered -> results/exp150_prereg.json")


def submit(backend_name):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit import transpile
    from qiskit_ibm_runtime import SamplerV2
    if not gate_qft_correct():
        print("REFUSING: QFT-correctness gate failed for a setting — DO NOT FLY it (G6/KILL)."); return 1
    be = _get_ibm_service().backend(backend_name)
    tqcs = [transpile(qpe_circuit(t, s, r), be, optimization_level=1, seed_transpiler=150)
            for t, s, r, N, g in SETTINGS]
    outp = os.path.join(RESULTS, "exp150_manifest.json")
    if os.path.exists(outp):
        print(f"REFUSING: {os.path.basename(outp)} exists."); return 3
    job = SamplerV2(mode=be).run([(t, None, SHOTS) for t in tqcs])
    json.dump({"exp": 150, "settings": SETTINGS, "shots": SHOTS, "backend": backend_name,
               "job_id": job.job_id(), "note": "QPE order-recovery, self-verifying (planted s/r)."},
              open(outp, "w"), indent=1)
    print(f"SUBMITTED Exp150: job {job.job_id()} ({len(tqcs)} settings) -> {os.path.basename(outp)}")
    print("  (no QPU figure until measured, C4796)")
    return 0


def analyze(mp):
    from run_exp66_qpu_partb import _get_ibm_service
    svc = _get_ibm_service()
    man = json.load(open(mp)); res = svc.job(man["job_id"]).result()
    pre = json.load(open(os.path.join(RESULTS, "exp150_prereg.json")))
    print("Exp150 QPE order-recovery on hardware | fence: QFT back-end, NOT factoring")
    rows = []
    for i, (t, s, r, Nmax, reg) in enumerate([tuple(x) for x in man["settings"]]):
        d = res[i].data; rg = list(d.keys())[0]
        v = recover_votes(getattr(d, rg).get_counts(), t, Nmax)
        top = v.most_common(3)
        rmaj = top[0][0] if top else None
        conf = (top[0][1] / sum(v.values())) if v else 0.0
        good = rmaj == r
        rows.append({"t": t, "phi": f"{s}/{r}", "regime": reg, "planted_r": r,
                     "recovered_r": rmaj, "confidence": round(conf, 3), "top": top, "correct": good})
        print(f"  t={t} phi={s}/{r} ({reg}): recovered r={rmaj} (conf {conf:.2f}) vs planted {r} "
              f"-> {'RECOVERED' if good else 'MISS'}  top={top}")
    n_ok = sum(r["correct"] for r in rows)
    verdict = f"{n_ok}/{len(rows)} settings recovered r on hardware (QFT/QPE back-end runs on kingston)"
    json.dump({"exp": 150, "rows": rows, "verdict": verdict, "prereg": pre,
               "fence": "QFT order-recovery back-end, NOT factoring RSA"},
              open(os.path.join(RESULTS, "exp150_analysis.json"), "w"), indent=1)
    print(f"\n  VERDICT: {verdict}\n  -> results/exp150_analysis.json")


def main():
    ap = argparse.ArgumentParser()
    for fl in ("gates", "prereg", "submit", "analyze"):
        ap.add_argument(f"--{fl}", action="store_true")
    ap.add_argument("--manifest"); ap.add_argument("--backend", default="ibm_kingston")
    a = ap.parse_args()
    if a.gates:
        print("=== QFT-correctness gate (G6, KILL) ==="); g1 = gate_qft_correct()
        print("=== survival gate (Move-3 predictor) ==="); g2 = gate_survival(a.backend)
        print(f"\nGATES: {'ALL PASS' if (g1 and g2) else ('QFT-correct FAIL' if not g1 else 'survival warn')}")
        return 0 if g1 else 1        # QFT-correctness is the hard KILL; survival is advisory
    if a.prereg: prereg(); return 0
    if a.submit: return submit(a.backend)
    if a.analyze: analyze(a.manifest or os.path.join(RESULTS, "exp150_manifest.json")); return 0
    ap.print_help(); return 0


if __name__ == "__main__":
    sys.exit(main())
