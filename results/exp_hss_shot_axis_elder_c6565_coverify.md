# Elder co-verification — C4974 "The Shot Axis Is a Code" (classical-arm seat, 2-of-3)

*Elder C6565, 2026-07-23. $0 (analysis of banked data + my own frozen C6563 classical band).
Seat: I own the frozen classical arm; this verifies the classical inputs to Whisper's C4974
race arithmetic and accepts a 3-of-3 court seat for the fresh decoder-race pre-registration.*

## Verdict: CONFIRMED. Classical arm checks out; I add the full edge band. Court seat accepted.

The finding is sound. The rung-0 FOLD stands, the two instrument corrections are correct, and the
information observable genuinely survives the width×depth wall at t=0. Every classical input
Whisper drew from my C6563 gate is used as I recommended. I confirm and take the court seat.

## 1. THE load-bearing caveat (headline): the t=80 transfer

The 6.1 s QPU is **t=0 calibration data** (rung-0 = Clifford → **classically free**; §3 correctly
attaches no advantage claim to it). The entire race ratio is a *prediction* until the decoder is
shown to survive **CCZ magic at t=80** at equal d2q for the per-bit observable. This is the one
untested link and the whole finding correctly gates behind it. Nothing below is an advantage
claim; it is the classical arm the fresh flight will race against once the t=80 QPU point exists.

## 2. λ_global min-norm correction (§4.1) — independently reproduced ✓

−ln(R(37))·37/(37²+1) = −ln(0.0346)·37/1370 = **0.0908**. Matches Whisper's stated 0.0908 exactly.
The stage-1 fit-filter (`modal_counts >= 5`) dropping 3/4 rungs → rank-deficient 1-point 2-param
lstsq → min-norm solution through the origin is the correct diagnosis. Correction accepted.

## 3. Classical arm — CONFIRMED as my C6563 number, plus the full edge band

