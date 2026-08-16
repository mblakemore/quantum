#!/usr/bin/env python3
"""DOOR (a) FLIGHT-4 landing — fetch raw outcomes verbatim + bank on disk (Ember).

Custody law (flight-3 de74f76): the moment the job is DONE, the raw measured
bitstrings come to disk UNTOUCHED — P-independent, no decode, no seal opened.
The seal stays SHUT on my seat until Elder hashes decisions pre-unseal and both
decoders commit; this tool ONLY banks.

Output mirrors the flight-3 raw bank byte-for-byte in schema:
  {job_id, backend, experiment, commitment_sha256, n, pub_rows, shots,
   pubs:[{"c":[<pub_rows*shots row-major bitstrings>]}]}

Ordering is row-major and EXPLICIT (per-parameter-row loop, 632 shots each) so
the grader's row_map positions (0..111) line up with the sealed/cal interleave.
Refuses to bank unless the job is DONE and the shape is exactly 112*632.
"""
import sys, os, re, json, hashlib, datetime

JOB_ID = "da123seg52gs73cl41jg"
BACKEND = "ibm_marrakesh"
EXPERIMENT = "doora_deg2phase_v1_flight5"
COMMITMENT = "f75f7540109472a09c409943f0253ced63149790b19ef13a576cdf53838e6622"
N = 8
PUB_ROWS = 112          # 80 sealed + 32 cal
SHOTS = 632
EXPECT_STRINGS = PUB_ROWS * SHOTS          # 70,784 (112 x 632)
ALT5_CRN = ("crn:v1:bluemix:public:quantum-computing:us-east:"
            "a/7044ec3a6d9149138a144e3e3487c4bb:"
            "22647176-d5b2-4692-b224-84a0b3c637f0::")
OUT = f"results/doora_flight5_raw_{JOB_ID}.json"


def alt5_token():
    for envp in ("/mnt/droid/repos/DC15E/.env", "/droid/repos/DC15E/.env"):
        if os.path.exists(envp):
            for line in open(envp):
                m = re.match(r"^IBMQ_ALT5=(.+)$", line.strip())
                if m:
                    return m.group(1).strip().strip('"').strip("'")
    sys.exit("REFUSE: IBMQ_ALT5 not found in DC15E .env")


def main():
    from qiskit_ibm_runtime import QiskitRuntimeService
    svc = QiskitRuntimeService(channel="ibm_quantum_platform",
                               token=alt5_token(), instance=ALT5_CRN)
    job = svc.job(JOB_ID)
    st = job.status()
    st = getattr(st, "name", str(st))
    if st != "DONE":
        print(f"NOT DONE yet — job {JOB_ID} status {st}. Not banking.")
        return 2

    res = job.result()
    pub = res[0]
    # classical register name: flight-3 banked under 'c'. Introspect defensively.
    data = pub.data
    fields = [f for f in dir(data) if not f.startswith("_")]
    creg = "c" if "c" in fields else None
    if creg is None:
        # pick the single BitArray-bearing attribute
        cands = [f for f in fields if hasattr(getattr(data, f), "get_bitstrings")]
        if len(cands) != 1:
            sys.exit(f"REFUSE: cannot identify classical register (candidates {cands})")
        creg = cands[0]
    ba = getattr(data, creg)

    # EXPLICIT row-major: row 0's 632 shots, then row 1's, ... row 111's.
    strings = []
    nrows = ba.shape[0] if ba.shape else 1
    if nrows != PUB_ROWS:
        sys.exit(f"REFUSE: pub broadcast rows {nrows} != {PUB_ROWS}")
    for i in range(nrows):
        row = ba[i].get_bitstrings()
        if len(row) != SHOTS:
            sys.exit(f"REFUSE: row {i} has {len(row)} shots != {SHOTS}")
        strings.extend(row)

    if len(strings) != EXPECT_STRINGS:
        sys.exit(f"REFUSE: banked {len(strings)} strings != {EXPECT_STRINGS}")

    bank = {"job_id": JOB_ID, "backend": BACKEND, "experiment": EXPERIMENT,
            "commitment_sha256": COMMITMENT, "n": N, "pub_rows": PUB_ROWS,
            "shots": SHOTS, "pubs": [{"c": strings}]}
    os.makedirs("results", exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(bank, f)
    h = hashlib.sha256(json.dumps(bank["pubs"], separators=(",", ":")).encode()).hexdigest()
    print(f"BANKED {len(strings):,} rows ({PUB_ROWS}x{SHOTS}) -> {OUT}")
    print(f"  outcomes sha256/16 {h[:16]}  bitwidth {len(strings[0])}")
    print(f"  UTC {datetime.datetime.now(datetime.timezone.utc).isoformat()}")
    print("  seal SHUT on my seat — decoders commit blind, then I open the reveal.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
