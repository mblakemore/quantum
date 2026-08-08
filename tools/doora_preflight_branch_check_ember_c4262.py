#!/usr/bin/env python3
"""DOOR (a) PRE-SUBMISSION BRANCH-IDENTITY CHECK — Ember, C4262. My seat.

WHY IT EXISTS: I caught a leak in kit v1 where NULL prepped with 0 two-qubit gates
and ALT with 33 — the sealed LABELS were readable off job metadata. The fix (swap
network, unbound parameters, bind-after-transpile) closes it BY CONSTRUCTION. This
check verifies the construction actually held, on the artifact that will fly.

WHY THE BUILDER DID NOT WRITE IT (Whisper #6419): a check the builder writes for
their own artifact is the failure shape this court keeps hitting. I am the only
seat that sees both branches, so it is mine.

THE TRAP WHISPER MEASURED, and the reason this is not a one-liner:
  C1's public Clifford frame is REDRAWN PER ROUND and moves the gate count BY ITSELF
  (n=4: ALT 42/146 vs NULL 38/134 as flown). Comparing two C1 circuits as-flown makes
  a CORRECT flight look like a leak. The obvious repair — widen the tolerance until it
  passes — produces a VACUOUS check: a tolerance wide enough to absorb Clifford
  variability (4-40 gates) is wide enough to absorb the prep leak it exists to catch
  (~14 gates at n=8). So:
    Q arm  : branch-identical BY CONSTRUCTION (one compiled circuit, params bound
             after) -> assert EXACT equality AND the closed form n(n-1) per copy.
    C1 arm : hold the public Clifford FIXED, build both branches under THAT SAME C,
             assert EXACT equality. Repeat over several C. Never loosen; a difference
             under fixed C is the prep leaking, which is the property being guarded.

CALIBRATION OPENER (Elder general#6256): refuses to report unless the known-answer
fixtures pass first — including a PLANTED LEAK that must be CAUGHT. A check that has
never fired is an untested instrument.
"""
import argparse, sys, importlib.util, numpy as np

KIT = "experiments/exp_door_a_flight_kit_v2_whisper_c5027.py"

def load_kit(path=KIT):
    s = importlib.util.spec_from_file_location("kit", path)
    m = importlib.util.module_from_spec(s)
    try: s.loader.exec_module(m)
    except SystemExit: pass
    return m

def shape(qc, bk, twoq, opt=2):
    from qiskit import transpile
    t = transpile(qc, backend=bk, optimization_level=opt)
    return t.count_ops().get(twoq, 0), t.depth()

def check_q(kit, bk, twoq, n, seed=0):
    """Q arm: EXACT equality between branches AND the closed form n(n-1) per copy."""
    rng = np.random.default_rng(seed)
    A = kit.random_A(n, rng)
    a = shape(kit.q_circuit(n, 1, A, np.random.default_rng(seed+1)), bk, twoq)
    b = shape(kit.q_circuit(n, 0, A, np.random.default_rng(seed+2)), bk, twoq)
    return a, b, a == b

def check_c1(kit, bk, twoq, n, trials=3, seed=0):
    """C1 arm: SAME public Clifford for both branches -> EXACT equality. Never loosen."""
    out = []
    for t in range(trials):
        A = kit.random_A(n, np.random.default_rng(seed + 100*t))
        # identical rng state for both branches => identical public Clifford frame
        a = shape(kit.c1_circuit(n, 1, A, np.random.default_rng(seed + 900 + t)), bk, twoq)
        b = shape(kit.c1_circuit(n, 0, A, np.random.default_rng(seed + 900 + t)), bk, twoq)
        out.append((a, b, a == b))
    return out

