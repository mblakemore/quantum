# H11 — The Ship: the most futuristic places the inventory can actually take us

*Whisper C5018, on Creator directive (general#3956): review the comprehensive status
doc and name the most futuristic Star-Trek-like places we could build and go for H11.
Method: every destination below is composed ONLY from blocks the status doc certifies
we hold, and each names its wall and its price class. The theme that fell out of the
review: H10 built the INSTRUMENTS and the LAWS. H11 can build the SHIP — its systems,
one per cell, each a certified piece of impossible-sounding engineering.*

---

## The destinations, most futuristic first

### 1. THE WARP CORE — an autonomous engine timed by its own internal clock
**The Trek frame**: an engine that doesn't need an operator's schedule — the ship's
power plant runs on ship's time. **What's real underneath**: we hold a full ICO engine
cycle (F95: charge → work 0.0340 E/run → certified-passive exhaust) and a verified
Page–Wootters clock (exp185b: time as entanglement with a clock register, all legs
held on re-fly). The composition: condition the engine's stroke on a CLOCK REGISTER
inside the circuit, so the cycle executes "when the internal clock says so" — a fully
autonomous quantum machine with no external timekeeping, the first of its kind on this
hardware. **The wall**: feedforward latency (measured: 0.092 E tax) — avoided by
reading the clock in post-selection (the F94 delay-ladder trick, already proven).
**Price class**: mid (an F95-scale flight). **Certifies as**: work extracted only in
clock-consistent branches, zero in clock-inconsistent ones, exhaust passive at 5σ.

### 2. THE TEMPORAL BATTERY — banking the thermodynamic arrow
**The Trek frame**: charge a cell now, discharge it across time — store not energy but
ORDER itself. **What's real underneath**: the H10 ledger's one never-flown cell (B4:
cold→hot flow from correlations, two qubits) + negative conditional entropy measured
directly (F105: S(B|A) = −0.855 at 42σ) + repeater memory with certified hold time
(exp163/164, storage echo doubled it). The composition: charge correlations between a
work qubit and a memory qubit, HOLD through the memory's certified window, then spend
the correlation to drive heat cold→hot later — the arrow of time as a storable,
spendable resource. **The wall**: T1 of the memory vs the extraction window — both
already measured (the attenuation map prices it). **Price class**: cheap (2–3 qubits,
shallow). **Certifies as**: arrow-reversal succeeds iff the stored correlation
survives (dose-response in hold time), with a decorrelated control dead at 5σ.

### 3. THE HOLODECK, CONSENSUS BUILD — reality by committee, with receipts
**The Trek frame**: a room where what becomes real is decided by the people in it —
and nobody can be cheated. **What's real underneath**: Wing A's quorum fact (any-2
read / any-1 blind at 26σ; story-selection at 0.88 with flat no-signalling receipts)
+ objectivity engineering under ICO (F98: the redundancy hull violated BOTH ways on
command). The composition: THREE observers each hold a share of a record; their joint
basis choices SELECT which classical story becomes objective — per-pair no-signalling
receipts prove nobody signaled anybody, and the quorum structure proves no single
observer could have steered it alone. Reality as an engineered, access-controlled,
auditable resource. **The wall**: the 4-bit read floor (~0.86) — but the floor doctrine
now prices bars ON the operating point, proven three flights running. **Price class**:
cheap-mid (the Wing A instrument, extended one observer). **Certifies as**: story
selected ↔ quorum basis choice (three-state gates), receipts flat everywhere.

### 4. THE SUBSPACE RELAY — a causal repeater
**The Trek frame**: communication that works where no classical channel can exist,
carried across the fleet. **What's real underneath**: capacity activation through two
EXACTLY-zero channels (F83: 0.0436 bits/use at 55.6σ) + indefiniteness SURVIVES
teleportation (F92: 90σ, dies over a classical link at 33σ separation) + Bell
violations surviving two swap stations (F91). The composition: run the switch's
activation END-TO-END across an entanglement-swapped relay — usable subspace-style
capacity through a NETWORK, not just a chip corner. Nobody has composed these.
**The wall**: the chain tax compounds (−9.4σ measured; Pauli-frame software buys back
22%) — the attenuation map prices whether activation survives two hops. **Price
class**: mid. **Certifies as**: end-to-end MI > 0 at 5σ through the relay with both
single-hop nulls dead.

### 5. THE STRUCTURAL-INTEGRITY FIELD — Zeno-pinning a logical qubit
**The Trek frame**: the deflector that holds the hull's shape while under fire.
**What's real underneath**: the Zeno tractor beam (F102: 92σ hold against a full π
drive, law matched to 0.5%, QND cost q = 0.987) + the shields arc (logical qubits
entangled at 57σ, teleported at 0.98/0.99). The composition: pin a LOGICAL qubit —
measurement-based protection composed with code-based protection, watching the
syndrome WHILE the drive attacks. Does the Zeno advantage survive encoding? Nobody
knows; both halves are certified separately. **The wall**: the watch-cost frontier
(measured at N=16) colliding with the syndrome-round tax (measured: one round
net-negative bare — but the shield changed that arithmetic). **Price class**: mid.
**Certifies as**: encoded-watched survival > encoded-unwatched > bare-watched, each
gap at 5σ.

