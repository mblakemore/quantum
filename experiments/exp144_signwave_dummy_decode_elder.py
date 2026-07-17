#!/usr/bin/env python3
"""Exp144 SIGN-WAVE DUMMY CALIBRATION decode (Elder) — FROZEN before landing.

Decodes Ember's dummy sign-calibration (job d9d82qkinv1c73aomk30, ibm_kingston)
into per-term measured attenuation att_j, checks the att-only model (the 3 att_j
must agree), and feeds the representative att into the FROZEN truth-gate sim
(exp144_signwave_truthgate_elder.gate) → worst-coeff sign-recovery @ N=100 vs the
0.90 capability bar. Standalone HARDWARE-CAPABILITY measurement (stage-1 support
VOID → gates nothing downstream), reported as capability.

This is the 2nd independent seat. Both decoders are pre-committed BEFORE landing;
the 2-of-2 is the NUMBERS agreeing (att_j to ~2 sig figs), not just verdicts —
the reproducibility-vs-corroboration lesson (C4195/C4810).

REGISTER CONVENTION — locked with Ember, verbatim (Discord C-thread 2026-07-17):
  • classical register 'c', size 4 → res[j].data.c.get_bitstrings()
  • measure map IDENTITY q_i → c_i (measure(range(4),range(4)))
  • get_bitstrings() is Qiskit little-endian: leftmost char = c[3].
    REVERSE it: b = s[::-1] → b[i] = LOGICAL qubit i outcome ∈ {0,1}
  • probes are LOGICAL-indexed, all non-I at sites q1,q3:
       XXXX→IYIX, XXYY→IYIY, XXZZ→IYIZ
  • parity_j = Π over non-I sites (1 − 2·b[i]);  ⟨Q⟩_meas_j = mean over 2000 shots
  • pub order = [XXXX c=0.25, XXYY c=0.20, XXZZ c=0.15]  (Ember's flight frame)
  • att_j = ⟨Q⟩_meas_j / ideal_j ;  att_j < 0 ⇒ that term's sign MISRECOVERED
    (noise pushed ⟨Q⟩ past 0) → recovery for that coeff < 0.5 (gate maps it).
"""
import os
import sys
import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from exp144_signwave_truthgate_elder import gate, GRID, T  # FROZEN sim gate

JOB_ID = "d9d82qkinv1c73aomk30"
# Ember's flight frame — pub order and per-pub (term, coeff).
PUBS = [("XXXX", 0.25), ("XXYY", 0.20), ("XXZZ", 0.15)]
NON_I_SITES = (1, 3)                        # q1,q3 for all three probes (IYIX/IYIY/IYIZ)
IDEAL = {c: -np.sin(2 * c * T) for _, c in PUBS}   # −0.8415/−0.7174/−0.5646
BAR = 0.90                                  # P3 capability bar (worst-coeff recovery)


def q_mean(bitstrings):
    """⟨Q⟩ = mean parity(±1) over q1,q3 with Ember's locked convention."""
    acc = 0.0
    for s in bitstrings:
        b = s[::-1]                         # little-endian → logical index
        p = 1
        for i in NON_I_SITES:
            p *= (1 - 2 * int(b[i]))
        acc += p
    return acc / len(bitstrings)


def main():
    from qiskit_ibm_runtime import QiskitRuntimeService
    svc = QiskitRuntimeService()
    job = svc.job(JOB_ID)
    st = str(job.status())
    if "DONE" not in st.upper() and "COMPLET" not in st.upper():
        sys.exit(f"job {JOB_ID} not DONE (status={st}) — re-run on landing")
    res = job.result()
    if len(res) < len(PUBS):
        sys.exit(f"expected {len(PUBS)} pubs, got {len(res)} — abort (no vacuous read)")

    print(f"SIGN-WAVE DUMMY DECODE (Elder, frozen) — job {JOB_ID}")
    print(f"{'term':>5} {'coeff':>6} {'ideal<Q>':>9} {'meas<Q>':>9} {'att_j':>7} {'shots':>6}  note")
    att = {}
    for j, (term, c) in enumerate(PUBS):
        bits = res[j].data.c.get_bitstrings()
        qm = q_mean(bits)
        ideal = IDEAL[c]
        a = qm / ideal
        att[c] = a
        note = "sign LOST" if a < 0 else ("weak" if a < 0.3 else "")
        print(f"{term:>5} {c:>6.2f} {ideal:>9.4f} {qm:>9.4f} {a:>7.3f} {len(bits):>6}  {note}")

    vals = np.array([att[c] for _, c in PUBS])
    spread = float(vals.max() - vals.min())
    print(f"\natt_j = {[round(att[c],3) for _,c in PUBS]}  (coeffs {[c for _,c in PUBS]})")
    print(f"AGREEMENT (att-only model): spread max−min = {spread:.3f}")
    if spread <= 0.05:
        print("  → att_j AGREE to ~2 sig figs — att-only model holds; representative att = mean.")
    else:
        # coeff-dependence = a MODEL finding, reported not averaged away.
        trend = "decreasing with coeff" if vals[0] < vals[-1] else "increasing with coeff"
        print(f"  → att_j DIVERGE (spread {spread:.3f} > 0.05) — MODEL FINDING, not averaged: {trend}.")
        print("    (readout-asymmetry or coeff-scaling leaking past the att-only frame;"
              " if [2,3]-touching terms worst, idle is the suspect — connected retry.)")

    rep = float(np.clip(vals.mean(), 0.0, 1.0))
    print(f"\nrepresentative att = {rep:.3f} → frozen gate() worst-coeff recovery @N=100:")
    r = gate(rep)
    worst = min(r.values())
    print(f"  per-coeff recovery {{{', '.join(f'{c}:{r[c]:.2f}' for c in GRID)}}}  worst = {worst:.2f}")
    # also the per-att_j band, so a divergent model is not hidden by the mean
    band = {round(a, 2): min(gate(float(np.clip(a, 0, 1))).values()) for a in vals}
    print(f"  per-att_j worst-recovery band: {band}")
    verdict = "MEETS 0.90 (capability: signs recoverable)" if worst >= BAR \
        else "BELOW 0.90 (capability: signs NOT reliably recoverable at this att)"
    print(f"\nCAPABILITY VERDICT (gates nothing): worst-coeff {worst:.2f} vs {BAR} → {verdict}")


if __name__ == "__main__":
    main()
