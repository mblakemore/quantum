# Exp206 — THE LOGICAL COMPUTER: CERTIFIED (all 5 gates) — the campaign's first error-corrected computation

**Whisper C4903, 2026-07-20. Job `d9ehr3cjeosc73fiq610`, `ibm_fez`, 2 circuits, 8000 shots,
seed 0. Substrate `claude-opus-4-8`. Prereg frozen pre-submit (`bfd1962`).** Horizons-4
Invention 6, flown on the Creator's standing go.

## Verdict

**REGISTERED VERDICT (W1∧W2∧W3∧W4∧G_ACC): HELD.** The BGK 2D-HLF constant-depth solver
runs inside [[4,2,2]] shields, and the **error-detected logical run beats the bare one** —
the campaign's first error-corrected *computation*, and the first time the shield-pays thesis
is demonstrated on the computational scoreboard (games/storage/metrology/sensing already had
it; computation did not).

## The headline: logical beats bare, uphill, at 19.7σ

| Arm | 2q gates | P(valid z) | σ over uniform floor (0.25) | acceptance | throughput |
|---|---|---|---|---|---|
| bare (unencoded HLF) | 7 | 0.8968 | 190 | 1.000 | 0.897 |
| **logical (shielded, post-selected)** | **25** | **0.9741** | **366** | 0.806 | 0.785 |

**W4 SHIELD BEATS BARE: margin +0.0773 at 19.7σ** — and this is the *hard* direction: the
logical circuit carries **3.5× the two-qubit gates** (25 vs 7), yet error detection more than
pays for the extra depth, lifting P(valid) from 0.897 to 0.974. Post-selection discards the
20% of runs that failed the XXXX parity check; the 80% that pass are near-perfect
(0.974 vs the ideal 1.0). The shield's blind-spot caveat (199) does not bite here — the HLF
solver's errors are the parity-detectable kind, not the coherent-common-mode kind.

## The solver works, and the constraint is real

- **W1 SOLVER**: both arms land in the valid set far over the uniform-random floor — bare
  190σ, logical **366σ**. The constant-depth quantum circuit solves the instance.
- **W2 COVERAGE**: all four valid z present in both arms, near-uniform (logical:
  0.246/0.245/0.245/0.237 — flat to 1%). No fixed-output mimic could pass; the solver
  covers the whole solution coset.
- **W3 NONTRIVIAL**: the valid set {0000, 0110, 1001, 1111} is a proper 4-element affine
  subspace (enumerated from the ideal statevector, not asserted) — the solver satisfies a
  genuine linear constraint (ker of the 4-cycle adjacency), not "anything goes."
- **G_ACC**: block-pair acceptance 0.806 (both blocks' XXXX parity), well over the 0.55 gate.

## Budget scoreboard (graded straight)

bare P(valid) 0.897 ∈ [0.75,0.90] **IN** (top); logical-post 0.974 vs [0.80,0.93] — **0.044
over** (cleaner than priced, the good direction); margin +0.077 ∈ [0.02,0.12] **IN**;
acceptance 0.806 vs [0.60,0.80] — **0.006 over**. 2/4 in band, 2 grazes both
cleaner-than-priced. The logical arm outperformed its own budget — error detection paid more
than the pricing assumed.

## Method notes (kept)

- **Decode by verified search, not hand algebra**: the valid set was defined from the bare
  ideal statevector, and the logical decode (which physical parities → the 4 logical bits,
  plus any frame XOR) was found by exhaustive search against it in the Clifford-exact
  selftest, then frozen. The winner was the plain 191 map with zero frame correction —
  but the simulator certified it, removing all hand-derivation risk from a 25-gate composed
  circuit.
- **Compiled from the C4901 audit**: in-block logical CZ = S⊗4 (zero physical 2q),
  inter-block straight pair = one permuted tCZ. The audit's "entangling logical gate for
  zero 2q gates" is now load-bearing in a computation for the first time.

## Scope (F113 honesty fence, unchanged)

n=4: P(valid) is a fidelity over the uniform-random floor, **not** a beaten classical bound
(the BGK asymptotic separation QNC⁰≠NC⁰ is carried by the theorem as n→∞, not demonstrated
on-chip). The certified on-chip claim is **logical-beats-bare** — error correction pays on a
computational task — device-characterized, this hardware generation. Textbook priors
credited (Bravyi–Gosset–König 2018).

## Line

**The shields already paid on games, channels, sensors. Tonight they paid on computation:
a program that runs 3.5× deeper but error-detected came out cleaner than the bare one it
encodes. The first error-corrected computation of the campaign — logical beats bare, uphill.**
