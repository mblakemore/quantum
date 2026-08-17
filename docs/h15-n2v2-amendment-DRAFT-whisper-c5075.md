# H15 N2v2 — PRE-REGISTRATION AMENDMENT (DRAFT)

**Whisper C5075 · substrate `claude-opus-5` · 2026-08-17**
**Amends**: `docs/h15-n2-positronic-neuron-prereg-DRAFT-whisper-c5074.md` (the N1 card)
**Evidence**: `results/h15_r1_probe_kingston_decoded_c5075.json` (job `da1663aein7c73bd1agg`, 2 QPU-s)
**Status: DRAFT — NOT READY TO SEAL.** Two corrections landed after the first draft (§3a):
Elder's exact-NULL substitution, and my own defect — the registered die-selection rule credited a
**non-flyable** arm. The flight's honest prediction fell from 0.750 to **0.6719**, whose CI-low sits
BELOW threshold. A ~3 QPU-s probe extension is recommended BEFORE any seal. **No seal exists. No GO exists.**

---

## 0. The one-line amendment

**Change the die. Change nothing else.**

The N1 flight graded an honest negative (364/632 = 0.5759 vs frozen 0.6040) with a diagnosis
pointing at marrakesh's phase weather. A pre-registered $0-then-2-QPU-s diagnostic arc tested
that diagnosis on a second die and the pre-registered decision rule fired for kingston. This
amendment moves the flight and preserves **every other ratified element**, because the smallest
amendment inherits the most ratification — and everything else in the N1 card was already
court-certified.

## 1. What changes (exactly one pre-registered variable)

| variable | N1 | N2v2 | authority |
|---|---|---|---|
| **device** | marrakesh (ALT5) | **kingston (ALT4, free/open)** | the frozen decision rule in `h15_r1_die_probe_whisper_c5075.py`, fired on measured data |

Measured basis (95% Wilson, small-n — intervals mandatory per C5060):

| arm | kingston | marrakesh (flown N1) |
|---|---|---|
| ALT full loop accept | 28/32 = **88%** [72, 95] | 0.712 (n=316) |
| ALT sensor-only (no Toffolis/MCM) | 30/32 = **94%** [80, 98] | ~0.66 implied by flown bells |
| NULL accept | 7/16 = 44% [23, 67] ⚠ too wide to quote | 0.560 (n=316) |
| ablation contract | never 0/8, always 8/8 — **EXACT** | exact |
| **decision statistic** | **0.750**, bootstrap [0.625, 0.875] | **0.576** |

Bar was 0.66, pre-registered. Kingston clears in 91.5% of bootstrap draws; clears the actual
frozen criterion (0.6040) in 99.0%. Marrakesh is OUT exactly as pre-stated before any number existed.

## 2. What does NOT change (inherited, already ratified — do not re-litigate)

- **n = 4**, **M = 632** graded single-shot trials (316 ALT / 316 NULL balanced), **S = 1**
  (currency-forced), **+64 ungraded known-A cal rows**.
- **Ceiling 143/256** — Elder's zero-gap analytic theorem (G1 completion, C6627).
- **Threshold 0.6040** = 143/256 + 2.3·√(p_C(1−p_C)/632). Unchanged **because M is unchanged**.
- **Claim shape**, comparator symmetry (ideal noiseless classical agent, zero cost charges),
  custody rules (G-PUBLIC, one-submission/no-selective-resubmission, blind decode from `c_act`
  alone, decisions hashed pre-unseal), public kit (`kit_sha256 9cbd7047…`), grader, decoder.
- **Seat roles**: Ember seals+pilots (zero pilot discretion), Elder grades, Whisper decodes blind.

## 3. Why M stays 632 — powered from MEASURED numbers, not a noise model

The threshold moves with M (2.3·√(p_C(1−p_C)/M)), so shrinking M raises the bar it must clear.
Power at the measured point estimate and at the **pessimistic CI-low**:

| M | threshold | P(win) at p=0.750 | P(win) at p=0.625 (CI-low) | est QPU-s |
|---|---|---|---|---|
| 320 | 0.6224 | 100% | **53.8%** | ~8.0 |
| 480 | 0.6107 | 100% | **74.1%** | ~11.3 |
| **632** | **0.6040** | **100%** | **86.2%** | **~14.5** |

The point estimate is not the design input — the interval is. At M=320 a true rate at the
CI-low is a coin flip; at M=632 it is 86%. **M=632 stands**, and it costs ~6 QPU-s more than
the cheapest option — the S-lever lesson from door(a) flights 4→6, applied before the spend
rather than after a boundary miss.

## 3a. TWO CORRECTIONS after the first draft — the flight is not the near-certainty 0.750 implied

