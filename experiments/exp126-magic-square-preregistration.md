# Exp126 Pre-Registration — THE KOBAYASHI MARU: Peres-Mermin Magic-Square Game (Horizons-3 H5)

**Author**: Whisper (DC15W), C4666 (2026-07-13)
**Status**: FROZEN before hardware submission
**Directive**: Creator (2026-07-13): *"See if you can come up with creative uses for our work to find a measurable quantum advantage."* This experiment IS a measurable quantum advantage in the strict sense: a game with an **exact classical theorem ceiling** that quantum strategies provably exceed — the third great no-go (contextuality) certified in the same court that graded Bell (F73-class) and the causal game (F82).

## Scope, stated first

- **What this is**: a *game-value* quantum advantage — the Mermin (1990) magic square in its pseudo-telepathy form (Brassard–Broadbent–Tapp 2005). Classical ceiling 8/9 over uniformly drawn contexts; quantum value 1 via two shared Bell pairs. Winning above 8/9 at 5σ certifies that **no local-hidden-variable / no-entanglement strategy can reproduce the record** — a provable-bound BEAT, the F82 class.
- **What this is NOT**: a computational-speedup claim. No time-to-solution statement is made. Prior art is credited plainly: the magic square is textbook, and hardware demonstrations exist on other platforms; **our contribution is the pre-registered, exhaustively-verified-bound, adversarially-controlled gate-model certification** with executed no-entanglement null, per the campaign's standing court.
- **Grading is honest about locality**: Alice and Bob are two halves of one chip, not space-like separated. No loophole-free claim. The claim is: the measured statistics exceed what ANY parity-respecting classical strategy pair (equivalently any LHV model, shared randomness included) can produce — certified against an **in-code exhaustively enumerated** bound, not a cited one.

## The square and the theorem checks (all verified in `exp126_magic_square_sim.py`, PASS)

```
        c1   c2   c3
   r1 [ XI   IX   XX ]     rows multiply to +I (all three)
   r2 [ IZ   ZI   ZZ ]     cols multiply to +I, +I, −I
   r3 [ XZ   ZX   YY ]
```

Verified by explicit matrix products: row/col parities as above; each row/column mutually commuting; derived-value identities XZ·ZX = +YY and XX·ZZ = −YY. **Classical bound verified by exhaustive enumeration over all 4096 deterministic parity-respecting strategy pairs: max average win = 8/9 exactly** (deterministic suffices; shared randomness is a convex combination). The bound is not taken from memory or literature — it is recomputed in the artifact (pattern c857: *verify the bound covers your instance class before grading*).

A second classical fact frozen here: for ANY classical strategy (mixtures included), **min-over-contexts win ≤ average ≤ 8/9**. So a min-context value above 8/9 is *also* classically impossible, and is frozen as the secondary gate.

## Apparatus

4 qubits, logical line **B1–A1–A2–B2** (Alice middle: her entangled row-3 context CZ(A1,A2) is connectivity-free; Bob's col-3 Bell measurement pays routing on 3 of 9 contexts — audited at transpile, and the FakeMarrakesh preview already includes it). Prep: Bell(A1,B1) + Bell(A2,B2). Alice measures her row's commuting triple, Bob his column's; each side's third value is the signed product (parity satisfied **by construction**), so grading reduces to intersection agreement.

- **Arms**: `main_rc` (9 contexts, Bell-prepped, 20k shots each = 180k); `null_rc` (9 contexts, |0000⟩ — no entanglement, 4k each = 36k); prep/readout sentinels (2 × 2k).
- **Placement**: calibration-gated 4-qubit line (best sum of 2q errors + readouts over coupled paths, exp91/109 logic), quiet-qubit family.
- **Shuffle**: arm order permuted, seed 4666. Co-batched in ONE job (same-window by construction, F77 primitive).

## Frozen gates

| Gate | Statement | PASS condition |
|---|---|---|
| **W1_GAME** (primary) | pooled win over 9 uniform contexts beats the classical ceiling | p̂_pooled > 8/9 + 5·SE_pooled |
| **W2_MIN** (secondary) | even the WORST context beats the ceiling (classically impossible for the min) | min_c p̂_c > 8/9 + 5·SE_context |
| **G_NULL** | executed no-entanglement arm stays at/below the ceiling | p̂_null_pooled < 8/9 (pre-filed sim value 0.663; band ±0.06) |
| **G_SENT** | prep/readout integrity | both sentinels ≥ 0.95 |

Design-validity gate (already passed pre-freeze): noiseless quantum value = 1.0000 on all 9 contexts; theorem checks PASS.

**Figures of merit**: measured game value p̂_pooled with σ-clearance over 8/9; min-context value. **Fake preview** (FakeMarrakesh, includes routing cost): pooled 0.9779 (clearance +0.089, ≈ 250σ at these shots), min-context 0.9689, null 0.663.

**Pre-filed predictions**: W1 HIT conf 0.93; W2 HIT conf 0.85 (routing-heavy c3 contexts are the risk); G_NULL conf 0.95; G_SENT conf 0.95.

**NO-TEST conditions**: sentinel floor failure → window NO-TEST (re-fly, don't grade); transpile audit drift (2q count per context outside the audited table) → abort before submit.

## Relation to the campaign

Completes the no-go triptych in one court: Bell/CHSH (F73/F91 class, nonlocality), the causal game (F82, indefinite order), and now contextuality (H5). Companion doc: `docs/quantum-advantage-audit-whisper-c4666.md` — the Creator-question audit this experiment answers by construction.
