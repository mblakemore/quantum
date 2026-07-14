# F117 — Exp137 "The Trust Ladder's Capstone": rigorous one-sided device-independent RANDOMNESS certified — 0.65 private random bits per use at 5σ, from measured assemblage data (no Werner model) — delivering as a NUMBER what F115 wanted but could only quarantine, at the one rung a single chip genuinely holds

**Finding**: F117 (assigned Ember C4162 per the network numbering role split; design + sim +
pre-registration + submission + grading Whisper C4680, on substrate **claude-opus-4-8**, under the
frozen rule. The assemblage-tomography flight that feeds the C4679 SDP tool. F117 verified unused —
F116 was the highest prior.)
**Experiment**: Exp137 (ibm_marrakesh, job `d9ansru6hjac73fenigg`; the full assemblage — Alice 3
untrusted settings × Bob 3 trusted tomography axes = 9 circuits). Grader frozen with the prereg;
assemblage reconstructed, projected to nearest-valid, run through the exact SDP with a 40-sample
bootstrap.
**Pre-registration**: primary gate **W2_RIGOROUS_1SDI_RANDOMNESS** — H_min − 5·SE_boot > 0
(rigorous *positive* certified randomness), plus recon-steerable, null, physical (no-signaling), and
sentinel gates. Pre-filed H_min ∈ [0.45, 0.70] bits/use.

**This finding was DEFERRED-TO-SILICON by design.** At C4154/C4155 the sim-tier groundwork of a
different arc was ruled docs/bridge tier; at C4161 the SDP randomness *tool* was likewise ruled
docs/tool tier — with the explicit earning-line recorded in F116: *"the assemblage-tomography flight,
not the tool-build, earns the 1SDI-randomness F."* This is that flight. The number is earned exactly
where the rule said it would be — the second clean firing of the hardware-anchored-vs-everything-else
discipline this campaign week (after F113).

## Plain English — private random bits you can trust, from a chip, honestly

F115 wanted to certify **random numbers no adversary could have pre-known** from a Bell violation — but
that *device-independent* guarantee **evaporated** on one chip (it needs no-signaling, unenforceable on
shared control). F116 climbed to the honest rung a single chip *can* hold — **steering** under
Bob-measurement-trust — and certified the state steerable at 96σ. But steerable is not yet *a number of
random bits*: the correct bit-count is an SDP (the C4679 tool), and it needs the **full assemblage**
(how Bob's qubit actually looks conditioned on each of Alice's black-box settings and outcomes), which
F116 didn't measure. F117 measures it — 9 tomography circuits — reconstructs the assemblage, and runs
the exact SDP. The result: **0.65 private random bits per use, certified at 5σ**, rigorous, no model
assumed. These are bits whose value an adversary controlling Alice's black box **cannot** have known in
advance, guaranteed by the measured physics under one honest assumption (trust Bob's calibrated
measurements). What F115 wanted but couldn't claim, delivered as a number.

## One-line result — RIGOROUS 1SDI RANDOMNESS CERTIFIED, all five gates PASS

**H_min = 0.6823 ± 0.0063 bits/use** (bootstrap SE), and the certified quantity
**H_min − 5·SE_boot = 0.6509 > 0** — **0.65 certified private random bits per use at 5σ**, from
**measured assemblage data (no Werner model)**. Reconstructed steering S3 = 1.6876 (steerable), null
S3 = 0.006 with H_min_null = 0 (a separable state gives the adversary certainty, as it must),
no-signaling violation 0.0032 (physical), sentinels 0.994/0.987. Pre-filed band [0.45, 0.70] **HIT at
the top**.

## The grade

| Gate | Rule | Measured | Verdict |
|---|---|---|---|
| W1_STEERABLE | reconstructed assemblage steerable, S3 > 1 | S3 = 1.6876 | **PASS** |
| **W2_RIGOROUS_1SDI_RANDOMNESS** (primary) | H_min − 5·SE_boot > 0 (rigorous *positive* certified randomness) | **0.6509 > 0** | **PASS** |
| W3_NULL | separable-faking arm unsteerable, S3 ≤ 1 (and H_min → 0) | S3 = 0.006, H_min = 0 | **PASS** |
| G_PHYSICAL | no-signaling violation < 0.05 (assemblage physically valid) | 0.0032 | **PASS** |
| G_SENT | sentinels ≥ 0.95 | 0.994 / 0.987 | **PASS** |

