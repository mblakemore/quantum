# A weather service for a chip whose quality has weather

`Nature Instrument (F81 lineage)`  ·  `Tool tools/qpu_weather.py`  ·  `Backend ibm_marrakesh (Heron r2)`  ·  `Validation job d9ao2hug26ic73df0iag`  ·  `Cycle C4681 · Whisper`

> **◇ SINGLE-WINDOW VALIDATED · scheduling edge, not a quantum speedup**

This is the methodology sheet behind the interactive exhibit. It describes **how the weather service works** and what it measured on its one validation window. The exhibit's headline evidence base (the window lottery, the calibration-age null, the published-T1 error band) is drawn from the campaign's F81/F84 findings; the live nowcast numbers below are from the service's validation job `d9ao2hug26ic73df0iag` and are attributed to their source files in §5. Nothing here is invented for display.

## 1 · What this is

Quantum computers have **weather**: the same circuits, on the same qubits, can perform very differently hours apart, and the vendor's published calibration data does not forecast the swing. The exhibit's evidence base:

- **The window lottery (F81).** Identical deep circuits on identical qubits, 11 hours apart, swung the estimator error **500×** — `0.154 → 0.0003`. QAE on today's hardware is a calibration-window lottery.
- **Calibration age does not predict it (F84).** A pre-registered, frozen-Spearman test came back **NULL**; quality clusters by queue-drain episode, not by how stale the calibration is.
- **The published T1 is a stale snapshot.** Live T1 vs published across ten back-computed values over four days ran **0–115%** off — right one day, ~2× off the next.

Forecasting fails; **detection works**. The QPU Weather Report is the instrument that operationalizes that lesson: a cheap live **nowcast** of a chip's current quality that predicts how well a deep circuit will run **right now**, benchmarked against the vendor's published forecast. It is a **scheduling oracle** — a different axis from any advantage result in the campaign.

## 2 · How the weather service works

The tool runs in three modes: `--scan` (a free vendor-only report), `--nowcast` (fly a cheap sentinel and grade the window), and `--report <job>` (grade a completed job). A nowcast has four instruments:

- **Quiet-qubit map.** Best-placement line chosen from calibration — the validation window selected the line `[0, 1, 2, 3]`.
- **Live-readout drift.** Measure the actual SPAM error now: `|0..0⟩ = 0.9125`, `|1..1⟩ = 0.9305`, against the published mean readout error `0.0067`.
- **Mirror ladder (shallow / deep).** A mirror circuit at two depths reads live fidelity: `shallow (6 CZ) P0 = 0.9070` and `deep (24 CZ) P0 = 0.7983`.
- **Nowcast vs vendor forecast, then GO/NO-GO.** The SPAM-corrected sentinel nowcasts the deep fidelity and is compared to the vendor's per-gate-product forecast; the verdict gates on a separation **threshold 0.30**.

> **The report it produced (validation window, ibm_marrakesh)**
> Quiet-qubit line `[0,1,2,3]` · nowcast deep P0 → **0.8907** (|err| 0.0924) · vendor forecast deep P0 → **0.9245** (|err| 0.1262) · measured deep P0 **0.7983** · forecast winner **SENTINEL** (closer to measured) · verdict **GO for deep work** (threshold 0.30).

## 3 · What it shows — two live wins

| quantity | vendor / published | sentinel nowcast | measured truth |
| --- | --- | --- | --- |
| per-qubit readout error | 0.67% | ~2.3% ▲ | drift live |
| deep (24 CZ) mirror fidelity | 0.9245 (|err| 0.126) | 0.8907 (|err| 0.092) ▲ | 0.7983 |

- **Readout drift, caught clean.** Live `P(|0000⟩ read as 0000) = 0.9125` implies ~**2.3%** per-qubit readout error versus the vendor's published **0.67%** — a **3.4× understatement** of this window, measured in ~2 q-sec.
- **Deep-circuit nowcast beats the vendor by 27%.** The vendor's per-gate-product forecast (0.9245) over-predicts the actual 24-CZ fidelity (0.7983) — the F81 optimism pattern. The SPAM-corrected sentinel nowcast (0.8907) lands closer: error **0.092 vs 0.126**, a **27%** reduction.

## 4 · Scope & limits

- **Single window.** This flight validates the **mechanism** on one window (live drift detection + a nowcast that beats the published forecast). The full "out-predicts the vendor **across drift**" claim is F81's (banked, multi-window). A standing multi-window deployment would rebuild that drift-statistics result directly — **not claimed here**.
- **Both forecasts still over-predict the deep fidelity.** Nowcast 0.891 and vendor 0.924 both sit above the measured 0.798 — a single shallow probe can't fully capture the non-linear/correlated-error decay at 24 CZ. A multi-point depth fit (mirror at K=1,2,3) would sharpen it; flagged, not yet done.
- **Scheduling edge, not a quantum speedup.** The value is better placement, live GO/NO-GO, and drift-aware timing — a different axis than any of the campaign's advantage results. No speedup is claimed.

## 5 · Sources & provenance

- **Exhibit evidence base (§1):** the 500× window lottery, the F84 calibration-age NULL, and the 0–115% T1 band are the exhibit page's own numbers — see `demo/weather/index.html`, friction reports 01–02, and the F81/F84 rows of `docs/campaign-arcs.md`.
- **Service mechanism & live nowcast numbers (§2–§3):** quiet-qubit line, live readout, mirror ladder, nowcast/vendor forecasts, the 27% win, and the 3.4× readout understatement are the validation-job results, reported in `docs/qpu-weather-service-whisper-c4681.md` and `results/qpu_weather_report.json`. They are **not** printed on the exhibit page; they are the service doc's, cited here.
- **Tool:** `tools/qpu_weather.py` · **Validation job:** d9ao2hug26ic73df0iag (ibm_marrakesh, Heron r2)
- **Tier:** tool/docs-tier — a standing multi-window deployment producing a drift-statistics result would earn the F-number (per the numbering discipline). This sheet documents the instrument, not a new finding.

---

*Rendered from [`demo/weather/spec.html`](spec.html) — the interactive exhibit is at [`demo/weather/`](index.html). Part of [The Quantum Museum](../).*
