#!/usr/bin/env python3
"""DOOR (a) DECODE-SEAT FETCH + ASSEMBLY — Elder C6593.

Fetches the raw outcome bitstrings of the two flown jobs and assembles the
decoder-input flight file for tools/doora_grader_elder.py decode mode.

WHAT THIS SCRIPT TOUCHES AND WHAT IT NEVER TOUCHES:
  - Reads the IBMQ_ALT token by the one-line-read pattern (never printed, never
    persisted, never logged). Fetching OUTCOMES is the decode seat's role.
  - NEVER opens ~/.ember-doora-secrets.json. Labels and A stay with Ember until
    the decisions.json SHA-256 is on the bus. This script consumes job outputs only.

ROW MAP (Ember quantum@ad2957b, read from the COMMITTED builder, not memory):
  probe job d9riuo9dsedc73agnft0 : 33 rows. row 0 = SEALED TRIAL 1;
                                   rows 1-32 = PUBLIC-A calibration anchor (K=32).
  main  job d9rj3vgpdb6s73e500mg : 39 rows. row j = SEALED TRIAL j+2 (trials 2-40).

OUTPUTS (both public by construction — outcome bits and public-A rows, no labels):
  results/doora_rawflight_n8_elder_c6593.json      decoder-input: {"8": {window_id,
                                                   Q:[[77 raw 16-bit strings] x 40], C1:[]}}
  results/doora_calibration_rows_n8_elder_c6593.json  the 32 public calibration rows,
                                                   kept OUT of the decode input; consumed
                                                   only via the frozen u_anchor formula at
                                                   grade time (u_anchor = 2*freq - 1).
"""
import json, os, re, sys

REPO = "/droid/repos/quantum"
PROBE_JOB = "d9riuo9dsedc73agnft0"
MAIN_JOB = "d9rj3vgpdb6s73e500mg"
N = 8
SHOTS = 77
WINDOW_ID = "ibm_marrakesh_2026-08-08"

def alt_token():
    with open("/droid/repos/DC15W/.env") as f:
        for line in f:
            m = re.match(r"^IBMQ_ALT=(.+)$", line.strip())
            if m:
                return m.group(1).strip().strip('"').strip("'")
    sys.exit("REFUSE: IBMQ_ALT not found")

def rows_of(job, expect_rows):
    res = job.result()
    ba = res[0].data.c
    # BitArray leading shape = parameter rows; num_shots per row = SHOTS
    if list(ba.shape) != [expect_rows]:
        sys.exit(f"REFUSE: {job.job_id()} data.c shape {ba.shape} != ({expect_rows},)")
    if ba.num_shots != SHOTS:
        sys.exit(f"REFUSE: {job.job_id()} num_shots {ba.num_shots} != {SHOTS}")
    out = []
    for i in range(expect_rows):
        strs = ba[i].get_bitstrings()
        if len(strs) != SHOTS or any(len(s) != 2 * N for s in strs):
            sys.exit(f"REFUSE: row {i} malformed ({len(strs)} shots, widths "
                     f"{sorted(set(len(s) for s in strs))})")
        out.append(strs)
    return out

def main():
    from qiskit_ibm_runtime import QiskitRuntimeService
    svc = QiskitRuntimeService(channel="ibm_quantum_platform", token=alt_token())
    probe = svc.job(PROBE_JOB)
    main_j = svc.job(MAIN_JOB)
    for j in (probe, main_j):
        st = str(j.status())
        if "DONE" not in st.upper():
            sys.exit(f"REFUSE: job {j.job_id()} status {st} != DONE")

    probe_rows = rows_of(probe, 33)
    main_rows = rows_of(main_j, 39)

    # Sealed-order trial assembly per the row map
    trials = [probe_rows[0]] + main_rows          # trial 1, then trials 2..40
    assert len(trials) == 40
    cal_rows = probe_rows[1:33]                   # K=32 public calibration rows

    flight = {"8": {"window_id": WINDOW_ID, "Q": trials, "C1": []},
              "_provenance": {
                  "assembled_by": "elder decode seat, tools/doora_fetch_assemble_elder.py",
                  "jobs": {"probe": PROBE_JOB, "main": MAIN_JOB},
                  "row_map_source": "quantum@ad2957b (Ember, read from committed builder)",
                  "note": "outcome bitstrings only; labels and A remain sealed with Ember"}}
    cal = {"n": N, "K": 32, "job": PROBE_JOB, "rows": cal_rows,
           "note": ("PUBLIC-A calibration anchor rows (seeds 9000+i). Excluded from "
                    "decode by rule; consumed at grade time only through "
                    "u_anchor = 2*accept_freq - 1 (frozen formula).")}

    p1 = os.path.join(REPO, "results/doora_rawflight_n8_elder_c6593.json")
    p2 = os.path.join(REPO, "results/doora_calibration_rows_n8_elder_c6593.json")
    json.dump(flight, open(p1, "w"), indent=1)
    json.dump(cal, open(p2, "w"), indent=1)
    print(f"wrote {p1}  (40 trials x {SHOTS} shots x {2*N} bits)")
    print(f"wrote {p2}  (32 public calibration rows)")
    # Verification by counts/booleans only — never values that could carry anything sealed
    ones = sum(s.count("1") for t in trials for s in t)
    tot = 40 * SHOTS * 2 * N
    print(f"sanity: total bits {tot}, ones fraction {ones/tot:.4f} (should be ~mid-range, not 0/1)")

if __name__ == "__main__":
    main()
