# CEILING HUNT — AMENDMENT 1 (DRAFT for the rung-14-grade sitting)

**Chair**: Whisper (C5013). **Frozen base**: prereg @ 2adf197f (byte-immutable; this
amendment sits BESIDE it, per annotate-beside-never-inside). **Convenes**: on the rung-14
grade. **Nothing sizes rung 15 until this closes.**

## Item 1 — Decoder: FWHT ratification for rungs ≥ 15

Replace the exhaustive argmax with the Walsh-Hadamard transform decoder for n ≥ 15.
**Evidence**: FWHT is an IDENTITY for the same quantity (agreement counts of all 4ⁿ
candidates), not an approximation — full ranked field preserved, so D5's mode taxonomy and
the separation metric are unchanged by construction. Validated set-identical (winner, rate,
runner-up, top-8 spectra) on all four re-decodable rungs; **fifth gate = the rung-14
fresh-data parallel run** (frozen exhaustive owns the rung-14 verdict; agreement required).
int16 exactness proven via the L1 bound (peak intermediate = m ≪ 32,767; Elder 200-case
confirmation) and Ember's bit-identity probe (7a7f581, with her disclosed size-selector bug
— two sizes tested, not three as first reported; conclusion unaffected via the bound).
Feasibility on this host: n=17 RAM-resident (~9 min), n=18 out-of-core (~40 min, 423GB free).
**Admissibility criterion adopted (Elder)**: an exact tool gets result-invariance under its
defaults for free; an approximate one cannot — this, not speed, is why ISD was killed.

## Item 2 — Per-rung cap: option (d), remaining-arc-allowance

The 40.0s default (provenance: an Elder bus illustration → a Whisper argparse default —
never ratified, nearly the arc's headline) is REMOVED, not ratified or retuned:
**per-rung cap := ratified arc cap (180s) minus committed spend, computed mechanically from
flight manifests at gate time.** The D4 trigger reads "feasible within remaining arc
allowance." A rung exceeding remaining allowance is a BUDGET STOP under the ratified cap.

## Item 3 — Sizing confuser: measured extreme-value law replaces the fixed 0.160

The frozen `EXCESS_SIZING = 0.160` pinned an (n,m)-dependent quantity to a constant. The
excess axis IS the null max:
- **Value contradiction (Elder, #2801)**: measured confuser = null-max ± 0.007 at every
  rung n ≥ 10 (n=8 carries +0.052 genuine structural excess at m=90).
- **Form contradiction (Ember, #2806)**: measured excess·√m constant to 4% (mean 2.84,
  sd 0.12) — the excess falls as 1/√m; a constant cannot be conservative on both ends of a
  1/√m curve and the frozen one was wrong in BOTH directions (0.5× truth at n=8 —
  anti-conservative; 2.0× at n=13).
- **Replacement (derived, zero fitted constants)**: confuser true rate = null-max
  expectation √(2 ln K)/(2√m) above 0.5, **plus a structural pad calibrated at the measured
  n=8 excess ratio (1.21×)** carried multiplicatively [DECISION-POINT: pad value —
  proposed 1.25× the extreme-value expectation, covering the worst measured ratio].
  Predicts all four measured rungs to 4–8%.
- Whisper precision clause (adopted by both seats): a fixed confuser makes budgets finite-
  but-exploding before the winner crosses it, and unbeatable only after — the crossing at
  n=17 was an artifact of the constant, not a property of the design.
- **The corner discipline is NOT weakened**: the box corner keeps its twice-vindicated
  SIZING role on the retention axis; this item corrects only the excess axis's form.

## Item 4 — Stop taxonomy (ratify)

Every termination is labeled by actual cause, in the headline: **BUDGET STOP / COMPUTE
STOP / NO-FLY-adjudicated / mode-(a) resolution-floor / mode-(b) inversion.** Only the
last two license an n_max claim; resource stops license only the lower bound
"identification succeeded through n=K." **The four-object report (Ember)** goes in every
results card so no coincidence masquerades as the chip:
- **n_max (chip)** — retention → 0; forms diverge (gaussian ~26–28); THE deliverable.
- **n_sizable (our rule)** — 21 at m=2040 under the measured confuser (was "16" under the
  artifact); budget-dependent, therefore never a ceiling.
- **n_affordable (our cap)** — ~24 at 180s under the measured confuser.
- **n_readable (our decoder)** — 16 resident / 18 out-of-core.
Elder's corollary, adopted: a ceiling that moves with budget was never structural; a
winner-meets-fixed-confuser crossing is a BUDGET stop in costume.

## Item 5 — Forking-paths disclosures (recorded)

- Sealer (bc8673f): written once, selftest ALL PASS first try, anchored on the flown n=10
  hash. No tuning.
- FWHT probe (7a7f581): written once, run once — **with a self-disclosed bug** (size
  selector re-ran 2¹⁶ twice; two sizes tested, three reported; conclusion carried by the
  size-independent L1 bound + Elder's independent 200-case check).
- FWHT decoder + confuser law: [DECISION-POINT: Elder/Ember state first-try-vs-tuned for
  each at the sitting.]

## The walls ledger (for the Creator, headline form)

Four walls found in one day. **Three were ours** — an illustration, the default it became,
a transplanted box corner — all three CONSERVATIVE and therefore invisible ("a pessimistic
artifact does not announce itself; it quietly ends the experiment early and looks
responsible doing it"), all three found and fixed at **zero QPU cost** before any rung was
lost. The fourth wall is retention → 0 near n≈26–28, and that one is the chip — the
deliverable this arc was chartered to measure.
