#!/usr/bin/env python3
"""
Exp105 — Causal Discrimination GAME: sim-tier feasibility + transpile audit (PRE-HARDWARE GATE)
Author: Ember (DC15E) | Cycle C4116 | Whisper C4522/C4523/C4524 handoff (role split: Ember = game pre-reg)

THE GAME (Araujo et al. NJP 17, 102001 (2015), App. H — bound re-solved by Whisper C4524):
  Ordered unitary pairs (U_A, U_B) drawn from the 10-set
    G = {1, X, Y, Z, (X+Y)/r2, (X-Y)/r2, (X+Z)/r2, (X-Z)/r2, (Y+Z)/r2, (Y-Z)/r2}
  per Whisper's recovered optimal distribution q* (priors: commute 0.6165 / anticommute 0.3835).
  Alice applies U_A once, Bob applies U_B once, Charlie measures the switch control in |+/-> and
  guesses commute on '+', anticommute on '-'.
    switch (ideal): p_succ = 1.  Best causally-separable strategy: p_sep = 0.8690 (SDP, validated).
  Our hardware wins the game iff measured weighted success > 0.8690 with pre-registered significance.

THIS SCRIPT (both gating steps Whisper named, NO hardware):
  GATE (a) TRANSPILE AUDIT: every non-identity U in G is a Hermitian +/-1 reflection, so
      U = V Z Vdag  (V = eigenbasis)  =>  ctrl-U = (1 x V) . CZ . (1 x Vdag)  — ONE 2q gate,
      and CZ is native on marrakesh heavy-hex. Audit: per-circuit 2q count must equal
      2 x (#non-identity members of the pair) (each unitary appears twice: once per control branch),
      i.e. <= 4 for every game circuit — same depth class as the validated F77/exp91 apparatus.
  GATE (b) FAKEMARRAKESH FEASIBILITY: noise-model sim of all q*>0 pairs; q*-weighted success
      must stay > 0.87 (Whisper C4524 gate) against the causal bound 0.8690.
  Plus: uniform-52 and class-balanced weighted success (bounds 0.9039 / 0.9098) for the design
  trade-off table, and a definite-order control arm (expected success = commuting prior 0.6165,
  it can never see commutation — F77's null arm, game-form).

Exit: prints PASS/FAIL per gate; writes results/exp105_causal_game_feasibility.json
"""
import json
import os
import sys

import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit_aer import AerSimulator
from qiskit_aer.noise import NoiseModel
from qiskit_ibm_runtime.fake_provider import FakeMarrakesh

HERE = os.path.dirname(os.path.abspath(__file__))
QIJ_PATH = os.path.join(HERE, '..', 'results', 'causal_game_sdp_qij.json')
OUT_PATH = os.path.join(HERE, '..', 'results', 'exp105_causal_game_feasibility.json')

SHOTS = 20000
SEED = 42
CAUSAL_BOUND_QSTAR = 0.8690277398739925
SIM_GATE = 0.87          # Whisper C4524: noisy switch success under q* must stay above this
BOUND_UNIFORM = 0.9038879558085138
BOUND_BALANCED = 0.9097847651921172

# ---------------------------------------------------------------- unitaries
I2 = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], dtype=complex)
Y = np.array([[0, -1j], [1j, 0]], dtype=complex)
Z = np.array([[1, 0], [0, -1]], dtype=complex)
R2 = np.sqrt(2.0)
UNITARIES = {
    '1': I2, 'X': X, 'Y': Y, 'Z': Z,
    '(X+Y)/r2': (X + Y) / R2, '(X-Y)/r2': (X - Y) / R2,
    '(X+Z)/r2': (X + Z) / R2, '(X-Z)/r2': (X - Z) / R2,
    '(Y+Z)/r2': (Y + Z) / R2, '(Y-Z)/r2': (Y - Z) / R2,
}


def parse_pair(key):
    """'(A,B)' with A,B in UNITARIES keys; split at the depth-0 comma."""
    inner = key[1:-1]
    depth = 0
    for i, ch in enumerate(inner):
        if ch == '(':
            depth += 1
        elif ch == ')':
            depth -= 1
        elif ch == ',' and depth == 0:
            a, b = inner[:i], inner[i + 1:]
            if a not in UNITARIES or b not in UNITARIES:
                raise ValueError(f"unparsed pair {key!r} -> {a!r},{b!r}")
            return a, b
    raise ValueError(f"no top-level comma in {key!r}")


