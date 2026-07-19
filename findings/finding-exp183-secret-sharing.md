# Finding — Exp183: THE TWO-OFFICER PROTOCOL — a secret neither officer can read alone, certified at 61σ

**Cycle**: C4873 · **Date**: 2026-07-19 · **Backend**: ibm_fez · **Job**: `d9e3cqsjeosc73fi9lqg`
(11 circuits: ghz×6, noghz×4, bellAB×1, 8000 shots). **New capability class: quantum secret
sharing** (HBB99 over GHZ) — the network wing's first *multi-party cryptographic* primitive
beyond key distribution. Creator go: ship-computer general#57.

## Result — the three-legged claim, all legs held

| leg | requirement | measured | verdict |
|-----|-------------|----------|---------|
| **Group CAN read** | recon ≥ 0.85, all 4 sifted bases | 0.918 / 0.920 / 0.922 / 0.924 | HELD (band 0.90–0.97 ✓) |
| **Singles CANNOT** | \|⟨AB⟩\|, \|⟨AC⟩\| < 0.05 everywhere | worst 0.028 | HELD |
| **Resource certified** | Mermin M > 2 at ≥5σ | **M = 3.369, 61σ** | HELD (band 3.1–3.6 ✓) |

Alice's measurement record is the secret. Bob XOR Charlie reconstruct it at ~92% per bit;
Bob alone — or Charlie alone — sees a coin flip (pair correlations ≤ 0.028, consistent with
the GHZ marginal theorem: the two-party reduced states are maximally mixed, so single-party
blindness is *structural*, not procedural). The pre-registered claim was deliberately a
conjunction — no single metric makes a secret-sharing scheme; the protocol IS all three.

## The falsifiers (both on script)

- **noghz** (product state): M = +0.003, reconstruction 0.500, every correlation flat — no
  resource, no protocol, exactly.
- **bellAB — the security anti-pattern**: replace the GHZ with a mere Bell pair between Alice
  and Bob and the scheme *inverts*: ⟨AB⟩ = **+0.902 — one officer reads Alice's every bit
  alone** — while group reconstruction collapses to 0.517 (no shared secret at all). The wrong
  entanglement topology is not "weaker security"; it is the *complement* of the protocol, and
  the data shows both failure modes at once. This is what a compromised vault looks like.

## Honest ledger — one secondary gauge missed, informatively

The sift-discard combos (XXY, YYY — one or three Y's, expectation zero for ideal GHZ) read
**E₃ = +0.096 and −0.101** against a pre-registered |E₃| < 0.05 band — a real ~9σ residual,
not shot noise. Interpretation: a small coherent imperfection in the GHZ prep (the same class
Exp165/178 characterized elsewhere) leaks correlation into the odd-Y sector. It is **harmless
to the protocol** — those rounds are discarded by the sifting rule precisely because they carry
no protocol correlation — but it is a genuine datum about the prep's coherent error structure,
and a reminder that "should be zero" sectors are free diagnostics. Primary legs unaffected.

## Fence

Three qubits on one die (patches, not officers); the secret is Alice's sifted measurement
record (information-theoretic layer only — no authentication, no eavesdropper-detection round
flown here, though the M > 2 certificate is the standard basis for one); HBB99 assumes honest
majority at reconstruction time; bases here were deterministic per circuit rather than
per-shot random (standard for hardware characterization; per-shot randomness is a
randomness-expansion integration, priced as a follow-up, not claimed).

## Where this leaves the wing

The quantum network now demonstrates, certified end-to-end: state teleportation → gate
teleportation → relay computing → keys through untrusted relays → distributed computation →
**multi-party secret sharing**. Ten pre-registered flights in ~28 hours (Exp175–183), every
falsifier on script, every miss (including this cycle's sift-sector residual) converted into a
named datum.
