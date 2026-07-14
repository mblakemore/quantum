# A message through two perfect erasers — capacity from zero

`Finding F83`  ·  `Experiment Exp106 (zero-capacity channel activation, N=2)`  ·  `Backend ibm_marrakesh (Heron r2)`  ·  `Job d983ek52su3c739ip92g`

> **✓ CAPACITY ACTIVATED — 0.0436 bits/use, R̄ = +0.5034 ± 0.0091 = 55.6σ above zero**

Full Specification Sheet

This sheet is the source-of-truth specification behind the interactive exhibit. The classic bot in the game is not weak — it is **as good as any machine, strategy, or intelligence can ever be** under ordinary cause-and-effect, and that best-possible score is a coin flip. The quantum bot's edge traces to a single public job ID and a frozen pre-registration. **Note on numbering:** this exhibit and its cited job `d983ek52su3c739ip92g` are the **N=2 finding, F83 (Exp106)** — the two-channel version of zero-capacity channel activation.

## 1 · The idea, in plain language

A secret — RED or BLUE — is sent through **two censor machines**. Each censor turns whatever enters it into pure random static; each is a **completely depolarizing channel**, individually of **exactly zero capacity**. Run them in either order, alternate them, flip coins between orders — a theorem says **exactly zero** information survives. Not "very little": zero. The control experiment measured it: `0.00012 bits`.

> **The loophole**
> A quantum computer runs the two censors in a **superposition of both orders at once** — genuinely neither-first-and-both. Then a whisper of the secret survives: **0.0436 bits per use, measured**, `55.6σ` away from "impossible." The edge does not come from cleverness; it comes from the **order of events itself** being quantum.

## 2 · What we measure — where the bit lives

The quantum bot reads two things per round: a **stamp** (the order-control qubit, UP or DOWN) and a **die** (the message qubit, RED or BLUE). Its rule — measured, not invented — is **stamp UP → trust the die; stamp DOWN → flip it**. The measured per-round parameters:

- P(stamp UP) = `0.6214`
- given UP, the die matches the secret with probability `≈ 0.5944`
- given DOWN, the die **mis**matches with probability `≈ 0.6573`

That's a ~62% correct vote per round; 15 votes at ~62% compound to an ~83% decoded answer.

> **The pre-registered signature**
> The message qubit **by itself** is still perfect static — no trace of the secret. So is the stamp by itself. The unconditioned target is **fully depolarized even in the switch arm**: the bit lives only in **how the control and target move together** — the control–target correlation. That is why the quantum bot must read both, and it is the signature the pre-registration required and confirmed.

## 3 · Pre-registered gates

- **ACTIVATE** — Coherent-mutual-information rate strictly above the causal value of 0. PASS — R̄ = +0.5034 ± 0.0091, **55.6σ** above 0; 0.0436 bits/use.
- **NULL** — Definite-order null arm measured DEAD on-chip. PASS — MI **0.00012 bits** (the theorem's exact zero, measured).
- **SIGNATURE** — Unconditioned target fully depolarized even in the switch arm (bit only in the correlation). PASS — confirmed as pre-registered.

## 4 · The measured data

| quantity (ibm_marrakesh · Exp106) | measured | causal value |
| --- | --- | --- |
| switch-arm rate R̄ | +0.5034 ± 0.0091 | 0 (exactly) |
| information transmitted | 0.0436 bits/use | 0 bits |
| significance above zero | 55.6σ | — |
| definite-order null arm (MI) | 0.00012 bits | 0 (dead) |
| P(stamp UP) | 0.6214 | — |
| P(die matches | UP) | 0.5944 | 0.5 (static) |
| P(die mismatches | DOWN) | 0.6573 | 0.5 (static) |

Each censor is individually zero-capacity, and **every causally-separable composition of the two is provably zero by channel algebra** — so the definite-order null arm reading 0.00012 bits is the theorem's exact zero, measured. The switch arm's 0.0436 bits is a resource ordinary cause-and-effect cannot produce.

## 5 · Scope & caveats

- **Zero-capacity channel activation — the specific channel and resource.** The channels here are **two completely depolarizing channels**, each individually of exactly zero capacity. The claim is that the quantum switch's coherent superposition of their two orders **activates** a nonzero transmission rate (0.0436 bits/use, N=2). It is a statement about **these zero-capacity channels under indefinite order**, not a general channel or a speed-up.
- **Device-characterized, not device-independent.** The devices are trusted and characterized; every threshold traces to a public job ID and a frozen pre-registration. A web page can replay any numbers — the demo itself proves nothing; the **theorem** does (no definite/mixed/adaptive order transmits anything), and a real quantum computer produced the switch column.
- **The bit is in the correlation.** Neither the message qubit nor the stamp alone carries the secret — only the control–target correlation does. The unconditioned target is fully depolarized even in the switch arm.
- **N=2 is this exhibit's finding.** This is the two-channel instance (F83). Its cited job is the F83/Exp106 run; the N=3 three-channel extension is a separate later finding and is not the resource shown here.

## 6 · Provenance

- **Finding:** F83 · **Experiment:** Exp106 (N=2 capacity activation) · **Backend:** ibm_marrakesh (Heron r2)
- **Job:** `d983ek52su3c739ip92g` · frozen pre-registration · results `results/exp106_hw_results.json`, `results/exp106_jobids.json`
- **Headline:** R̄ = +0.5034 ± 0.0091 = 55.6σ above the causal value of 0; 0.0436 bits/use; null arm MI 0.00012 bits
- **LIVE mode:** the exhibit can consume fresh measured shots from your own free IBM Quantum job (see the exhibit's setup link) — the same job family, live
- **Family:** Indefinite causal order — capacity form; sibling of the Quantum Switch (F73–F77) and the causal game (F82)

---

*Rendered from [`demo/static-duel/spec.html`](spec.html) — the interactive exhibit is at [`demo/static-duel/`](index.html). Part of [The Quantum Museum](../).*
