#!/usr/bin/env python3
"""doorb_fetch_refly_elder.py — decode-seat fetch of the door(b) RE-FLY (Elder, C6599).

Chartered by the seats ruling (register=Whisper, seal+fly=Ember, decode=Elder) for flight
d9sifr8pdb6s73e63140 (22 chunked jobs, seal b3fb6cfe..., go general#8174 bound #8186).

Token: IBMQ_ALT3 from DC15W/.env — one-line read, never printed, never persisted.
Blind discipline: this script touches ONLY raw bitstrings + the public manifest. No P, no
draws, no sealed material exists anywhere it can reach. Outputs verified against the manifest
EXACTLY (per-job row counts, total shots) — a mismatch REFUSES rather than proceeds.
"""
import argparse, hashlib, json, os, re, sys

# PARAMETERISED 2026-08-29 so a SECOND flight can be fetched without a copy of this file.
# It was pinned to one manifest, one token env and one output name; the n-ladder P2 flight
# needed all three different. A reimplementation is exactly where the REFUSE checks below
# get dropped by whoever is in a hurry, so the one definition grew arguments instead.
#
# NO IMPLICIT FLIGHT SELECTION — --manifest is REQUIRED and has no default. A default
# pointing at the previous flight is the same defect as a runner that silently bound an
# exhausted account: it does something plausible with no argument and the operator reads
# success as agreement. Wrong flight is worse than no flight.
#
# REPO is DERIVED, never hardcoded — the old absolute path made this work only for a
# checkout at that exact location, and hid because here they are the same directory.
REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def read_token(env_file, var):
    """One-line read of a token env var. Never printed, never persisted."""
    try:
        with open(env_file) as f:
            for line in f:
                m = re.match(rf"^{re.escape(var)}=(.+)$", line.strip())
                if m:
                    return m.group(1).strip().strip('"').strip("'")
    except OSError as e:
        sys.exit(f"REFUSE: cannot read {env_file} ({e.__class__.__name__})")
    sys.exit(f"REFUSE: {var} not found in {env_file}")

def main():
    ap = argparse.ArgumentParser(description="decode-seat fetch of a door(b) flight")
    ap.add_argument("--manifest", required=True,
                    help="flight manifest JSON (REQUIRED — no default; see note above)")
    ap.add_argument("--env-file", default="/droid/repos/DC15W/.env")
    ap.add_argument("--token-env", default="IBMQ_ALT3")
    ap.add_argument("--tag", required=True,
                    help="output name tag, e.g. 'p2_n16' -> results/doorb_raw_{science,cal}_<tag>.json")
    a = ap.parse_args()

    man = json.load(open(a.manifest))
    n = man["n"]; jobs = man["jobs"]; cal_rows_declared = man["cal_rows"]
    total_shots_declared = man["shots"]
    assert jobs[0]["role"].startswith("calibration"), "lead job is not the calibration block"
    print(f"  manifest {a.manifest}\n  n={n} cal_rows={cal_rows_declared} "
          f"science_shots={total_shots_declared} jobs={len(jobs)} token_env={a.token_env}")

    from qiskit_ibm_runtime import QiskitRuntimeService
    svc = QiskitRuntimeService(channel="ibm_quantum_platform",
                               token=read_token(a.env_file, a.token_env))

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

    sci_path = f"{REPO}/results/doorb_raw_science_{a.tag}.json"
    cal_path = f"{REPO}/results/doorb_raw_cal_{a.tag}.json"
    json.dump({"n": n, "shots": science}, open(sci_path, "w"))
    json.dump({"n": n, "shots": cal}, open(cal_path, "w"))
    h = hashlib.sha256(json.dumps({"n": n, "shots": science}, sort_keys=True).encode()).hexdigest()
    print(f"FETCH COMPLETE: cal {len(cal)} rows, science {len(science)} rows")
    print(f"raw science record sha256: {h}")

if __name__ == "__main__":
    main()
