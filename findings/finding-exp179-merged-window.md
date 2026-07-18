# Finding — Exp179: THE MERGED WINDOW — architecture pays (+12.3σ), and the circuit-level plateau is found

**Cycle**: C4866 · **Date**: 2026-07-19 · **Backend**: ibm_fez · **Job**: `d9e0gv4inv1c73aplk4g`
(15 circuits: 5 frame-tracked arms × ZZ/XX/YY, 8000 shots; engineered-Hahn delay 425 dt ≈ 1.70 μs).
Sixth and closing flight of the composition-tax arc.

## Result

| arm | ZZ / XX / YY | F(Φ+) |
|-----|--------------|-------|
| seq (2 windows, Exp177 replica) | +0.774 / +0.256 / −0.247 | 0.569 |
| seqecho (2 windows + midpoint echo, Exp178 replica) | +0.750 / +0.629 / −0.597 | 0.744 |
| **merged (ONE window)** | +0.822 / +0.531 / −0.506 | **0.715** |
| **mergedecho (one window + X–delay–X)** | +0.787 / +0.663 / −0.646 | **0.774** |
| direct | +0.968 / +0.970 / −0.964 | 0.976 |

- **PRIMARY HELD — window-count is architecture**: merged − seq = **+0.146 at 12.3σ**. Because
  the Pauli frame decouples the second swap's gates from the first swap's outcomes, both Bell
  measurements merge into one simultaneous window — window count 2→1, middles never idle through
  a window — and it buys +0.146 with zero added gates. A compiler-level rule: **schedule
  frame-tracked measurements simultaneously.** (Merged also posts the best chain ZZ of the night,
  0.822.)
- **The engineered Hahn works**: mergedecho − merged = **+0.059 at 5.0σ**. The delay-matched
  X–delay(w)–X refocuses the single window; the pre-named transpiler-reflow risk did not bite.
- **SECONDARY NOT HELD (honest)**: mergedecho − seqecho = +0.030 at **2.5σ** — under the
  pre-registered 3σ bar. The new stack leans ahead of the old; it is not crowned.
- **The pre-registered open comparison resolves as a TIE** (merged − seqecho = −0.029, −2.5σ):
  the two attack routes — halve the windows and spare the middles, vs refocus the ends through
  both windows — recover **the same pool**. This is Exp178's overlap principle at the
  architecture level: every circuit-level countermeasure drains one common coherent reservoir.

## The plateau (what the arc's last flight adds)

Across Exp178–179 the best stacks converge: defecho 0.782, mergedecho 0.774, seqecho 0.744 —
a **circuit-level plateau at ~0.75–0.78**, roughly 0.11 below the no-window ceiling (0.885).
What remains is the share no circuit-level trick reached: the non-refocusable component of the
end-qubits' in-window noise (backaction/crosstalk; echo cancels only the quasi-static part) plus
the T1/T2 price of the Hahn delay itself (refocusing buys dephasing cancellation by *doubling*
idle time — it cannot help amplitude damping). The frontier below 0.885 is pulse-level or
hardware, and the arc labels it precisely rather than promising it.

## Calibration ledger — ALL FIVE BANDS HELD (first time tonight)

seq 0.569 ∈ [0.50–0.62] ✓ · seqecho 0.744 ∈ [0.70–0.82] ✓ · merged 0.715 ∈ [0.68–0.82] ✓ ·
mergedecho 0.774 ∈ [0.75–0.88] ✓ · direct 0.976 ∈ [0.95–0.99] ✓. After five flights of
band misses (three low from multiplicative priors, two high from a conservative echo prior),
the sixth flight's bands — priced from the accumulated dose-response and echo-efficacy data —
all held. The pricing model converged in one night because every miss was converted into a
model update. Ledger prediction was logged pre-submission this cycle (gap from C4864/65 closed).

## The completed arc (six flights, one night)

175 tax discovered (−3.4σ) → 176 compounds with windows (−9.4σ) → 177 decomposed
(measurement window dominant; frame = free +0.09) → 178 cured (coherent; one X = certification,
+24.8σ; countermeasures overlap) → **179 architecture (+12.3σ merged windows; engineered Hahn
+5.0σ; circuit-level plateau located at ~0.78)**. Operational rules shipped: track Paulis in
software; merge frame-tracked measurement windows; echo end-qubits through every window; price
countermeasure stacks jointly; expect the plateau ~0.11 under the no-window ceiling.

## Fence

Secondary at 2.5σ stays unclaimed. One night's conditions (volatile — the day's record); the
plateau value is condition-dependent even if its existence is structural. The engineered delay
pays a T1 tax not separated from its dephasing gain here (a splittable follow-up if ever needed:
sweep delay length). Frame arms remain verification-equivalent for non-Clifford consumption.
