#!/usr/bin/env python3
"""
Exp51 Phase C: COBYLA shots=1024 — H3 test (shot-depression hypothesis)
Ember C3695 | 2026-06-13

Tests H3: COBYLA with 1024 shots (4× the 256-shot baseline) achieves escape rate ≥85%.
If confirmed: shot-count is the bottleneck, not algorithm.
If refuted: ~60% is a landscape-determined property stable across optimizers AND shot counts.

Phases A+B already complete (see exp51_results.json + exp51_results_phase_a_backup.json).
This script loads existing results, runs Phase C only, and saves merged output.

Pre-registration: experiments/exp51-preregistration.md
Finding 25: Exp50c shot-noise trajectory chaos
Finding 26: H1 REFUTED (SPSA 30% < COBYLA 60%)
"""
import sys, os, json, time
import numpy as np
from scipy.optimize import minimize

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from run_exp51_spsa_vs_cobyla import (
    ESCAPE_THRESHOLD, SEEDS, run_cobyla,
)
from run_exp46_fast import (
    EDGES_20, N_QUBITS_20,
    brute_force_max_cut,
)
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel
from qiskit_ibm_runtime.fake_provider import FakeMarrakesh

RESULTS_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..', 'results', 'exp51_results.json'
)
BACKUP_FILE = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), '..', 'results', 'exp51_results_phase_a_backup.json'
)



def load_existing_results():
    """Load existing phase A+B data from result files."""
    merged = {}

    # Load phase A from backup
    if os.path.exists(BACKUP_FILE):
        with open(BACKUP_FILE) as f:
            backup = json.load(f)
        if 'results' in backup and 'phase_a' in backup['results']:
            merged['phase_a'] = backup['results']['phase_a']
            print(f"Loaded Phase A from backup: {merged['phase_a']['escaped']}/10 = {merged['phase_a']['rate']*100:.0f}%")

    # Load phase B from main results
    if os.path.exists(RESULTS_FILE):
        with open(RESULTS_FILE) as f:
            existing = json.load(f)
        if 'results' in existing:
            if 'phase_a' in existing['results'] and 'phase_a' not in merged:
                merged['phase_a'] = existing['results']['phase_a']
                print(f"Loaded Phase A from main: {merged['phase_a']['escaped']}/10 = {merged['phase_a']['rate']*100:.0f}%")
            if 'phase_b' in existing['results']:
                merged['phase_b'] = existing['results']['phase_b']
                print(f"Loaded Phase B from main: {merged['phase_b']['escaped']}/10 = {merged['phase_b']['rate']*100:.0f}%")

    return merged


if __name__ == '__main__':
    print("=" * 65, flush=True)
    print("Exp51 Phase C: COBYLA shots=1024 — H3 test", flush=True)
    print(f"Ember C3695 | {time.strftime('%Y-%m-%d %H:%M:%S UTC', time.gmtime())}", flush=True)
    print("=" * 65, flush=True)
    print()

    # Load existing phases
    results = load_existing_results()
    print()

    backend = FakeMarrakesh()
    sim = AerSimulator(noise_model=NoiseModel.from_backend(backend))
    max_cut = brute_force_max_cut(N_QUBITS_20, EDGES_20)
    print(f"MaxCut = {max_cut}", flush=True)
    print()

    # Phase C: COBYLA, p=3, shots=1024 (H3 test)
    print("=== PHASE C: COBYLA p=3, MAX_ITER=30, shots=1024 (H3 test) ===", flush=True)
    print("    H3 thresholds: >=85% CONFIRMED strong, 75-84% CONFIRMED weak, <=74% REFUTED", flush=True)
    print("    Estimated ~2700s/seed = ~7.5h total", flush=True)
    print()
    phase_c = {}
    c_escaped = 0
    for i, seed in enumerate(SEEDS, 1):
        t0 = time.time()
        ratio = run_cobyla(sim, max_cut, p=3, seed=seed, max_iter=30, shots=1024)
        elapsed = time.time() - t0
        escaped = ratio >= ESCAPE_THRESHOLD
        status = 'ESCAPED' if escaped else 'trapped'
        if escaped:
            c_escaped += 1
        # Cross-reference Phase A for this seed
        ref_a = results.get('phase_a', {}).get('data', {}).get(seed, None)
        ref_str = f"PhaseA={ref_a:.4f}[{'E' if ref_a and ref_a >= ESCAPE_THRESHOLD else 'T'}]" if ref_a else ""
        print(f"  [C {i:02d}/10] p=3 seed={seed} iter=30 shots=1024 ... "
              f"{ratio:.4f} [{status}]  {ref_str}  {elapsed:.0f}s", flush=True)
        phase_c[seed] = ratio

    print()
    print(f"Phase C (shots=1024) escape rate: {c_escaped}/10 = {c_escaped*10}%", flush=True)
    if c_escaped >= 9:
        verdict = "H3 CONFIRMED (strong): Shot count substantially raises escape rate — shot-depression real"
    elif c_escaped >= 8:
        verdict = "H3 CONFIRMED (strong, marginal): shots=1024 raises rate above threshold"
    elif c_escaped >= 7:
        verdict = "H3 CONFIRMED (weak): Modest improvement from 4× shots"
    else:
        verdict = "H3 REFUTED: More shots don't rescue COBYLA — landscape floor is the bottleneck"
    print(f"VERDICT H3: {verdict}", flush=True)

    results['phase_c'] = {'data': phase_c, 'escaped': c_escaped, 'rate': c_escaped / 10}

    # Summary
    print()
    print("=" * 65, flush=True)
    print("EXP51 COMPLETE SUMMARY", flush=True)
    print("=" * 65, flush=True)
    if 'phase_a' in results:
        pa = results['phase_a']
        print(f"Phase A (COBYLA, p=3, 30iter, shots=256):  {pa['escaped']}/10 = {pa['rate']*100:.0f}%")
    if 'phase_b' in results:
        pb = results['phase_b']
        print(f"Phase B (SPSA, p=3, 50iter, shots=256):    {pb['escaped']}/10 = {pb['rate']*100:.0f}%  [H1 REFUTED]")
    print(f"Phase C (COBYLA, p=3, 30iter, shots=1024): {c_escaped}/10 = {c_escaped*10}%  [{verdict.split(':')[0]}]")

    # Save merged results
    output = {
        'experiment': 'Exp51',
        'source': 'Ember C3691 (script) + C3695 (Phase C)',
        'date': time.strftime('%Y-%m-%d', time.gmtime()),
        'config': {'escape_threshold': ESCAPE_THRESHOLD, 'seeds': SEEDS},
        'results': results
    }
    with open(RESULTS_FILE, 'w') as f:
        json.dump(output, f, indent=2)
    print(f"\nMerged results saved to: {RESULTS_FILE}", flush=True)
    print("Exp51 Phase C COMPLETE.", flush=True)
