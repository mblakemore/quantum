# Exp130 Pre-Registration — THE HEISENBERG LADDER: GHZ Fisher Advantage Up the N-Rungs

**Author**: Whisper (DC15W), C4669 (2026-07-13) · **Substrate**: claude-opus-4-8
**Status**: FROZEN before hardware submission (advisor-audited pre-freeze)
**Directive**: Creator ("F108 numbered, next one of course!") — the registered Exp129 follow-up:
turn the single-point N=3 Fisher advantage into a **ladder** and locate where it stops paying.

## Scope, stated first (advisor-frozen)

- **Claim shape — turnover location, NOT a scaling exponent.** F_GHZ(N) = N²·V_N² is N²
  multiplying an *exponential* visibility decay in N, not a power law; a log-log "exponent"
  over four points would imply a cleanliness the data does not have. The honest, still-strong
  objects: (a) **per-rung**, does GHZ Fisher info beat the *executed* separable reference
  F_sep(N) = Σᵢ V₁,ᵢ² over the N physical qubits; (b) plot **R(N) against the ideal Heisenberg
  line R = N** and locate the turnover N* where visibility decay pulls R below N; (c) the
  **F85 contrast** — cheap-prep metrology (2(N−1) CX) vs deep capacity activation (110 CX,
  which *inverted* at N=3). **Both outcomes pre-registered**: PERSISTS (F_GHZ(5) > F_GHZ(2) at
  5σ) or TURNOVER (some N* < 5 maximizes) — either is the finding, same discipline as the
  campaign's informative nulls.
- **Dynamic-range caveat (the honesty line).** GHZ super-resolution buys per-shot Fisher info
  ∝ N² by **spending unambiguous range**: cos(Nφ) fixes φ only within 2π/N. The certified
  object is **local per-shot sensitivity at fixed bias, given prior confinement to one fringe**
  — NOT unconditional phase-estimation superiority (restoring range needs adaptive/multi-N
  protocols). This is the exact analog of the campaign's "not a Holevo violation" (F107) and
  "not literal time travel" (F101) scope lines. Prep CX are not charged against the probe
  budget (standard metrological accounting).
- Prior art plain: GHZ/N00N phase super-resolution is textbook (Bollinger et al. 1996). The
  contribution is the frozen-court, executed-reference, both-outcomes ladder on 2026 silicon.

## Apparatus

Linear chain q0..q₄ on a calibration-gated heavy-hex path (min Σ 2q errors + readouts).
- **GHZ arm** per N ∈ {2,3,4,5}: H(0), CX ladder forward, Rz(φ)⊗N, CX ladder reverse, H(0),
  measure q0 → P₀ = (1 + V_N cos Nφ)/2. **2(N−1) CX** (2/4/6/8). 16 φ points/rung.
- **SEP arm**: all 5 qubits (H | Rz(φ) | H) independently, measure all — **zero 2q gates**,
  one 16-point sweep gives V₁,ᵢ per qubit; F_sep(N) = Σᵢ₌₀^{N−1} V₁,ᵢ² (the same N physical
  qubits the GHZ chain uses).
- **NPTS = 16** (Nyquist harmonic 8, headroom over the top rung N=5 — advisor: N=5 must not
  sit one bin under Nyquist where G_FREQ can't scan for an aliased neighbor). Free-frequency
  scan over k = 1..7. Estimator: V = 4|Σ(p_j−p̄)e^{−ikφ_j}|/16, exact binomial SE propagation.
- 64 GHZ + 16 SEP + 2 sentinels (|00000⟩, |11111⟩) = 82 pubs, 4000 shots each (~328k),
  shuffled (seed 4669), co-batched in one window.

## Frozen gates

| Gate | Statement | PASS condition |
|---|---|---|
| **W1_ADVANTAGE** (primary) | GHZ beats executed separable ref at EVERY rung | R(N) > 1 + 5·SE_R for all N ∈ {2,3,4,5} |
| **W2_SCALING** (the finding, both outcomes) | Heisenberg-like growth vs turnover | **PERSISTS** if R(5) > R(2) at 5σ AND F_GHZ(5) > F_GHZ(2) at 5σ; else **TURNOVER** at N* = argmax_N F_GHZ(N) — report N* and the R(N)-vs-N bend either way |
| **G_FREQ** | super-resolution law at every rung | each GHZ_N peaks at harmonic k=N, amp(N) > 2× max amp(k≠N) |
| **G_SENT** | prep/readout integrity | both sentinels ≥ 0.95 |

**Figures of merit**: the R(N) ladder against R=N; N* = argmax F_GHZ(N); F_GHZ(5)/F_GHZ(2) net
gain; per-rung V_N decay curve. **Fake preview**: R = [2.00, 2.81, 3.72, 4.58], F_GHZ = [3.88,
8.25, 14.47, 22.06], **N* = 5, PERSISTS** — and the N=3 fake (R=2.81, F_GHZ=8.25) reproduces
Exp129 hardware (2.85, 8.29), cross-validating the apparatus. Noiseless: R tracks N exactly,
peaks at k=N, all rungs.

**Pre-filed predictions**: W1 HIT all four rungs conf 0.93; W2 = **PERSISTS** conf 0.80 (rests
entirely on V₅ at 8 CX — need V₅ > ~0.4 for F_GHZ(5) > F_GHZ(2); expect V₅ ≈ 0.85–0.92, robust,
but a cratered window turns it into a genuine TURNOVER finding); the R(N)-vs-N bend widening
with N conf 0.85; G_FREQ conf 0.92; G_SENT conf 0.92. Fake likely optimistic ~1–2pp on V_N per
the C4666/C4668 crossover curve.

**NO-TEST conditions**: sentinel failure → window NO-TEST; SEP pub with 2q gates or GHZ_N pub
≠ 2(N−1) CX (audited pre-submit) → abort; G_FREQ failure at a rung with W1 passing there →
apparatus audit before claiming that rung.

## Relation to the campaign

F108 (Exp129) certified the advantage at N=3; this maps the whole ladder and answers the F85
question in a new task: **does the NISQ scaling inversion (theory scales, practice inverts at
N=3 for 110-CX capacity activation) also bite cheap-prep metrology?** Pre-filed answer: no —
2(N−1)-CX GHZ keeps the metrological advantage climbing through N=5, making the inversion
**task-dependent, not a hardware verdict**. That contrast is the finding's spine.
