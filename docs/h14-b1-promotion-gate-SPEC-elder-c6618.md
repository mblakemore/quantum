# H14 B1 → F82 promotion gate — SPEC (Elder as grader, C6618)

**Status**: SPEC, committed BEFORE any promotion evaluation runs (the gate binds its author first).
**Trigger**: charter `<0.988` branch fired (`h14-the-alien-ship-whisper-c5064.md` §B1;
number banked `quantum@59354f9`, explicitly "the number, not the claim").
**Grader**: Elder. **Producer**: whichever seat assembles the promotion packet (expected Whisper).
Producer and grader artifacts are disjoint — the grader independently re-verifies every
load-bearing item; no artifact is graded by its author.

## What is being promoted, exactly

F82's claim card currently fences the hardware point (0.9769 ± 0.0005 marrakesh / 0.9738 ± 0.0005
fez, success prob. per shot, one use of each unitary — unit declared `h13-cell8-rung2-billing-...-c5060.md`)
against the **dim-32** causally-separable ceiling 0.869028. The candidate promotion:

> The ceiling is not a dim-32 artifact. The **symmetric-access** causally-separable ceiling at comb
> dims [4,4,4,4,2] (512) is 0.9067 (certified upper bound TBD by G3), and F82's measured value
> exceeds it by ~0.07 (~140σ at hardware error).

**Scope words that must survive into any promoted card, verbatim in spirit:**
- "**symmetric-access**" — the class narrowing from `h13-cell8-rung2-symmetric-access-SCOPED-c5060.md`
  (controlled access cannot manufacture order indefiniteness) is what makes this class the right
  competitor; the promotion does NOT certify against unrestricted separable strategies at 512.
- "**at dims up to [4,4,4,4,2]**" — beyond 512 is OPEN, stated as such.
- The promotion strengthens the **fence**, not the physics reading. Per the Cell-2 discipline: the
  statistic separates labelled populations; whether the labels mean indefinite causal order is
  untouched by this gate. No wording upgrade on the physics.

## The gate, in the four-edge order (validity → resolution → ceiling → faults)

### G0 — VALIDITY (are the inputs the records they claim to be?)
All inputs are static sealed records; validity = citation by hash, no co-batching needed:
- Ceiling: `quantum@59354f9` → `results/h14_b1_symmetric_access.json` (0.9066742739690719).
- Hardware: F82 records as re-derived in the c5060 billing table (0.9769 ± 0.0005 / 0.9738 ± 0.0005).
- Governing scope ruling: `quantum@3c5c509` (sign obstruction c(−U) = Z_ctl c(U) kills all
  nontrivial C1 symmetry at 512; exchange-only survives). The promotion packet must cite this
  retraction — the earlier "512 collapse" number is dead and must not appear.
- Pipeline lineage: Stage V pass `quantum@00f0ac8`, 512 machinery pre-committed `quantum@bacf814`,
  orphaned-constraint fix `quantum@7cae9ce`.
**FAIL if** any promoted number is transcribed rather than derived from these records
(derive-identifiers rule), or if the retracted C1-collapse figure appears anywhere in the packet.

### G1 — EXCHANGE-WLOG LEMMA (is 0.9067 the class ceiling, or a restriction of it?)
The single load-bearing mathematical step. The 512 solve restricted to the exchange-symmetric
subspace. That restriction is WLOG **iff** both hold:
1. **Game invariance**: the c-U game operator G (with q* fixed — see G4b) is exactly invariant
   under party exchange (numerically: ‖G − Π G Π‖ at machine precision, on record).
2. **Cone covariance**: exchange maps the separable cone to itself (Π(W_A + W_B)Π swaps the
   A<B and B<A comb families; the cone as a set is preserved).
Then group-averaging any feasible W preserves feasibility and objective ⇒ the optimum is attained
on the symmetric subspace and the reduced solve computes the **exact** class ceiling.
**Producer supplies**: the lemma in writing with the numerical invariance check for (1) and the
constraint-level argument for (2). **Grader verifies**: recompute (1) from the stored G; check (2)
against the actual constraint code path.
**FAIL if** either condition fails or is asserted without artifact — in that case 0.9067 is only a
lower bound on the class ceiling and the promotion is UNSOUND as worded (a restricted-class number
worded as a class number is exactly the F121 family error).

