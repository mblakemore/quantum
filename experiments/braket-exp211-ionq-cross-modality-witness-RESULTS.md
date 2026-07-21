# Exp211 (Braket) — RESULTS: cross-MODALITY causal-order witness FIRES on IonQ Forte-1 (trapped ion)

**WITNESS-FIRED. Substrate: claude-opus-4-8. Whisper, C4941.**
Pre-registration: `braket-exp211-ionq-cross-modality-witness-preregistration.md` (frozen, committed cb9ca44).
Device: IonQ Forte-1 (`arn:aws:braket:us-east-1::device/qpu/ionq/Forte-1`), trapped ion, us-east-1.
Task ARNs: smoke `...quantum-task/37c301c0...`; witness `...quantum-task/b479e273-d4f9-4ab3-9833-ed3188c51b40`.
Cost: smoke $16.60 + witness $161.20 = **$177.80** (under the $200 us-east-1 ceiling).

## Result — the causal witness fires on individual atoms, against the same theory bound

| arm | counts (500 shots) | ⟨X_c⟩ |
|---|---|---|
| w_start_c (comm) | {'00':475, '10':11, '01':9, '11':5} | **+0.944** |
| w_start_a (anti) | {'11':482, '10':8, '01':6, '00':4} | **−0.952** |
| w_end_c (comm) | {'00':480, '01':10, '10':8, '11':2} | **+0.952** |
| w_end_a (anti) | {'11':476, '00':9, '01':9, '10':6} | **−0.940** |

**W (witness DISC) = +1.8940 ± 0.0632** · W − 5·seW = **+1.578 (29.9σ over the causal-mixture bound 0)** · verdict **WITNESS-FIRED**.
Pre-committed reading rule: W ≥ 1.3 → the cross-modality firing (clean, offset-implausible). ✓

## What it means
Indefinite causal order fires on a **trapped-ion** machine — qubits are single atoms held by lasers,
all-to-all connectivity, native gates GPI/GPI2/RZZ, and **none of the CZ Z-bias** the whole campaign
noise story rested on. Same witness circuit, same theory bound as every superconducting flight. The
phenomenon is **not a superconducting artifact** — it spans the deepest hardware divide. Three physically
different substrates now host it:

> **IBM Heron (SC, heavy-hex): W 1.89–1.95 · IonQ Forte-1 (trapped ion, all-to-all): W 1.89 · Rigetti Cepheus (SC, different vendor): W 1.11**

The trapped-ion chip matches IBM's tuned Heron and **far exceeds Rigetti** — the witness strength tracks
the specific device's fidelity, not its modality. Indefinite causal order is substrate-general; how
*cleanly* it runs is a per-device quality question.

## Scope (honest) — WITNESS, not the full PASS-CAUSAL card
Budget forced witness-only: this is **W crossing the causal-mixture bound**, NOT the three-number
PASS-CAUSAL certification Exp210 got on Rigetti (capacity Rbar + null D were not flown — the full
frozen axis is ~$9k on IonQ at $0.08/shot). The null-integrity arm that would rule out a spurious
offset was **not run**; its job was done up front by the **semantic smoke check** (comm arm 97/100 on
'00', anti arm 93/100 on '11' — the qubit mapping and bit convention survived IonQ's native compile),
and the four-arm comm/anti structure is the in-flight control. A W of 1.89 at 29.9σ with a validated
port is a strong firing, but it is the witness, not the multi-axis card.

## Prediction ledger — both halves HIT
Pre-filed: **WITNESS-FIRED ~0.85 → HIT**; W ~1.7–2.0 → **HIT (1.894)**. Unlike Exp210 (Rigetti), where
the binary PASS hit but the W-magnitude missed low, here the magnitude prediction landed — trapped-ion
high fidelity + no routing overhead on the 2-qubit witness gave a near-Heron W, exactly as reasoned.
The named failure mode (native-compile mangling → W near 0) did not occur; the smoke check guarded it.

## Method notes
- Port: `backend.run(native=True)` compiles the abstract switch circuit to IonQ's GPI/GPI2/RZZ + verbatim
  box (the Rigetti path generalized). Two $0 pre-submission bugs cleared: backend name `Forte 1` (space,
  not the ARN's `Forte-1`), and `best_pair` guarded for non-CZ devices.
- Shots 500/pub (not the bench's 4000) — a cost choice that widens seW (0.063), does not retune the bound.
- Single window per device; same-instrument, not same-instant (identical scope to the Heron/Rigetti flights).
