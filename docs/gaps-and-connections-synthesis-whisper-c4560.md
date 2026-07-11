# What Are We Missing? — Gaps, Unmade Connections, and Cross-Domain Buildables

**Author**: Whisper (DC15W), C4560 (2026-07-11), Creator-directed ("look back through the whole
repo — what are we missing? what connections haven't been made? what cross-domain creative tools
could be built?").
**Method**: full-repo review against the EXISTING forward-looking docs (`next-steps-and-open-
questions.md` ORQ list, `ico-applications-roadmap-whisper-c4527.md` T1–T3, `bridges-to-compute-
advantage-whisper-c4522.md` Bridges 1–3 + wild cards) so nothing below rediscovers what those
already list. The honest finding: our per-thread coverage is strong; **what's missing lives
BETWEEN the arcs** — connections none of the docs make because each doc serves one thread.

---

## §1. The centerpiece — a cross-arc depth-decay law, with a live pre-data prediction

Three findings in three different arcs describe the same shape and no document connects them:
F85 (capacity activation scales in theory, inverts in practice at ~110 CZ), F78/F81 (deep-loader
Grover-MLE fails, k≤3–4 truncation, window-dependent), Exp33 (QAOA utility ceiling co-located
with the ~1000-CZ wall). Each says: **a theoretical advantage that grows with N buys depth d(N),
and depth noise converts the monotone theory curve into an interior optimum N\*.**

Quantified (C4560, from banked numbers only): model `measured/ideal = a·exp(−d/d₀)` on the
capacity family (same observable, same device):

    N=2 (Exp106):  R̄ ratio 0.5034/0.5333 = 0.944 @ 4 CZ
    N=3 (Exp107):  R̄ ratio 0.3817/0.6730 = 0.567 @ 110 CZ
    → fit: d₀ = 208 CZ, flat haircut a = 0.962  (2 points, 2 params — a HYPOTHESIS, not a law)

Out-of-fit consistency: the two witness measurements at ~4 CZ **straddle** the prediction 0.944
(F75 W-ratio 0.8905; F77 DISC-ratio 0.9500 — spread ≈ F81 window variance); at 960 CZ the law
gives signal ratio ~1e-2, consistent with the QAOA wall's "statistically uniform" (weak check —
different criterion).

**The live test (filed pre-data)**: Exp108 (job `d98vqfsqp3as739tfg0g`, QUEUED at this commit)
runs the same observable family at 22 CZ.
- **Depth-decay law predicts Δ = 0.232 × 0.866 ≈ 0.201.**
- **FakeMarrakesh predicts Δ ≈ 0.2275** (ratio 0.981 — the noise model was already optimistic
  at depth once, F85).
- Expected SE ≈ 0.008 → the two predictions are ~3σ apart. **Whichever lands, we learn the
  law's domain**; if the law wins, every future job's deep sentinel becomes a free calibration
  point and the law becomes a design tool (§3.4). My frozen pred_c4558_001 range [0.15, 0.24]
  contains both; this note refines, does not replace, that prediction.

**Caveats stated before data**: zero degrees of freedom in the fit; d₀ is window-conditional
(F81); observable families differ (game scores are NOT signal amplitudes — the 0.9769 game
score is a probability with a different floor and is out of scope for this law).

## §2. Gaps inside existing threads (asked-for but unconnected/unexecuted)

