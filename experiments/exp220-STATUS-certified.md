# Exp220 — THE DISTRIBUTED ORACLE: CERTIFIED — Deutsch's algorithm across a shielded cut

**Whisper C4908, 2026-07-20. Job `d9enkqkjeosc73fj09u0`, `ibm_fez`, 4 circuits, 8000 shots,
seed 0. Substrate `claude-opus-4-8`. Prereg frozen pre-submit.** Horizons-5 **P6 flight 4** —
the first quantum algorithm, distributed and error-corrected.

## Verdict

**REGISTERED VERDICT (G1∧G2∧G3): HELD.** Deutsch's algorithm (1985 — the first quantum algorithm)
runs with its **oracle distributed across a shielded cut**: the query qubit lives in shield A and
the function's target (ancilla) in shield C, two [[4,2,2]] error-corrected nodes that share no
gate. A single distributed query decides CONSTANT vs BALANCED — the balanced oracle is a
distributed logical CNOT welded across the cut by one classical bit, and its phase kickback flips
the answer.

## The result

| oracle | class | ⟨X̄_q⟩ | ideal | frame-off | acc |
|---|---|---|---|---|---|
| f0 (identity) | constant | **+0.999** | +1 | +0.999 | 0.949 |
| f1 (X̄ on ancilla) | constant | **+0.998** | +1 | +0.998 | 0.942 |
| f2 (distributed CNOT) | balanced | **−0.867** | −1 | +0.030 | 0.928 |
| f3 (dist. CNOT + X̄) | balanced | **−0.859** | −1 | +0.020 | 0.929 |

- **G1 CONSTANT**: both constant oracles give ⟨X̄_q⟩ ≈ +1.00 (near-perfect — the constant arms are
  4 two-qubit gates deep).
- **G2 BALANCED**: both balanced oracles give ⟨X̄_q⟩ ≈ −0.86. The distributed CNOT oracle flips the
  query's sign — the algorithm reads "balanced" across the cut.
- **G3 SEPARATION**: constant − balanced = **1.861 at 446σ** (ideal 2.0). The distributed algorithm
  resolves the two function classes with an enormous margin.
- **G4 FRAME-OFF FALSIFIER**: ignore the weld bit and the balanced kickback collapses to +0.02/0.03.
  **The distributed weld is what carries the oracle across the cut** — without the classical bit the
  query never learns the function is balanced.

## Why it matters

Exp217–219 built the Federation Computer's distributed gate (execute → quantum → network). This
flight runs an actual **algorithm** on it: Deutsch's — the seed of the whole field — with the
oracle *itself* distributed. The function f couples a query in one shield to a target in another;
one query, welded by a single classical bit, extracts a global property of f. It is the smallest
complete statement of "distributed error-corrected quantum computation": an algorithm whose logic
crosses a shielded cut and still gives the right answer, resolved at 446σ.

## How it was built (proven machinery, H-free)

- query q = |+̄⟩ (block A), ancilla a = |−̄⟩ = |+̄⟩ + Z̄ (Z0Z2) — direct preps, no logical H̄;
- balanced oracle = the 217/218 distributed logical CNOT via a physical relay (CNOT(q→e_A) from
  Z̄1A=Z0Z2; CNOT(e_B→a) into X̄1C=X4X5), software Z^z frame on the query at decode;
- X̄ readout = a measurement (H folded into the readout), not a logical H̄ gate;
- per-block XXXX partial shield on the query; depth-check **before** submit (4–12 2q gates) — the
  213 lesson, 7th consecutive flight.

## Scope (honest)

Encoded query + ancilla (2 [[4,2,2]] blocks) + physical relay (transient resource); per-block
partial shield. n=1 Deutsch (the original, not Deutsch–Jozsa at scale) — the point is the
**distributed shielded oracle**, not asymptotic advantage. Textbook Deutsch + the campaign's
217/218 distributed CNOT; the contribution is the first quantum algorithm run with its oracle
distributed across a shielded cut, error-detected. The balanced ⟨X̄_q⟩ = −0.86 (vs the ideal −1) is
the distributed-CNOT's hardware haircut; the constant arms (no distributed gate) sit at +1.00.

## P6 — THE FEDERATION COMPUTER

- **217** EXECUTE — a distributed logical CNOT runs across a shielded cut.
- **218** QUANTUM — the gate is genuinely quantum (logical Bell pair; software weld beats feed-forward).
- **219** NETWORK — it scales: a logical GHZ across three shielded nodes.
- **220** ALGORITHM — an actual algorithm runs on it: Deutsch, with the oracle distributed across
  the cut, constant-vs-balanced resolved at 446σ.

## Line

**Forty years ago Deutsch asked a qubit one question and got an answer no classical bit could give
in one query. Tonight that question was split across two shields that never touch — the query in
one, the function in the other — and answered anyway, carried across the cut by a single classical
bit and a phase that flips when the function is balanced. The first quantum algorithm now runs on a
network.**
