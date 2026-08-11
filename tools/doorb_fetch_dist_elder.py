#!/usr/bin/env python3
"""doorb_fetch_dist_elder.py — decode-seat fetch for the F122 DISTRIBUTION batch (Elder, C6601).

Same verification logic as doorb_fetch_refly_elder.py (C6599) VERBATIM — the blind discipline
is the logic, not the path — with the manifest taken from argv because the refly script's
hardcoded MANIFEST was a frozen-tool-shape that breaks at the next rung (each distribution
instance has its own flight manifest). Chartered by the seats ruling; prereg sha256 31246d34…
AT quantum@67afd41; incremental-atomic per instance.

Usage: doorb_fetch_dist_elder.py <flight-manifest.json> <instance-number>

Token: IBMQ_ALT3 from DC15W/.env — one-line read, never printed, never persisted.
Blind discipline: touches ONLY raw bitstrings + the public manifest. No P, no draws, no sealed
material exists anywhere it can reach. Outputs verified against the manifest EXACTLY (per-job
row counts, total shots) — a mismatch REFUSES rather than proceeds.
"""
import hashlib, json, os, re, sys

REPO = "/droid/repos/quantum"

# C6605: THIS FUNCTION WAS `alt3_token()` AND HARD-CODED IBMQ_ALT3 FROM ONE .env PATH.
# i3 flew on **ALT4**, so the decode path would have opened the WRONG ACCOUNT — and an account
# that does not hold the jobs returns "not found", which reads as a failed flight rather than as a
# wrong-tank lookup. That is the PAID_CRN defect exactly (a constant naming an account the code no
# longer uses), landing on the retrieval side within an hour of us fixing it on the submit side.
# THE ACCOUNT IS NOW NAMED BY THE CALLER and searched across the known env files. No default:
# refusing beats guessing, because a silent wrong-account read is indistinguishable from an empty
# result. Resolve the right name with:
#     python3 tools/registry_fit_precheck.py --need <s> --venue <backend> --resolve
ENV_FILES = ("/droid/repos/DC15W/.env", "/mnt/droid/repos/digital-creature-1.5/.env",
             "/droid/repos/quantum/.env", "/droid/repos/market-bot/.env")

def account_token(env_var):
    """Read a NAMED credential. Never printed, never persisted, never defaulted."""
    for path in ENV_FILES:
        try:
            with open(path) as f:
                for line in f:
                    m = re.match(rf"^{re.escape(env_var)}=(.+)$", line.strip())
                    if m:
                        return m.group(1).strip().strip('"').strip("'")
        except OSError:
            continue
    sys.exit(f"REFUSE: {env_var} not found in any known env file — NOT falling back to another "
             f"account. A wrong-account fetch returns 'no jobs', which reads as a failed flight.")

def main():
    if len(sys.argv) not in (3, 4):
        sys.exit("usage: doorb_fetch_dist_elder.py <flight-manifest.json> <instance-number> "
                 "[ACCOUNT_ENV_VAR]   (e.g. IBMQ_ALT4 — the account the flight ACTUALLY used; "
                 "resolve it with registry_fit_precheck --resolve)")
    acct_var = sys.argv[3] if len(sys.argv) == 4 else os.environ.get("QPU_ACCOUNT_VAR")
    if not acct_var:
        sys.exit("REFUSE: no account named. Pass ACCOUNT_ENV_VAR or set QPU_ACCOUNT_VAR. "
                 "This tool used to hard-code IBMQ_ALT3; i3 flew on ALT4 and that silent default "
                 "would have looked like a failed flight.")
    manifest_path, inst = sys.argv[1], int(sys.argv[2])
    man = json.load(open(manifest_path))
    n = man["n"]; jobs = man["jobs"]; cal_rows_declared = man["cal_rows"]
    total_shots_declared = man["shots"]
    assert jobs[0]["role"].startswith("calibration"), "lead job is not the calibration block"

    from qiskit_ibm_runtime import QiskitRuntimeService
    svc = QiskitRuntimeService(channel="ibm_quantum_platform", token=account_token(acct_var))

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

    sci_path = f"{REPO}/results/doorb_dist_i{inst}_raw_science_n{n}_elder.json"
    cal_path = f"{REPO}/results/doorb_dist_i{inst}_raw_cal_n{n}_elder.json"
    json.dump({"n": n, "shots": science}, open(sci_path, "w"))
    json.dump({"n": n, "shots": cal}, open(cal_path, "w"))
    h = hashlib.sha256(json.dumps({"n": n, "shots": science}, sort_keys=True).encode()).hexdigest()
    print(f"FETCH COMPLETE: cal {len(cal)} rows, science {len(science)} rows")
    print(f"raw science record sha256: {h}")
    print(f"science -> {sci_path}")
    print(f"cal     -> {cal_path}")

if __name__ == "__main__":
    main()
