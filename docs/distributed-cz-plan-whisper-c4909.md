# Deeper distributed-CZ: the missing entangling gate (plan)

**Whisper C4909, 2026-07-20. Substrate `claude-opus-4-8`.** Plan on the Creator directive "build a
plan for deeper distributed-CZ, revisit for gaps + add pre-dev planning structure, then fly it."

---

## 1. Why it matters

Exp217–220 built the Federation Computer on ONE entangling gate: the distributed logical CNOT. But
CNOT alone doesn't give the **graph-state / cluster-state** family — that needs **CZ** edges. CZ is
the missing half of the distributed entangling set, and it unlocks:
- **graph / cluster states** across shielded nodes (the resource for measurement-based computation);
- the **BGK 2D-HLF** (Exp206) run *distributed* — the flagship constant-depth quantum-advantage
  algorithm, split across shielded nodes;
- **distributed MBQC** — computing by measuring a distributed cluster state.

So the deeper distributed-CZ is the keystone that turns the Federation Computer from "a gate + a
network" into "a distributed computational substrate."

---

## 2. The obstruction, and the key that opens it

**Why the obvious gadget fails (verified C4909):** a *symmetric* non-local CZ — local CZ(d_A,e_A)
+ local CZ(d_B,e_B) + measure the relay — yields the **parity** d_A⊕d_B, not the **product**
d_A·d_B that CZ needs. (Direct calc + sim: both cluster stabilizers came out 0.) A non-local CZ,
like the non-local CNOT, requires the **sequential** control→measure→target structure, not the
symmetric one.

**The key (derived + verified C4909):** CZ = (I⊗H_B)·CNOT(d_A→d_B)·(I⊗H_B). Conjugating the
*working* distributed CNOT (218) by the target Hadamard changes exactly two things, both of which
absorb cleanly — **no single-qubit logical H̄ gate is needed** (the [[4,2,2]] wall is avoided):
1. the second handshake CNOT(e_B→d_B) *into the X-support* becomes **CZ(e_B→d_B) into the
   Z-support** (`cz(9,4),cz(9,6)` instead of `cx(9,4),cx(9,5)`) — the target Hadamard absorbed into
   the coupling;
2. the target frame **X^x → Z^x** (H X H = Z).

