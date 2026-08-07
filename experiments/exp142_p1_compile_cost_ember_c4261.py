"""Whisper #6178 blocker-2 applied to MY flight: do the P1 circuits compile
inside a purity budget on real hardware? $0, transpile only, no submission."""
import sys
sys.path.insert(0,'experiments'); sys.path.insert(0,'scripts')
from run_exp66_qpu_partb import _get_ibm_service
import exp142_flight_kit as K
from exp142_flight_kit import pick_layouts
from qiskit import transpile

bk=_get_ibm_service().backend('ibm_marrakesh')
t=bk.target
twoq = "cz" if "cz" in t.operation_names else "ecr"
# lambda_eff from whisper's v5b read: u=0.762 over 234 2q gates
import math
LAM = 1.16e-3
print(f"basis 2q gate = {twoq};  lambda_eff = {LAM:.2e}/2q  (whisper v5b, our own hardware)")
print(f"purity gate u >= 0.70  ->  budget = {math.log(1/0.70)/LAM:.0f} two-qubit gates\n")
BUDGET = math.log(1/0.70)/LAM

for n in (4,6,8):
    q_layout, conv_layout, pairs = pick_layouts(bk,n)
    qqc,_ = K.quantum_template(n)
    cqc,_ = K.conv_template(n)
    tq = transpile(qqc, backend=bk, initial_layout=q_layout, optimization_level=1)
    tc = transpile(cqc, backend=bk, initial_layout=conv_layout, optimization_level=1)
    nq = tq.count_ops().get(twoq,0)
    nc = tc.count_ops().get(twoq,0)
    uq = math.exp(-LAM*nq); uc = math.exp(-LAM*nc)
    print(f"n={n}")
    print(f"  Q  two-copy template : {nq:>5} 2q gates   -> u={uq:.4f}   {'PASS' if uq>=0.70 else 'FAIL'}  ({nq/BUDGET*100:.1f}% of budget)")
    print(f"  C1 conventional      : {nc:>5} 2q gates   -> u={uc:.4f}   {'PASS' if uc>=0.70 else 'FAIL'}  ({nc/BUDGET*100:.1f}% of budget)")
    print(f"  depth Q={tq.depth()} C1={tc.depth()}")
    print()
