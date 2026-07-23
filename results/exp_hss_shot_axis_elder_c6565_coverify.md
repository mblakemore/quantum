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
