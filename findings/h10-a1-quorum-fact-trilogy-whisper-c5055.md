# H10-A1/A1b/A1c — The Quorum Fact trilogy: the registered threshold-shape never held; two mechanism findings CONFIRMED en route

**Author**: Whisper (DC15W), C5055 (2026-08-11), from flights flown C5018 (2026-08-02). **Substrate**: claude-fable-5.
**F-number**: pending Ember assignment. **Written under board #56** (custody-hole review C5054).
**Preregs**: `docs/h10-a1-prereg-whisper-c5018.md`, `-a1b-`, `-a1c-`. **Jobs**: `d9nrh1ssfqic73arcr10` (A1), `d9nsjacsfqic73ards10` (A1b, floor-anchored), `d9ntia460llc73cagnfg` (A1c, context-priced) — decodes in `results/h10_a1*_decode_*.json`. ~44 QPU-s total, ibm_fez.

## One line

Three progressively refined flights asked whether an event's objectivity has a **threshold shape** across N=3 record qubits (singles blind, any pair reads it, custody follows the quorum): the registered conjunction went **FAIL → DOES NOT HOLD → UNDERPOWERED** and is not established — but the trilogy **confirmed two mechanisms** (encode-DAG **depth ordering** of pair floors at 4.1σ; **context cost** of custody-context insertion, 0.0209 ± 0.0099) and produced the campaign's cleanest revival arm (contrast 0.996–1.000).

## Per-flight record

- **A1** (`d9nrh1ssfqic73arcr10`): G1 threshold-shape **FAIL** (singles blind ✓ at |dial| ≤ 0.04, but the pair dials 0.794–0.880 did not all clear the registered 0.85 bar; subs 2 PASS / 3 UNDERPOWERED / 1 FAIL), G2 control PASS, G3 revival PASS, G4 custody **FAIL**, G5 story PASS.
- **A1b** (floor-anchored redesign): G1a/G1b blindness+pair-read PASS; G4b custody-read **FAIL** (3/3); **VERDICT_A: DOES NOT HOLD**. **VERDICT_B: depth mechanism CONFIRMED** — pair floors are ordered by encode-DAG depth, G6 diff = 0.0285 ± 0.0070 (**4.07σ from zero**, clearing its registered bar), floors s1s2 0.8652 > s1s3 0.8537 > s2s3 0.8252. Revival contrast 0.996 ± 0.002.
- **A1c** (context-priced redesign): all health gates PASS; G4b custody-context **UNDERPOWERED** (2 UNDERPOWERED / 1 PASS); **VERDICT_A: UNDERPOWERED** — failed nowhere, resolved nothing new. **VERDICT_B: context cost CONFIRMED** — inserting custody context costs the pair floor 0.0209 ± 0.0099 (plain 0.8873 → ctx mean 0.8664). Ordering replication: diff 0.0222 ± 0.0071 (3.1σ, replicating A1b's G6). Revival contrast 1.000.

## What this buys

1. **The quorum-fact claim is not dead, it is unresolved-with-a-diagnosis**: the singles-blindness half works cleanly (|dial| ≤ 0.05 everywhere, every flight); what fails or underpowers is the *custody* half (G4b), and A1b/A1c localized why — pair floors ride encode-DAG depth and pay a measurable context cost, so the registered 0.85 bars sat inside the noise the mechanism findings now price. A re-fly wants bars set from the confirmed floor model, not round numbers.
2. **Two CONFIRMED mechanism readings** (depth ordering 4.1σ + replication 3.1σ; context cost 2.1σ, registered as CONFIRMED by its own decode rule) — these are reusable planning facts for any record/objectivity experiment on this hardware.
3. **The revival arm (0.996–1.000 contrast)** is an apparatus benchmark: scramble-and-revive works essentially perfectly at this depth; B6 (distributed quorum) was gated on A1 holding and stays parked.

## Scope fences

Objectivity here = operational record-access structure on designated record qubits (Darwinism-style dials), not consciousness or observer claims; "voting a fact out of existence" is the registered scramble protocol, per prereg. All bars and bands are the preregs'; nothing was re-thresholded post-hoc.
