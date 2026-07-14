# How much randomness a chip can certify — and where it evaporates

`Findings F115 / F116 / F117`  ·  `Experiment Exp137 (assemblage tomography → SDP randomness)`  ·  `Backend ibm_marrakesh (Heron r2)`  ·  `Job d9ansru6hjac73fenigg`

> **✓ ONE-SIDED-DI RANDOMNESS CERTIFIED — 0.65 private bit/use at 5σ · full-DI quarantined**

This sheet is the source-of-truth specification behind the interactive exhibit. Every number on the exhibit page is drawn from here; every number here is drawn from the hardware records `results/exp137_hw_results.json` and `results/exp137_jobids.json`, and the campaign finding rows for F115 / F116 / F117. The top rung is a labelled null: we did **not** perform full device-independence.

## 1 · The idea, in plain language

Random numbers are only as trustworthy as the **assumption** behind them. Climb a ladder: the higher you go, the **less** you trust your devices — and the **more** you demand of the hardware. At the bottom you trust the box completely and get a full random bit. At the top you trust **nothing** — but that demands the two measurement sites cannot signal to each other, and on **one chip** they can. Somewhere in the middle is the rung where the number is both **strong** and **real**. This exhibit finds it.

> **The three rungs**
> **Full trust** → 1 Born bit/qubit, but a compromised device could hand you anything. **One-sided device-independence** → you trust only your **own** measurement; the partner is a black box. **Full device-independence** → you trust nothing at all — the strongest security, and the one this chip cannot deliver.

## 2 · What we measure — and the method

Three witnesses, one per rung, each graded against the bound its assumption sets:

- **CHSH** `S` (F115) — the quantum-behavior witness. Over the local-hidden-variable bound `S = 2` it proves the device is behaving quantumly. Under **full trust** this only **health-checks** the box; the random bit comes from the trust, not from `S`.
- **CJWR steering functional** `S₃` (F116) — over the local-hidden-state (unsteerable) bound `1.0`, it certifies the state is steerable ⇒ entangled while trusting **only Bob's** measurements.
- **Assemblage tomography → SDP** (F117) — Alice's 3 untrusted settings × Bob's 3 trusted tomography axes reconstruct the assemblage; a semidefinite program projects it to the nearest valid (no-signaling) form and solves the guessing-probability SDP for a rigorous **min-entropy** `H_min`. That is the certified randomness.

## 3 · Pre-registered gates (frozen before flight)

- **WITNESS** — CHSH over the LHV bound: `S > 2`. PASS — `S = 2.7522 ± 0.0141`, **53σ** (97.3% of Tsirelson 2.8284); no-entanglement null `S = 0.036` (dead).
- **W1_STEERING** — One-sided-DI steering over the unsteerable bound: `S₃ > 1.0`. PASS — `S₃ = 1.6813 ± 0.0071`, **96σ** (97% of √3); separable-faking null `S₃ = 0.025` (dead).
- **CERTIFIED** — Randomness certified: `H_min − 5·SE > 0`, pre-filed band [0.45, 0.70]. PASS — `H_min = 0.6823 ± 0.0063` ⇒ certified **0.6509 > 0**, HIT at top of band.
- **FULL-DI** — No certified-bits gate frozen — the DI quantity is QUARANTINED: no-signaling is unmet on one shared-control chip.

## 4 · The measured data — the three rungs

| rung · trust assumption | randomness | measured witness | significance | status |
| --- | --- | --- | --- | --- |
| Full device trust | 1.00 bit/qubit (Born) | CHSH S = 2.7522 ± 0.0141 | 53σ | health-check only |
| One-sided-DI | 0.65 bit/use (certified) ▲ | S₃ = 1.6813 ± 0.0071 · H_min = 0.6823 ± 0.0063 | 96σ / 5σ | RIGOROUS |
| Full device-independence | 0.5928 bit/use (counterfactual) | DI bound — no-signaling unmet | — | EVAPORATES ✕ |

▲ = the rung a single chip genuinely holds. The certified **0.65** is `H_min − 5·SE = 0.6509`. Near-ideal steering correlations (X 0.969 / Y −0.969 / Z 0.974); reconstructed `S₃ = 1.6876`; separable null `H_min = 0` (adversary certain); residual no-signaling violation `0.0032`; sentinels 0.994 / 0.987. The rigorous value **beat the Werner model** (0.682 > the 0.656 isotropic-noise estimate) — the real state is closer to ideal in the certifying directions than noise assumes.

## 5 · Scope & caveats — the rung that evaporates is the point

- **Full-DI is unsupportable on one chip — stated, not hidden.** Device-independence requires **no-signaling** between the two measurement sites. On a single chip the two qubits share control lines, so a **deterministic** device could output `S = 2√2` at **zero** entropy. The `0.5928` bit/use is therefore a **labelled counterfactual** — a what-if, never a certificate. A real full-DI number needs space-like separation, off-chip. **We did not perform it.** This is categorically stronger than qualifying an interpretation: here the DI **quantity itself** evaporates.
- **One-sided-DI is the rigorous rung.** Its assumption (trust only Bob) is **exact at the logical level** — `Tr_A(U_A ρ U_A†) = Tr_A(ρ)` — failing only via physical crosstalk. Faking `S₃` needs a ~0.68 correlation excess, but the only on-chip mechanism (Alice-setting crosstalk back-acting on Bob) is measured at **~1%** across the campaign's own F55 / F56 records. 1% cannot fake 0.68 (the null at 0.025 confirms).
- **Not loophole-free.** Locality is open and crosstalk is **bounded, not closed**. The one-sided-DI gate is named `W1_STEERING_ONE_SIDED_DI` precisely so it is never misread as full device-independence.

## 6 · Provenance

- **Job:** d9ansru6hjac73fenigg (Exp137, assemblage tomography) · **Backend:** ibm_marrakesh (Heron r2)
- **Records:** `results/exp137_hw_results.json` · `results/exp137_jobids.json`
- **Finding rows:** `docs/campaign-arcs.md` — F115 (CHSH + three-tier scope correction), F116 (one-sided-DI steering, 96σ), F117 (rigorous one-sided-DI randomness, 0.65 bit/use)
- **Family:** Wing IV, The Advantage Ladder · F115 quarantined the DI number, F116 delivered the steering rung, F117 the certified bits from the measured assemblage

---

*Rendered from [`demo/trust-ladder/spec.html`](spec.html) — the interactive exhibit is at [`demo/trust-ladder/`](index.html). Part of [The Quantum Museum](../).*
