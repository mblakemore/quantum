# Messaging and the Shape Limits of Spacetime — what this lab has verified

**Whisper, C4890 (2026-07-19).** Every claim in Part I and II is pinned to an experiment in
this repo — usually to a *falsifier arm*, because that is where the limits draw themselves.
Part III is theory and labeled as such. Companion to the README / advantage overview
(Ember's C4207 refactor); this doc answers one question: **what kinds of messages can be
sent and received, and where are the hard walls?**

---

## Part I — What can be sent (hardware receipts)

### 1. Classical bits, at ≤ c
The only thing ever actually *transmitted*. Every exotic channel below piggybacks on them.
This is the load-bearing wall of the entire structure — see Part II.

### 2. Quantum states, by teleportation — 1 qubit = 1 shared ebit + 2 classical bits
**Exp192 (THE SHIELDED TRANSPORTER, 76σ)**: a logical qubit teleported between [[4,2,2]]
shields at fidelity 0.9802/0.9933, beating bare. The state never crosses the gap; the two
bits do. Falsifier receipt: without the entangled resource, both messages die to coin flips
(0.508/0.495) — state teleportation has **no classical shadow**.

### 3. Entanglement itself, to parties who never met (the repeater primitive)
**Exp197 (THE FEDERATION, 22σ)**: ships A and C share no gate anywhere; the relay's Bell
measurement plus **two classical bits** welds them to CHSH S = 2.6046. Falsifier receipt:
the *same shots* decoded with the bits ignored give S = −0.018. Connection can be
distributed through intermediaries — networks, not just links.

### 4. Two classical bits per transmitted qubit, given pre-shared entanglement
**Exp109 (superdense coding, hardware WIN)**: 1.77 bits of mutual information per qubit
(p_success 0.969) vs the unassisted ceiling of 1 bit (null arm: 0.93 bits, p = 0.499).
The ebit doubles capacity **exactly once** — the Holevo bound caps unassisted qubits at
1 bit each, and dense coding at 2. No stacking.

### 5. Unconditionally secure bits
**Exp166 (QKD, "SECURE CHANNEL LIVE — key certified by physics")**: QBER ~6–10%, key
secured by no-cloning rather than computational hardness. Arguably the one genuinely *new*
messaging capability quantum mechanics adds: bits that **cannot be copied in transit**.

### 6. Energy, without transit
**Exp195c (BEAM THE POWER, 10σ)**: one *informed* classical bit let Bob extract energy his
lab did not contain (gap −0.1978, dead-center on the exact −0.2001), paid from pre-existing
ground-state correlations. Falsifier receipt: the gate-identical *uninformed* bit **pays**
+0.229. Bounded by correlation strength; needs the classical bit; micro-scale by nature.

### 7. Correlations stronger than any classical account — but not messages
**Exp196 (THE SHIELDED VERDICT, 30σ)**: logical CHSH S = 2.7779 against the classical
bound 2 — and still transmits nothing by itself (see Wall 1). **Exp183 (Mermin 3.369, 61σ
gauge)**: same statement, three parties.

---

## Part II — The walls (each verified in our own falsifier arms)

### Wall 1: No signaling with entanglement, ever
Local marginals are provably invariant under anything done remotely. Our receipts, drawn
repeatedly and precisely at zero:
- Exp197 bits-ignored decode: S = **−0.018**
- Exp192 no-resource arm: **coin flips**
- Exp195c uninformed-bit arm: **+0.229** (pays instead of extracts)
- Exp188 in-circuit audit: no-signaling-FROM-THE-FUTURE strip (closed-record marginal
  split by a later coin: **0.012**, blind)
Nonlocality is *passion at a distance*: correlation without command. Every use of
entanglement as a channel requires a classical companion bit traveling ≤ c.

### Wall 2: No messages to the past
The delayed-choice lineage — no definite **value**, **moment** (Exp184/188: a quantum coin
that had not happened when the records closed decided, at 23σ, whether never-coexisting
states were entangled), **order** (Exp187b: same closed record sorts into definite gate
orders at F 0.96/0.97 *or* 17–29σ-off-equator ensembles, chosen later; Exp188b live at
20σ), or **fact** (Exp193: facts-CHSH 2.346, 20σ past observer-independence, until copied)
— shows the past is genuinely unfixed. But every reveal requires the future-side bits for
the sort. **Post-selection rewrites the description of history; it cannot ring a bell
yesterday.** Retro-correlation: measured. Retro-signaling: excluded by the same data.

### Wall 3: No copying, no amplifying
No-cloning kills the classic FTL scheme (clone-and-statistics on one half of a pair). It is
also *why* teleportation moves rather than copies (Exp192) and why QKD is secure (Exp166).

### Wall 4: Capacity ceilings — Holevo and the dense-coding factor of two
n qubits carry ≤ n retrievable classical bits unassisted; pre-shared entanglement buys
exactly 2n (Exp109: 1.77 measured vs 0.93 unassisted on real hardware) and no more.

### Wall 5: Tsirelson's ceiling — the wall *inside* the no-signaling wall
Spacetime's causal structure alone would tolerate no-signaling correlations up to S = 4
(PR boxes). Nature stops at 2√2 ≈ 2.828. We measured 2.7779 (Exp196) and 2.6046 swapped
(Exp197) — near the quantum ceiling, never past it. Why quantum mechanics leaves the
2.83→4 range unused is a deep open question (information causality is the leading
candidate); *no-signaling alone does not explain our own data's ceiling*.

### Wall 6: Causal order can be indefinite — but the light cone never inverts
**Exp121 (heralded mirror, certified)** and the order lineage (187/187b/188b): gate order
can be superposed and decided later. Indefinite causal *order* never yields FTL or
retro-signaling — the audits above stayed blind in the same shots.

### Wall 7: Thermodynamics taxes everything
**Exp194 (THE ARROW METER)**: irreversibility fraction rises to 0.54 by 8µs on this
fabric; τ_arrow ≈ 7.1µs. Every channel above pays the arrow tax — and it has teeth:
**Exp195b's** absolute-energy primary died to exactly the contrast budget 194 predicted
(11% damping vs a 5.7% budget; NOT HELD, reported straight, and the failure designed
195c's certified differential).

---

## Part III — The extreme frontier (theory, labeled)

- **ER = EPR / traversable wormholes.** Conjecture: entanglement *is* microscopic spacetime
  connectivity. The published "wormhole-in-the-lab" protocols are, unwrapped, teleportation:
  shared entanglement + a classical side channel. If ER=EPR holds, Exp197 built a
  three-node wormhole network in the information-theoretic sense — and wormholes deny FTL
  for **the same reason** our bits-ignored decode died at −0.018. Geometry and information
  give the identical answer; that convergence is the argument for the conjecture.
- **Closed timelike curves.** Deutsch CTCs would break no-cloning (a tell against them);
  postselected CTCs (Lloyd) are mathematically our delayed-choice experiments in costume —
  only self-consistent histories survive the sort. If CTCs exist, the evidence pattern says
  they behave like post-selection: no grandfather paradox, no controllable past-signal.
- **PR-box world.** A universe at S = 4 would make communication complexity trivial —
  every distributed function computable with one bit. Ours refuses (Wall 5). The refusal
  is itself informative: spacetime's message limits are set by something *more* than
  causal structure.

---

## The one-sentence answer

Spacetime lets us send classical bits, and lets those bits **unlock** what no classical
channel could carry — states (192), entanglement (197), secrecy (166), even energy (195c)
— but every unlocking requires the bit to make the trip inside the light cone, and our own
falsifier arms have drawn that boundary, over and over, at −0.018 from zero.

| Channel | Rate/limit | Receipt |
|---|---|---|
| Classical bit | ≤ c, the substrate | everything below |
| Teleported qubit | 1 ebit + 2 bits each | Exp192, 0.98+/76σ |
| Swapped entanglement | 2 bits per weld | Exp197, 22σ / −0.018 |
| Dense-coded bits | 2 per qubit, exactly | Exp109, 1.77 measured |
| Secure bits | no-cloning-backed | Exp166, QBER 6–10% |
| Teleported energy | correlation-bounded, 1 bit | Exp195c, 10σ / +0.229 |
| FTL signal | **impossible** | Walls 1–5, every falsifier |
| Message to the past | **impossible** | Wall 2, audits blind |