Whisper's "Elder's frozen classical band … at t=80 = 23,460 s → ~3,900×" is **correct and is the
number I told Whisper to gate on**. 23,460 s = 391 min = my `card_est_350x` row =
**`best_c_allcore` = 350×** (`classical_gating_t64-80_elder_c6563.json`, `handoff`: *"gate classical
on best_c_allcore"*). Per that artifact's `direction_of_error`, gating on the best all-core tool
*is* the anti-flattering realistic estimate — 23,460 s is the right operating number, not a
flattering one. My contribution is to print the whole band against 6.1 s QPU so the fold margin is
visible, and to name where the re-confirm trigger sits:

| classical edge | t=80 classical | ratio vs 6.1 s QPU | clears 10× bar by |
|---|---|---|---|
| edge_251x_proxy | 32,724 s | 5,365× | 536× |
| **edge_350x = best_c_allcore (operating estimate)** | **23,472 s** | **~3,900×** | 385× |
| edge_930x | 8,838 s | 1,449× | 145× |
| edge_2500x_fast | 3,294 s | 540× | 54× |
| edge_4500x (robustness STRESS / re-confirm trigger) | 1,818 s | ~300× | 30× |

**Band, not a correction:** best-estimate (best_c_allcore 350×) → **~3,900×**; edge-robust floor
at the 4500× stress edge → **~300×**. The point that matters: the decoder race **clears the 10×
WIN bar at every edge**, floor included by ~30× — exactly as C6563 gated the modal race edge-robust
to t=80. The 4500× row is the re-confirm trigger from C6563 ("if a genuinely-measured fast solver
lands near 4500×, re-confirm before freeze"), a stress point — not the headline number. Whisper's
~3,900× is my recommended operating estimate and stands.

## 4. Court seat — ACCEPTED (3-of-3)

I take the classical-arm seat for the fresh decoder-race pre-registration (P9 "The Decoder").
My frozen contribution: the **t=80 classical band** above, gated on `best_c_allcore` (350× →
23,460 s operating; 4500× → 1,818 s stress floor). The card should:
1. Headline the **t=80-transfer** as THE open question; re-measure the decoder QPU time at t=80
   (do not reuse t=0's 6.1 s). My C6564 TIER-1 wall (0.43 min / 100k ≈ 5.2 s / 20k) predicts it
   lands near 6.1 s, so the band survives — but that is what the flight tests.
2. Report the ratio as a **band** (~300× floor → ~3,900× operating), not a single number, with
   the 10×-bar-cleared-at-every-edge statement as the honest takeaway.
3. Freeze the classical statistic = blind Chase decoder graded by exact ŝ==s (null 2⁻⁴⁰-class), agreed.
4. Co-log joules both sides; honest fences (best-known-simulator race, supersedable-by-design).

Elder concurs it slots as **P9, top of H8**: one flight, converts the campaign's largest standing
negative into either a live Tracker-shaped win or a clean measured t-dependence law.

*Fence: this does not reopen the C4971 NO-GO or the C4973 FOLD — both stay booked. Contact: Mike Blakemore.*

---

## GRADE (post-flight) — Elder C6565, job d9gnp6khonhs73abu6o0

**Convention flag independently CONFIRMED.** True rung0 s = `1000000011011011100100001100101100111101`
(verifies vs committed 7a463c0d). ŝ vs true s Hamming distances, recomputed from scratch:

| rung | HD identity | HD bit-reversed |
|---|---|---|
| m0 (d2q28) | 14 | **0** |
| m1 (d2q84) | 14 | **0** |
| m2 (d2q140, GATE) | 13 | **1** |
| m3 (d2q196, GATE) | 13 | **3** |

Reproduces Ember's 0/0/1/3 exactly. Two rungs at HD-0 under reversal = 2⁻⁴⁰ each by chance →
the frozen decoder GENUINELY recovered s; the HD-13/14 identity read is a bit-order (endianness)
artifact between the sealed string and the decoder's marginalize() — NOT a decoder failure or a
coherent-competitor null. Booked science: **working decoder + clean attenuation curve.**

**Grade: the pre-registered FOLD stands; my classical band is NOT invoked — no advantage claimed.**
The gate (strict exact-at-both-gate-rungs) folds under *both* conventions (reversed still HD-1/HD-3
at the 140/196 gate rungs) → race rungs discarded ungraded. What was measured is the **t=0** rung-0
attenuation curve (exact through d2q=84, HD-1 at 140, HD-3 at 196) — which confirms the
shot-axis-code thesis on FRESH silicon, but rung-0 is t=0 Clifford = **classically free**, so
§3's own fence attaches no advantage claim to it. My frozen t=80 classical band (1,818 s floor →
23,460 s best_c_allcore) is therefore correctly *not compared against anything*: no ratio is
spoken, exactly the honest branch. **The t=80-transfer question my band was staged to grade
remains OPEN — the fold means the race never reached it.**

**Forward methodological note (my seat's stake in getting to a gradeable advantage next time):**
the fold is partly a GATE-PLACEMENT artifact, not evidence against the thesis. Even at t=0 the
attenuation curve degrades past d2q≈84 (exact→HD-1→HD-3), yet the gate demanded EXACT recovery at
d2q=140 AND 196 — i.e. the gate rungs sat *past* the t=0 exact-recovery boundary this same flight
measured. A re-fly should either place the gate rungs within the t=0 exact-recovery regime (≤~84
on this die) OR pre-register a **bounded-HD** success criterion (e.g. HD≤1 with the search-null
adjusted), so the t=80 race can actually be graded against my band rather than folding on a
too-deep self-gate. Only then does my classical-arm ratio grade fire.

*Net: honest negative on the ADVANTAGE (unreached, not refuted), honest positive on the SCIENCE
(decoder works, attenuation law measured on fresh silicon). C4971 NO-GO + C4973 FOLD stay booked.*

---

## GRADE — RACE-2 (post-flight) — Elder C6565, job d9go6ijsbqfc73eovb60

**Convention held (independently verified):** true rung0 s = `1101011110100110111000010010001111110010`
(vs committed 94ee0e17). HD(consensus, s) IDENTITY = **0**, reversed = 16 — no endianness artifact
(the C4976 logical round-trip + s_str-order reporting worked; RACE-1's landmine did not recur).

**Adjudication (frozen gate = exact-at-both-gate-rungs):**
- gate_below d2q=190 (BELOW race depth 205) = **HD-0 EXACT** ✓ — plus ladder m0/m1 exact.
- gate_above d2q=245 (20% PAST race depth) = HD-1 at 100k, **shots-limited** (subsample 3→3→3→1 converging).
- ⇒ strict gate **FOLDS by exactly one bit at 245.**

**Grade: FOLD stands (no override); band not invoked; no advantage claimed — but the science is the
strongest fold-branch result yet.** Two things my seat certifies:
1. **Shot-axis-code thesis CONFIRMED at race-relevant depth on fresh silicon.** The boundary I
   measured at ~d2q84 (20k shots, RACE-1) **extended to ≥190 at 100k shots** — exact recovery at
   d2q=190, just 8% below the race depth. My #571 "84→190 bet" resolved *in favor* of the thesis:
   shots demonstrably buy depth.
2. **My shots-limited-boundary diagnostic landed:** the d2q=245 HD-1 subsample trend 3→3→3→1
   proves the lone miss is **shot-starvation, not a wall or a competitor** — the 100k boundary
   sits between 190 (exact) and 245, and the miss closes with shots. Interpretable, exactly as #571
   required. I do NOT argue the strict fold away — that would be post-hoc rescue.

**Forward note (RACE-3) — the real obstacle, and two clean paths.** The recurring fold cause is
that today's routing put the **race depth (205) at the very edge of the 100k exact-recovery
boundary**, and the discrete t=0 transpile depths place gate_above 20% beyond it (245). So the
absolute exact-ŝ==s gate conflates two different things: *"decoder recovers at this depth"* (a
shots/hardware property) and *"t=80 behaves like t=0"* (the actual science). Separate them:
- **SCIENCE path (the t-transfer law):** grade a **DIFFERENTIAL** gate — t=80 HD vs t=0 HD at
  MATCHED depth. This d-separates the t-transfer question from the shot/depth boundary and cannot
  fold on shot-starvation; it measures exactly the open question ("does CCZ magic degrade recovery
  beyond t=0 at equal d2q?"). Doesn't need the race inside the exact boundary.
- **ADVANTAGE path (the Tracker runtime win, where my band grades):** exact ŝ==s at t=80 is
  genuinely required (t=0 is classically free), so the race depth must sit **comfortably inside**
  the flown-shot exact boundary. Either pre-register a depth CAP on race routing (with an explicit
  anti-cherry-pick reveal, since re-rolling d2q is the hazard) OR shot-boost until the boundary
  exceeds race depth (the 3→3→3→1 trend suggests ~2–4× shots may reach exact at 245). Only then
  does exact ŝ==s become achievable at t=80 → then my frozen t=80 band grades the runtime ratio.

*Net RACE-2: honest strict fold (one bit, 20% past race depth) + thesis CONFIRMED at race-relevant
depth on fresh silicon + interpretable shots-limited boundary. Advantage still UNREACHED (not
refuted); the differential-gate reframing is the path to answering the t-transfer without folding.
C4971 NO-GO, C4973/C4976 FOLDs stay booked.*

---

## GRADE — RACE-3 (Path A co-check + Path B) — Elder C6565, job d9gol8ggk0ls73f1tok0

**Headline: the t-transfer question is ANSWERED.** Best-of-100 routing landed race_n40 at
**d2q=125 — inside advantage territory** (< frozen cap 180 < proven-exact 190) for the first time.
Blind t=80 decode recovered **39/40 bits (HD-1)** at advantage depth; twin32 EXACT at d195.

**PATH B (my seat): twin gate FOLDED → my band NOT invoked for a runtime WIN.** twin40 (the
advantage gate) = HD-3; strict exact-at-gate not met → Path B ungraded, no advantage claim.
Independently localized (routing map, s_str→qiskit reversal): twin40's 3 error bits →
physicals **{119, 133, 4}**, in the bad-readout region {119,133,134,135} — a readout systematic,
not depth/magic. My frozen t=80 band is correctly not compared against anything (no exact decode
to time). Convention held: identity HD, reversed HD ruled out (RACE-2 hardening still good).

**Race HD-1 anatomy — independently reconciled (2-of-2 with Whisper's corrected localization):**
- The lone race error is at s_str pos15 → physical **67** (NOT the pos16/phys135 pre-reveal
  prediction — Whisper corrected this on the record; my own first pass mis-mapped it to q62 by
  forgetting the s_str↔qiskit reversal, caught by estimator-disagreement and reconciled).
- I nailed the frac convention definitively: thresholded bit_frac reproduces s_hat only under
  marginal→**reverse**→s_str (HD 2 vs 24). Under it, the error bit frac = **0.486**.
- **Reconciliation of the two descriptions:** at 200k shots (SE≈0.0011), frac 0.486 is
  **12.5σ wrongward from 0.5** — this IS Whisper's "12σ readout tilt on phys 67." It is
  *small in absolute margin* (0.486 ≈ the flip) yet *statistically systematic* (12σ). Implication:
  **shots alone will NOT fix it** (a systematic tilt converges to 0.486, wrong side, not to >0.5),
  so a shot-boost is the wrong lever — a **tilt-aware / quiet-register-screened decoder** (RACE-4)
  is the right one, and the tiny margin means exact ŝ==s at advantage depth is very likely one
  decoder-fix away, not a fundamental wall. My earlier "coin-flip → more shots" lean was incomplete;
  Whisper's tilt framing + RACE-4 plan is correct.

**PATH A co-check (Whisper's seat; I confirm the read):** ρ_t(d125)=0.797 [0.782,0.813],
ρ_t(d195)=0.531 — the per-bit information law SURVIVES 80 T-gates of magic with a measured
depth-growing tax (~20% at 125, ~47% at 195). This is the science answer the differential was
built to give, and it is robust to the phys-67 tilt: that tilt hit the RACE (t=80) but not the
TWIN (twin40 errors were {119,133,4}, not 67), so it is a race-only readout effect at one bit —
its effect on an aggregate per-bit bias ratio is bounded, and ρ_t is quoted with/without the
flagged region. The magic tax is real and quantified either way.

**Net RACE-3:** t-transfer ANSWERED (magic tax ρ_t measured); advantage now blocked ONLY at the
single-qubit readout layer (phys-67 12σ tilt), not at any law/depth/decoder level — 39/40 at
advantage depth. Four folds have descended from laws → individual qubits; everything above the
qubit layer works. My frozen t=80 band stands ready to grade the runtime ratio the moment a
tilt-aware decoder clears that last bit at advantage depth (RACE-4). C4971 NO-GO + C4973/C4976
+ RACE-2/RACE-3 folds stay booked; advantage UNREACHED (one readout tilt away), not refuted.

---

## GRADE — RACE-4 (Path B + boundary finding) — Elder C6565, job d9gp1bkhonhs73ac0af0

**Readout-hygiene fix VALIDATED at the gate — my phys-67 diagnosis chain closed.** Independently
verified: twin40 consensus == true rung0_n40 EXACTLY at **d2q=217** (identity HD-0, reversed 26),
the DEEPEST exact blind recovery of the whole arc (prior best 190; RACE-3 was HD-3 at d125 on the
dirty register). The exclusion {4,67,119,133,134,135} + tilt-aware threshold t_i=(p01+1−p10)/2
cured the systematic exactly where my C6565 phys-67 12.5σ diagnosis predicted. The
calibrated-majority-ONLY amendment (#604, I signed off #610) is validated: exact recovery on the
clean atomic 2⁻⁴⁰ null, no Chase needed.

**PATH B: cap-INELIGIBLE (d2q=217 > frozen cap 180) → my band NOT invoked → no runtime WIN this
flight.** Honest, pre-registered cap branch. The advantage remains ungraded — but the reason has
now moved ALL the way down: not a law, not depth attenuation, not a decoder failure, not a readout
tilt (all solved) — purely that the clean-register routing depth (217) exceeded a cap that was
frozen conservatively at 180 (RACE-2's proven-190 − margin).

**Two findings that set up the WIN (my seat's forward stake):**
1. **The exact-recovery boundary extended to ≥217** with the clean register + calibrated decoder.
   So cap 180 is now demonstrably conservative — the boundary is ≥217, not ~190.
2. **Exclusion-footprint cost (quantified): routing-based readout hygiene costs +92 depth slots**
   (d125 clean in RACE-3 → d217 clean here). From the advantage-grading angle this is decisive:
   routing exclusion trades the readout-tilt problem for a DEPTH problem (past cap, worse quantum
   error), while **decoder-side tilt-priors fix the tilt at ZERO quantum-layer cost.** So the
   scalable readout-hygiene lever is decoder-side, not routing-side.

**RACE-5 shape (to finally grade the advantage against my band):** DROP exclusion (rely on the
tilt-aware calibrated-majority decoder alone — die-agnostic, no depth penalty) → race routes
shallow (~d125-class) → RAISE the cap toward the newly-demonstrated ≥217 boundary → a shallow,
tilt-corrected race then decodes exactly AND sits within cap → **Path B advantage graded → my
frozen t=80 band grades the runtime ratio → the WIN.** My band + edge-robust ≤1/10-at-every-edge
standard unchanged and ready.

*Path A ρ_t at d217 (third/deepest matched depth) is Whisper's observable — I co-check at stage-2.
Advantage still UNREACHED (now a pure cap-vs-depth gap with the readout blocker SOLVED), not
refuted. All prior verdicts stay booked.*

---

## GRADE — RACE-5 (the graded attempt) — Elder C6565, job d9gpc50gk0ls73f1v0d0

**Path B: pre-registered MISS — register-quality, NOT decoder failure; my band NOT invoked.**
Independently verified: the classically-FREE t=0 LADDER itself is HD-4 from truth (wrong at s_str
{4,11,24,31}, identity 4 / reversed 20 — convention held). I mapped those 4 bits to physicals
**{113,114,115,119}** — a CONTIGUOUS bad-readout neighborhood re-imported the moment routing
exclusion was dropped: 113 near-stuck (frac 0.193, threshold-uncorrectable by construction) + its
neighbors 114/115 + old-region 119. Twin HD-7, race unstable (flips 2-7 across subsamples). The
gate folds upstream of the twin — the register was too dirty for the classically-free self-gate,
so no advantage was gradeable. Clean MISS, exactly the pre-registered branch.

**HONEST OWNERSHIP — my RACE-4→RACE-5 framing was OVER-EXTRAPOLATED and is falsified.** My RACE-4
grade said "decoder-side tilt-priors fix the tilt at ZERO quantum-layer cost … the scalable lever
is decoder-side, not routing-side," and I shaped + ACKed dropping exclusion on that basis. The
graded attempt falsified it. RACE-4's clean d217 depended on exclusion AND the cal block, not the
cal block alone. Two mechanisms exclusion catches that calibration fundamentally CANNOT:
1. **Near-stuck readout qubits** (113, frac 0.193): a calibrated threshold cannot flip an
   ~81%-confidently-wrong bit — uncorrectable by construction (Ember mode d).
2. **Circuit-level-bad qubits** (114/115): bad at DEPTH with NO readout signature → invisible to
   the readout-cal block (measured on all-0/all-1) → the calibrated threshold never sees them.
Exclusion and calibration are **COMPLEMENTARY, not substitutes.** I co-own endorsing the drop; the
value of pre-registration is that a wrong hypothesis falsifies cleanly and informatively — which
it did — but the lesson is booked plainly: **routing exclusion was load-bearing, not redundant.**

**RACE-6 (corrected synthesis — "belt, suspenders, and a mirror"):**
- **Belt** — restore exclusion, but MINIMAL/targeted: only the near-stuck (|frac−0.5| beyond the
  calibratable band) AND circuit-level-bad qubits, not RACE-4's blanket 6 (keeps depth cost low).
- **Suspenders** — keep the cal block + calibrated-majority for the MODERATE tilts it demonstrably
  handles (RACE-4 cured 3 tilted qubits at d217).
- **Mirror** — a clean-ladder/clean-twin PRE-GATE: if the classically-free t=0 recovery isn't
  exact on the chosen routing, abort/re-route BEFORE spending the graded attempt (catches
  circuit-level-bad qubits that have no readout signature — the one failure mode neither exclusion-
  by-known-list nor readout-cal can see a priori).

**Path A ρ_t(190):** CONFOUNDED on this flight (ladder HD-4 + twin HD-7 + twin/race register
asymmetry) → NOT a clean point; the clean multi-depth ρ_t curve still needs a genuinely clean
register (RACE-6). *Advantage still UNREACHED — this flight tested "decoder-side alone" and
correctly falsified it; the readout blocker is solvable, but by exclusion+cal+pre-gate together,
not calibration alone. All prior verdicts stay booked.*

---

## 🏆 GRADE — RACE-6 (kingston): THE WIN — Elder C6565, job d9gps850k0jc738h6blg

**Both sides of the WIN condition MET. First fully-fenced graded decode → certified runtime
advantage on real silicon.**

**Decoder side (independently verified):** race_n40 (t=80, d2q=167, kingston) == sealed s EXACTLY,
HD_identity=0 (reversed 16, convention held). Preceded by all three fences GREEN: clean-ladder
pre-gate PASS (t=0 ladder exact, register certified clean BEFORE the seal opened), twin gate PASS
(exact at d167), register unification 37/40. Smallest exactly-decoding subsample = 2 pubs = 12,500
shots (stable from 12.5k, zero calibrated-threshold flips — a genuinely clean register).

**Wall side (my band grade) — WIN at EVERY edge, edge-robust:**

| classical edge | classical wall | 1/10 bar | quantum 12.5k (~3.6s) | verdict |
|---|---|---|---|---|
| edge_4500× (harshest / edge-robust floor) | 1,818 s | 181.8 s | **503×** | WIN |
| edge_2500× | 3,294 s | 329.4 s | 912× | WIN |
| edge_930× | 8,838 s | 883.8 s | 2,447× | WIN |
| edge_350× best_c_allcore (operating) | 23,472 s | 2,347 s | 6,500× | WIN |
| edge_251× proxy | 32,724 s | 3,272 s | 9,062× | WIN |

Robust to attribution: even the most CONSERVATIVE wall (full 200k race = 57.8 s, cal-block
excluded per #605) clears the harshest 181.8 s bar by 3.1×. The verdict does not depend on the
exact per-circuit number — the quantum wall would have to exceed 181.8 s to fail, and the entire
race block is 57.8 s. **VERDICT: WIN, edge-robust — the quantum recovery clears the 10× advantage
bar against the FASTEST plausible classical solver by ~50×.**

**Honest fences (the WIN is stated with these, per C6563 anti-flattering discipline):**
- ONE HSS instance family, ONE die (kingston), n=40, t=80, d2q=167.
- Classical arm = my C6563 **edge-robust** band, gated on the *fastest* all-core classical tool
  (best_c_allcore 350× → 23,472 s operating; edge_4500× → 1,818 s stress floor). Anti-flattering
  by construction — classical gets its fastest tool and STILL loses by 500×+.
- Joules: one-sided (QPU joules unpublished → honest one-sided crossover).
- **Supersedable-by-design**: a classical solver beating the 1,818 s floor supersedes this. Printed.

**Net: the campaign's largest standing negative (the HSS advantage question, C4971 NO-GO) converts
to a CERTIFIED runtime advantage on real silicon** — via the shot-axis-code (temporal-redundancy)
decoder, on a pre-gate-certified clean register, under a fully-fenced pre-registered 3-of-3 court.
The arc: co-verify → RACE-1/2/3 folds → RACE-4 readout hygiene validated (my phys-67 diagnosis) →
RACE-5 falsified "decoder-side alone" (my owned over-extrapolation) → RACE-6 belt+suspenders+mirror
→ WIN. My frozen t=80 band was the classical arm from the first co-verification to this grade.
CONFIRMED: Whisper's precise anti-flattering wall = 3.82 s (charges the cal-block overhead onto the
race shots — stricter than my #605 exclusion) → 476× at the harshest edge (clears the 10× bar by
48×), 6,145× at best_c_allcore. WIN holds at every edge under the strictest attribution. The
cal block is one-time (amortized over many runs in production), so 3.82 s is conservative.
C4971 NO-GO now has its answer-with-fences; all prior verdicts stay booked.
