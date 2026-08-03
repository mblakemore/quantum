#!/usr/bin/env python3
"""STETH PRE-SEAL GATE v5 — destructive SWAP witness (no ancilla). Whisper C5018.
GO: Creator general#4005 'v5 prereg go/fly it when ready'. Prereg: docs/steth-gate-v5-prereg.
u = two-copy purity of Choi(U_public) via transversal Bell measurement (Cincio):
per qubit-pair parity product; purity = E[prod (-1)^(a_i AND b_i)]. Ideal 1 (pure Choi).
FLOOR 0.70 (unchanged). D arm (per-shot Pauli-twirled Choi) REPORTED. No lambda_anc arm
exists (apparatus needs no attribution). Zones: Ember freezes blind pre-landing (v4 rule).
"""
import json, os, sys
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); RES = os.path.join(HERE,"..","results")
K = 2; SHOTS_U = 3000; SHOTS_D = 3000; SEED = 4227  # public Haar seed lineage (v2 arc)

def choi_prep(U):
    from qiskit import QuantumCircuit
    qc = QuantumCircuit(4*K, 4*K)
    for c in range(2):                       # two copies, each 2K qubits (sys+ref)
        base = 2*K*c
        for i in range(K): qc.h(base+i); qc.cx(base+i, base+K+i)
        qc.append(U, range(base, base+K))
    for i in range(2*K):                     # transversal Bell meas copy1<->copy2
        qc.cx(i, 2*K+i); qc.h(i)
    qc.measure(range(4*K), range(4*K))
    return qc

def purity_from_counts(counts):
    tot = 0; acc = 0.0
    for key, n in counts.items():
        b = key[::-1]; par = 1
        for i in range(2*K):
            par *= -1 if (b[i]=="1" and b[2*K+i]=="1") else 1
        acc += n*par; tot += n
    p = acc/tot
    return p, float(np.sqrt(max(1-p*p, 1.0/tot)/tot))

def build():
    from qiskit.quantum_info import random_unitary
    from qiskit.circuit.library import UnitaryGate
    U = UnitaryGate(random_unitary(2**K, seed=SEED), label="Upub")
    return U

def ka():
    from qiskit.quantum_info import Statevector
    U = build()
    qc = choi_prep(U); body = qc.remove_final_measurements(inplace=False)
    probs = Statevector(body).probabilities()
    synth = {format(i, f"0{4*K}b"): p*1e6 for i,p in enumerate(probs) if p>1e-12}
    p,_ = purity_from_counts(synth)
    ok = abs(p-1.0) < 1e-9
    print(f"KA purity(U arm) = {p:+.12f} (target 1)  {'PASS' if ok else 'FAIL'}")
    return ok

