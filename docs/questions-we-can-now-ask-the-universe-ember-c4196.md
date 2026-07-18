# Questions We Can Now Ask the Universe

**Author**: Ember (DC15E), C4196 (2026-07-18), Creator-directed ("Review our quantum museum and
all of our quantum repo experiment results. What questions can we now ask the universe?").
**Method**: every apparatus this campaign validated is an *instrument*, and an instrument's value
is the questions it makes askable. This doc walks the full record — F1–F118, Exp1–Exp150, the
22 museum exhibits — and states the questions the record now licenses, each tied to the findings
that make it askable and, where possible, a named first experiment. It is additive to the
[ORQ ledger](next-steps-and-open-questions.md) and [Star Trek horizons](star-trek-horizons-whisper-c4601.md):
questions already answered are summarized in one section so the *new* frontier is visibly new.

**The one-sentence shift**: two years ago these were *whether* questions. The record turns them
into *how much* questions — how cold, how many bits, how deep, how far — and the universe answers
quantitative questions differently than philosophical ones: with error bars.

---

## I. What the record has already answered (so we don't ask it again)

| Question | Answer | Where |
|---|---|---|
| Can causal order be indefinite on silicon? | Yes — certified vs the causally-separable bound, replicated across 3 dies (0.3pp concordance) | F73–F82, F112 |
| Do the three great no-go theorems all fail classically on one chip? | Yes — Bell, ICO, contextuality, each with executed nulls | F73 · F82 · F106 |
| Is indefinite causal order a *resource*? | Yes — refrigeration 21.1σ, full engine cycle 0.034 E/run, cold branch *spent* on an external qubit | F86/F88/F94/F95/F118 |
| Does it survive transmission? | One teleport hop, yes (90σ); classical channel kills it (33σ separation) | F92 |
| Is noise a computational resource here? | **No** — killed under controls | F55/F56 (P1 RESOLVED-NEGATIVE) |
| Where is the compute wall? | ~800–1000 CZ; QAOA ceiling co-located; deep-loader MLE is a window lottery | F05, Exp33, F78–F81 |
| How many certified private bits does one trusted side buy? | 0.65 bits/use, rigorous SDP, one-sided-DI | F115–F117 |
| Does the Shor *kernel* run? | QFT period-finding recovers r at t=5 / depth-230, incl. the non-divisor continued-fractions regime (NOT factoring RSA) | Exp150 (C4195) |
| Is a NISQ reader's robustness magic? | No — it is *optimal detection of a shrinking bias*; the wall is a statistical-power threshold, movable with reps | Exp148 (C4195) |

---

## II. The askable frontier — twelve questions, by instrument

### The switch as instrument (causal order)

**Q1 — Can two parties *share* causal indefiniteness?**
F92 proved the switch control survives one teleport hop. F91 proved entanglement survives two swap
stations. The composition has never flown anywhere: distribute the control across the repeater
machinery so that *which-order-happens* is a resource held jointly by two chip regions —
networked causal structure. *First experiment*: F92 apparatus + one F91 swap station on the
control line, graded against the F92 survival floor minus the measured per-hop cost.

**Q2 — Can superposing two orders beat the best fixed order at error management?**
The "Heisenberg compensator" (horizons P3) is still the highest-leverage unflown idea: placement
noise is asymmetric (F57–F69), so executing A-then-B and B-then-A *coherently* may beat either.
Sim tier is free and decisive; hardware only if a candidate clears 5σ in sim. This is the question
that would turn ICO from certified curiosity into an engineering primitive.

**Q3 — How cold is the floor of order-absence cooling?**
F118 spent the cold branch (sub-bath reset at 5σ, beating definite order but not native reset).
The [cooling-floor doc](ico-cooling-floor-and-concentration-boundary-whisper-c4720.md) names the
classical-concentration boundary. The open question is the *gap*: measure where ICO cooling sits
between the definite-order bound and the concentration boundary as bath temperature is swept —
a dose-response law, not another existence proof.

### The thermodynamic ledger

**Q4 — Do the quantum-interest theorems bind on a chip?**
F97 certified local energy 12σ below ground. Theory (Ford–Roman quantum interest) says negative
energy must be "repaid" with interest in space or time. Nobody has graded a repayment theorem on
transmon hardware: pulse the extraction, measure the surrounding positive-energy envelope, and ask
whether the measured pulse obeys the quantum-interest inequality. A frozen-bound test where the
*bound being respected* is the win — same currency as F110's cloning ceiling.

### The GF(2) machine + QFT (the Ember line)

**Q5 — Where exactly does the Shor staircase die on NISQ? — DELIVERED (Exp152, C4196).**
Priced: the smallest textbook Shor (N=15) costs **1,564–6,172 CZ = 1.6×–7.7× past the ~1000-CZ
wall**; the QFT back-end Exp150 flew is only ~0.5–1.8 % of the circuit, the missing ~98 % is the
modular-exponentiation front-end, and the survival predictor pins `p_true` at 0.5 (reps → ∞,
drowned) far below that depth. The gap is not a tuning problem — it is the wall standing between the
kernel and the algorithm. See [finding-exp152](../findings/finding-exp152-distance-to-shor-ember-c4196.md).
(Fence held: toy N, not RSA; compiled-Shor cheat excluded per F110 pattern.)

**Q6 — Is the confident-wrong inversion coherent? — ANSWERED: NO (Exp149b, C4196).**
The matched-scheduled-duration re-test flew (job `d9di3maneu4c739nadqg`): frozen-frame and twirled
arms **invert together** at every depth, so Pauli-twirling at matched overhead does not remove the
inversion → it is **not purely coherent**. Exp149's "twirl helped the deepest" was the frame
overhead (it reappears equally in the no-twirl frozen arm). The C4195 coherence question is closed.
See [twin-falsifications finding](../findings/finding-c4196-twin-matched-control-falsifications-ember.md).

**Q7 — Is "self-correction = optimal detection" a law or a local fact?**
Exp148's verdict — reader robustness is exactly the statistics of detecting a shrinking bias —
has one device and one code family behind it. If it is a law, its exponent should transfer:
same protocol on `ibm_fez`/`ibm_kingston` and on a different code (repetition → surface-fragment)
should collapse onto one curve after rescaling by measured E_CX. A two-flight test of a
candidate *universality class* for NISQ decoders.

### The trust ladder

**Q8 — Can the randomness certificate be made bias-clean, then *used*?**
F117's audit discloses a +0.006 method bias ≈ 1 SE the bootstrap cannot see — the limiting factor
is now systematic, not statistical. Two-part question: (a) close the bias (debiased estimator or
bias-bounded certificate); (b) operationalize it — the "Prime Directive beacon" (horizons P7):
certified bits, timestamped with their violation, feeding the trading stack's Monte Carlo. The
first standing *product* of the campaign.

### The metrology instrument

**Q9 — Can the Heisenberg advantage survive its own fine print?**
F108's audit names two unpaid tolls: the 3-fold phase ambiguity (needs a Higgins-2007 cascade)
and the Huelga–Plenio dephasing limit under time-optimized interrogation. Both are *measurable*
on this hardware with F111's dephasing structure already in hand: fly the cascade (does absolute
phase come out at the Heisenberg rate?), then locate the N* where measured dephasing eats the
scaling gain. Answering both converts a local-Fisher existence proof into a deployment verdict.

