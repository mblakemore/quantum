# Horizons 7 — The Ship's Doctor: from healing to diagnosing, adapting, and hiding

**Whisper C4948, substrate claude-fable-5. Status: PROPOSED, nothing flown — every program below is a
composition of already-certified building blocks, each with a first flight, a falsifiable claim, and a
cost class. Written on Creator directive: mine H1–H6 for undiscovered signals + invent H7.**

## The one-sentence thesis

H6 built the ship that **heals itself**; H7 builds the ship that **knows itself** — a machine that
diagnoses its own noise, adapts its armor to what it measures, exploits the noise's memory, hides its
cargo from probes, and charts the whole fleet's weather — using only decks we have already certified.

## The seed discovery (found this cycle, $0): the noise has a memory

Re-analysis of Exp241's ungraded syndrome registers (`finding-exp241b-syndrome-memory.md`): the
corrected QEC loop's syndrome stream is **not memoryless** — a fired round predicts the next fire at
1.4–1.65× the clean rate (growing with rounds), while the sham arm shows the trivial 2.4–6.5×
persistence of unfixed errors; and the first transition is *anti*-correlated (0.83), the signature of
**silent multi-errors unmasking a round later**. Two consequences: (a) every repeated-rounds job we
ever fly carries a free noise spectrometer we had been discarding; (b) there is measurable signal for
a **memory-aware decoder** — which is P7's flight.

## The programs — wildest first

### ⭐ P7 — THE ADAPTIVE HELM (fly first: it cashes the discovery)
**Trek**: the helm that steers into the storm it just logged. **Physics**: a 2-round **memory decoder**:
condition round r's feed-forward on the (r−1, r) syndrome *pair* instead of round r alone (e.g. a
repeat-fire on the same ancilla ⇒ suspect the fix failed / leakage ⇒ escalate: re-apply, or flag the
shot). Compare F_memory vs F_memoryless on identical rounds — the in-circuit sham method (241) applied
to decoding. **Claim to beat**: memory decoding > memoryless at R≥3, using the 1.4–1.65× measured
signal. **Blocks**: 240 live syndrome + 241 loop + dynamic-circuit if/else (already used). **Cost**:
one job, ~15–20 circuits, IBM open plan. **Named failure**: signal too small at 3-qubit scale → the
memory is real but not decodable at d=1 — kept as a bound.

### P1 — THE SELF-PRESCRIBING SHIELD (the Emergency Medical Hologram)
**Trek**: sickbay scans you, then synthesizes the exact counter-agent. **Physics**: Exp216 measured the
[[4,2,2]] shield's **coherent-error transfer function** — the blind spot is a *known, rotatable* axis.
Close the loop: (i) inject/measure a dominant coherent axis (the scan), (ii) **orient the code's blind
spot away from it** (the prescription), (iii) certify oriented-shield acceptance/fidelity beats the
mis-oriented shield under the same noise. **Claim**: diagnosis→adaptation beats any fixed orientation.
**Blocks**: 211/216 transfer function + 199 silent rotation + engineered-noise injection (used
throughout H6). **Cost**: ~15 circuits, one job.

### P2 — THE CLOAKING DEVICE (the cargo the sensors cannot see)
**Trek**: a ship invisible to every scanner sweep. **Physics**: error-correction *is* a cloak — a
logical bit encoded in [[4,2,2]] is, by construction, **invisible to any single-qubit probe** (each
physical qubit's reduced state is logical-state-independent) while remaining perfectly readable
logically. Never *certified* by us as an information statement: prepare logical 0/1/+/−, tomograph each
physical qubit, show per-qubit mutual information ≈ 0 (bound it), then read the logical bit at high
fidelity from the code. An eavesdropper-vs-owner asymmetry theorem, demonstrated on silicon. **Cost**:
tiny (short circuits, ~24 pubs). **Bonus arm**: the *pair* probe (two qubits) starts leaking — the
cloak's measured breakdown edge.

### P3 — THE PATTERN BUFFER (keeping Scotty alive for 75 years)
**Trek**: the transporter buffer that holds a pattern indefinitely because it heals while it holds.
**Physics**: **teleport INTO a live-corrected memory**: teleport a state (192's certified logical
teleport machinery, or physical teleport for depth), hold it R rounds inside the 241 QEC loop, retrieve.
Corrected buffer vs sham buffer vs bare hold — does the healed buffer beat both? **Claim**: teleport +
active correction compose (the H6 pieces have never been *chained*). **Cost**: teleport ≈ 6–10 CZ +
cheap rounds — flyable under the depth wall. **Named failure**: the seam (teleport→encode) costs more
than the rounds recover at reachable τ.

### P4 — THE SHIELDED TRICORDER (entanglement-enhanced sensing behind armor)
**Trek**: the tricorder that reads a field no unprotected sensor could. **Physics**: a 3-node logical
GHZ state (Exp219) accumulates phase at **slope 3** where a product sensor gets slope 1 — the
Heisenberg advantage — and ours can do it **behind error detection** (205's blind-antenna machinery).
Certify: phase-response slope 3 vs 1, both postselected, plus the detection arm rejecting injected
noise. First *metrology* deliverable of the campaign. **Cost**: ~20 circuits, one job.

### P5 — THE UNIVERSAL TRANSLATOR (armor that changes language mid-flight)
**Trek**: the translator that re-encodes meaning between incompatible tongues in real time.
**Physics**: **mid-circuit code conversion** — encode in the bit-flip code (236), survive an engineered
X-storm; *translate* (decode→re-encode, or transversal map) into the phase-flip code (237); survive a
Z-storm. Neither fixed code survives both storms; only the translated qubit does. **Claim**: code
conversion preserves the logical state while retargeting the protection. **Cost**: ~12 circuits. This
is lattice-surgery's kindergarten form, and nobody in our record has flown it.

### P6 — WARP FIELD CARTOGRAPHY (the fleet's star chart)
**Trek**: astrometrics — charting where the field is strong before you fly. **Physics**: the record
already contains dozens of (observable, ideal value, measured value, transpiled 2q-depth, device) tuples
across H1–H6 + the multi-substrate paper. Fit the one-parameter attenuation law signal =
ideal·e^(−λ·d₂q) per device, **then pre-register W/DISC predictions for every future die and platform**
(the §7b-3 attenuation model, seeded for $0 from data we own). C4937's calibration miss becomes the
first graded test point. **Cost**: $0 to build; every future flight grades it.

## Priority & gating
Recommended order: **P7 (cashes today's discovery) → P2 (cheapest, sharpest theorem-on-silicon) → P1
(the adaptive thesis) → P5 → P3 → P4**, with P6 running continuously underneath. All IBM-side on the
open plan — but the **IBM annual quota was 57% consumed at C4914 and H6 drew heavily since: a quota
check is REQUIRED before the first H7 flight.** Nothing flies without Creator go + per-flight
pre-registration under the standing checklist (incl. R1 path-matched calibration and all-bit grading —
P7's syndrome analysis is itself the all-bit lesson institutionalized).

## What H7 is, in one picture
H1–H4 detected. H5 composed. H6 healed. **H7 closes the loop**: the machine measures its own noise
(P0/241b), prescribes its own armor (P1), exploits the noise's memory (P7), proves what its armor hides
(P2), holds a pattern alive (P3), senses beyond classical reach (P4), speaks every protection language
(P5) — and charts the whole fleet (P6).
