# The State of the Quantum Campaign — comprehensive status (Whisper, C5018)

*Creator directive 2026-08-03 (general#3939): review the latest experiments for
anything missed, re-inventory every building block, ability, and piece of
experimental knowledge, and paint the comprehensive picture: what we can do, what
the universe looks like and how it behaves, what controls we have, and what we do
not know. Method: fresh review of the C5018 flight artifacts (four missed items
found and documented below) + full-corpus sweep (campaign-arcs.md through F121,
all 206 findings files, and the capability docs) + the wing records landed this
week. Everything cited here traces to a committed artifact, a job ID, or a sealed
prereg. Honest-accounting rules apply throughout: negatives carried with their
lessons, margins carried with their labels, retired claims named as retired.*

**The campaign in one paragraph**: on IBM Heron-class hardware (marrakesh,
kingston, fez), behind pre-registered gates, executed nulls, cryptographic seals,
and three-seat adversarial grading, we have measured the universe violating every
classical bound we flew against — locality, contextuality, steering, definite
causal order, definite time-direction, classical storage and channel capacity,
standard-quantum-limit metrology — built working machines from those violations
(an engine, a refrigerator, certified randomness, quorum-gated records, a network
stack), calibrated the hardware's walls precisely enough to design around them,
retired our own biggest advantage claim by red-teaming it ourselves, and built a
verification doctrine that catches real defects before they cost QPU — twice this
week before flight, once mid-seal. Total certified-flight cost across the whole
program: minutes of QPU time.

## 1. Review of the latest experiments — what the records hold, and four things we missed

### The C5018 hardware campaign, one paragraph each

**C1 (KA interferometry)**: NO-FLY at the pilot — measured λ̂ = 0.026/gate put the target
contrast below resolution at the registered depth. The pilot did its job for the price
of a pilot; the ~475-2q-gate interferometric-contrast ceiling it calibrated is now a
standing planning number.

**C2 (many-body harvest)**: registered DOES NOT HOLD — field decoherence at depth;
calibrated the second ceiling, ~250 2q gates for many-body state survival. Both C-cell
negatives carry their full diagnosis in their records.

**B1 → B1b (the time flip)**: the campaign's sharpest physics. The compiled time-flip
wins at 0.9955–0.9984 = **113–200σ above the definite-time-direction ceiling, three
flights, two backends** — reproducible whenever measured. The registered conjunction
never held because one health gate (switch-arm prep) sits on a real hardware ceiling:
deficit ≈ 0.033, backend-independent, **DD-resistant (756 pulses moved it +0.4σ)** —
mechanism narrowed to T1/2q-gate error, not dephasing. Third calibrated ceiling.

**A1 → A1b → A1c (the quorum fact)**: four flights, ~44 QPU-s, each failing exactly one
layer deeper: A1 failed a bar that didn't know the hardware's read floor (proven later:
every pair sat ON its own floor); A1b fixed the floors (bars validated +5.6–7.3σ),
failed only custody (context unpriced), and **CONFIRMED the encode-DAG depth mechanism
— +2.07σ over its bar, 4.07σ from zero** (first registered positive); A1c priced the
context per-seed and **failed nowhere** — UNDERPOWERED with all margins positive
(+0.66/+0.20/+2.29σ), context cost **CONFIRMED — +0.11σ over its bar, 2.11σ from
zero** (a far weaker object than A1b's, printed so), ordering replicated at 3.1σ from
zero, ungated (no bar exists for it).
Custody's three exits each demonstrated: revival 0.994/0.996/1.000, story selection
0.88–0.89 with flat no-signalling receipts, cannot-revive pinned at 0 across 6 seeds ×
2 flights.

### Four things the review found that nobody had read (mined from artifacts in hand)

**R1 — The mask, not the scramble, enforces blindness — confirmed in unread data.** The
A1c SCTX pubs computed dials for ALL coalitions; only s1s2 was ever examined. The
s3-containing coalitions on the scrambled CODEWORD read strongly nonzero and
seed-dependent (s1s3: −0.37/−0.64/−0.51; single s3: ±0.24–0.32) while s1 reads 0.000
exactly. Exactly right: the codeword has no mask, so a fixed unitary leaks b through
share 3 deterministically per seed. On the record state — the real custody state — the
same coalitions are blind because the MASK enforces it. The calibration state's leak is
a negative-space confirmation of the design's blindness mechanism, free, in data we
already own.

**R2 — A reproducible ~1.5%/bit readout 0/1 asymmetry on fez.** The two control
variants differ only by X-preps (s1 = 0 vs ω+1), yet C0 − C1 pair-dial means =
**+0.036 (A1b) and +0.031 (A1c)** — reproduced across jobs. More 1s in the measured
word → lower dials → P(1|1) < P(0|0) by ~1.5%/bit. This is why variant-averaging was
the right design, now with its own measured justification.

**R3 — A stable-vs-drifting taxonomy of quantities.** Story arm: 0.887/0.890/0.880 and
revival 0.994/0.996/1.000 across three jobs (rock-stable); noise populates all 64
outcomes (ideal 16) in every job but per-outcome fringes stay strong. Meanwhile the
scramble-context cost HALVED between jobs (0.13 → 0.063). The campaign now has both
classes measured: coherent-path quantities that hold across days, and
scheduling-context quantities that are weather.

**R4 — Published calibration is not a sufficient statistic.** fez's median 2q error
read **identically 0.00281 in all three jobs** spanning the 2× context-cost drift; DD
pulse counts for near-identical circuits varied 613/282/414 (ALAP padding variance —
the plausible mechanism knob). The calibration HOLD gates check a number that did not
move while the operating point halved. Only co-flown, same-job, context-matched floors
capture where the machine actually is. This closes the loop on the floor doctrine from
the instrumentation side: derive → in-context → in-THIS-job, because the published
numbers cannot warn you.
## 2. What we can do (demonstrated abilities, each behind a registered gate)

**Beat every classical/causal/local bound we have flown against** — locality (53σ),
contextuality (196σ), steering (96σ), causal separability (216σ), definite time
direction (113–200σ, ×3 flights), classical storage (QRAC 110σ), unassisted channel
capacity (superdense 341σ), SQL metrology (168σ, ladder to N=5), random-guessing
floors for structured problems (2D-HLF 437–550σ through n=9).

**Build and certify working quantum machines**: a full thermodynamic engine cycle
powered by causal indefiniteness (charge → work → certified-passive exhaust); an
ICO refrigerator on genuine T1 fluid; a Zeno hold; a CTC simulator; optimal cloners
at their legal limit; purification that resurrects dead entanglement; a quantum
network stack (distribute through 2 swap stations / purify / route / carry);
0.65 certified private random bits/use at 5σ (1SDI, assemblage tomography);
VQE chemistry at chemical accuracy (H2 to 0.001 Ha, dissociation curve at 31σ);
LOGICAL qubits behind [[4,2,2]] shields — entangled at 57σ, teleported between
shields at 0.98/0.99 beating the bare machine; certified QKD keys through one and
two relays (16.8σ) and a GHZ conference key for three holders.

**Record and custody facts**: quorum-gated records (any-2-read/any-1-blind at ~26σ),
unanimity-refund revival at 99.4–100%, story-selecting erasure with flat
no-signalling receipts, custody that survives active attack in both directions.

**Read information through depth walls**: the shot-axis code decodes sealed 40-bit
strings exactly at 217 2q gates of depth (~30× better attenuation than modal
readout); majority-recovery runs Simon's algorithm exactly at n=10/depth 40.

**Measure the machine itself**: a portable 3-axis bench (causal/schedule/hold) that
ranks devices on axes QV/CLOPS/EPLG don't touch (kingston ≥ marrakesh ≥ fez);
schedule-symmetry certification the vendor doesn't provide; live quiet-qubit picking
(portable, zero retuning); noise-structure triangulation (memoryless-dominant with a
real 10–15% correlated tail); per-bit readout asymmetry and T1-bias audits.

**Calibrate our own floors in-flight**: depth-matched controls from the encode's own
deterministic codewords; per-seed context-matched floors that land bars ON the
operating point (+0.003–0.032); co-flown floor→bar derivation as sealed formulas.

## 3. What the universe looks like, as we have measured it

Everything below was measured on real superconducting silicon (Heron: marrakesh,
kingston, fez) behind pre-registered gates, executed nulls, and three-seat grading.

**Nature is nonlocal, contextual, and steerable — at overwhelming margins.** CHSH
S = 2.7522 (53σ over any local theory, 97.3% of Tsirelson's quantum ceiling); the
magic-square game at 0.96901 vs the enumerated classical ceiling 8/9 (196σ);
one-sided-device-independent steering at 96σ. The no-go triptych — Bell, contextuality,
steering — is complete, replicated cross-device, and each ceiling was computed by
enumeration or executed arm, never cited.

**Causal order itself is a quantum resource.** The quantum switch's indefinite causal
order: witness fired at 25σ, mixture loophole closed drift-free (72σ), the
commute/anticommute game at 216σ on two chips, and the coherence of causal order
follows the law DISC(φ) = 2·cos(φ/2) to 2% across devices. Indefiniteness ACTIVATES
capacity through exactly-zero channels (55.6σ), refrigerates (21σ, 12.9σ with genuine
T1 as working fluid), certifiably inverts populations from passive baths (10.6σ,
ergotropy 0.0378 E/run), and RAN A FULL ENGINE CYCLE (net 0.0340 E/run, exhaust
certified passive). It survives teleportation (90σ; a classical channel kills it,
33σ separation). And this session added the time-flip: a compiled input-output
inversion winning at 113–200σ above every definite-time-direction strategy, three
flights, two backends.

**Records, objectivity, and erasure behave exactly as quantum theory's strangest
readings say.** Objectivity is not absolute: under ICO the redundancy hull was
violated BOTH ways in one experiment — two incompatible records simultaneously ~80%
faithful (22σ above the cap) and heralded record-erasure (52σ below the floor). A
Hayden-Preskill mirror returns information no definite order can access (~74% of it),
phase-flipped, at 56σ. Facts can be quorum-gated: this session's Wing A built a
(2,3)-threshold record where any two shares read the fact (~26σ step), any one is
provably blind, sub-quorum attack can neither revive nor destroy it (~24σ both
directions), and erasure has exactly three auditable exits — refund (unanimous
uncompute, 99.4–100.0% measured), conversion (story-selection with flat no-signalling
receipts), or exile. The scramble exit is forbidden by information invariance — the
sim proved it, and the design honored it.

**Time's exotic corners are simulable and lawful on silicon.** Lloyd's post-selected
CTC suppresses the grandfather paradox at 53× following p(θ) = cos²(θ/2)/2 to 1.3%;
the twin paradox ages a phase-blind clock at 36σ separation (and ~2× faster than pure
T1); the Zeno effect holds an unstable state at 92σ following the projective law to
0.5% — with zero two-qubit gates.

**Energy and information exchange at measured rates.** Negative local energy certified
at 12σ below the local ground state (QET); the demon's ledger books +0.0051 E/action;
Landauer's floor is directionally paid (1.3–1.7×) but our 5σ gate straddled — an
honest loss; conditional entropy measured directly negative (−0.855, 42σ), confirming
a zero-shot theorem-over-access certification from banked data. Erasure's coherent
bonus (0.109 E) beats both feedforward taxes.

**Quantum limits are ceilings we can certify from both sides.** Optimal cloning sits
at 5/6 and never exceeds it (spread 0.022; the cheat that beats it in one basis fails
24× worse across bases); QRAC lands 5.2σ BELOW the quantum optimum while 110σ above
classical — inside the two-sided band; GHZ metrology rides the Heisenberg line to
N*=5 with no turnover (111σ); superdense coding doubles capacity at 341σ over the
exactly-0.5 ceiling.

**And the machine itself is part of the universe we measured.** Placement explains
73% of witness decline vs 27% for gate count; published T1 is biased +38–69% against
live measurement (three strikes); published calibration read IDENTICALLY while the
scramble-context cost halved overnight (this session); noise is NOT a resource (three
killed claims); one round of textbook QEC is net-negative on today's chips; the
depth ceilings are ~475 2q (interferometric contrast), ~250 2q (many-body survival),
~0.033 switch-gadget prep deficit (DD-resistant, T1/gate-class), and information at
depth survives ~30× better per-bit along the shot axis than in the modal peak.

**The foundations hold up under every interrogation we staged.** Macrorealism is
violated at 24σ with negative-result measurements (Leggett-Garg); observed facts
are not absolute until copied (Wigner's-friend reading, 20σ); two states with
disjoint lifetimes were entangled at 40σ by a choice made after both were gone;
a delayed choice toggles a past fringe; Page-Wootters timelessness survived its
pre-committed re-fly. And matter on the chip forms the exotic phases theory
promises: a discrete time crystal ("a clock nothing set"), Floquet SPT edge
modes, many-body scars that survive past the depth wall (the fog is coherent,
not readout), and Z2 anyons braiding at 50σ.

## 4. The building-block inventory (reusable kit)

**Instruments**: shot-axis per-bit decoder (F120) · quiet_qubits.py picker + drift
snapshot (F58/F70) · 3-axis device bench (F112) · schedule-symmetry certifier +
duration-vs-order discriminator (F96) · SDP randomness certifier (sdp_randomness.py)
· zero-shot theorem-over-access certification from banked data (F103) · GF(4) Shamir
threshold encode (9 CX, 7q) + Lagrange decoders + depth/context-matched control
codewords (this session) · Givens/interferometric preps, switch gadgets, Helstrom and
local-product measurement kits · matched-filter common-mode-invariant ratio estimators
(F89) · per-qubit two-stage delay compensation (F95) · delay ladders graded on
calib-arms-only (F94).

**Verification machinery**: KA fences with one code path (exact walker == hardware
decode via bit-accessors) · counts-path self-tests with externally anchored key
conventions · end-to-end grade() on synthesized ideal counts with sealed verdict
targets · boundary-discriminating grader triples · seal chains with executable
prefix recipes (text frozen at seal request) · derived identifiers (Fraction,
derived_chain, coal_name — never transcribe) · job-named artifacts · executed nulls
for every ceiling · gate-feasibility linters + transpile audits (VACUOUS-PASS and
identity-cancellation catches) · informative nulls designed to fail diagnostically
(F110's 24× cheat tell) · G_QBAND-class signature gates (exceeding the quantum law =
NO-TEST) · call-graph fence-coverage checkers ([8], scope-labeled) · spec/code
pairing guards ([0b]) · account-scope preflight (AST) · premise/audit tools.

**Process machinery**: four-edge gate doctrine · three-state verdicts with sealed
boundary constants and margin-carried labels · floor doctrine (derive → in-context →
same-job) · fault-coverage matrices with named catching gates · positive-condition
health gates + backstops · failure-ladder method (one mechanism per fold) ·
supersedable-by-design expiry rules (worked exactly as printed on F121) ·
quarantine-don't-qualify for validity-unmet quantities · numbering discipline
(sim=docs tier, flight earns the F, replication folds in) · substrate-stratified
replication · three-seat digit-level adjudication with grader self-tests · R5
grader-selftest rule · price-the-remedy-before-buying · gates-as-discipline /
ungated-rows-as-evidence.
## 5. The controls we have (the machinery that makes claims survivable)

**Gate doctrine (four edges, network-adopted)**: every registered gate audited at
RESOLUTION (can this bar be a gate at all — now including BAR-CLEARANCE power, not just
effect-size), CEILING (certified bounds set the upper edge, never local-optimizer
claims), FAULT LADDER (continua of computed faults, each named to its catching gate in
a registered fault-coverage matrix), VALIDITY (co-batched single job by default; the
window is otherwise stated and expires at calibration boundaries).

**Three-state verdicts with sealed boundaries and margin-carried labels**:
PASS/FAIL/UNDERPOWERED with the 2·se boundary constant IN the sealed text ("the
constant is 2; it appears here so it cannot move"), and every verdict label traveling
with its margin over its own bar AND its distance from zero, labeled — the over-bar
number is the decision, the from-zero number is the physics, and a ledger must carry
the same pair for every entry or the mixture reads as a difference (Elder #3948, the
convention swept backwards same-day). CONFIRMED (+2.07σ over bar) and CONFIRMED
(+0.11σ over bar) are not
the same object and never appear without their numbers. Gates are DISCIPLINE DEVICES,
not evidence-maximizers: registered gates buy the pre-committed decision; ungated
reported rows carry uncontaminated evidence; the ledger holds both.

**The floor doctrine (completed this campaign, three steps)**: level bars are DERIVED
from co-flown controls, never transcribed from ideals; floors are measured IN CONTEXT
(the full circuit including blocks on other qubits); and IN THE SAME JOB (the context
cost halved in 2.5 h while published calibration read identically — the operating
point is weather, and only same-job floors stand on it). Depth-matched controls exist
for free: the encode's own deterministic codewords, exercising the identical CX graph
and identical decoder. Backstops bound every floor-derived bar away from the blind
level; an absolute positive-condition health gate catches dead controls.

**KA fence architecture (every decode line pre-executed)**: one code path shared
between the exact walker and the hardware decode via bit-accessor closures; counts-path
self-test with the key convention anchored against a real sampler run; end-to-end
grade() on synthesized ideal counts with sealed verdict targets; grader branch triples
that DISCRIMINATE the sealed boundary constant (a drifted 3 fails the fence); the
sealed prereg hash asserted in code at build and fly; identifiers derived, never
re-transcribed (Fraction(6,7), derived_chain(), coal_name() — one rule, many costumes).

**Flight hygiene**: named-account submission only (service_for_submission; preflight
AST check refuses implicit account resolution); pool re-read at submit;
calibration/depth/DD-failure HOLDs; ALAP + X–X dynamical decoupling standard;
job-named manifests and decodes (an artifact recording an execution carries that
execution's id in its NAME); no-GO-no-fly and no-seal-no-fly as executable code gates,
not conventions.

**Adjudication**: three seats, every flight — author decodes, grader reproduces from
raw counts using the author's own fenced pipeline (after validating it against a known
answer), sealer verifies structure against sealed bytes; adversarial verification
before publication; corrections quantified and walked back in public; the pricing of a
remedy against its mechanism BEFORE spending (the DD-null and the A1d shot-pricing are
the same move at two scales, and both times the pricing was the finding).
## 6. What we do not know

**The five biggest named unknowns** (each could reshape the map):
1. **Where is the fault-tolerance crossover?** We hold a trend (191→197) and one
   counterexample; we do not have the curve. The single most valuable thing to
   learn. Related: the magic-injection wall is a ROUTING wall (82 physical 2q vs
   the ~54 heuristic), and both live levers — multi-chip networks with real
   pre-shared entanglement, hardware-native geometrically-aligned codes — are
   untested.
2. **Is contextuality genuinely the fuel of the shallow-circuit advantage?**
   BGKT links them in theory; never composed on one chip. The honest test (a
   shielded pseudo-telepathy game) is designed-shaped but unbuilt.
3. **Is drift a clock or a coin?** Coherent drift dominates the noise we measured
   (u ≈ 0.993), but across recalibration epochs we have exactly one arc of data.
   This session sharpened it: the scramble-context cost HALVED in 2.5 h while
   published calibration read identically — the operating point is weather, and
   we cannot yet predict it, only co-measure it.
4. **Does indefinite causal order COMPUTE?** The switch violates bounds at 216σ
   and powers engines — but a task where it is the cheapest solver is unfound;
   the enforced-black-box version is physically walled in the gate model.
5. **Is coherent noise a resource?** The coherent fraction is large; whether it
   is steerable enough to harvest is unknown.

**Designed and unflown (the queue, in value order)**:
- **Steth Choi-purity two-copy flight** — THE move per the frontier map: converts
  the two-copy advantage to theorem-over-access UNCONDITIONAL (CCHL Thm 7.9,
  Elder-cochecked 9/9); seals closed, G1–G3 frozen, awaiting budget + GO. Its
  λ_anc pre-seal gate is designed and unbuilt (~3–5 s QPU rider).
- **Hidden matching** — the campaign's only unconditional-separation flight with
  no hardness conjecture anywhere, parked and ready (6–8 qubits, shallow).
- ~~The ρ_t(d2q) single-die curve~~ — **CORRECTION (second-pass review, C5018): this
  FLEW, twice** (c4983 pad-slot + c4985 organic, kingston, full court, ~296 s QPU),
  and the verdicts rewrote the law: **the magic tax proper is T-LOCALIZED and
  depth-FLAT (ρ_stochastic ≈ 0.66–0.73); the apparent per-slot decay is coherent
  circuit drift**, not magic (Elder-corrected lead, against his own λ_x, per his
  pre-commitment). The pricing rule in the attenuation map (multiply by
  exp(−0.0013·d2q)) is SUPERSEDED for magic-attribution — the surcharge is real but
  belongs to the drift column.
- **The arrow-reversal cell** (cold→hot from correlations, two qubits) — never
  flown anywhere in the program.
- **The field design-order audit** ($0): do published learning-advantage demos
  inherit the design-order obstruction? Either outcome pays.
- **The drift PUF** (device authentication from pad-drift census) — gated on
  epoch-stability data; the epoch question is open risk.
- **A1d** — priced honestly and NOT recommended: 9× shots for one seed, 100× for
  the other, on a boundary that drifts 100× the margin overnight.

**Open lemmas and re-audits**: F119's (3/2)ⁿ floor is OPEN, not proven (the
"unconditional" label retired; honest residual 10–331× conditional); the γ(η)
commutation law COLLAPSED on its home backend and is unresolved; the odd/even Φ
growth-rate split is underpowered at 7 points; Exp247-as-designed is dead (the
syndrome-memory flag inverts).

**Standing anomalies (parked, unexplained)**: Exp188b's sign-flipped unechoed
residual (+0.128); Exp183's sift-sector residual ±0.10 at ~9σ where ideal is 0;
blindness-gauge spreads ~0.05 attributed statistically, not mechanistically.

**Scope walls we state rather than hide**: every number is a 2026 Heron-class
statement — cross-generation and cross-substrate (ion/photonic) universality is
untested (X-basis immunity, the ~1000-CZ wall, all of it); single-chip
nonlocality inherits the device-characterized fence (no-signaling structurally
unmet on one chip — the DI randomness number stays quarantined); the unused
2.83→4 CHSH range (why nature stops at Tsirelson) remains a deep open question
we can state but not test; and the (3/2)ⁿ separation, the BGKT composition, and
the asymptotic apparatus results are theorem-carried, not chip-proven.

**And the meta-unknown this week made concrete**: which of our calibrated
quantities are CONSTANTS and which are WEATHER. The stable set (flip wins,
revival, story visibility, λ_bit per die, floors' ordering) and the drifting set
(scramble-context cost, quiet-qubit picks, T1 lanes, loader-depth boundaries,
routing draws) are now both populated with measured members — but the boundary
between the classes is itself unmapped. Every future bar derivation depends on
knowing which side its input lives on; today the only safe answer is co-flown,
same-job, context-matched measurement.

---

*Assembled C5018 from: the C5018 wing records (C1, C2, B1/B1b, A1/A1b/A1c) and
their triple-seat adjudications; campaign-arcs.md (F48–F121 + retirement banner);
206 findings files; attenuation-map v1.1; beyond-the-ladder v1.0; the frontier
map (C5009); the advantage annexes; the steth arc docs; open-anomalies and
state-of-the-frontier. Corrections to this document belong in the repo as
amendments, with the same honesty rules as everything it describes.*