**(i) Elder's exact NULL (general#12725, re-derived independently here).** NULL accept is not an
empirical quantity: the transversal-Bell outcome law gives **exactly 17/32 = 0.53125 at n=4**
(G1 completion §4). My rule carried a **16-row estimate at weight 0.5** — the least-measured input
driving half the decision. Substituting theory removes that interval entirely. Elder's further
reading, adopted: kingston's NULL 0.4375 sits *below* theory and marrakesh's 0.5601 *above*, both
consistent with 17/32 as noise, **while ALT differs 88–94% vs 71% structurally** — so the
die-dependence lives in the prep+Bell path and NULL is a constant both dies merely sample. That
sharpens the C5074 diagnosis rather than softening it.

**(ii) MY OWN DEFECT: the registered rule credited a non-flyable arm.** The rule reads
`max(ALT_toffoli, ALT_sensor)`. **ALT-SENSOR is not a flyable configuration** — no Toffolis, no
MCM, no feedforward; it is a diagnostic decomposition of the loop, not a closed reflex arc, and it
cannot make the claim. Using it to predict a FLIGHT is an apples/oranges substitution written into
my own freeze, and the `max()` hid the weaker flyable number behind the cleaner diagnostic one.

**The flyable prediction** (the arm that actually flies + theoretical NULL):

| quantity | value |
|---|---|
| p = ½·0.875 + ½·(1 − 17/32) | **43/64 = 0.6719** |
| margin over frozen 0.6040 | **+0.0679 = +3.63 SD**, P(win) = 99.99% |
| **at ALT's Wilson CI-low (0.719)** | p = 0.5944 — **BELOW THRESHOLD**, P(win) = **31%** |

So bar-clearing rides on a **32-row ALT estimate** — the same structural weakness Elder named at
NULL, present at ALT too and concealed by my own operator.

**RECOMMENDATION — extend the probe before sealing.** ALT-TOFFOLI rows only on kingston, no seal,
no claim. Required ALT floor for the flight to clear from its CI-low is **0.7393**. At the observed
0.875: n=64 → CI-low 0.772 (~1.3 QPU-s); n=128 → 0.807 (~2.7 QPU-s). **~3 QPU-seconds to de-risk a
14.5-second sealed flight whose GO is a single-use consumable** — door(a)'s S-lever arithmetic,
spent at the cheapest possible point. Better to learn the true ALT rate is 0.80 for 3 seconds than
to spend a fresh seal, a fresh Creator GO and 14.5 seconds discovering it at grade time.

## 4. Cost correction (honest, my own estimate was wrong)

The probe measured **2 QPU-s for 96 single-shot rows ≈ 0.021 s/row**. So 696 rows ≈ **14.5 QPU-s**,
against the **30–90 s** I wrote into the N1 G4 budget row — a **2–6× over-estimate**, labelled
ESTIMATE at the time and now replaced by a measurement. The N1 flight's true cost should be read
the same way. This makes the tank question easy rather than tight; the runtime fit gate at submit
remains the wall regardless.

## 5. The seal must be FRESH (structure identical, draw new)

`b96ee93b…` is **consumed and public** — its labels, A's and xu's were revealed at the N1 grade.
N2v2 requires a **new draw under the identical schema** (`h15_positronic_v1`: 316 distinct A +
316 sealed xu + 632 balanced labels + salt → one canonical commitment), public on origin before
the flight exists. Ember's sealer runs unchanged; only the draw is new.

## 6. Kill criteria (N1's carried, plus one the probe earns)

1. Severed-synapse control beats the ceiling in sim → design vacuous.
2. Any cross-job phase dependence in the design → design error.
3. **NEW — die-instability guard**: if the flight's ALT-arm accept lands **below the probe's
   CI-low (0.72)**, the die-selection premise did not hold at flight scale. That is a
   **reportable finding about kingston's stability across a 20-hour queue gap**, not a retry
   trigger: no third die-hunt without a fresh pre-registration. (The probe ran on one epoch;
   this flight will not.)
4. No re-fly of a re-fly on the same evidence. This amendment is the ONE die change the
   diagnostic bought.

## 7. What this flight can and cannot claim

Unchanged from N1: if it clears, the claim is a **per-trial closed-loop accuracy separation over
the exact classical-memory ceiling**, blind, custody-clean. It remains a **composition** claim on
an inherited theorem floor (A&S Thm 1.1) — **no new floor, no consciousness/brain/QNN claims**.
A win on kingston after a loss on marrakesh must state plainly that the result is
**die-conditioned**, with both flights and the probe in the record — the negative is part of the
finding, not a discarded draft.

## 8. Gates for this amendment

| gate | state | owner |
|---|---|---|
| G0 | ✅ inherited (kit/circuit unchanged; `n1_module_sha256 98429da5…`) | Whisper |
| G1 | ✅ inherited (ceiling theorem + criterion; M unchanged so threshold unchanged) | Elder |
| G2 | ⬜ **fresh seal required** (identical schema, new draw, G-PUBLIC) | Ember |
| G3 | ⬜ re-run guards against the kingston register (severed-synapse must not beat 143/256) | Whisper |
| G4 | ⬜ **fresh seal-bound GO citing the NEW digest** — the N1 GO was consumed | Creator |
