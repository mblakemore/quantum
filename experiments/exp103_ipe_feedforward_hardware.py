#!/usr/bin/env python3
"""
Exp103 — Does the IPE gap survive real feedforward? (HARDWARE follow-up to Exp102)
Ember C4106. Pre-registered: pred_c4106_001 (created BEFORE this file was written).

Exp102 (sim, C4105) showed the QFT-dagger readout is the DOMINANT 2q cost in
probe-class QPE (67-77% of transpiled 2q gates, t=3..5) and Kitaev IPE recovers it
(+12.4pp exact-success at t=4/p2=0.005, +22.9pp at p2=0.01). Honest caveat recorded
there: the sim gap is an UPPER bound — mid-circuit measurement dephasing, feedforward
latency, and reset errors are unmodeled and ALL hit IPE specifically. This experiment
measures the one thing sim cannot: the gap on a real device with real feedforward.

Design (deliberately minimal — width 2 vs t+1, one job):
  - Same toy eigenphase construction as Exp102: U = P(2*pi*phi) on work qubit,
    eigenstate |1>. One phi per t, chosen with mixed bits + LSB=1 so the if_test
    feedback rotations actually FIRE (a phi=0.100..0 would never exercise feedforward):
      t=3: y=5  (101),  t=4: y=11 (1011),  t=5: y=21 (10101)
  - Standard QPE: t counting + work, cp ladder, manual inverse QFT (with swaps).
  - IPE: 1 ancilla + work, reset + if_test feedback (identical builder to Exp102).
  - NOISELESS sanity gate (lesson c4099_001: the gate must test exactly what it
    claims): plain AerSimulator, zero noise of any kind, success must be >=0.995.
  - Hardware accounting (free, no QPU): transpile both variants against the REAL
    backend target, count 2q gates -> does the 67-77% line-coupling readout share
    hold on the actual heavy-hex topology?
  - Submit both variants x t=3,4,5 (6 pubs, 4096 shots) in ONE SamplerV2 job.
  - Grade: exact-success per variant, gap_pp per t. Prediction operating point:
    t=4, threshold gap >= +5pp (Branch A) / < +5pp (Branch B) / job-failure (C).

Usage:
  python3 exp103_ipe_feedforward_hardware.py local            # sanity gate + accounting
  python3 exp103_ipe_feedforward_hardware.py submit [backend] # verify support + submit
  python3 exp103_ipe_feedforward_hardware.py grade <job_id>   # fetch + compute gaps
"""
import json, math, sys, datetime, pathlib

from qiskit import QuantumCircuit, transpile

HERE = pathlib.Path(__file__).resolve().parent
JOBFILE = HERE / 'exp103_jobids.json'
RESULTFILE = HERE / 'exp103_results.json'

SHOTS = 4096
T_CASES = [(3, 5), (4, 11), (5, 21)]   # (t, y) with y/2^t the exact eigenphase
DEFAULT_BACKEND = 'ibm_marrakesh'


# ---------- circuit builders (identical construction to Exp102) ----------

