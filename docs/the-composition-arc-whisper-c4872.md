# The Composition Arc — What a Quantum Network Costs to Stack, and How to Stop Paying

*(docs/the-composition-arc-whisper-c4872.md — the repository's definitive account of
Exp175–182, the nine-flight composition campaign of 2026-07-18/19)*

**Written to venue standard, versioned in this repository as the publication (Creator
direction C4594: the repo is the venue). v1.0, Whisper C4872. All experiments pre-registered
(prereg files committed before decode from Exp177 onward), all executed on `ibm_fez`
(Heron r2) in a single night, all findings files and decode JSONs in this repository.
Plain-language version: the museum exhibits* The Relay Computer *and* The Untrusted Relay
*(demo/relay-computer/, demo/relay-key/).*

> **Abstract.** Quantum-network capability is conventionally priced by benchmarking layers in
> isolation — an entanglement-swap fidelity, a gate-teleportation fidelity — and composing on
> paper. We report a nine-experiment campaign on commercial superconducting hardware showing
> that this fails in a specific, measurable, and ultimately curable way. (1) Composing a swap
> link with a teleported gate costs 0.06 Bell fidelity *beyond* the product of the layers
> (−3.4σ, Exp175); the excess **compounds** with the number of feedforward windows (−9.4σ
> dose-response, Exp176). (2) The cost decomposes into three named parts (Exp177): the
> mid-circuit **measurement window** dominates (0.330), classical feedback latency is minor
> (0.093), circuit depth is minor (0.094). (3) The dominant part is **coherent**: one echo X
> per end qubit recovers +0.293 at 24.8σ and converts a failed entanglement certification into
> a 22σ pass (Exp178); countermeasures overlap (frame-deferral's gain shrinks from +0.093 to
> +0.015 on an echoed chain), so stacks must be priced jointly. (4) The cost is
> **architectural**: with Pauli-frame tracking, measurement windows merge (2→1) for +0.146 at
> 12.3σ with zero added gates (Exp179); circuit-level countermeasures plateau at F ≈ 0.78,
> ~0.11 under the no-window ceiling. (5) The stack, so corrected, delivers its payload:
> E91 keys certified through one untrusted relay (CHSH S = 2.307, +16.8σ) **and two** (S =
> 2.235, +12.7σ; Exp180) — the two-relay violation *refuting our own pre-registered Werner
> prediction* and forcing the correction S = √2(⟨ZZ⟩+⟨XX⟩) for dephasing-structured links —
> and a **distributed computation** (Bernstein–Vazirani across a register cut, every oracle
> gate teleported) at 96% of monolithic performance with zero in-flight communication
> (Exp181), whose per-gate cost is banded at 3–5% across three doses with no resource-scale
> interaction at 10 qubits (Exp182). The through-line: **the tax was never the stacking — it
> was always the windows** (second gate: 45% with windows, 3% without), and every corrective
> lever is software or compilation, not hardware.

---

## §1. The question, and why isolated benchmarks cannot answer it

By mid-campaign this repository had certified the network primitives separately: Bell pairs at
F ≈ 0.98, state teleportation at 0.913 against the 2/3 classical bound (Exp154), entanglement
swapping at 0.836 against the 1/2 separable witness (40σ, Exp162), and gate teleportation — the
Eisert–Jozsa–Simon nonlocal CNOT — at 0.789 (25σ, Exp170). The standing assumption in network
design is that these numbers compose: a swap link at Werner parameter p₁ feeding a gate channel
of ratio r should yield p₁·r. Nobody on this hardware had measured the composition.

Every experiment below shares the campaign's discipline: **theorem-fixed witnesses** (the 1/2
separable bound; CHSH S = 2; the 1/2^w guessing floor), never thresholds fit from the data they
judge; **within-job baseline arms** for every comparison (the night's conditions swung enough to
carry an identical circuit from 0.571 to 0.463 in one hour — cross-job absolute comparisons are
meaningless, same-job deltas are not); **pre-registered prediction bands that encode a model**,
so a miss is not a vague overestimate but a named model failure; and a **falsifier arm** whose
behavior is predicted by theory (all nine landed on script).

## §2. The tax exists and compounds (Exp175, Exp176)

**Exp175** (job `d9dvseineu4c739nrb2g`) executed the first composition: the e-bit consumed by
the EJS nonlocal CNOT is itself produced by a Bell-measurement relay. The stack works — Bell
F = 0.576, 6σ over the witness, truth table 0.822, and the no-resource falsifier keeps the
truth table (0.877, the classical action is LOCC) while capping at F = 0.454 — but the
pre-registered composition test `p(stack) = p(gate)·p(link)/p(anchor)` failed at **−3.4σ**
(predicted 0.638, measured 0.576). Stacking costs extra.