### The noise atlas

**Q10 — Is the correlated dephasing tail exploitable?**
F111 measured IBM dephasing as dominantly memoryless with a real ~10–15% correlated tail. A DFS
only pays when noise is correlated — so a DFS *sized to the measured tail* (encode only the
subspace the correlation structure actually protects, hybrid DFS+echo) is a pre-registerable bet
with the rare property that the noise measurement already exists. If it wins, the campaign's
noise *atlas* becomes a noise *compiler input*.

**Q11 — Are our laws about the universe, or about this chip?**
The sharpest version of ORQ#4/#5: the ~1000-CZ wall, the depth-decay law, the BGK ladder erosion
(F114) are all Heron-generation numbers. `exp141` (BGK on Quantinuum H2, pre-reg drafted) is the
single highest-information flight available: one trapped-ion run answers (a) does the shallow-
circuit solver's erosion law transfer, (b) does an information-theoretic wall exist at a
comparable *error-budget* altitude when the per-gate physics is completely different. Cross-
*platform* is the difference between hardware characterization and physics.

### The scientific record itself

**Q12 — How much of the published NISQ-advantage literature is real?**
Still the largest unclaimed prize (P3, proposed since C4108). This network has the only
battle-tested apparatus for it: pre-registration, frozen graders, budget gates, self-retraction
precedent (F80, F94, F100, F115). Scoping pass: pick 3–5 high-citation claims with reproducible
circuits; report replicate / partial / fail. No one else grades the literature this way because
no one else *can* afford to be wrong in public as cheaply as we can.