def reflection_eigenbasis(U):
    """U Hermitian with eigenvalues +1,-1: return V with U = V Z Vdag (exact)."""
    w, vecs = np.linalg.eigh(U)
    # eigh sorts ascending (-1 first); Z-order needs +1 eigenvector in column 0
    order = np.argsort(-w)
    V = vecs[:, order]
    assert np.allclose(V @ Z @ V.conj().T, U, atol=1e-12), "V Z Vdag != U"
    return V


# cache eigenbases; also validates every non-identity member is a +/-1 reflection
EIGBASIS = {name: reflection_eigenbasis(U) for name, U in UNITARIES.items() if name != '1'}


def apply_ctrl_unitary(qc, name, ctrl, tgt, ctrl_state):
    """ctrl-U with U = V Z Vdag: local Vdag on tgt, CZ, local V. Identity: no-op.
    ctrl_state=0 realized by X-sandwich on the control (exp91 template)."""
    if name == '1':
        return
    V = EIGBASIS[name]
    if ctrl_state == 0:
        qc.x(ctrl)
    qc.unitary(V.conj().T, [tgt], label=f'Vdag[{name}]')
    qc.cz(ctrl, tgt)
    qc.unitary(V, [tgt], label=f'V[{name}]')
    if ctrl_state == 0:
        qc.x(ctrl)


def build_game_circuit(a_name, b_name, definite=False):
    """exp91 switch template, generalized to any pair from G. control=q0, target=q1."""
    qc = QuantumCircuit(2, 1)
    qc.h(0)
    if not definite:
        apply_ctrl_unitary(qc, a_name, 0, 1, 0)   # A if c==0 (first for c=0)
        apply_ctrl_unitary(qc, b_name, 0, 1, 1)   # B if c==1 (first for c=1)
        qc.barrier()
        apply_ctrl_unitary(qc, b_name, 0, 1, 0)   # B if c==0 (second for c=0)
        apply_ctrl_unitary(qc, a_name, 0, 1, 1)   # A if c==1 (second for c=1)
    else:
        # fixed order A then B on target, control spectator (F77 null arm)
        if a_name != '1':
            qc.unitary(UNITARIES[a_name], [1], label=a_name)
        if b_name != '1':
            qc.unitary(UNITARIES[b_name], [1], label=b_name)
    qc.barrier()
    qc.h(0)
    qc.measure(0, 0)
    return qc


def commutes(a_name, b_name):
    A, B = UNITARIES[a_name], UNITARIES[b_name]
    C = A @ B - B @ A
    AC = A @ B + B @ A
    if np.allclose(C, 0, atol=1e-12):
        return True
    assert np.allclose(AC, 0, atol=1e-12), f"{a_name},{b_name} neither commutes nor anticommutes"
    return False


def p_plus(counts, shots):
    """P(control measured '+') after the readout H (bit 0)."""
    return counts.get('0', 0) / shots


