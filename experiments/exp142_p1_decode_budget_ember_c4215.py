#!/usr/bin/env python3
"""P1 decode-BUDGET check (Ember C4215) — the $0 pre-seal precondition that BLOCKS the spend.

Advisor-flagged gap: G3 verified the Q constraint-rate SURVIVES on-device (0.846≫0.5), but NOT that
the decoder RESOLVES the planted P from BQ noisy Bell samples at that rate — different quantities, and
with 4ⁿ−1 all-Paulis candidates the copies-to-resolve could sit in the truncation tail (exp142b
catch#7). BQ is frozen (C4746); if 90 is thin at the degraded α=0.95 on-device rate, that needs court
attention — far cheaper pre-seal than after a wasted flight. This is the seat-that-spends' check.

METHOD (faithful, $0, no QPU): for a planted PUBLIC P, generate BQ two-copy Bell samples via the
ibm_fez NOISE MODEL on the real quantum_template + the α=0.95 shot-ensemble prep (captures BOTH the
α² signal AND readout attenuation), decode over the FULL all-Paulis∖{I} candidate set (4ⁿ−1), and
report the smallest m at which the planted P is the UNIQUE argmax — vs BQ. PASS iff Q resolves with
headroom (m_resolve ≤ BQ and comfortably below it) at all rungs.
"""
import argparse, os, sys, itertools
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
import exp142_flight_kit as K
import exp142_robust_decoder_sim as G2
from exp142_p1_prep_confirm_ember_c4215 import prep_angles, ALPHA


def all_paulis_matrix(n):
    """(4ⁿ−1, 2n) symplectic matrix of ALL Paulis∖{I} + ypar (Y-count parity). I-sites -> (0,0)."""
    cands = ["".join(c) for c in itertools.product("IXYZ", repeat=n) if c.count("I") < n]
    M = np.zeros((len(cands), 2 * n), dtype=np.int8)
    ypar = np.zeros(len(cands), dtype=np.int8)
    tab = {"I": (0, 0), "X": (1, 0), "Y": (1, 1), "Z": (0, 1)}
    for k, P in enumerate(cands):
        for i, p in enumerate(P):
            x, z = tab[p]; M[k, i], M[k, n + i] = x, z
        ypar[k] = P.count("Y") % 2
    return cands, M, ypar


def gen_bell_Q(n, P, n_samples, sampler, mapping):
    """n_samples degraded two-copy Bell Q's (2n-bit) via the noise sampler on quantum_template."""
    qc, params = K.quantum_template(n)
    rng = np.random.default_rng(abs(hash(P)) % (2**32))
    rows = []
    for _ in range(n_samples):
        t1, p1 = prep_angles(n, P, rng); t2, p2 = prep_angles(n, P, rng)
        rows.append(list(t1) + list(t2) + list(p1) + list(p2))
    pr = sampler.run([(qc, K.named_rows(params, np.array(rows)), 1)]).result()[0]
    Qs = []
    for i in range(n_samples):
        bitstr = next(iter(pr.data.c[i].get_counts()))
        Qs.append(G2.outcome_to_bits(bitstr, n, mapping))
    return np.array(Qs)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true")
    ap.add_argument("--backend", default="ibm_fez")
    ap.add_argument("--trials", type=int, default=6)
    args = ap.parse_args()
    if not args.check:
        print("use --check ($0 decode-budget on the noise model)"); return 0

    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_aer import AerSimulator
    from qiskit_aer.noise import NoiseModel
    from qiskit_aer.primitives import SamplerV2 as AerSampler
    svc = _get_ibm_service(); backend = svc.backend(args.backend)
    nm = NoiseModel.from_backend(backend)
    sampler = AerSampler(options={"backend_options": {"noise_model": nm}})
    mapping = G2.calibrate_bell_mapping(); csign = G2.calibrate_constraint_sign(mapping)
    print(f"P1 DECODE-BUDGET on {backend.name} noise model (α={ALPHA}, all-Paulis 4ⁿ−1 candidates, "
          f"{args.trials} planted-P trials/rung):\n")

    all_ok = True
    for n in (4, 6, 8):
        BQ = K.BQ[n]
        cands, M, ypar = all_paulis_matrix(n)
        grid = sorted(set(list(range(4, min(BQ, 40) + 1, 2)) + list(range(40, BQ + 1, 5))))
        rng = np.random.default_rng(4215 + n)
        m_resolves, rates = [], []
        for _ in range(args.trials):
            P = cands[rng.integers(0, len(cands))]        # planted all-Paulis P (public)
            idx = cands.index(P)
            Qs = gen_bell_Q(n, P, BQ, sampler, mapping)
            # sanity: on-device constraint-rate for the planted P
            want = csign[P.count("Y") % 2]
            Pb = M[idx]
            rate = float(np.mean([(int(G2.sp_inner(Q, Pb, n)) == want) for Q in Qs]))
            rates.append(rate)
            curve = G2.decode_success_curve(Qs, idx, M, ypar, csign, n, grid)
            solved = [m for m, s in curve.items() if s == 1]
            # smallest m that is solved AND stays solved for all larger grid points (sustained)
            m_res = None
            for i, m in enumerate(sorted(curve)):
                if all(curve[mm] == 1 for mm in sorted(curve) if mm >= m):
                    m_res = m; break
            m_resolves.append(m_res if m_res is not None else BQ + 1)
        med_rate = float(np.median(rates))
        resolved = [m for m in m_resolves if m <= BQ]
        worst = max(m_resolves)
        frac_ok = len(resolved) / len(m_resolves)
        headroom = BQ - (max(resolved) if resolved else BQ)
        ok = frac_ok == 1.0 and worst <= BQ * 0.7          # all trials resolve, with >=30% headroom
        all_ok &= ok
        print(f"  n={n}: BQ={BQ}  on-device constraint-rate~{med_rate:.3f}  "
              f"m_resolve: median={int(np.median(m_resolves))} worst={worst}  "
              f"({len(resolved)}/{len(m_resolves)} trials resolve ≤BQ, headroom {headroom}) "
              f"-> {'PASS' if ok else 'THIN — court attention (BQ frozen C4746)'}")
    print(f"\nDECODE-BUDGET: {'PASS — Q resolves within BQ with headroom at the degraded rate, all rungs. '
          'Flight will produce an executed win.' if all_ok else 'BLOCK — BQ may be thin; surface pre-seal.'}")
    return 0 if all_ok else 1


if __name__ == "__main__":
    sys.exit(main())
