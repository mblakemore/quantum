#!/usr/bin/env python3
"""DOOR-family H15 N1 positronic-neuron reflex flight binder (Ember).

Flies the frozen public kit (experiments/h15_n2_public_kit_whisper_c5074.py) on
the sealed multi-instance secret. The kit builds the 696 circuits (632 graded +
64 cal) and the public row map; this binder supplies the SEALED rows (labels
never leave this seat), runs the gate stack, transpiles, and submits ONE job at
S=1. Custody model (ratified coordination#12447/#12468):
  public deterministic schedule (kit) + frozen kit circuits (hash-gated) +
  G-PUBLIC pre-commit + blind decode from c_act alone + decisions-hash pre-unseal
  + NO selective resubmission (one job; any resubmit reasoned on record first).

BINDING TRIPLE: n=4, M=632 sealed single-shot (316 ALT / 316 NULL), S=1.
COMMITMENT b96ee93b (multi-instance: 316 distinct A + 316 sealed xu + labels).
Threshold frozen 0.6040. MCM 3x billing carried in G-FIT.
"""
import sys, os, re, json, hashlib, importlib.util, argparse

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
KIT_PATH = os.path.join(REPO, "experiments", "h15_n2_public_kit_whisper_c5074.py")
KIT_SHA = "9cbd70471fc4a4f2"          # two-seat verified (Whisper #12475)
SEALER_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                           "h15_positronic_sealer_ember.py")
SECRETS = os.path.expanduser("~/.ember-doora-secrets.json")
STORE_KEY = "h15_positronic_v1:4"
COMMITMENT = "b96ee93b29983352a543c25969fee3bba720e45cc2ee06e252449529cb2914f1"
COMMIT_FILE = "experiments/doora_commitments/h15_positronic_commitment_n4.json"
ALT5_CRN = ("crn:v1:bluemix:public:quantum-computing:us-east:"
            "a/7044ec3a6d9149138a144e3e3487c4bb:"
            "22647176-d5b2-4692-b224-84a0b3c637f0::")
SEED_TRANSPILE = 5074
SAFE_2Q = 0.039                        # marrakesh safe-score doctrine (prereg §1)
# MCM 3x billing: 696 executions, Whisper budget est 30-90 QPU-s. Use the top of
# the band x1.25 as the conservative G-FIT number (never under-estimate a spend).
_EST_QPU_S = 90 * 1.25


def alt5_token():
    for envp in ("/mnt/droid/repos/DC15E/.env", "/droid/repos/DC15E/.env"):
        if os.path.exists(envp):
            for line in open(envp):
                m = re.match(r"^IBMQ_ALT5=(.+)$", line.strip())
                if m:
                    return m.group(1).strip().strip('"').strip("'")
    sys.exit("REFUSE: IBMQ_ALT5 not found in DC15E .env")


def load_mod(path, name):
    s = importlib.util.spec_from_file_location(name, path)
    m = importlib.util.module_from_spec(s)
    try:
        s.loader.exec_module(m)
    except SystemExit:
        pass
    return m


def g_public_gate():
    """G-PUBLIC (door(a) flight-6 doctrine): the commitment must be on origin
    BEFORE submit. Refuses otherwise."""
    import subprocess

    def git(*a):
        return subprocess.run(["git", *a], capture_output=True, text=True, cwd=REPO)

    if git("status", "--porcelain", "--", COMMIT_FILE).stdout.strip():
        sys.exit(f"REFUSE G-PUBLIC: {COMMIT_FILE} uncommitted — commit+push the seal first.")
    committed = json.loads(git("show", f"HEAD:{COMMIT_FILE}").stdout).get("commitment_sha256")
    if committed != COMMITMENT:
        sys.exit(f"REFUSE G-PUBLIC: committed {str(committed)[:16]} != {COMMITMENT[:16]}.")
    git("fetch", "origin", "main", "-q")
    commit = git("log", "-1", "--format=%H", "--", COMMIT_FILE).stdout.strip()
    if git("merge-base", "--is-ancestor", commit, "origin/main").returncode != 0:
        sys.exit(f"REFUSE G-PUBLIC: seal commit {commit[:12]} not on origin — push before flying.")
    print(f"  [PASS] G-PUBLIC  seal commit {commit[:12]} public on origin (pre-flight)")


def build_sealed_rows(sec):
    """Walk the sealed labels; pop A_list for ALT, xu_list for NULL, in order.
    Emits exactly the dict shape kit.build_flight consumes (Whisper #12470)."""
    labels, A_list, xu_list = sec["labels"], sec["A_list"], sec["xu_list"]
    rows, ka, kn = [], 0, 0
    for ch in labels:
        if ch == "1":
            rows.append({"label": "ALT", "A": A_list[ka]}); ka += 1
        else:
            rows.append({"label": "NULL", "xu": list(xu_list[kn])}); kn += 1
    assert ka == len(A_list) and kn == len(xu_list), "seal list exhaustion mismatch"
    return rows


