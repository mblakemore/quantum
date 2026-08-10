#!/usr/bin/env python3
"""H13 Cells 6+6b MERGED — Silent Tripwire + Counterfactual Computation — SUBMIT.

Prereg: docs/h13-cell6-6b-merged-prereg-DRAFT-v2-whisper-c5056.md (freeze act = this run's
live-cal re-centering, recorded in the manifest).
Creator GO: #70 tank package (Cell 2 + Cell 6+6b), 2026-08-11.
Usage: QPU_ACCOUNT_VAR=IBMQ_ALT3 python3 scripts/h13_cell6_6b_submit_c5058.py [--dry-run]
"""
import json, os, sys, math, hashlib
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.pop("QISKIT_IBM_INSTANCE", None)
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile
from qiskit.circuit.library import RCCXGate, RC3XGate

DECLARED_BACKENDS = ("ibm_marrakesh", "ibm_fez")
SHOTS = 4000
EST_COST_S = 55.0
LADDER_A = (1, 2, 4, 8)
LADDER_B = (2, 4, 8)
MARKED = (1, 1)      # marked item x = 11
UNMARKED = (0, 1)    # transparent variant

def build(tier, N, x, label):
    """probe p=0, detector d=1, x1=2, x2=3, r/anc=4. Same gate SEQUENCE for all x (f-oblivious)."""
    q = QuantumRegister(5, "q")
    cd = ClassicalRegister(max(N, 1), "d")
    cp = ClassicalRegister(1, "p")
    cr = ClassicalRegister(1, "r")
    qc = QuantumCircuit(q, cd, cp, cr, name=label)
    p, d, x1, x2, aux = 0, 1, 2, 3, 4
    if x[0]: qc.x(q[x1])
    if x[1]: qc.x(q[x2])
    if tier == "A":                      # U_f runs unconditionally, writes answer into aux
        qc.ccx(q[x1], q[x2], q[aux])
    qc.barrier()
    for k in range(N):
        qc.ry(math.pi / N, q[p])
        if tier == "A":
            qc.append(RCCXGate(), [q[p], q[aux], q[d]])          # answer-conditioned tripwire
        else:
            qc.append(RC3XGate(), [q[p], q[x1], q[x2], q[d]])    # machine runs only in probe's branch
        qc.measure(q[d], cd[k])
        qc.reset(q[d])
        qc.barrier()
    qc.measure(q[p], cp[0])
    qc.measure(q[aux], cr[0])
    return qc

def premise(kind, tier, x, label):
    q = QuantumRegister(5, "q"); cd = ClassicalRegister(1, "d"); cr = ClassicalRegister(1, "r")
    qc = QuantumCircuit(q, cd, cr, name=label)
    p, d, x1, x2, aux = 0, 1, 2, 3, 4
    if x[0]: qc.x(q[x1])
    if x[1]: qc.x(q[x2])
    if tier == "A": qc.ccx(q[x1], q[x2], q[aux])
    if kind in ("faithful", "transparent"):
        qc.x(q[p])                       # probe FORCED into the arm
        qc.barrier()
        if tier == "A": qc.append(RCCXGate(), [q[p], q[aux], q[d]])
        else:           qc.append(RC3XGate(), [q[p], q[x1], q[x2], q[d]])
    qc.measure(q[d], cd[0]); qc.measure(q[aux], cr[0])
    return qc

def circuit_list():
    out = []
    for N in LADDER_A:
        out.append(("A", N, "marked", build("A", N, MARKED, f"A_N{N}_marked")))
        out.append(("A", N, "unmarked", build("A", N, UNMARKED, f"A_N{N}_unmarked")))
    for N in LADDER_B:
        out.append(("B", N, "marked", build("B", N, MARKED, f"B_N{N}_marked")))
        out.append(("B", N, "unmarked", build("B", N, UNMARKED, f"B_N{N}_unmarked")))
    out.append(("A", 0, "P1_faithful", premise("faithful", "A", MARKED, "P1_A_faithful")))
    out.append(("A", 0, "P2_transparent", premise("transparent", "A", UNMARKED, "P2_A_transparent")))
    out.append(("B", 0, "P1_faithful", premise("faithful", "B", MARKED, "P1_B_faithful")))
    out.append(("B", 0, "P2_transparent", premise("transparent", "B", UNMARKED, "P2_B_transparent")))
    out.append(("A", 0, "P3_integrity", premise("integrity", "A", MARKED, "P3_A_integrity")))
    return out

def isomorphism_lint(tcircs, tags):
    """f-OBLIVIOUS LINT: for each (tier,N), marked and unmarked transpiled circuits must have
    IDENTICAL gate sequences apart from the leading X-prep layer on the input qubits."""
    def sig(c):
        s = []
        seen_barrier = False
        for inst in c.data:
            nm = inst.operation.name
            if nm == "barrier": seen_barrier = True
            if not seen_barrier and nm in ("x", "sx", "rz"): continue   # prep layer skipped
            s.append((nm, tuple(c.find_bit(q).index for q in inst.qubits)))
        return hashlib.sha256(repr(s).encode()).hexdigest()[:16]
    groups, fails = {}, []
    for (tier, N, var, _), tc in zip(tags, tcircs):
        if var in ("marked", "unmarked"):
            groups.setdefault((tier, N), {})[var] = sig(tc)
    for k, v in groups.items():
        if len(v) == 2 and v["marked"] != v["unmarked"]:
            fails.append((k, v))
    return fails, {f"{k[0]}_N{k[1]}": v for k, v in groups.items()}

