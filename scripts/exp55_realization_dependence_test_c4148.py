import sys; sys.path.insert(0, "/droid/repos/quantum/scripts")
import numpy as np, time
from scipy.optimize import minimize
from qiskit import transpile
from qiskit_aer import AerSimulator
from qiskit_ibm_runtime.fake_provider import FakeMarrakesh
from run_exp46_fast import (EDGES_20, N_QUBITS_20, brute_force_max_cut,
    build_parameterized_xbasis_qaoa, evaluate_with_transpiled)

P, OPT, STR, THR, SHOTS, MAXIT = 5, 1, 42, 0.64, 1024, 50
edges, nq = EDGES_20, N_QUBITS_20
max_cut = brute_force_max_cut(nq, edges)
fake = FakeMarrakesh()
qc, gp, bp = build_parameterized_xbasis_qaoa(P, nq, edges)
tqc = transpile(qc, backend=fake, optimization_level=OPT, seed_transpiler=STR)

def cobyla_best(x0, simseed):
    sim = AerSimulator(seed_simulator=simseed)
    best=[0.0]
    def obj(x):
        r=evaluate_with_transpiled(x,tqc,gp,bp,P,sim,edges,max_cut,nq,SHOTS)
        if r>best[0]: best[0]=r
        return -r
    minimize(obj,x0,method='COBYLA',options={'maxiter':MAXIT,'rhobeg':0.5})
    return best[0]

# Hold x0 fixed (identical to Arm-0 mapping), vary ONLY seed_simulator
print(f"Mechanism test: same x0, same FakeMarrakesh circuit, vary seed_simulator only. thr={THR}")
for seed in [47, 43]:
    np.random.seed(seed); x0=np.random.uniform(0,2*np.pi,2*P)
    labels=[]
    for ss in [1000, 2001, 2002, 2003, 2004, 2005]:
        t0=time.time(); r=cobyla_best(x0,ss)
        lab='ESC' if r>=THR else 'TRAP'; labels.append(lab)
        print(f"  seed {seed} seed_sim={ss}: ratio={r:.4f} {lab} ({time.time()-t0:.0f}s)", flush=True)
    ne=labels.count('ESC')
    print(f"  => seed {seed}: {ne}/6 ESC, {6-ne}/6 TRAP  -> {'FLIPS across noise realizations' if 0<ne<6 else 'stable label'}", flush=True)
