"""TWO DECIDING MEASUREMENTS, both $0.
 A: t-dependence with the CLIFFORD HELD FIXED (kills my rng confound, gives Whisper the power they lacked)
 B: lambda_eff at SIXTEEN qubits — the width the two-copy circuit actually uses"""
import sys, math, statistics as st
sys.path.insert(0,'experiments'); sys.path.insert(0,'scripts')
from run_exp66_qpu_partb import _get_ibm_service
from exp142_flight_kit import pick_layouts
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import random_clifford
import numpy as np
bk=_get_ibm_service().backend('ibm_marrakesh'); tgt=bk.target
twoq="cz" if "cz" in tgt.operation_names else "ecr"

print("=== A: t-dependence, SAME Clifford, only t varies (12 Clifford draws x t in 0,2,4,8) ===")
res={t:[] for t in (0,2,4,8)}
for d in range(12):
    c1=random_clifford(8, seed=900+d); c2=random_clifford(8, seed=5000+d)
    sites=np.random.default_rng(77+d).permutation(8)      # fixed site ORDER, prefix by t
    for t in (0,2,4,8):
        qc=QuantumCircuit(16)
        qc.compose(c1.to_circuit(), qubits=range(0,8), inplace=True)
        qc.compose(c2.to_circuit(), qubits=range(8,16), inplace=True)
        for q in sites[:t]:
            qc.t(int(q)); qc.t(int(q)+8)
        for i in range(8): qc.cx(i,8+i); qc.h(i)
        res[t].append(transpile(qc, backend=bk, optimization_level=3).count_ops().get(twoq,0))
base=st.median(res[0])
for t in (0,2,4,8):
    m=st.median(res[t])
    print(f"  t={t:>2}  median {m:>5.0f}  mean {st.mean(res[t]):>6.1f}  sd {st.pstdev(res[t]):>5.1f}   delta-vs-t0 {m-base:+.0f}")
# paired test: same Clifford, t=8 vs t=0
diffs=[a-b for a,b in zip(res[8],res[0])]
print(f"  PAIRED t=8 minus t=0 (same Clifford each pair): mean {st.mean(diffs):+.1f}  sd {st.pstdev(diffs):.1f}  n={len(diffs)}")
print(f"    per-T-gate implied: {st.mean(diffs)/16:+.2f} routed 2q per T  (16 T gates added: 8 sites x 2 copies)")

print("\n=== B: lambda_eff at SIXTEEN qubits (the real circuit width) ===")
_,_,pairs8=pick_layouts(bk,8)
q16=[q for p in pairs8 for q in p]
errs=[]
for (a,b),inst in tgt[twoq].items():
    e=getattr(inst,"error",None)
    if e is not None and a in q16 and b in q16: errs.append(e)
allq=[getattr(i,"error",None) for i in tgt[twoq].values()]; allq=[e for e in allq if e is not None and e<1]
print(f"  edges INSIDE the 16-qubit region: n={len(errs)}  mean {st.mean(errs):.3e}  worst {max(errs):.3e}")
print(f"  the 8 SELECTED pairs only     : mean 2.565e-3  (what the knife-edge pass used)")
print(f"  device-wide median            : {st.median(allq):.3e}")
for lam,l in ((2.565e-3,'selected-8-pairs'),(st.mean(errs),'16q region mean'),(st.median(allq),'device median')):
    for g,gl in ((132,'whisper joint opt3+lottery n=8 t=2'),(118,'n=8 t=4')):
        u=math.exp(-lam*g)
        print(f"    lambda={lam:.3e} ({l:16}) {gl:36} u={u:.4f} {'PASS' if u>=.7 else 'FAIL'}")
