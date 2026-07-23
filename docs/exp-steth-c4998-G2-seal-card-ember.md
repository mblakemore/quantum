# C4998 steth-advantage — G2 seal card + design ACK + metadata-leak check (Ember)

**Gate:** G2 (coordination#821) — "seal-design ack + generation (arm T: U + trial labels; arm N:
labels), and check the arm-N block-selection rule for metadata leaks to the decision path."
Prereg: `docs/exp-steth-advantage-prereg-DRAFT-whisper-c4998.md` (DRAFT, NOT FROZEN). G1 closed
(#830). Tool: `tools/exp_steth_c4998_sealer_ember.py`. Commitments (hashes only):
`results/steth_c4998_commitments/commitments_steth_c4998_ember.json`. Secrets (seeds+salts+labels)
OFF-GIT at `~/.ember-steth-c4998-secrets.json` (chmod 600). Round-trip self-verifies (ALL VERIFY).

## 1. What is sealed (committed SHA-256, before any flight)

| item | k | commitment (SHA-256, first 16) |
|---|---|---|
| Arm T — Haar unitary U | 6 | `69a8cce658d7aa95` |
| Arm T — trial labels    | 6 | `f025c9a8e172f338` |
| Arm T — Haar unitary U | 9 | `ab1d45a177664cb8` |
| Arm T — trial labels    | 9 | `c26e25d9eeefcb57` |
| Arm T — Haar unitary U | 12| `d50cc3d87b3c5319` |
| Arm T — trial labels    | 12| `b0fb6fca9bd416f3` |
| Arm N — trial labels    | 2 | `720eeed002ce3a8c` |
| Arm N — trial labels    | 3 | `e4ef6d6053a24be5` |

M = 40 trials/rung. Full 64-hex hashes in the commitments JSON.

## 2. Commitment scheme (design choices I own as sealer — flagging for court)

- **U committed via a SECRET 32-byte crypto-random SEED**, not the raw 2ᵏ×2ᵏ matrix. The seed
  regenerates U by a PINNED draw (Mezzadri 2007 QR-of-Ginibre Haar algorithm on
  `numpy.default_rng(int.from_bytes(seed))` — tested: unitary ✓, seed-deterministic ✓, Haar ✓
  mean|U₀₀|²=0.130≈1/d). Binds U (hash includes seed), hides U (seed+salt secret), and avoids
  storing/committing a 4096×4096 matrix at k=12. **The compiled circuit for U is built at flight
  from the off-git seed and is NEVER committed** — the Exp142/F119 discipline: no public
  description of the sealed instance (the exact axis that killed F121; the seal is what makes
  Thm 7.9 apply — Elder #816).
- **Trial labels = INDEPENDENT crypto-random bits** (python `secrets`), NOT a balanced 20/20 draw.
  This is deliberate and is the *metadata-clean* choice: a fixed count is a cross-trial constraint
  that leaks into the per-trial decision path (a decoder knowing "exactly 20 ALT" gains leverage
  beyond each trial's own data). Independent bits keep every decision data-only. Realized per-arm
  balance is revealed post-hoc; chance = 50%/trial regardless. If the designer WANTS balanced
  labels for power reasons, say so and I re-seal (pre-reveal, `--force`) — but I recommend
  independent bits and flag balanced as a leak.
- **Convention pinned** in every U preimage: little-endian qiskit qubit order; ALT channel = U
  compiled once/rung; NULL channel = completely depolarizing D via fresh uniform k-qubit Pauli
  conjugation per copy (exact I/2ᵏ in expectation; fresh-per-copy = the delivery fence, no
  batching).

## 3. Seal-design ACK

The prereg §1/§3 seal design is **sound — ACK**, with the scheme above. Race-arc hygiene holds:
SHA-256 + off-git salt, Ember sole sealer, reveal only after all decisions posted. Two points I
verified actively rather than assumed:
- **NULL = fresh-Pauli-per-copy correctly realizes D for the two-copy witness.** Each of the two
  Choi copies gets an independent fresh Pauli, so the SWAP-test sees two independent samples of the
  depolarized Choi and estimates its (low) purity correctly; U gives a pure Choi. The witness
  separation is real and the fresh-per-copy delivery is the honest oracle (no batching → no F119
  determinism artifact).
- **The seed→U draw is Haar.** Verified numerically (§2). A secret crypto-random seed yields a
  secret Haar-random U — exactly the theorem's hypothesis.

## 4. Arm-N block-selection metadata-leak check (the G2 mandate)

Arm N asks the decoder to decide, per trial, DRIFTER block vs matched NON-DRIFTER block from
measurement data only, and claims the two-copy coherence witness separates what single-copy per-bit
bias cannot. **The result is only meaningful if the two blocks are indistinguishable by ANYTHING
except the coherence being tested.** The block-selection rule is "frozen at G3"; before it freezes,
here are the leak vectors the rule MUST close — the current spec ("class-best residual < 0.05, same
die region class") closes only one of them:

1. **Physical-qubit-identity / layout leak (DOMINANT).** The drifter block is a *named public qubit
   set* {53,26,73,23,45,25}; a matched null block is a *different* qubit set. If the decoder's input
   carries which physical qubits produced a trial (or the trials are delivered per-block), the qubit
   IDs ARE the label — a total leak, and both Q and C1 would "win" for free. **REQUIRED:** the
   decoder receives outcome bitstrings in a **block-identity-blind, canonically-relabeled** form
   (logical index only; identical relabeling for both blocks); no physical mapping, job, or layout
   metadata reaches the decision path. This is the analogue of the F119 "P-independent manifest."
2. **Readout/SPAM-profile leak.** If the drifter qubits have systematically different readout error
   or SPAM than the null qubits, the marginal 0/1 statistics distinguish blocks WITHOUT the
   coherence witness. "Class-best residual < 0.05" matches the *stochastic-drift* residual but NOT
   necessarily the readout/SPAM profile. **REQUIRED:** the G3 selection also matches per-qubit
   readout error and SPAM (co-batched identity/reference blocks, prereg fence #3, must show the two
   blocks' SPAM within tolerance) — else fold or reselect.
3. **Depth/structure leak.** Both blocks are "same-depth padded idle" — good; **confirm at G3** the
   compiled circuits are structurally identical (gate counts, L·L=I pad pattern, barriers) except
   the physical mapping.
4. **Trial-order leak.** Delivery order must be independent of the label (no "all DRIFT first").
   My labels are independent crypto-random bits; **REQUIRED:** trials interleaved in a
   label-independent order, and the per-copy randomization (fence #6) applied identically to both
   blocks.

**Verdict:** Arm-N labels sealed; the block-selection rule as drafted is **NOT yet leak-safe** —
it closes vector (2)'s stochastic-drift axis only. Before G3 freeze it must add: block-identity
blinding of the decoder input (1), readout/SPAM matching (2), structural-identity confirmation (3),
and label-independent trial order (4). Q's coherence-witness win is only credible once a decoder
that sees *only* the canonicalized outcomes still separates the blocks — i.e., the separation comes
from the physics, not the metadata. (Arm T has no analogue: its NULL/ALT differ only in the sealed
channel, and the fresh-Pauli NULL + compiled-U ALT are delivered on the same pinned layout.)

## 5. Status

G2 GENERATION done (8 commitments, self-verifying, secrets off-git). Seal-design ACK given.
Metadata-leak check delivered with 4 required additions to the G3 block-selection rule. Re-seal is
one command (`--force`, pre-reveal) if the court changes rungs, M, the label rule, or the NULL/ALT
definition. Reveal only after all decision postings (race-arc protocol). Awaiting G3 (Whisper sims)
+ G4 (budget + Creator GO); no QPU spent.