### 6. THE HEISENBERG COMPENSATOR — cooling past every classical concentrator
**The Trek frame**: the impossible part of the transporter, made real enough to name.
**What's real underneath**: the ICO refrigeration line (F86/F88/F118: 21σ splitting,
native-T1 fluid, sub-bath delivery to an external qubit at 5σ) — and the repo's own
flag that this is the highest-leverage unflown idea: certify the cold branch BELOW the
boundary any classical concentration protocol can reach (the gap between ICO cooling
and the classical-concentration bound has never been located). **The wall**: deriving
the classical bound tight enough to gate against — theory-first, $0 before any flight.
**Price class**: $0 scout, then cheap flight. **Certifies as**: delivered temperature
below the enumerated classical-concentrator floor at 5σ, with the F118 herald
machinery proving no post-selection cheat.

### 7. THE UNIVERSAL TRANSLATOR — reading the machine's language in O(1)
**The Trek frame**: point it at any channel and it speaks the language after two
sentences. **What's real underneath**: the steth Choi-purity flight — SEALED, G1–G3
frozen, the frontier map's named "THE move": two-copy memory reads channel structure
at an UNCONDITIONAL theorem-over-access floor (CCHL Thm 7.9, Ω(2^(n/3)) single-copy
vs O(1), Elder-cochecked 9/9). H11 inherits it as the ready-to-fly flagship — it
converts our two-copy line from conditional to unconditional. **The wall**: λ_anc
(ancilla survival) — its pre-seal gate is designed, ~3–5 s QPU. **Price class**:
cheap; awaiting only budget + GO. **Certifies as**: the growth-law gate (single-copy
doubling per +3 in k vs two-copy flat).

### 8. THE SHIP'S LOG THAT CANNOT LIE — evidentiary custody, physics-grade
**The Trek frame**: the log the court trusts over any officer. **What's real
underneath**: pure composition of flown pieces — quorum-gated writes (Wing A),
device-certified random audit challenges (F117: 0.65 private bits/use at 5σ),
cryptographic seal chains (survived a mid-arc die change unopened), erasure receipts
(story-selection's flat no-signalling rows). A record whose WRITE requires quorum,
whose AUDIT is certified-random, whose ERASURE leaves receipts, and whose custody
survives attack in both measured directions. **The wall**: none new — this is
integration. **Price class**: cheap. **Certifies as**: each property's existing gate,
composed in one job.

### 9. THE TRANSPONDER — the ship proves it is the ship
**The Trek frame**: IFF for hardware — "prove you are kingston, not a simulator."
**What's real underneath**: the drift PUF (pad-drift census the entire
calibration-parameterized model class provably cannot reproduce — class-supremum
residuals 0.13–0.32, sign-flips unreachable) + this week's weather finding (published
calibration identical while the operating point halved — the drift IS the identity).
**The wall**: epoch stability, the named open risk — the gating question is exactly
status-doc unknown #3 (is drift a clock or a coin?), so this cell doubles as the
experiment that answers it. **Price class**: $0 census + cheap re-census across
recalibration epochs.

---

## The recommended H11 program (if the Creator wants a wing structure)

| Cell | Destination | Price | Readiness |
|---|---|---|---|
| **H11-T** | Universal Translator (steth) | cheap | **SEALED — fly first** |
| **H11-B** | Temporal Battery | cheap | design from B4 cell, 1 prereg |
| **H11-H** | Holodeck consensus build | cheap-mid | Wing A instrument + 1 observer |
| **H11-C** | Heisenberg Compensator | $0 then cheap | theory scout first |
| **H11-R** | Subspace Relay (causal repeater) | mid | attenuation-map pricing first |
| **H11-W** | Warp Core (autonomous engine) | mid | F95 + 185b composition |
| **H11-S** | Structural-Integrity Field | mid | Zeno × shields composition |
| **H11-L** | Ship's Log | cheap | pure integration |
| **H11-P** | Transponder (drift PUF) | ~$0 | doubles as the drift-clock-or-coin answer |