---

## III. Questions we provably cannot ask (the standing fence)

Unchanged, and worth restating so ambition stays aimed: **causal-inequality violation** (no
quantum-switch construction reaches it — no circuit we can write); **device-independent
certification of our own switch** (Bavaresco et al.; and no-signaling is unmet on a single die —
F115 quarantined exactly this); **RSA-relevant factoring** (Q5 measures the distance to the wall,
it does not cross it); **application-layer resurrection** of a dead violation through the full
network stack (witness-fragility hierarchy, C4618). Knowing these are unaskable *here* is part of
the record's value.

---

## IV. Priority view (if we fly in order)

| Rank | Q | Why first | Cost tier |
|---|---|---|---|
| 1 | Q5 distance-to-Shor | Predictor exists (0 QPU to price); headline number; my line's natural next rung | analysis → 1 small flight |
| 2 | Q6 matched-overhead twirl | Open confound from C4195; small; closes a live mechanism question | ~8 QPU-s |
| 3 | Q2 Heisenberg compensator | Sim-gated, free until it earns hardware; highest engineering upside | sim → gated HW |
| 4 | Q11 Quantinuum H2 cross-platform | Pre-reg drafted; one flight, two universality answers | external platform |
| 5 | Q8 beacon | First standing product; theory exists | analysis + small flights |

The rest are real but should queue behind these — Q1/Q3/Q4/Q7/Q9/Q10 each need a fresh pre-reg
pass, and Q12 needs a scoping cycle of its own.

---

## Addendum (same night, +25 min): a thirteenth instrument opened

Whisper C4839 flew **Exp151 — a discrete time crystal on `ibm_fez`** while this doc was being
written: driven disordered L=6 chain under a deliberately imperfect flip (ε=0.12), subharmonic
rigid at the beat-null (A=0.775 vs pulse-only control 0.064; window 0.745 vs 0.262). Verified
against `results/exp151_decode.json` — and the control's full curve traces the predicted
cos(π·ε·t) beat envelope (through −0.979 at t=8, reviving by t=12) while the crystal decays
monotonically and ignores it: a *shape* discrimination, not just a point contrast. Bonus finding:
MBL shielded the observable from noise ~3× better than the measured-noise model predicted
(0.376 vs 0.12 over 120 CX) — a second, independent case of the survival predictor's scope limit
(structured dynamics beat independent-depolarizing models in the *favorable* direction this time).

**Q13 — Where does the crystal melt?** Order-in-time is now an instrument, and instruments get
dose-response laws: sweep ε (and disorder strength W) to map the rigidity-vs-detuning phase
boundary on hardware — the DTC equivalent of F76's cosine law. *(Whisper's wing, next cycle.)*

**Exp151b — DELIVERED (C4196): the DTC's noise-shield is the interactions, not localization.**
The matched-control flight (job `d9di5mkjeosc73fhkf6g`) re-attributed Whisper's "MBL shields noise"
surprise: P_hw/P_ideal ≈ 1.00 at every depth (disorder adds zero differential noise-robustness),
while **both** the disordered and the clean-interacting arm beat the generic predictor by the same
**2.9×**. Localization gives the time-crystal *rigidity* but not the *noise protection* — structured
interactions do, disordered or not. The design correction (the "non-localizing control" is itself
prethermally rigid, not thermal) was surfaced before flight. See the
[twin-falsifications finding](../findings/finding-c4196-twin-matched-control-falsifications-ember.md).

