#!/usr/bin/env python3
"""Exp243 — MAGIC INJECTION: applying a non-Clifford gate by CONSUMING a magic state. C4922.

The magic-fold toward fault tolerance (Creator directive "fly the magic-fold"). Exp235 broke the
Clifford ceiling by applying a non-Clifford gate DIRECTLY (Rzz on the data) — which preserves [[4,2,2]]
but is non-transversal, and by Eastin-Knill is a DEAD END for fault tolerance (no code has a transversal
T). The ONLY known route to a fault-tolerant T is INJECTION: prepare a magic ancilla, then teleport its
gate onto the data via a transversal CNOT + logical measurement + a classical byproduct frame. This
flight flies that gadget on silicon, error-DETECTED — a different, more-advanced mechanism than 235,
composing the certified pieces (213's teleported-S gadget machinery, the [[4,2,2]] shield).

CONSTRUCTION (two [[4,2,2]] blocks, 8 qubits — 191/213-class depth, NO idle):
  A (data, q0-3) = |+bar> ;  B (magic ancilla, q4-7) = Rzz(theta)|+bar> = Rz_bar(theta)|+bar>
  transversal CNOT A->B (bitwise cx(i,i+4)) ; measure B in Z-bar (m = z4^z6) ; keep A, read X-bar.
  The gadget teleports Rz(theta) onto the data: A -> Rz(theta)|+bar> up to a Z-bar-plane byproduct.

WHY X-BAR (dodges the Y-bar wall, and is robust): Rz(theta)|+bar> has <X-bar> = cos(theta); a STABILIZER
state on |+bar> gives <X-bar> in {0,+-1}, so <X-bar> = 0.707 at theta=pi/4 IS the non-stabilizer (magic)
signature. The teleportation byproduct is an S-bar (Y-bar plane) — it does NOT change <X-bar> (both m=0
and m=1 branches give cos(theta)), so the magic witness needs no active correction (shown by the m-split
being flat). The byproduct frame matters only for the Y-bar component (the deterministic full state) —
that is 213's established software-frame mechanism, named here, not the object of this measurement.

FROZEN GATES (checked in selftest, statevector-exact; postselect XXXX_A & ZZZZ_B):
  G1_MAGIC_INJECTED: <X-bar_A>(theta=pi/4, gadget) in [0.55,0.85] — a non-stabilizer value strictly
     between the Clifford points {0,+-1}, injected into the data by consuming the magic ancilla.
  G2_GADGET_NECESSARY: <X-bar_A>(theta=pi/4, NO-CNOT) >= 0.9 (without the gadget the magic does NOT
     reach the data) AND the Clifford checkpoints land: theta=0 -> +1, pi/2 (S, Clifford) -> ~0,
     pi -> ~ -1 (the injected sweep is cos(theta); only the non-Clifford angle gives a magic value).
  Registered verdict = G1 and G2. REPORTED: full <X-bar>(theta) sweep; m=0 vs m=1 split (byproduct-
     robustness of the witness); acceptance (postselection rate, first-class).
SCOPE: error-DETECTED magic injection (the FT T-gadget mechanism), one [[4,2,2]] data block + one magic
  ancilla block, distance-2 (detect+postselect, cannot distill or correct). The CORRECTING-code and
  DISTILLATION versions (distance-3 magic, [[15,1,3]] 15-to-1) are depth-blocked on ibm_fez and named as
  the next-hardware ideal, NOT flown. Textbook gate-teleportation of T + [[4,2,2]]; contribution = the
  fault-tolerant T-gate GADGET on silicon (vs 235's non-transversal direct gate).
Usage: --selftest | --submit [--backend ibm_fez --shots 8000] | --decode
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
PI = np.pi
THETAS = (0.0, PI / 4, PI / 2, PI)          # identity, T (magic), S (Clifford), Z
LABELS = {0.0: "I", PI / 4: "T(magic)", PI / 2: "S(Cliff)", PI: "Z"}


def _prep_plus_bar(qc, base):
    qc.h(base); qc.cx(base, base + 1); qc.h(base + 2); qc.cx(base + 2, base + 3)   # |+bar> on L1


def circuit(theta, gadget):
    qc = QuantumCircuit(8, 8)
    _prep_plus_bar(qc, 0)                     # A (data) = |+bar>
    _prep_plus_bar(qc, 4)                     # B (magic ancilla) = |+bar> ...
    if theta != 0.0: qc.rzz(theta, 4, 6)      # ... then Rz_bar(theta) -> magic state Rz(theta)|+bar>
    qc.barrier()
    if gadget:
        for i in range(4): qc.cx(i, i + 4)    # transversal logical CNOT A->B (the injection)
    qc.barrier()
    for q in range(4): qc.h(q)                # A read in X (X-bar_A = x0^x1; XXXX_A postselect)
    for q in range(8): qc.measure(q, q)       # B read in Z (Z-bar_B = z4^z6 = m; ZZZZ_B postselect)
    return qc


def _analyze(counts):
    """Postselect XXXX_A & ZZZZ_B; return <X-bar_A> overall and split by m = z4^z6."""
    acc = 0; c = 0; cm = {0: 0.0, 1: 0.0}; nm = {0: 0, 1: 0}; tot = 0
    for s, n in counts.items():
        b = s.replace(" ", ""); v = [int(b[-1 - i]) for i in range(8)]
        tot += n
        pA = v[0] ^ v[1] ^ v[2] ^ v[3]        # XXXX_A (A measured in X)
        pB = v[4] ^ v[5] ^ v[6] ^ v[7]        # ZZZZ_B (B measured in Z)
        if pA or pB: continue
        acc += n
        xbar = 1 - 2 * (v[0] ^ v[1])          # X-bar1_A = X0X1
        c += xbar * n
        m = v[4] ^ v[6]                        # Z-bar1_B (gadget/Bell outcome)
        cm[m] += xbar * n; nm[m] += n
    return {"xbar": (c / acc if acc else 0.0), "acceptance": acc / tot,
            "xbar_m0": (cm[0] / nm[0] if nm[0] else 0.0), "xbar_m1": (cm[1] / nm[1] if nm[1] else 0.0)}


def selftest():
    from qiskit_aer import AerSimulator
    sim = AerSimulator(); shots = 40000
    print("Exp243 selftest | MAGIC INJECTION — teleport a non-Clifford gate by consuming a magic ancilla")
    print("  theta sweep, GADGET arm: <X-bar_A> should trace cos(theta); magic at pi/4")
    for th in THETAS:
        r = _analyze(sim.run(circuit(th, True), shots=shots).result().get_counts())
        print(f"    {LABELS[th]:>9} (theta={th:.3f}): <X-bar_A>={r['xbar']:+.3f} (ideal {np.cos(th):+.3f}) "
              f"| m0 {r['xbar_m0']:+.3f} m1 {r['xbar_m1']:+.3f} | acc {r['acceptance']:.2f}")
        assert abs(r["xbar"] - np.cos(th)) < 0.03, "gadget must inject Rz(theta): <X-bar>=cos(theta)"
        assert abs(r["xbar_m0"] - r["xbar_m1"]) < 0.05, "S-byproduct must NOT affect X-bar (both m equal)"
    rT = _analyze(sim.run(circuit(PI / 4, True), shots=shots).result().get_counts())
    rN = _analyze(sim.run(circuit(PI / 4, False), shots=shots).result().get_counts())
    print(f"  MAGIC (T): gadget <X-bar>={rT['xbar']:+.3f} (~0.707 non-stabilizer)  |  "
          f"NO-CNOT control <X-bar>={rN['xbar']:+.3f} (~+1, no injection)")
    assert 0.55 <= rT["xbar"] <= 0.85, "magic point must be non-stabilizer ~0.707"
    assert rN["xbar"] >= 0.9, "without the gadget CNOT the magic must NOT reach the data"
    print("SELFTEST PASS: the gadget teleports Rz(theta) onto the data (cos(theta) sweep), the pi/4 point "
          "is a non-stabilizer MAGIC value ~0.707 injected by consuming the ancilla, the S-byproduct is "
          "immaterial to X-bar (m-split flat), and NO injection happens without the gadget. Cleared to fly.")


def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    order = [("gadget", th) for th in THETAS] + [("nocx", PI / 4)]
    circuits = [transpile(circuit(th, arm == "gadget"), backend=backend, optimization_level=3,
                          seed_transpiler=0) for (arm, th) in order]
    n2s = [sum(1 for i in c.data if i.operation.num_qubits == 2) for c in circuits]
    print(f"  DEPTH CHECK: {len(circuits)} circuits, 2q {min(n2s)}-{max(n2s)} (two [[4,2,2]] blocks + transversal CNOT)")
    job = SamplerV2(mode=backend).run(circuits, shots=shots)
    out = os.path.join(HERE, "..", "results", "exp243_magic_injection_manifest.json")
    man = {"exp": 243, "slug": "magic_injection", "backend": backend_name, "shots": shots,
           "job_id": job.job_id(), "order": [[a, float(t)] for (a, t) in order],
           "prereg": {"G1_magic_injected": "<X-bar_A>(pi/4, gadget) in [0.55,0.85] (non-stabilizer, injected)",
                      "G2_gadget_necessary": "<X-bar_A>(pi/4, no-cnot) >= 0.9 AND Clifford checkpoints land (cos theta)",
                      "registered_verdict": "G1 and G2",
                      "reported": "cos(theta) sweep, m0/m1 split (byproduct-robust witness), acceptance",
                      "scope": "error-DETECTED magic injection = the FT T-gadget on silicon (vs 235 direct gate); "
                               "distance-2; correcting-code magic + distillation depth-blocked, named not flown"}}
    json.dump(man, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits, {shots} shots) -> {out}")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    man = json.load(open(os.path.join(HERE, "..", "results", "exp243_magic_injection_manifest.json")))
    svc = _get_ibm_service(); res = svc.job(man["job_id"]).result()
    def counts(idx):
        r0 = res[idx]; reg = list(r0.data.keys())[0]; return getattr(r0.data, reg).get_counts()
    print(f"Exp243 MAGIC INJECTION decode | job {man['job_id']}")
    rows = {}
    for idx, (arm, th) in enumerate(man["order"]):
        rows[(arm, round(th, 4))] = _analyze(counts(idx))
    print("  arm     theta       <X-bar_A>  (ideal cos)   m0 / m1        acceptance")
    for (arm, th) in [(a, round(t, 4)) for (a, t) in man["order"]]:
        r = rows[(arm, th)]; lab = LABELS.get(th if arm == "gadget" else -1, arm)
        tag = f"{arm}:{LABELS.get(th,'')}" if arm == "gadget" else "NO-CNOT ctrl"
        print(f"  {tag:>16}  {r['xbar']:+.3f}   ({np.cos(th):+.3f})   {r['xbar_m0']:+.3f}/{r['xbar_m1']:+.3f}   {r['acceptance']:.3f}")
    xT = rows[("gadget", round(PI / 4, 4))]["xbar"]; xN = rows[("nocx", round(PI / 4, 4))]["xbar"]
    xI = rows[("gadget", 0.0)]["xbar"]; xS = rows[("gadget", round(PI / 2, 4))]["xbar"]; xZ = rows[("gadget", round(PI, 4))]["xbar"]
    g1 = 0.55 <= xT <= 0.85
    cliff_ok = xI >= 0.85 and abs(xS) <= 0.2 and xZ <= -0.85
    g2 = xN >= 0.9 and cliff_ok
    print(f"\n  Clifford checkpoints: I={xI:+.3f} S={xS:+.3f} Z={xZ:+.3f}  (should be +1 / 0 / -1)")
    print(f"G1 MAGIC INJECTED: <X-bar>(T) = {xT:+.3f} in [0.55,0.85] {'OK' if g1 else 'MISS'} "
          f"(non-stabilizer: no Clifford injection can put |+bar> here)")
    print(f"G2 GADGET NECESSARY: no-cnot <X-bar> = {xN:+.3f} >= 0.9 & Clifford checkpoints land {'OK' if g2 else 'MISS'}")
    ok = g1 and g2
    win = ("MAGIC INJECTION — a non-Clifford gate applied by CONSUMING a magic ancilla and teleporting it "
           "onto the data (transversal CNOT + logical measurement), error-detected: the injected sweep "
           "traces cos(theta), the pi/4 point lands at a non-stabilizer ~0.707 that NO Clifford injection "
           "could reach, and nothing reaches the data without the gadget. The fault-tolerant T-gate "
           "mechanism on silicon — the route 235's direct gate (Eastin-Knill dead end) could not take")
    print(f"VERDICT: {win if ok else 'NOT HELD (accounting above)'}")
    json.dump({"job_id": man["job_id"], "rows": {f"{a}_{round(t,4)}": rows[(a, round(t, 4))] for (a, t) in man["order"]},
               "xbar_T": xT, "xbar_nocx": xN, "xbar_I": xI, "xbar_S": xS, "xbar_Z": xZ,
               "g1": bool(g1), "g2": bool(g2), "verdict_ok": bool(ok)},
              open(os.path.join(HERE, "..", "results", "exp243_magic_injection_decode.json"), "w"), indent=1)
    print("-> results/exp243_magic_injection_decode.json")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true"); ap.add_argument("--submit", action="store_true")
    ap.add_argument("--decode", action="store_true")
    ap.add_argument("--backend", default="ibm_fez"); ap.add_argument("--shots", type=int, default=8000)
    a = ap.parse_args()
    if a.selftest: selftest()
    elif a.submit: submit(a.backend, a.shots)
    elif a.decode: decode()
    else: ap.print_help()
