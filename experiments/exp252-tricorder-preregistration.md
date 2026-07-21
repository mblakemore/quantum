# Exp252 (H7-P4) — PRE-REGISTRATION: THE SHIELDED TRICORDER (Heisenberg super-resolution sensing)

**FROZEN before submission. Whisper C4963, substrate claude-opus-4-8. Creator directive: "Fly P4".
Builder+grader frozen together: `experiments/exp252_tricorder.py`.**

## Claim
A GHZ sensor of N qubits accumulates phase N-fold faster than a single qubit. Sweeping a phase dial φ on
all N qubits of GHZ_N, the X-parity ⟨X^N⟩(φ) = cos(Nφ) — its DFT peak frequency equals N. N=1 is the
single-qubit standard-quantum-limit reference (freq 1); N=2,3,4 demonstrate super-resolution (freq 2,3,4).

## Flight
`ibm_fez`, 36 pubs × 4,000 shots, static, transpiled 2q ≤ 10 (asserted). N∈{1,2,3,4} × M=9 phase points
over [0,2π). Est. 30–60 s of 3,989 s remaining.

## Frozen gates
- **PASS-HEISENBERG**: DFT peak frequency == N for N∈{2,3,4} AND the single-qubit reference peaks at 1.
- Reported always: per-N visibility (parity amplitude vs ideal 1.0) — the metrology contrast and the
  honest decoherence cost at N=4.

## PD gate (passed pre-freeze)
PD-1: each GHZ_N peaks exactly at frequency N in noiseless sim, ideal visibility ~1.0 → PASS-HEISENBERG.

## Pre-filed prediction (before any data)
**PASS-HEISENBERG, confidence 0.8.** The peak LOCATION (the Heisenberg signature) is robust to amplitude
loss, so the scaling law should survive decoherence. Predicted hardware visibility: N=1 ~0.95, N=2 ~0.8,
N=3 ~0.6, N=4 ~0.35–0.5 (GHZ fidelity falls with size on Heron). **Named failure mode**: N=4 GHZ
visibility drops into the shot-noise floor (< ~0.15) so its DFT peak is mislocated — then the honest
result is super-resolution certified up to N=3 with the N=4 attenuation reported (a device-fidelity
boundary, kept with full weight).

## Scope (honest)
This is the PHYSICAL GHZ metrology result. The error-DETECTED (shielded) logical-GHZ version (Exp219,
16 qubits) attenuates the signal at current depth and is named as the next-hardware step, not flown —
the frequency super-resolution is the clean, robust deliverable.