**Exp176** (job `d9e008kinv1c73apkuug`) made the window count a dose: a repeater chain at
N = 0, 1, 2 swaps. The two-station chain still certifies end-to-end (F = 0.571, 9σ — two
qubits with no shared history, two stations apart), but the multiplicative model misses by
**−0.212 at −9.4σ**, the per-stage ratio collapsing 0.81 → 0.55: the second swap costs nearly
twice the first. The pre-registered fingerprint held: the ZZ-vs-XX/YY asymmetry grows with N
(0.00 → 0.12 → 0.50) — idle-window dephasing, dose-dependent. Un-echoed chains on this
hardware lose fidelity faster than exponentially in hops; the depth ceiling without
countermeasures is ~2–3.

## §3. The tax decomposes, and the dominant part is curable (Exp177, Exp178)

**Exp177** (job `d9e0521htsac739dkslg`) noted that swap corrections are Pauli corrections,
which commute through Cliffords as a classically tracked frame (on the end qubit:
x = c₃⊕c₁, z = c₂⊕c₀; per-basis readout flips; algebra selftest-proven exact). Four arms —
live, frame-deferred, fully end-measured, direct — split the 2-swap chain's 0.516 deficit into:

| component | cost | significance |
|---|---|---|
| mid-circuit measurement window | **0.330** | 27.8σ — dominant, 3.5× anything else |
| classical feedback latency | 0.093 | 7.8σ — recovered **free** by the software frame |
| circuit depth (all gates) | 0.094 | the chain's gates are nearly free |

The pre-registered magnitude prediction (latency ≥ 60% of the window deficit) **missed** — the
named alternative branch fired: the tax is the measurement pulse window, not the classical wait.

**Exp178** (job `d9e0a4ineu4c739nrt50`) asked whether that dominant window cost is coherent
(echo-recoverable) or irreversible backaction. The minimal echo — one simultaneous X on both
end qubits at the midpoint *between* the two windows; X⊗X leaves Φ⁺ invariant, so it costs no
closing gates and no frame bookkeeping — recovered **+0.293 at 24.8σ** on the live chain. That
night's un-echoed chain had *failed* certification (0.474 < 1/2); with one gate per end qubit
it certified at 0.767, 22σ over. The fingerprint was textbook: ZZ unmoved, the entire recovery
in XX/YY. Second finding: **countermeasures overlap** — frame-deferral alone was worth +0.093,
but adds only +0.015 on an echoed chain; both drain the same coherent pool. Countermeasure
stacks must be priced jointly, in the same job, never by summing solo gains.

## §4. The tax is architectural (Exp179)

With the frame tracked in software, the second swap's *gates* never depend on the first swap's
*outcomes* — sequencing was only ever forced by live feedforward. **Exp179** (job
`d9e0gv4inv1c73aplk4g`) merged both Bell measurements into one simultaneous window: **+0.146
at 12.3σ over the sequential chain, with zero added gates** — a compiler rule (schedule
frame-tracked measurements simultaneously), not a physics upgrade. An engineered Hahn
(X–delay–X, delay matched to the 1.70 μs measurement duration from backend timing) added
+0.059 at 5.0σ. Honest ledger: the new stack's lead over the old (+2.5σ) fell under the
pre-registered 3σ bar and stays unclaimed, and the pre-registered open comparison (merged vs
sequential-echoed) resolved as a tie — the overlap principle at architecture level. Best
circuit-level stacks converge at **F ≈ 0.75–0.78**, ~0.11 under the 0.885 no-window ceiling;
the remainder (non-refocusable backaction plus the T1 price of the Hahn delay itself) is
pulse-level or hardware territory, labeled rather than promised.

## §5. The stack, used: keys through untrusted relays (Exp180)

**Exp180** (job `d9e15q1htsac739dm7i0`) ran E91 key distribution through the corrected stack.
Method contribution: CHSH angles are non-Clifford, so relay corrections cannot be XOR-ed —
but conjugation gives **frame-steered sifting**: a pending frame (x,z) maps the measurement
A(θ) → (−1)ˣ·A((−1)^(x⊕z)·θ), so each shot's outcome is sign-flipped by x and re-sorted
between Bob's ±π/4 settings by x⊕z. Every shot lands in a valid CHSH term; this is precisely
how entanglement-swapping QKD folds published relay outcomes into sifting, here derived from
the frame algebra and selftest-proven (noiseless S = 2√2 recovered through both architectures).

Results: **S = 2.307 ± 0.018 through one relay (+16.8σ over the classical bound, QBER 8.2%)
and S = 2.235 ± 0.019 through two (+12.7σ, QBER 10.6%)**; the no-entanglement falsifier flat
(S = −0.010, key bits 49.9% disagreement). The two-relay certification **refuted our own
pre-registered point prediction** (S = 1.97, from the Werner mapping S = 2√2·p at the plateau
fidelity). The decomposition is structural: for dephasing-limited links (ZZ ≫ XX ≈ −YY), with
A ∈ {Z, X} and B at ±π/4, **S = √2·(⟨ZZ⟩ + ⟨XX⟩)** — the previous flight's own correlations
already predicted a violation (2.05), hidden by collapsing a structured state to a scalar
fidelity. The ZZ surplus that dephasing leaves intact both buys CHSH margin and keeps Z-basis
key errors low: dephasing-limited links are *better* key carriers than their fidelity suggests.

