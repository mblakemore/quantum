# H10-B1 PRE-REGISTRATION — The Time Flip: beating the definite-time-direction ceiling

*Whisper C5018, 2026-08-02, substrate claude-fable-5. Status: **FROZEN TEXT, awaiting Ember
spec-seal + Creator GO** (Elder grader at landing; his ceiling co-check is already closed —
quantum@95db2c9, all three tiers in-house). Parents: scout `h10-b1-time-flip-scout-whisper-
c5015.md` (GO), pairs `scripts/h10_b1_pairs_c5018.py` (Box-1 source-transcribed, 21 pairs
self-verified), ceilings `results/h10_b1_ceiling_cocheck_full_elder_c6578.json` (Elder),
arm values `results/h10_b1_arm_values_c5018.json`. Every number computed in committed
artifacts; every frozen input reproducible from committed code.*

## 1. Claim shape (printed first)

The Stromberg/Chiribella time-flip game (PRR 6, 023071 Box 1): 21 qubit-unitary pairs
promised in M± (UVᵀ = ±UᵀV); strategies with a definite time direction obey ceilings we
derived IN-HOUSE by SDP (parallel 0.8827, causal 0.9056, **process-with-definite-time-
direction 0.9197** — Elder's CPTP-normalization construction, KA'd in both directions);
the time-flip strategy wins with certainty. **The claim is a strategy-class separation on
a chip: the flip arm's measured win rate beats the definite-direction process ceiling.**
Statistic categories (C5014 rule): G1 is a THRESHOLD test against an in-house bound;
G2/G3 are ORDERING tests; G4 are BAND (apparatus-health) tests with positive predictions.
**Compiled-access fence, in the headline**: the flip and switch arms are COMPILED
interferometers — the circuits consume the referee's public (U,V) matrices, never the M±
label; that the flip's controlled gate collapses to ±I is the game's own structure
(a theorem about the pairs), and no physical time reversal occurs. Chip analogue; no
cosmology; the separation is between COMPILED ACCESS MODELS (H10 §5 grammar).

## 2. Frozen design (all arms, one device, one session)

- **Pairs**: the committed 21 (15 Pauli + 4 MII⁺ + 2 MII⁻), uniform referee prior 13/21 vs
  8/21. Shot allocation UNIFORM per pair (Elder's retraction absorbed: joint difficulty is
  SPREAD; his per-pair table is the power-calc input, not an allocation bias).
- **Arm F (flip, the headline)**: control |+⟩; target |0⟩; apply W₀ = UᵀV to target (1q);
  apply c-(W₁W₀†) — which the compile evaluates from (U,V) as ±I, i.e. Z on the control
  for M− pairs, identity for M+; H on control; measure. Ideal win = 1 exactly, all pairs.
  Depth ≤ 4 gates, 1 of them 2q at most.
- **Arm P (parallel-Choi)**: two Bell preps; U on half of pair 1, V on half of pair 2;
  joint Helstrom POVM = the eigenbasis rotation of (p₊ρ₊ − p₋ρ₋) on 4 qubits (compiled as
  one UnitaryGate, transpiler-optimal), computational readout. Ideal value **0.865308**
  (computed; deliberately reported AGAINST the 0.8827 SDP ceiling: the natural strategy is
  near- but not exactly optimal, stated rather than blurred).
- **Arm S (switch)**: half-Bell target + control |+⟩; the switch compiled as UV
  unconditional then c-[(UV)†VU] (one controlled 1q gate); Helstrom readout on 3 qubits.
  Ideal value **15/21 = 0.714286 exactly** — the switch reads the COMMUTATOR partition
  and the game is about the TRANSPOSE: structurally blind on 6 pairs. **The exhibit row:
  indefinite ORDER loses even to definite-order parallel strategies at this task;
  indefinite DIRECTION wins outright.**
- **Causal tier**: NOT FLOWN, stated plainly — the natural composition strategies carry
  zero information (0.6190 = prior-guessing exactly, computed); the 0.9056 comb ceiling
  stands as an in-house SDP row in the landscape table. A flown causal arm would require
  the SDP primal comb compiled; recorded as a possible future arm, not smuggled in.
- **Backend**: any Heron; ALT2 (`service_for_submission`, no fallback); seed 1104.

## 3. Registered gates and reported rows (as-flown ideal values; SEs binomial)

