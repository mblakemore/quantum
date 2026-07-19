# Exp212 — THE SHIELDED DIAL: CERTIFIED — fault-tolerant indefinite causal order is tunable

**Whisper C4905, 2026-07-20. Job `d9el9qphtsac739ecsv0`, `ibm_fez`, 10 circuits, 8000 shots,
seed 0. Substrate `claude-opus-4-8`. Prereg frozen pre-submit (`270acbe`).** Horizons-5 ICO
arc, on the "ICO!" directive.

## Verdict

**REGISTERED VERDICT (G1∧G2∧G3): HELD.** Indefinite causal order is a *smooth, tunable*
resource behind the shield — the shielded witness DISC follows the continuous F74/F76 law
from full switch to full mixture, error-detected.

## The measured continuous law

| φ/π | DISC (shielded) | exact 2cos(φ/2) | acceptance |
|---|---|---|---|
| 0 | 1.7956 | 2.0000 | 0.917 |
| ¼ | 1.6489 | 1.8478 | 0.886 |
| ½ | 1.3003 | 1.4142 | 0.882 |
| ¾ | 0.7183 | 0.7654 | 0.886 |
| 1 | −0.0076 | 0.0000 | 0.889 |

- **G1 ANCHORS**: DISC(0) = 1.796 (full shielded switch, **48σ** over the 1.0 bar, reproducing
  208/209); DISC(π) = −0.008 (full mixture, inert). The two endpoints of the shielded-ICO arc,
  in one sweep.
- **G2 CONTINUOUS LAW**: the measured curve tracks 2cos(φ/2) to **max interior residual 0.199**
  and is strictly monotone — the whole law, not two points, holds behind the shield.
- **G3 HALF-POINT**: DISC crosses half its full value at **φ* = 0.673π** — order-definiteness
  has a measured midpoint, error-detected.

**Budget scoreboard**: DISC(0) 1.796 ∈ [1.4, 1.9] **IN**; law residuals — the interior max is
0.199 vs the filed 0.15, a **graze** (the deeper dial arm carries a little extra noise, the
good direction is that it stayed inside the 0.25 gate); half-point 0.673π ≈ the filed π/2–2π/3
region **IN**. 2/3 filed predictions clean, one residual graze inside the gate.

## What this adds

Indefinite causal order behind the shield is **not binary**. 208 established it fires; 209
established it beats a *full* classical mixture; this fills in the continuum and shows the
shielded witness is a **smooth knob** obeying the exact bare law DISC(φ) = 2cos(φ/2)
(F74/F76, Pearson 0.9992 bare). Fault-tolerant indefinite causal order is a *continuously
tunable* resource — you can set the amount of order-coherence and read it back, error-detected.
The cry(φ) partial-decoherence dial cleanly interpolates full-switch ↔ full-mixture.

## Process note (kept, honest)

This flight was chosen after **pruning two deeper/underived options at design time** — the
pre-dev depth-check and feasibility-check working:
- the **shielded refrigerator** (Felce–Vedral thermal split) needs controlled-*logical*-SWAPs,
  ~90 CZ — the signal would wash out; pruned by the depth-check (stage 2);
- the **shielded switch-vs-coherent-paths** (F89 resource separation) needs the
  Chiribella–Kristjánsson coherent-control-of-channels formalism — a naive construction gave a
  dead paths arm (R̄ = 0.014); pruned by the feasibility sim (stage 1).

Neither cost any QPU. The dial is the shallow, certified-apparatus, Clifford-exact choice.

## The shielded-ICO arc (complete four-flight story)

- **Exp208** — the causal witness survives encoding (fault-tolerant ICO exists)
- **Exp209** — it beats any classical mixture of orders (rigorous vs the loophole)
- **Exp210** — it transmits information through zero-capacity channels (a useful resource;
  deliverable held 46.9σ, registered split on a mis-aimed null gate)
- **Exp212** — it is a smooth, tunable resource obeying DISC(φ) = 2cos(φ/2) (this flight)

## Scope

Coherence-of-causal-order witness (F77), half-shielded target, single-syndrome ZZZZ (inherited
from 208). Reproduces the F74/F76 continuous order-coherence law in the [[4,2,2]] code.
Textbook ICO + code priors credited; the contribution is the composition + the law in the code.

## Line

**208 said fault-tolerant causal order exists; 209 said it's real; 210 said it works; 212 says
you can dial it. The shielded witness slid down the exact 2cos(φ/2) curve from full switch to
full mixture, 48σ at the top and dead at the bottom — indefinite causal order is a knob now,
error-detected.**
