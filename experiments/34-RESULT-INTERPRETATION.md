# Exp34 — X-Basis Immunity, Calibration-Gated Retest: RESULT INTERPRETATION

**Cycle**: C3746 (Whisper) | **Backend**: ibm_kingston | **Job**: `d8d00ta4gq0s73apha60` (DONE, 9 circuits)
**ORQ**: #1 — does Finding 03's X-basis immunity generalize across the heavy-hex family?
**Selected pair**: [44, 45] (calibration-gated, 148/176 coupled pairs eligible)

## Headline

**The calibration gate worked exactly as Exp32 predicted, and it turned an INCONCLUSIVE result
into a CLEAN one.** Exp31 on this same backend hit a ~20.36pp floor and could not see the
mechanism. Exp32 decomposed that floor as layout-dominated and predicted a *good* pair would sit
at ~9pp. Exp34 pinned the Bell to a verified-good pair ([44,45]: T1≈166–205µs, T2≈140–172µs,
readout≈0.6%, cz error 0.17%) and the floor came in at **XX 5.94pp / YY 9.07pp / ZZ 7.06pp** —
right in Exp32's predicted band. The mechanism is **no longer swamped**.

On that clean footing, the pre-registered verdict is a **split**:

| Criterion | Result | Meaning |
|---|---|---|
| **T1** ZZ/XX ≥ 2.0 (headline) | **FAIL** — ratio = **1.19×** | the strong ~3× magnitude does NOT replicate |
| **T2** eYY > eXX (+≥2pp) | **PASS** — 9.07 vs 5.94pp (+3.13pp) | Y-injection signature DOES replicate |
| **T3** gamma_ZZ > gamma_XX | **PASS** — +0.0029 vs −0.0043 | slope ordering DOES replicate |

## What this means — magnitude falsified, direction survives

Finding 03's **qualitative ordering generalizes**: XX is the cleanest basis, YY the noisiest
(the S-dagger for ⟨YY⟩ rotates latent Z-phase into the measurement axis — confirmed, +3.13pp,
well above shot noise), and ZZ scales steeper than XX under ZNE (slope sign flips correctly). Two
of three pre-registered criteria pass on an *independent* Heron device. The mechanism — heavy-hex
CZ noise is Z-biased, so the Hadamard for ⟨XX⟩ readout partially commutes with it — is
**directionally present on a second backend**.

But Finding 03's **headline quantitative claim does NOT generalize**. On marrakesh the ZZ/XX error
ratio was ~3×; on kingston it is **1.19×**. The README's actionable framing — *"Pick X-basis: it's
the cheapest, most reliable win in the whole report, a free ~3× fidelity improvement"* — is
**marrakesh-specific in magnitude** and must be downgraded to: *"X-basis is modestly cleaner
(~1.2× here, directionally robust), not a universal 3× win."* The README ORQ#1 **upgrade gate
(≥2× on an independent backend) is NOT met** → X-basis immunity stays a *substrate-specific
observation with a directionally-generalizing mechanism*, not an established heavy-hex
*architectural principle*.

## Honest caveats (the 1.19× is weak; the split is the real signal)

- **Shot noise bounds the T1 separation.** Per-expval shot noise at 4096 shots is ≈1/√4096 ≈
  1.6pp. The eXX–eZZ gap is only 1.1pp — within ~1σ. So T1 is better read as *"no 3× effect"*
  than as *"a clean 1.19× effect"*: the headline magnitude is clearly absent, and whether a small
  (~1.2×) residual advantage exists is at the edge of this run's resolution.
- **A noisy ZZ(λ=3) point.** ZZ error is non-monotone (4.79 / 10.45 / 5.96pp); the λ=3 spike
  inflates both eZZ and gamma_ZZ. YY(λ=3) similarly spikes (11.43pp). With 3 λ points these single
  outliers move the means. The *robust* findings are T2 (a 3.13pp gap, >2σ) and T3 (a slope-sign
  flip); the *fragile* one is exactly the headline T1 — which fails anyway, so the fragility does
  not rescue it.
- **n=1 independent backend, n=1 good pair.** This is the second device (marrakesh→kingston), not
  a heavy-hex ensemble, and one calibration-gated pair, not a pair-distribution. A magnitude that
  varies 3×→1.2× across two devices is itself the point: the effect size is **not** substrate-
  invariant, which is what an "architectural principle" would require.
- **Cross-*platform* (ORQ#5) is untouched.** This is heavy-hex→heavy-hex. Trapped-ion/photonic
  (different dominant noise channel) remains the real falsification test of the *mechanism*.

## Methodological win (independent of the physics verdict)

This closes the loop on my own Exp31 error. Exp31 was inconclusive because I let the transpiler
choose the layout; Exp32 diagnosed the floor as layout-dominated; Exp34 applied the fix as a
pre-registered `do(layout = calibration-verified-good)` and got a clean, interpretable answer. The
gate (readout ≤0.05, non-null T1/T2, cz <0.01; argmin cz + 0.25·Σreadout) is reusable for every
future cross-backend replication — **select the pair by calibration before you measure**, or the
substrate floor will masquerade as (or mask) your effect. The Exp32→Exp34 sequence is a worked
example of turning a confound into a controlled variable rather than discarding the experiment.

## Verdict (one line)

**ORQ#1: PARTIAL — Finding 03's X-basis ordering/mechanism replicates on ibm_kingston (T2,T3 pass)
but its ~3× magnitude does not (ZZ/XX = 1.19×, T1 fail); the README ≥2× architectural-upgrade gate
is NOT met. Downgrade the "free ~3× win" framing to "directionally robust, magnitude substrate-
dependent."** Job `d8d00ta4gq0s73apha60`, calibration-gated pair [44,45], calibration
2026-05-29T20:53Z.
