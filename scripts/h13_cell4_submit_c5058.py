#!/usr/bin/env python3
"""H13 Cell 4 — THE HINDSIGHT METER — SUBMIT.  Whisper C5058, Creator GO ("fly whatever else you can with the 91").

Retrodiction beats prediction by a computable margin: guess a mid-circuit outcome from the past
alone (foresight) vs from past+future (hindsight). Law-match genre — NO advantage claim.
ZERO 2q GATES BY CONSTRUCTION, which is why this cell is flyable where 6+6b was not: tonight's
NO-TEST traced to 21 transpiled 2q gates per segment on a topology (heavy-hex) that offers no
denser layout. A circuit with no entangling gates cannot hit that wall.
Usage: QPU_ACCOUNT_VAR=IBMQ_ALT3 python3 scripts/h13_cell4_submit_c5058.py [--dry-run]
"""
import json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.pop("QISKIT_IBM_INSTANCE", None)
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile

ANGLES = (0, 15, 30, 45, 60, 75, 90)
SHOTS = 4000
EST_COST_S = 25.0
PREREG = "docs/h13-cell4-hindsight-prereg-FROZEN-whisper-c5058.md"

def circ(theta_deg, with_mid=True):
    q = QuantumRegister(1, "q"); c = ClassicalRegister(2, "c")
    qc = QuantumCircuit(q, c, name=f"th{theta_deg}" + ("" if with_mid else "_nomid"))
    # PREP |0> (NOT |+>): measuring X on |0> is a fair coin, which is the design's exact-1/2
    # foresight floor. Prepping |+> makes the X-measurement DETERMINISTIC (foresight 1.0) and
    # destroys the floor — caught by the dry run before flight, which is what dry runs are for.
    if with_mid:
        qc.h(q[0]); qc.measure(q[0], c[0]); qc.h(q[0])   # projective MID measurement in X
    qc.ry(-math.radians(theta_deg), q[0])        # final basis at theta_f from X
    qc.measure(q[0], c[1])
    return qc

def main():
    dry = "--dry-run" in sys.argv
    circs = [circ(t, True) for t in ANGLES] + [circ(45, False)]
    labels = [{"theta_f": t, "mid": True} for t in ANGLES] + [{"theta_f": 45, "mid": False}]
    if dry:
        from qiskit_aer import AerSimulator
        sim = AerSimulator(); tc = transpile(circs, sim, optimization_level=1, seed_transpiler=20260811)
        n2q = max(sum(v for k, v in c.count_ops().items() if k in ("cz", "ecr", "cx")) for c in tc)
        print(f"[lint] max 2q gates across all circuits = {n2q} (design requires 0 — the wall that killed 6+6b)")
        res = sim.run(tc, shots=20000).result()
        print("[dry-run ideal] theta  foresight  hindsight  gap   (ideal sin/2)")
        for lab, c in zip(labels, tc):
            if not lab["mid"]: continue
            counts = res.get_counts(c); tot = sum(counts.values())
            # bits: c[1]=final (left), c[0]=mid (right) in qiskit's string
            joint = {}
            for k, v in counts.items():
                b = k.replace(" ", ""); fin, mid = int(b[0]), int(b[1])
                joint[(mid, fin)] = joint.get((mid, fin), 0) + v
            fore = max(sum(v for (m, f), v in joint.items() if m == mm) for mm in (0, 1)) / tot
            hind = sum(max(joint.get((0, f), 0), joint.get((1, f), 0)) for f in (0, 1)) / tot
            t = lab["theta_f"]
            print(f"   {t:>3}    {fore:.4f}    {hind:.4f}   {hind-0.5:+.4f}   ({math.sin(math.radians(t))/2:.4f})")
        return
    from ibm_multi_account import assert_explicit_account, service_for_submission, _load_env_files
    _load_env_files()
    acct = assert_explicit_account()
    if acct != "IBMQ_ALT3": raise SystemExit(f"prereg declares IBMQ_ALT3; got {acct} — REFUSING.")
    svc = service_for_submission(acct)
    u = svc.usage(); remaining = float(u["usage_limit_seconds"]) - float(u["usage_consumed_seconds"])
    if u.get("usage_limit_reached") or remaining < EST_COST_S:
        raise SystemExit(f"FIT GATE REFUSES: remaining={remaining}s < est {EST_COST_S}s")
    print(f"[fit gate] {acct}: {remaining:.1f}s remaining >= est {EST_COST_S}s — OK")
    backend = svc.backend("ibm_marrakesh")
    props = backend.properties(); ro = {}
    for qq in range(backend.num_qubits):
        try: ro[qq] = props.readout_error(qq)
        except Exception: pass
    q_best = min(ro, key=ro.get)
    print(f"[layout] live pick q{q_best} (readout err {ro[q_best]:.5f}) — never cached")
    tc = [transpile(c, backend, initial_layout=[q_best], optimization_level=1, seed_transpiler=20260811) for c in circs]
    n2q = max(sum(v for k, v in c.count_ops().items() if k in ("cz", "ecr", "cx")) for c in tc)
    if n2q != 0:
        raise SystemExit(f"🔴 TRANSPILED-COUNT GATE: {n2q} 2q gates found, design requires 0 — REFUSING TO FLY")
    print(f"[transpiled-count gate] 0 two-qubit gates on the flown layout — PASS (the C5058 lesson, applied pre-submit)")
    from qiskit_ibm_runtime import SamplerV2
    job = SamplerV2(mode=backend).run(tc, shots=SHOTS)
    print(f"[submitted] job_id={job.job_id()}")
    man = {"cell": "H13-Cell4-HindsightMeter", "prereg": PREREG, "account": acct, "backend": backend.name,
           "job_id": job.job_id(), "shots": SHOTS, "angles": list(ANGLES), "layout": [q_best],
           "readout_err": ro[q_best], "labels": labels, "transpiled_2q": n2q,
           "fit_gate": {"remaining_at_submit": remaining, "est": EST_COST_S}}
    p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), f"results/h13_cell4_manifest_{job.job_id()}.json")
    json.dump(man, open(p, "w"), indent=1); print(f"[manifest] {p}")

if __name__ == "__main__":
    main()
