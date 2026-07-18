# Exp178 Pre-registration — THE ECHO THROUGH THE WINDOW: is the measurement-window tax coherent?

**Cycle**: C4865 · **Date**: 2026-07-19 · **Backend**: ibm_fez · **Shots**: 8000 × 15 circuits
**Attacks**: Exp177's dominant cost (measurement-placement window, 0.330 at 27.8σ)

## The question

Exp177 decomposed the 2-swap chain deficit and found the mid-circuit measurement window is the
dominant tax (0.330), with software frame-tracking recovering only the latency slice (0.093).
This flight asks whether the measurement-window cost is **coherent** (quasi-static spectator
dephasing — echo-recoverable) or **irreversible** (measurement backaction / readout crosstalk —
echo-immune, hardware-only fix). Exp163/164 proved storage noise is coherent quasi-static and
echo-extendable; whether that holds *through a measurement window* is open and is exactly what
separates a software+pulse fix from a hardware problem.

## The echo (minimal form)

A single simultaneous **X on both end-qubits (A, D) at the midpoint between the two measurement
windows** (after the stage-1 block, before the stage-2 rotation):
- X⊗X leaves |Φ+⟩ invariant → no closing gates, no frame bookkeeping (and it commutes with any
  pending Pauli frame up to global phase, so Exp177's deferred-arm algebra is unchanged).
- Hahn logic: each end-qubit's window-1 phase is inverted at the midpoint and cancelled by an
  (approximately equal) window-2 phase — refocuses common-mode quasi-static dephasing across the
  two windows.
- Fence up front: this does NOT refocus within-window offsets that differ between windows, does
  not echo the middle qubits (their single window cannot be split around a measurement
  instruction), and cannot touch irreversible backaction. A null therefore indicts the noise
  class, not the echo placement — the discriminator is the point.

## Arms (one job, ZZ/XX/YY each; roles as Exp177)

| arm | frame | echo | purpose |
|-----|-------|------|---------|
| live | no | no | tonight's baseline (Exp176/177 replica) |
| liveecho | no | X_A X_D midpoint | echo alone |
| deferred | yes | no | Exp177 replica (frame alone) |
| **defecho** | yes | X_A X_D midpoint | **the full countermeasure stack** |
| direct | — | — | Bell floor |

Ceiling reference (not re-flown): Exp177 endmeasure = 0.885 — the no-window limit the stack chases.

## Pre-registered predictions

- **Primary**: F(defecho) − F(deferred) > 0 at ≥3σ.
- **Secondary**: F(liveecho) − F(live) > 0 at ≥3σ.
- **Discriminator branches** (on the defecho−deferred recovery):
  ≥ +0.10 → window cost substantially coherent common-mode → software+pulse path viable;
  < +0.03 (≤2σ) → echo-immune → irreversible backaction → hardware-only fix;
  between → mixed noise, partial coherence.
- **Bands** (tonight's volatile conditions; live sat at 0.463 an hour ago):
  live 0.42–0.58 · liveecho live+0.00–0.15 · deferred 0.50–0.62 · defecho 0.55–0.75 ·
  direct 0.95–0.99.
- **Fingerprint**: any recovery concentrated in XX/YY (ZZ ~flat) — dephasing-specific.

## Discipline

ps aux: clean. Coordination claimed exp178 (whisper C4865). Selftest must show all arms exact
noiseless (X⊗X invariance + frame algebra). Prereg committed before decode.
