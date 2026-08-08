#!/usr/bin/env python3
"""Door (a) MAIN FLIGHT — 40 sealed trials at 316 shots, on WhisperPaid. C4262 (Ember).

A minimal, faithful adaptation of tools/doora_probe_fly_ember_c4262.py, which flew the
21:44 probe successfully. Deliberately NOT a rewrite: this runs against a live paid
account (real dollars), so the parts that worked are copied rather than improved.

DIFFERENCES FROM THE PROBE, each one intentional:
  1. Account: IBMQ_TOKEN from Whisper's .env (Creator authorisation general#6987) and the
     WhisperPaid CRN passed EXPLICITLY. This key sees THREE instances, so neither a name
     nor a substring is an identifier, and default resolution would trust ordering.
     Refuses on usage_limit_reached — the 738s open-instance is flagged and is the
     accepts-but-never-runs account.
  2. All 40 sealed labels are flown (the probe flew trial 1 only + 32 public-A rows).
  3. The flown-object two-point bind is GONE — retired as a blocking gate by Elder
     (quantum@82ac799) after it was shown tautological: assign_parameters substitutes into
     gates that already exist and runs no passes, so the count is fixed at transpile before
     any value exists. Replaced by G-C'lib, the same check on a small object, ~0s.
  4. G-FIT is evaluated against the same-family estimate (17.1s at pure linear x1.25)
     rather than the probe's 50%-of-remaining ceiling, which was written for a 6s tank.

BLINDNESS, unchanged from the probe: the compiled circuit is NEVER written to disk. A is
injected from the off-git seal at bind time and never leaves this process. The manifest
carries row indices only — no labels, no A.
"""
import sys, os, re, json, datetime, argparse
sys.path.insert(0, "scripts")

N = 8
TRIALS_TOTAL = 40
SHOTS = 316
SECRETS = os.path.expanduser("~/.ember-doora-secrets.json")
SEAL_KEY = f"doora_deg2phase_v1:{N}"
PAID_CRN = ("crn:v1:bluemix:public:quantum-computing:us-east:"
            "a/65155eedeb8b464eadf55d101fb3c931:27609585-d5b2-43cb-808d-2d47aeb87c05::")
EXPECTED_COMMITMENT = "ff43996c11405f17dae2b9ba9ad5eee210c27109553abc8b99ec5613f88b5622"
EST_S = 17.1          # 12,640 samples x 1.08s/1k x 1.25 safety, same-family reference


def paid_token():
    with open("/droid/repos/DC15W/.env") as f:
        for line in f:
            m = re.match(r"^IBMQ_TOKEN=(.+)$", line.strip())
            if m:
                return m.group(1).strip().strip('"').strip("'")
    sys.exit("REFUSE: IBMQ_TOKEN not found")