**Verified in sim (C4909):** with the physical relay (e_A=q8, e_B=q9), the construction makes the
2-qubit **cluster state** across the cut. Both stabilizers reach +1, each in its own basis-variant
(exactly as 218's CNOT needed a Z-variant and an X-variant):
- **⟨X̄_A Z̄_B⟩ = +1.000** in the variant reading e_A in X;
- **⟨Z̄_A X̄_B⟩ = +1.000** in the variant reading e_A in Z.
Both +1 uniquely identify the cluster state CZ|+̄+̄⟩ — i.e. a genuine distributed CZ.

---

## 3. The flight — Exp221: THE DISTRIBUTED CZ (cluster state across a shielded cut)

**Claim:** a logical CZ between d_A (shield A) and d_B (shield C), executed across the cut with a
physical relay + software frame (no gate crossing, no single-qubit H̄), produces the logical
**cluster state** CZ|+̄_A +̄_B⟩ — witnessed by **both** cluster stabilizers ⟨X̄_A Z̄_B⟩ = ⟨Z̄_A X̄_B⟩
= +1, which uniquely certify the CZ.

**Frozen gates (finalized at build, formula-frozen pre-submit):**
- **G1 STABILIZER-XZ:** ⟨X̄_A Z̄_B⟩ ≥ 0.55, ≥ 5σ over 0 (XZ-variant).
- **G2 STABILIZER-ZX:** ⟨Z̄_A X̄_B⟩ ≥ 0.55, ≥ 5σ over 0 (ZX-variant). Both ⇒ the cluster state ⇒ a
  genuine distributed CZ (not a mere correlation).
- **G3 FRAME-OFF:** in-decode falsifier — ignore the relay frame bits and both stabilizers collapse
  (|·| ≤ 0.25). The weld is the classical bits.
- **G4 (descriptive):** the CZ truth phase — on |1̄_A 1̄_B⟩ the induced phase / on the graph a
  1-qubit MBQC teleportation check, as a bonus that the gate composes.
- Registered verdict = G1 ∧ G2 ∧ G3.

**Budget predictions (C4887, filed pre-submit):** from the transpiled depth-check; prior: 218's
per-cut correlators landed ~0.87 at ~22 2q, so predict the cluster stabilizers ≥ 0.75.

---

## 4. Gap review (revisit for gaps)

Gaps found and closed:

1. **Symmetric-gadget gap.** Initial instinct (local CZ both ends) gives parity not product. CLOSED
   by the sequential CNOT-conjugation construction (§2), verified.
2. **Single-qubit H̄ gap.** CZ = H_B CNOT H_B naively needs the non-transversal [[4,2,2]] H̄. CLOSED
   by absorbing H_B into the second handshake (CZ-into-Z-support) + the X^x→Z^x frame flip — no H̄
   gate anywhere. Verified.
3. **Both-stabilizers gap.** A terminal-frame weld can only expose one stabilizer per relay basis
   (the 218 lesson: computational-basis coherence per variant). CLOSED by measuring **two
   variants** (e_A in X for ⟨XZ⟩, e_A in Z for ⟨ZX⟩) — both hold, jointly certifying the cluster
   state. Stated honestly: the two stabilizers are checked across two variants, not simultaneously
   (the same partial-shield/partial-witness structure as 197/217/218).
4. **Composition gap (CZ as a mid-circuit unitary).** A terminal-frame CZ is a valid *state-prep*
   (graph state) but NOT a composable mid-circuit unitary — the full unitary needs feed-forward
   (the 218 finding). CLOSED-BY-SCOPE: Exp221 demonstrates the CZ as **cluster-state generation**
   (the HLF/MBQC use-case ends in measurement, so terminal-frame suffices there). A composable
   feed-forward CZ, if ever needed mid-computation, is a later flight — and 218 already showed
   feed-forward is *worse* on today's hardware, so the state-prep form is the right primitive.
5. **"Is it really CZ" gap.** A single stabilizer or a Bell-like correlation could masquerade.
   CLOSED: both cluster stabilizers at +1 *uniquely* identify CZ|+̄+̄⟩ among stabilizer states; the
   frame-off falsifier rules out a trivial/classical origin.

---

## 5. Pre-dev planning structure

### 5.1 Seven-stage pipeline
1. **Derive** — the CNOT-conjugation construction + frame (DONE, §2).
2. **Selftest** — statevector-exact: both cluster stabilizers → +1, frame-off → 0. MUST pass.
3. **Depth-check** — transpile to ibm_fez, 2q count + width. GO iff within band.
4. **Freeze** — formula-freeze gates + budget predictions, commit pre-submit.
5. **Fly** — submit; write the manifest the instant job_id exists (Exp201 rule).
6. **Decode** — grade frozen gates only; keep misses; no band-shopping.
7. **Certify + consolidate** — STATUS, decode JSON, pattern + anchor, network post, persist.

### 5.2 Readiness / dependency / kill map
| item | state |
|---|---|
| **Readiness** | construction derived + both stabilizers verified in sim (C4909). Physical-relay + software-frame machinery proven (218). **Ready to build the full selftest + fly.** |
| **Dependency** | none unmet — reuses 218's relay handshakes; the only new piece (CZ-into-Z-support second handshake) is verified. |
| **Kill-criteria** | **K1** transpiled depth/width over the confident band → simplify or defer, no force-submit. **K2** selftest fails to reach both stabilizers at +1 → construction bug, re-derive, don't fly. **K3** frame-off does NOT collapse → the weld isn't carrying the gate; re-examine. **K4** on hardware a stabilizer misses its band → honest NOT HELD (the distributed CZ is deeper than the CNOT; a real negative). |

### 5.3 What it unlocks (downstream flights)
- **Distributed HLF** — 206's 2×2-grid HLF with inter-block CZ edges made distributed (terminal-
  frame works: the HLF ends in an X-measurement). The flagship distributed quantum-advantage flight.
- **Distributed MBQC** — a linear cluster across nodes + measurements = a computed gate at a distance.
- **Larger graph states** — cluster resources across the shielded network.

---

## 6. Success criterion

The deeper distributed-CZ succeeds when the logical cluster state CZ|+̄_A +̄_B⟩ is certified across a
shielded cut (both stabilizers, frame-off falsified) — giving the Federation Computer its second,
missing entangling gate and opening the graph-state / HLF / MBQC family.
