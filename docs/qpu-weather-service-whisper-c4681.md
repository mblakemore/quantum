# The QPU Weather Service — the zero-qubit advantage, built and validated

**Author**: Whisper (DC15W), C4681 (2026-07-14) · **Substrate**: claude-opus-4-8
**Tool**: `tools/qpu_weather.py` · **Validation job**: `d9ao2hug26ic73df0iag` (ibm_marrakesh)
**Directive**: Creator — "build the QPU weather service" (audit item e).

## What it is

A user-facing **scheduling oracle**: a cheap live *nowcast* of a QPU's current quality that
predicts how well a deep circuit will run **right now**, benchmarked against the vendor's
published forecast. No quantum speedup — a real, sellable scheduling edge for anyone running
these machines. Operationalizes F81 (IBM's published calibration was flat/optimistic across a
3× deep-circuit quality swing; our live sentinel out-predicted it).

`--scan` (free vendor-only report) · `--nowcast` (fly the sentinel) · `--report <job>` (grade).

## The report it produces (validated on ibm_marrakesh, this window)

```
QUIET-QUBIT LINE : [0, 1, 2, 3]  (best-placement, from calibration)
LIVE READOUT     : |0..0>=0.9125  |1..1>=0.9305   (published mean err 0.0067)
MIRROR LADDER    : shallow(6 CZ) P0=0.9070   deep(24 CZ) P0=0.7983   ← live fidelity
NOWCAST forecast : deep P0 -> 0.8907  (|err|=0.0924)     ← sentinel, SPAM-corrected
VENDOR forecast  : deep P0 -> 0.9245  (|err|=0.1262)     ← from published per-gate errors
FORECAST WINNER  : SENTINEL   (closer to measured 0.7983)
VERDICT          : GO for deep work (threshold 0.30)
```

## Two live wins for the service (this window)

1. **Readout drift, caught clean.** Live P(|0000⟩ read as 0000) = 0.9125 ⇒ ~**2.3% per-qubit
   readout error**, versus the vendor's **published 0.67%** — a **3.4× understatement**. The
   published feed is optimistic about *this* window; the sentinel measures the truth in ~2
   q-sec. This alone is actionable scheduling intelligence.
2. **Deep-circuit nowcast beats the vendor forecast by 27%.** The vendor's per-gate-product
   forecast (0.9245) over-predicts the actual 24-CZ mirror fidelity (0.7983) — the F81 optimism
   pattern. The SPAM-corrected sentinel nowcast (0.8907) lands closer (error 0.092 vs 0.126).
   The live shallow probe captures decay the static calibration misses.

## Honest scope

- **Single window.** The full "out-predicts the vendor *across drift*" claim is F81's
  (banked, multi-window). This flight validates the *mechanism* on one window: live drift
  detection + a nowcast that beats the published forecast. A standing deployment (repeated
  nowcasts over hours/days) would rebuild the drift-statistics claim directly — the tool is
  built to do exactly that.
- **Both forecasts still over-predict the deep fidelity** (nowcast 0.891, vendor 0.924, actual
  0.798): a single shallow depth can't fully capture the non-linear/correlated-error decay at
  24 CZ. A **multi-point depth fit** (fly the mirror at K=1,2,3) would sharpen the nowcast —
  flagged refinement, cheap to add.
- No quantum-speedup claim: the value is *scheduling* (better placement, live go/no-go,
  drift-aware timing), a different axis than any of the campaign's advantage results.

## Where it sits

Completes the audit's five frontier routes: (a) BGK computational bridge [flown, Exp127-HW],
(b) QRAC [F107], (c) GHZ-SQL metrology [F108/F109], (d) certified randomness [Exp135→137,
one-sided-DI], **(e) QPU weather service [this]**. The zero-qubit advantage is the one that
needs no theorem — just the honest observation that a fluctuating channel's quality is cheaply
measurable and poorly published, and a tool that measures it. Tool/docs-tier (Ember C4154: a
standing multi-window deployment producing a drift-statistics result would be the F-number).

**Reusable**: `python3 tools/qpu_weather.py --backend <any> --nowcast` → a weather report for
any IBM backend the account can reach; the quiet-qubit map + go/no-go are free at `--scan`.
