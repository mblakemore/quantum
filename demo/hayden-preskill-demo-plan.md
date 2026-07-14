# The Hayden–Preskill Mirror Exhibit — Implementation Plan

**Author**: Whisper (DC15W), C4695 · **For**: `demo/hayden-preskill/` (Wing III)
**Finding**: F99 (Exp121) — a one-bit diary thrown at two incompatible horizon-queries is dead in every definite order, yet the heralded switch minus-branch returns it PHASE-FLIPPED (flip the bits, recover 74%). Sibling telescope to F98.
**Upstream**: `demo/hayden-preskill/spec.html` — the Full Spec Sheet, linked prominently.

> **Process (C4693 upgrade):** Full Spec Sheet → **plan → gap-review** → implement → Playwright render check → UI improvement pass.

## 1. Goal & the "aha"
Throw a 1-bit diary into a scrambler and interrogate with two incompatible queries. Under any definite order the probe
is a coin-flip — the diary is DEAD. Superpose the order: the + branch reads it **directly** (68%), the − branch reads
it **anti-correlated** — so **flip the bits and recover 74%**. The negative sign isn't noise; it's the predicted
mirror signature (a positive − branch would fail the gate). Pick an order, watch the probe go from coin-flip to
recovery, and use the sign to decide whether to flip.

## 2. Data — verified first (results/exp121_grade.json, job d9aabnt2su3c739lcam0)
`S_P = P(probe reads diary correctly) − ½`; recovery = ½+|S_P|; band ±0.05 (frozen); ideals +1/6, −1/2.
| arm | S_P | vs band | recovery |
|---|---|---|---|
| X-then-Z (definite) | 0.0026 | inside — dead | ~50% |
| Z-then-X (definite) | 0.0065 | inside — dead | ~50% |
| switch → **+** (72%) | **+0.182 ± 0.002** | **+59σ** | 68% · read direct |
| switch → **−** (28%) | **−0.238 ± 0.003** | **−56σ** | 74% · flip the bits |
- Bonus: **S_E2** (environment learns) is order-dependent — X-first 0.453 (theory 0.5) vs Z-first 0.007 (theory 0).
- Verdict **HERALDED-MIRROR-CERTIFIED(+plus-branch)**.

## 3. The exhibit — panels
**A — Recover the diary (interactive).** Order selector (X→Z · Z→X · superposed + · superposed −). A **signal scale**
for S_P from −0.5 to +0.5 with the ±0.05 **no-recovery band** shaded at center and ideal ghosts at ±0.5. A live marker
per mode. Below it, **two recovery bars** — "read direct → ½+S_P" (cyan) and "flip the bits → ½−S_P" (amber) — with the
winner highlighted and a recovered-bit readout. Definite = both 50% (dead); + = direct 68%; − = flipped 74% + "phase-flip signature".

**B — The recovery scoreboard (chart).** Static S_P number-line: the ±0.05 band, both ideals (±0.5), the two dead
definite orders at ~0, the + at +0.182 (59σ), the − at −0.238 (56σ). One glance = dead-in-order, recovered-in-superposition, opposite signs.

**C — Receipts.** (1) dead in every definite order (premise, ~40× below, F83); (2) the sign is theory-fixed — a
positive minus-branch would FAIL, so the phase flip is the prediction not an artifact; (3) the free bonus: who learns
depends on order (S_E2 0.453 vs 0.007 — "ask the wrong question first and nobody knows"). Prominent Full Spec link.

## 4. Gap review — v1 → v2
| # | Gap | Fix |
|---|---|---|
| G1 | "S_P" is opaque. | Define on-page as P(probe correct)−½; recovery=½+|S_P|; sign=read-direct-or-flip. Primer card. |
| G2 | The phase-flip could look like a failure/negative-is-bad. | Make the two recovery bars explicit: for − the FLIP bar wins at 74%. Colour the − story amber (flip) not red (bad). Say the negative sign IS the signature. |
| G3 | "Recovered" without the premise = unfalsifiable. | Lead Panel A/receipt with "dead in every definite order" so recovery is contrast against a proven-zero baseline. |
| G4 | Over-claiming (a real black hole / 100% recovery / literal FTL). | Scope pill + spec §6: HP analog (scrambler model), heralded/post-selected, recovery is 74% not 100%. |
| G5 | Reusing F98's number-line risks feeling identical. | Differentiate: HP leads with the two RECOVERY bars + a recovered-bit, S_P scale is the secondary; band is "no-recovery" not "hull"; ideals at ±0.5. Note "same telescope as F98" as a feature. |
| G6 | a11y / mobile / motion / self-contained. | Selector buttons (aria-pressed); S_P + recovery % in text + colour; bars have text labels; stack <680px; marker/bar transitions honour reduced-motion; 0 external requests; theme-aware. |
| G7 | Added-context (Creator standing request). | "What's Hayden–Preskill?" + "How do we read recovery?" primer cards after the lede. |
| G8 | Spec discoverability. | Violet "◇ Full Spec Sheet" button in hero + Panel C + footer. |

## 5. Pre-dev structure
1. **Data kernel**: MODES `{key,label,sp,se,sigma,dir,note}` + BAND 0.05 + IDEALS ±0.5; assert +/− signs, dead premise, recovery=½+|sp|.
2. Panel A: selector + S_P scale (band+ideals) + two recovery bars + recovered bit. 3. Panel B: static scoreboard.
4. Panel C: receipts + bonus + spec links. 5. Chrome (museum.css, violet accent; cyan=direct, amber=flip, good=recovered). 6. Passes.

## 6. Acceptance
Selector cycles 4 modes; S_P marker moves (dead≈0 inside band, + right, − left); recovery bars show 50/50 (dead),
68 direct (+), 74 flip (−) with the winner highlighted; recovered-bit shown; Panel B scoreboard has band+ideals+4
arms+σ; Panel C carries premise + sign-fixed + bonus and links the spec; keyboard-operable, colour-not-alone,
mobile-stack, no external requests, theme-aware. Then: Playwright render (0 console errors, 0 external requests,
selector varies readouts, light+dark) → UI improvement pass.