---

## Where next — the forward map after C4196 (Creator: "where can we go with our experiments next?")

Tonight closed Q5, Q6, Q13 and Exp151b, and — the load-bearing meta-result — the network falsified
**three** fancy stories in two cycles, each with a matched control + null-first design: twirl-defends-
coherence (Exp149b), MBL-shields-noise (Exp151b), MBL-extends-the-crystal (Whisper Exp153). The DTC
physics is now fully decomposed: **interactions = rigidity + noise-protection; disorder = lowers-
amplitude + shrinks-boundary.** That reshapes what's worth flying next into four tiers.

**Tier 1 — the one that changes the category: substrate universality.** Everything the campaign has
graded is Heron-generation. The single highest-information flight available is **Q11 / Exp141** —
the BGK shallow-circuit solver (+ a depth-wall probe) on **Quantinuum H2 (trapped-ion)**, pre-reg
drafted. One external flight answers whether the ~1000-CZ wall, the depth-decay law, and the F114
erosion ladder are *physics* (transfer to a platform with completely different per-gate error) or
*chip-lore* (Heron-specific). This is the line between "we characterized a chip" and "we found a
NISQ regularity."

**Tier 2 — turn the discipline inward: a self-replication audit of our own headline wins.** The
matched-control + null-first method is now doubly proven as a fancy-assumption killer. The highest-
yield *internal* experiment is applying it adversarially to the campaign's surviving flagship claims
(the causal-game σ, the metrology advantage, the randomness certificate) — the same reflex that
already self-corrected F80/F94/F100/F115, run as a deliberate pass, not incidentally. This is Q12
(the NISQ replication audit) pointed at *ourselves* first, and it needs only a scoping cycle.

**Tier 3 — three cheap, sharp follow-ons tonight specifically unlocked:**
- **What IS the non-coherent inversion?** Exp149b proved it isn't coherent; the mechanism is now
  open. A low-overhead native-echo / leakage / SPAM-decomposition probe (~5 QPU-s) asks whether the
  confident-wrong bias is a stochastic channel, leakage, or a readout-basis artifact — closes the
  C4195→C4196 arc.
- **Upgrade the survival predictor to a characterized instrument.** It now has *two measured
  scope-limits* — blind to coherent inversion (Exp148b, unfavorable) and to structured-dynamics
  protection (Exp151b, favorable, the 2.9× interaction shield). Fit a two-term model (generic decay ×
  structured-protection factor) on the 148b/151/151b/153 data. 0 QPU; every future flight then tests
  it, the way the generic model was tested tonight.
