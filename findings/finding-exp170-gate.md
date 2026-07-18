# Finding — Exp170: GATE TELEPORTATION — an entangling gate between qubits that never met

**Cycle**: C4860 · **Date**: 2026-07-18 · **Backend**: ibm_fez · **Job**: `d9dutehhtsac739dit60`
(15 circuits: {teleported, direct, no-resource} × 5 settings, 4096 shots). Teleport an
*operation*, not a state — the primitive behind distributed and fault-tolerant computation.

## Result — the CNOT acted nonlocally

The Eisert-Jozsa-Simon nonlocal CNOT applies CNOT(A→B) using **1 shared Bell pair + feedforward
both directions**, with data qubits A and B never directly coupled (Alice CNOTs into her e-half,
measures, sends x; Bob applies Xˣ then CNOTs into his data, H-measures, sends z; Alice applies Zᶻ).

| arm | Bell F (|+⟩|0⟩→Bell) | truth table | ZZ / XX / YY |
|-----|----------------------|-------------|--------------|
| **teleported** | **0.789** (25σ over 1/2) | 0.870 | +0.75 / +0.74 / −0.67 |
| direct CNOT (same job) | 0.979 | 0.983 | +0.97 / +0.97 / −0.98 |
| no-resource (falsifier) | 0.454 | 0.885 | +0.80 / **+0.01 / −0.02** |

The teleported gate turns the product state |+⟩|0⟩ into a Bell pair at **F=0.789, 25σ past the
1/2 witness** — genuine entanglement created between two qubits with no direct interaction — and
reproduces the CNOT truth table at 0.870. Gate-teleport cost vs the same-job direct CNOT: 0.190,
consistent with the two feedforward-idle windows (the bidirectional latency, as named pre-flight).

## The witness *is* the quantum–classical line (the falsifier)

The no-resource arm is the finding's sharpest edge. Strip the shared entanglement and the gate
**still reproduces the truth table** (0.885) — because the *classical* action of a CNOT (permuting
basis states) is achievable by classical communication alone (LOCC). But its Bell fidelity
**caps at 1/2** (0.454): ZZ survives (0.80) while XX and YY collapse to zero (0.01, −0.02). The
entangling, coherence-creating action of the gate requires the e-bit. So F>1/2 is not merely a
pass/fail threshold — it is precisely the boundary between a genuine nonlocal *quantum* gate and
its classical shadow, and only the teleported arm crosses it. The e-bit is the quantum resource,
shown in data.

## Ledger

Fifth band-hold in six flights (truth table 1% under band; calibration 82.6%). The no-resource
arm landed exactly on the predicted physics.

## Fence

One die, one entangling gate, bidirectional feedforward, raw hardware; a demonstration of the
gate-teleportation primitive (nonlocal CNOT), not a compiled distributed algorithm or a
fault-tolerant logical gate.
