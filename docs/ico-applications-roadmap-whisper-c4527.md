# What Else Can a Certified Quantum Switch Do? — ICO Applications Roadmap

**Author**: Whisper (DC15W), C4527 (2026-07-09) — Creator-directed follow-up to the Exp105 WIN
**Standing assets**: certified switch apparatus (F75/F77, Exp105 game WIN 216.8σ, Exp105b fez
replication in queue), a validated causal-bound SDP solver (`causal_game_sdp.py` — bounds for ANY
finite game on demand), the padded uniform-skeleton compilation trick, sentinel/window discipline.
**Honesty tiers**: T1 = theory-backed, low-depth, winnable with the existing pipeline;
T2 = creative/novel on our hardware, needs a feasibility pass; T3 = zero-QPU leverage.

## T1 — Next provable beats (same pipeline that won Exp105)

**1. Capacity activation — "information through two walls"** (Ebler–Salek–Chiribella 2018).
Two completely depolarizing channels each transmit exactly zero information; placed in a switch,
classical information flows (~0.05 bits/use for full depolarizing — small but provably nonzero).
Any definite order (or mixture) of the same two channels transmits zero, so ANY measured mutual
information above a pre-registered noise floor is the win. Depth class: switch skeleton + twirl
ancillas — near Exp105. The most headline-friendly demo in the family ("we sent a message through
two perfect walls"). Pre-req: implement "genuinely depolarizing" arms honestly (twirled gates),
device-characterized scope stated as in Exp105.

**2. The N=3 switch and SCALING separations** (Araújo–Costa–Brukner 2014). The N-switch solves
the Fourier promise problem with N queries where causal circuits need O(N²) — a *scaling*
separation, qualitatively stronger than Exp105's fixed gap. N=3 = superposition of 6 orders
(2–3 control qubits). Step 1 is a free transpile audit: does a 3-switch fit the depth budget on
heavy-hex? If yes, my solver generalizes to the 3-party bound (bigger SDP, same machinery).
First hardware demonstration of a query-SCALING causal advantage would be a genuine flag-plant.

**3. The bound factory — design the game the chip is best at.** The SDP solver computes the
causal bound for ANY finite game; Ember's audit computes hardware cost for any unitary set. Run
them in a loop: search game space (unitary sets, priors) to MAXIMIZE (hardware margin − causal
bound), subject to 1-CZ-per-controlled-U implementability. Exp105 played the game the literature
handed us; nothing stops us designing games native to this chip's noise profile. Zero QPU until
a candidate beats 0.869's margin in sim.

## T2 — Creative instruments (novel on our hardware, feasibility first)

**4. ICO thermodynamics fueled by the chip's own decoherence** (Felce–Vedral 2020 switch
refrigerator; battery-charging variants). The thermalizing channels in these protocols are
usually synthetic. Ours don't have to be: **idle delay near T1 IS a thermalizing channel** — the
chip's native noise as the working fluid, switch of two idle-decay arms, heat/work signature read
from the control. Connects the entire noise-characterization corpus (scramblon structure, drift,
T1 maps) to the ICO arc. Honest label: the literature disputes whether the switch-fridge is
"really" ICO-powered vs coherence-powered — a both-sides discriminating test is itself a
contribution.

**5. Hidden-order diagnostics — causal tomography of the chip itself.** Invert the tool:
nominally-SIMULTANEOUS gates on coupled qubits may have effective hidden ordering (crosstalk
timing, scheduler artifacts). A witness-style circuit can certify "genuinely order-symmetric" vs
"secretly sequenced" execution of parallel operations. Nobody frames crosstalk as a causal-witness
problem; we own both the apparatus and the metrology niche (quiet-qubit picker, window sentinels
→ "QPU weather service"). Candidate new findings arc; zero theory risk (it's characterization,
not foundations).

**6. ICO noise-averaging.** If error accumulates differently for A-then-B vs B-then-A (it does —
routing/crosstalk are asymmetric), the switch executes both orders coherently. Test: does
switch-averaged execution beat the classical 50/50 mixture of the two orders on a fidelity
metric? If yes, "compile into superposed order" becomes a tiny but real error-management
primitive — from our own F57/F67 placement-asymmetry data. Sim first; cheap.

**7. Game-wins as certified randomness (semi-DI direction).** Exp105's 97.7% vs 87% margin
witnesses nonclassicality that randomness-expansion protocols could consume, against
causally-ordered adversaries (Bavaresco et al. semi-DI framework). Theory gap to close before
any hardware: what min-entropy rate does a game win certify, under which assumptions? Flagged as
a literature-collaboration item — NOT claimable with device-characterized scope alone.

## T3 — Zero-QPU leverage

**8. The Pearl bridge paper** (my specialist lane): Exp105 is the cleanest physical object
showing where do-calculus typing ends — the causal skeleton itself in superposition, with
game data. A write-up aimed at the CAUSAL-INFERENCE community (which has no hardware
demonstrations) rather than the quantum one: F80 synthesis + Exp105 numbers, Rung-by-Rung.
**9. Interactive demo, game mode**: extend the GitHub Pages switch demo — play the discrimination
game against the real per-pair hardware distributions; watch a causal player cap at the prior.
**10. The manuscript**: F73–F77 + Exp105(+105b) is arXiv-shaped: sim → hardware → adversarial
control → drift-free same-device → cross-device law → pre-registered game beat (→ replication).

## Recommended order

Exp105b grade (in queue) → **capacity activation** (T1.1, one job, headline demo) → **3-switch
transpile audit** (free) → **hidden-order diagnostic prototype** (cheap, entirely ours) →
bound-factory search as background sim work. The Pearl paper and demo game mode are
rainy-day/zero-budget cycles. All hardware steps inherit the Exp105 discipline: frozen pre-reg,
sentinel gates, padded skeletons, sibling cross-check.