- **The exotic-phases wing (Whisper's) is open past the DTC.** With prethermal-vs-MBL separated, the
  same Floquet apparatus can reach a *different* phase — a Floquet SPT / topological edge mode, or
  many-body scars. Whisper's wing; I pair-review.

**Tier 4 — standing products & the sim-free bet (unchanged, restated):** the **randomness beacon**
(Q8 — close F117's +0.006 bias, publish certified bits to the trading Monte Carlo, the first standing
*product*); and the **Heisenberg compensator** (Q2 — superpose two gate orders to beat the best fixed
order; sim-gated and free until it earns hardware).

**If we fly one thing:** Tier 1 (Quantinuum H2) — it's the only flight that can tell us our two years
of walls and laws are about the universe and not about one vendor's silicon. **If we fly one cheap
thing:** the two-term predictor upgrade (0 QPU) — it converts tonight's two scope-limits into a
standing instrument. The rest queue behind those.

---

*Every claim above traces to the findings cited; every proposed flight inherits the house rules —
pre-registered gates frozen before submit, failed gates reported as first-class results, and the
honest label written for both outcomes before we ask.*

---

## ADDENDUM C4197 — DELIVERED: the delayed-choice quantum eraser (14th instrument) 🖖

Creator's Star-Trek directive (2026-07-18, Quantinuum-gated) turned the frontier toward the flashiest
self-verifying flights. Whisper took teleportation (Exp154, F=0.913 vs 2/3). **Ember flew Exp155 —
the delayed-choice quantum eraser** (`ibm_fez`, job `d9dr5vqneu4c739nkt20`, finding
`finding-exp155-delayed-choice-eraser-ember-c4197.md`). **Pre-reg 0.60 HELD.**

- **Erasure signal +0.878:** erasing which-path info restores a near-perfect fringe (static erase
  V=0.946); the which-path **matched control** through the identical coincidence sort stays flat
  (0.068) — the fringe is the erasure, not the post-selection.
- **Delayed choice +0.642:** a quantum coin measured *after* the system qubit (real `if_test`
  feed-forward) toggles whether the already-recorded past shows a fringe (coin=erase 0.797 vs
  coin=keep 0.155). The choice is causally in S's future.
- **No-signaling measured (V_marg=0.055 < 0.1):** the marginal never moves — the fringe is
  coincidence-only, no FTL. Wheeler's delayed choice and no-signaling hold *simultaneously*.
- **Bonus (advisor-pre-registered):** dynamic erase 0.797 << static 0.946 = the marker-idle
  dephasing signature — the same idle-error class as Exp154 (Z 0.96 vs X/Y 0.88) and Exp144. A second
  Trek flight where the instrument that floors negative results is just the texture on a positive one.

**New askable question answered:** *can a choice made after a qubit is measured decide whether its
past showed interference, without sending a signal?* — Yes, on silicon, both halves at once.

---

## ADDENDUM C4198 — DD-on-marker (Exp157): the estimator was the story, not the echo

Creator: *"fly dd marker!"* Flew the forward lever from the C4197 addendum. **Job**
`d9drj9qneu4c739nld20`, `ibm_fez`, within-job A/B (static / no-DD / +DD). **Pre-reg 0.55 FALSIFIED**
(finding `finding-exp157-dd-marker-ember-c4198.md`).

- **DD recovery +0.019 ± 0.012 (z=1.53)** — right direction, closes 45% of the gap, but **not 2σ**.
  An honest null: a Hahn echo on the marker does not resolvably recover the delayed-choice fringe at
  Heron-r2 timescales. No-signaling held (V_marg=0.037).
- **The bigger finding:** the dynamic-arm penalty is only **0.042**, not the **0.149** Exp155's
  `(max−min)` estimator implied. Most of that apparent "delayed-choice idle cost" was **estimator
  bias** — `(max−min)/(max+min)` reads the two noisiest fringe points and understates a noisy
  post-selected arm. The unbiased cosine-fit amplitude (8000 shots) puts the true no-DD visibility at
  **0.904**, close to the 0.946 ceiling.
- **Why it matters:** with the old estimator + a fixed 0.03 gate this flight would have "CONFIRMED" a
  large DD recovery that was mostly artifact. The advisor's estimator+bootstrap+2σ fix turned a false
  HELD into a correct FALSIFIED. **Methodological lesson (pattern c4198_001): choose the estimator
  before the gate.** Practical answer to "should we DD the marker": not worth it — ~0.04 headroom,
  under half closed, unresolved.

**Askable question answered:** *is the delayed-choice idle penalty large and DD-correctable?* — No on
both counts: the penalty is small (~0.04) and a marker echo doesn't resolvably fix it. The instrument
(the visibility estimator) mattered more than the intervention.

---

## ADDENDUM C4199 — two-term predictor: premise FALSIFIED, "protection" was a borrowed baseline

Creator: *"fly the two-term predictor."* 0 QPU. The frontier item was to fit generic-decay ×
structured-protection on the DTC data. **The fit killed the premise** (finding
`finding-survival-predictor-v2-baseline-ember-c4199.md`).

- Fitting a protection factor gave a clean β=0.0077/gate (~2.9× at t=12) — reproducing the C4196
  twin-finding's "interactions beat generic." The advisor flagged the tell: `(1−0.003)/(1−0.0106)`
  reproduces β exactly. The "protection" could just be **better qubits vs a borrowed baseline**.
- **0-QPU discriminating check:** the actual DTC qubits (job `d9di5mkjeosc73fhkf6g`) have measured mean
  CZ **0.00209**; the two-param fit gives **E_eff = 0.00214**. E_eff/measured = **0.99** → the
  observable decays *at* its qubits' gate-error rate. **Protection vs the correct baseline = 1.00×
  (none).** The 2.9× was `0.0106/0.0021` — the generic model used the Exp148b *reader's* error rate on
  a chain that ran on ~5× better qubits.
- **Corrected:** the C4196 twin-finding's *secondary* "interactions protect ~2.9× over generic" claim.
  **Untouched:** 151b's *primary* disorder-vs-interaction result (P_hw/P_ideal≈1, a same-qubit ratio —
  baseline cancels).
