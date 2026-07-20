# P6 — THE FEDERATION COMPUTER: distributed error-corrected computation (plan)

**Whisper C4906, 2026-07-20. Substrate `claude-opus-4-8`.** Horizons-5 Program 6 pre-dev plan.
Written on the Creator directive "P6 distributed logical — create a plan, revisit for gaps + add
pre-dev planning structure, then fly it." This is the planning half; the first flight (Exp217)
is specified here and flown separately.

---

## 1. The vision

197 (Federation) entangled three [[4,2,2]] shields that never met — welded end-to-end by the
relay's **two classical bits**, applied as a software Pauli frame at decode (no feed-forward).
206/213/214 (the Full Replicator) ran the entire BGK Clifford family *inside one shield*,
error-corrected, logical-beats-bare. **P6 composes them: a logical two-qubit gate between qubits
living in two DIFFERENT shielded nodes, executed with only in-block gates + a shared logical
resource + classical bits — the first distributed error-corrected computation.**

The organizing question: *can a computation be split across a cut, error-detected end to end,
and still beat the bare (unshielded) distributed version?* If yes, the network stack (repeater
arc, 175–197) and the logical computer (206–214) fuse into one fault-tolerant distributed
machine.

---

## 2. What we stand on (every layer certified)

| layer | flight | what it gives P6 |
|---|---|---|
| logical Bell pair across shields | **197** Federation (22σ) | the shared resource + the weld-by-classical-bits trick, no feed-forward |
| permuted-wiring transversal CNOT | 191/197 | zero-cost cross-block handshake (SWAP = code automorphism) |
| in-block logical CZ = S⊗4 | 206/214 (C4901 audit) | the computational gate, zero 2q inside a block |
| logical S̄ (teleported + in-block) | 213/214 | universal Clifford per node |
| software Pauli frame at decode | 197/199 | terminal correction instead of feed-forward |
| shielded relay through untrusted node | 202 | the cut is a relay, not a wire |
| depth-check-before-submit discipline | 213→216 (3 consecutive) | feasibility gate reformed |

**Key inherited move (197):** the relay's classical bits weld the two halves *at decode* as a
software Pauli frame — no mid-circuit feed-forward. P6's first flight must keep that property:
the distributed gate is the **last** operation before measurement, so its Eisert-protocol
corrections are terminal Paulis absorbable into the decode frame. This is the design constraint
that keeps it shallow and hardware-honest.

---

> **STATUS (C4906): Exp217 CERTIFIED** — flown as a distributed logical **CNOT** (crisper truth
> table than the CZ phase, and H-free). Job `d9emnnineu4c739okjn0`, ibm_fez. Verdict G1∧G2∧G3
> HELD: truth table 0.992 (627σ), shield-beats-bare +0.056 (37.7σ), frame-off falsifier 0.496.
> The coherence witness moved to **flight 2** (3-block architecture) — the 191-map shared-q0
> structure forbids reading a data qubit and its in-block ebit in incompatible bases. See
> `experiments/exp217-STATUS-certified.md`.

## 3. The first flight — Exp217: THE DISTRIBUTED LOGICAL CZ

**Claim to test:** a logical CZ̄ between control d_A in shield A and target d_B in shield B,
executed with **no gate ever crossing the A–B cut** — only in-block gates, a shared logical Bell
pair (e_A in A, e_B in B), terminal measurement of the e-qubits, and a software Pauli frame from
their two classical bits — acts as the correct logical CZ on all four logical inputs, AND the
shielded distributed gate beats the bare (physical, unencoded) distributed gate.

### 3.1 The gadget (non-local CZ, terminal-frame form)

Standard non-local CZ (Eisert–Jozsa–Wilkens) needs 1 shared ebit + local CZs + 2 measurements +
Pauli corrections. Placed as the FINAL logical gate, the corrections commute to the end and become
a decode-time Pauli frame (the 197 trick). Per-node, all operations are in-block logical Cliffords
already certified: logical CZ = S⊗4, logical CNOT = permuted-wiring transversal, X̄/Z̄ measurement
= transversal. The A–B cut carries only the pre-shared Bell pair (made once, à la 197) and 2
classical bits at the end.

### 3.2 Inputs and verification

Prepare d_A, d_B in each of the 4 logical basis states {|0̄0̄>, |0̄1̄>, |1̄0̄>, |1̄1̄>} and in the
|+̄+̄> superposition. CZ̄ is diagonal: it must (a) leave all computational-basis inputs' populations
unchanged, (b) impart the −1 phase only on |1̄1̄>, detectable as a Z̄_A→X̄ / stabilizer-parity
signature on the |+̄+̄> input (CZ̄|+̄+̄> is entangled: measuring both in X̄ gives correlated parity).
The crisp scalar: **the induced CZ̄ phase measured on the superposition input**, and the
truth-table fidelity over the 4 basis inputs.

### 3.3 Frozen gates (to be finalized at build, formula-frozen pre-submit)

- **G1 TRUTH-TABLE:** basis-input logical populations match ideal CZ̄ to ≤ 0.10 (diagonal gate
  leaves populations fixed; this is the "does nothing wrong on the diagonal" check).
- **G2 THE PHASE:** on |+̄+̄> input, the CZ̄-induced correlation (⟨X̄_A X̄_B⟩ or the parity signature
  distinguishing CZ from identity) is present at ≥ [band] and ≥ N σ over the no-gate control.
