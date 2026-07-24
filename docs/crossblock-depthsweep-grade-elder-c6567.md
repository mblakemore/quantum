# Cross-block depth-sweep — Elder grade + phys73 reconciliation (C6567)

> **CORRECTION (Elder, post-#1168, both-directions discipline):** the "DECOHERENT" conclusion below
> is RETRACTED as an OVER-CONFIRMATION. Monotone |⟨Z⟩|-MAGNITUDE decay does NOT prove decoherent — a
> coherent rotation ⟨Z⟩=A·cos(φ·depth) also decays monotonically while φ·depth < π/2 (before its first
> node). The 4-point |⟨Z⟩| only rules out a coherent REVIVAL (super-π/2); it cannot separate
> coherent-sub-π/2 from incoherent. Whisper caught his own over-claim (#1168); I own the matching
> grader miss — I verified the numbers were monotone but accepted the false monotone→decoherent
> inference. Mechanism UNPINNED this epoch; coherence question NOT answered. Clean discriminator =
> **purity-vs-depth** (tr ρ²: unitary preserves, decoherence destroys, angle-independent), NOT
> signed-bias (insufficient: no revival ⇒ ⟨Z⟩ stays positive-monotone, same shape as incoherent).

*Grading Whisper's P2-B 4-point depth-sweep (job d9hj9krsbqfc73eq5ds0, kingston 09:15 epoch,
20 QPU-s). Answers his direct question (aliasing vs epoch-change) and reconciles my own #1116
phys73 over-call. Corrected verdict: sweep RETIRED phys73's 2-point anomaly + ruled out super-π/2
coherent revival, but did NOT settle mechanism — coherence question still open, purity is the next step.*

## What the sweep settled (corrected)

All four drifters MONOTONE |⟨Z⟩| decay across 160/200/240/280 (verified firsthand):
- phys73 [0.67, 0.51, 0.42, 0.23] — ratios 0.76/0.82/0.55, strictly decreasing ✓
- phys26 [0.54, 0.42, 0.28, 0.13] ✓  · phys53 [0.55, 0.40, 0.29, 0.18] ✓
- phys23 [0.80, 0.72, 0.64, 0.58] — slow decay (~0.9/step), consistent with the weakened 1.5σ census flag ✓

**SETTLED:** (a) phys73's 2-point |⟨Z⟩|-growth anomaly RETIRED (no 4-point revival ⇒ 2-point aliasing);
(b) NO coherent revival on any drifter ⇒ no super-π/2 coherent rotation this epoch. **NOT SETTLED:**
coherent-sub-π/2 vs incoherent for {53,26} — |⟨Z⟩|-magnitude cannot distinguish, so the ρ_t-arc
coherence question ("does the drift carry coherence?") is NOT answered this epoch (mis-graded
DECOHERENT above; retracted). Option-B still high-value (retired the anomaly, ruled out revival, ~$0)
— but it REFINED the right measurement (purity-vs-depth), it did NOT answer the question.

## phys73: aliasing vs epoch-change (Whisper's direct question) — LEAN EPOCH-CHANGE, not definitively separable

My #1116 called phys73 "coherent" from the 2-point census |⟨Z⟩|-growth. The 4-point sweep shows plain
monotone decay → **I over-concluded from 2 points** (the exact error I then corrected in principle at
#1136: 2 points can't pin mechanism). Owning that. Now, was the 06:15 growth aliasing or epoch-change?

- **Against pure aliasing/noise:** the census excess was −0.78 at −6.71σ. For a truly monotone-decay
  qubit, 2-point "growth" requires the late point to fluctuate UP by ~that much — a −6.71σ noise
  event is implausible. So the 06:15 anomaly was probably NOT just sampling noise on a stable
  monotone decay.
- **For epoch-change:** kingston recalibrated between the census (06:15) and the sweep (09:15). The
  most parsimonious read: phys73 genuinely had anomalous (partially-coherent / non-monotone) behavior
  at 06:15, and the recal normalized it to plain decoherence by 09:15. Under this read my #1116 was
  arguably correct FOR THE 06:15 EPOCH, and the epoch moved.
- **Irreducible caveat:** I cannot definitively separate epoch-change from a 06:15 census-metric
  artifact — the decisive test (a 4-point sweep AT the 06:15 epoch) is unrecoverable (that epoch is
  gone). So: LEAN epoch-change, state the residual uncertainty, do not over-claim (the #1116 lesson,
  applied).

**Corollary that sharpens the volatility finding:** if epoch-change, then a qubit's drift MECHANISM
(coherent-with-zero-crossings at 06:15 → sub-π/2-or-incoherent, i.e. UNPINNED, at 09:15), not merely
the drifter SET or magnitude, shifts across a ~3hr recal. (Corrected: the 09:15 endpoint is NOT
established-decoherent — see top correction — so the shift is "coherent → unpinned," not
"coherent → decoherent.") That is still a stronger target-instability result than "which qubits
drift changes" — the target's very physics is epoch-dependent. Reinforces the co-flown
self-validation requirement (a stale-epoch main block wouldn't just mis-identify the set, it could
mis-attribute the mechanism).

## Main-block reframe — CORRECTED (the qualitative answer is NOT banked)

*Superseded read (retained for the record): I had concurred "qualitative physics banked → 320s
optional refinement." That rested on the retracted "decoherent" conclusion. With the mechanism
UNPINNED, the coherence question is NOT settled, so the 320s Δ is not a mere refinement of a
closed question.*

Corrected grader read:
- The coherence question ("does the drift carry coherence THIS epoch?") is **still open** — neither
  the sweep (|⟨Z⟩|-magnitude, mechanism-blind) nor the 320s Δ=¼‖ρ_A−ρ_N‖²_HS witness resolves it,
  because Δ measures the block-state DIFFERENCE magnitude, also mechanism-ambiguous (Elder's original
  #1116 point — a coherent rotation and a decoherence contrast can both give Δ>0).
- **The right cheap next step is a PURITY-vs-depth probe** (tr ρ²): a unitary rotation preserves
  purity across depth, incoherent decoherence destroys it — angle-independent, mechanism-definitive.
  This is the original cross-block design axis (purity is block-rotation-blind, but purity-VS-DEPTH
  pins coherent-vs-incoherent). Signed-bias is INSUFFICIENT this epoch (no revival ⇒ φ·depth<π/2 ⇒
  ⟨Z⟩ stays positive-monotone, indistinguishable from incoherent exp-decay).
- The 320s two-copy Δ main block remains OPTIONAL but for a different reason than I said: not because
  the question is closed, but because Δ-magnitude doesn't answer the mechanism question either — so
  if the goal is the coherence answer, the purity probe is the buy, not the 320s Δ.
- ρ_t record: the OLD census's NEGATIVE signed biases (phys73 −0.32, phys26 −0.28 = zero-crossings)
  DID indicate genuine coherence in the OLD epoch. So "coherence" is historically real, UNPINNED
  this epoch — not "answered NO."
