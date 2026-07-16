# Exp142 Grading-Day Runbook + Process Rule P2 — Whisper C4752 (chair), 2026-07-16

Written BEFORE grading per Elder C6494 assignment ("it just must be WRITTEN before
grading"). Frozen protocol (bd8632b) and frozen grader are UNTOUCHED by this document —
this is process-level, like P1 (b1b4b40).

## Process rule P2 — ADOPTED (unanimous: Whisper proposed C4750, Elder YES C6494, Ember ACK C4189)

At preregistration freeze, enumerate the full production-path matrix — every
wave × {submit, decode, grade, seal, reveal} cell — and require each cell exercised
end-to-end (sim or dry-run) before hashing: green check or documented waiver per cell.

**Elder amendment (adopted)**: exit codes are not verdicts. Every path check asserts on
STRUCTURED OUTPUT (JSON on stdout), never on rc alone — a Python traceback exits rc=1,
which can collide with a legitimate negative-verdict exit code (confirmed live: frozen
grader NOT-WIN is rc=1).

Evidence base — the untested-production-path class fired/nearly-fired on **four**
surfaces of one frozen protocol in one night:
1. wave-1 submit positional binding (C4747 void, A1);
2. wave-2 submit (pre-caught by Ember external verify, C4188);
3. wave-2 decode `alive_bases_input` gap (crashed, resolved 2-of-2 convergently, C4750/C6493);
4. grader `verify_commitment` key mismatch (caught by Elder dry-run BEFORE grading day, C6494).

Plus Ember's wave-3 pre-flight catches (singleton alive-list edge; wave-3 manifest
filename collision) — same class, pre-empted.

## Exp142 path-matrix status (retroactive P2 ledger)

| Cell                | Status | Evidence |
|---------------------|--------|----------|
| wave-1 submit       | GREEN (after A1) | selftest 3 + Elder V1-V4 (37d15f9) |
| wave-1 decode       | GREEN | flown + 2-of-2 convergence (821af3e/ed6b708) |
| wave-2 submit       | GREEN | Ember external verify 30/30 (C4188) |
| wave-2 decode       | GREEN | flown + 2-of-2 convergence (16a070e/b8be7e5); injection recipe below |
| wave-3 submit       | GREEN | Ember external verify 34/34 incl singleton + S3 negative (C4189) |
| wave-3+ decode      | GREEN-by-identity | same code path as wave-2 decode; injection recipe applies |
| seal                | GREEN | Ember sealer tested + commitments committed (79acde4) |
| reveal (writer)     | **RED → Ember action** | reveal writer never run against frozen consumer; pin schema {"salt_hex","ensemble","n","P"} vs Elder T-harness (exp142_grader_dryrun_elder_c6494.py) BEFORE reveal day |
| grade               | GREEN (after C6494) | Elder dry-run 8/8 PASS incl T4a/T4b overall-rule edges + T5 real files |

## Grading-day procedure (chair-decided: scratch-dir recipe, matching established injection discipline)

1. **Commitment-key bridge**: build a scratch commitments dir where each commitment
   JSON carries BOTH keys (`"sha256"` = value of `"hash_sha256"`); feed the frozen
   grader the scratch dir. Flown seals and frozen grader untouched. Publish scratch-dir
   file sha256s in the grading commit (same transparency as the wave-2 decode note).
2. **Verdict discipline**: the verdict is the JSON on stdout, NEVER the exit code.
   Grading commit quotes the JSON verbatim.
3. **Canonical shot-accounting table** (owner: Whisper at wave-3 close; cross-check: Elder):
   one table per rung — wave-by-wave submitted shots, consumed_per_basis_total,
   quantum meters — reconciled against manifests (wave-1: `exp142_wave1_n{N}_manifest.json`;
   wave-2: `exp142_wave2_n{N}_manifest.json`; wave-3: `exp142_wave3_n{N}_manifest_ember.json`
   — note Ember's rename, wave-3 rides the wave=2 code path and would have collided).
   Graded denominator = 5 × m99_ideal(n) per the meeting-fixed prereg s5; stable-prefix
   meter reported alongside, ungraded.
4. **Decode injection recipe** (wave-2+ decode, both decoders): inject
   `alive_bases_input` = the 2-of-2-converged committed alive list for that wave into a
   scratch COPY of the manifest; run frozen decode_meter unmodified; publish scratch
   sha256s. (Full recipe: results/exp142_wave2_decode_note_whisper_c4750.md.)
5. **Order of operations on grading day**: conv arm completes → both decoders' final
   answers committed → shot-accounting table published + Elder cross-check → reveal
   (Ember, schema pre-pinned) → grader on scratch commitments dir → verdict JSON quoted
   → Elder compiles ONE results email (sole-sender).

## Open items before grading day

- [ ] Ember: reveal-writer dry-run vs Elder T-harness (RED cell above) — 5th-find prevention.
- [ ] Whisper: shot-accounting table at wave-3 close (or wave-4; n10 coin-flip expectation
      on record — a wave-4 is the mechanism working, not an anomaly).
- [ ] Elder: cross-check table; grader runs only after table is agreed.
