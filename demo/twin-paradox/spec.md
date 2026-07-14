# The Twin Paradox, adjudicated end-to-end

`Finding F100`  ·  `Experiment Exp122b (phase-blind retest of Exp122)`  ·  `Backend ibm_marrakesh (Heron r2)`  ·  `Job d9ah35eg26ic73demgag`  ·  `Cycle C4653 · Whisper`

> **✓ VERDICT — AGING-CERTIFIED-CLEAN · 36σ**

This sheet is the complete, source-of-truth specification behind the interactive exhibit. Every number on the exhibit page is drawn from here; every number here is drawn from the frozen grade file `results/exp122b_grade.json` and its job record `results/exp122b_jobids.json`. Nothing is hand-tuned for display.

## 1 · The idea, in plain language

Einstein's twin paradox: a twin who takes a fast trip ages **less** than the twin who stays home — moving clocks run slow. Now make it quantum. Send a single particle through an interferometer — a device that splits it onto **two paths at once** and recombines them, so it interferes with itself. Interference only appears if the two paths are truly **indistinguishable**: nothing must record which way it went.

Put a tiny **clock** on the particle. If the clock **ticks** (ages) while in flight, its reading becomes a record of **how much time elapsed on that path** — and if the two paths accumulate different amounts of aging, the clock has quietly written down **which path was taken**. That which-path record destroys the interference. Aging, in other words, is **which-path information**. This is the Zych–Brukner insight: proper time itself can act as a which-path marker, decohering a quantum superposition.

> **The chip analog**
> We cannot dilate real time on a qubit, so we build the **analog**: a "clock" qubit that either **ages** or **doesn't**, riding an interferometer built from a second qubit. An **excited** clock (prepared in |1⟩) decays and dephases — it ages. A **vacuum** clock (left in |0⟩) barely evolves — it is the stay-at-home twin. Prediction: the excited-clock interference should wash out **far faster** than the vacuum-clock interference. It does. That gap **is** the twin paradox on silicon — an analog of which-path clock decoherence, **not** a measurement of literal gravitational/velocity time dilation.

## 2 · What we measure — and why it is "phase-blind"

The health of the interference is its **visibility** `V` — the contrast of the fringes, 1 = perfect, 0 = washed out to grey. We read it out on two axes (X and Y) and combine them:

> **The phase-blind estimator**
> `|V| = √(X² + Y²)` — the **length** of the coherence vector, discarding its **angle**. This is deliberate. A coherent stray rotation (the clock qubit tugging the phase around) would **move** the fringe sideways without destroying it — and an X-only estimator would misread that spin as a loss of contrast. By taking the magnitude, we are **immune to rotation by construction**: only genuine loss of coherence can shrink `|V|`. This estimator is the fix that turned a confounded win into a clean one (see §5).

## 3 · Pre-registered gates (frozen before flight)

The decision rules were written and committed in `experiments/exp122b-phase-blind-preregistration.md` before any data was taken. The grade script self-tested against four synthetic outcomes (MIXED / AGING-CLEAN / CLOCK-PULL / UNRESOLVED) and passed 4/4 before touching the real counts.

- **G0** — Both arms must start coherent: `|V|(0) > 0.7` for vac and exc, else NO-TEST. PASS (0.885, 0.862).
- **W_TWIN** — Aging signal: `V_vac − V_exc > 5·SE` at 73µs **or** 146µs. PASS (36σ and 23σ — both).
- **W_ROT** — Rotation probe: `echoX − rawX > 5·SE` at 73µs (would indicate a recoverable coherent pull). did not fire (−0.119, wrong sign).

Classification map: `MIXED | AGING-CERTIFIED-CLEAN | CLOCK-PULL | UNRESOLVED`. W_TWIN firing while W_ROT stays silent ⇒ the loss is real decoherence from aging, not a hidden rotation ⇒ **AGING-CERTIFIED-CLEAN**.

## 4 · The measured data

Phase-blind visibility `|V| = √(X²+Y²)` down the delay ladder (delay is the proper-time proxy — more delay = more aging). 20,000 shots per setting, X and Y readouts, 28 two-qubit gates per circuit.

