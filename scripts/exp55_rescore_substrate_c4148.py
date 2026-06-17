import sys; sys.path.insert(0, "/droid/repos/quantum/scripts")
import json, numpy as np
from qiskit_aer import AerSimulator
from run_exp46_fast import (
    EDGES_20, N_QUBITS_20, brute_force_max_cut,
    build_parameterized_xbasis_qaoa, evaluate_with_transpiled,
)
from qiskit import transpile
from qiskit_ibm_runtime.fake_provider import FakeMarrakesh

P, OPT_LEVEL, SEED_TRANSPILER, THR = 5, 1, 42, 0.64
ck = json.load(open("../results/exp55_optionA_p5_checkpoint.json"))["arm0"]

edges, nq = EDGES_20, N_QUBITS_20
max_cut = brute_force_max_cut(nq, edges)
fake = FakeMarrakesh()
qc, gp, bp = build_parameterized_xbasis_qaoa(P, nq, edges)
tqc = transpile(qc, backend=fake, optimization_level=OPT_LEVEL, seed_transpiler=SEED_TRANSPILER)

def rescore(x, shots, reps, base):
    vals = []
    for r in range(reps):
        sim = AerSimulator(seed_simulator=base + r)
        vals.append(evaluate_with_transpiled(x, tqc, gp, bp, P, sim, edges, max_cut, nq, shots))
    return np.array(vals)

print(f"p={P} thr={THR}  re-score of captured Arm-0 x_best (noiseless = no device-noise model)")
print(f"{'seed':>4} {'logged':>8} | {'1024sh x8 mean':>14} {'min':>7} {'max':>7} {'#esc':>5} | {'32768sh x6 mean':>15} {'verdict':>10}")
for s in ["47","43","51","42","48"]:
    if s not in ck: continue
    x = ck[s]["x"]; logged = ck[s]["ratio"]
    lo = rescore(x, 1024, 8, 3000)
    hi = rescore(x, 32768, 6, 9000)
    nesc = int((lo >= THR).sum())
    verdict = "ESCAPE" if hi.mean() >= THR else "TRAP"
    print(f"{s:>4} {logged:8.4f} | {lo.mean():14.4f} {lo.min():7.4f} {lo.max():7.4f} {nesc:>3}/8 | {hi.mean():15.4f} {verdict:>10}")
