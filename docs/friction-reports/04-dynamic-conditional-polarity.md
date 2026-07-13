# Friction Report 04 — Dynamic-Circuit Conditional Executed With Inverted Effective Polarity (one pub class)

**Status: DRAFT, NOT FILED** (Creator approval required). Target: Qiskit Runtime /
dynamic-circuit execution. Forensics: Whisper C4625 on banked Exp112 data
(job `d9a19kcqp3as739un8e0`, ibm_marrakesh, 2026-07-13).

## Summary

In one job, the 1-station entanglement-swapping arm with active `if_test` corrections
produced a **deterministic Ψ+ output where Φ+ was prepared** — the exact fingerprint of the
conditional X firing with inverted polarity (or an equivalent uncorrected deterministic X in
the feedforward path). The 2-station arm **in the same job, same chain, same session**
executed correctly (Φ+ pattern across all 16 branches).

## The exclusion chain (all steps reproducible from repo artifacts)

1. **Logical circuit correct**: noiseless validator passed for this exact builder at k=1
   (per-branch S = 2√2; `exp112_swap_chain_sim.py`).
2. **Transpiled circuit correct**: the exact submitted object (same backend target, layout
   [8,7,6,5], seed 4598, opt 1) re-simulated noiselessly C4625: E(ab) = +0.7015 (Φ+). The
   defect is NOT in transpilation.
3. **Hardware output**: all four k=1 active branches show the (−,−,+,−) setting pattern =
   Ψ+ = net X_B, at feedforward-diluted magnitudes (|E| 0.22–0.71). Sign-flip structure,
   not dilution → wiring-class, not noise-class. Branch-INDEPENDENT → deterministic, not
   the branch-dependent feedforward error of arXiv:2604.28037.

## Honest scope

n = 1 pub-class in 1 job. A within-session runtime transient cannot be excluded. The
discriminating re-fly is queued (Exp112b micro: ONLY the active-k1 cell, 4 settings ×
4000 shots ≈ 16k shots, minutes of QPU) — persistent inversion = reportable bug;
non-reproduction = transient, documented here either way.

## Why it matters

A silently inverted conditional is worst-case for dynamic-circuit users: results look
plausible (a valid Bell state, just the wrong one) and gate-count audits cannot see
classical wiring. Our detection required branch-resolved sign forensics against exact
state fingerprints. Ask: any known issue class for conditional-polarity in runtime
execution of `if_test` on 2-bit registers; and/or expose the compiled classical program
for user audit.
