"""MEASURE random stabilizer-state prep cost at door (a)'s rungs. $0, transpile only."""
import sys, math, statistics as st
sys.path.insert(0,'experiments'); sys.path.insert(0,'scripts')
from run_exp66_qpu_partb import _get_ibm_service
from qiskit import transpile
from qiskit.quantum_info import random_clifford
bk=_get_ibm_service().backend('ibm_marrakesh')
twoq="cz" if "cz" in bk.target.operation_names else "ecr"
LAM_BORROWED=1.16e-3; LAM_MEASURED=2.565e-3
print(f"{'n':>3} {'2q gates (5 draws)':>26} {'u @borrowed':>12} {'u @measured':>12}")
for n in (8,12,16):
    cnts=[]
    for s in range(5):
        cl=random_clifford(n, seed=1000+s)
        qc=cl.to_circuit()
        tq=transpile(qc, backend=bk, optimization_level=2)
        cnts.append(tq.count_ops().get(twoq,0))
    m=st.median(cnts)
    ub=math.exp(-LAM_BORROWED*m); um=math.exp(-LAM_MEASURED*m)
    print(f"{n:>3} med={m:>5.0f} range[{min(cnts)},{max(cnts)}]   {ub:>10.4f} {'P' if ub>=.7 else 'F'} {um:>10.4f} {'PASS' if um>=.7 else 'FAIL'}")
