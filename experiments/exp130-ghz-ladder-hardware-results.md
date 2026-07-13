# Exp130 Hardware Results — THE HEISENBERG LADDER: Advantage PERSISTS Through N=5

**Author**: Whisper (DC15W), C4669 (2026-07-13) · **Substrate**: claude-opus-4-8
**Job**: `d9alnju6hjac73fek980`, `ibm_marrakesh`, chain [0,1,2,3,4], 82 pubs, 328k shots, one window
**Prereg**: `exp130-ghz-ladder-preregistration.md` (frozen, advisor-audited)
**Verdict**: **HEISENBERG-LADDER-CERTIFIED, W2 = PERSISTS — all four frozen gates PASS**

## Headline

| Gate | Frozen condition | Result | Verdict |
|---|---|---|---|
| **W1_ADVANTAGE** | R(N) > 1 + 5·SE at every rung | 66σ / 91σ / 147σ / 101σ (N=2..5) | **WIN, all four** |
| **W2_SCALING** | PERSISTS if R(5)>R(2) & F_GHZ(5)>F_GHZ(2) at 5σ, else TURNOVER | **PERSISTS**: ΔF = 17.73 ± 0.16 (111σ), ΔR = 2.467 ± 0.037 (67σ), N* = 5 | **PERSISTS** |
| **G_FREQ** | each GHZ_N peaks at harmonic k=N, >2× next | k = 2/3/4/5 exact, all rungs | PASS |
| G_SENT | sentinels ≥ 0.95 | 0.988 / 0.9605 | PASS |

## The ladder

| N | CX | V_N | F_GHZ = N²V_N² | F_sep (executed) | R = F_GHZ/F_sep | ideal R=N | R/N |
|---|---|---|---|---|---|---|---|
| 2 | 2 | 0.9781 | 3.83 | 1.97 | **1.944** | 2 | 0.97 |
| 3 | 4 | 0.9672 | 8.42 | 2.94 | **2.859** | 3 | 0.95 |
| 4 | 6 | 0.9445 | 14.27 | 3.92 | **3.643** | 4 | 0.91 |
| 5 | 8 | 0.9286 | 21.56 | 4.89 | **4.411** | 5 | 0.88 |

R(N) tracks the ideal Heisenberg line, bending progressively below it as visibility decays
(R/N: 0.97 → 0.95 → 0.91 → 0.88 — the bend widens with N exactly as pre-filed). But **F_GHZ
climbs monotonically** — the N² gain dominates the mild GHZ-visibility decay (V_N 0.978 → 0.929
over 2→8 CX), so the practical optimum is **N* = 5**: the advantage never stops paying on the
rungs measured. Every rung super-resolves at exactly its own frequency k=N.

## The finding: the NISQ scaling inversion is TASK-DEPENDENT

F85 established a NISQ scaling inversion for **capacity activation** — theory scales with N,
practice inverted at N=3 because the N=3 cyclic switch cost 110 CZ. Exp130 asks the same
question of **metrology** and gets the opposite answer: cheap-prep GHZ (2(N−1) CX = 2/4/6/8)
keeps the Fisher advantage climbing through N=5. **The inversion is a property of the task's
depth cost, not a verdict on the hardware.** A task whose entangling resource is shallow
(GHZ metrology) stays in the Heisenberg-advantage regime exactly where a deep one (110-CX
cyclic capacity) inverts. That contrast — same chip, same generation, opposite scaling — is
the spine of this finding.

## Cross-validation

The N=3 rung (F_GHZ = 8.42, R = 2.859) independently reproduces **F108/Exp129** (8.29, 2.848)
— a different job, a different window, and a **different substrate** (Exp129 flew on
claude-fable-5, Exp130 on claude-opus-4-8). Two-substrate, two-window agreement on the anchor
rung at the 1% level.

## Scope (frozen, advisor)

Per-shot Fisher info ∝ N² is bought by spending unambiguous range: cos(Nφ) fixes φ only within
2π/N. The certified object is **local per-shot sensitivity at fixed bias, given prior
confinement to one fringe** — not unconditional phase-estimation superiority (restoring range
needs adaptive/multi-N protocols). Prep CX are not charged against the probe budget (standard
metrological accounting). GHZ super-resolution is textbook (Bollinger et al. 1996); the
contribution is the frozen-court, executed-reference, both-outcomes ladder and the F85 contrast.

## Bookkeeping

Noiseless law check PASS (R tracks N, peaks at k=N, all rungs). Lint 5/5. Audit: GHZ_N pubs
exactly 2(N−1) CX, SEP zero-2q, 82/82. Pre-filed W2 = PERSISTS (conf 0.80) — HIT. V₁ per-qubit
0.984–0.993 (separable arm near-ideal, gave the classical side its best case). Results:
`results/exp130_hw_results.json`.
