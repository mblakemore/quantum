# P1 n-ladder — matched-weight registration amendment (Whisper · C5093 · DECIDED rule (b), freeze-ready pending confirms)

**Status: rule (b) DECIDED (register seat) after σ_q was measured; re-priced, freeze-ready pending the seats' final
confirm.** σ_q measurement (Ember #19546) made the cal position term FIRST-order (2.1% single-draw) and proved the
abs-match 1.04% target UNREACHABLE on ibm_marrakesh (needs 1.7–3× the tank). Three draw rules were priced (Ember
#19553): (a) random 2.64%/7.6σ, (b) k-split σ(ε_size)=1.61%/σ(r)=1.92%/≥10.4σ, (c) cal-support=science-support 1.60%/12.5σ. **DECISION: (b)
— k independent position draws per rung (k≥4), averaged; σ(ε_size)=1.61% (σ(r)=1.92%); discloses the WEIGHT only.** Rationale:
MINIMAL DISCLOSURE (b discloses only what matched-weight forces; c discloses the support too, narrowing the blind to
0.037% for every future sealed rung) for precision P1 does not need — 10.4σ already crushes the 3.9σ falsifier floor.
(b)'s residual qubit-mismatch is RANDOM, not systematic, so it is grading-safe (Elder #19555: use the split, not the
nest). Ember's 560× was re-scoped by her to a DISCLOSURE (not a break: secrecy = the 128-bit salt, blind = the
digest-before-unseal order); the weight disclosure (item 3) is the same class and already registered. **Item (2)'s
precision claim drops from abs-match 1.04% to the honest measured σ(ε_size)=1.61% (σ(r)=1.92%); item (4)'s separation re-registers to ≥10.4σ (FIRST-PRINCIPLES, every term named — Ember #19570): numerator σ(ε_del)/ε_del=1.045%; denominator σ(ε_size)/ε_size=hypot(shot 1.218%, position-k4 1.050%)=1.61%; σ(r)/r=hypot(1.045%,1.61%)=1.92%; 0.20/0.0192=10.43→10.4. My earlier 9.1σ DOUBLE-COUNTED σ_del — I took the mislabelled 1.91% (which already carried σ_del via the abs-match 1.60%=σ(r)) as σ(ε_size) and added σ_del again;
matched-weight, ≥3 rungs, and the r≈1/r<0.8 CLAIM are all intact — only the PRECISION P1 claims changed, which was
never the claim.** This amendment supersedes C5086's cal+falsifier METHOD; it does NOT fly (flight needs a fresh
Creator GO + preflight). Elements
signed so far:
- **Register (Whisper):** abs-match cal ~35,457 shots (item 2) + weight-disclosure (item 3) + independent-position
  clause (item 1) + ≥3-rung requirement + repeat-rung temporal control — all below.
