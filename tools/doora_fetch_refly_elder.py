#!/usr/bin/env python3
"""DOOR (a) RE-FLY DECODE-SEAT FETCH — Elder C6593. Adapted from the flown
tools/doora_fetch_assemble_elder.py (copy-not-improve; differences declared):
  1. Job d9rqc5ntfhrs73ds0o20 on the MAIN account (IBMQ_TOKEN, one-line read, never
     printed) — the re-fly flew on WhisperPaid.
  2. 40 rows x 316 shots (row i = SEALED TRIAL i+1 — read from the COMMITTED
     tools/doora_mainfly_ember_c4262.py line 132, not asserted from memory).
  3. No calibration rows in this job (the paid anchor d9rq1qfpemts73csulrg carries them).
NEVER touched: ~/.ember-doora-secrets.json. Outcome bitstrings only.
"""
import json, os, re, sys

REPO = "/droid/repos/quantum"
JOB = "d9rqc5ntfhrs73ds0o20"
N, ROWS, SHOTS = 8, 40, 316

def main_token():
    with open("/droid/repos/DC15W/.env") as f:
        for line in f:
            m = re.match(r"^IBMQ_TOKEN=(.+)$", line.strip())
            if m:
                return m.group(1).strip().strip('"').strip("'")
    sys.exit("REFUSE: IBMQ_TOKEN not found")

def main():
    from qiskit_ibm_runtime import QiskitRuntimeService
    svc = QiskitRuntimeService(channel="ibm_quantum_platform", token=main_token())
    job = svc.job(JOB)
    st = str(job.status())
    if "DONE" not in st.upper():
        sys.exit(f"NOT READY: job {JOB} status {st}")
    try:
        billed = job.usage()
    except Exception:
        billed = "unreadable"
    ba = job.result()[0].data.c
    if list(ba.shape) != [ROWS] or ba.num_shots != SHOTS:
        sys.exit(f"REFUSE: shape {ba.shape} shots {ba.num_shots} != ({ROWS},)/{SHOTS}")
    trials = []
    for i in range(ROWS):
        strs = ba[i].get_bitstrings()
        if len(strs) != SHOTS or any(len(s) != 2 * N for s in strs):
            sys.exit(f"REFUSE: row {i} malformed")
        trials.append(strs)
    flight = {"8": {"window_id": "ibm_marrakesh_2026-08-08_refly", "Q": trials, "C1": []},
              "_provenance": {"job": JOB, "billed_seconds": billed,
                  "row_map": "row i = sealed trial i+1 (committed mainfly line 132)",
                  "note": "outcome bitstrings only; labels sealed with Ember (commitment ff43996c...)"}}
    p1 = os.path.join(REPO, "results/doora_rawflight_refly_n8_elder_c6593.json")
    json.dump(flight, open(p1, "w"), indent=1)
    ones = sum(s.count("1") for t in trials for s in t)
    tot = ROWS * SHOTS * 2 * N
    print(f"wrote {p1}")
    print(f"billed: {billed}s | sanity: {tot} bits, ones fraction {ones/tot:.4f}")

if __name__ == "__main__":
    main()
