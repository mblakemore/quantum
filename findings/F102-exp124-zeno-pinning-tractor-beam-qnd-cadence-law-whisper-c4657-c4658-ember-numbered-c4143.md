# F102 — Exp124: "The tractor beam" — measurement pins a qubit against a full π-rotation (92σ), and the QND-corrected Zeno cadence law matches to 0.5%; the completion of Horizons-2, six-for-six

**Epoch**: n=1 basis=distinct-submission · dispersion=- · window_retrievable=yes · checked=2026-08-18  *(single submission; window banked in `results/window_rescue_c5075.json`. n=1 is legal — the gate requires that it be STATED, not that it exceed 1.)*

**Finding**: F102 (assigned Ember C4143 per the network numbering role split; design + sim +
pre-registration + submission Whisper C4657, frozen grading C4658, under the frozen rule.
Horizons-2 Q6 — **the last one; with it the program is complete, six of six.** F102 verified
unused — F101 was the highest prior.)
**Experiment**: Exp124 (ibm_marrakesh, job `d9ai9ku6hjac73fefdeg`, 180k shots; **single qubit —
zero two-qubit gates, a first for the campaign and its cheapest, shallowest flight**). Grader
frozen *with* the prereg (R2 synthetic-counts selftest 4/4 before hardware grading).
**Pre-registration**: `experiments/exp124-zeno-preregistration.md` (FROZEN; a design correction
owned *at design time* — see scope).

## Plain English — the quantum Zeno "tractor beam"

"A watched pot never boils." The quantum version — the **Zeno effect** — is real: measure a
quantum system often enough and you *freeze* its evolution. Here a qubit is driven by a full
**π-rotation**, which would flip it from |1⟩ to |0⟩ with certainty if left alone. Instead we
**watch it** at cadence N (measure, nudge, measure, …). Unwatched, it flips — survival ≈ 0.
Watched, it *stays* — and the more often you look, the tighter you hold it, following the law
**P = [cos²(π/2N)]^N**. That is the "tractor beam": *measurement itself* holds the state in place
against coherent evolution. The one genuinely new thing here is not the Zeno effect (textbook) but
that, once the small cost of each measurement is divided out, the cadence law matches to **half a
percent** — *and* that watching too fast starts to cost more than it holds, so there is an
**optimal grip cadence**, and we measured where it sits.

## Design correction, owned first (the honest core of the scope)

The Horizons-2 sketch said "pin against T1 decay" — **physically wrong**, and corrected at design
time: Markovian T1 decay is exponential and **measurement-cadence-invariant**, so no amount of
watching slows it; Zeno protection needs the *quadratic short-time* dynamics of **coherent**
evolution. So the honest claim class is **"measurement holds a state against coherent evolution at
a certified strength,"** not "measurement beats thermodynamics." The quantum Zeno effect itself is
credited as textbook physics; the contribution is the frozen-graded, QND-corrected law match and
the measured watch-cost frontier.

## One-line result — ZENO-PINNING-CERTIFIED (+ cadence law)

**W_TRACTOR**: watching holds the qubit against the full π-rotation — **P(pinned, N=8) = 0.644 vs
P(unwatched) = 0.020, separation 0.624 ± 0.0035 = 92σ over the 0.3 bar**. **W_CADENCE**: watch
faster, hold tighter — **P(pinned, N=8) − P(pinned, N=2) = 0.398 ± 0.0046 = 87σ**. Predictions
0.92 / 0.90 both **HIT**.

## The quantitative jewel: the QND-corrected cadence law to 0.5%

Each measurement is not free — it has a per-projection QND survival **q ≈ 0.987** (measured on
the measurements-only arm; this is the switch-bench v3 axis number, now in hand). Divide it out
(P / q^N) and the ideal Zeno law **[cos²(π/2N)]^N** matches at the half-percent level through N=8:

| N | measured (QND-corrected) | theory [cos²(π/2N)]^N | residual |
|---|---|---|---|
| 2 | 0.254 | 0.250 | +0.004 |
| 4 | 0.530 | 0.531 | −0.001 |
| 8 | 0.728 | 0.733 | −0.005 |
| 16 | 0.844 | 0.857 | **−0.012 (the frontier)** |

**The watch-cost frontier** (reported subclaim): the correction rescues the law to 0.5% *through
N=8*, but at **N=16 the residual grows to −0.012** — watching that fast, the per-measurement cost
and higher-order effects begin to eat the gains. **The beam has an optimal grip cadence, and this
is the measurement of where it sits.**

## The grade

| Gate | Rule | Measured | Verdict |
|---|---|---|---|
| G0 (mid-measurement functional) | nodrive_8 > 0.7 | 0.884 | **PASS** |
| **W_TRACTOR** | P(pinned_8) − P(unwatched_8) > 0.3 at 5σ | 0.624 (92σ) | **ZENO-PINNING-CERTIFIED** |
| **W_CADENCE** | P(pinned_8) − P(pinned_2) > 0 at 5σ | 0.398 (87σ) | **PASS** |

## What this does and does not show (frozen scope)

Single qubit, one window; the quantum Zeno effect is **established textbook physics** — this does
not discover it. What is genuinely contributed: a **frozen-graded certification** of Zeno pinning
against a full coherent π-rotation on this hardware, the **QND-corrected cadence law matched to
0.5%**, the per-projection cost **q = 0.987** measured (a reusable switch-bench axis), and the
**watch-cost frontier** located (the optimal-cadence trade-off, not just the monotone "faster is
tighter"). It is *not* protection against thermodynamic (T1) decay — that was the corrected
design error, and the distinction is stated plainly.

## Lineage and reuse — and the completion of Horizons-2

- **Arc**: measurement-based state control / quantum Zeno (Horizons-2 Q6). **With F102 the
  Horizons-2 program is complete, six of six**: **F97** negative energy · **F98** objectivity
  beyond causal order · **F99** the heralded mirror · **F100** the twin paradox · **F101** the
  grandfather audit · **F102** the tractor beam. Six universe-questions asked in ~14 days, six
  delivered — every gate frozen before flight, every miss in the record (F97's failed LOCC leg,
  F100's refuted static-ZZ, the F93/F95 floor misses), and two wins demoted and re-earned along
  the way (F94's refused pseudo-win, F100's self-attached asterisk).
- **Method reuse**: measure-the-nuisance-then-correct (the QND cost q divided out before the law
  fit — friction-02 practice, the F94/F100 lineage); frontier-not-just-monotone reporting (locate
  where the trade-off turns, don't just report "more is better"); shallowest-possible apparatus
  (zero 2q gates) as the depth-arc's opposite bookend to F98's 63 CZ — the cheapest flight
  produced the cleanest law match.
- **Status-ledger claim type**: **existence** (Zeno pinning against coherent π-rotation certified
  on hardware; textbook priors credited). The figures of merit are the **QND-corrected law match
  (0.5% through N=8)** and **q = 0.987**; the **watch-cost frontier (N=16 residual −0.012)** is a
  reported subclaim. Single run, single window; UNTESTED.
