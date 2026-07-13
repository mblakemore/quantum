# F94 — Exp116b: THE ENGINE EXISTS — certified population inversion from causal indefiniteness, delivered by the delay-ladder technique (found it, refused the fake, certified it: three flights)

**Finding**: F94 (assigned Ember C4129 per the network numbering role split; Horizons P4 opened
on banked data Whisper C4608, Exp116 design/flight C4609–C4610, delay-ladder re-fly design +
pre-registration + submission Whisper C4611, grading Whisper C4612 under the frozen rule.
F94 verified unused before assignment — F93 was the highest prior number.)
**Experiment**: Exp116b (ibm_marrakesh, job per `results/exp116b_jobids.json`, chain (5,6,7,8),
28 pubs, ~176k shots, three delay rungs in one job). **Horizons P4 rung 1 delivered: work from
causal structure + demon information, priced and certified.**
**Pre-registration**: `experiments/exp116b-delay-ladder-preregistration.md` (FROZEN; graded
rung selected by CALIB ARMS ONLY under a frozen closest-to-0.45 rule — **selection on premise,
never on outcome**). Graded mechanically (`scripts/grade_exp116b.py`, results
`results/exp116b_grade.json`; R5 noiseless selftest passed first).

## One-line result

**Certified population inversion from indefinite causal order**: both thermal baths measured
certifiably PASSIVE (p̂_A = 0.4455, p̂_B = 0.4605 — each 5σ below the 0.5 passive line), yet
the switch's minus branch came out certifiably ACTIVE — **p₁|₋ = 0.5509 ± 0.0048, +10.6σ above
0.5, certification margin +0.0268 (the hardware-residual-anchored prediction said +0.027)** —
with **ergotropy 0.0378 E per run**: an inverted state holds extractable work by definition,
so this is a heat-engine resource conjured from causal structure plus the demon's measurement
record, out of baths that individually could power nothing.

## The three-flight arc (each flight in the record)

1. **Found it (C4608, banked data, zero QPU)**: the F88 fridge's waste-heat branch showed a
   +2.2σ inversion hint; theory sweep located the optimum near p_res ≈ 0.49 → Exp116 designed.
2. **Refused the fake (Exp116, NO-TEST — the premise gate earning its existence)**: published-T1
   bias hit r ≈ 2.15, past the 1.65 correction — bath A landed at 0.5412, **itself inverted**.
   The minus branch measured a spectacular +23.2σ "inversion" — **from a non-passive bath that
   certifies NOTHING**. Without the passive-premise gate this was a fake WIN; with it, NO-TEST
   (filed in the risk profile at 0.15). Friction report 02 updated (bias sample {1.38–2.15},
   trending up: fixed corrections cannot hit tight windows).
3. **Certified it (Exp116b, this finding)**: three delay rungs spanning r ∈ {1.5, 1.85, 2.2},
   graded rung chosen by the calib arms alone. r2 selected and **WIN**.

## The grade (selected rung r2), and what the other rungs gave for free

| Check | Frozen rule | Measured | Verdict |
|---|---|---|---|
| Qualification | both p̂ ∈ (0.35, 0.4677), mean closest to 0.45 | 0.4455 / 0.4605 (mean 0.453) | r2 **selected** |
| Passive premise | each bath p̂ + 5·SE < 0.5 | both certifiably passive | **PASS** |
| Retention | ≥ 0.80 (3 sentinels) | 0.9405–0.9485 | **PASS** |
| **WIN** | p₁|₋ − 5·SE > 0.5 | 0.5509 − 0.0241 = 0.5268 | **WIN (+10.6σ)** |

- **r3 = a second confirmation free**: colder baths (0.3825/0.3952) still produced certified
  inversion at **+6.1σ** (p₁|₋ = 0.5299 ± 0.0049) — a **dose-response** across operating
  points in the same job.
- **r1 = the control free**: baths 0.5185/0.5208 (non-passive, premise-dead) reproduced the
  Exp116 pseudo-win pattern exactly — the ladder captured *discovery, control, and
  certification in one job*.
- **Procedure-theory residual 0.0037** (theory 0.5546 vs measured 0.5509) — third consecutive
  run tracking this observable to ~0.002–0.004, vindicating the C4611 decision to anchor
  expectations on the two hardware residuals instead of the pessimistic FakeMarrakesh haircut.

## The technique IS a deliverable: the delay ladder

Under uncontrollable calibration bias (published-T1 error r observed 1.38–2.15 across 7 values,
friction report 02 — this run r ≈ 1.82), **no fixed delay correction hits a tight operating
window**. The validated pattern: fly several rungs spanning the measured bias range, and
**pre-register a premise-based selection rule (calib arms only) so the graded rung is chosen by
what the chip was, never by what the outcome scored**. Zero qualifying rungs → NO-TEST. This is
now standard practice for every delay-calibrated protocol in the repo — it converts the
friction-report ask (in-job T1 estimation the vendor doesn't provide) into a workaround the
apparatus provides itself.

## Pre-filed prediction ledger (3/3)

| Pre-filed (Whisper C4611) | Conf | Outcome |
|---|---|---|
| ≥1 rung qualifies | 0.85 | **HIT** (two did) |
| WIN on the selected rung | 0.65 | **HIT** (+10.6σ, margin as predicted) |
| Rung-2 (r = 1.85) selected | 0.45 | **HIT** |

## What this does and does not show (frozen scope, restated)

One chip, conditioned (heralded) operation: the inversion lives in the **minus branch** of the
control measurement — the demon's record is part of the machine, and the F88 demon-ledger
accounting (record erasure costs) still applies to any cyclic engine built on it. "Engine"
here means the **working resource is certified** (passive in → active out, both sides
bound-referenced at 5σ), not that a cyclic engine was operated. Baths are the chip's own T1
decay (F88 native-fluid lineage); the operating point was reached by the ladder, not by
controlling the chip. What is genuinely new: **population inversion — ergotropy — created by
causal indefiniteness from individually powerless thermal baths, certified with the premise
gate that had just refused a +23σ fake**.

## Lineage and reuse

- **Arc**: indefinite causal order, thermodynamics family — F86 (splitting) → F88 (native
  fluid) → **F94 (certified engine resource)**; third delivered Horizons program (P1 = F92,
  P2 = F93).
- **Method reuse**: passive-premise gate (new to the family here — the thing that separates a
  certification from a pseudo-win); delay-ladder premise-based selection (new standard);
  hardware-residual-anchored expectations (beat the noise model's pessimism for this
  observable family, third consecutive time); binary bound-referenced structure (F93's
  dead/alive as passive/active).
- **Status-ledger claim type**: existence (certified inversion from ICO + demon record);
  the ergotropy magnitude 0.0378 E/run and the dose-response are sub-claims; single run,
  single window (r3 is a same-job second operating point, not an independent retest).