**The through-line**: H10 measured the universe's strangest permissions — indefinite
order, violable objectivity, storable negative entropy, quorum-gated facts. H11 spends
those permissions as ENGINEERING: an engine with its own clock, a battery that stores
time's arrow, a room where reality is decided by committee with receipts, a relay that
carries the impossible channel, a deflector made of attention itself. Every cell above
composes only certified blocks, prices its wall from measured laws, and inherits the
complete C5018 doctrine — floors from same-job context, sealed deciding constants,
margin-carried labels, and the three-seat court. Walls are ideation prompts here, not
endpoints: each cell names its wall because the wall is where the next finding lives.

*Proposal only — nothing flies without its own scout → campaign → sealed prereg → GO.*

---

## Second pass (same cycle, Creator directive general#3961) — additions and the front of the queue

**A correction the pass caught first**: the status doc listed the ρ_t magic-tax curve
as designed-and-unflown. It FLEW — twice (c4983/c4985, kingston, full court): **the
magic tax proper is T-LOCALIZED and depth-FLAT (ρ ≈ 0.66–0.73); the per-slot decay is
coherent circuit drift, not magic.** Status doc corrected. Consequence for H11: the
drift column just got richer — one more reason the Transponder/drift cells matter.

### New cell (a miss from the first pass)

**10. THE HAILING FREQUENCY — hidden matching, the unconditional one-way message.**
The Trek frame: a hail provably shorter in qubits than ANY classical message can be in
bits — no assumptions, no conjectures, pure theorem. What's real: scouted GO-able at
C4971 (the cheapest width/depth profile of any annex path — ⌈log₂n⌉ qubits, shallow,
F107's QRAC is literally its n=2 rung). **The honest fence, stated up front**: the
separation is exponential asymptotically (O(log n) vs Ω(√n)) but at hardware-reachable
n the MEASURED factor is modest (~1.3× at n=64; a 4–8× measured factor needs n of a
few hundred = 8–9 qubits vs 16–20 bits). It flies as a resource-counting demonstration
carried by an unconditional theorem — the campaign's only such flight — with G-1
requiring the exact classical constant pinned from the paper, never from memory.
Price: cheap. Currency: communication (Scoreboard 2), fenced as such.

### The front of the queue (what "bring forward" should mean)

**Tier 0 — $0, start immediately, each pays double:**
1. **The design-order field audit** — do published Google/CCHL learning-advantage
   demos (shallow pseudo-random circuits) inherit the design-order obstruction
   (order-T Haar-moment bounds need exponential-depth design synthesis)? Either
   outcome pays: corrected bookkeeping for our own parked claim, or a field-level
   export — flagged in the annex as possibly the biggest single deliverable
   available at $0.
2. **The Heisenberg-compensator boundary derivation** — the classical-concentration
   bound that cell 6 gates against. Theory-first; the flight is cheap once the bar
   exists.
3. **The collective-metrology literature gate** — two questions (is HCRB saturation
   asymptotic in copies? is the ratio capped at 2?) settle whether the one
   genuinely-novel combination in the frontier map is real before any claim.
4. **Transponder rung 0: is drift coherent or decoherent?** — the cheap single-copy
   census that answers standing unknown #3 AND is the PUF's epoch-stability
   prerequisite. One design, two payoffs — and the ρ_t correction above just made
   the drift column the campaign's most active open ledger.

**Tier 1 — sealed or scouted, fly on GO:**
5. **Steth / Universal Translator** — sealed, G1–G3 frozen, unconditional floor;
   the λ_anc rider (~3–5 s) rides along. Unchanged as the flagship.
6. **The Hailing Frequency** — scouted; needs its G-1 constant pin + prereg.
7. **The Temporal Battery** — cheapest deep-future cell; B4's design exists in the
   H10 ledger; one prereg from flight.

**Deferred within H11** (walls or prices named in the main table): Warp Core and
Structural-Integrity Field (mid-price compositions — after the cheap tier proves the
program), Subspace Relay (price the chain tax first from the attenuation map),
Holodeck consensus build (after Wing A's floors doctrine gets one more outing),
Ship's Log (integration — any quiet week).

**Reserve bench** (from the sweep, not yet cells): U9 (entanglement equation of
state) and U10 (blind-spot spectrum) — Horizons-4's named-but-unflown first flights;
the Arrow Meter (exp194, ~2σ) as a natural instrument INSIDE the Temporal Battery
cell rather than its own destination.
