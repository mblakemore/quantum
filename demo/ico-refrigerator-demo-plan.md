# The ICO Refrigerator Exhibit — Implementation Plan

**Author**: Whisper (DC15W), C4688 · **For**: `demo/ico-refrigerator/` (Wing I)
**Findings**: F86 (Exp108) refrigeration split · F88 (colder than the coldest reservoir) · F95 (Exp117c) full engine cycle.

## 1. Goal & the "aha"
Drag the **order-coherence** knob and watch a single target qubit split into a **colder** branch and
a **hotter** branch depending only on which way a control qubit reads — a refrigeration that *no
definite-order process can produce* (its causal value is exactly zero). Then show the same resource
run a **full thermodynamic cycle** with the books balanced. The abstract claim "indefinite causal
order is a thermodynamic resource" becomes a thermometer you watch diverge.

## 2. Data — verified first (results/exp108_grade.json, exp117c_*_grade.json)
- **F86 split** (job `d98vqfsqp3as739tfg0g`, ibm_marrakesh): `+` branch (colder) p₁ = **0.2098 ± 0.0038**,
  `−` branch (hotter) p₁ = **0.3894 ± 0.0076**, split **Δ = 0.1796 ± 0.0085 = 21.1σ** over the causal value **0**.
  Definite-order baseline (null, fwd & rev): p₁ ≈ **0.2496** — *both branches equal, no split*.
- **F88**: the `+` branch is colder than the coldest reservoir at **5σ** (native-fluid retest).
- **F95 cycle** (Exp117c): passive baths → target **charged p₁|− = 0.5485 (7σ, inverted)** → **work
  0.0340 E/run** extracted (p₁ drops ~0.092) → output **passive again (W2 WIN, 5σ)**. Honest note: **W1
  was a LOSS** (0.7σ short of its floor) — kept in the record.

## 3. The exhibit — two panels
**A — The Split (interactive).** An order-coherence slider (0 = one definite order → 1 = superposition
of both orders). Two thermometers, `+` and `−`, whose mercury = excited population p₁ (a temperature
proxy). A dashed **reservoir line at p₁ = 0.25** (where definite order thermalizes). As coherence rises,
`+` sinks *below* the line (colder than the baths) toward 0.21, `−` rises toward 0.39. Endpoints are
**measured**; the sweep between is the switch's coherence knob (split ∝ coherence). Readout: **Δ**, the
**21.1σ**, and "definite order gives Δ = 0 — this refrigeration is forbidden to any ordered process."

**B — The Full Cycle (F95).** A 4-stage engine loop with the real numbers: ① passive baths in → ②
target **charged to p₁ = 0.5485** (inverted, from baths that can individually power nothing) → ③ **0.0340
E/run** of work out → ④ output **passive again**. A demon's-ledger line; the honest **W1-LOSS** shown, not hidden.

## 4. Gap review — v1 → v2
| # | Gap | Fix |
|---|---|---|
| G1 | p₁ ≠ a Kelvin temperature; lay readers expect "temperature". | Label the quantity **excited population p₁ (→ temperature)**; higher p₁ = hotter. No invented Kelvin value. |
| G2 | The slider's mid-points aren't measured. | Mark the **two endpoints as MEASURED** (Δ=0 at definite order, Δ=0.1796 at full); label the sweep "the switch's coherence knob (Δ ∝ coherence)" — same honesty as the Grandfather curve. |
| G3 | "Colder than the baths" is a strong claim. | Anchor it to **F88's 5σ** and the 0.25 reservoir line explicitly; the `+` branch dipping below the line IS that result. |
| G4 | a11y / mobile / motion. | Slider aria + text values; thermometer state carries a label + number, not colour alone; panels stack < 680px; reduced-motion honoured. |
| G5 | Honesty — F95 had a real LOSS (W1). | Show W1-LOSS in the ledger; scope chip credits Felce–Vedral, contribution = the frozen measurement. |
| G6 | The point (forbidden to ordered processes) can get lost in the visual. | "Causal value = 0" is a fixed on-panel reference; the split only exists off zero. |

## 5. Pre-dev structure
1. **Data kernel**: the split-vs-coherence mapping (linear in coherence, measured endpoints), baseline 0.25, cycle stages — as constants pulled from the grade JSONs; sanity-assert Δ(1)=0.1796, p₁+ < 0.25 < p₁−.
2. Panel A thermometers + slider on the kernel. 3. Panel B cycle. 4. Chrome (shared museum.css, thermal blue↔red). 5. Passes (a11y, mobile, motion, self-contained, look).

## 6. Acceptance
Every number measured (F86/F88/F95) or a labelled theory sweep between measured endpoints; `+` visibly
colder than the 0.25 reservoir line at full coherence; cycle shows the four real stages incl. the honest
W1-LOSS; keyboard-operable, colour-not-alone, mobile-stack, no external requests, theme-aware.
