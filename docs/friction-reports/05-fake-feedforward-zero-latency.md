# Friction Report 05 — FakeMarrakesh executes dynamic feedforward at zero latency

**Filed**: Whisper C4640 (2026-07-13), from Exp119 grade. **Status: OPEN (queued
with 01-03 per Creator hold).**

## Summary

Aer/FakeMarrakesh executes `if_test` classical feedforward with **zero latency and
zero decoherence cost**. Real ibm_marrakesh charges a large, measurable price for the
mid-circuit-measure → classical-decision → conditional-gate round trip. In Exp119 this
INVERTED a pre-registered sim prediction and consumed the experiment's entire effect
budget.

## Data (Exp119, job `d9a9ma8tcv6s73do74r0`, 30k shots/basis/arm)

| Quantity | Sim (FakeMarrakesh) | Hardware |
|---|---|---|
| E_B(feedforward arm) | −0.0644 ± 0.0077 | +0.1199 ± 0.0086 |
| E_B(coherent/deferred arm) | −0.0446 ± 0.0078 | +0.0279 ± 0.0082 |
| D1 = ff − def | **−0.020 (ff BETTER)** | **+0.092 (ff WORSE)** |

The sim says feedforward beats the coherent decomposition (fewer 2q gates); hardware
says the opposite by ~11σ — the latency window decoheres the target qubit by ≈0.09
energy-units in the Exp119 Hamiltonian's natural scale (T2-dominated dephasing of B
between Alice's measurement and Bob's conditional rotation).

## Why it matters

Any experiment whose budget is a small energy/coherence margin (QET dip = 0.115 E)
gets a falsely optimistic sim tier whenever the protocol uses dynamic circuits. The
F90 finding already measured feedforward cost in witness units (1.766 vs 1.825);
Exp119 prices it in ENERGY units. The noise model needs a feedforward-latency
dephasing term (even a crude fixed-duration delay on all qubits during if_else
would have flipped the sim's D1 sign).

## Workaround (proven this campaign)

Pre-register a coherent-control twin arm as the latency-free comparator (Exp119's D1
did exactly this — the failure mode was named at freeze and isolated at grade), and
treat sim-tier feedforward results as upper bounds on performance, never estimates.
