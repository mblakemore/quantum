# Finding — Exp168: THE GHZ CONFERENCE KEY — one trio, one shared secret, three holders

**Cycle**: C4859 · **Date**: 2026-07-18 · **Backend**: ibm_fez · **Job**: `d9duedineu4c739np50g`
(10 circuits: {honest, Eve} × 5 settings, 4096 shots). The multi-party subspace channel —
extends Exp166 (2-party QKD) to three parties sharing one key at once.

## Result — a certified 3-party key

One GHZ trio |000⟩+|111⟩ gives Alice/Bob/Charlie a **shared conference key** (all measure Z →
the same bit), certified not by three pairwise Bell tests but by genuine tripartite nonlocality —
the **Mermin inequality** (classical bound 2, GHZ maximum 4):

| | Mermin M | conference QBER | secret fraction |
|---|----------|-----------------|-----------------|
| **honest** | **3.467** (+23σ over 2) | 3.7% | 0.547 |
| Eve (wiretap on Charlie) | −0.032 | 4.3% (Z stays clean) | key aborted |

The certificate clears the classical bound decisively, the conference error is 3.7%, and the
shared key carried a broadcast: **"ENGAGE" one-time-padded and read correctly by Bob — and Charlie
holds the same key.** One key, three parties, one entangled state.

## The wiretap, three-party edition

Eve's intercept-resend on Charlie's qubit collapses the GHZ coherence completely — Mermin falls to
≈0 (every X/Y correlation dies), far below the classical 2 — so the protocol aborts. And the same
two-bases lesson appears in the tripartite data: Eve measures in Z, so the Z-basis conference key
stays clean (4.3%) while the Mermin (X/Y) certificate is destroyed. A conference protocol checking
only the key basis would miss her; the nonlocality certificate is what catches the tap.

## Ledger

All pre-registered bands held (Mermin, QBER, Eve collapse, broadcast) — fourth band-hold in five
flights (calibration 82.5%). Eve's M landed near 0 rather than the predicted ~√2 because a full
Z-collapse of one party kills *all* Mermin terms, not just some — a sharper collapse than the
2-party analogue.

## Fence

One die, co-located parties, one GHZ state, one attack strategy, raw key (no privacy
amplification). A physics-certified *multi-party* key demonstration — the network's subspace
channel generalized from a private line to a conference call no one can wiretap silently.