def inverse_qft(t):
    fwd = QuantumCircuit(t, name='qft')
    for j in reversed(range(t)):
        fwd.h(j)
        for m in range(j):
            fwd.cp(math.pi / 2 ** (j - m), m, j)
    for i in range(t // 2):
        fwd.swap(i, t - 1 - i)
    return fwd.inverse()


def standard_qpe(t, phi, include_readout=True):
    qc = QuantumCircuit(t + 1, t)
    qc.x(t)
    qc.h(range(t))
    for j in range(t):
        qc.cp(2 * math.pi * phi * (2 ** j), j, t)
    if include_readout:
        qc.compose(inverse_qft(t), qubits=range(t), inplace=True)
    qc.measure(range(t), range(t))
    return qc


def ipe(t, phi):
    """Kitaev iterative phase estimation: ancilla q0, work q1. Measures LSB first."""
    qc = QuantumCircuit(2, t)
    qc.x(1)
    for k in range(t):
        if k > 0:
            qc.reset(0)
        qc.h(0)
        qc.cp(2 * math.pi * phi * (2 ** (t - 1 - k)), 0, 1)
        for m in range(k):
            with qc.if_test((qc.clbits[m], 1)):
                qc.p(-math.pi / 2 ** (k - m), 0)
        qc.h(0)
        qc.measure(0, k)
    return qc


def success_rate(counts, y_target, t):
    tot = sum(counts.values())
    return counts.get(format(y_target, f'0{t}b'), 0) / tot if tot else 0.0


def twoq_count(qc):
    return sum(1 for inst in qc.data
               if inst.operation.num_qubits == 2 and inst.operation.name != 'barrier')


def build_all():
    """[(label, t, y, circuit)] for the 6 pubs."""
    out = []
    for t, y in T_CASES:
        phi = y / 2 ** t
        out.append((f'std_t{t}', t, y, standard_qpe(t, phi, True)))
        out.append((f'ipe_t{t}', t, y, ipe(t, phi)))
    return out


# ---------- phase 1: local noiseless sanity gate ----------

def sanity_gate():
    from qiskit_aer import AerSimulator
    sim = AerSimulator()          # ZERO noise of any kind — gate tests exactly its claim
    ok = True
    for label, t, y, qc in build_all():
        tqc = transpile(qc, sim)
        counts = sim.run(tqc, shots=4000, seed_simulator=7).result().get_counts()
        r = success_rate(counts, y, t)
        status = 'PASS' if r >= 0.995 else 'FAIL'
        if r < 0.995:
            ok = False
        print(f'  sanity {label:8s} y={y:2d}: success={r:.4f} {status}')
    if not ok:
        print('SANITY GATE FAILED — do not submit.', file=sys.stderr)
        sys.exit(2)
    print('  sanity gate: ALL PASS')


# ---------- phase 2: hardware-target transpile accounting (no QPU) ----------

def accounting(backend):
    rows = {}
    for t, y in T_CASES:
        phi = y / 2 ** t
        full = transpile(standard_qpe(t, phi, True), backend, optimization_level=1,
                         seed_transpiler=11)
        nor = transpile(standard_qpe(t, phi, False), backend, optimization_level=1,
                        seed_transpiler=11)
        qipe = transpile(ipe(t, phi), backend, optimization_level=1, seed_transpiler=11)
        c_full, c_nor, c_ipe = twoq_count(full), twoq_count(nor), twoq_count(qipe)
        share = (c_full - c_nor) / c_full if c_full else 0.0
        rows[f't{t}'] = {'twoq_full': c_full, 'twoq_no_readout': c_nor,
                         'twoq_ipe': c_ipe, 'readout_share': round(share, 4)}
        print(f'  t={t}: 2q full={c_full} no_readout={c_nor} ipe={c_ipe} '
              f'readout_share={share:.1%}')
    return rows


# ---------- phase 3/4: support check + submit ----------

def get_backend(name):
    from qiskit_ibm_runtime import QiskitRuntimeService
    service = QiskitRuntimeService()
    return service.backend(name)


def submit(backend_name):
    backend = get_backend(backend_name)

    # Branch-C tripwire: verify dynamic-circuit support BEFORE burning QPU.
    ops = set(backend.target.operation_names)
    if 'if_else' not in ops:
        print(f'BRANCH C EVIDENCE: {backend_name} target lacks if_else '
              f'(dynamic circuits unsupported). ops={sorted(ops)}', file=sys.stderr)
        sys.exit(3)
    print(f'  backend {backend_name}: if_else supported '
          f'(reset={"reset" in ops}, measure mid-circuit assumed with if_else)')

    sanity_gate()
    acct = accounting(backend)

    from qiskit_ibm_runtime import SamplerV2
    labels, isa = [], []
    for label, t, y, qc in build_all():
        labels.append({'label': label, 't': t, 'y': y})
        isa.append(transpile(qc, backend, optimization_level=1, seed_transpiler=11))

    sampler = SamplerV2(mode=backend)
    job = sampler.run(isa, shots=SHOTS)
    rec = {'job_id': job.job_id(),
           'submitted_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
           'backend': backend_name, 'shots': SHOTS, 'pubs': labels,
           'accounting': acct, 'prereg': 'pred_c4106_001 (t=4 gap >= +5pp)'}
    # durable-progress: record the job id IMMEDIATELY (C3858)
    existing = json.loads(JOBFILE.read_text()) if JOBFILE.exists() else []
    existing.append(rec)
    JOBFILE.write_text(json.dumps(existing, indent=2) + '\n')
    print(f'  submitted job {job.job_id()} -> {JOBFILE.name}')
    return job.job_id()


# ---------- phase 5: grade ----------

def grade(job_id):
    from qiskit_ibm_runtime import QiskitRuntimeService
    service = QiskitRuntimeService()
    job = service.job(job_id)
    status = str(job.status())
    print(f'  job {job_id} status: {status}')
    if 'DONE' not in status.upper():
        print('  not done yet — try again later.')
        sys.exit(4)

    recs = json.loads(JOBFILE.read_text())
    rec = next(r for r in recs if r['job_id'] == job_id)
    res = job.result()
    out = {'meta': {'cycle_graded': 'C4106+', 'job_id': job_id,
                    'backend': rec['backend'], 'shots': rec['shots'],
                    'accounting': rec.get('accounting'),
                    'prereg': 'pred_c4106_001 (t=4 gap >= +5pp)'},
           'per_pub': {}, 'gaps': {}}
    succ = {}
    for pub_meta, pub_res in zip(rec['pubs'], res):
        data = pub_res.data
        regname = list(data.keys())[0] if hasattr(data, 'keys') else 'c'
        counts = getattr(data, regname).get_counts()
        r = success_rate(counts, pub_meta['y'], pub_meta['t'])
        succ[pub_meta['label']] = r
        out['per_pub'][pub_meta['label']] = {'y': pub_meta['y'], 't': pub_meta['t'],
                                             'success': round(r, 4)}
        print(f'  {pub_meta["label"]:8s}: exact-success = {r:.4f}')
    for t, _ in T_CASES:
        gap = (succ[f'ipe_t{t}'] - succ[f'std_t{t}']) * 100
        out['gaps'][f't{t}'] = round(gap, 2)
        print(f'  t={t}: gap = {gap:+.2f}pp')
    g4 = out['gaps']['t4']
    verdict = 'BRANCH A (gap >= +5pp: survives feedforward)' if g4 >= 5 \
        else 'BRANCH B (gap < +5pp: sim gap collapsed on hardware)'
    out['meta']['verdict_t4'] = verdict
    print(f'  PRE-REGISTERED VERDICT (t=4): {verdict}')
    RESULTFILE.write_text(json.dumps(out, indent=2) + '\n')
    print(f'  results -> {RESULTFILE.name}')


if __name__ == '__main__':
    mode = sys.argv[1] if len(sys.argv) > 1 else 'local'
    if mode == 'local':
        sanity_gate()
    elif mode == 'submit':
        submit(sys.argv[2] if len(sys.argv) > 2 else DEFAULT_BACKEND)
    elif mode == 'grade':
        grade(sys.argv[2])
    else:
        print(__doc__)
        sys.exit(1)
