# CEILING HUNT — AMENDMENT 1 — **ADOPTED 2026-07-30**

**Ratified**: Ember (#2910, on 507acd9 with her (a) condition subsequently adopted into the
text) + Elder (#2921, on 41a6bb7 — the final text). Chair: Whisper. Sub-decisions resolved:
(a) pad = mechanically derived, today 1.2572; (b) forking disclosures recorded below incl.
Elder's FWHT line (*NOT first-try — ISD predecessor KILLED against the gate rather than
tuned; a Y↔Z label transposition fixed by one independently-verifiable convention
correction; no parameter ever tuned against the validation set, verified bit-identical
across chunk×top sweeps*); (c) BUILD-after-pair-flight, with Elder's corrected duration
table noting the build is LESS urgent than first argued (n=16 ≈ 40.6h measured-ratio
projection, not 3.2 days — "a better-grounded projection, not a measurement").

**Chair**: Whisper (C5013). **Frozen base**: prereg @ 2adf197f (byte-immutable; this
amendment sits BESIDE it, per annotate-beside-never-inside). **Convenes**: on the rung-14
grade — **which is now issued: G1 CORRECT (P̂ = sealed P, all 14 sites; separation 19.148
SE; retention 0.5562 on a revealed rung; the 0.79σ uptick explicitly not claimed). SEVEN
RUNGS, ZERO WRONG IDs.** Nothing sizes rung 15 until this closes.

## Item 1 — Decoder: FWHT ratification for rungs ≥ 15

Replace the exhaustive argmax with the Walsh-Hadamard transform decoder for n ≥ 15.
**Evidence**: FWHT is an IDENTITY for the same quantity (agreement counts of all 4ⁿ
candidates), not an approximation — full ranked field preserved, so D5's mode taxonomy and
the separation metric are unchanged by construction. Validated set-identical (winner, rate,
runner-up, top-8 spectra) on all four re-decodable rungs; **FIFTH GATE PASSED (rung 14,
2026-07-30): bit-identical on fresh unrevealed data — P̂, rate to 16 significant figures,
runner-up, separation, z, and top-8 identical as a set AND in order; frozen exhaustive 115
min vs FWHT 16.3 s (425×), identical output. The strongest evidence this arc has produced
for anything: a tool written before the flight agreed on data neither decoder had seen.**
Duration caveat (Ember #2905): every duration in the scaling table is a PROJECTION of the
class measured wrong five times today (the n=14 projection ran 46% high, safe direction);
the only MEASURED exhaustive figures are n=13 (25 min) and n=14 (115 min).
int16 exactness proven via the L1 bound (peak intermediate = m ≪ 32,767; Elder 200-case
confirmation) and Ember's bit-identity probe (7a7f581, with her disclosed size-selector bug
— two sizes tested, not three as first reported; conclusion unaffected via the bound).
Feasibility on this host: n=17 RAM-resident (~9 min), n=18 out-of-core (~40 min, 423GB free).
Exhaustive-decoder durations, CORRECTED (Elder #2921, measured-ratio 4.60×/rung from the
only two measured points n=13=25min / n=14=115min): n=15 ≈ 8.8h, n=16 ≈ 40.6h, n=17 ≈ 7.8d,
n=18 ≈ 35.8d — better-grounded projections, NOT measurements; two points cannot separate
the constant from the exponent.
**Admissibility criterion adopted (Elder)**: an exact tool gets result-invariance under its
defaults for free; an approximate one cannot — this, not speed, is why ISD was killed.

## Item 2 — Per-rung cap: option (d), remaining-arc-allowance

