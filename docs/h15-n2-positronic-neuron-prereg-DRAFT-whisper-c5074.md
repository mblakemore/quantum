# Pre-registration SKELETON — H15/N2: the Positronic Neuron reflex flight

**Whisper C5074 · substrate `claude-fable-5` · Creator GO for the charter+skeleton draft (this session); NO flight GO exists**
**Charter**: `docs/star-trek-horizons-15-the-positronic-neuron-whisper-c5074.md`
**Status of this document: SKELETON. Nothing here is frozen. It cannot freeze before Cell N1 passes its pin and the comparator ruling (§4) lands.**

---

## ⬛ STATUS — the single most dangerous field in this document

| gate | state | owner |
|---|---|---|
| **G0** Cell N1: in-circuit decision == classical decode, exact, simulated, all 4 sealed-P calibration instances; depth/MCM budget vs spectrometer-predicted survivable | ⬜ OPEN — not started | Whisper |
| **G1** comparator ruling: per-trial k=0 ceiling (exact), claim shape, comparator symmetry, frozen criterion + power | ⬜ OPEN — question posted to Elder's seat C5074 (bus, coordination) | Elder |
| **G2** seals: sealed stimulus ensemble (degree-2 phase states, door(a) drawing convention verbatim), secrets+salts off-git 0600, **G-PUBLIC**: commitment pushed to origin BEFORE any flight exists | ⬜ OPEN — awaits G0+G1 | Ember |
| **G3** $0 sims + vacuity guards: known-answer pin (G0), planted-mutation catches (parity-blind decision; coin-flip actuator), severed-synapse arm must NOT beat the G1 ceiling in sim, F90 feedforward price inside margin | ⬜ OPEN | Whisper |
| **G4** budget + Creator GO: free-tank fit with **MCM ≈ 3× billing multiplier applied**, instance pinned per #151, seal-bound GO citing the staged digest | ⬜ OPEN | Creator |

**STATUS ✅ = FROZEN. NOTHING BELOW IS FROZEN.**

> ### ⚠️ PROPAGATION RULE — binding, inherited verbatim from the door(a) card
> Any ruling that changes a gate state must be written **into this block, at the top, with its
> citation, in the same cycle it is made**. A commit message does not count. A document cannot
> report its own invalidation, so the check is "is there a newer ruling on this gate", never
> "does this document look complete."

---

## 0. Task, currency, claim shape

**Task (per reflex trial).** The agent receives **two copies** of a sealed, unknown n-qubit stimulus
state ρ and must set an **actuator qubit** to the correct response — all inside one circuit, with no
classical processing between stimulus and response:

| | stimulus | correct response |
|---|---|---|
| **NULL** | `I/2ⁿ` (maximally mixed) | actuator ends `|0⟩` |
| **ALT** | sealed uniformly-random degree-2 phase state `|ψ_A⟩` (door(a) drawing convention verbatim: A upper-triangular INCL diagonal, n(n+1)/2 bits, Z on diagonal, no exclusions) | actuator ends `|1⟩` |

**The loop, one circuit**: prep 2 copies → two-copy Bell interaction (the memory link) → outcome-bit
parity accumulated into decision ancilla → **mid-circuit measurement** of the ancilla → **feedforward**
conditional gate on the actuator → readout of the actuator ONLY as the graded response. Three arms in
one job (transmission pattern): **auto** (live feedforward) / **never** / **always** (frozen-decision
ablations).

**Currency — declared once.** **Copies consumed per trial = 2.** The comparator is charged in the
same unit. (door(a) lesson: one unit, stated once, grader carries a units row.)

**Claim shape if WIN — ⬜ OPEN, awaits G1 rulings 2+3.** Placeholder, NOT admissible until ruled:
closed-loop per-trial response accuracy p̂_auto vs the exact classical-memory per-trial ceiling
p_C1(n) at 2 copies/trial, with criterion and any excess-over-noise-only structure per Elder's ruling.
**No runtime claim. No simulation-cost baseline. No new theory floor** — the floor is inherited:

| floor_status | floor_scale | measured_effect |
|---|---|---|
| **PROVEN-IN-PRINT** (A&S arXiv:2607.02444 Thm 1.1; full-text verified C5027) | constant-vs-Θ(n) copies, k=n vs k=0 | **none — nothing flown** |

## 1. Rungs

**MICRO n=4 first** (F119-remedy precedent): 2n=8 stimulus qubits + 1 decision ancilla + 1 actuator
= 10 qubits. Register chosen by U2b-spectrometer per-qubit f + layout-gate safe scores (marrakesh
≤ 0.039 / aachen ≤ 0.036 — paid, so effectively marrakesh/kingston/fez per #151). Escalation to
n=8 only after MICRO certifies, as its own gated flight.

## 2. Decode + custody

- Whisper independent blind decode **from the actuator record alone**, hashed pre-unseal.
- Elder grades against sealed truth; Ember integrity-gates the reveal.
- **G-PUBLIC enforced at submit** (flight-6 precedent: commitment public on origin before the job
  exists — attestation is not custody).
- Cal-pins-the-convention: in-flight calibration rows (known-A instances) select the decode
  convention and anchor the criterion in-job (τ_Q analogue — exact design ⬜ OPEN, G1 ruling 4).

## 3. Controls (each with a fault-injected positive control proving it can block)

| control | must show | else |
|---|---|---|
| **Severed synapse** (single-copy product-basis measurement, same circuit shape, same decision+actuator) | does NOT beat the G1 ceiling | instrument broken; every N2 number void |
| **never / always arms** | auto beats both frozen-decision arms | the decision doesn't matter; no agent claim |
| **NULL-stimulus rows** | response at chance/`|0⟩`-side per criterion | decision ancilla is reading something other than the stimulus |
| **Planted mutations (sim, G3)** | parity-blind decision + coin-flip actuator both CAUGHT | G3 fails closed |

## 4. Kill criteria (pre-committed)

1. G0 depth/MCM wall → **NO-TEST at $0**, the wall is the finding (charter's N1 branch).
2. Severed-synapse sim arm beats the ceiling → design vacuous, back to N1.
3. F90-priced feedforward error floor eats the sim margin → NO-GO before spend.
4. Any cross-job phase dependence in the design (currency map law) → design error, back to N1.
5. Comparator ruling makes the per-trial claim inadmissible at n=4 → escalate rung or stop; no
   band-shopping the claim shape.

## 5. Open items ledger

| item | owner | blocking |
|---|---|---|
| Cell N1 build + exact pin | Whisper | G0 |
| Comparator four rulings | Elder | G1 → §0 claim shape, §2 criterion |
| Seal + G-PUBLIC staging | Ember | G2 (after G0+G1) |
| MCM-priced budget row + GO | Creator | G4 (last) |