def main():
    dry = "--dry-run" in sys.argv
    tags = circuit_list()
    circs = [t[3] for t in tags]
    print(f"[build] {len(circs)} circuits; ladders A{LADDER_A} B{LADDER_B}; {SHOTS} shots each")
    if dry:
        from qiskit_aer import AerSimulator
        sim = AerSimulator()
        tc = transpile(circs, sim, optimization_level=1, seed_transpiler=20260811)
        fails, sigs = isomorphism_lint(tc, tags)
        print(f"[lint] f-oblivious isomorphism: {'FAIL ' + str(fails) if fails else 'PASS (all variant pairs identical modulo prep)'}")
        res = sim.run(tc, shots=2000).result()
        for (tier, N, var, _), c in zip(tags, tc):
            counts = res.get_counts(c)
            tot = sum(counts.values())
            if var in ("marked", "unmarked"):
                eta = fired = f0 = 0
                for bits, n in counts.items():
                    parts = bits.split()               # qiskit: 'r p d' reversed order
                    r_b, p_b, d_b = parts[0], parts[1], parts[2]
                    if "1" in d_b: fired += n
                    elif p_b == "0": eta += n
                    else: f0 += n
                print(f"  {tier} N={N:<2} {var:<9} eta={eta/tot:.3f} f0call={f0/tot:.3f} fired={fired/tot:.3f}")
            else:
                print(f"  {tier} {var}: {dict(list(counts.items())[:4])}")
        return
    from ibm_multi_account import assert_explicit_account, service_for_submission, _load_env_files
    _load_env_files()
    acct = assert_explicit_account()
    if acct != "IBMQ_ALT3": raise SystemExit(f"prereg declares IBMQ_ALT3; got {acct} — REFUSING.")
    svc = service_for_submission(acct)
    u = svc.usage()
    remaining = float(u["usage_limit_seconds"]) - float(u["usage_consumed_seconds"])
    if u.get("usage_limit_reached") or remaining < EST_COST_S:
        raise SystemExit(f"FIT GATE REFUSES: remaining={remaining}s < est {EST_COST_S}s")
    print(f"[fit gate] {acct}: {remaining:.1f}s remaining >= est {EST_COST_S}s — OK")
    backend = None
    for name in DECLARED_BACKENDS:
        try:
            b = svc.backend(name)
            if b.status().operational: backend = b; break
        except Exception: continue
    if backend is None: raise SystemExit("no declared backend operational")
    print(f"[backend] {backend.name} queue={backend.status().pending_jobs}")
    props = backend.properties()
    ro = {}
    for q in range(backend.num_qubits):
        try: ro[q] = props.readout_error(q)
        except Exception: pass
    adj = {}
    for a, b_ in backend.coupling_map:
        adj.setdefault(a, set()).add(b_); adj.setdefault(b_, set()).add(a)
    best, best_s = None, 1e9
    for seed in sorted(ro, key=ro.get)[:40]:
        sub = [seed]
        while len(sub) < 5:
            cands = [n for s in sub for n in adj.get(s, ()) if n not in sub and n in ro]
            if not cands: break
            sub.append(min(cands, key=ro.get))
        if len(sub) < 5: continue
        s = sum(ro[q] for q in sub)
        for i in range(len(sub)):
            for j in range(i+1, len(sub)):
                if sub[j] in adj.get(sub[i], ()):
                    try: s += props.gate_error("cz", (sub[i], sub[j]))
                    except Exception: pass
        if s < best_s: best, best_s = sub, s
    print(f"[layout] live pick {best} (score {best_s:.4f}, never cached)")
    tc = transpile(circs, backend, initial_layout=best, optimization_level=1, seed_transpiler=20260811)
    fails, sigs = isomorphism_lint(tc, tags)
    if fails: raise SystemExit(f"F-OBLIVIOUS LINT FAILED — REFUSING TO FLY: {fails}")
    print(f"[lint] f-oblivious isomorphism PASS ({len(sigs)} variant groups identical modulo prep)")
    from qiskit_ibm_runtime import SamplerV2
    sampler = SamplerV2(mode=backend)
    job = sampler.run(tc, shots=SHOTS)
    print(f"[submitted] job_id={job.job_id()}")
    man = {"cell": "H13-Cell6+6b", "prereg": "docs/h13-cell6-6b-merged-prereg-DRAFT-v2-whisper-c5056.md",
           "account": acct, "backend": backend.name, "job_id": job.job_id(), "shots": SHOTS,
           "layout": best, "layout_score": best_s, "ladder_A": list(LADDER_A), "ladder_B": list(LADDER_B),
           "labels": [{"tier": t, "N": n, "variant": v} for t, n, v, _ in tags],
           "lint": {"f_oblivious_isomorphism": "PASS", "group_sigs": sigs},
           "fit_gate": {"remaining_at_submit": remaining, "est": EST_COST_S}}
    out = f"results/h13_cell6_6b_manifest_{job.job_id()}.json"
    json.dump(man, open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), out), "w"), indent=1)
    print(f"[manifest] {out}")

if __name__ == "__main__":
    main()