| delay (µs) | vacuum |V| | excited |V| | aging gap | significance |
| --- | --- | --- | --- | --- |
| 0.0 | 0.885 | 0.862 | 0.023 | — |
| 36.6 | 0.657 | 0.355 | 0.302 | — |
| 73.2 | 0.493 | 0.155 | **0.338 ± 0.009** | **36σ** |
| 146.4 | 0.283 | 0.052 | **0.230 ± 0.010** | **23σ** |
| 292.7 | 0.066 | 0.027 | 0.038 | floor |

The vacuum twin keeps its interference far longer; the excited twin's washes out almost twice as fast. At the longest delay both have decayed to the noise floor (nothing coherent left to distinguish) — the signal lives in the **middle** of the ladder, exactly where a which-path clock should bite hardest.

## 5 · The adjudication — the adjudication that is itself the finding

The first run, **Exp122**, passed at **67σ** — a bigger number than the one reported here. It was not reported. Its author attached her own asterisk and withheld it, for a specific reason:

> **Why the bigger number was withheld**
> The X-only visibility curves went **negative**. A true visibility **cannot** be negative — but a fringe that is **rotating** can swing its X-projection below zero. That was the tell: some of the apparent "decoherence" was actually the clock qubit **coherently spinning the phase** (a ZZ-type pull), which an X-only estimator confounds with genuine contrast loss. Rather than bank the inflated 67σ, the run was frozen as a confounded result and a **phase-blind retest** (Exp122b, this sheet) was designed to be immune to exactly that artifact.

The retest keeps two sub-stories on the record:

- **The rotation was real** — coherence had spun into the Y axis; Exp122 was reading the wrong axis. The phase-blind `|V|` recovers it and still shows a clean 36σ aging gap.
- **But the proposed mechanism was refuted.** The pre-filed hypothesis was a **static ZZ** pull, which a spin-echo should **recover**. The echo recovery came back **−0.119 ± 0.010 — the wrong sign**. Static-ZZ REFUTED. The author's 0.80 prior on that mechanism missed; the realized class was her **least-favored** (0.10). Calibration lesson logged, not buried.

> **Verdict**
> **AGING-CERTIFIED-CLEAN.** The aging signal survives the estimator that a rotation cannot fool (36σ), and the one mechanism that would have explained it away as a recoverable artifact was tested and rejected. The adjudication — win demoted, confound isolated, retest designed, mechanism refuted in the open — **is** the finding.

## 6 · Scope & caveats

- **Analog, not literal.** This is a which-path **clock-decoherence** analog (Zych–Brukner style). It is not a measurement of gravitational or velocity time dilation on a qubit.
- **Coherent decoherence.** "Aging" here is the excited clock's decay + dephasing marking the path. Reported subclaim: the excited-arm decay runs **~2× faster than pure T1** would predict (`V-ratio 0.314` measured vs `√0.1 = 0.667` expected) — extra channels beyond simple relaxation, reported as an open excess, not swept under.
- **Published-T1 is not trustworthy for grading.** The clock lane's published T1 swung 334→188µs in 24h (and 361µs in this job's calibration). The rule of the campaign holds: **place by published, grade by measured.** The in-job measured T1 (K=188µs, L=174µs) is what the certificate rests on.
- **Floor at long delay.** At 292.7µs both arms have decohered to noise; the aging gap there (0.038) is not a claim — only the coherent middle of the ladder carries the result.

## 7 · Provenance

- **Grade file:** `results/exp122b_grade.json` · **Job record:** `results/exp122b_jobids.json`
- **Pre-registration:** `experiments/exp122b-phase-blind-preregistration.md` · **Parent (confounded):** Exp122
- **Backend:** ibm_marrakesh (Heron r2) · **Layout:** [2,3,1] · **Shots:** 20,000/setting (10,000 for calibration probes)
- **Self-test:** grade script 4/4 PASS on synthetic MIXED / AGING-CLEAN / CLOCK-PULL / UNRESOLVED before scoring real data
- **Family:** Horizons-2 Q4 · sibling of the Grandfather audit (F101) and the Zeno tractor beam (F102)

---

*Rendered from [`demo/twin-paradox/spec.html`](spec.html) — the interactive exhibit is at [`demo/twin-paradox/`](index.html). Part of [The Quantum Museum](../).*
