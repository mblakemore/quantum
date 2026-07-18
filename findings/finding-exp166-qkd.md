# Finding — Exp166: THE SUBSPACE CHANNEL — a key certified by physics, a wiretap that can't hide

**Cycle**: C4857 · **Date**: 2026-07-18 · **Backend**: ibm_fez · **Job**: `d9du1bkjeosc73fi2h3g`
(16 circuits: {honest, Eve} × 8 basis settings, 4096 shots). What the network is *for*: the six
primitives (Exp154–165) turned into a working secure channel. Creator directive: "the most Star
Trek thing" over the quantum network.

## Result — the channel works, and it cannot be tapped silently

Alice (q0) and Bob (q3) share **only a swapped pair — they never interacted** (Exp162). From it,
E91/BBM92 quantum key distribution:

| | S (CHSH) | QBER_Z | QBER_X | secret fraction |
|---|---------|--------|--------|-----------------|
| **honest** | **2.179** (+6σ over 2) | 6.0% | 14.7% | **0.040 > 0** |
| Eve (wiretap) | 1.184 | 8.1% | **50.7%** | key aborted |

1. **Certified key.** The honest S = 2.179 beats the classical bound of 2 at 6σ — physics
   (not assumption) guarantees no eavesdropper holds a copy — and QBER 10.4% leaves a positive
   secret fraction. A real key was distilled and used: **"BEAM ME UP" one-time-padded and
   recovered, 100% of characters correct.**
2. **The wiretap detects itself.** Eve's intercept-resend on Bob's qubit collapses the
   certificate (S 2.179 → 1.184, below 2) and spikes QBER_X to 50.7% — the protocol aborts the
   key. **The falsifier passing *is* the security feature**: you cannot listen without announcing
   yourself.
3. **The two-bases lesson, in data.** Eve measures in Z, so QBER_Z stays clean (8%) while QBER_X
   explodes — a one-basis protocol would have missed her entirely. This is *why* BB84/E91 use
   conjugate bases, shown rather than asserted. (A fixed-Z Eve drives Bob's X-read to a coin —
   50%, not the basis-averaged 25% — a physics correction to the pre-registration, caught in
   the sim truth-gate.)

## Why this is the wing's payoff

The secure channel consumes the whole stack: the **swap** makes the shared pair between strangers,
the witness discipline becomes the CHSH certificate, and the honest error accounting becomes the
key rate. The secret fraction is thin (0.04 — swap-grade fidelity), which is exactly the honest
hook for the next rung: **purify first (Exp165) → higher fidelity → fatter key.** The wing is now
a story with a use at the end.

## Ledger

Third consecutive full band-hold (S, both QBERs, Eve separation all as predicted; the marginal
key coin — pre-registered 50/50 — landed positive). Calibration 82.5%.

## Fence

One die, entanglement-based QKD with the certificate and both parties co-located; no finite-key
security proof, no privacy amplification implemented (secret *fraction* reported, raw key used
for the demo); Eve is one intercept-resend strategy, not a general attack. A working
demonstration of physics-certified key exchange and tamper-evidence, not a deployed cryptosystem.
