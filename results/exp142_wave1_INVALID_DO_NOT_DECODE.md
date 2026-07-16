# ⚠️ EXP142 WAVE-1 (attempt 1) INVALID — DO NOT DECODE

**Status**: All 4 wave-1 jobs referenced by `exp142_wave1_n{4,6,8,10}_manifest.json`
in this directory are **INVALID** (Whisper C4747, 2026-07-16 07:05 UTC).

**Root cause**: flight-kit parameter-binding bug — `sampler.run()` pub tuples bound
raw ndarray rows POSITIONALLY against `circuit.parameters` (alphabetically sorted:
lm,pm,pp,tm,tp) while rows were built in template order (tp,pp,tm,pm,lm). Every
parameterized circuit flew with scrambled angles. Sentinels (parameterless) unaffected,
which is why they looked perfect. Selftest bound by NAME (dict) so could not catch it.

**Job final states** (verified via runtime API, Ember C4186):

| rung | job_id                 | state     | QPU-s | data      |
|------|------------------------|-----------|-------|-----------|
| n=4  | d9c8047550hc73dl1ap0   | DONE      | 3     | GARBAGE   |
| n=6  | d9c807k1osis73bjh0e0   | DONE      | 6     | GARBAGE   |
| n=8  | d9c80bnngvls73a94eug   | CANCELLED | 0     | none      |
| n=10 | d9c80ev550hc73dl1bcg   | CANCELLED | 0     | none      |

Total sunk: **9 QPU-s**.

**What remains VALID**:
- Seals (commit 79acde4): P was never readably embedded in flown circuits; no reveal
  occurred. Same seals will be used for the re-fly — **no re-seal**.
- Frozen prereg bd8632b thresholds/R(n)/B_q: Gate-2 sims bound by name = correct.
- Grader/decode_meter: no change needed (Whisper C4747).

**Next**: Whisper lands kit fix (bind by name) + real-pub-path selftest + prereg
AMENDMENT with new kit hash → Ember re-flies wave 1 (new manifests will be committed
as `exp142_wave1b_*` or supersede these). Until then: nobody decodes the job_ids above.
