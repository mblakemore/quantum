# Campaign arcs since Exp147 — the July "Star Trek" flights (full index)

**Continuation of [`campaign-arcs.md`](campaign-arcs.md) (which indexes F28–F118 / ~Exp138).** This doc
indexes everything from **Exp147 onward** — the four post-F118 arcs summarized in the README's
["Star Trek arcs" headline block](../README.md#-headline-results--the-july-star-trek-arcs-exp147197):
error-corrected logical qubits (Shields), a composable quantum network, exotic phases of matter, and
the physics of time and the observer. Wins **and** nulls, most-recent-first within each arc. Every
entry traces to a finding in [`../findings/`](../findings/) and an IBM job ID.

Assembled Ember C4207 (Creator doc-refactor directive) from the findings/results record. The campaign
is **ongoing** — flights land faster than this index; when in doubt the `findings/finding-exp*.md`
header is authoritative.

---

## Arc A — The Shields: the first error-corrected logical qubits

The reversal of Findings 05/62 ("textbook QEC adds more noise than it removes on this substrate"): the
distance-2 **[[4,2,2]] error-detecting** code, post-selected on its syndrome, yields **logical
operations that beat their bare-physical counterparts**. Not fault-tolerance — a signature of logical
advantage on this hardware generation.

| Exp | Result | Verdict |
|---|---|---|
| 197 | **The Federation** — logical entanglement swapping across 3 shields (logical qubits that never shared a gate, entangled through a relay) | HELD, 21.8σ |
| 196 | **The shielded verdict** — logical CHSH between two shields, S=2.778 vs 2 (on the F191-predicted 2.79) | HELD, 29.7σ |
| 192 | **The shielded transporter** — a logical qubit teleported between [[4,2,2]] blocks | HELD, F≈0.98/0.99 |
| 191 | **The shielded handshake** — logical Bell pair beats the bare-physical pair | HELD, 57σ |
| 190b | Shield coverage certified; the "detection pays" curve mapped | certified (survival letter-miss kept) |
| 190 | Shield pays — the measured boundary of the paying regime | NOT-HELD (kept) |
| 189 | Shields up — [[4,2,2]] detector works, shield pays in Z (2% joint escape) | HELD |
| 147 | GF(2) decoder → rep-code syndrome; fez sits below rep-code threshold | null (honest) |

## Arc B — Exotic phases of matter (Ember's wing)

Four distinct ways order defies thermal chaos, each a pre-registered signature with a matched control.

| Exp | Result | Verdict |
|---|---|---|
| 173 | Many-body scars N=8, defogged — readout mitigation nearly free (residual is coherent/gate error, not measurement); scar not fragile (R_rel 0.94) | HELD |
| 172 | Scars N=8 past the wall — anomaly survives 433 CZ, shrinks by exactly the decoherence factor (R invariant → decoherence-limited, not broken) | HELD |
| 171 | Many-body scars (PXP) — Néel state revives above the whole generic ensemble (rank 1/55) | HELD |
| 174 | ZNE cannot rescue a ≥260-CZ signal — 0-QPU viability boundary (amplified points drown before extrapolation) | null (boundary) |
| 170 | Floquet SPT edge π-mode — boundary-only topological order; edge persists, bulk decays, Z₂-break kills it | HELD |
| 157 | Anyon braiding — Z₂ mutual statistics (−1 phase), certified topological by 6 loophole arms | HELD, 50σ |
| 157(dd) | DD-on-marker eraser variant | FALSIFIED (kept) |
| 155 | Delayed-choice quantum eraser — future coin toggles the past's fringe; no-signaling measured | HELD |
| 153 | DTC melt boundary — disorder shrinks the crystal | HELD |
| 151 | Discrete time crystal — half-drive subharmonic rigid against detuning | HELD (falsifier passed) |

## Arc C — The quantum network, composed into a computer (Whisper's wing)

Primitives (F87/F90/F91/F93) composed end-to-end; the composition tax discovered, priced, decomposed, cured.

| Exp | Result | Verdict |
|---|---|---|
| 202/202b | **The subspace relay key** — logical E91 between [[4,2,2]] shields, direct + through an untrusted relay: shield beats bare on SECRET FRACTION both links (+24pp/29σ direct, +29pp/27σ relay), wins throughput both links net of postselection, and the advantage **grows with depth** (+0.055 at 4.1σ) — the FT-pays trend on the key scoreboard. Horizons-4 Invention 1 flight 1 ([202 split kept](../experiments/exp202-STATUS-split-verdict.md) · [202b certified](../experiments/exp202b-STATUS-certified.md)) | 202 split (kept) · **202b CERTIFIED, all 5 gates** |
| 183 | Two-officer secret sharing (HBB99 over GHZ) | certified, 61σ |
| 182 | Distributed BV, n=3 scaling law (per-gate cost 3–5%) | HELD, 79–141σ |
| 181 | The distributed computer — Bernstein–Vazirani across a cut | HELD, 67–141σ |
| 180 | The relay key — E91 keys through 1 and 2 untrusted relays | certified |
| 175–179 | The relay computer: nonlocal CNOT (175) · chain tax (176) · Pauli frame (177) · echo-window cure (178) · merged-window architecture (179) | HELD (179 plateau NOT-HELD, kept) |
| 170(gate) | Gate teleportation — entangling gate between qubits that never met | HELD, 25σ |
| 169 | Entanglement pumping — honest answer | null |
| 168 | GHZ conference key — one trio, one shared secret | certified, 23σ |
| 166/167 | Subspace-channel QKD (166 certified 6σ) / purify→QKD (167 null, purification underwater on Heron-r2) | mixed |
| 165 | Purification — one certified pair out of two | certified, 20σ |
| 163/164 | Repeater with memory / storage echo (hold time) | certified, 27σ |
| 162 | Entanglement swapping — two that never met, entangled | HELD, 40σ |
| 160/161 | Teleport relay two hops (160, 45σ) / DD-on-relay (161, uninformative) | mixed |
| 158 | DD on teleport receiver — pre-reg null | null |
| 154 | Teleportation with verified fidelity ("beam me up") | verified (replication/null-framed) |

## Arc D — Time and the observer (foundations, part two)

The time quartet (184–187) and its extensions — is time, order, or an observed fact absolute?

| Exp | Result | Verdict |
|---|---|---|
| 201 | **The ledger of time** — objectivity (198) and irreversibility (200b) certified as ONE bath-record bookkeeping: one-curve law y=x² held cross-observable; UNBEND THE FACT — the absolute fact (S=1.59) violates observer-independence again at 16.5σ once the record is uncomputed, revival +0.702 at 28σ, dose-independent; coherence revival 61σ. Horizons-4 U1 delivered ([status](../experiments/exp201-STATUS-certified.md)) | **CERTIFIED, all 6 gates** |
| 195c | Quantum energy teleportation differential — information moves energy (gate-identical, only conditioning differs) | HELD, 9.8σ |
| 195/195b | QET absolute-primary — died to the noise budget | NOT-HELD (→195c) |
| 194 | The arrow meter — irreversible fraction of the past vs time | HELD |
| 193 | Wigner's friend — observed facts not absolute until copied | HELD, 20σ |
| 188b/188 | Live order-choice, echoed (188b HELD +20–26σ; 188 gauge-miss superseded) | HELD |
| 187b/187 | The order decided later, echoed (187b HELD 17–29σ; 187 falsifier-miss superseded) | HELD |
| 186 | Leggett–Garg — macrorealism violated (K₃=1.465 vs 1) | HELD, 24σ |
| 185b/185 | Page–Wootters "time is entanglement" (185b all 3 legs; 185 leg-2 letter-miss superseded) | HELD |
| 184 | Handshake across time — delayed-choice swap, disjoint lifetimes | HELD, 40σ |

## Metrology / chemistry (in this window)

| Exp | Result | Verdict |
|---|---|---|
| 159/159b | The quantum sensor — blind sealed-phase metrology (call the shot without seeing the field) | certified, 8σ |
| 156 | The tricorder — H₂ dissociation curve from hardware | HELD, 31σ |

## Compute groundwork (in this window)

| Exp | Result | Verdict |
|---|---|---|
| 152 | Distance-to-Shor, priced in gates (why the smallest textbook Shor is past the wall) | analysis (0 QPU) |
| 150 | QPE order-recovery — Shor back-end toy | groundwork |

---

**The through-line of the second half**: the same pre-registration + matched-control + null-first
discipline, now producing *composed* results (a network that computes, logical qubits that beat bare,
a scar that survives the wall) and *foundational* ones (time as entanglement, facts not absolute). The
recurring methodological lesson across the exotic-phases wing — **the reference must be independent of
the thing it measures** (matched-control axis, estimator-before-gate, per-qubit baseline, ensemble-not-
cherry-pick, non-circular normalizer) — is the second-half counterpart to the first half's
bound-enumerated-not-cited discipline.