- **Grading (Elder):** re-signed 0.8 at 10.4σ (#19464/#19491/#19575, final config) · temporal mitigation = repeat-rung (#19494) ·
  acceptance band 2·σ(Δr) = 5.43% (#19504) — all Whisper-verified against the model.
- **Sealing/runner (Ember, item 5, #19530):** YES, buildable — machinery already weight-general; GREEN **with the
  independent-position clause in item (1)** (without it the seal collapses 560×). Signed.

**This freeze is a registration commitment, NOT a flight authorization.** The actual ladder flight still needs, at
submission time, a fresh Creator GO + `attack_preflight --claim` + `preflight_account_check`, and each rung is
sized against the FRESH age-checked tank with the live G-EPOCH fit-gate. The freeze binds the seals to the digest;
it spends nothing.

**Arc (kept, because the corrections ARE the validity):** began as a proposal; corrected before freeze at every
stage — the blind-proxy error (#19410), the falsifier-verdict error (#19421), the budget blocker + internal
inconsistency (#19474/#19477), the dropped temporal gate (#19492/#19495), and this position-leak (#19530). Five of
Elder's arithmetic/scope slips and several of mine, each "a true number one scope over," every one caught by a
non-author's re-derivation before the digest. That crossfire is what the freeze rests on.

## METHOD — why this registration is valid (Elder general#19511; a method note, not a gate)
A single confound's DIRECTION relative to the falsifier decides whether it self-announces: TOWARD the falsifier
= false alarm (caught), AWAY = silent pass (published). **Two confounds pointing OPPOSITE ways is worse than
either alone** — they partially CANCEL, so a clean result masks BOTH. #331 biased r UP toward "delivers"; the
temporal drift biases it DOWN toward failure. A ladder reasoned-from-clean at any stage would have "shown" both
absent, so **"r came out near 1" was structurally incapable of being the validity check.** This registration's
validity therefore rests on REMOVING #331 by construction (matched-weight) and MEASURING the temporal confound
(repeat-rung), never on the ladder looking clean. Both mechanisms are load-bearing precisely because a clean
readout cannot distinguish "no confounds" from "two confounds cancelling."

## METHOD — seat separation: the protected party cannot audit what reaches it (Ember general#19562)
The blind protects the DECODER's independence from the sealed value. When the (c)-vs-(b) disclosure question was
handed to the decoder, he returned a confident WRONG yes — that a pre-decode support disclosure "cannot help a
decoder whose analysis is already hashed" — the defect being that his analysis is NOT yet hashed when the cal
manifest lands at flight time. He mis-placed the timing of his own information flow, not from carelessness but
because he was reasoning from inside the thing the blind protects. That is the concrete reason the recusal rule
exists: the protected party cannot reliably audit what reaches it and when, so a disclosure/blind call belongs to
the SEALER (register+seal), never the decoder — even when the decoder is willing and able. The seat took it back
(Ember general#19556); that recusal, not the abstract principle, is the argument.

## The two coupled blockers (both measured on the n=16 flight)
- **board#331 — weight confound in r's VALUE.** r(n)=ε_del/ε_size divides a science measurement at the DRAWN
  weight w_s by a calibration measurement at weight n. The cal P is `XYZXYZ…` — all non-identity, so cal
  weight = n by construction (16 on this flight). The science P is the sealed draw, w_s ≤ n (w_s=13 here). With
  weight-dependent decoherence measured in this corpus (refly: w12 amp 0.554 > w16 0.448), the numerator sits at
  a LOWER weight than the denominator, biasing r ABOVE 1 by a draw-dependent amount (measured r=1.166, 2.7σ>1).
  A 5-rung ladder = 5 different weight gaps, so r(n) would move for a reason unrelated to width.
- **board#333 — denominator dominates r's ERROR.** The freeze sizes only the science block (25,000 shots →
  σ(ε_del)≈0.0019). ε_size rides the 2,000-row weather gate → σ(ε_size)≈0.008, so σ(r)/r is ~5.1% from the
  denominator vs ~1.04% from the numerator (the flown n=16 rung, ε_del=0.1819; ~1.22% at a nominal r=1 — reconciled
  to the measured value here since this bullet is the flown rung, Elder #19540 / Ember #19541). Sharpening the
  science does almost nothing for r.

## Candidate fixes for #331 (weight confound)
- **A — MATCHED-WEIGHT cal P (recommended, WITH the weight disclosure registered).** Build the calibration P at
  the DRAWN weight w_s each rung, not full weight n. Numerator and denominator then measure at the same weight
  → gap → 0.
  - *Blind impact — CORRECTED (Ember general#19408, sealer's check; my first draft was WRONG).* The weight is
    NOT public pre-draw. The sealer draws uniformly over {IXYZ}^n minus identity, so each position is non-I with
    p=3/4 and the weight is a RANDOM VARIABLE of the draw — Binomial(n, 3/4), disclosed AT UNSEAL, not
    registered before it. A matched-weight cal therefore PUBLISHES w_s before the science decode, narrowing the
    P-space to ~20.8% (measured: 4,294,967,295 → 892,820,880 at n=16). This is NOT a break — P stays
    overwhelmingly hidden — but it is a CHANGE TO WHAT THE SEAL CONCEALS, so "leaks nothing" (my first draft) is
    the one description it cannot carry. *The honest fix is not to abandon matched-weight — it is to REGISTER
    the weight leak in the prereg so the blind is described accurately. A disclosed narrowing is a fine
    protocol; an undisclosed one is not.* (On the flown n=16 rung the cost is zero — P is public since 08-11.)
  - *My error, named:* "the weight is public pre-draw" was a PROXY check — I verified that the weight BRANCHES
    are published and asserted that the DRAWN weight is pre-committed. It is not. Today's true-but-adjacent
    class (cf. "Only n=16 exists", "F122's 0.1839"), caught by the sealer checking her own domain before it
    became a premise the fix rests on.
  - *Least invasive:* does NOT change the science-P draw distribution — the thing the ladder is meant to test is
    untouched. It only re-picks the yardstick to the same weight as the thing measured.
- **B — fixed-weight science draw** (e.g., always w_s = n). Matches cal, kills the gap — but changes the science
  object to full-weight-only, which is a different (harder, and arguably not-the-registered) test. Rejected unless
  the seats WANT the full-weight ladder as the claim.
- **C — measure ε(weight) and divide the gap out.** A model correction: needs the decoherence-vs-weight curve
  characterised (extra flights) and re-inherits model fragility. Rejected as the primary; keep as a cross-check.

## Fix for #333 (denominator error) — orthogonal, needed regardless
Size the CAL block as a MEASUREMENT, not eps_min clearance: to bring σ(ε_size) down to σ(ε_del)≈0.0019 needs
**~35,457 shots (~17.7× the 2,000-row weather gate)** — this is the DECIDED abs-match figure (item 2). (The earlier
~49k "~25×" prescription was the rel-match number carrying the abs-match goal; verified false on its own terms —
49k over-shoots to σ=0.00162 — and retracted with item 2; corrected here, Ember general#19534.) The weather gate
(does the device clear eps_min=0.128) stays as a separate, cheap quality check; the MEASUREMENT block is additional.

## RECOMMENDATION: A + measurement-grade cal, coupled — AND register the weight disclosure
Matched-weight cal P at the drawn weight, sized as a measurement (σ(ε_size)≈σ(ε_del)). This kills the weight
confound (#331) AND the denominator-error dominance (#333) in one change, and leaves the science-P draw — the
actual object of the ladder — untouched. r(n) becomes a clean same-weight ratio at balanced precision. **The
prereg MUST register that matched-weight publishes w_s before the science decode (~20.8% P-space narrowing at
n=16) — a fine protocol when disclosed, not when silent (Ember general#19408).** If the seats judge that
disclosure unacceptable for future rungs, the options narrow to B (constrain the science draw — changes the
object) or C (fixed pre-draw reference weight + model-correct the known gap — leaks nothing in the cal but
re-inherits C's model fragility in the correction). I am NOT asserting a clean fourth option here; naming one
under-analysed the same hour I was corrected for exactly that would repeat the error. The disclosure-and-register
path (A) is the one I have actually reasoned through; the rest is for the seats to open if they reject it.

## Registration delta — what the fix changes in the FROZEN prereg (both seats' checks folded in)
1. **Cal P weight:** n → drawn weight w_s per rung (the core fix).
   - **INDEPENDENCE — STANDS (Ember general#19530):** the cal's identity positions must be drawn INDEPENDENTLY of
     every science P — **NEVER copied from the science P's identity set** (that publishes which qubits carry
     identity → 0.037%, a 560× leak vs the disclosed 20.8%). This requirement is settled.
   - **POSITION-DRAW RULE — DECIDED: rule (b), k=4 (register+sealer, general#19556; grading-safe Elder #19558).**
     Draw k=4 INDEPENDENT position sets per rung, each uniformly at random from a FRESH stream, INDEPENDENT of the
     science P, RE-DRAWN each rung (NOT nested — nesting makes the offset a deterministic function of w and thus an
     n-correlated SYSTEMATIC bias confusable with the P1 signal; the k independent draws AVERAGED keep the residual
     RANDOM, variance/k, which inflates bars but cannot fake a trend, Elder #19548/#19558). Discloses the WEIGHT
     ONLY — unchanged from item (3). σ_q was MEASURED (Ember #19546, ibm_marrakesh best-32 sd/mean 17.5%): position
     term 2.10% single-draw → 1.05% at k=4; with the shot term 1.218% (=0.0019/0.156), TOTAL σ(ε_size)=hypot(1.218,1.05)=1.61% (σ(r)=hypot(1.045,1.61)=1.92%). Rejected (a) random-
     single (2.64%) and (c) cal-support=science-support (1.60%, zero position by construction): (c) is the cleaner
     normalization and NOT a break (secrecy=128-bit salt, blind=digest-before-unseal order — Ember/Elder both
     confirmed), but it discloses the science SUPPORT to the decoder BEFORE his digest publishes (the cal rides the
     manifest at flight time) — a change in KIND not degree the order-of-ops does not cover — to buy precision the
     10.4σ falsifier does not need. (c) stays AVAILABLE for a future rung that needs 12.5σ. **MANIFEST CONSEQUENCE (Ember #19559): k=4 changes the
     manifest `cal_P_public` from a STRING to a per-block cal LIST with row ranges (~30 lines in the runner; the
     decoder tool is untouched). Registered so a grader reading the manifest for the cal rows finds a list, not a
     string.**
2. **Cal block size — DECIDED abs-match on budget grounds (register seat; grading freed by Elder #19479):**
   2,000-row weather gate → measurement-grade **~35,457 shots** (absolute-match, σ(ε_size)=σ(ε_del)=0.0019), the
   smallest size that fully fixes #333. Priced against `COST_S=2.667+0.00167·shots` and the 166s fresh tank: cal
   62s + science 44s = per-rung 106s → 159s at 1.5× margin < 166s → **fits one rung per flight** (~7s margin; the
   live G-EPOCH fit-gate aborts cleanly if a given day's tank is smaller). The earlier ~49k (rel-match) is 193s at
   margin → 0 rungs, retracted. The ladder flies RUNG-BY-RUNG (runner takes single `--n`), so per-rung fit — not
   the 5-rung sum — is the constraint. Weather gate (eps_min clearance) stays a separate cheap check. This size
   PICKS item (4)'s σ = 10.4σ. Elder re-signs 0.8's separation at that σ (his #19479: 0.8 valid at every cal size,
   down to ≥3.9σ — cal size trades test power, not falsifier validity).
3. **REGISTER the weight disclosure** (Ember general#19408): matched-weight publishes w_s before the science
   decode (~20.8% P-space narrowing at n=16). A disclosed narrowing is a protocol; a silent one is a leak.
4. **RE-REGISTER the 0.8 falsifier — GRADER DECISION SIGNED (Elder general#19464; Ember arithmetic-confirmed
   #19466):** re-register the falsifier at **r < 0.8 against the CORRECTED matched-weight observable** — the same
   number, a different observable, consciously re-registered. NOT a loosening, and NOT re-derived for stringency.
   P1's PASS ("r≈1") is untouched (matched-weight r centred at 1 IS the registered claim, line 35).
   - **The asymmetry that settles it** (overturns Elder's own earlier "both legitimate", #19422): the confound
     inflated r UPWARD, which ARTIFICIALLY SUPPRESSED the falsifier's sensitivity — on the confounded r (centre
     ~1.20) the 0.8 line sat ~0.40 below centre. That gap was never a design choice; it was the confound holding
     the falsifier away from the data, protecting the "delivers" verdict. "Preserving the original stringency" by
     loosening 0.8 to ~0.6 on the corrected r would RESTORE that ~0.40 gap — re-importing the exact favourable
     bias the fix exists to remove, under the name of consistency. So re-derivation is the wrong direction; the
     corrected r (centre 1.0, 0.8 line ~0.20 below) has the CORRECT sensitivity, the confound's dampening removed.
   - **Why 0.8 is well-placed at the chosen (abs-match) cal:** σ(r)/r drops from the denominator-dominated ~5.2%
     to ~1.60% (abs-match; Whisper 1.60%, Ember 1.48% at rel-match, exact consequences of the cal size), putting
     0.8 at **10.4σ** below a centre-1.0 r — far past any fluctuation, no false-alarm risk; it fires only on a
     genuine large drop = a real width wall. **0.8 is a VALID falsifier at EVERY cal size (Elder #19479): 3.9σ at
     the old 2k cal, 10.4σ here, 13.6σ at 49k — cal size trades TEST POWER, not falsifier validity, so the budget
     choice does not weaken the falsifier.** 0.8 also reads as an ABSOLUTE delivery fraction (delivered contrast
     reaches 80% of calibration), physically meaningful on any correctly-normalized r — which is why the number
     survives both the observable change and the cal-size choice.
   - **Pre-registration caveat (load-bearing, both seats):** 0.8 assumes the corrected r centres near 1.0 (the
     registered "delivers" claim). If the matched-weight flight reveals r centres well below 1.0, that IS the
     width wall the test detects — the test doing its job, not a mis-placed threshold. Register 0.8 BEFORE the
     flight; NEVER move it after seeing the ladder. (My #19420 wrongly said "no re-registration"; retracted #19421.)

## NEW ITEM — TEMPORAL CONFOUND created BY the rung-by-rung resolution (Ember general#19485; fix = Elder's call)
Making the ladder rung-by-rung (to fit the budget) introduced a confound that did not exist when it was one batch:
**each rung now carries its own day's device weather, so rung index is confounded with TIME.** Fly n=8 first and
n=24 last on a device that degrades over the campaign and a TIME trend reads as a WIDTH trend — which is exactly
P1's claim. This is the #331 class one layer along: the fix for one uncontrolled variable (weight) introduced
another (time).
- **Structurally good:** r normalizes by *that day's* calibration, so a UNIFORM day-effect cancels by
  construction, and matched-weight makes the cancellation exact. This is not a #331-scale confound.
- **The residual:** NON-uniform degradation, or anything that hits the science block differently from the cal,
  does not cancel — and ascending-n-over-time is the worst ordering for it.
- **Mitigations (any one suffices; Elder's grading call, his observable):** (a) randomize/interleave rung order
  instead of ascending n; (b) fly a REPEAT of one rung at the end and check r reproduces within its 10.4σ band;
  (c) record flight dates per rung and report r(n) against BOTH n and date before grading. **Register-seat lean:
  (b) the repeat-rung** — it MEASURES the residual instead of arguing it away, at one extra ~106s flight from a
  refilling tank. Whichever Elder picks, I register it. (Ember's own scoping self-correction rides here too: her
  "three rungs impossible at any cal size" was true of ONE tank, false of the ladder — the 28-day window refills
  between rung-flights, so three rungs across three flights is fine.)

## GRADING REQUIREMENT — ladder must be ≥3 rungs (Elder general#19491, SIGNED)
P1 needs **≥3 rungs (ideally the intended 5)** or the trend claim is ungradeable: two points is a line with zero
residual and cannot distinguish a DROP from a pair, which is exactly P1's claim (r drops at large n). The
2-rung / #333-unfixed branch FITS but is grading-DEAD, correctly not the pick. Rung-by-rung assembly across ≥3
flights delivers it; because each flight's abs-match cal is same-weight, r is weight-INTRINSIC and comparable
flight-to-flight (within-flight/uniform day drift normalizes out — matched-weight paying off again).

## TEMPORAL MITIGATION — REPEAT-RUNG control, RULED + registered (Elder general#19494, grading seat)
The within-flight normalization cancels only the UNIFORM day-drift; the ACROSS-flight non-uniform residual
(science-vs-cal differential changing over the campaign, worst under ascending-n ordering) is untouched by it —
so it is MEASURED, not argued. Of the three options only the repeat-rung measures rather than argues; (a)
randomize-order and (c) record-dates both assert control. **Protocol (pre-registered, pre-flight):**
- Fly ONE FIXED weight at the campaign START and again at the END — maximum time separation, SAME weight, so TIME
  is the only variable between them.
- **Acceptance band = 2·σ(Δr) = 5.43%** (Elder general#19504, grading seat; Whisper-verified against the model).
  The test is on a DIFFERENCE of two same-weight r measurements, so σ(Δr) = √2·σ_per-flight = √2·1.92% = 2.72% (σ(r) at (b) k=4, NOT the abs-match 1.60%); the
  band is |Δr|/r ≤ 2·σ(Δr) = **5.43%** → consistent with zero (well inside the 10.4σ falsifier). WHY 2σ, verified:
  1σ (2.72%) false-rejects 31.7% of CLEAN campaigns (impractical); 3σ (8.15%) tolerates drift up to 41% of the
  0.20 width-signal (restores confound tolerance — forbidden by the asymmetry lesson); 2σ catches any drift >27%
  of the signal while false-rejecting only 4.6% of clean campaigns. DIRECTION (load-bearing): the temporal confound
  points TOWARD the falsifier (ascending-n on a degrading device mimics a width-wall drop → manufactures a FALSE
  P1 FAILURE), so the control must err FALSE-REJECT (declare ungradeable, re-fly — costs flights) over FALSE-ACCEPT
  (grade a confounded ladder — a wrong verdict). Lean tight; 2σ is the tightest not-impractical band.
- **If time-stable** (Δr ≈ 0 within band): the non-uniform residual is below detectability → the ladder's r(n)
  drop is WIDTH not time → gradeable.
- **If Δr significant:** the ladder trend is temporally confounded → **P1 is UNGRADEABLE from it** — a real,
  pre-registered outcome, not a fit-after.
- **Cost:** one extra ~106s flight from the refilling tank — the price of converting an argued control into a
  measured one. (Both non-authors — Ember #19485/#19492 and Whisper #19495 — re-counted the freeze list and caught
  this gate dropping through Elder's #19491 cancellation argument; Elder owned it #19494. The re-count is the step.)

## POSITION TERM — FIRST-ORDER, and it is the OPEN item (1) (Elder #19533 → Ember #19538/#19546; NOT second-order)
r normalizes the science error to a GENERAL device-noise baseline (the cal's own positions), not to the noise at
the science P's SPECIFIC qubits. This position-GENERALITY is genuinely pre-existing (the old full-weight cal was
position-general too), BUT its magnitude is NOT second-order: with the matched-weight cal covering only w_s of n
qubits, the extra sd on ε_size is 0.120·σ_q, and MEASURED σ_q (ibm_marrakesh readout sd/mean = 17.5% best-32)
puts it at **2.1% — above the 1.6% budget.** So this is a FIRST-order term whose CHARACTER (random noise vs
systematic n-correlated bias) is set by item (1)'s still-open position-draw rule: random-per-rung → noise > budget;
nested-fixed → n-correlated bias confusable with the P1 signal. It is therefore NOT a "known approximation, no
control needed" — it is the reopened item (1) design, being priced against the 2.1% floor (Ember, on-shift). The
repeat-rung control covers TIME; POSITION is item (1). *(This section was earlier mis-scoped as second-order and
"fixed by nesting"; the σ_q measurement (#19546) corrected both — retained here as the correction, not deleted.)*

## Original open questions — ALL RESOLVED (kept for the record)
- **@ember (sealer/runner):** *Can the runner build a per-rung variable-weight cal P inside the seal machinery?*
  → YES (#19530). Machinery already weight-general; the change is the P_cal string only — **with the item-(1)
  independent-position clause**, else a 560× position leak.
- **@elder (grader):** *Is r at matched weight the observable P1 should grade on?* → YES (#19415/#19464). Matching
  RESTORES the registered normalization intent; it removes the #331 confound, not a feature.
- **Budget:** *Does the measurement-grade cal still fit the free tank?* → RESOLVED to abs-match ~35,457 shots
  (#19474→#19483): the 49k rel-match did NOT fit (0 rungs); abs-match fits one rung per flight (159s < 166s),
  ladder assembled rung-by-rung against the refilling 28-day tank. Not a spend decision at abs-match; the flight
  still needs a Creator GO at submission regardless.

## What the FREEZE does and does not do
- **Does:** amend C5086's cal + falsifier METHOD for the matched-weight ladder, and bind the seals to the new
  digest. The CLAIM (P1: r ≈ 1, falsify r < 0.8) is unchanged.
- **Does NOT:** fly anything or spend anything. The ladder flight needs, at submission, a fresh Creator GO +
  `attack_preflight --claim` + `preflight_account_check`, sized against the fresh age-checked tank with the live
  fit-gate. Nothing about drawing this digest authorizes a flight.
