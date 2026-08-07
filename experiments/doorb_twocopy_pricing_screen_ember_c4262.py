"""DOOR (b) PRICING SCREEN — Elder #6224 ordering rule: price the TWO-COPY ROUTED
circuit BEFORE any theorem work. t-doped stabilizer = Clifford prep + t T-gates.
Prices the JOINT two-copy circuit (my n=12 error: I priced ONE copy). $0."""
import sys, math, statistics as st
sys.path.insert(0,'experiments'); sys.path.insert(0,'scripts')
from run_exp66_qpu_partb import _get_ibm_service
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import random_clifford
import numpy as np
bk=_get_ibm_service().backend('ibm_marrakesh')
twoq="cz" if "cz" in bk.target.operation_names else "ecr"
LAM=2.565e-3; GATE=0.70
def tdoped_twocopy(n,t,seed):
    """two independent t-doped copies + transversal Bell measurement across them"""
    rng=np.random.default_rng(seed)
    qc=QuantumCircuit(2*n)
    for off in (0,n):
        cl=random_clifford(n, seed=int(rng.integers(1e6)))
        qc.compose(cl.to_circuit(), qubits=range(off,off+n), inplace=True)
        for q in rng.choice(n, size=t, replace=False):
            qc.t(off+int(q))
    for i in range(n):                      # transversal Bell measure
        qc.cx(i, n+i); qc.h(i)
    return qc
print(f"DOOR (b) SCREEN — TWO-COPY joint routed, lambda={LAM:.3e}, gate u>={GATE}")
print(f"{'n':>3} {'t':>3} {'routed 2q (3 draws)':>24} {'u':>8}")
for n,t in ((4,2),(6,3),(8,2),(8,4)):
    c=[]
    for s in range(3):
        qc=tdoped_twocopy(n,t,4262+s)
        tq=transpile(qc, backend=bk, optimization_level=2)
        c.append(tq.count_ops().get(twoq,0))
    m=st.median(c); u=math.exp(-LAM*m)
    print(f"{n:>3} {t:>3}   med {m:>5.0f} range[{min(c)},{max(c)}]   {u:>7.4f} {'PASS' if u>=GATE else 'FAIL'}")