def main(fly):
    import numpy as np, importlib.util
    from qiskit import transpile
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
    s = importlib.util.spec_from_file_location(
        "kit", "experiments/exp_door_a_flight_kit_v2_whisper_c5027.py")
    kit = importlib.util.module_from_spec(s)
    try:
        s.loader.exec_module(kit)
    except SystemExit:
        pass

    print(f"DOOR (a) MAIN FLIGHT — n={N}, {TRIALS_TOTAL} trials x {SHOTS} shots, "
          f"{TRIALS_TOTAL*SHOTS:,} samples")
    print(f"  UTC {datetime.datetime.now(datetime.timezone.utc).isoformat()}\n")

    # ---- the seal. Assert it is the one published at general#6998 BEFORE anything flies.
    sec = json.load(open(SECRETS))[SEAL_KEY]
    if sec["sha256"] != EXPECTED_COMMITMENT:
        sys.exit(f"REFUSE G-SEAL: secret commitment {sec['sha256'][:16]} != published "
                 f"{EXPECTED_COMMITMENT[:16]}. Flying a different A than the one committed "
                 f"in git would make the blind claim false.")
    print(f"  [PASS] G-SEAL    commitment {sec['sha256'][:16]}... matches the published seal")
    bits, labels = sec["A_bits"], sec["labels"]
    if len(labels) < TRIALS_TOTAL:
        sys.exit(f"REFUSE: seal carries {len(labels)} labels, need {TRIALS_TOTAL}")
    A = [[0]*N for _ in range(N)]
    k = 0
    for i in range(N):
        for j in range(i, N):
            A[i][j] = int(bits[k]); k += 1

    # ---- account identity BEFORE any spend
    svc = QiskitRuntimeService(channel="ibm_quantum_platform", token=paid_token(),
                               instance=PAID_CRN)
    u = svc.usage()
    crn, rem = u["instance_id"], u["usage_remaining_seconds"]
    if crn != PAID_CRN or u["usage_limit_reached"]:
        sys.exit(f"REFUSE G-CRN: crn/flag mismatch — {crn[-24:]} flagged={u['usage_limit_reached']}")
    print(f"  [PASS] G-CRN     ...{crn[-24:]}  {u['usage_consumed_seconds']}/"
          f"{u['usage_limit_seconds']}  remaining {rem}s  flagged=False")

    bk = svc.backend("ibm_marrakesh")
    twoq = "cz" if "cz" in bk.target.operation_names else "ecr"
    lay = kit.line_layout(bk.target.build_coupling_map(), 2*N)
    if not lay or len(lay) != 2*N:
        sys.exit("REFUSE G-A: no line layout")
    print(f"  [PASS] G-A       line_layout({2*N}) -> {len(lay)}")

    qc, hA, hB = kit.q_circuit_unbound(N)
    t = transpile(qc, backend=bk, initial_layout=lay, optimization_level=1)
    if t.num_parameters == 0:
        sys.exit("REFUSE G-B: object has no free parameters — bound-then-transpiled")
    print(f"  [PASS] G-B       {t.num_parameters} free params, ISA 2q={t.count_ops().get(twoq,0)}")

    # ---- G-C'lib: the library's substitute-only behaviour, small object, this process.
    from qiskit.circuit import Parameter as _P
    from qiskit import QuantumCircuit as _QC
    _ps = [_P(f"x{i}") for i in range(4)]
    _qc = _QC(3)
    for _i, _p in enumerate(_ps[:2]):
        _qc.cp(_p, _i, _i+1)
    for _i, _p in enumerate(_ps[2:]):
        _qc.rz(_p, _i)
    _t = transpile(_qc, backend=bk, initial_layout=[0, 1, 2], optimization_level=3)
    _b = _t.count_ops().get(twoq, 0)
    _z = _t.assign_parameters({q: 0.0 for q in _ps}).count_ops().get(twoq, 0)
    _o = _t.assign_parameters({q: 3.14159 for q in _ps}).count_ops().get(twoq, 0)
    if not (_b == _z == _o):
        sys.exit(f"REFUSE G-C'lib: substitution changed gate count {_b}/{_z}/{_o}")
    print(f"  [PASS] G-C'lib   small-object substitute-only: {_b}/{_z}/{_o}")

    # ---- G-FIT against the measured balance
    if EST_S > rem:
        sys.exit(f"REFUSE G-FIT: estimate {EST_S}s exceeds remaining {rem}s")
    print(f"  [PASS] G-FIT     est {EST_S}s (pure-linear x1.25) vs {rem}s remaining, "
          f"slack {rem-EST_S:.1f}s")

    # ---- bind. One compiled circuit, TRIALS_TOTAL rows, in the circuit's parameter order.
    order = list(t.parameters)
    def row(bd):
        return [float(bd[prm]) for prm in order]
    rng_salt = int(sec["salt"][:8], 16)
    param_array = [row(kit.q_bindings(int(labels[i]), A,
                                      np.random.default_rng(rng_salt + i), hA, hB))
                   for i in range(TRIALS_TOTAL)]
    print(f"\n  PUB: 1 circuit x {len(param_array)} sealed rows x {SHOTS} shots "
          f"= {len(param_array)*SHOTS:,} samples")

    if not fly:
        print("\n  DRY — nothing submitted. Pass --fly to submit.")
        return 0

    job = SamplerV2(mode=bk).run([(t, param_array, SHOTS)])
    jid = job.job_id()
    print(f"\n  SUBMITTED  job {jid}")
    meta = {
        "spec": "doora_deg2phase_v1", "n": N, "M": TRIALS_TOTAL, "shots_per_trial": SHOTS,
        "samples": TRIALS_TOTAL*SHOTS, "backend": "ibm_marrakesh", "instance": "WhisperPaid",
        "commitment_sha256": sec["sha256"], "job": jid,
        "row_index_map": "row i (0-based) = sealed trial i+1",
        "tau_Q_registered": 0.562976, "registered_at": "general#6969 (whisper), BEFORE seal",
        "emitted_utc": datetime.datetime.now(datetime.timezone.utc).isoformat(),
        "contract": "v2_raw_bitstrings; grader reads counts from job_id",
    }
    os.makedirs("results", exist_ok=True)
    # ── C4262: RESULTS ARTIFACTS ARE APPEND-ONLY UNTIL SUCCESS (Elder, shared file) ──────
    # This wrote the CANONICAL manifest here, at submission, before knowing whether the job
    # completes — the exact defect that let a void exp142 flight destroy the pointer to a
    # COMPLETED 07-24 arm tonight. My own graded 29/40 manifest sat under the same hazard: one
    # failed re-fly would have overwritten it.
    #
    # Two-stage instead. The RUN-SCOPED file is keyed by job_id so it can never collide or
    # clobber, and it is written immediately so a process death is still recoverable. The
    # CANONICAL pointer is written ONLY after the job reports DONE, below.
    run_path = f"results/doora_mainfly_n8_{jid}.json"
    with open(run_path, "w") as f:
        json.dump(meta, f, indent=2)
    print(f"  run manifest -> {run_path} (no labels, no A; canonical written only on DONE)")

    import time
    for _ in range(60):
        if str(job.status()) in ("DONE", "ERROR", "CANCELLED"):
            break
        time.sleep(15)
    st = str(job.status())
    print(f"  status {st}")
    if st == "DONE":
        # canonical pointer updated ONLY now that the run verifiably succeeded
        with open("results/doora_mainfly_n8_ember_c4262.json", "w") as f:
            json.dump(meta, f, indent=2)
        print("  canonical -> results/doora_mainfly_n8_ember_c4262.json (run DONE)")
        used = job.usage()
        after = svc.usage()
        print(f"  BILLED {used}s   (estimate was {EST_S}s)")
        print(f"  balance {after['usage_consumed_seconds']}/{after['usage_limit_seconds']} "
              f"remaining {after['usage_remaining_seconds']}s")
    return 0


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--fly", action="store_true")
    sys.exit(main(ap.parse_args().fly))
