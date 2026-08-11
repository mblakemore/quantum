#!/usr/bin/env python3
"""H13 Cell 7 — THE SPEED OF SUBSPACE — SUBMIT. Whisper C5058, Creator GO (the 91s grant).

Measures the emergent light cone: connected correlator C(r,d) between a perturbed site and site r
after d brickwork layers. Deliverables: v_LR in sites/layer (strict circuit bound 2), outside-cone
correlators ~0, and the T2.5 HIDDEN-ORDER CONFOUND ARM folded in (board #65 decision): a
nominally-parallel layer vs an explicitly-sequenced one — if the chip secretly sequences, the cone
is measuring the scheduler, not the physics.
Usage: QPU_ACCOUNT_VAR=IBMQ_ALT3 python3 scripts/h13_cell7_submit_c5058.py [--dry-run]
"""
import json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.pop("QISKIT_IBM_INSTANCE", None)
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile

NSITES, DEPTHS, SHOTS, EST_COST_S = 21, (1, 2, 3, 4, 5, 6, 7, 8), 4000, 45.0
PREREG = "docs/h13-cell7-lightcone-prereg-FROZEN-whisper-c5058.md"

def brickwork(qc, q, n, d, sequenced=False):
    for layer in range(d):
        for s in (layer % 2, 1 - layer % 2) if sequenced else (layer % 2,):
            for i in range(s, n - 1, 2):
                qc.cz(q[i], q[i + 1])
            if sequenced: qc.barrier()
        if not sequenced:
            for i in range(n): qc.ry(math.pi / 4, q[i])
        else:
            for i in range(n): qc.ry(math.pi / 4, q[i])

def circ(n, d, perturb, name, sequenced=False):
    q = QuantumRegister(n, "q"); c = ClassicalRegister(n, "c")
    qc = QuantumCircuit(q, c, name=name)
    if perturb: qc.x(q[0])
    qc.barrier()
    brickwork(qc, q, n, d, sequenced)
    qc.measure(q, c)
    return qc

def build():
    circs, labels = [], []
    for d in DEPTHS:
        for pert in (True, False):
            circs.append(circ(NSITES, d, pert, f"d{d}_{'P' if pert else 'R'}"))
            labels.append({"depth": d, "perturbed": pert, "arm": "cone"})
    # T2.5 confound arm (board #65): nominally-parallel vs explicitly-sequenced, same depth
    for seq in (False, True):
        circs.append(circ(NSITES, 4, True, f"t25_{'seq' if seq else 'par'}", sequenced=seq))
        labels.append({"depth": 4, "perturbed": True, "arm": "t25_sequenced" if seq else "t25_parallel"})
    return circs, labels

def main():
    dry = "--dry-run" in sys.argv
    circs, labels = build()
    print(f"[build] {len(circs)} circuits ({NSITES} sites, depths {DEPTHS}, + T2.5 confound pair)")
    if dry:
        from qiskit_aer import AerSimulator
        sim = AerSimulator(); tc = transpile(circs, sim, optimization_level=1, seed_transpiler=20260811)
        mx = max(sum(v for k, v in c.count_ops().items() if k in ("cz", "cx", "ecr")) for c in tc)
        print(f"[depth] max 2q gates = {mx} (standing many-body ceiling ~250 — {'INSIDE' if mx <= 250 else 'OVER'})")
        res = sim.run(tc, shots=4000).result()
        zs = {}
        for lab, c in zip(labels, tc):
            if lab["arm"] != "cone": continue
            counts = res.get_counts(c); tot = sum(counts.values())
            z = [0.0] * NSITES
            for b, v in counts.items():
                bs = b.replace(" ", "")[::-1]
                for i in range(NSITES): z[i] += v * (1 - 2 * int(bs[i]))
            zs[(lab["depth"], lab["perturbed"])] = [x / tot for x in z]
        print("[dry-run ideal] front position (largest r with |C(r)|>0.05), strict bound = 2r/layer:")
        for d in DEPTHS:
            C = [abs(zs[(d, True)][r] - zs[(d, False)][r]) for r in range(NSITES)]
            front = max([r for r in range(NSITES) if C[r] > 0.05], default=0)
            print(f"   d={d}: front r={front:<3} (bound {min(2*d, NSITES-1)})  {'OK' if front <= 2*d else 'VIOLATION'}")
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
    adj = {}
    for x, y in backend.coupling_map: adj.setdefault(x, set()).add(y); adj.setdefault(y, set()).add(x)
    def cz_err(a, b):
        for pair in ((a, b), (b, a)):
            try: return props.gate_error("cz", pair)
            except Exception: continue
        return 1.0
    best, best_s = None, 1e9
    for start in sorted(ro, key=ro.get)[:80]:                    # QUIET-LINE PICKER, live, never cached
        line, cur = [start], start
        while len(line) < NSITES:
            cands = [n for n in adj.get(cur, ()) if n not in line and n in ro]
            if not cands: break
            cur = min(cands, key=lambda n: ro[n] + cz_err(line[-1], n)); line.append(cur)
        if len(line) < NSITES: continue
        s = sum(ro[q] for q in line) + sum(cz_err(line[i], line[i+1]) for i in range(NSITES-1))
        if s < best_s: best, best_s = line, s
    if best is None: raise SystemExit("no 21-qubit quiet line found")
    print(f"[layout] live quiet line ({NSITES} sites) score {best_s:.4f}: {best[:6]}…{best[-3:]}")
    tc = transpile(circs, backend, initial_layout=best, optimization_level=1, seed_transpiler=20260811)
    mx = max(sum(v for k, v in c.count_ops().items() if k in ("cz", "cx", "ecr")) for c in tc)
    print(f"[transpiled-count gate] max 2q = {mx} vs standing many-body ceiling 250 — {'PASS' if mx <= 250 else 'REFUSE'}")
    if mx > 250: raise SystemExit("🔴 over the standing many-body ceiling — REFUSING TO FLY")
    from qiskit_ibm_runtime import SamplerV2
    job = SamplerV2(mode=backend).run(tc, shots=SHOTS)
    print(f"[submitted] job_id={job.job_id()}")
    man = {"cell": "H13-Cell7-SpeedOfSubspace", "prereg": PREREG, "account": acct, "backend": backend.name,
           "job_id": job.job_id(), "shots": SHOTS, "nsites": NSITES, "depths": list(DEPTHS),
           "layout": best, "layout_score": best_s, "labels": labels, "max_2q": mx,
           "fit_gate": {"remaining_at_submit": remaining, "est": EST_COST_S}}
    p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), f"results/h13_cell7_manifest_{job.job_id()}.json")
    json.dump(man, open(p, "w"), indent=1); print(f"[manifest] {p}")

if __name__ == "__main__":
    main()
