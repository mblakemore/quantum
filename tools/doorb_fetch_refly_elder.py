#!/usr/bin/env python3
"""doorb_fetch_refly_elder.py — decode-seat fetch of the door(b) RE-FLY (Elder, C6599).

Chartered by the seats ruling (register=Whisper, seal+fly=Ember, decode=Elder) for flight
d9sifr8pdb6s73e63140 (22 chunked jobs, seal b3fb6cfe..., go general#8174 bound #8186).

Token: IBMQ_ALT3 from DC15W/.env — one-line read, never printed, never persisted.
Blind discipline: this script touches ONLY raw bitstrings + the public manifest. No P, no
draws, no sealed material exists anywhere it can reach. Outputs verified against the manifest
EXACTLY (per-job row counts, total shots) — a mismatch REFUSES rather than proceeds.
"""
import hashlib, json, re, sys

REPO = "/droid/repos/quantum"
MANIFEST = f"{REPO}/results/doorb_flight_n16_d9sifr8pdb6s73e63140.json"

def alt3_token():
    with open("/droid/repos/DC15W/.env") as f:
        for line in f:
            m = re.match(r"^IBMQ_ALT3=(.+)$", line.strip())
            if m:
                return m.group(1).strip().strip('"').strip("'")
    sys.exit("REFUSE: IBMQ_ALT3 not found")

def main():
    man = json.load(open(MANIFEST))
    n = man["n"]; jobs = man["jobs"]; cal_rows_declared = man["cal_rows"]
    total_shots_declared = man["shots"]
    assert jobs[0]["role"].startswith("calibration"), "lead job is not the calibration block"

    from qiskit_ibm_runtime import QiskitRuntimeService
    svc = QiskitRuntimeService(channel="ibm_quantum_platform", token=alt3_token())

    cal, science = [], []
    for i, j in enumerate(jobs):
        job = svc.job(j["job_id"])
        st = str(job.status()).upper()
        if "DONE" not in st:
            sys.exit(f"REFUSE: job {i} {j['job_id']} status {st} — not decoding a partial flight")
        res = job.result()
        rows = []
        for pub in res:
            rows.extend(pub.data.c.get_bitstrings())
        if len(rows) != j["rows"]:
            sys.exit(f"REFUSE: job {i} {j['job_id']} rows {len(rows)} != manifest {j['rows']}")
        if any(len(r) != 2 * n for r in rows[:5]):
            sys.exit(f"REFUSE: job {i} bitstring width != 2n")
        if i == 0:
            cal.extend(rows)
        else:
            science.extend(rows)
        print(f"  job {i:2d} {j['job_id']} rows={len(rows)} OK")

    if len(cal) != cal_rows_declared:
        sys.exit(f"REFUSE: cal rows {len(cal)} != declared {cal_rows_declared}")
    if len(science) != total_shots_declared:
        sys.exit(f"REFUSE: science rows {len(science)} != declared shots {total_shots_declared}")

    sci_path = f"{REPO}/results/doorb_refly_raw_science_n16_elder.json"
    cal_path = f"{REPO}/results/doorb_refly_raw_cal_n16_elder.json"
    json.dump({"n": n, "shots": science}, open(sci_path, "w"))
    json.dump({"n": n, "shots": cal}, open(cal_path, "w"))
    h = hashlib.sha256(json.dumps({"n": n, "shots": science}, sort_keys=True).encode()).hexdigest()
    print(f"FETCH COMPLETE: cal {len(cal)} rows, science {len(science)} rows")
    print(f"raw science record sha256: {h}")

if __name__ == "__main__":
    main()
