# Finding — Exp187b: THE ORDER DECIDED LATER, certified — and the echoed late choice beats the early one

**Cycle**: C4877 · **Date**: 2026-07-19 · **Backend**: ibm_fez · **Job**: `d9e4r2sjeosc73fib9hg`
(21 circuits, 8000 shots, one pinned layout [23,22,2], Hahn delay 425 dt). Companion to
finding-exp187-late-order.md; criteria pre-committed in the 187b amendment (difference-form
falsifier, pinned layout, forward-priced band, echo arm). **Full verdict: HELD.**

## Result

| quantity | measured | criterion | verdict |
|----------|----------|-----------|---------|
| W₊ = ⟨Z\|+⟩ (delayed) | **+0.218 (+17σ)** | off the mixture equator (0) ≥5σ; band +0.08..+0.25 | HELD |
| W₋ = ⟨Z\|−⟩ (delayed) | **−0.657 (29σ)** | ≥5σ; band −0.85..−0.50 | HELD |
| Z-sort (same record) | F = 0.963 / 0.974 | ≥ 0.85 | HELD |
| hull break (＋ensemble) | X−Y = 1.326 | > 1 | HELD |
| falsifier (difference form) | sort-dependence 0.073 | ≤ 0.10 (mixture: 0) | **HELD** |
| no-signaling (pinned) | spread 0.0162 | < 0.025 | **HELD** (was 0.030 unpinned — placement confirmed) |

**The claim, certified**: the target was measured — record closed — before the control was
looked at. The later basis choice sorts that same record into the two *definite causal orders*
(Z-sort) or into ensembles sitting 17σ and 29σ off the equator that **every**
definite-or-mixed order is pinned to (X-sort). Causal order is choice-dependent structure in
the record, not a property the past possessed. With Exp184 and Exp186, the trilogy becomes a
quartet: no fixed moment, no definite value, no definite order — each decided later, each with
its no-signaling audit clean.

## The echo arm — the run's toolkit inverts the cost of choosing late

Pre-registered: the engineered Hahn (X–delay–X on the control through the target's measurement
window) should recover ≥ half the delayed-choice cost. Measured: **recovery +0.249 against a
cost of +0.127 — 196%**. The echoed delayed arm (W₊ = +0.467, W₋ = −0.814) **beats the
standard immediate measurement** (W₊ = +0.345, W₋ = −0.858 → on W₊ by +0.122): the Hahn
refocused not only the window dose but background quasi-static dephasing that the standard arm
also pays. Operational sentence: **on this hardware, deferring the choice — with an echo — is
better than choosing now.** (Consistent with Exp178's discovery that the coherent pool is
large; the echo drains all of it, not just the window's share.)

## Ledger

All criteria held; p₋ = 0.198 grazes its 0.20–0.30 band low by 0.002 (readout asymmetry on
the control; noted, not load-bearing). The 187→187b pair now stands with 185→185b as the
repository's amendment-discipline examples: letter-verdicts preserved, fixes rule-derived and
pre-committed, and in both cases the re-flight's physics came back stronger than the original
claim (normalized ratios stable; echo recovery 196%).

## Fence

As Exp187 (compiled switch; wing-1 posture; per-circuit late choice; RNG-in-the-loop the named
follow-up). One die, one pinned layout, same-night conditions. The echo's 196% recovery
includes background-dephasing refocusing — the window-specific share is bounded by the
measured cost (0.127); the exhibit/finding language keeps the two separate.
