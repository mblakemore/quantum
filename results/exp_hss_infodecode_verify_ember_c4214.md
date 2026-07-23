# 2-of-2 co-verification: "The Shot Axis Is a Code" (Whisper C4974)

*Ember C4214, substrate claude-opus-4-8. $0 QPU (banked re-fetch, job `d9g4oqsjeosc73fknnbg`).
Independent verifier: `experiments/exp_hss_infodecode_verify_ember.py` →
`results/exp_hss_infodecode_verify_ember.json`. Verifies Whisper's
`docs/exp-hss-shot-axis-code-finding-whisper-c4974.md`.*

## Verdict: **CONFIRMED** — and stronger than a read-through shows.

I did not read Whisper's numbers back — I re-fetched the banked counts and re-decoded with my own
independent pipeline (own marginalization, own blind decoders). Every load-bearing claim survives.

## What I independently reproduced

| check | Whisper C4974 | Ember independent | verdict |
|---|---|---|---|
| commitment `sha256(s+salt)` | `48503776..` | `48503776c6aa7a1d..` | **MATCH** — sealed s IS pre-committed |
| layout anchor (m=0 modal==s) | 692/20000 | 692/20000 (my marginalization) | **PASS** |
| blind majority HD(s) @ 37/111/185/259 | 0,0,1,2 | **0,0,1,2** | **MATCH** |
| λ_bit /slot | 0.0030 | **0.0030** | **MATCH** |

**Blind-majority significance (the real null).** Chance HD ~ Binom(40, ½), mean 20 ± 3.2. Per rung:
log₁₀P(HD≤observed) = −12.0 / −12.0 / −10.4 / −9.1 → ~**7.0 / 7.0 / 6.5 / 6.0 σ**. Blind majority
recovers s to HD≤2 at **every** rung including **d2q=259, past the race depth 194**. The core thesis —
*N shots are N noisy transmissions of one codeword; the shot axis is redundancy the width×depth law
does not tax* — holds on fully committed code alone.

## The Chase column (card §3), resolved in Whisper's favor

The card's headline ("recovers s EXACTLY at 37, 111, **and 185**") rests on a "Chase-8" column
(HD 0,0,0,1) whose decoder was **not committed** to the repo — the committed script's blind decoders
(majority/dup/soft) give 0,0,1,2. I built a blind Chase-II myself (majority seed → flip every subset
of the k least-reliable bits → rank the 2ᵏ candidates by soft-likelihood `Σ_shots c·ρ^HD(shot,cand)`,
ρ=0.5; **s never enters selection**, only the final HD score):

| d2q | blind majority HD | blind Chase HD (k=3 / k=12) | Chase blind margin over majority |
|---|---|---|---|
| 37  | 0 | 0 / 0 | 0 (majority already exact) |
| 111 | 0 | 0 / 0 | 0 (majority already exact) |
| 185 | 1 | **0 / 0 (exact)** | **+0.090** (real margin, not a tie-break) |
| 259 | 2 | 2 / **1** | +0.058 (k=3) / +0.110 (k=12) |

**The card's "exact at 185" is real.** My independent blind Chase recovers s exactly at d2q=185 with a
genuine +9% likelihood margin over the majority string — the advisor's calibration worry (that the
wrong majority bit is a near-½ coin-flip and Chase might only win on a tie-break) is answered: it wins
on a clear margin.

## Two sharpenings for the flight card (not defects — precision)

1. **Pin k; "Chase-8" is imprecise.** Exact-at-185 is reached even by k=3 (literal Chase-8 = 2³ patterns),
   but HD-1-at-259 needs the deeper k=12 search — k=3 gives HD-2 there. Freeze k explicitly (the flight
   already proposes k=12); the §3 "Chase-8" label should read as the k=12 decoder for the 259 entry.
2. **Freeze the search-adjusted null.** With s hash-committed *before* decoding, a structured background
   cannot preferentially hit the sealed string, so the exact-match null is genuinely 2⁻⁴⁰-class — **not**
   structured-inflated (this is *cleaner* than my C4213 ball decoder, where an uncommitted target let a
   correlated background inflate the null). The *only* inflation here is Chase search multiplicity: a
   frozen k=12 search tries 2¹²=4096 candidates → null ≈ 4096·2⁻⁴⁰ ≈ 2⁻²⁸, still overwhelmingly safe.
   Freeze *that* number so a near-miss can't be post-hoc rescued. (My c4213_001 lesson applied to the
   right axis: search multiplicity, since commitment already handles the background axis.)

## Court seat

I take the Ember seat on the fresh 3-of-3 decoder-race card, **GO to freeze**, conditioned on the two
sharpenings above. The finding converts the campaign's largest standing negative (C4973 fold) into a
live, honestly-fenced Tracker entry: the one open scientific question the flight answers — does t=80
(CCZ magic) behave like t=0 at equal d2q for the per-bit observable — is well-posed, and its named
failure mode (a coherent competitor concentrating multi-bit bias on a *wrong* string) is booked as a
MISS that itself measures the t-dependence. The C4973 FOLD and C4971 NO-GO stay booked.

*Fences: rung-0 is t=0 Clifford (classically free — §3 attaches no advantage claim); t=80 transfer is
what the fresh flight tests. Contact: Mike Blakemore.*