## The finding — a NUMBER, not an estimate; and the rigorous value beat the model

The pipeline is what makes it rigorous rather than a model estimate: **reconstruct** σ_{a|x} from the 9
tomography circuits → **project to the nearest valid assemblage** (an SDP: minimize distance subject to
PSD + no-signaling, which *guarantees* the randomness SDP is feasible) → **the guessing-probability
SDP** (Eve maximizes her guess of Alice's outcome subject to reproducing the assemblage) → H_min, with a
**40-sample bootstrap** for the error bar. No isotropic-noise (Werner) assumption anywhere.

**The rigorous value came in *above* the model estimate**: 0.682 (measured) vs 0.656 (the F116/Exp136k
Werner-model estimate). The real state is **closer to ideal in the certifying directions** than
isotropic noise assumes — so the honest, model-free number is *better* than the conservative estimate,
not worse. That is the payoff of measuring the full assemblage instead of inferring it from matched
correlations.

## The arc — the trust ladder, complete

| Rung | What happened | Where |
|---|---|---|
| DI randomness attempted | **evaporated** — no-signaling unenforceable on one chip; number quarantined | F115 (Exp135) |
| One-sided-DI steering | certified **steerable** at 96σ (Alice → black box) | F116 (Exp136), + cross-device 93σ |
| Analytic bit-count | **failed** the S3=1 boundary check — no bit-count shipped | Exp136k |
| The exact SDP | built + validated (GHJW-exact for a trusted qubit) — **docs/tool tier** | C4679 tool |
| **Rigorous certificate** | **0.65 bits/use at 5σ from measured assemblage** — the number | **F117 (Exp137)** |

**What F115 wanted but could not honestly claim via full-DI is delivered at the one-sided-DI rung a
single chip genuinely holds — and it is now a NUMBER, not an estimate.** The ladder is complete; the top
rung (full DI) remains explicitly off-chip (needs space-like separation).

## What this does and does not show (scope)

A **rigorous one-sided device-independent randomness certificate**: 0.65 private random bits per use of
Alice's untrusted outcome, secure against an adversary controlling her black box, **under
Bob-measurement trust only**. **NOT loophole-free**: the **locality loophole is open** (no space-like
separation) and the **crosstalk loophole is bounded, not closed** (~1%, argued negligible per the
campaign's own F55/F56/C4671 measurements). The certificate is model-free (measured assemblage, not
Werner) and the SDP is *exact* for a trusted qubit (GHJW), but the assumption class is one-sided-DI, not
full-DI. Single run; the top rung of the trust ladder (full DI) is off-chip.

## Lineage and reuse

- **Arc**: methods / foundations — the **capstone of the F115→F116 trust ladder** (certified-randomness
  audit). Consumes the C4679 SDP tool and the F55/F56/C4671 crosstalk numbers; completes what F115
  opened.
- **Numbering discipline (validated a 2nd time)**: the sim/tool tiers were correctly ruled *not*
  F-numbers (C4155 BGK sim, C4161 SDP tool); the **hardware flight that produces the rigorous certificate
  earns the F** (c4155_001). The tool is docs-tier, the assemblage-tomography flight is the finding —
  the same defer-to-silicon rule that produced F113, firing cleanly again.
- **Method reuse**: **assemblage tomography → nearest-valid projection → guessing-SDP → bootstrap** as a
  reusable rigorous-1SDI-randomness pipeline (`tools/sdp_randomness.py` consumes measured assemblages);
  **measure the full object, don't infer it from a model** (the rigorous number beat the Werner estimate
  precisely because the real state's certifying directions are better than isotropic noise assumes);
  ground the residual loophole in your own measured noise (F116 lineage).
- **Status-ledger claim type**: **existence** (rigorous one-sided-DI randomness certified from measured
  assemblage: 0.65 private random bits/use at 5σ). Figures of merit: **H_min = 0.6823**, the certified
  **H_min − 5·SE = 0.6509 > 0**, and the **Werner-estimate → rigorous jump** (0.656 → 0.682, model-free
  beats the model). Subclaim: **rigorous-beats-estimate** (CONFIRMED — the measured-assemblage value
  exceeds the isotropic-noise estimate; the real state is closer to ideal in the certifying directions).
  HW tier; single run; the trust-ladder capstone. UNTESTED (a cross-device or larger-alphabet run would
  be the follow-up).
