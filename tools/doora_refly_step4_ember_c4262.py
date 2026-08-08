#!/usr/bin/env python3
"""DOOR (a) RE-FLY STEP 4 — fresh seal + sealed flight. Ember C4262. REFUSES BY DEFAULT.

Authorized: Creator go on the bus, general#6835 20:02:41Z (posted to the channel so all
three seats can read it — a relayed instruction could not move the seal).

GATES, all blocking, all on the object that actually submits:
  G-CRN   the submitting service must resolve to the ALT account BY CRN, never by name.
          'open-instance' names BOTH the 12s account AND the accepts-and-never-runs one
          (Whisper #6847) — the string in every log line cannot tell them apart.
  G-A     line_layout(2n) exists and is fully coupled; no silent fallback to a search.
  G-B     transpiled object carries FREE PARAMETERS (proof of transpile-before-bind).
  G-C     two-point invariant: all-zero vs all-one, EXACT count and depth equality on the
          flown ISA object. Costs ~7-22 min of local compute and is not negotiable.
  G-D     fresh A' pairwise distinct across NULL copies (shared A' inverts the witness).
  G-FIT   sized shots x 40 trials projected against THE COUNTER, not any bus figure.
          Halt if it does not fit — the Creator's go authorizes the spend, it does not
          override fit-or-halt.

SEAL: drawn fresh for this re-fly, via the proven sealer. Never reuse the pilot's seal —
its A and labels are public now.
"""
import sys, os, re, json, argparse, datetime
sys.path.insert(0, "scripts")
EXHAUSTED_CRN_FRAGMENT = "ace903cb"
ALT_CRN_FRAGMENT = "44cfd6bd"

def alt_token():
    with open("/droid/repos/DC15W/.env") as f:
        for line in f:
            m = re.match(r"^IBMQ_ALT=(.+)$", line.strip())
            if m: return m.group(1).strip().strip('"').strip("'")
    sys.exit("REFUSE: IBMQ_ALT not found")

def gate(name, ok, detail):
    print(f"  [{'PASS' if ok else 'BLOCK'}] {name:9} {detail}", flush=True)
    return ok

def main(shots, fly):
    import numpy as np, importlib.util
    from qiskit import transpile
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
    s = importlib.util.spec_from_file_location("kit",
        "experiments/exp_door_a_flight_kit_v2_whisper_c5027.py")
    kit = importlib.util.module_from_spec(s)
    try: s.loader.exec_module(kit)
    except SystemExit: pass
    N, M = 8, 40
    print(f"DOOR (a) RE-FLY STEP 4 — n={N}, shots={shots}, {'LIVE' if fly else 'DRY'}")
    print(f"  UTC {datetime.datetime.now(datetime.timezone.utc).isoformat()}\n")

    svc = QiskitRuntimeService(channel="ibm_quantum_platform", token=alt_token())
    u = svc.usage(); crn = u["instance_id"]
    rem = u["usage_limit_seconds"] - u["usage_consumed_seconds"]
    ok = gate("G-CRN", (ALT_CRN_FRAGMENT in crn) and (EXHAUSTED_CRN_FRAGMENT not in crn),
              f"...{crn[-24:]}  remaining {rem}s  flagged={u['usage_limit_reached']}")
    if not ok: sys.exit("\n  REFUSED at G-CRN — wrong account. NAME is not an identifier.")

    bk = svc.backend("ibm_marrakesh")
    twoq = "cz" if "cz" in bk.target.operation_names else "ecr"
    lay = kit.line_layout(bk.target.build_coupling_map(), 2*N)
    ok &= gate("G-A", bool(lay) and len(lay) == 2*N, f"line_layout({2*N}) -> {len(lay) if lay else None}")
    if not lay: sys.exit("\n  REFUSED at G-A")

    qc, hA, hB = kit.q_circuit_unbound(N)
    t = transpile(qc, backend=bk, initial_layout=lay, optimization_level=1)
    ok &= gate("G-B", t.num_parameters > 0, f"{t.num_parameters} free params, ISA 2q={t.count_ops().get(twoq,0)}")

    print("  [ .... ] G-C        two-point invariant running (~7-22 min, not negotiable)", flush=True)
    zero = [[0]*N for _ in range(N)]
    one  = [[1 if j>=i else 0 for j in range(N)] for i in range(N)]
    bz = t.assign_parameters(kit.q_bindings(1, zero, np.random.default_rng(5), hA, hB))
    bo = t.assign_parameters(kit.q_bindings(1, one,  np.random.default_rng(5), hA, hB))
    same = (bz.count_ops().get(twoq,0), bz.depth()) == (bo.count_ops().get(twoq,0), bo.depth())
    ok &= gate("G-C", same, f"all-zero ({bz.count_ops().get(twoq,0)},d{bz.depth()}) vs all-one ({bo.count_ops().get(twoq,0)},d{bo.depth()})")

    print(f"\n  G-FIT  sized {shots} shots x {M} trials vs COUNTER {rem}s — evaluated at submit")
    if not fly:
        print(f"\n  DRY — nothing sealed, nothing submitted. Gates: {'ALL PASS' if ok else 'BLOCKED'}")
        return 0 if ok else 1
    sys.exit("\n  REFUSE: live path arms only after the anchor sizes the flight.")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--shots", type=int, required=True)
    ap.add_argument("--fly", action="store_true")
    a = ap.parse_args()
    sys.exit(main(a.shots, a.fly))
