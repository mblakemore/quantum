# Exp 30 — SUBMIT BLOCKED (no job_id yet)

**Status (Whisper C3734, 2026-05-29)**: design + pre-registration + sim-validation COMPLETE;
**hardware submission FAILED** — no IBM Quantum job was created.

- Error: `QiskitBackendNotFoundError: No backend matches the criteria` at
  `service.backend("ibm_marrakesh")`, after runtime WARNING `Invalid instance crn:v1:...us-east:...`
  → fell back to `open` plan (premium Heron-r2 not visible).
- Root cause: saved account instance binding dropped mid-session (instance field empty;
  service discovery hangs on the invalid CRN). NOT a budget issue.
- Exp23–29 submitted to ibm_marrakesh fine earlier today, so access was live and dropped.

**No design change needed.** Once the premium instance is restored:
`python3 scripts/run_exp30_gatecount_vs_duration.py --submit` then `--finalize <job_id>`.
The `30-...-results.json` currently holds the FakeMarrakesh **sim preview** (job_id="FakeMarrakesh-sim"),
not hardware. Creator notified; full diagnosis in DC15W `logs/boundaries.md` C3734.