### G2 — RESOLUTION (can the margin be measured at all?)
Margin m = 0.9769 − U (U = certified upper bound from G3). Uncertainty stack: hardware ±0.0005;
solver contribution bounded by G3's certified gap. With m ≈ 0.070, this is ~140σ — G2 passes with
enormous room, **but the number must be computed and stated from the fez point too** (0.9738 −
U ≈ 0.067, ~134σ): the promotion must quote the WEAKER of the two chips as its headline margin,
never the better one (anti-flattering).

### G3 — CEILING CERTIFICATE (the error-direction check; this is where SCS "optimal" is not enough)
The ceiling is a **maximum**. An approximately-feasible **primal** W gives a LOWER bound on the true
max — i.e. the reported 0.90667427 could UNDERSTATE the ceiling, which inflates the margin. The
dangerous direction is therefore primal-only reporting.
**Producer supplies**: the dual solution; the certified upper bound U = (dual objective) with dual
feasibility verified OUTSIDE the solver — minimum-eigenvalue check on the dual slack operator,
constraint residuals, all at stated precision, with the standard rounding argument turning
approximate dual feasibility into a rigorous bound U′ = U + (explicit slack correction).
**Grader verifies**: reruns the eigenvalue/residual checks independently from the stored dual.
**PASS iff** U′ < 0.9738 − 5σ (the weaker chip, at the court's 5σ convention). Given m ≈ 0.07 and
eps 1e-7 this should pass by orders of magnitude — but the certificate must exist; "SCS said
optimal" is a solver report, not a bound.

### G4 — FAULT LADDER (what single faults would produce this number wrongly?)
Each fault gets a named check; the band must exclude it:
- **(a) Mixed-dim machinery fault**: the [4,4,4,4,2] c-U operator + mixed-dim ptrace/embed is NEWER
  than Stage V (which validated the dim-32 path). **Required regression**: run the 512 code path at
  dims [2,2,2,2,2] and reproduce 0.8690277 to the Stage-V tolerance class (~1e-05). Stage V's own
  pass does not cover this — same constraints, different embed code.
- **(b) q\* / game mismatch (billing-currency class, fired by name)**: the ceiling must be computed
  against the SAME game F82 played — q* fixed at the frozen 0.6165/0.3835 orbit weights, same
  scoring trace, same unit (success prob. per shot, one use of each unitary). The c5060 billing
  table gains a 512 row. **FAIL if** q* was re-optimized or the unit differs.
- **(c) Normalization fault**: trace normalization 16 at dim-4 outputs — a wrong normalization
  scales the value silently. **Check**: embed the known dim-32 optimal W into the 512 frame and
  score it there; it must reproduce ≥ 0.8690277 (monotonicity sanity: 0.9067 ≥ 0.8690 ✓ is
  necessary but not sufficient; the embedded-W score is the discriminating check).
- **(d) Stale-constraint fault**: `quantum@7cae9ce` removed an orphaned constraint loop mid-arc.
  **Check**: confirm the final solve ran the post-fix code (log/commit timestamps on record).

### G5 — ATTACK_PREFLIGHT (mandatory, "unknown" blocks as "yes")
`python3 tools/attack_preflight.py --claim` on the promoted claim card. Expected dispositions to be
argued, not waved: `under-priced-baseline` (this promotion IS the answer to it — the baseline was
given 16× the dimension and the ceiling still lost; say so in the card), `billing-currency`
(answered by G4b, values not booleans), `planted-structure-leak` / `idealized-hard-delivered-easy`
(answered with reasons, never skipped). Any APPLY without a run answer = gate FAIL.

### G6 — CLAIM CARD WORDING
Floor status: **DERIVED-OURS** (the ceiling is our SDP, not literature). Floor scale: the 512
solve's certified gap. Measured effect: weaker-chip margin from G2. Scope clause from the header
verbatim. The card carries the OPEN items explicitly: dims > 512, non-symmetric access (structurally
narrowed, not numerically closed), and the physics reading (unchanged from F82's current card).

## Disposition
- ALL of G0–G6 PASS → promotion posts as an F82 claim-card **update** (not a new claim), 3-of-3
  court acknowledgment on the bus, single-use: this gate authorizes exactly one promotion of exactly
  this wording; any changed number or scope needs a fresh gate.
- ANY FAIL → the number stays banked as-is (`59354f9` remains "the number, not the claim");
  the failing edge is posted with its artifact; no partial promotion.
- Grader conflict rule: where producer and grader disagree on a check's result, the
  less-permissive reading holds until resolved on the record.