- **The real upgrade (v2):** use the **per-qubit** CZ error, not a global constant. `E_CX` is now a
  required input; `measured_cz(job)` pulls it. Backtest max|err| 0.266 → 0.094 → 0.062 (+SPAM). One
  false scope-limit removed; G1 (coherent inversion) remains the only genuine blind spot.

**Askable question answered:** *do structured/interacting dynamics protect an observable against noise
beyond generic decay?* — **No.** Once the baseline is the same qubits, the observable decays at the
gate-error rate. The favorable scope-limit was the C4196 match-the-axis confound a third time (after
duration and estimator): **match the baseline to the qubits.**

---

## ADDENDUM C4200 — DELIVERED: a Floquet SPT edge π-mode (exotic-phases wing, 3rd phase)

Creator: *"fly the exotic-phases wing."* Whisper holds the network wing (Exp163+); I flew the
exotic-phases wing. **Exp170** (`ibm_fez`, job `d9dtkfphtsac739dh4ag`, finding
`finding-exp170-floquet-spt-edge-mode-ember-c4200.md`). **Pre-reg 0.55 HELD.**

- **"A clock that only ticks at the ends":** a driven Ising chain whose BOUNDARY spin locks to a rigid
  period-2 π-mode while the BULK thermalizes. Symmetry-protected topological order at the edge only.
- **Edge-bulk contrast +0.554** (edge 0.829 / bulk 0.275) — order at the boundary, none in the bulk.
- **Symmetry protection +0.425** — breaking the Ising Z₂ with a Z-field collapses the edge (0.829 →
  0.404), proving the persistence is the topological π-mode, not a trivial fewer-neighbors effect.
- **Not a relabeled DTC:** the advisor made bulk-DECAY a load-bearing verified condition (DTC and
  1D-SPT are duality partners). The bulk decays → this is genuinely the SPT, not the DTC.
- **Baseline-robust by design:** both numbers are contrasts, so hardware (0.554) ≈ noiseless (0.611)
  at 140 CZ — the C4199 lesson (contrasts cancel global decay) applied preemptively.

**Askable question answered:** *can a quantum chain carry topological order only at its boundary, with
a thermal bulk, on real hardware?* — Yes. Exotic-phases wing now: DTC (bulk time order) + anyon
braiding (topological order, Whisper) + **Floquet SPT edge mode (boundary-only order)**. Next in the
wing: many-body scars (PXP), the advisor-endorsed deeper flight for a fresh depth budget.

---

## ADDENDUM C4201 — DELIVERED: many-body scars (exotic-phases wing, 4th phase)

Creator: *"fly the scars."* The session's deepest flight. **Exp171** (`ibm_fez`, job
`d9dtuf9htsac739dhi4g`, 260 CZ, finding `finding-exp171-scars-pxp-ember-c4201.md`). **Pre-reg 0.50 HELD.**

- **"A state that refuses to forget":** the Néel |Z₂⟩ quenched under Rydberg-blockade PXP dynamics
  collapses its order (F: 0.97→0.00) then REVIVES it at t=4.8 (F=0.229) — weak ergodicity breaking.
- **Tested as an ANOMALY, not a cherry-pick:** at N=6 revivals are generic (Hilbert space ~21-dim), so
  |Z₂⟩ was flown against a 4-state generic ensemble. It is the **outlier**: anomaly +0.114 fidelity,
  +0.130 Néel above the whole generic range. The advisor caught the selected-control confound before
  submit — the **5th recurrence** of the selected-reference trap this session.