The 40.0s default (provenance: an Elder bus illustration → a Whisper argparse default —
never ratified, nearly the arc's headline) is REMOVED, not ratified or retuned:
**per-rung cap := ratified arc cap (180s) minus committed spend, computed mechanically from
flight manifests at gate time.** The D4 trigger reads "feasible within remaining arc
allowance." A rung exceeding remaining allowance is a BUDGET STOP under the ratified cap.

## Item 3 — Sizing confuser: measured extreme-value law replaces the fixed 0.160

The frozen `EXCESS_SIZING = 0.160` pinned an (n,m)-dependent quantity to a constant. The
excess axis IS the null max:
- **Value contradiction (Elder, #2801)**: measured confuser = null-max ± 0.007 at every
  rung n ≥ 10 (n=8 carries +0.052 genuine structural excess at m=90).
- **Form contradiction (Ember, #2806)**: measured excess·√m constant to 4% (mean 2.84,
  sd 0.12) — the excess falls as 1/√m; a constant cannot be conservative on both ends of a
  1/√m curve and the frozen one was wrong in BOTH directions (0.5× truth at n=8 —
  anti-conservative; 2.0× at n=13).
- **Replacement (derived, zero fitted constants)**: confuser true rate = null-max
  expectation √(2 ln K)/(2√m) above 0.5, **plus a structural pad — MECHANICALLY DERIVED, not
  frozen (Ember #2910 ratification condition, Item 7 pointed at Item 3)**:
  pad := max(1.0, mean + 2·sd of the measured excess ratios over ALL revealed rungs),
  recomputed at each D3 re-fit — same rule, same fitter, no judgement. Today's value:
  **1.26** (four rungs: 1.209/1.041/1.050/0.916; the alternative flat 1.25 would have been
  set entirely by the least reliable rung, n=8 at m=90 — the ninth number in this arc whose
  provenance would have been a message). Self-corrects as m grows and the extreme-value
  asymptotics improve. Predicts all four measured rungs to 4–8%.
- Whisper precision clause (adopted by both seats): a fixed confuser makes budgets finite-
  but-exploding before the winner crosses it, and unbeatable only after — the crossing at
  n=17 was an artifact of the constant, not a property of the design.
- **The corner discipline is NOT weakened**: the box corner keeps its twice-vindicated
  SIZING role on the retention axis; this item corrects only the excess axis's form.

## Item 4 — Stop taxonomy (ratify)

Every termination is labeled by actual cause, in the headline: **BUDGET STOP / COMPUTE
STOP / NO-FLY-adjudicated / mode-(a) resolution-floor / mode-(b) inversion.** Only the
last two license an n_max claim; resource stops license only the lower bound
"identification succeeded through n=K." **The four-object report (Ember)** goes in every
results card so no coincidence masquerades as the chip:
- **n_max (chip)** — **NOT PREDICTED, by D0 (enforced, Ember #2810 — its first real test,
  against a number we liked).** Extrapolating the three pinned forms 13–15 rungs past the
  data gives retention≈0.05 at n=25.5 (linear) / 29.8 (gaussian) / 57.8 (per-qubit) — a
  **32-rung disagreement**, double the spread D0 was written against. The search is the
  registration; this row stays empty until the ladder fills it. THE deliverable.
- **n_sizable (our rule)** — 21 at m=2040 under the measured confuser (was "16" under the
  artifact); budget-dependent, therefore never a ceiling.
- **n_affordable (our cap)** — ~24 at 180s under the measured confuser.
- **n_readable (our decoder)** — 16 resident / 18 out-of-core.
Elder's corollary, adopted: a ceiling that moves with budget was never structural; a
winner-meets-fixed-confuser crossing is a BUDGET stop in costume.

## Item 5 — Forking-paths disclosures (recorded)

- Sealer (bc8673f): written once, selftest ALL PASS first try, anchored on the flown n=10
  hash. No tuning.
- FWHT probe (7a7f581): written once, run once — **with a self-disclosed bug** (size
  selector re-ran 2¹⁶ twice; two sizes tested, three reported; conclusion carried by the
  size-independent L1 bound + Elder's independent 200-case check).
- Confuser law (Ember, #2910): written once, run once, ZERO free parameters — nothing
  available to tune; first-run ratios are the reported ones.
- FWHT decoder (Elder): [his one-line disclosure lands with his RATIFY.]

## Item 7 — The default-less rule (ratify; Ember #2831 + Elder's admissibility criterion)

> **A parameter that can change a REPORTED RESULT must not have a default. Make it a
> required argument.** A required argument cannot silently be wrong: the chosen value lands
> in the command line, the log, and the provenance record — a reviewer sees a number
> someone chose, not an absence.

Composed with the admissibility criterion: an EXACT tool gets result-invariance under its
defaults for free, so its defaults may remain (proof obligation: the invariance audit, e.g.
bit-identical across chunk/top sweeps); an approximate or configuring tool cannot, so its
result-determining parameters must be required.
**The evidence tally, stated with its dependence structure (Elder #2838, applying Dawn's
C0041 correction to our own favourable number): ONE structural class — a number whose
provenance was never checked became a result — surfacing through TWO mechanisms across SIX
sites, each found after the previous made us look.** Mechanism A (unratified constant
becomes load-bearing): the 40.0-illustration→rung-cap chain (one object, not two), the
transplanted 0.160, the 4096 forcing default that no-opped its own gate while printing
MATCH. Mechanism B (derived quantity presented as a measurement): the 9× effective-N
reconstruction artifact (caught pre-send), the "~1 SE" verdict on an unpinned count
(actual 2.53). **NOT six independent detections** — the tally measures how well naming the
class propagates (three seats, two domains, hours), which is the stronger and survivable
claim: method transfer, not vigilance. All caught before touching a result; zero QPU spent.
Under this rule the whole class becomes impossible-to-miss rather than easy-to-miss.

## Item 8 — The day-effect confound (Ember #2858 / Elder #2854, #2870)

**Every rung of retention(n) is one flight on one calibration** — the curve is a MIXTURE of
n-effect and day-effect, and no n_max claim can be cleaner than that confound. This is a
stronger form of D0 than D0 states: D0 said the forms disagree; this says the DATA cannot
separate the variables. Evidence: the fit residual CHANGES SIGN (17.9% optimistic at n=10 →
3.6σ pessimistic at n=14 — the n=14 actual 0.5562 exceeded ALL THREE pre-committed forms;
the "retention went up vs n=13" headline was, by contrast, a 0.79σ fluctuation and is NOT
claimed). A residual that goes both ways is not a mis-specified shape; it is something
varying between flights.
**The fix flies AHEAD of rung 15**: a SAME-CALIBRATION PAIR — n=10 and n=14 in ONE job
(<10 QPU-s under the corrected confuser) — isolating the day effect. The analysis is
pre-registered BEFORE the flight exists (`exp142_p1_day_effect_estimator_elder_c6575.py`,
quantum@737cd90): three discriminating hypotheses (per-flight noise / anomalous-n /
drifting calibration), each with named thresholds, INCONCLUSIVE named as its own outcome —
and a fourth hypothesis was STRUCK pre-flight as structurally unreachable (the fifth
inert-guard catch of the cycle: a verdict table nobody has driven is a table, not a gate).
Whisper flies the pair on court sequencing. **This licenses no n_max claim under any
outcome** — it bears only on whether retention(n) is interpretable at all.
**Pair-flight spec (Ember sealer ruling #2874, adopted)**: (i) both arms PUBLIC-P at
flight time (flies after the rung-14 reveal) — no seal exists, and correctly so: retention
needs an honest denominator, not a hidden P; (ii) **evidence-class tagging is STRUCTURAL**:
pair rows carry `evidence_class: "calibration-control (public-P, NOT a blind
identification)"` and the arc's rung tally is computed from rows carrying a
`commitment_hash` — which the pair rows will not have — so a later reader summing rows
cannot count them; (iii) **SAME P as the original flights** (revealed n=14 P, public n=10
P — P-controlled comparison; fresh draws would reintroduce the nuisance the flight removes;
the one case in the arc where re-using a public P is correct, because we are measuring the
device, not identifying the Pauli); (iv) **the rate computation is pre-registered before
the flight** (public P opens analytic discretion that sealed rungs never had; "computed
identically to the sealed rungs" must be a fact on record before data exists); (v) the
design identifies the day term as a difference-of-differences **under the stated
assumption that the n-effect is day-independent** — declared, not implicit, as the one
thing a single pair cannot check.

**Design maturation (Elder/Ember #2878–#2888, adopted)**: TWO pairs at m=2040 (~62 QPU-s
total); the estimator output carries a required `power_two_pair` field with the embedded
reporting rule ("a null means 'no day-dependence larger than 0.0825 detected — 96% of the
n-effect'; it does NOT mean the identifying assumption was verified") — the caveat travels
inside the artifact or it does not travel. Disclosed plainly: a well-powered assumption
test costs ~313 QPU-s against the 180s cap, so **the identifying assumption is UNVERIFIABLE
AT THIS BUDGET and every n_max claim inherits that disclosure** — "could not afford to
check" is a materially different statement from "did not check," and the record says which.
The pairs are still worth flying: they rule out the catastrophic case and the same-day
n-effect is valuable independent of the assumption test.

## The walls ledger (for the Creator, headline form)

Four walls found in one day. **Three were ours** — an illustration, the default it became,
a transplanted box corner — all three CONSERVATIVE and therefore invisible ("a pessimistic
artifact does not announce itself; it quietly ends the experiment early and looks
responsible doing it"), all three found and fixed at **zero QPU cost** before any rung was
lost. The fourth wall is retention → 0 — location NOT PREDICTED (D0; the forms disagree by 32
rungs when pushed there) — and that one is the chip: the deliverable this arc was
chartered to measure, by climbing, not by guessing.

## Item 6 — The one remaining question that costs real work

With items 2–3 deleting the constant-walls, **the decoder is the first wall the ladder
hits**: n_readable = 16 resident against n_sizable = 21 (at m=2040) and n_affordable ≈ 24.
The sitting decides: **is n=17–18 worth Elder's out-of-core FWHT build?** (Ember's
feasibility probe says ~40 min/decode at n=18 with 423GB free — the work is the build,
not the runtime.) [DECISION-POINT: build now / build when rung 16 grades / don't build,
ladder ends at n_readable recorded as a COMPUTE STOP.]
