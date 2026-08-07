"""Elder #6216: ALT := random degree-2 phase state, prep H^n . S^diag . CZ^offdiag,
<= n(n-1)/2 CZ LOGICAL. Question: what is it AFTER ROUTING on heavy-hex? $0."""
import sys, math, statistics as st
sys.path.insert(0,'experiments'); sys.path.insert(0,'scripts')
from run_exp66_qpu_partb import _get_ibm_service
from qiskit import QuantumCircuit, transpile
import numpy as np
bk=_get_ibm_service().backend('ibm_marrakesh')
twoq="cz" if "cz" in bk.target.operation_names else "ecr"
LAM_M=2.565e-3; LAM_B=1.16e-3
def phase_state(n, seed):
    rng=np.random.default_rng(seed)
    A=np.triu(rng.integers(0,2,size=(n,n)))
    qc=QuantumCircuit(n); qc.h(range(n))
    for i in range(n):
        if A[i,i]: qc.s(i)
    for i in range(n):
        for j in range(i+1,n):
            if A[i,j]: qc.cz(i,j)
    return qc, int(A[np.triu_indices(n,1)].sum())
print(f"{'n':>3} {'logical CZ':>18} {'ROUTED 2q (5 draws)':>22} {'blowup':>7} {'u@meas':>8}")
for n in (8,12,16):
    log_,rout=[],[]
    for s in range(5):
        qc,nz=phase_state(n,4262+s)
        t=transpile(qc, backend=bk, optimization_level=2)
        log_.append(nz); rout.append(t.count_ops().get(twoq,0))
    ml,mr=st.median(log_),st.median(rout)
    cap=n*(n-1)//2
    u=math.exp(-LAM_M*mr)
    print(f"{n:>3}  med {ml:>4.0f} (cap {cap:>3})   med {mr:>5.0f} range[{min(rout)},{max(rout)}]  {mr/max(ml,1):>6.2f}x  {u:>7.4f} {'PASS' if u>=.7 else 'FAIL'}")