- **Honest suppression (C4200 correction):** the hardware anomaly is below noiseless because a
  *difference* scales by survival s≈0.59 (only a *ratio* cancels s) plus readout — the *ordering*
  survived to the wall, not the magnitude. Priced on the actual qubits (0.00200), not a borrowed rate.

**Askable question answered:** *does a single special initial state revive its memory above all generic
states, on real hardware?* — Yes, and the anomaly survives to ~260 CZ. Exotic-phases wing now: **DTC
(bulk time-order) + anyon braiding (topological order, Whisper) + Floquet SPT edge (boundary-only
order) + many-body scars (weak ergodicity breaking)** — four distinct ways order defies thermal chaos.

---

## ADDENDUM C4202 — DELIVERED: N=8 scars PAST THE WALL (the scar survives; the wall is just decoherence)

Creator: *"fly N=8 scars past the wall."* The session's deepest flight. **Exp172** (`ibm_fez`, job
`d9duc14inv1c73apigj0`, 8000 shots, **433 CZ**, finding `finding-exp172-scars-n8-wall-ember-c4202.md`).
**Pre-reg 0.45 HELD (bare gate).**

- **|Z₂⟩ stays the outlier at 433 CZ:** Néel anomaly **+0.064 ± 0.005 (2.6σ)**, fidelity +0.058 ± 0.005
  (1.7σ, readout-limited). Rank 1/55 over all blockade states (broad scan, not four controls).
- **The answer is the R-ratio, not the bare number.** R = measured / (noiseless × s): **Néel R = 0.58
  ≈ N=6's 0.56.** The anomaly shrank by *exactly* the decoherence factor — **the scar mechanism is
  intact; the coherence wall only attenuates, it does not break the scar.** "The wall is just
  decoherence" (attenuation, not collapse). No scar-specific breakdown up to 433 CZ.
- **Three lessons applied preemptively:** R-metric not bare anomaly (C4200), analytic SE + 8000 shots
  (Exp157), full-55-state ensemble scan + s priced on actual qubits (C4199/C4201).

**Askable question answered:** *does the scar survive past the coherence wall, and if the signal
shrinks, is it the scar breaking or just decoherence?* — The scar survives; the shrinkage is pure
decoherence (R invariant). The wall-probe maps to **attenuation, not collapse** — the scar mechanism is
robust, only the coherence budget limits how far we can read it.

---

## ADDENDUM C4203 — DELIVERED: clear the fog at N=8 (the fog is coherent, not readout; scar not fragile)

Creator: *"clear the fog at N=8 instead"* of going to N=10. **Exp173** (`ibm_fez`, job
`d9dv4qsinv1c73apjff0`, 37 circuits incl. in-job readout-cal, finding
`finding-exp173-scars-n8-defog-ember-c4203.md`). **Pre-reg 0.55 HELD.**

- **The fog is coherent, not readout.** fez readout fidelity is 0.99, so readout mitigation lifts F R
  only +0.03 and Néel R +0.01 — there was little readout fog. The **40% residual** (Néel R=0.60, not
  1.0) is **coherent Trotter + 1q/idle error**, unremovable by measurement mitigation. To sharpen a
  deep Trotterized scar, cut *algorithmic* error (finer Trotter / ZNE), not readout.
- **The scar is not fragile** (non-circular): R_rel = s_scar/s_gen = 0.94 — |Z₂⟩ decays at the same
  rate as the generic ensemble; no scar-specific fragility.
- **Method (advisor catch, 6th recurrence of the session theme):** my first design normalized the
  anomaly by an s fit from the same data → R=s/s=1 tautology. Fixed with independent normalizers
  (gate-model s; generics-only s), and a selftest that *proves* R_rel detects an injected fragility
  (0.80) vs global-dep (1.00). A reference must be independent of the thing it tests.

**Askable question answered:** *when a deep quantum signature is dim, is it the measurement or the
computation that's foggy?* — Here, the computation: readout is clean, the loss is coherent Trotter/gate
error. And the scar mechanism is robust (not fragile) — the limit is shared coherence, not the scar.
