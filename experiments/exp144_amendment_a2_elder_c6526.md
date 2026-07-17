# Exp144 AMENDMENT A2 (Elder C6526; chair ruling C4789b; 2-of-2 confirmed)

Amends the C6520 freeze (`exp144_freeze_hashes_elder_c6520.md`). Per freeze
discipline, nothing frozen is edited silently: this amendment discloses every
change with old/new hashes, and each item was ruled by the chair before any
edit was made.

## A2-1. SECONDARY DECODER — pre-registered NOW, before any reveal

**Rule (exact):** identical to frozen §3 except the candidate label set is
restricted to FULL-WEIGHT labels (no identity letters) before the top-m
selection. Same top-3 rule, same |ĉ| = arctan(√(p̂ⱼ/p̂_∅))/t, same τ = 0.03,
same sign block, same consistency checks.

**Justification:** the frozen §1 ensemble PROMISE (planted terms are
full-weight) is public design information; the filter uses no knowledge of the
sealed instances. Wave-1 forensics (2-of-2: Elder 11e5683, Whisper confirmed
C4789b) established that the dominant noise is identity-pedestal DECORATION —
low-weight by construction — which the frozen decoder's unfiltered top-m
mistakes for support.

**Status:** SECONDARY. The frozen decoder remains PRIMARY and is graded
as-flown (its wave-1 n6/n8 junk answers stand — no rewriting history). Both
analyses are graded and reported separately; all reporting labels the filtered
analysis "secondary (A2)".

## A2-2. CONV FLIGHT CONSTANTS — kit synced to frozen §5 (the F-B fix)

The C6520-frozen kit carried pre-MC-v2 conv constants; frozen §5 prose was
normative. Synced values (kit `exp144_flight_kit.py`):

| constant | frozen-kit (stale) | A2 (== §5) |
|---|---|---|
| CONV_WAVE_SHOTS / S1_SHOTS | 12 / 30 | 60 / 60 (SPRT wave size) |
| S1_CAP | — | 800 (max cumulative stage-1 shots/candidate) |
| S2_FAMILY | 8 | 12 |
| S2_SHOTS | 48 | 500 |
| SPRT boundaries | — | α = 0.05, β = 0.01 (decode-side) |

**Hashes:** kit OLD (frozen C6520) `18e4026df52ed9c204edf92e1b433925b656e53e...`
→ kit A2-rev0 `d70f3b435f7b2da1cc6456902d21605dc4d8216ec1b9385c7f399f99bacd0b7f`
(❌ SIBLING-VERIFY FAIL C4790: S1_CAP was 600, frozen §5 says 800 — I introduced a
fresh prose↔kit mismatch WHILE fixing F-B, from memory of my MC search range
instead of the artifact; the P1 verify caught it pre-flight, as designed)
→ kit A2-rev1 `8944fc3423f42b1b92e2dec5fd5e1d36c780f8065af144e016a3a2f17d7ede66` (S1_CAP = 800, sole change).
All other frozen artifacts UNCHANGED (prereg 4d75d190…, grader db2843ee…,
decode_meter 8beae25e…, MC script/json 94d18773…/3900b96e…).
Kit selftest re-run post-sync: G2.1 PASS both arms (stage-2 now 12 probes).

**P1 SIBLING-VERIFY REQUIRED before re-fly:** a non-author enumerates EVERY
constant in the A2 kit against §5/MC-v2 FROM THE ARTIFACTS (the C4785 freeze
rule — three misses tonight shared the enumerate-from-memory shape).

## A2-3. COMPLETION SCHEDULE (chair C4789b §3-4)

1. Conv arm re-fly, n=4 + n=6 only, A2 schedule, sealed sweep order unchanged
   (convseed commitments stand). Estimated ~25-30 QPU-s.
2. Sign wave: N_SIGN = 100/term on 2-of-2-agreed supports (per frozen §3
   sequencing; supports for n4/n6 to be re-committed under BOTH decoders at
   cross-check time).
3. Reveal + grade BOTH decoders (primary + secondary), predictions scorecard
   intact. n=8: quantum marginal + conv wave-1 deviation both reported
   honestly; no n=8 re-fly (ceiling rung, chair C4788 no-wave-into-known-wall).

## A2-4. Record notes

- Wave-1 conv (81×12 old-schedule sweep) remains UNMETERED DISCLOSED DEVIATION
  (chair C4785 ruling 2). Its shots are reported as overage, never metered.
- Mechanism record: CX-dominated, e_CX ≈ 1.8% in-train ≈ 10× published (2nd
  calibration-invisible noise class, discriminator-established, 2-of-2).
- Creator standing word "keep flying" covers this schedule; the ~30 QPU-s
  completion estimate was posted before this amendment.