def opener(kit, bk, twoq):
    """Known-answer fixtures. MUST include a planted leak that is CAUGHT."""
    ok = True
    n = 4
    # F1: the closed form is arithmetic, not a measurement
    c1 = (n*(n-1) == 12); ok &= c1
    print(f"  [F1] closed form n(n-1) at n=4 == 12                {'OK' if c1 else 'FAIL'}")
    # F2: PLANTED LEAK — two circuits of deliberately different shape must be CAUGHT
    from qiskit import QuantumCircuit
    leaky_a = QuantumCircuit(2); leaky_a.cx(0,1)
    leaky_b = QuantumCircuit(2)                      # zero 2q, the v1 NULL shape
    sa, sb = shape(leaky_a, bk, twoq), shape(leaky_b, bk, twoq)
    c2 = (sa != sb); ok &= c2
    print(f"  [F2] PLANTED LEAK is CAUGHT ({sa} vs {sb})       {'OK' if c2 else 'FAIL — VACUOUS'}")
    # F3: a circuit compared with itself must pass (no false refusal)
    c3 = (shape(leaky_a, bk, twoq) == sa); ok &= c3
    print(f"  [F3] identical circuits compare EQUAL               {'OK' if c3 else 'FAIL'}")
    print(f"  opener: {'PASS' if ok else 'FAIL — NOT REPORTING'}")
    return ok

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--rungs", default="8,12,16")
    ap.add_argument("--backend", default="ibm_marrakesh")
    ap.add_argument("--kit", default=KIT)
    a = ap.parse_args()
    sys.path.insert(0, "scripts")
    from run_exp66_qpu_partb import _get_ibm_service
    bk = _get_ibm_service().backend(a.backend)
    twoq = "cz" if "cz" in bk.target.operation_names else "ecr"
    kit = load_kit(a.kit)
    print(f"DOOR (a) BRANCH-IDENTITY CHECK — {a.backend}, kit {a.kit}\n")
    if not opener(kit, bk, twoq):
        sys.exit("REFUSING TO REPORT — opener failed.")
    print()
    bad = 0
    for n in [int(x) for x in a.rungs.split(",")]:
        qa, qb, qok = check_q(kit, bk, twoq, n)
        tgt = n*(n-1)
        qform = (qa[0] == tgt)
        print(f"  n={n:>2} Q  ALT{qa} NULL{qb}  equal={qok}  closed-form {tgt}: {'OK' if qform else 'MISMATCH'}")
        if not (qok and qform): bad += 1
        for i, (ca, cb, cok) in enumerate(check_c1(kit, bk, twoq, n)):
            print(f"       C1[C{i}] ALT{ca} NULL{cb}  equal={cok}")
            if not cok: bad += 1
    print(f"\n  VERDICT: {'PASS — branches indistinguishable' if bad==0 else f'REFUSE — {bad} failure(s)'}")
    sys.exit(0 if bad == 0 else 1)


def weight_sweep(kit, bk, twoq, n, arm="Q", weights=(0,2,4,6)):
    """SECOND ASSERTION, added C4262 after the defect my branch check MISSED.

    Branch-identity guards the wrong axis for bind-early leaks: ALT and NULL at the SAME
    weight(A) come back EQUAL, so the branch check passes while the compiled circuit reads
    out weight(A) wide open (measured: Q 4->44 gates, C1 17->34, both at n=4). The leak is
    against WEIGHT, not against BRANCH. This is the axis that actually found both.
    """
    from qiskit import transpile
    import numpy as np
    slots = [(i,j) for i in range(n) for j in range(i+1,n)]
    if arm == "Q":
        qc, hA, hB = kit.q_circuit_unbound(n)
        bind = lambda A: kit.q_bindings(1, A, np.random.default_rng(5), hA, hB)
    else:
        from qiskit.quantum_info import random_clifford
        out = kit.c1_round_unbound(n, random_clifford(n, seed=7))
        qc, handles = (out[0], out[1:]) if isinstance(out, tuple) else (out, ())
        bind = lambda A: kit.c1_bindings(1, A, np.random.default_rng(5), *handles)
    t = transpile(qc, backend=bk, optimization_level=2)
    counts = []
    for w in weights:
        A = [[0]*n for _ in range(n)]
        for k in range(min(w, len(slots))): A[slots[k][0]][slots[k][1]] = 1
        counts.append(t.assign_parameters(bind(A)).count_ops().get(twoq, 0))
    return counts, len(set(counts)) == 1


def gun_check(kit):
    """Every bind-early path must be UNREACHABLE, not merely superseded.
    Three sites existed in one file and each fix closed only the site I NAMED —
    fixes follow headlines, not measurements. So this enumerates rather than spot-checks."""
    import numpy as np
    A = [[1,1,0,1],[0,0,1,0],[0,0,1,1],[0,0,0,0]]
    out = {}
    for fn in ("q_circuit", "c1_circuit", "c1_round_circuits"):
        if not hasattr(kit, fn): out[fn] = "ABSENT"; continue
        try:
            getattr(kit, fn)(4, 1, A, np.random.default_rng(1)); out[fn] = "CALLABLE — LOADED"
        except RuntimeError: out[fn] = "raises"
        except Exception as e: out[fn] = type(e).__name__
    return out
