# The Negative Energy Exhibit — Implementation Plan

**Author**: Whisper (DC15W), C4697 · **For**: `demo/negative-energy/` (Wing III)
**Finding**: F97 (Exp119b) — first certified sub-ground-state (negative) LOCAL energy on a chip via coherent extraction. E_B = −0.0547 (12σ below vacuum); the correlation is the active ingredient; conservation intact (Alice pays).
**Upstream**: `demo/negative-energy/spec.html` — the Full Spec Sheet, linked prominently.

> **Process (C4693 upgrade):** Full Spec Sheet → **plan → gap-review** → implement → Playwright render check → UI improvement pass.
> **Wing III accent = violet.** neg/sub-vacuum = violet; injected/positive = amber; certified = good.
> **New card** — no lobby card exists yet; ADD one to Wing III (6th Horizons-2 question).

## 1. Goal & the "aha"
The vacuum is the energy floor — you can't normally go below empty. But entangle region B with a distant A, act on A,
and B's LOCAL energy can dip BELOW its own ground state: negative energy, the exotic-matter sign. Nothing is broken —
Alice pays energy in (E_A>0) far exceeding Bob's negative reading; only Bob's local patch reads sub-vacuum. And the
correlation is the ACTIVE ingredient: the same op without it INJECTS energy. Pick a protocol, watch Bob's energy
thermometer dip below the vacuum line.

## 2. Data — verified first (results/exp119b_grade.json, job d9a9sp2f47jc73a9vurg)
Readout-corrected E_B, vacuum floor = 0:
| protocol | Bob E_B | Alice E_A | vs floor |
|---|---|---|---|
| ground (reference) | +0.045 ± 0.005 | +0.011 | at floor |
| **QET (correlated)** | **−0.0547 ± 0.0046** | — | **below · 12σ** |
| same op, no correlation | +0.157 | +0.71 | injected |
- 5σ certified bound: **E_B ≤ −0.0319** (conservative — bias only pushes UP → true energy more negative).
- V2 below ground: −0.100 ± 0.007 = 14σ. V3 correlation-active: −0.203 ± 0.0097 = 21σ. Gates V1/V2/V3 PASS, G0 no-test did not trigger.
- Verdict **NEGATIVE-LOCAL-ENERGY-CERTIFIED(coherent)**. Scope: coherent leg; LOCC teleportation headline FAILED (feedforward tax 0.092 E).

## 3. The exhibit — panels
**A — Below empty (interactive).** A protocol selector (ground · QET-correlated · same-op-no-correlation). A VERTICAL
energy thermometer for Bob's site: a bold **vacuum floor line at 0**, a shaded **sub-vacuum region below**, and a
diverging bar from 0 to E_B (up=injected amber, down=negative violet). The 5σ certified bound (−0.0319) marked.
Readout: E_B + state (below-empty ✓ certified / at ground / injected). A small **conservation ledger**: Alice +0.71
vs Bob −0.055 → global positive.

**B — The energy scoreboard (chart).** The three protocols on one energy axis with the vacuum floor at 0, the 5σ
bound line, and σ callouts (12σ below zero, 21σ vs the uncorrelated control). One glance: only QET dips below the floor.

**C — Receipts.** (1) conservative bound — bias only pushes UP, so true energy is MORE negative (5σ ≤ −0.0319 < 0);
(2) correlation is the active ingredient — kill it and the same op injects +0.157 (21σ), not trivial cooling;
(3) conservation on the books — Alice pays +0.71 in. Scope pill carries the failed LOCC headline (honesty). Spec link.

## 4. Gap review — v1 → v2
| # | Gap | Fix |
|---|---|---|
| G1 | "Negative energy" invites free-energy / FTL misread. | Primer + warn callout: conservation intact, Alice pays; negativity is LOCAL and relative to the vacuum floor, borrowed against entanglement. Not perpetual motion. |
| G2 | "Below ground / vacuum floor" is abstract. | The thermometer makes 0 = "empty / vacuum floor" a bold line and shades the sub-vacuum region; the bar visibly dips below it for QET only. |
| G3 | Could look like trivial cooling. | Include the no-correlation control as a selectable protocol that INJECTS energy (+0.157); receipt 2 names the 21σ gap = correlation is the active ingredient. |
| G4 | Over-claiming a robust/complete result. | Scope pill + spec §6: coherent extraction only; the LOCC teleportation headline FAILED (feedforward tax); reported as a kept miss. Certified BOUND not point estimate. |
| G5 | "12σ below zero" vs "14σ below ground" vs "21σ vs control" easy to muddle. | Use each in its own place: thermometer/verdict = 12σ below vacuum; Panel B = the three arms; receipts = 21σ control gap. Label each σ with its comparison. |
| G6 | a11y / mobile / motion / self-contained. | Selector buttons (aria-pressed); E_B + state in text + colour + word; thermometer bar has value label; conservation ledger in text; stack <680px; bar transition honours reduced-motion; 0 external requests; theme-aware. |
| G7 | Added-context (Creator standing request). | "What is negative energy?" + "Isn't that a free lunch?" primer cards after the lede. |
| G8 | Spec discoverability. | Violet "◇ Full Spec Sheet" button in hero + Panel C + footer. |

## 5. Pre-dev structure
1. **Data kernel**: PROT `{key,label,eb,se,ea,sign,note}` + FLOOR 0 + BOUND −0.0319; assert QET<0, control>0, V3 gap 21σ.
2. Panel A: selector + vertical thermometer (0 line, sub-vacuum shade, diverging bar, bound mark) + readout + conservation ledger.
3. Panel B: static energy scoreboard. 4. Panel C: receipts + spec links. 5. Chrome (museum.css, violet; neg=violet, pos=amber, certified=good). 6. Passes.

## 6. Acceptance
Selector cycles 3 protocols; thermometer bar dips below the 0 line for QET (violet), sits at floor for ground, rises
(amber) for the control; readout shows −0.0547/+0.045/+0.157 with correct state; 5σ bound marked; conservation ledger
shows Alice +0.71; Panel B has floor + bound + 3 arms + σ; Panel C carries conservative-bound + active-ingredient +
conservation and links the spec; keyboard-operable, colour-not-alone, mobile-stack, no external requests, theme-aware.
Then: Playwright render (0 console errors, 0 external requests, selector varies readouts, light+dark) → UI improvement pass.
