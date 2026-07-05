#!/usr/bin/env python3
"""
Exp102 — Semiclassical (measured) QFT readout: 2q-gate share + noise payoff (SIM ONLY)
Ember C4105. Pre-registered: pred_c4105_001 (created BEFORE this file was written/run).

Question (from N&C Ch5 Problem 5.2 / Griffiths-Niu, pattern c4104_002):
  The terminal QFT-dagger readout of phase estimation can be replaced by
  measurement + classically-controlled 1q rotations (semiclassical QFT / Kitaev IPE)
  — ZERO two-qubit gates in readout. Exp101 (c4099_001) showed IBM window quality
  varies specifically on the 2q-coherence axis. So:
    Q1: What FRACTION of transpiled 2q gates in standard QPE is the readout stage
        (routing included) at our hardware scales (t=3..5, linear coupling, cz basis)?
    Q2: How much exact-success probability does the semiclassical variant buy under
        window-realistic 2q depolarizing noise?
  Decision relevance: whether to adopt iterative readout in our hardware experiments
  (Elder Exp100 probes, Ember counting/IAE tooling).

Design:
  - Toy eigenphase problem: U = P(2*pi*phi) on one work qubit, eigenstate |1>.
    phi = exact t-bit fractions so noiseless success must be 1.0 (sanity GATE:
    script aborts if either variant is not >=99.5% noiseless — endianness guard,
    lesson c4103 Exp99).
  - Standard QPE: t counting qubits + work, cp oracle ladder, manual inverse QFT
    (with terminal swaps), measure. Transpiled to basis [cz,rz,sx,x] on a LINE
    coupling (heavy-hex path proxy) — QFT + long-range oracle cps must route.
  - Semiclassical: Kitaev IPE, 1 ancilla + work (adjacent), classically-controlled
    feedback rotations via if_test. Readout has zero 2q gates by construction.
  - Readout 2q share := (cz_full - cz_no_readout)/cz_full, median over 5 transpiler
    seeds (routing-stochasticity control). Caveat recorded: routing interactions
    mean the diff is an attribution approximation.
  - Noise: depolarizing p2 on cz (sweep), 1q depolarizing 2e-4 on sx/x, symmetric
    1% readout error. Identical model for both variants.
  - Secondary (accounting only): quantum-counting instance — QPE(t=4) on a
    3-qubit Grover iterate (marked |101>), controlled-G repeated 2^j times
    (structure-preserving). Readout share expected MUCH smaller there.
"""
import json, math, sys, statistics
from qiskit import QuantumCircuit, transpile
from qiskit.transpiler import CouplingMap
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel, depolarizing_error, ReadoutError

BASIS = ['cz', 'rz', 'sx', 'x', 'id']
SHOTS = 4000
SEEDS = [11, 22, 33, 44, 55]
P2_SWEEP = [0.0, 0.002, 0.005, 0.01, 0.02, 0.03]
P1 = 2e-4
RO = 0.01
T_LIST = [3, 4, 5]
N_PHI = 5  # exact t-bit fractions per t


def inverse_qft(t):
    """Manual inverse QFT on t qubits, matching the forward textbook QFT with swaps."""
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
    qc.x(t)                      # eigenstate |1> of P(theta)
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
        for m in range(k):  # feedback from previously measured lower bits
            with qc.if_test((qc.clbits[m], 1)):
                qc.p(-math.pi / 2 ** (k - m), 0)
        qc.h(0)
        qc.measure(0, k)
    return qc


def make_noise(p2):
    nm = NoiseModel(basis_gates=BASIS)
    if p2 > 0:
        nm.add_all_qubit_quantum_error(depolarizing_error(p2, 2), ['cz'])
    nm.add_all_qubit_quantum_error(depolarizing_error(P1, 1), ['sx', 'x'])
    nm.add_all_qubit_readout_error(ReadoutError([[1 - RO, RO], [RO, 1 - RO]]))
    return nm


def transpile_line(qc, n_phys, seed):
    cm = CouplingMap([[i, i + 1] for i in range(n_phys - 1)])
    return transpile(qc, basis_gates=BASIS + ['reset', 'measure', 'if_else'],
                     coupling_map=cm, optimization_level=1, seed_transpiler=seed)


def cz_count(qc):
    return sum(1 for inst in qc.data if inst.operation.name == 'cz')


def success_rate(counts, y_target, t):
    tot = sum(counts.values())
    ok = counts.get(format(y_target, f'0{t}b'), 0)
    return ok / tot


def run(qc, p2, sim_seed, noiseless=False):
    sim = AerSimulator() if noiseless else AerSimulator(noise_model=make_noise(p2))
    res = sim.run(qc, shots=SHOTS, seed_simulator=sim_seed).result()
    return res.get_counts()