def main():
    print("=" * 78)
    print("Exp105 — Causal Game sim-tier feasibility (Ember C4116, Whisper C4524 handoff)")
    print("=" * 78)

    with open(QIJ_PATH) as f:
        qij = json.load(f)
    qstar = {}
    for key, w in qij['q_star_commuting'].items():
        qstar[key] = (float(w), True)
    for key, w in qij['q_star_anticommuting'].items():
        qstar[key] = (float(w), False)

    # verify pair classes against our own matrices + q* normalization
    pairs = {}
    for key, (w, is_comm) in qstar.items():
        a, b = parse_pair(key)
        assert commutes(a, b) == is_comm, f"class mismatch for {key}"
        pairs[key] = {'A': a, 'B': b, 'q': w, 'commuting': is_comm}
    all_names = sorted(UNITARIES.keys())
    all_valid = []
    for a in all_names:
        for b in all_names:
            A, B = UNITARIES[a], UNITARIES[b]
            if np.allclose(A @ B - B @ A, 0, atol=1e-12) or np.allclose(A @ B + B @ A, 0, atol=1e-12):
                all_valid.append((a, b))
    qsum = sum(w for w, _ in qstar.values())
    print(f"q* pairs: {len(pairs)} (sum {qsum:.6f}) | all valid ordered pairs: {len(all_valid)}")
    assert abs(qsum - 1.0) < 1e-4, "q* does not normalize"
    assert len(all_valid) == 52, "expected 52 valid ordered pairs"

    # make sure every valid pair has a circuit (uniform-52 needs the (1,1) pair too)
    for a, b in all_valid:
        key = f"({a},{b})"
        if key not in pairs:
            pairs[key] = {'A': a, 'B': b, 'q': 0.0,
                          'commuting': commutes(a, b)}

    fake = FakeMarrakesh()
    nm = NoiseModel.from_backend(fake)
    cmap = fake.coupling_map
    bgates = nm.basis_gates
    ideal = AerSimulator(seed_simulator=SEED)
    noisy = AerSimulator(noise_model=nm, seed_simulator=SEED)

    # ------------------------------------------------ GATE (a): transpile audit
    print("\n--- GATE (a): transpile audit (FakeMarrakesh coupling map + basis, exp91 flow) ---")
    audit_rows = []
    audit_pass = True
    tqcs = {}
    for key, info in sorted(pairs.items()):
        qc = build_game_circuit(info['A'], info['B'])
        tqc = transpile(qc, coupling_map=cmap, basis_gates=bgates,
                        optimization_level=1, seed_transpiler=SEED)
        twoq = sum(1 for inst in tqc.data
                   if inst.operation.num_qubits == 2
                   and inst.operation.name not in ('barrier',))
        n_nonid = (info['A'] != '1') + (info['B'] != '1')
        expected = 2 * n_nonid
        ok = twoq <= max(expected, 0) and twoq <= 4
        audit_pass &= ok
        tqcs[key] = tqc
        audit_rows.append({'pair': key, 'twoq': twoq, 'expected_max': expected,
                           'depth': tqc.depth(), 'ok': bool(ok)})
    worst = max(audit_rows, key=lambda r: r['twoq'])
    print(f"  circuits: {len(audit_rows)} | max 2q count: {worst['twoq']} ({worst['pair']}) | "
          f"all within 2-per-controlled-U and <=4: {audit_pass}")
    by_class = {}
    for r in audit_rows:
        by_class.setdefault(r['twoq'], 0)
        by_class[r['twoq']] += 1
    print(f"  2q-count histogram: {dict(sorted(by_class.items()))}")

    # ------------------------------------------------ GATE (b): noisy feasibility
    print("\n--- GATE (b): FakeMarrakesh noise-model sim, all 52 pairs, "
          f"{SHOTS} shots each ---")
    per_pair = {}
    for key, info in sorted(pairs.items()):
        # ideal (sanity: every pair should give p+ ~ 1 for commuting, ~0 for anti)
        qi = transpile(build_game_circuit(info['A'], info['B']), ideal,
                       seed_transpiler=SEED)
        ci = ideal.run(qi, shots=4000).result().get_counts()
        pi = p_plus(ci, 4000)
        # noisy on the routed circuit
        cn = noisy.run(tqcs[key], shots=SHOTS).result().get_counts()
        pn = p_plus(cn, SHOTS)
        succ_ideal = pi if info['commuting'] else 1.0 - pi
        succ_noisy = pn if info['commuting'] else 1.0 - pn
        per_pair[key] = {**{k: info[k] for k in ('A', 'B', 'q', 'commuting')},
                         'p_plus_ideal': pi, 'p_plus_noisy': pn,
                         'succ_ideal': succ_ideal, 'succ_noisy': succ_noisy}
        flag = '' if succ_ideal > 0.98 else '  <-- IDEAL NOT ~1, CHECK'
        if flag:
            print(f"  {key:28s} ideal succ {succ_ideal:.4f}{flag}")

    def weighted(dist):
        s = sum(w * per_pair[k]['succ_noisy'] for k, w in dist.items())
        se = np.sqrt(sum((w ** 2) * per_pair[k]['succ_noisy'] * (1 - per_pair[k]['succ_noisy']) / SHOTS
                         for k, w in dist.items()))
        return s, se

    dist_qstar = {k: v['q'] for k, v in pairs.items() if v['q'] > 0}
    dist_unif = {f"({a},{b})": 1.0 / 52 for a, b in all_valid}
    n_comm = sum(1 for a, b in all_valid if commutes(a, b))
    dist_bal = {}
    for a, b in all_valid:
        c = commutes(a, b)
        dist_bal[f"({a},{b})"] = 0.5 / n_comm if c else 0.5 / (52 - n_comm)

    s_qstar, se_qstar = weighted(dist_qstar)
    s_unif, se_unif = weighted(dist_unif)
    s_bal, se_bal = weighted(dist_bal)
    ideal_qstar = sum(w * per_pair[k]['succ_ideal'] for k, w in dist_qstar.items())

    # definite-order null arm under q*
    s_def = 0.0
    for key, w in dist_qstar.items():
        info = pairs[key]
        qd = build_game_circuit(info['A'], info['B'], definite=True)
        td = transpile(qd, coupling_map=cmap, basis_gates=bgates,
                       optimization_level=1, seed_transpiler=SEED)
        cd = noisy.run(td, shots=4000).result().get_counts()
        pd = p_plus(cd, 4000)
        s_def += w * (pd if info['commuting'] else 1.0 - pd)

    gate_b = s_qstar > SIM_GATE
    print(f"\n  ideal switch success under q*:      {ideal_qstar:.4f}  (theory: 1.0)")
    print(f"  NOISY success under q*:             {s_qstar:.4f} +/- {se_qstar:.4f}"
          f"   vs causal bound {CAUSAL_BOUND_QSTAR:.4f}  vs sim gate {SIM_GATE}")
    print(f"  NOISY success, uniform-52:          {s_unif:.4f} +/- {se_unif:.4f}   vs bound {BOUND_UNIFORM:.4f}")
    print(f"  NOISY success, class-balanced:      {s_bal:.4f} +/- {se_bal:.4f}   vs bound {BOUND_BALANCED:.4f}")
    print(f"  definite-order null arm under q*:   {s_def:.4f}  (expected ~= commuting prior 0.6165)")

    print("\n" + "=" * 78)
    print(f"GATE (a) transpile audit:  {'PASS' if audit_pass else 'FAIL'}"
          f"  (max 2q {worst['twoq']}, all <= 2 per controlled-U)")
    print(f"GATE (b) sim feasibility:  {'PASS' if gate_b else 'FAIL'}"
          f"  (q* success {s_qstar:.4f} {'>' if gate_b else '<='} {SIM_GATE})")
    margins = {
        'qstar': s_qstar - CAUSAL_BOUND_QSTAR,
        'uniform': s_unif - BOUND_UNIFORM,
        'balanced': s_bal - BOUND_BALANCED,
    }
    print(f"sim margins over causal bounds: q* {margins['qstar']:+.4f} | "
          f"uniform {margins['uniform']:+.4f} | balanced {margins['balanced']:+.4f}")
    verdict = audit_pass and gate_b
    print(f"VERDICT: {'PASS — proceed to pre-registration' if verdict else 'FAIL — report mechanism, do not submit'}")

    out = {
        'experiment': 'exp105_causal_game_feasibility',
        'cycle': 4116, 'author': 'ember',
        'shots': SHOTS, 'seed': SEED,
        'gate_a_transpile_audit': {'pass': bool(audit_pass),
                                   'max_twoq': worst['twoq'],
                                   'twoq_histogram': by_class,
                                   'rows': audit_rows},
        'gate_b_sim_feasibility': {'pass': bool(gate_b), 'sim_gate': SIM_GATE,
                                   'success_qstar': s_qstar, 'se_qstar': se_qstar,
                                   'success_qstar_ideal': ideal_qstar,
                                   'success_uniform52': s_unif, 'se_uniform52': se_unif,
                                   'success_class_balanced': s_bal, 'se_class_balanced': se_bal,
                                   'definite_null_arm_qstar': s_def,
                                   'margins_over_bounds': margins,
                                   'bounds': {'qstar': CAUSAL_BOUND_QSTAR,
                                              'uniform52': BOUND_UNIFORM,
                                              'class_balanced': BOUND_BALANCED}},
        'per_pair': per_pair,
        'verdict_pass': bool(verdict),
    }
    with open(OUT_PATH, 'w') as f:
        json.dump(out, f, indent=1)
    print(f"\nresults -> {os.path.relpath(OUT_PATH, os.path.join(HERE, '..'))}")
    return 0 if verdict else 1


if __name__ == '__main__':
    sys.exit(main())
