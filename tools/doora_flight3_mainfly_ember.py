#!/usr/bin/env python3
"""DOOR (a) FLIGHT-3 binder (Ember) — the pure-Q WIN test with tau_Q traveling
IN the job. Delta on the flight-2 binder (doora_mainfly_ember_c4262):

  * commitment  ff43996c -> d889caa5  (fresh balanced n=8 M=40 seal)
  * account     WhisperPaid PAID_CRN -> free ALT5 (IBMQ_ALT5)
  * IN-JOB CAL  ADD K=658 public-A calibration rows (kit builder, seeds
                30000+i, i=0..657) INTERLEAVED with the 40 sealed trials in
                ONE PUB — the mechanical heart of flight-3 (both prior
                flights died on anchor-vs-science epoch drift; interleaving
                makes f_cal an unbiased estimate of the conditions the SEALED
                rows actually saw). Elder ruling general#12194.
  * ROW MAP     sealed row j (j=0..39) at PUB position floor((j+0.5)*698/40);
                cal rows fill the remaining positions in seed order. Public,
                deterministic, ships in the flight record; tau_Q = grade-time
                only (grader pools f_cal over the map's cal positions).

Blind protocol: the SECRET (sealed A + labels) touches only this seat at
bind time. Cal rows are DETERMINISTIC-PUBLIC (q_bindings label=1 ignores the
rng), so Whisper re-derives them byte-identical pre-submit as the two-seat
verification that replaces a handoff (Elder general#12191).

SHOTS is the û-re-quoted per-trial count (Elder clause #6633) — passed in via
--shots from Whisper's pre-flight λ read; the G-FIT gate refuses if the total
exceeds the live tank. NO fixed 316.
"""
import sys, os, re, json, hashlib, datetime, argparse
import numpy as np

N = 8
TRIALS_TOTAL = 40
K_CAL = 32          # amendment 3 (Elder): 658 SAMPLES/316 shots = 32 ROWS; floor-32 for A-diversity
CAL_SEED_BASE = 30000
TOTAL_ROWS = TRIALS_TOTAL + K_CAL          # 698
SECRETS = os.path.expanduser("~/.ember-doora-secrets.json")
SEAL_KEY = f"doora_deg2phase_v1:{N}"
EXPECTED_COMMITMENT = "d889caa59800c9788eb940743acefa525aa826c0173865f010b58570b7a7566f"
ALT5_CRN = ("crn:v1:bluemix:public:quantum-computing:us-east:"
            "a/7044ec3a6d9149138a144e3e3487c4bb:"
            "22647176-d5b2-4692-b224-84a0b3c637f0::")
KIT_PATH = "experiments/exp_door_a_flight_kit_v2_whisper_c5027.py"
# refly reference: 12,640 samples in ~17.1s -> per-sample seconds, x1.25 safety
_S_PER_SAMPLE = 17.1 / 12640 * 1.25


def alt5_token():
    for envp in ("/mnt/droid/repos/DC15E/.env", "/droid/repos/DC15E/.env"):
        if os.path.exists(envp):
            for line in open(envp):
                m = re.match(r"^IBMQ_ALT5=(.+)$", line.strip())
                if m:
                    return m.group(1).strip().strip('"').strip("'")
    sys.exit("REFUSE: IBMQ_ALT5 not found in DC15E .env")


def interleave_positions():
    """Sealed row j -> position floor((j+0.5)*TOTAL/40); cal rows fill the
    rest in seed order. Deterministic, public, no label dependence."""
    sealed_pos = {}
    taken = set()
    for j in range(TRIALS_TOTAL):
        p = int((j + 0.5) * TOTAL_ROWS / TRIALS_TOTAL)
        while p in taken:                 # collision guard (dense-packing safety)
            p += 1
        sealed_pos[j] = p
        taken.add(p)
    cal_positions = [p for p in range(TOTAL_ROWS) if p not in taken]
    assert len(cal_positions) == K_CAL, f"cal slot count {len(cal_positions)} != {K_CAL}"
    return sealed_pos, cal_positions