- **G3 NO CROSSING GATE:** an in-decode falsifier — the same shots decoded with the two relay
  classical bits IGNORED collapses the gate (the 197 falsifier form: the weld IS the bits).
- **G4 SHIELD BEATS BARE:** shielded distributed CZ fidelity − bare distributed CZ fidelity > 0
  at ≥ N σ (the P6 hardware thesis; error detection pays for distributed depth, 197 trend +0.240).
- **G_ACC:** joint two-block acceptance in a pre-registered band (197 gave 0.60–0.66).

Registered verdict = G1 ∧ G2 ∧ G3 ∧ G4.

### 3.4 Budget predictions (C4887, filed pre-submit)

To be filled from the transpiled depth-check. Prior: 197's two-block joint acceptance 0.60–0.66;
shield-beats-bare advantage grows with depth (191 +0.07 → 197 +0.240), so predict the distributed
CZ advantage ≥ +0.05.

---

## 4. Gap review (revisit for gaps)

Ran the roadmap's P6 sketch against the certified building blocks. Gaps found and closed in this
plan:

1. **Feed-forward gap.** Roadmap said "welded by classical bits" but didn't pin *when*. GAP: a
   mid-computation distributed gate needs feed-forward (illegal terminal-only). CLOSED: constrain
   Exp217's distributed gate to be the LAST gate, so corrections are terminal Paulis → decode
   frame (197 property). Distributed gates mid-circuit are deferred to a later P6 flight that
   needs real feed-forward (kill-criterion K3 below).
2. **Qubit-count gap.** Two data blocks (8) + a shared Bell resource risks >12 physical qubits.
   GAP: depth/width feasibility unknown. CLOSED-BY-PROCESS: the build's transpile depth-check is
   the go/no-go gate (K1); if width/2q depth exceeds the confident band, fall back to the minimal
   form (one logical qubit per node, one ebit) or register-and-defer.
3. **"Beats bare" definition gap.** Distributed BV (roadmap's first choice) has a diffuse
   fidelity metric at small n (the F113 fence). GAP: weak verdict. CLOSED: switched the first
   flight from distributed BV to the **distributed CZ truth-table + phase**, which has a crisp
   4-input truth table and a single phase scalar — a sharper verdict than BV's population-over-floor.
   Distributed BV becomes flight 2 once the CZ primitive is certified.
4. **Composition-tax gap.** 175–179 showed composition depth inflates error. GAP: unpriced. CLOSED:
   G_ACC band carries the tax explicitly, and G4 measures the net (shield advantage AFTER paying
   the tax) — the honest scoreboard.
5. **Automorphism-reuse gap.** 197's permuted-wiring CNOT is per-block; does it compose with the
   cross-cut resource? CLOSED: yes — the cross-cut carries only the Bell pair + bits, never a gate,
   so each node's internal gates are exactly the certified in-block set. No new primitive needed.

---

## 5. Pre-dev planning structure

### 5.1 Seven-stage pipeline (Horizons-5 standard)

1. **Derive** — write the non-local CZ terminal-frame algebra; prove corrections are terminal
   Paulis (paper check, this cycle / next).
2. **Selftest** — statevector-exact `--selftest`: CZ̄ truth table + phase on the simulator, decode
   frame reproduces ideal. MUST pass before any hardware thought.
3. **Depth-check** — transpile to backend, count 2q gates + width. GO iff within confident band.
4. **Freeze** — formula-freeze gates + budget predictions, git commit pre-submit.
5. **Fly** — submit, write manifest immediately after job_id exists (Exp201 lesson).
6. **Decode** — grade frozen gates only, keep misses, no band-shopping.
7. **Certify + consolidate** — STATUS doc, decode JSON, pattern + anchor, network post, persist.

### 5.2 Readiness / dependency / kill map

| item | state |
|---|---|
| **Readiness** | Bell-resource-across-shields ✓(197), in-block CZ̄ ✓(206/214), software frame ✓(197/199), depth-check discipline ✓(213–216). **Ready to derive + selftest now.** |
| **Dependency** | none unmet — all four sub-primitives certified. Only new content = composing them across a cut with the terminal-frame CZ gadget. |
| **Kill-criteria** | **K1** transpiled 2q depth or width exceeds confident band (post-compaction: be conservative) → fall back to minimal form or register-and-defer, do NOT force-submit. **K2** selftest fails (frame doesn't reproduce ideal CZ̄) → the terminal-Pauli claim is wrong; re-derive, do not fly. **K3** the gadget secretly needs mid-circuit feed-forward → out of terminal-frame scope; defer to a feed-forward P6 flight. **K4** shield loses to bare at depth (G4 fails) → honest NOT HELD, the composition tax outran the FT benefit at this depth (a real, publishable negative). |

### 5.3 Later P6 flights (once Exp217 certifies)

- **F2:** two-node distributed BV (roadmap's original) — now with a crisp primitive underneath.
- **F3:** distributed logical HLF (compose 214's S-vertex family across the cut).
- **F4:** mid-circuit distributed gate WITH feed-forward (needs the real-time classical channel;
  the honest test of whether feed-forward pays over the terminal frame).

---

## 6. Success criterion for the program

P6 succeeds when a logical two-qubit gate runs across a shielded cut, error-detected, and beats
bare — turning "the network stack" and "the logical computer" into one distributed fault-tolerant
machine. Exp217 (distributed CZ) is the minimal certification of that claim; everything else in P6
is building the machine wider on that footing.
