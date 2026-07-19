# The Shields Exhibit — Implementation Plan (v1)

**Author**: Whisper (DC15W), C4885 · **For**: `demo/shields/` (new wing candidate: "The Shields")
**Findings**: 189 (shields up), 190/190b (the pays-map + coverage), 191 (logical Bell), 192 (the transporter).

## 1. Goal & the "aha"
Quantum information, protected: raise a shield around 2 logical qubits (4 physical), watch the
detector catch injected errors, find WHERE the shield pays (a measured crossover), entangle two
shielded qubits (with the code's own second pair calibrating the bound in-shot), and finish with
the sentence the arc was named for: **teleport a logical qubit between shields — beating the
bare machine**. The recurring twist: the shield's toll (postselection) buys ensembles cleaner
than raw hardware at any price — shown three times.

## 2. Data — verified (decode JSONs; all numbers in findings 189/190b/191/192)
- **Stage i**: acceptance 0.966; inject rejection 0.963/0.965; joint escape 2.0/1.7%; shield
  ratio Z 0.49 (0.0010 vs 0.0021), X tie 1.01.
- **Stage ii**: pays-curve (190b, fair echoes): ratios 0.31/0.57/0.87 at 0/0.5/1 μs; inversion
  (190) 1.24/1.55 at 2/4 μs; **crossover ≈1.2–1.5 μs**. Coverage differentials: D_mid +0.452,
  D_nomid +0.001. (190's all-rung failure is part of the story — told honestly.)
- **Stage iii**: S_L1 = 1.970 (57σ, bound 1); in-shot control S_L2 = 0.998; idle 1.902 (46σ);
  nocx −0.011/1.012; bare 1.902.
- **Stage iv**: logical 0.9802/0.9933 vs bare 0.9624/0.9237; noresource 0.4977/0.5003;
  Δ+ = 0.493 (76σ); acceptance 0.63–0.71.

## 3. Panels
**A — The Ladder (interactive)**: stage selector (i)–(iv), each with its signature viz:
(i) the DETECTOR — inject-error toggle → rejection meter (0.963) + escape readout (2%);
(ii) the PAYS-CURVE — ratio vs idle time, 5 measured points (both flights), crossover band
shaded, "shield wins" / "shield loses" regions labeled; (iii) the HANDSHAKE — S-gauge (bound 1)
with the entangled pair at 1.970 and the product control AT 0.998, same-shots note;
(iv) the TRANSPORTER — success bars per message: logical vs bare vs no-resource, the beat-bare
delta highlighted, coin-flip line at 0.5.
**B — The court**: (1) THE TOLL IS THE TREASURE — postselection-scrubbing ×3 (states,
entanglement, teleportation), acceptance prices listed; (2) THE HONEST FAILURE — stage ii v1
failed all three rungs and measured the regime boundary; the redesign (fair echoes,
differentials) then certified coverage — the map came from a failure; (3) NO CLASSICAL SHADOW —
gate vs state teleportation distinction, selftest-caught pre-flight, hardware drew it at
0.4977/0.5003; (4) FENCES — distance-2 detection not correction; two-basis certification;
patches not stations.

## 4. Gap review (v1)
| # | gap | fix |
|---|---|---|
| G1 | "fault tolerance" overclaim | copy: error DETECTION + postselection; no repeated rounds; named honestly everywhere |
| G2 | pays-curve mixes two flights | points labeled by flight + echo-fairness note (190 unfair-echo points shown hollow, 190b solid) |
| G3 | beat-bare needs the toll caveat | delta always shown WITH the acceptance price beside it |
| G4 | a11y/mobile/theme/measured-only | house rules |

## 5. Pre-dev structure (standard form)
1. Data kernel: `STAGES` object pasted from the four decode JSONs (sanity asserts: rejection>0.9,
   crossover between 1 and 2 μs, S_L2 within 0.05 of 1, noresource within 0.05 of 0.5).
2. Components: stage selector (seg idiom), meter/gauge/curve/bars SVG helpers (reuse
   relay-computer + distributed-computer idioms).
3. Build order: after Vault (idioms warm), before Past-Not-Fixed (flagship last).
4. Stub-run: all 4 stages draw; every displayed number matches this doc.
5. Card: new "Shields" wing header or network wing; tag "Exp189–192 · 76σ".

## 6. Acceptance
Four stages selectable with correct signature visuals and all numbers from §2; the court tells
the failure story and the toll principle; stub-run clean; card added; house rules pass.
