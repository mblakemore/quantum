# Two bits in one qubit, either one retrievable

`Finding F107`  ·  `Experiment Exp128 (2→1 QRAC)`  ·  `Backend ibm_marrakesh (Heron r2)`  ·  `Job d9al7om6hjac73fejisg`

> **✓ QRAC CERTIFIED IN THE TWO-SIDED BAND · 110.5σ over classical, 5.2σ under the quantum law**

This sheet is the source-of-truth specification behind the interactive exhibit. Every number is drawn from the frozen grade file `results/exp128_hw_results.json` and its job record. It is the campaign's **first zero-two-qubit-gate advantage flight** — the whole trick fits in a single qubit's angles.

## 1 · The idea, in plain language

Alice has **two bits**. She must pack them into **one** carrier and send it. Bob, on the other end, gets to ask for **either** bit — his choice, made **after** he receives the carrier — and he may look **once**. How often can he be right?

> **The classical packing limit**
> With one **classical** bit you cannot store two. The best you can do is store one bit faithfully and guess the other — averaged over Bob's random choice, that is **75%**. This ceiling is a theorem: enumerated here over all **256 encode/decode strategy pairs**, it comes out **exactly 0.75**.

> **The quantum trick**
> Encode the two bits into **one qubit's angle** on the Bloch sphere — the four messages point to the four "diagonals". Bob measures along the axis for the bit he wants. Because the states are cleverly spread, he is right `cos²(π/8) = 0.8536` of the time **for either bit**. Two bits, one qubit, either retrievable — **above what any classical bit can do.**

## 2 · The two-sided band — certifying inside the physical regime

Quantum mechanics doesn't just have a floor to beat; it has a **ceiling of its own**. A correct QRAC must land **between** the classical wall and the quantum law:

> **The advantage band**
> `classical 0.75  <  (a real 2→1 QRAC)  ≤  0.8536 quantum law`. Beating 0.75 is the advantage; **exceeding 0.8536 is impossible** — so a reading above the quantum law is an **apparatus error**, not a better result. The gate `G_QBAND` makes crossing the quantum ceiling a **NO-TEST**. Certifying **inside** the band is stronger than merely clearing the floor: it says the result is **real physics**.

## 3 · Pre-registered gates (frozen before flight)

- **G_SENT** — Readout sentinels healthy. PASS (0.998 / 0.995).
- **G_CLASS** — The executed classical arm honors its own 0.75 law. PASS (0.74818).
- **W1_QRAC** — **advantage:** pooled quantum − 5·SE > 0.75. PASS (0.84893, 110.5σ).
- **W2_MIN** — **every case:** the worst single (message, bit) case > 0.75. PASS (min 0.84325, 36.3σ).
- **G_QBAND** — **two-sided:** pooled must not exceed the quantum law 0.8536 (else NO-TEST). PASS (5.2σ below, inside the band).

## 4 · The measured data

Retrieval success for each of the 8 cases — 4 messages × which bit Bob asks for — plus the pooled result and the executed classical arm. Classical ceiling 0.75; quantum law 0.8536.

| Alice's message | read bit 1 | read bit 2 |
| --- | --- | --- |
| 00 | 0.84325 | 0.84455 |
| 01 | 0.84345 | 0.84940 |
| 10 | 0.85300 | 0.85410 |
| 11 | 0.85650 | 0.84715 |
| pooled (quantum) | **0.84893 ± 0.00090 — 110.5σ over 0.75, 5.2σ under 0.8536** |  |
| classical arm | 0.74818 (honors its own 0.75 law) |  |

Every one of the eight cases clears the classical 0.75 wall; the pooled value sits inside the band, a residual 0.0046 below the quantum law (device imperfection, in the expected direction).

## 5 · What makes it real

- **The ceiling is proven, not cited.** 0.75 is enumerated in-code over all 256 classical encode/decode strategy pairs — provable inside the grader.
- **Both laws honored on one chip.** The quantum player lands at 0.849; the executed classical player lands at 0.748 — each obeying its own law, same window. Only the quantum player crosses the line.
- **Two-sided, not one-sided.** `G_QBAND` would flag an over-the-law reading as apparatus error. Landing inside the band certifies the physics, not just "a big number".
- **Zero two-qubit gates.** The entire advantage is one qubit's rotation angles — the campaign's first zero-2q-gate **advantage** flight (the earlier zero-2q flight, F102, was a law-match, not an advantage).

## 6 · Scope & caveats

- **A communication/coding advantage, not computational speedup.** This certifies a random-access-coding advantage over a classical bit — one of the campaign's five advantage scoreboards, not a runtime speedup.
- **Device-characterized.** A hardware certification on a characterized device with an executed classical control, not a loophole-free protocol.
- **Textbook prior credited.** The 2→1 QRAC is Ambainis–Nayak–Ta-Shma–Vazirani; the contribution is the frozen, two-sided-band, null-controlled hardware certification.

## 7 · Provenance

- **Grade file:** `results/exp128_hw_results.json` · **Job:** d9al7om6hjac73fejisg
- **Pre-registration:** `experiments/exp128-qrac-preregistration.md`
- **Backend:** ibm_marrakesh (Heron r2) · **Classical ceiling:** 0.75 (enumerated, 256 pairs) · **Quantum law:** cos²(π/8) = 0.8536
- **Family:** Horizons-3 · one of the five advantage scoreboards (communication & sensing)

---

*Rendered from [`demo/pocket-dictionary/spec.html`](spec.html) — the interactive exhibit is at [`demo/pocket-dictionary/`](index.html). Part of [The Quantum Museum](../).*
