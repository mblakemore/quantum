#!/usr/bin/env python3
"""H15 N1 landing — fetch raw actuator records verbatim + bank (Ember).

Custody law: the moment the job is DONE the raw per-circuit measurement records
come to disk UNTOUCHED — no decode, no seal opened. Each of the 696 circuits
carries three classical registers (act/dec/bell); banked as the mem-line
'act dec bell' the kit's classical_rule consumes, in FLIGHT ORDER so the public
row map's positions line up. The grader reads c_act only; the cal contract pins
the actuator-bit convention. Refuses unless DONE and exactly 696 records.
"""
import sys, os, re, json, hashlib, datetime

JOB_ID = "da14kue3kjvs7386a2l0"
BACKEND = "ibm_marrakesh"
EXPERIMENT = "h15_positronic_v1_n1"
COMMITMENT = "b96ee93b29983352a543c25969fee3bba720e45cc2ee06e252449529cb2914f1"
N, M, C, TOTAL = 4, 632, 64, 696
ALT5_CRN = ("crn:v1:bluemix:public:quantum-computing:us-east:"
            "a/7044ec3a6d9149138a144e3e3487c4bb:"
            "22647176-d5b2-4692-b224-84a0b3c637f0::")
OUT = f"results/h15_n1_raw_{JOB_ID}.json"


def alt5_token():
    for envp in ("/mnt/droid/repos/DC15E/.env", "/droid/repos/DC15E/.env"):
        if os.path.exists(envp):
            for line in open(envp):
                m = re.match(r"^IBMQ_ALT5=(.+)$", line.strip())
                if m:
                    return m.group(1).strip().strip('"').strip("'")
    sys.exit("REFUSE: IBMQ_ALT5 not found in DC15E .env")


def one_bits(bitarray_field):
    """Single-shot bitstring from a SamplerV2 BitArray register field."""
    bs = bitarray_field.get_bitstrings()
    if len(bs) != 1:
        sys.exit(f"REFUSE: register carried {len(bs)} shots != 1 (S=1 violated).")
    return bs[0]


def main():
    from qiskit_ibm_runtime import QiskitRuntimeService
    svc = QiskitRuntimeService(channel="ibm_quantum_platform",
                               token=alt5_token(), instance=ALT5_CRN)
    job = svc.job(JOB_ID)
    st = getattr(job.status(), "name", str(job.status()))
    if st != "DONE":
        print(f"NOT DONE yet — job {JOB_ID} status {st}. Not banking.")
        return 2

    res = job.result()
    if len(res) != TOTAL:
        sys.exit(f"REFUSE: {len(res)} pub-results != {TOTAL} circuits.")

    rows = []
    for i in range(TOTAL):
        d = res[i].data
        fields = {f for f in dir(d) if not f.startswith("_")}
        for reg in ("act", "dec", "bell"):
            if reg not in fields:
                sys.exit(f"REFUSE: pub {i} missing register '{reg}' (have {sorted(fields)}).")
        # mem-line format the kit's classical_rule consumes: 'act dec bell'
        rows.append(f"{one_bits(d.act)} {one_bits(d.dec)} {one_bits(d.bell)}")

    bank = {"job_id": JOB_ID, "backend": BACKEND, "experiment": EXPERIMENT,
            "commitment_sha256": COMMITMENT, "n": N, "M": M, "C": C, "total": TOTAL,
            "shots": 1, "mem_format": "act dec bell (space-sep, per kit.classical_rule)",
            "rows": rows}
    os.makedirs("results", exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(bank, f)
    h = hashlib.sha256(json.dumps(rows, separators=(",", ":")).encode()).hexdigest()
    print(f"BANKED {len(rows)} actuator records ({TOTAL} circuits x 1 shot) -> {OUT}")
    print(f"  records sha256/16 {h[:16]}  (mem-line 'act dec bell')")
    print(f"  UTC {datetime.datetime.now(datetime.timezone.utc).isoformat()}")
    print("  seal SHUT on my seat — decoders commit blind from c_act, then I open the reveal.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
