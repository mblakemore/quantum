# Have We Found Quantum Advantage? — The Complete Answer

**Author**: Whisper (DC15W), C4682 (2026-07-14) · **Substrate**: claude-opus-4-8
**Supersedes**: `docs/quantum-advantage-audit-whisper-c4666.md` (the mid-campaign audit that
scoped five routes). This is the completion: every route flown, every scope named.

---

**Visual scoreboard**: `demo/scoreboard/index.html` — the five scoreboards, the σ-clearances, and the boundaries at a glance (self-contained, theme-aware; deployable on the campaign Pages site).

## The one-line answer

**Yes — measurably, on four of five scoreboards, against exact theorem ceilings cleared by
21σ–341σ; and on the fifth (computational), the constant-depth solver the only depth-separation
theorem is built on now runs on silicon at 90%. What we have *not* found is a brute-force
time-to-solution speedup, and F54 measured exactly the wall that forbids it. Every claim is
scoped to the assumption its hardware honestly provides.**

The question is not one claim but five scoreboards. Here is where each stands, with receipts.

---

## The five scoreboards

### 1. Provable-bound games & correlations — **FOUND, the campaign's spine**

Every entry beats an *exact* theorem ceiling for classical (or causally-ordered) resources,
pre-registered, on silicon:

| Advantage | Ceiling | Measured | Finding |
|---|---|---|---|
| Causal discrimination game | 0.8695 (SDP, all definite-order) | 0.9769; **216.8σ within-run**, physical carrier is the 0.3 pp two-chip concordance (replicated 0.9738 / 201σ; audit C4714) | F82 |
| Superdense coding | 0.5 exactly | 0.9688, **341σ** | F87 |
| Magic-square contextuality | **8/9 exactly (enumerated in-artifact, 4096 strategies)** | 0.9690, **196σ**; worst context still >8/9 at 37.8σ | **F106** |
| Capacity activation | 0 exactly | 0.0436 bits/use, 55.6σ (N=3: 61.7σ) | F85 |
| Bell/CHSH + repeater | 2 exactly | 2.74; survives two swaps | F01/F91/F93 |

The three great no-go theorems — nonlocality (Bell), indefinite causal order (F82),
**contextuality (F106)** — are certified in one pre-registration court.

### 2. Communication & sensing — **FOUND, a ladder**

| Advantage | Ceiling | Measured | Finding |
|---|---|---|---|
| Superdense coding | 0.5 | 341σ | F87 |
| 2→1 QRAC (two bits in one qubit) | 0.75 (enumerated) | 0.849, **110σ**, inside the two-sided band vs the quantum optimum | **F107** |
| GHZ metrology vs standard quantum limit | executed separable Fisher info | ratio 2.848, **168σ**; **N-ladder persists to N=5** (task-dependent, contra F85's inversion) | **F108/F109** |

### 3. Thermodynamics from causal indefiniteness — **FOUND**

The ICO engine arc: refrigeration forbidden to ordered processes (21.1σ, F86; native-fluid
retest colder than the coldest reservoir, F88); certified population inversion from passive
baths (F94); full thermodynamic cycle, books audited (F95); certified negative local energy
(F97). Scope kept honest: per-interaction resource advantages, not power plants; and the
coherent-erasure advantage was found **below** NISQ's 5σ certification floor three instrument-
walls deep (F104/F105) — the null is part of the record.

### 4. Information-theoretic — **FOUND**

Negative conditional entropy S(B|A) = −0.855 at 42σ (F105), −0.0986 at 5σ from banked data
(F103) — a sign classical physics forbids. Zero-capacity transmission (F85) and definite-order-
inaccessible information recovered by the switch (F99, 56σ) sit in the same class.

### 5. Computational (time-to-solution / depth) — **THE WALL MEASURED, THE BRIDGE FLOWN**

- **The wall (no brute-force speedup)**: F54 — the Grover/QAE crossover needs ~10⁴ two-qubit
  gates against a ~10³ scrambling wall (F05). No stack of constant factors closes a 10× depth
  deficit. Honestly measured, not hand-waved.
- **The bridge (the honest depth advantage)**: Bravyi–Gosset–König is the only *unconditional*
  computational-separation theorem at our depth (constant-depth quantum solves 2D-HLF; any
  bounded-fan-in classical circuit needs Ω(log n)). We **flew it**: the constant-depth solver
  runs on silicon at **P(valid) = 0.9017, 438σ over the random-chance floor 0.25** (a fidelity number, not a beaten classical bound), covering the full solution coset
  (**F113**), and the advantage **persists through n=9** as heavy-hex routing grows (F114). The
  fence held throughout: this is *not* a QNC⁰≠NC⁰ on-chip proof — the separation is asymptotic,
  carried by the theorem; the apparatus works on 2026 hardware.
- **The through-line**: BGKT 2020 proves the separation survives noise via a construction that
  plays the **magic-square game** — F106's exact 8/9 contextuality. The classical hardness of
  this *computational* problem is the *same resource* certified at 196σ in scoreboard 1. The
  correlation advantage and the computational advantage are one thing.

---

## The five frontier routes (C4666 audit) — all delivered

| Route | Status | Where |
|---|---|---|
| (a) BGK shallow-circuit computational bridge | **flown on silicon** | F113/F114 + `sdp`/HLF tooling |
| (b) 2→1 QRAC communication | **certified** | F107 |
| (c) GHZ metrology vs SQL | **certified + laddered** | F108/F109 |
| (d) Certified randomness | **rigorous one-sided-DI certificate** | F115→F117 (below) |
| (e) QPU weather service (zero-qubit advantage) | **built + validated** | `tools/qpu_weather.py` |

---

## The arcs — how the pieces connect

**The advantage-genre sweep (four Creator-directed cycles):** games (F106) → storage (F107) →
metrology point + ladder (F108/F109). Every ceiling enumerated in-artifact or executed as a
live competitor.

**Horizons-3, six-for-six:** the replicator's legal limit (optimal cloning ceiling 5/6 with a
cheat-detector, F110), the cloaking device (DFS vs echo — active beats passive 35σ, a
correlated-noise probe, F111), the transporter's exam (the three-axis bench travels to a second
chip, device-independent, F112). With F106 (Kobayashi Maru) and the earlier H1–H4, the round
closed complete.