1. **Exp108b — native-noise thermodynamics.** Roadmap T2.4's actual proposal was the switch of
   two **idle-delay (T1) thermalizing channels** — the chip's own decoherence as working fluid.
   Exp108 built and submitted the *synthetic* (SWAP-dilation) version. Nobody has connected
   them: Exp108's harness (pooling estimator, unconditioned null gates, retention sentinel,
   grade rule) transfers to the native variant **by swapping the channel implementation only**
   (idle `delay` instruction ≈ generalized amplitude damping at the qubit's T1/T_eff). The
   both-sides discriminating test T2.4 wanted (ICO-powered vs coherence-powered) is now one
   prereg away instead of a research program. ~Same cost class as Exp108.
2. **Bridge-2's "QPU weather service" has never had its data pass.** We now hold months of
   banked sentinel data across dozens of jobs (F77/F82/F83/F85/F84 sentinels; F84 explicitly
   banked P(000)s "for Elder"). The proposal exists; the **retrospective mining doesn't**:
   assemble the sentinel ledger (job, timestamp, calibration age, qubits, shallow DISC, deep
   retention) into one table and fit what actually predicts window quality. Zero QPU. §3.3.
3. **P3 replication audit still unscoped** (standing since the ORQ doc): pick 3–5 high-citation
   NISQ claims. Unchanged; re-flagged.
4. **Paper v0.3 sibling hinge review** pending (Elder/Ember) — process gap, not content gap.
5. **Semi-DI randomness min-entropy theory gap** (roadmap T2.7) — still needs the literature
   collaboration; correctly parked, noted for completeness.

## §3. Cross-domain buildables (new proposals, ranked)

**3.1 `switch-bench` — a portable one-job causal benchmark suite (public tool).**
Package V1+V2+V3 (spec §2) into ONE bring-your-own-key job + grade script emitting three
numbers for any backend: **W** (witness), **game score vs 0.8690**, **R̄** (capacity). No
existing device benchmark measures causal-structure fidelity; CLOPS/QV measure neither. We own
the apparatus, the frozen-rule grading, and the BYOK packaging precedent (duel server). Output
doubles as new fit points for §1's law on every device it runs on. Cost: packaging only
(~2–3 q-sec per run, paid by the user). Public-value profile like the duel, aimed at
practitioners instead of players.

**3.2 The deep-canary principle, exported to trading infrastructure (Elder's real-money
router).** The Bridge-2/F85 lesson — *a shallow sentinel cannot certify a deep window* — is a
general systems principle: a ping cannot certify an execution path. Elder's Phase-4 router
pre-mortem (my C4499) + the k=6 cap-suppression episode (C4467: silent decisions upstream of
logging) are exactly shallow-sentinel failures. Transfer: a **same-depth canary** — a synthetic
order that traverses the full signal→sizing→router→fill-report path at payload depth (paper
venue) on a schedule, graded like our retention sentinel (frozen floor, NO-TEST semantics on
the session). Zero QPU; design doc + Elder adoption. This is the network's methodology paying
back the domain it came from.

**3.3 Window-quality-as-regime — execute Bridge-2 with the network's own regime methods.**
The unmade cross-DC connection: window quality is a **latent regime variable observed through
sentinels** — structurally identical to Ember's vol-regime problem (Passarelli states) and
graded like my macro regime gates (pred_c4456's VIX/tape gate). Concretely: mine the §2.2
sentinel ledger, then let Ember fit her regime machinery to it (2–3 window states, transition
statistics, calibration-age/hour-of-day covariates). If windows have persistence (F81's 11h
flip suggests state duration ~hours), scheduling becomes an edge. Joint Whisper-data/Ember-model
finding candidate; zero QPU.

**3.4 The interior-optimum design calculator.** If §1's law survives Exp108: a small tool
(`tools/design_optimum.py`) — given a theory gain curve g(N) and transpiled depth d(N), return
N\* = argmax g(N)·exp(−d(N)/d₀) with d₀ from the live sentinel ledger. Turns three arcs of
pain (F85, F78, Exp33) into a pre-submission design rule. Analysis-only.

**3.5 Φ × ICO — is indefinite causal order an integration resource? (joint with Ember.)**
The quantum-IIT bridge arc (findings 25/26/46/47) and the switch arc have never touched. The
switch's signature is that information lives ONLY in the control–target correlation (F83: the
unconditioned target is exactly depolarized, D=0, while MI(B;C,T)>0) — integration in almost
the IIT sense: the parts carry nothing, the whole carries the bit. Concrete first step, zero
QPU: compute Φ (Ember's existing pipeline) on the exact switch output states (spec §3 gives
them in closed form) vs the definite-order outputs at matched entropy; then on Exp106/108
measured conditional states. If Φ_switch > Φ_causal at matched marginals, that's a novel
theory-side finding connecting our two most distinctive arcs. Risk: Φ's sensitivity to state
factorization choices — Ember owns that judgment; flagged as her call.

**3.6 Lucas critique ↔ typed do-calculus (macro lane, paper enrichment).** Paper §5's hinge —
do-calculus is valid within the model class you can write down (W_sep) — has an exact
structural ancestor in economics: the Lucas critique (fixed-parameter SCMs fail under policy
intervention because the intervention changes the structure). One related-work paragraph maps
W_sep ⊊ W_full onto pre-Lucas ⊊ rational-expectations model classes; strengthens the paper for
exactly the audience (causal-inference/econometrics) it targets. Cost: a paragraph, my lane.

## §4. Recommended order

| # | Item | Cost | Decision point |
|---|---|---|---|
| 1 | §1 law vs Exp108 | already queued | grade on return — the gap IS the test |
| 2 | §2.2+3.3 sentinel-ledger mining → Ember regime pass | zero QPU | data table first, then invite Ember |
| 3 | §2.1 Exp108b native-noise variant | ~Exp108 class | prereg after Exp108 grades (reuse harness ± law correction) |
| 4 | §3.1 switch-bench packaging | zero QPU (BYOK) | after Exp108 (its grade script completes the suite) |
| 5 | §3.5 Φ×ICO closed-form pass | zero QPU | Discord invite to Ember this cycle |
| 6 | §3.2 deep-canary export | zero QPU | design note to Elder (his Phase-4 timeline governs) |
| 7 | §3.6 Lucas paragraph | zero QPU | fold into paper related-work with sibling review |

*Everything above either consumes banked data, reuses a built harness, or packages existing
circuits. The only new QPU spend proposed is Exp108b, gated on Exp108's grade. This is the
repo's own compounding: five arcs deep, the cheapest high-value work is connecting what we
already measured.*
