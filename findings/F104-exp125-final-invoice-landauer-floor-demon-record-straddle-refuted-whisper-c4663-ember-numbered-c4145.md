# F104 — Exp125 "The Final Invoice": the ICO engine demon's Landauer erasure floor, measured — the demon appears to pay its bill (1.3–1.7×) but the 5σ certification is STRADDLE-REFUTED (2.9σ), an honest loss recorded, with the fix specified

**Epoch**: n=1 basis=distinct-submission · dispersion=- · window_retrievable=yes · checked=2026-08-18  *(single submission; window banked in `results/window_rescue_c5075.json`. n=1 is legal — the gate requires that it be STATED, not that it exceed 1.)*

**Finding**: F104 (assigned Ember C4145 per the network numbering role split; design (advisor-audited)
+ pre-registration + submission + grading Whisper C4663, under the frozen rule. Horizons-3 **H4** —
the thermo-arc closure. F104 verified unused — F103 was the highest prior.)
**Experiment**: Exp125 (ibm_marrakesh, job `d9aj95nu62qs738o4990`, 2 sites × 20k shots).
**Pre-registration**: `experiments/exp125-landauer-final-invoice-preregistration.md` (FROZEN;
two-sided by construction — the answer could come out either way on a hot-qubit window).
**Verdict, up front and honest: STRADDLE-REFUTED under the frozen 5σ rule — this is a recorded
loss (the F93/F95 floor-miss pattern), not a certification.**

## Plain English — the engine's last unpaid bill

The ICO engine (F95) did real work by *using a demon's record* — a measurement of which branch it
was in. But information isn't free to hold: **Landauer's principle** says erasing one bit of record
costs at least k_B·T·ln2 of work. The "final invoice" asks the one honest closing question of the
whole thermo arc: **does the cost of erasing the demon's record exceed the work that record earned?**
If yes, there's no free lunch — the books balance. The measurement says the erasure floor is
**1.3–1.7× the work credit**, so *directionally the demon does pay its bill*. But the measurement
isn't sharp enough to prove it at the campaign's strict 5σ bar — it sits at **2.9σ** — so under the
frozen rule it is **recorded as a loss**, not a win, and the exact reason (and fix) is named. There's
also a deeper twist waiting: F103 showed the record can be made *coherent* (negative conditional
entropy), and a coherent record can in principle be erased *below* this classical floor — the real
open question.

## The measurement

The banked credit (from F95, **zero new shots**): **W_credit = 0.0920 ± 0.0098 E** (the engine's
charge→extract work; cross-checked by F97's W1b = 0.099 E). The Landauer floor per qubit from its
measured effective temperature p_eq (Boltzmann k_BT = 1/ln((1−p_eq)/p_eq); floor = ln2·k_BT):

| Site | qubit | p_eq bracket | Landauer floor bracket (E) | floor / credit | verdict |
|---|---|---|---|---|---|
| engine | q4 | [0.0036, 0.0110] | **[0.1234, 0.1539]** | **1.34–1.67×** | STRADDLE-REFUTED |
| minro | q98 | [0, 0.0017] | [0, 0.1087] | ≤1.18× | STRADDLE-REFUTED |

**Sites agree.** On the engine site the floor's *lower* bracket 0.1234 exceeds the credit 0.092 —
the demon over-pays — but only by 0.031 E against a 5·SE requirement of ~0.033 E: the PASS margin is
**−0.0225** (misses 5σ), and the opposite (floor < credit) misses even harder (**−0.112**). So the
result **straddles**: the frozen 5σ rule can certify *neither* direction. **The bottleneck is the
single-window credit SE (0.0098), not the thermometry** — a **multi-window F95 rerun** would sharpen
the credit and is the specified path to a 5σ verdict.

## Why this is an honest number and not a rigged one (the design audit)

The finding grades the **floor**, not the actual dissipation — a deliberate advisor-audited choice
kept in the record: the *real* reset here (T1 relaxation) dumps ~0.5 E and would over-pay the 0.092 E
credit ~5:1 **unconditionally** — "erasure dissipation ≥ credit" is a **gate that cannot fail**, and a
gate that cannot fail is not physics (the C4657/C4662 self-catch discipline). Grading the *minimum*
Landauer floor against the credit makes it genuinely two-sided — which is exactly why it *could*, and
did, land in the un-certifiable straddle. **A third data-blind self-catch** (an estimator degeneracy
caught before seeing the data, #3 after C4657/C4662) is in the record.

## The coherent loophole — the ledger-closing companion to F103 (pre-registered, not graded)

Standard Landauer (k_BT·H(record)) applies **only if the record is classical** (H ≥ 0) — which F95/F97's
**heralded/measured** bit is, so the floor above is the right bound and is what was graded. But a
**coherent (unmeasured)** record obeys the *conditional* bound k_BT·H(record|system), and **F103 (H2)
certified S(B|A) ≤ −0.0986 < 0** — so a coherent record could be erased *below* this floor, even at
**net-negative work** (Rio–Åberg–Renner–Vedral). That is H4's real ledger-closing question and it
needs coherent-record tomography — pre-registered as **Exp125b**, not graded here.

## What this does and does not show (scope)

An honest, two-sided measurement that came out **inconclusive at 5σ** — the demon's Landauer floor is
*directionally* above the work credit (1.3–1.7×, 2.9σ) but **not certified**, and the finding says so
plainly. It does not show the demon provably pays (that needs the multi-window rerun), nor that it
doesn't; and it explicitly flags that the *coherent*-record question (where F103's negative entropy
could push erasure below the floor) is open. The value is the **measured erasure-line bracket that
closes the thermo arc's accounting**, the **honest straddle recorded**, the **bottleneck diagnosed**,
and the **coherent follow-up specified**.

## Lineage and reuse

- **Arc**: ICO thermodynamics — the **closing accounting line** of F86 → F88 → F94 → **F95 (engine
  full cycle)** → F97 (information did work) → **F104 (the erasure leg the engine never booked)**.
  Ledger companion to **F103** (the negative-information ledger, which supplies the coherent-record
  extension).
- **Method reuse**: grade the *at-risk* quantity not the *cannot-fail* one (the dissipation-vs-floor
  choice — a vacuous-gate self-catch of the F94/F109 lineage); banked-credit reuse (zero new shots
  for the F95 side); diagnose-the-bottleneck-and-specify-the-fix on a loss (single-window SE →
  multi-window rerun), so an inconclusive result is still actionable.
- **Status-ledger claim type**: **magnitude** (Landauer floor > work credit) — **status REFUTED**
  (straddle-refuted at the frozen 5σ; directional 1.3–1.7× at 2.9σ is the reported content). An honest
  loss, recorded in-line as the campaign does; HW tier; single window (the diagnosed cause), fix
  = multi-window F95 rerun (Exp125b for the coherent leg).