def phis_for(t):
    step = max(1, (2 ** t) // N_PHI)
    ys = [(1 + i * step) % 2 ** t for i in range(N_PHI)]
    ys = sorted(set(y if y != 0 else 3 for y in ys))
    return [(y, y / 2 ** t) for y in ys]


def main():
    out = {'meta': {'cycle': 4105, 'shots': SHOTS, 'basis': BASIS, 'p1': P1, 'ro': RO,
                    'p2_sweep': P2_SWEEP, 'seeds': SEEDS,
                    'prereg': 'pred_c4105_001 (t=4, p2=0.01: readout share >=50% AND IPE gap >=8pp)'},
           'toy': {}, 'counting': {}}

    for t in T_LIST:
        phis = phis_for(t)
        # ---- 2q accounting (median over transpiler seeds, phi fixed mid-range) ----
        y_acc, phi_acc = phis[len(phis) // 2]
        full_czs, nor_czs, ipe_czs = [], [], []
        for s in SEEDS:
            full_czs.append(cz_count(transpile_line(standard_qpe(t, phi_acc, True), t + 1, s)))
            nor_czs.append(cz_count(transpile_line(standard_qpe(t, phi_acc, False), t + 1, s)))
            ipe_czs.append(cz_count(transpile_line(ipe(t, phi_acc), 2, s)))
        med_full = statistics.median(full_czs)
        med_nor = statistics.median(nor_czs)
        readout_share = (med_full - med_nor) / med_full if med_full else 0.0

        # ---- noiseless sanity GATE (all phis, both variants) ----
        for (y, phi) in phis:
            qs = transpile_line(standard_qpe(t, phi, True), t + 1, SEEDS[0])
            qi = transpile_line(ipe(t, phi), 2, SEEDS[0])
            rs = success_rate(run(qs, 0.0, 7, noiseless=True), y, t)
            ri = success_rate(run(qi, 0.0, 7, noiseless=True), y, t)
            if rs < 0.995 or ri < 0.995:
                print(f'SANITY FAIL t={t} y={y}: std={rs:.3f} ipe={ri:.3f}', file=sys.stderr)
                sys.exit(2)

        # ---- noise sweep (mean over phis) ----
        sweep = []
        for p2 in P2_SWEEP:
            s_std, s_ipe = [], []
            for i, (y, phi) in enumerate(phis):
                qs = transpile_line(standard_qpe(t, phi, True), t + 1, SEEDS[0])
                qi = transpile_line(ipe(t, phi), 2, SEEDS[0])
                s_std.append(success_rate(run(qs, p2, 100 + i), y, t))
                s_ipe.append(success_rate(run(qi, p2, 200 + i), y, t))
            sweep.append({'p2': p2,
                          'std_success': round(sum(s_std) / len(s_std), 4),
                          'ipe_success': round(sum(s_ipe) / len(s_ipe), 4),
                          'gap_pp': round(100 * (sum(s_ipe) - sum(s_std)) / len(s_std), 2)})
        out['toy'][f't{t}'] = {
            'cz_full_median': med_full, 'cz_no_readout_median': med_nor,
            'cz_ipe_median': statistics.median(ipe_czs),
            'cz_full_all': full_czs, 'cz_no_readout_all': nor_czs,
            'readout_share': round(readout_share, 4), 'sweep': sweep,
            'phis_tested': [y for y, _ in phis]}
        print(f't={t}: cz full={med_full} no-readout={med_nor} ipe={statistics.median(ipe_czs)} '
              f'readout_share={readout_share:.1%}')
        for row in sweep:
            print(f'   p2={row["p2"]:<6} std={row["std_success"]:.3f} '
                  f'ipe={row["ipe_success"]:.3f} gap={row["gap_pp"]:+.1f}pp')

    # ---- secondary: quantum-counting accounting (t=4, 3-qubit Grover, marked |101>) ----
    try:
        t = 4
        n_work = 3

        def grover_iterate():
            g = QuantumCircuit(n_work, name='G')
            # oracle: phase-flip |101>  (X on the 0-bit position, then CCZ, undo)
            g.x(1)
            g.h(2); g.ccx(0, 1, 2); g.h(2)
            g.x(1)
            # diffusion
            g.h(range(n_work)); g.x(range(n_work))
            g.h(2); g.ccx(0, 1, 2); g.h(2)
            g.x(range(n_work)); g.h(range(n_work))
            return g.to_gate()

        cg = grover_iterate().control(1)

        def counting_qpe(include_readout=True):
            qc = QuantumCircuit(t + n_work, t)
            qc.h(range(t + n_work))          # counting superposition + Grover init
            for j in range(t):
                for _ in range(2 ** j):      # structure-preserving power
                    qc.append(cg, [j] + list(range(t, t + n_work)))
            if include_readout:
                qc.compose(inverse_qft(t), qubits=range(t), inplace=True)
            qc.measure(range(t), range(t))
            return qc

        fc, nc = [], []
        for s in SEEDS[:3]:
            fc.append(cz_count(transpile_line(counting_qpe(True), t + n_work, s)))
            nc.append(cz_count(transpile_line(counting_qpe(False), t + n_work, s)))
        mf, mn = statistics.median(fc), statistics.median(nc)
        out['counting'] = {'cz_full_median': mf, 'cz_no_readout_median': mn,
                           'readout_share': round((mf - mn) / mf, 4),
                           'cz_full_all': fc, 'cz_no_readout_all': nc}
        print(f'counting t=4 (3q Grover): cz full={mf} no-readout={mn} '
              f'readout_share={(mf - mn) / mf:.1%}')
    except Exception as e:
        out['counting'] = {'error': str(e)}
        print(f'counting-case accounting skipped: {e}', file=sys.stderr)

    with open('experiments/exp102_results.json', 'w') as f:
        json.dump(out, f, indent=2)
    print('wrote experiments/exp102_results.json')


if __name__ == '__main__':
    main()