def main(fly):
    kit = load_mod(KIT_PATH, "kit")
    sealer = load_mod(SEALER_PATH, "h15sealer")
    import datetime as _dt
    print(f"H15 N1 positronic flight — n={kit.N}, {kit.M} graded + {kit.C} cal "
          f"= {kit.TOTAL} rows x 1 shot")
    print(f"  UTC {_dt.datetime.now(_dt.timezone.utc).isoformat()}\n")

    # G-KIT-HASH: the public circuits are the two-seat-verified frozen kit.
    kh = hashlib.sha256(open(KIT_PATH, "rb").read()).hexdigest()
    if not kh.startswith(KIT_SHA):
        sys.exit(f"REFUSE G-KIT-HASH: kit {kh[:16]} != verified {KIT_SHA}.")
    print(f"  [PASS] G-KIT-HASH kit {kh[:16]} (two-seat verified)")

    # G-SEAL: recompute the commitment from the stored secret via the SEALER's
    # frozen digest (never a guessed preimage).
    if not sealer.selftest():
        sys.exit("REFUSE: sealer selftest failed — cannot trust digest().")
    sec = json.load(open(SECRETS))[STORE_KEY]
    recomputed = sealer.digest(sec["labels"], sec["A_list"], sec["xu_list"], sec["salt"])
    if recomputed != COMMITMENT or sec.get("sha256") != COMMITMENT:
        sys.exit(f"REFUSE G-SEAL: recomputed {recomputed[:16]} != {COMMITMENT[:16]}.")
    print(f"  [PASS] G-SEAL    commitment {COMMITMENT[:16]} (frozen-preimage recompute)")

    # G-BAL: 316/316, and the seal carries per-trial secrets (not one A).
    n_alt = sec["labels"].count("1")
    if n_alt != kit.M // 2 or len(sec["A_list"]) != n_alt or len(sec["xu_list"]) != kit.M - n_alt:
        sys.exit(f"REFUSE G-BAL: {n_alt} ALT / A_list {len(sec['A_list'])} / xu {len(sec['xu_list'])}.")
    print(f"  [PASS] G-BAL     {n_alt} ALT / {kit.M - n_alt} NULL; {len(sec['A_list'])} distinct A + "
          f"{len(sec['xu_list'])} sealed xu (per-trial secret, not single-A)")

    # Build the sealed rows + the full 696-circuit flight from the public kit.
    sealed_rows = build_sealed_rows(sec)
    circs, rowmap = kit.build_flight(sealed_rows)
    assert len(circs) == kit.TOTAL, f"circuit count {len(circs)} != {kit.TOTAL}"
    print(f"  BUILT            {len(circs)} circuits (public schedule; zero pilot choice)")

    from qiskit import transpile
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
    svc = QiskitRuntimeService(channel="ibm_quantum_platform",
                               token=alt5_token(), instance=ALT5_CRN)
    u = svc.usage()
    crn, rem = u["instance_id"], u["usage_remaining_seconds"]
    if crn != ALT5_CRN or u["usage_limit_reached"]:
        sys.exit(f"REFUSE G-CRN: {crn[-24:]} flagged={u['usage_limit_reached']}")
    print(f"  [PASS] G-CRN     ...{crn[-24:]}  remaining {rem}s")

    # G-FIT with the MCM 3x already inside the estimate (conservative top-of-band).
    if _EST_QPU_S > rem:
        sys.exit(f"REFUSE G-FIT: est {_EST_QPU_S:.0f}s (MCM-3x, conservative) > {rem}s remaining.")
    print(f"  [PASS] G-FIT     est {_EST_QPU_S:.0f}s (MCM-3x, top-of-band x1.25) vs {rem}s")

    bk = svc.backend("ibm_marrakesh")
    tcircs = transpile(circs, backend=bk, optimization_level=1, seed_transpiler=SEED_TRANSPILE)

    # G-LAYOUT (safe-score doctrine): the worst 2q error on any USED coupling in
    # the transpiled batch must be <= SAFE_2Q. Reads live day-of calibration.
    try:
        tgt = bk.target
        worst = 0.0
        for tqc in tcircs[:8]:                # sample; layout is shared across the batch
            for inst in tqc.data:
                if inst.operation.num_qubits == 2:
                    qs = tuple(tqc.find_bit(q).index for q in inst.qubits)
                    props = tgt.get(inst.operation.name, {})
                    ip = props.get(qs) or props.get(tuple(reversed(qs)))
                    if ip and ip.error is not None:
                        worst = max(worst, ip.error)
        if worst > SAFE_2Q:
            sys.exit(f"REFUSE G-LAYOUT: worst 2q error {worst:.4f} > safe {SAFE_2Q} — reseed/relayout.")
        print(f"  [PASS] G-LAYOUT  worst used 2q error {worst:.4f} <= {SAFE_2Q}")
    except SystemExit:
        raise
    except Exception as e:
        print(f"  [WARN] G-LAYOUT could not read live 2q errors ({e}); "
              f"state the manual safe-score check on record before --fly.")

    rowmap_out = {"total": kit.TOTAL, "graded": kit.M, "cal": kit.C, "shots": 1,
                  "commitment_sha256": COMMITMENT, "kit_sha256": kh,
                  "schedule": rowmap, "threshold": 0.6040,
                  "n": kit.N, "seed_transpile": SEED_TRANSPILE}
    mp = "results/h15_n1_rowmap_ember.json"

    if not fly:
        print("\n  DRY — nothing submitted. Pass --fly to submit (after G-PUBLIC + fresh GO).")
        json.dump(rowmap_out, open(mp, "w"), indent=1)
        print(f"  row map (public) -> {mp}")
        return 0

    # G-PUBLIC is the LAST gate before spend.
    g_public_gate()

    # ONE submission, 696 distinct circuits each as its own PUB (no parametric
    # broadcast — each row is a different A/xu prep), one shot each = S=1.
    # Job-id announced by the caller AT submit (resubmit guard).
    job = SamplerV2(mode=bk).run(list(tcircs), shots=1)
    jid = job.job_id()
    print(f"\n  SUBMITTED  job {jid}")
    rowmap_out["job"] = jid
    rowmap_out["emitted_utc"] = _dt.datetime.now(_dt.timezone.utc).isoformat()
    json.dump(rowmap_out, open(mp, "w"), indent=1)
    print(f"  row map (public, with job) -> {mp}")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--fly", action="store_true")
    a = ap.parse_args()
    sys.exit(main(a.fly))
