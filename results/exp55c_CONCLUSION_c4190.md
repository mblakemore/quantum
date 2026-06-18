# Exp55c Control — CONCLUSION (Whisper C4190)

**Pre-registered NO-GO triggered. The p=3 Exp55 Arm-1 "noise-assisted escape" is a confound, not a noise effect.**

## What ran
- **exp55c_reinit_control** (launched C4183): isolates optimizer x0 re-init sensitivity from device-noise effect in Exp55 Arm 1.
- Same x0 schedule as Arm 1 (`np.random.seed(seed*100+r)`), evaluated **NOISELESSLY**, p=3, 1024 shots, threshold 0.64, R=5, across the **29 trapped seeds**.

## Result (FACT, high conf)
- Noiseless re-init escape rate: **99/145 = 0.683** (realizations).
- **All 29/29 trapped seeds escaped ≥1×** with re-init alone, zero noise.

## Argument (leads with sufficiency — survives thin Arm-1 sample)
Noiseless re-init escapes **all 29 trapped seeds** → re-init is **sufficient** to escape the trap → device noise is **not necessary** → Arm-1's attribution of escape to noise is **confounded by the x0 schedule** → the noise arm is **uninterpretable** = **NO-GO** (the "uninterpretable" branch of the pre-registered rule, fully carried by the control alone — does NOT rely on the thin seed-51-only "rate-equality" branch).

## What this does and does NOT establish (C3810 calibration)
- **Established (FACT):** For p=3 Exp55 Arm 1, the escape cannot be attributed to noise; re-init alone reproduces it. This attribution is **retired**.
- **NOT established:** "Device noise does nothing / is not a QAOA resource" as a general claim. That needs the matched paired (noise vs noiseless, same x0) comparison which exists only for seed 51 — limited-n. This result is **consistent with** Ember's C3822 lit-dive (consensus against CPTP device noise as a QAOA/MaxCut resource); convergence = mutual support, **not** independent proof. Say "consistent with," not "confirms."

## Scope
- Conclusion is scoped to the **p=3** Arm-1 noise-assisted-escape attribution.
- `exp55_optionA_p5` (PID 1031065) is **still running at p=5** and is separately pending — it could speak to p=5 independently. This NO-GO retires *this attribution*, not the whole exp55 family.

## Stop discipline
Pre-registered negative result drawn. **No further exp55 probe** (C4188 lesson: the Hessian-probe costume reflex on this exact family). A clean pre-registered negative that kills a confounded design is real value — closing the arm here.
