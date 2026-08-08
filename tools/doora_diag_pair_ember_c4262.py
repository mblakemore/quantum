#!/usr/bin/env python3
"""DOOR (a) v5 DIAGNOSTIC PAIR — public-A only, NO SEALED CONTENT. Ember C4262.

WHY: the probe's STOP rests on 3 - 2 = 1, a difference of small INTEGERS. usage()
returns integer seconds, so the projection's resolution floor is coarser than the
quantity it decides. Two public-A jobs at 32 and 100 rows solve OH and r EXACTLY:

    usage(32)  = OH + 32r
    usage(100) = OH + 100r
    r  = (usage(100) - usage(32)) / 68     <- the 68-row difference divides the
    OH = usage(32) - 32r                      integer readings, ~15x better resolution

Frozen v5 refusal branch (Elder). Touches NOTHING sealed — every A here is drawn
publicly and printed in the clear.
"""
import sys, os, re, json, time, datetime
sys.path.insert(0, "scripts")
N = 8

def alt_token():
    with open("/droid/repos/DC15W/.env") as f:
        for line in f:
            m = re.match(r"^IBMQ_ALT=(.+)$", line.strip())
            if m: return m.group(1).strip().strip('"').strip("'")
    sys.exit("REFUSE: IBMQ_ALT not found")

import numpy as np, importlib.util
from qiskit import transpile
from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
s = importlib.util.spec_from_file_location("kit",
    "experiments/exp_door_a_flight_kit_v2_whisper_c5027.py")
kit = importlib.util.module_from_spec(s)
try: s.loader.exec_module(kit)
except SystemExit: pass

svc = QiskitRuntimeService(channel="ibm_quantum_platform", token=alt_token())
bk = svc.backend("ibm_marrakesh")
cm = bk.target.build_coupling_map()
lay = kit.line_layout(cm, 2*N)
qc, hA, hB = kit.q_circuit_unbound(N)
t = transpile(qc, backend=bk, initial_layout=lay, optimization_level=1)
order = list(t.parameters)

u0 = svc.usage(); rem0 = u0["usage_limit_seconds"] - u0["usage_consumed_seconds"]
print(f"  remaining before diagnostics: {rem0}s")

def public_rows(k, seed0):
    """PUBLIC A only — drawn from a stated seed, nothing sealed."""
    out = []
    for i in range(k):
        A = kit.random_A(N, np.random.default_rng(seed0 + i))
        bd = kit.q_bindings(1, A, np.random.default_rng(seed0 + 5000 + i), hA, hB)
        out.append([float(bd[p]) for p in order])
    return out

res = {}
for k, seed0 in ((32, 700000), (100, 800000)):
    rows = public_rows(k, seed0)
    job = SamplerV2(mode=bk).run([(t, rows, 1)])
    print(f"  k={k:>3} submitted job {job.job_id()}", flush=True)
    for _ in range(60):
        st = str(job.status())
        if st in ("DONE", "ERROR", "CANCELLED"): break
        time.sleep(10)
    print(f"  k={k:>3} status {job.status()}  usage={job.usage()}s", flush=True)
    if str(job.status()) != "DONE": sys.exit("  diagnostic did not complete")
    res[k] = job.usage()

r = (res[100] - res[32]) / 68.0
OH = res[32] - 32*r
print()
print(f"  usage(32)={res[32]}s  usage(100)={res[100]}s")
print(f"  r  = ({res[100]} - {res[32]})/68 = {r:.6f} s/row")
print(f"  OH = {res[32]} - 32*{r:.6f}     = {OH:.4f} s")
u1 = svc.usage(); rem1 = u1["usage_limit_seconds"] - u1["usage_consumed_seconds"]
ceiling = rem1 * 0.5
proj40 = OH + 39*77*r
proj20 = OH + 19*77*r
print()
print(f"  remaining now {rem1}s   ceiling(50%) {ceiling}s")
print(f"  PROJECT 39 more trials (M=40): {OH:.2f} + 3003*{r:.6f} = {proj40:.2f}s -> {'PASS' if proj40<=ceiling else 'STOP'}")
print(f"  PROJECT 19 more trials (M=20): {OH:.2f} + 1463*{r:.6f} = {proj20:.2f}s -> {'PASS' if proj20<=ceiling else 'STOP'}")
