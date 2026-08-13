#!/usr/bin/env python3
"""
H14 Lock 5c executor — ghost negativity on fez p1 banks, pin IMPORTED not fitted.
Frozen: docs/h14-lock5c-ghost-third-die-external-pin-FROZEN-whisper-c5071.md (ff08706).
One code path: conventions come verbatim from experiments/exp142_robust_decoder_sim.py
(known-answer-validated on the revealed n6 rung; produced the graded FWHT decodes).
"""
import json, os, sys
import numpy as np

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', 'experiments'))
from exp142_robust_decoder_sim import (calibrate_bell_mapping, calibrate_constraint_sign,
                                       outcome_to_bits, pauli_to_bits, sp_inner)

R = 'results'
RUNGS = {
    10: ('exp142_p1_n10_qarm_bank_elder_c6577.json', 'exp142_p1_n10_qarm_blind_decode_elder_c6575.json'),
    12: ('exp142_p1_n12_qarm_bank_elder_c6577.json', 'exp142_p1_n12_qarm_blind_decode_elder_c6575.json'),
    13: ('exp142_p1_n13_qarm_bank_elder_c6577.json', 'exp142_p1_n13_qarm_blind_decode_elder_c6575.json'),
    14: ('exp142_p1_n14_qarm_bank_elder_c6577.json', 'exp142_p1_n14_qarm_blind_decode_FWHT_elder_c6575.json'),
    15: ('exp142_p1_n15_qarm_bank_elder_c6577.json', 'exp142_p1_n15_qarm_blind_decode_FWHT_whisper_c5016.json'),
}

def main():
    rng = np.random.default_rng(50713)
    mapping = calibrate_bell_mapping()
    csign = calibrate_constraint_sign(mapping)
    print('imported mapping:', mapping, 'csign:', csign)

    surviving, channel_rows, Vmats = [], [], {}
    parity, planted_prod = {}, {}
    for n, (bankf, decf) in RUNGS.items():
        bank = json.load(open(os.path.join(R, bankf)))
        dec = json.load(open(os.path.join(R, decf)))
        P_hat, rate_banked = dec['P_hat_Q'], float(dec['rate'])
        bits = [s for s in bank['raw_bitstrings'] if len(s) == 2*n]
        Q = np.array([outcome_to_bits(s, n, mapping) for s in bits], dtype=np.int8)  # (m, 2n) Weyl x|z
        Pb = pauli_to_bits(P_hat)
        ypar = P_hat.count('Y') % 2
        vals = np.array([sp_inner(q, Pb, n) for q in Q], dtype=np.int8)
        rate = float((vals == csign[ypar]).mean())
        pin_ok = abs(rate - rate_banked) < 1e-9
        print(f'n{n}: pin rate {rate:.12f} vs banked {rate_banked:.12f} -> {"PASS" if pin_ok else "FAIL"}')
        if not pin_ok: continue
        surviving.append(n)
        x, z = Q[:, :n], Q[:, n:]
        vX, vZ = (1 - 2*z).astype(np.float32), (1 - 2*x).astype(np.float32)
        vY = -vX * vZ
        Vmat = np.concatenate([vX, vY, vZ], axis=1)  # (m, 3n) channel order X..,Y..,Z..
        Vmats[n] = Vmat
        m = Vmat.mean(axis=0)
        se = np.sqrt(np.maximum(1e-12, 1 - m**2) / Vmat.shape[0])
        for k in range(3*n):
            L, j = 'XYZ'[k // n], k % n
            channel_rows.append({'n': n, 'pair': j, 'L': L, 'm': float(m[k]),
                                 'se': float(se[k]), 'z': float(m[k]/se[k])})
        singlet = (x == 1) & (z == 1)
        parity[n] = float((singlet.sum(axis=1) % 2 == 1).mean())
        supp = [i for i, p in enumerate(P_hat) if p != 'I']
        pv = np.ones(Vmat.shape[0], dtype=np.float32)
        for i in supp:
            pv *= Vmat[:, 'XYZ'.index(P_hat[i]) * n + i]
        planted_prod[n] = float(pv.mean())

    if len(surviving) < 2:
        json.dump({'verdict': 'NO-TEST', 'gate': 'pin (rate reproduction)', 'surviving': surviving},
                  open(os.path.join(R, 'h14_lock5c_verdict.json'), 'w'), indent=1)
        print('NO-TEST: <2 rungs survive the pin'); return

    zs = np.array([c['z'] for c in channel_rows])
    print(f'channels {len(zs)} · z range [{zs.min():+.2f},{zs.max():+.2f}] · negative {(zs<0).sum()}')

    # P-A': n14+n15 Bonferroni
    sub = [c for c in channel_rows if c['n'] in (14, 15)]
    from math import sqrt
    alpha = 0.01 / len(sub)
    # one-sided z threshold via bisection on erfc
    import math
    lo, hi = 2.0, 7.0
    for _ in range(60):
        mid = (lo + hi)/2
        p = 0.5 * math.erfc(mid / sqrt(2))
        if p > alpha: lo = mid
        else: hi = mid
    thr = -(lo + hi)/2
    hits = [c for c in sub if c['z'] < thr]
    print(f"P-A': {len(sub)} channels, threshold z < {thr:.2f}, hits: {[(c['n'],c['pair'],c['L'],round(c['m'],4),round(c['z'],2)) for c in hits]}")

    # P-B': sign-flip null
    S_obs = float((np.minimum(zs, 0)**2).sum())
    NSIM = 100000
    S_null = np.zeros(NSIM)
    for n in surviving:
        Vmat = Vmats[n]; N = Vmat.shape[0]
        ses = Vmat.std(axis=0, ddof=0) / np.sqrt(N)
        flips = rng.choice([-1.0, 1.0], size=(NSIM, N)).astype(np.float32)
        mm = flips @ Vmat / N
        zz = mm / np.maximum(ses, 1e-12)
        S_null += (np.minimum(zz, 0)**2).sum(axis=1)
    p_b = float((S_null >= S_obs).mean())
    print(f"P-B': S_obs {S_obs:.1f} vs null {S_null.mean():.1f}±{S_null.std():.1f} -> p = {p_b:.5f}")
    print('descriptive planted-product (ideal +1):', {k: round(v,4) for k,v in planted_prod.items()})
    print('descriptive odd-singlet-parity:', {k: round(v,4) for k,v in parity.items()})

    verdict = ('GHOST-CLASS-ANOMALY-PRESENT-ON-FEZ' if p_b < 0.01 else
               'NO-DISTRIBUTED-NEGATIVITY-ON-FEZ-AT-RESOLVED-SCALE')
    print('VERDICT (frozen rules):', verdict)
    json.dump({'verdict': verdict, 'surviving_rungs': surviving,
               'P_Aprime': {'n_channels': len(sub), 'z_thr': thr,
                            'hits': [(c['n'], c['pair'], c['L'], c['m'], c['z']) for c in hits]},
               'P_Bprime': {'S_obs': S_obs, 'null_mean': float(S_null.mean()),
                            'null_sd': float(S_null.std()), 'p': p_b, 'nsim': NSIM},
               'neg_channels': int((zs < 0).sum()), 'total_channels': int(len(zs)),
               'planted_product': planted_prod, 'parity_odd_rate': parity,
               'channels': channel_rows},
              open(os.path.join(R, 'h14_lock5c_verdict.json'), 'w'), indent=1)
    print('-> results/h14_lock5c_verdict.json')

if __name__ == '__main__':
    main()