def build_cal_param_rows(kit, order, hA, hB):
    """The 658 public-A calibration rows, seed order. label=1 so q_bindings
    ignores the rng (verified against the kit) — fully determined by the
    seed. Returns (rows, sha256_of_block)."""
    mats, rows = [], []
    for i in range(K_CAL):
        A_pub = kit.random_A(N, np.random.default_rng(CAL_SEED_BASE + i))
        mats.append(A_pub)
        bd = kit.q_bindings(1, A_pub, np.random.default_rng(0), hA, hB)
        rows.append([float(bd[p]) for p in order])
    # cross-check hash = the A MATRICES (Whisper's convention, general#12196),
    # compact-JSON seed order — the two-seat byte-identical verification.
    mat_hash = hashlib.sha256(
        json.dumps(mats, separators=(",", ":")).encode()).hexdigest()
    return rows, mat_hash


def main(shots, fly, hash_only):
    from qiskit import transpile
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
    import importlib.util
    s = importlib.util.spec_from_file_location("kit", KIT_PATH)
    kit = importlib.util.module_from_spec(s)
    try:
        s.loader.exec_module(kit)
    except SystemExit:
        pass

    print(f"DOOR (a) FLIGHT-3 — n={N}, {TRIALS_TOTAL} sealed + {K_CAL} cal "
          f"= {TOTAL_ROWS} rows x {shots} shots = {TOTAL_ROWS*shots:,} samples")
    print(f"  UTC {datetime.datetime.now(datetime.timezone.utc).isoformat()}\n")

    # ---- G-SEAL: the fresh balanced commitment
    sec = json.load(open(SECRETS))[SEAL_KEY]
    if sec["sha256"] != EXPECTED_COMMITMENT:
        sys.exit(f"REFUSE G-SEAL: {sec['sha256'][:16]} != {EXPECTED_COMMITMENT[:16]}")
    print(f"  [PASS] G-SEAL    commitment {sec['sha256'][:16]}... (fresh balanced seal)")
    bits, labels = sec["A_bits"], sec["labels"]
    if len(labels) < TRIALS_TOTAL:
        sys.exit(f"REFUSE: seal carries {len(labels)} labels, need {TRIALS_TOTAL}")
    if labels[:TRIALS_TOTAL].count("1") != TRIALS_TOTAL // 2:
        sys.exit(f"REFUSE G-BAL: labels not balanced 20/20 (got "
                 f"{labels[:TRIALS_TOTAL].count('1')} ones)")
    print(f"  [PASS] G-BAL     labels balanced {labels[:TRIALS_TOTAL].count('1')}/20 ones")
    A = [[0] * N for _ in range(N)]
    k = 0
    for i in range(N):
        for j in range(i, N):
            A[i][j] = int(bits[k]); k += 1

    # ---- transpiled ISA object (needs the backend; account first)
    svc = QiskitRuntimeService(channel="ibm_quantum_platform",
                               token=alt5_token(), instance=ALT5_CRN)
    u = svc.usage()
    crn, rem = u["instance_id"], u["usage_remaining_seconds"]
    if crn != ALT5_CRN or u["usage_limit_reached"]:
        sys.exit(f"REFUSE G-CRN: {crn[-24:]} flagged={u['usage_limit_reached']}")
    print(f"  [PASS] G-CRN     ...{crn[-24:]}  remaining {rem}s")
    bk = svc.backend("ibm_marrakesh")
    lay = kit.line_layout(bk.target.build_coupling_map(), 2 * N)
    if not lay or len(lay) != 2 * N:
        sys.exit("REFUSE G-A: no line layout")
    qc, hA, hB = kit.q_circuit_unbound(N)
    t = transpile(qc, backend=bk, initial_layout=lay, optimization_level=1)
    if t.num_parameters == 0:
        sys.exit("REFUSE G-B: bound-then-transpiled (no free params)")
    order = list(t.parameters)
    print(f"  [PASS] G-A/B     line_layout({2*N}), {t.num_parameters} free params")

    # ---- CAL block (public, deterministic) + its hash for Whisper's re-derive
    cal_rows, cal_hash = build_cal_param_rows(kit, order, hA, hB)
    print(f"  CAL BLOCK        {K_CAL} public-A rows, seeds {CAL_SEED_BASE}.."
          f"{CAL_SEED_BASE+K_CAL-1}  sha256 {cal_hash}")
    if hash_only:
        print("\n  --hash-only: cal block hashed, nothing bound or flown.")
        print(f"  CAL_BLOCK_SHA256={cal_hash}")
        return 0

    # ---- SEALED rows (secret-touch, this seat only)
    rng_salt = int(sec["salt"][:8], 16)
    sealed_rows = []
    for j in range(TRIALS_TOTAL):
        bd = kit.q_bindings(int(labels[j]), A,
                            np.random.default_rng(rng_salt + j), hA, hB)
        sealed_rows.append([float(bd[p]) for p in order])

    # ---- INTERLEAVE per Elder's fixed pattern
    sealed_pos, cal_positions = interleave_positions()
    param_array = [None] * TOTAL_ROWS
    for j, p in sealed_pos.items():
        param_array[p] = sealed_rows[j]
    for idx, p in enumerate(cal_positions):
        param_array[p] = cal_rows[idx]
    assert all(r is not None for r in param_array), "gap in interleave"

    # PUBLIC row map (positions only, no hypothesis) for the grader
    row_map = {"total_rows": TOTAL_ROWS, "shots": shots,
               "cal_positions": cal_positions,
               "cal_seed_of_position": {str(cal_positions[i]): CAL_SEED_BASE + i
                                        for i in range(K_CAL)},
               "sealed_positions": {str(sealed_pos[j]): f"sealed_trial_{j}"
                                    for j in range(TRIALS_TOTAL)},
               "cal_block_sha256": cal_hash,
               "pattern": "sealed j at floor((j+0.5)*698/40); cal fill rest seed-order",
               "commitment_sha256": sec["sha256"], "n": N}

    # ---- G-FIT against the live tank (û-re-quoted shots)
    est_s = TOTAL_ROWS * shots * _S_PER_SAMPLE
    if est_s > rem:
        sys.exit(f"REFUSE G-FIT: est {est_s:.1f}s > remaining {rem}s "
                 f"(shots={shots}; max fits ~{int(rem/(TOTAL_ROWS*_S_PER_SAMPLE))})")
    print(f"  [PASS] G-FIT     est {est_s:.1f}s (x1.25) vs {rem}s remaining")
    print(f"  INTERLEAVE       {TOTAL_ROWS} rows woven; map -> flight record")

    if not fly:
        print("\n  DRY — nothing submitted. Pass --fly to submit.")
        mp = "results/doora_flight3_rowmap_ember.json"
        json.dump(row_map, open(mp, "w"), indent=1)
        print(f"  row map (public) -> {mp}")
        print(f"  CAL_BLOCK_SHA256={cal_hash}")
        return 0

    job = SamplerV2(mode=bk).run([(t, param_array, shots)])
    jid = job.job_id()
    print(f"\n  SUBMITTED  job {jid}")
    row_map["job"] = jid
    row_map["emitted_utc"] = datetime.datetime.now(datetime.timezone.utc).isoformat()
    json.dump(row_map, open("results/doora_flight3_rowmap_ember.json", "w"), indent=1)
    print("  row map (public, with job) -> results/doora_flight3_rowmap_ember.json")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--shots", type=int, required=True,
                    help="û-re-quoted per-trial shots (Whisper's λ read); no fixed default")
    ap.add_argument("--hash-only", action="store_true",
                    help="build+hash the cal block only (for Whisper's pre-submit re-derive)")
    ap.add_argument("--fly", action="store_true")
    a = ap.parse_args()
    sys.exit(main(a.shots, a.fly, a.hash_only))