**The trust ladder (the deepest honest-path arc, six cycles):** the campaign's cleanest lesson
in claiming *exactly* the assumption the hardware provides.
- F115 — on-chip CHSH: a 53σ quantum-behaviour witness. The device-independent randomness
  number *evaporated* (no-signaling unmet on one chip) and was quarantined to a labeled
  counterfactual — not caveated, quarantined, because the quantity itself failed.
- F116 — one-sided-DI steering, 96σ: Alice demoted from trusted to a black box. The certificate
  holds because faking the violation needs ~0.68 correlation excess, and the only on-chip
  mechanism (crosstalk) is ~1% — measured in this campaign's own noise studies.
- The randomness bound then failed a boundary check (it certified randomness where there is
  none) → **the SDP tool** was built (`tools/sdp_randomness.py`), exact via GHJW for a trusted
  qubit, boundary-validated.
- F117 — **the rigorous certificate: 0.65 certified private random bits per use, from
  measured assemblage tomography** (bias-disclosed: a +0.006 method bias ≈1 SE the bootstrap can't
  see is the limiting factor, not the ~100σ statistical margin; audit C4713). What F115 wanted but could not honestly claim via DI,
  delivered at the one-sided-DI rung a single chip genuinely holds.

The ladder of trust, each rung claiming exactly its assumption: full-trust Born randomness →
one-sided-DI steering (F116/F117) → full-DI (needs space-like separation, off-chip, flagged not
attempted).

---

## The tools that outlive the results

- **`tools/sdp_randomness.py`** — exact 1SDI randomness SDP for a trusted qubit (GHJW collapses
  the hierarchy to an exact finite program). Boundary-validated. Consumes any qubit assemblage.
- **`tools/qpu_weather.py`** — the scheduling oracle: a live nowcast that beat the vendor's
  published deep-circuit forecast by 27% and caught a 3.4× readout-drift understatement on one
  window. The zero-qubit advantage — no theorem, just a fluctuating channel that is cheaply
  measurable and poorly published.
- **`tools/switch_bench.py`** — the three-axis causal-structure benchmark, shown
  device-independent (F112).

---

## What is NOT claimed (the boundaries, stated plainly)

- **No brute-force time-to-solution speedup** — F54's wall, measured.
- **No QNC⁰≠NC⁰ on-chip proof** — F113/F114 are the working apparatus of an *asymptotic*
  theorem, not the asymptotics.
- **No loophole-free device-independence** — F115–F117 are one-sided-DI (locality loophole open;
  crosstalk loophole bounded, not closed). Full DI needs space-like separation, off-chip.
- **No cross-generation portability** — F112 is same-generation Heron; an Eagle exam is the
  harder unclaimed test.
- **Resource advantages, not deployed machines** — the thermo and comms results are per-
  interaction resources with stated scope.

Every result names the assumption it holds under. That discipline — enumerate the bound
in-artifact, quarantine a quantity that evaporates, build the tool when the shortcut fails,
claim the rung the hardware provides — is what makes the "yes" defensible.

---

## The answer, restated

The campaign found **measurable quantum advantage** on the defensible axes where the ceiling is
a theorem: games, communication, thermodynamics, information — 53σ to 341σ. It measured the
**wall** that forbids a brute-force speedup, and flew the **constant-depth bridge** that is the
honest route toward the computational scoreboard, tied by the same contextuality resource to the
games. And it built the tools — an exact randomness SDP, a scheduling oracle — that turn the
one-off certificates into standing capabilities.

Receipts: ~110 experiments, every number anchored to an IBM job ID, findings F01–F118, two
Heron dies (all Heron-generation). The scoreboard is the answer.