## §6. The stack, used again: distributed computation (Exp181, Exp182)

**Exp181** (job `d9e28tcjeosc73fi8fi0`) distributed Bernstein–Vazirani across a register cut:
Alice's data qubits and Bob's oracle ancilla never interact; every oracle CNOT is teleported.
The corrections vanish architecturally — X^x lands on the |−⟩ ancilla as global phase (dropped);
Z^z commutes through the final Hadamard into a decode XOR — so the distributed algorithm runs
with **zero live feedforward and zero mid-circuit measurement**. Results: the right hidden
string is the modal outcome for **4/4 programs**, average correctness 0.914 = **96% of the
monolithic baseline** (0.949); the falsifier sat on the classical guessing floor exactly
(+141σ separation). The per-gate ratio P(11)/P(01) = 0.971 closes the arc's loop from the
absence side: **second gate with windows, 45% (Exp176); without windows, 3%.**

**Exp182** (job `d9e2f4kinv1c73apo1l0`; n = 3, the campaign's first 10-qubit flight) turned
that single ratio into a dose-response: 8 programs spanning 1–3 teleported gates. All eight
returned the right answer modally (+79σ to +141σ over exact 1/2^w floors). Per-gate ratios
0.954 / 0.945 / 0.972 — all within the pre-registered band; pooled r̂ = 0.954; the
extrapolation license r̂¹⁰ = 0.62. The strict constant-ratio test failed at 2σ, but through a
**third path** neither pre-registered branch anticipated: the drift is non-monotone and the
*monolithic baseline shows the same texture more strongly* (local w=3 outperforms local w=2) —
compiler/placement texture, not a distribution cost. Distribution itself costs <1% per gate at
w ≤ 2. No resource-scale interaction appeared at 10 qubits with 3 simultaneous e-bits.

## §7. The rules (what a network engineer should take from this repository)

1. **Never price a stack by multiplying layer benchmarks.** Composition carries a tax that
   compounds with feedforward/measurement windows (−9.4σ dose-response).
2. **The window hierarchy**: measurement placement ≫ feedback latency ≈ circuit depth.
   Attack the windows, not the gates.
3. **Track Paulis in software** (free, +0.09 here) — and it unlocks rule 4.
4. **Merge frame-tracked measurement windows** (compiler-level, +0.146 here, zero gates).
5. **Echo end-qubits through every window you cannot remove** (one X gate = the difference
   between failing and passing certification here).
6. **Price countermeasure stacks jointly** — their gains overlap; solo-measured gains do not add.
7. **Never scalar-collapse a structured state.** Werner mappings mis-price dephasing-limited
   links (S = √2(ZZ+XX), not 2√2·p); dose-response designs on compiled hardware must
   pre-register *baseline-normalized* ratios or compiler texture masquerades as physics.
8. **Prefer architectures where corrections defer entirely** (Clifford consumption;
   correction-eigenstate targets): they run window-free, and the tax vanishes (3%/gate).

## §8. Method note: the calibration loop

The night's bands missed five times — three low (multiplicative priors), then two high
(conservative echo priors) — and every miss was converted into a pricing update
(super-linear window pricing, C4863; echo up-rating, C4865; per-CX pricing for window-free
designs, C4869). Flights eight and nine held **every** pre-registered band. Model-encoding
bands make misses informative; a predict → validate → reprice loop run at QPU cadence
converged a domain pricing model in five iterations. The ledger practice (prediction logged
before submission, validated the same cycle) has been unbroken since Exp179.

## §9. Fences and limitations (stated, not buried)

One die (chip patches, not stations); e-bits are pre-shared resources (the standard
distributed model); no error correction, privacy amplification, or authenticated channels in
the key experiments (Ekert's security layer only); frame-deferred arms are
verification-equivalent and require live feedforward for non-Clifford consumption; the
plateau (0.78) and tax magnitudes are one night's conditions on one backend — the *existence*
and *structure* claims are the durable results, carried by same-job contrasts at 5–141σ. The
two-relay S = 2.235 includes a favorable condition swing; the certified claim rests on its
12.7σ margin, not the point value.

## §10. Data availability

Per-experiment pre-registrations (`experiments/exp17[5-9]-*.md`, `exp18[0-2]-*.md`), code
(`experiments/exp175_relay_gate.py` … `exp182_dist_bv3.py`, each with `--selftest`),
manifests and decode JSONs (`results/`), findings (`findings/finding-exp175-*.md` …
`finding-exp182-*.md`), walkable exhibits (`demo/relay-computer/`, `demo/relay-key/`).
IBM Quantum job IDs are quoted per experiment above and in every finding.
