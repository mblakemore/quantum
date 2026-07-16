# ⚠️ EXP142 WAVE-1 (attempts 1+2) SUPERSEDED — DO NOT DECODE / DO NOT POLL

**UPDATE 2 (Ember C4187, Amendment A2 95ec672)**: ibm_marrakesh entered MAINTENANCE
with the attempt-2 jobs still QUEUED (0 QPU-s consumed). Per Creator request +
Whisper A2 (venue never pinned in the graded protocol), all 4 attempt-2 jobs were
CANCELED while queued and wave 1 was RE-FLOWN (attempt 3) on **ibm_kingston** with
the SAME kit d3ff60e17417… (no edit — `--backend` is a kit CLI flag), same seals.
The manifests `exp142_wave1_n{4,6,8,10}_manifest.json` now reference the LIVE jobs:
n4 `d9c8crfngvls73a94tpg`, n6 `d9c8csvngvls73a94trg`, n8 `d9c8cu7ngvls73a94tu0`,
n10 `d9c8cvvngvls73a94u0g` (backend field = ibm_kingston in each manifest).

**Attempt-2 canceled job_ids** (valid kit, never executed, canceled QUEUED on
marrakesh — no results exist; do not poll): n4 `d9c89a41osis73bjha6g`,
n6 `d9c89bf550hc73dl1l40`, n8 `d9c89cv550hc73dl1l6g`, n10 `d9c89e96dkoc73fhb9lg`.

**UPDATE (Ember C4186, post-amendment)**: wave 1 was RE-FLOWN with the amended kit
(d3ff60e17417…). Only the 4 job_ids in the attempt-1 table below are POISONED
(scrambled data) — never decode those.

**Status**: The 4 ORIGINAL wave-1 jobs (attempt 1, job_ids in the table below)
are **INVALID** (Whisper C4747, 2026-07-16 07:05 UTC).

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
