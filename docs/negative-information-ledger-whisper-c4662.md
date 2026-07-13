# The Negative-Information Ledger (H2) — Whisper C4662

**Horizons-3 H2, Creator: "Run H2!" Total QPU cost: ZERO shots.** Tool:
`tools/entropy_ledger.py` → `results/entropy_ledger_c4662.json`. Source theory:
QCQI Ch11 (read C4659) — Fannes continuity, negative conditional entropy,
entropy-vs-twirl monotonicity.

## The scope correction that leads (my own C4659 export had a bug)

My reading-cycle pattern claimed "every TVD certification converts to an entropy
certification." **Overstated.** Observed measurement TVD only LOWER-bounds the
states' trace distance; quantum Fannes needs an UPPER bound. Corrected split:
- **Always valid**: CLASSICAL Fannes on the measured outcome distributions —
  |H(p)−H(q)| ≤ T·log₂d + η(T). Leg 1 claims are Shannon-entropy claims about
  distributions, stated as such.
- **Quantum (von Neumann) claims need another route** — leg 2 builds one.
Caught at implementation, corrected in the pattern store. The court applies to
my book reports too.

## Leg 1 — Shannon-Fannes certifications (from banked bounds)

| Certified source | T bound | \|ΔH\| bound |
|---|---|---|
| F96 hotspot schedule-symmetry | 0.0303 | **≤ 0.304 bits** |
| F96 control | 0.0393 | ≤ 0.380 bits |
| Exp118 duration artifact (D_A, 5SE-inflated) | 0.0808 | ≤ 0.697 bits |
| switch-bench sched card (regression path) | 0.0302 | ≤ 0.303 bits |

Reading: the transpiler's "parallel" not only preserves the outcome distribution
to 3% TVD — it preserves its *information content* to 0.3 bits, certified.

## Leg 2 — Entanglement by negative ink (banked CHSH → von Neumann claim)

From Exp112b-micro's four CHSH correlators (S = 2.453, 16k banked shots):
- Setting geometry gives **⟨XX⟩+⟨ZZ⟩ = S/√2 = 1.7345 ± 0.0224** (derived
  in-code from the measured E's).
- **Positivity forces the unmeasured ⟨YY⟩ ≤ −0.734** — the Bell-twirled state
  has no choice but strong Y anti-correlation.
- Worst-case MAXIMIZATION of H(p_Bell) over the unknown ⟨YY⟩ and XX/ZZ split
  (one-sided conservative; twirling itself only increases entropy, so the
  twirled claim is safe against the untwirled truth):
  **H ≤ 0.9014 even at −5σ on the measured sum.**
- Therefore **S(B|A)_twirl ≤ −0.0986 at 5σ** (point: −0.296):
  **NEGATIVE CONDITIONAL ENTROPY CERTIFIED** — Bob's registry knows MORE than
  its own contents once Alice's side exists; the Ch11 entanglement witness
  (Ex 11.14 lineage), operationalized from data that had already flown.

Scope (stated): claim is for the Bell-twirled banked state (LOCC-constructible);
standard CHSH setting geometry per the Exp112 apparatus; one banked dataset.

## Method exports

1. **Twirl + positivity + worst-case-maximize** = a general recipe for turning
   partial correlator sets into certified one-sided von Neumann entropy bounds
   — reusable on every banked CHSH dataset we own (Exp112, Exp114 raw AND
   purified — a purification-arc entropy audit is now a free follow-up).
2. Certified-TVD → certified-Shannon column now mintable for any bench card.
3. The negative-ink witness is a switch-bench candidate axis (4th): certify
   S(B|A) < 0 from the causal module's existing correlators at zero extra pubs.

Ember numbering requested (candidate: entanglement certified by negative
conditional entropy at zero marginal cost; the scope-corrected Fannes column as
subclaim; method = twirl+positivity worst-case).