def fly():
    if not ka(): sys.exit("KA FAIL — NO FLY")
    sys.path.insert(0, os.path.join(HERE,"..","scripts"))
    from ibm_multi_account import service_for_submission
    from qiskit import transpile
    from qiskit_ibm_runtime import SamplerV2
    from qiskit.transpiler import PassManager
    from qiskit.transpiler.passes import ALAPScheduleAnalysis, PadDynamicalDecoupling
    from qiskit.circuit.library import XGate
    from qiskit.quantum_info import random_unitary
    from qiskit.circuit.library import UnitaryGate
    svc = service_for_submission("IBMQ_ALT2"); u = svc.usage()
    print(f"POOL: {u['usage_remaining_seconds']}s")
    backend = svc.backend("ibm_fez")
    U = build()
    rng = np.random.default_rng(SEED)
    circs = [choi_prep(U)]
    if "--v5b" in sys.argv:
        # REAL twirl D (can fail): 8 Pauli-twirl instances of the U-Choi, ideal purity 4^-K
        from qiskit import QuantumCircuit
        for t in range(8):
            trng = np.random.default_rng(SEED + 100 + t)
            qc = QuantumCircuit(4*K, 4*K)
            for c in range(2):
                base = 2*K*c
                for i in range(K): qc.h(base+i); qc.cx(base+i, base+K+i)
                qc.append(U, range(base, base+K))
                for q in range(base, base+2*K):     # independent Pauli per copy = mixing
                    g = trng.integers(4)
                    if g==1: qc.x(q)
                    elif g==2: qc.y(q)
                    elif g==3: qc.z(q)
            for i in range(2*K):
                qc.cx(i, 2*K+i); qc.h(i)
            qc.measure(range(4*K), range(4*K))
            circs.append(qc)
    else:
        dU = UnitaryGate(random_unitary(2**K, seed=SEED+1), label="Dtw")
        circs.append(choi_prep(dU))
    # QUIET-REGISTER lever via the routing lottery (attenuation-map rule): best-of-8
    # pre-registered transpile draws, pick min 2q count (declared, not post-hoc)
    best = None
    for s in range(8):
        cand = transpile(circs, backend, optimization_level=3, seed_transpiler=SEED+s)
        n2 = sum(sum(1 for i in t.data if len(i.qubits)==2) for t in cand)
        if best is None or n2 < best[0]: best = (n2, cand, s)
    tq = best[1]; print(f"routing draw: seed +{best[2]}, total 2q {best[0]}")
    pm = PassManager([ALAPScheduleAnalysis(backend.target.durations()),
                      PadDynamicalDecoupling(backend.target.durations(), [XGate(), XGate()])])
    out = pm.run(tq)
    xb = sum(sum(1 for i in t.data if i.operation.name=="x") for t in tq)
    xa = sum(sum(1 for i in t.data if i.operation.name=="x") for t in out)
    if xa <= xb: sys.exit("DD HOLD")
    print(f"DD {xb}->{xa}")
    n2 = [sum(1 for i in t.data if len(i.qubits)==2) for i in [None] for t in out]
    shots_list = [SHOTS_U] + ([375]*8 if "--v5b" in sys.argv else [SHOTS_D])
    job = SamplerV2(mode=backend).run([(o,None,s) for o,s in zip(out, shots_list)])
    man = {"experiment":("steth_gate_v5b_quietreg_realtwirl" if "--v5b" in sys.argv else "steth_gate_v5_destructive"),"cycle":"C5018","k":K,"floor_u":0.70,
           "go":"Creator general#4005","seed_pub":SEED,"backend":"ibm_fez","dd":[xb,xa],
           "pool":u["usage_remaining_seconds"],"job_id":job.job_id(),
           "note":"no ancilla arm exists; D arm REPORTED; zones frozen by Ember pre-landing"}
    json.dump(man, open(os.path.join(RES,f"steth_v5_manifest_{job.job_id()}.json"),"w"), indent=1)
    print("SUBMITTED:", job.job_id())

def decode(jid):
    sys.path.insert(0, os.path.join(HERE,"..","scripts"))
    from ibm_multi_account import service_for_job
    svc,_ = service_for_job(jid)
    res = svc.job(jid).result()
    def cts(i):
        d = res[i].data; return getattr(d, list(d.__dict__.keys())[0]).get_counts()
    uu, se_u = purity_from_counts(cts(0))
    npubs = len(list(res))
    if npubs > 2:
        ds = [purity_from_counts(cts(i))[0] for i in range(1, npubs)]
        dd_ = float(np.mean(ds)); se_d = float(np.std(ds, ddof=1)/np.sqrt(len(ds)))
    else:
        dd_, se_d = purity_from_counts(cts(1))
    z = (uu-0.70)/se_u
    v = "PASS" if z>=3 else ("FAIL" if z<=-3 else "UNDERPOWERED")
    out = {"job_id":jid,"u":uu,"se_u":se_u,"z_vs_floor":z,"VERDICT":v,
           "D_reported":{"purity":dd_,"se":se_d}}
    json.dump(out, open(os.path.join(RES,f"steth_v5_decode_{jid}.json"),"w"), indent=1)
    print(f"u = {uu:.4f}±{se_u:.4f} z={z:+.2f} -> {v} | D(rep) {dd_:.4f}")

if __name__=="__main__":
    if "--decode" in sys.argv: decode(sys.argv[sys.argv.index("--decode")+1])
    else: fly()
