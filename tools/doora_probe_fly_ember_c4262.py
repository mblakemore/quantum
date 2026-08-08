#!/usr/bin/env python3
"""DOOR (a) PROBE FLIGHT — n=8, one sealed trial + K=32 public-A calibration rows.
Ember C4262. ARMED. Requires --fly.

RULED SEQUENCE (Elder 0148664, Whisper #6695 fix, sign-corrected):
    projected_remaining = JOB_OVERHEAD + 39 * (usage(probe) - JOB_OVERHEAD)
    gate: projected_remaining <= 50% of instance remaining
    JOB_OVERHEAD = 2s, MEASURED from a throwaway 1-qubit job (usage=2, confirmed
    seconds three ways: job.usage(), metrics quantum_seconds, and the instance
    counter moving 577 -> 579).

WHY THE NAIVE x39 WAS WRONG: a fixed per-JOB cost is paid ONCE, not forty times.
usage(probe) x 39 = 79-82s against an 11.5s gate would have REFUSED a flight that
costs 2.8-4.5s. An 18-28x error in the direction that stops a flight that fits.

BLINDNESS: the compiled circuit is NEVER written to disk. The manifest carries row
indices and outcome bits only. A is injected from the off-git seal at bind time and
never leaves this process.
"""
import sys, os, re, json, math, datetime, argparse
sys.path.insert(0, "scripts")

JOB_OVERHEAD_S = 2.0
N = 8
TRIALS_TOTAL = 40
SHOTS = 77
K_CAL = 32
SECRETS = os.path.expanduser("~/.ember-doora-secrets.json")

def alt_token():
    with open("/droid/repos/DC15W/.env") as f:
        for line in f:
            m = re.match(r"^IBMQ_ALT=(.+)$", line.strip())
            if m: return m.group(1).strip().strip('"').strip("'")
    sys.exit("REFUSE: IBMQ_ALT not found")

def main(fly):
    import numpy as np, importlib.util
    from qiskit import transpile
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
    s = importlib.util.spec_from_file_location("kit",
        "experiments/exp_door_a_flight_kit_v2_whisper_c5027.py")
    kit = importlib.util.module_from_spec(s)
    try: s.loader.exec_module(kit)
    except SystemExit: pass

    sec = json.load(open(SECRETS))[f"doora_deg2phase_v1:{N}"]
    bits, labels = sec["A_bits"], sec["labels"]
    A = [[0]*N for _ in range(N)]; k = 0
    for i in range(N):
        for j in range(i, N):
            A[i][j] = int(bits[k]); k += 1
    label1 = int(labels[0])          # trial 1's sealed label — used, never printed

    svc = QiskitRuntimeService(channel="ibm_quantum_platform", token=alt_token())
    bk = svc.backend("ibm_marrakesh")
    twoq = "cz" if "cz" in bk.target.operation_names else "ecr"
    cm = bk.target.build_coupling_map()
    lay = kit.line_layout(cm, 2*N)
    if not lay or len(lay) != 2*N: sys.exit("REFUSE G-A: no line layout")

    qc, hA, hB = kit.q_circuit_unbound(N)
    t = transpile(qc, backend=bk, initial_layout=lay, optimization_level=1)
    isa = t.count_ops().get(twoq, 0)
    if t.num_parameters == 0: sys.exit("REFUSE G-B: object has no free parameters")

    zero = [[0]*N for _ in range(N)]
    one  = [[1 if j>=i else 0 for j in range(N)] for i in range(N)]
    bz = t.assign_parameters(kit.q_bindings(1, zero, np.random.default_rng(5), hA, hB))
    bo = t.assign_parameters(kit.q_bindings(1, one,  np.random.default_rng(5), hA, hB))
    if (bz.count_ops().get(twoq,0), bz.depth()) != (bo.count_ops().get(twoq,0), bo.depth()):
        sys.exit("REFUSE G-C: two-point invariant FAILED — branch is distinguishable")
    print(f"  G-A/B/C PASS   ISA 2q={isa}  free params={t.num_parameters}  "
          f"two-point {bz.count_ops().get(twoq,0)}/d{bz.depth()} both branches")

    u = svc.usage(); rem = u["usage_limit_seconds"] - u["usage_consumed_seconds"]
    ceiling = rem * 0.5
    print(f"  instance: {u['usage_consumed_seconds']}/{u['usage_limit_seconds']}  "
          f"remaining {rem}s  ceiling(50%) {ceiling}s  flagged={u['usage_limit_reached']}")
    if u["usage_limit_reached"]: sys.exit("REFUSE: instance limit reached")

    rng = np.random.default_rng(int(sec["salt"][:8], 16) % (2**31))
    trial_binding = kit.q_bindings(label1, A, rng, hA, hB)
    # PUB SHAPE FIX: SamplerV2 takes (circuit, parameter_VALUES) where parameter_values is an
    # ARRAY — one ROW per binding. Calling assign_parameters K_CAL times builds K_CAL circuits
    # and is both slow (each call walks a 372-gate circuit) and the WRONG OBJECT: the whole
    # point is ONE compiled circuit with many bindings. Build the value array in the circuit's
    # own parameter order instead.
    order = list(t.parameters)
    def row(bd): return [float(bd[prm]) for prm in order]
    cal_rows = [row(kit.q_bindings(1, kit.random_A(N, np.random.default_rng(9000+i)),
                                   np.random.default_rng(8000+i), hA, hB)) for i in range(K_CAL)]
    param_array = [row(trial_binding)] + cal_rows
    print(f"  probe: 1 sealed trial ({SHOTS} shots) + {K_CAL} public-A calibration rows, ONE PUB")

    if not fly:
        print("\n  DRY — nothing submitted. Pass --fly to submit.")
        return 0

    t0 = datetime.datetime.now(datetime.timezone.utc)
    job = SamplerV2(mode=bk).run([(t, param_array, SHOTS)])
    print(f"\n  SUBMITTED  job {job.job_id()}  at {t0.isoformat()}")
    import time
    for i in range(40):
        st = str(job.status())
        if st in ("DONE","ERROR","CANCELLED"): break
        time.sleep(15)
    print(f"  status {job.status()}")
    if str(job.status()) != "DONE":
        sys.exit(f"  job did not complete: {job.status()}")
    used = job.usage()
    proj = JOB_OVERHEAD_S + (TRIALS_TOTAL-1) * (used - JOB_OVERHEAD_S)
    print(f"  usage(probe) = {used}s")
    print(f"  projected_remaining = {JOB_OVERHEAD_S} + 39*({used} - {JOB_OVERHEAD_S}) = {proj:.2f}s")
    print(f"  ceiling = {ceiling}s   ->  {'PASS — remaining 39 trials fit' if proj <= ceiling else 'STOP — projection exceeds ceiling'}")
    return 0

if __name__ == "__main__":
    ap = argparse.ArgumentParser(); ap.add_argument("--fly", action="store_true")
    sys.exit(main(ap.parse_args().fly))