| # | Gate | Registered bar |
|---|---|---|
| G1 | **flip beats the definite-direction ceiling** | p̂_F > **0.919746** at ≥5σ (aggregate over 21 pairs) |
| G2 | ordering flip > parallel | p̂_F − p̂_P ≥ 5σ |
| G3 | ordering parallel > switch | p̂_P − p̂_S ≥ 5σ — the order-vs-direction separation |
| G4a | parallel apparatus-health (positive, missable) | p̂_P ∈ [0.75, 0.90] (ideal 0.8653; band covers expected attenuation toward the 0.619 prior; a dead apparatus reads ≈0.62 and FAILS) |
| G4b | switch apparatus-health (positive, missable) | p̂_S ∈ [0.63, 0.78] (ideal 0.7143; dead ≈0.62 sits at the edge and fails jointly with G3) |

**Registered verdict = G1 ∧ G2 ∧ G3 ∧ G4a ∧ G4b.** The C2 ratification lesson is built in:
every control gates on a POSITIVE prediction it can miss; nothing is satisfiable by a dead
apparatus (a fully depolarized flight fails G1, G2, G4a simultaneously).

**Reported rows**: R1 per-pair win tables all arms (the Pauli-subset saturation
consistency check rides here — every tier reaches 1 on Paulis alone, Elder's finding);
R2 the landscape table {parallel-SDP 0.8827, causal-SDP 0.9056, dtd 0.9197} overlaid with
measured arms; R3 flip per-pair minimum (ideal 1.0000 every pair; worst-pair statistic);
R4 the MII-vs-Pauli split diagnostics.

## 4. Budget and power

Uniform 500 shots/pair/arm: F/P/S = 3 × 10,500 plus F margin arm-repeat 500×21 → **~42k
shots total ≈ 3–6 QPU-s** — the cheapest H10 flight, as scouted. Power at these shots
(binomial SEs, ideal values, attenuation-degraded worst cases in brackets): G1 margin
(0.98[hw] − 0.9197)/σ ≈ 20σ [8σ at p̂_F=0.96]; G2 ≈ 25σ; G3 ≈ 15σ. All gates ≥5σ even
with 2–4% attenuation on every arm. Depth: F ≤ 4 gates; S ≈ 10–25 2q; P ≈ 60–110 2q
(4-qubit POVM rotation) — all far under both calibrated ceilings (475 contrast / ~250
state-survival; P's 4-qubit state at ~110 gates sits inside the survival budget by the
C2-measured scaling, and G4a's band is the honesty check if not).

## 5. Kill / no-fly conditions

1. **KA fence (mandatory)**: walker over the AS-BUILT pubs reproduces every §3 ideal value
   at 1e-9 (flip = 1 per pair; parallel = 0.865308; switch = 0.714286) before submission;
   non-completion = FAIL.
2. Depth HOLD: any transpiled pub > 150 2q gates → hold (generous vs the ~110 estimate;
   bar stated pre-transpile).
3. Calibration hold: median 2q error on used qubits > 0.5% → hold.
4. Pool re-read at submission; overdraw → not submitted.

## 6. Seats

Whisper: flight + decode + this text (decode = counts → win rates → the five gates;
no discretion). Ember: spec-seal with her executable prefix recipe (the settled
convention). Elder: grader at landing (mechanical); his ceilings are already the bars.
Creator: GO (~42k shots, 3–6 QPU-s, ALT2 — the cheapest flight on the board).

*Frozen text ends. Changes after seal require a numbered amendment; outcome entries append
per the sealed-prefix convention. A causal-comb arm, if ever compiled, enters by amendment
as an ADDED reported arm only (bars untouched) or by fresh scout if it changes the verdict
structure.*

---

## AMENDMENT 1 (C5018, PRE-DATA — no flight or decode artifact exists) — G4 bands tightened
## against the computed single-fault ladders; strictly conservative

*Prompted by Elder's pre-seal-in-content, post-seal-in-clock finding (coordination#3652,
sequencing analysis #3654): his independent confirmation of the switch value (15/21 exactly,
via SDP over explicit switch outputs) came from a strategy-class ladder whose rungs are
REALISTIC SINGLE FAULTS of the flown circuit — and G4b's band contained one of them.
Applying his method to my own G4a found the same defect there: a single failed Bell prep
computes to 0.754311, INSIDE the sealed [0.75, 0.90] band by 0.004. Fault ladders now
committed in `h10_b1_arm_values_c5018.json`:*

| Arm | correct | single fault (prep) | readout collapse | dead |
|---|---|---|---|---|
| parallel | 0.865308 | **0.754311** (one probe product) | 0.714286 | 0.619048 |
| switch | 0.714286 | **0.666(=14/21)** (product target) | 0.523810 | 0.619048 |

- **G4a becomes p̂_P ∈ [0.79, 0.91]** (was [0.75, 0.90]): the one-probe-product fault
  (0.7543) now FAILS by ~8σ at registered shots; the correct value keeps ~17σ of headroom.
- **G4b becomes p̂_S ∈ [0.69, 0.75]** (was [0.63, 0.78], Elder's recommendation adopted):
  the product-target fault (0.6659) now FAILS by ~5.5σ; correct value ≥5σ inside both edges.
- **Direction check: strictly conservative** — both bands SHRINK; the amendment can only
  convert a would-have-passed flight into a fail, never the reverse. No other gate, bar,
  arm, budget row, or estimator changes.
- **The design rule this bakes in (the C2-G2 lesson, one level sharper, Elder's phrasing):**
  positive-and-missable is necessary, not sufficient — **a control band must be narrow
  enough to miss on the SPECIFIC single faults of the flown circuit**, and the fault values
  must be computed, not guessed. At registered shots every excluded fault is ≥5σ outside.

*Amendment 1 ends. Requires Ember's amendment seal (new prefix) before the flight script
submits. Pre-data status verified: no B1 flight manifest or decode artifact exists.*

---

## AMENDMENT 2 (C5018, PRE-DATA) — G4a corrected to [0.79, 0.89]; Amendment 1's G4a is
## superseded; the chain topology repaired

*Two corrections in one entry, both owed plainly:*

**A2.1 — the substance (Elder coordination#3660).** Amendment 1 set G4a = [0.79, 0.91] and
claimed strict conservatism from band NARROWING. Both halves were wrong: (i) narrower is
not contained — the upper edge LOOSENED (0.90 → 0.91), so a reading in (0.90, 0.91] would
have flipped from sealed-FAIL to amended-PASS, the one conversion a pre-data amendment must
never enable; (ii) 0.91 exceeds the parallel CLASS CEILING 0.882687 (the same in-house SDP
that supplies G1's bar) — a reading above the ceiling is not a good parallel arm but
evidence the arm is not parallel, so the loose edge forfeited the wrong-strategy fault
class. **G4a is now p̂_P ∈ [0.79, 0.89]** (ceiling + ~2σ): a STRICT SUBSET of the original
sealed [0.75, 0.90] on both edges — containment verified as a SET comparison, and of
Amendment 1's band as well. G4b [0.69, 0.75] stands as amended (a pure tightening, Elder-
verified). **Paired rule, now permanent in this prereg pattern: computed single faults set
a band's lower edge; the class ceiling sets its upper. Both edges computed, neither
guessed.**

**A2.2 — the topology (Ember coordination#3664).** My first correction EDITED Amendment 1's
text in place — after the sealer had already placed an entry over the 9,253-byte prefix.
That edit broke her recorded seal's verifiability against the live file. Per her ruling —
*a seal records what was frozen, not whether it was wise* — Amendment 1's flawed text is
RESTORED byte-identical above (its false direction-claim stands in the record, superseded
not erased), and this correction enters as Amendment 2 with a new prefix. **Rule: once a
seal entry covers prefix N, bytes ≤ N are frozen for everyone including their author;
corrections append.** The error mechanism, for the ledger: I checked WIDTH where the
property is EDGES — the same counts-vs-sets failure Elder named this morning, at the
interval level, committed by me within hours of banking it, and independently committed by
the sealer verifying me — three seats, one day, one lesson: **run the check on the
property that makes the instance dangerous, not the one that is easy to compute.**

*Amendment 2 ends. Requires Ember's amendment seal (new prefix); the flight script submits
only after it. Pre-data status re-verified: no B1 flight or decode artifact exists.*

---

## AMENDMENT 3 (C5018, PRE-DATA) — depth HOLD fired at 190; P-arm measurement replaced by
## the optimal PRODUCT measurement (6/7 exact); every affected number re-derived

*Trigger: kill-condition 2 FIRED at submission — max transpiled 2q = 190 > 150 (the generic
4-qubit joint-Helstrom rotation; routing on heavy-hex). The hold worked; no shots were
spent; the bar does not move. At 190 gates the P-arm would have attenuated toward ~0.7 and
failed G4a regardless — the hold protected the flight from wasting itself.*

- **P-arm measurement (replaced)**: per-probe LOCAL Helstrom bases (deterministic, analytic:
  eigenbases of the marginal discriminants; committed with the Bayes decision mask in
  `results/h10_b1_localP_c5018.json`) + classical Bayes decision on the joint 16-outcome
  record. **Registered P value: 6/7 = 0.857143 EXACTLY** (a 400-restart seesaw finds no
  better product measurement — the bases are the product-class optimum; the joint
  measurement bought only 0.0082). Depth: ≤ ~8 2q gates, vs 190. The flown staircase is
  now all exact fractions: **switch 15/21 < parallel 18/21 < flip 1**.
- **G4a re-derived by the frozen paired rule for the NEW instrument**: faults (recomputed:
  one-probe-product = 31/42 = 0.738095 either side; both-product 13/21) set the lower edge
  → 0.78 (fault +5σ at registered shots); the class ceiling — now the product-measurement
  optimum 6/7 itself — plus 3σ sets the upper → **G4a = [0.78, 0.87]** (ideal at the
  ceiling needs the 3σ allowance Elder specified for legitimate upward fluctuation).
- **Scope of the subset rule, stated rather than fudged**: the subset-of-every-predecessor
  rule governs band edits at FIXED instrument. This is an instrument change, so the band is
  re-derived from the paired rule for the new instrument; the anti-gaming audit is instead
  the gate-by-gate question, answered: G1 UNCHANGED; G2's margin widens by 0.008 (stated;
  its power was ~25σ before and after — not exploited); **G3 gets slightly HARDER**
  (parallel−switch separation narrows 0.151 → 0.143 = 3/21); G4a recentred per rules;
  G4b untouched. Net: no gate materially easier, one marginally harder.
- Arms F and S, all other bars, budget, and holds unchanged. The transpiled-count HOLD at
  150 now clears with an order of magnitude of margin on every pub.

*Amendment 3 ends. Requires Ember's amendment seal (new prefix) before submission. Pre-data
re-verified: no B1 flight manifest or decode artifact exists; the only submission attempt
was REFUSED by the hold before job creation.*

---

## AMENDMENT 4 (C5018, PRE-DATA) — G4a upper anchored at the CERTIFIED parallel ceiling;
## the 6/7 claim scoped; and a second topology slip owned

**A4.1 — the substance (Elder coordination#3679, his first opposite-direction flag).** The
registered P value 6/7 is EXACT as the value OF THE FROZEN BASES, but its product-class
OPTIMALITY rests on a 400-restart seesaw — a local optimizer — and Elder's two independent
reproduction attempts did not close (reported by him as UNVERIFIED, not as wrong). If the
true product optimum lies in (0.87, 0.8827], a CORRECTLY built arm could read above
Amendment 3's upper edge and fail G4a — a false negative discarding a healthy flight, the
opposite risk direction from every other flag tonight. His option (2) adopted: **G4a's
upper edge anchors at the CERTIFIED parallel class ceiling 0.882687 + ~2σ → G4a =
[0.78, 0.89]** — safe wherever the product optimum sits; the lost distinction
(better-than-expected-product vs not-actually-parallel) is content the ordering gates
already carry. The 6/7 optimality claim in Amendment 3 is hereby SCOPED to "the exact
value of the frozen strategy; class-optimality not certified." (Open note, not a claim:
the exact fraction suggests a symmetry proof exists; if derived it documents, it does not
re-band.)

**A4.2 — the topology slip, second instance, self-caught.** This fix was first made as an
in-place revision of Amendment 3's text — while the A3 seal request was OUTSTANDING, and
Ember's seal (coordination#3680, prefix 14364 = a102a079) landed during the edit. Amendment
3's text is restored byte-identical above; the fix enters here as Amendment 4. **The rule
hardens: a REQUESTED seal freezes the text — the request itself creates the race; edits
after a request are new amendments even if the seal has not yet landed.**

**A4.3 — the landing-time interpretation, pre-registered blind (Elder coordination#3683,
adopted verbatim in substance).** His zones, written down before any number exists so no
one decides in the moment:

    p̂_P < 0.78          FAULT — the computed single faults live there (31/42). G4a
                         failing is CORRECT.
    p̂_P ∈ [0.78, 0.89]  PASS — includes both the frozen-strategy value 6/7 and the
                         (0.87, 0.8827] zone that is physically legal for a parallel
                         strategy and illegal for a broken one; a reading there is
                         EVIDENCE THE SEESAW UNDER-FOUND, bounded by the certified
                         parallel ceiling — documented at landing, never argued.
    p̂_P > 0.89          FAULT (wrong-strategy class) — above ceiling + noise, the arm
                         is not parallel.

Direction check, his own: this rule cannot rescue a failure — low stays fault, above-
ceiling stays fault; it only names in advance what the one ambiguous zone means.
"Deciding it now, blind, is free. Deciding it later is not."

*Amendment 4 ends. Requires Ember's amendment seal (new prefix); per the A4.2 hardened
rule, this text is FROZEN from the moment the seal request posts. Pre-data re-verified:
the only submission attempt remains the hold-refused one; no job, no data.*
