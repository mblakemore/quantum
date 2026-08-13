#!/usr/bin/env python3
"""
H14 Lock 5b executor — state-independent cross-copy negativity on fez p1 Bell banks.
Frozen: docs/h14-lock5b-ghost-third-die-negativity-protocol-FROZEN-whisper-c5071.md (065939f).

P-B' null implemented as per-shot Rademacher sign-flips (the freeze's "its null by simulation"):
preserves within-shot cross-channel dependence exactly while enforcing the m=0 boundary.
"""
import json, os, itertools
import numpy as np

R = 'results'
RUNGS = {
    10: ('exp142_p1_n10_qarm_bank_elder_c6577.json', 'exp142_p1_n10_qarm_flight_manifest.json'),
    12: ('exp142_p1_n12_qarm_bank_elder_c6577.json', 'exp142_p1_ceiling_flight_n12_manifest.json'),
    13: ('exp142_p1_n13_qarm_bank_elder_c6577.json', 'exp142_p1_ceiling_flight_n13_manifest.json'),
    14: ('exp142_p1_n14_qarm_bank_elder_c6577.json', 'exp142_p1_ceiling_flight_n14_manifest.json'),
    15: ('exp142_p1_n15_qarm_bank_elder_c6577.json', 'exp142_p1_ceiling_flight_n15_manifest.json'),
}
MAPPINGS = list(itertools.product([False, True], ['interleave', 'block'], [False, True]))

def load_rung(n):
    bank, man = RUNGS[n]
    b = json.load(open(os.path.join(R, bank)))
    m = json.load(open(os.path.join(R, man)))
    bits = b['raw_bitstrings']
    ok = [s for s in bits if len(s) == 2*n]
    if len(ok) != len(bits):
        print(f'  n{n}: WARNING {len(bits)-len(ok)} rows wrong width (kept {len(ok)})')
    arr = np.array([[int(c) for c in s] for s in ok], dtype=np.int8)
    return arr, m['bell_pairs']

def pair_bits(arr, n, mapping):
    rev, layout, roleswap = mapping
    a = arr[:, ::-1] if rev else arr
    if layout == 'interleave':
        p, q = a[:, 0::2], a[:, 1::2]
    else:
        p, q = a[:, :n], a[:, n:]
    if roleswap: p, q = q, p
    return p, q  # (shots, n) phase bits, parity bits

def letter_vals(p, q):
    vx = 1 - 2*p           # (-1)^phase
    vz = 1 - 2*q           # (-1)^parity
    vy = -vx * vz
    return {'X': vx, 'Y': vy, 'Z': vz}

def main():
    rng = np.random.default_rng(50712)
    data = {}
    for n in RUNGS:
        try:
            arr, pairs = load_rung(n)
            data[n] = (arr, pairs)
            print(f'n{n}: {arr.shape[0]} rows x {arr.shape[1]} bits, {len(pairs)} pairs')
        except FileNotFoundError as e:
            print(f'n{n}: MISSING {e}')
    if not data: print('NO-TEST: no banks'); return

    # --- mapping pin: total power sum(m^2), argmax with >=2x margin, per rung, consistent ---
    pin = {}
    for n, (arr, _) in data.items():
        powers = []
        for mp in MAPPINGS:
            p, q = pair_bits(arr, n, mp)
            V = letter_vals(p, q)
            tot = sum(float((V[L].mean(axis=0)**2).sum()) for L in 'XYZ')
            powers.append(tot)
        order = np.argsort(powers)[::-1]
        best, second = powers[order[0]], powers[order[1]]
        pin[n] = (MAPPINGS[order[0]], best, second, best/max(second, 1e-12))
        print(f'  pin n{n}: best {MAPPINGS[order[0]]} power {best:.4f} vs runner-up {second:.4f} (margin {best/max(second,1e-12):.2f}x)')
    chosen = {n: pin[n][0] for n in pin}
    margins_ok = all(pin[n][3] >= 2.0 for n in pin)
    consistent = len(set(map(tuple, [(c[0], c[1], c[2]) for c in chosen.values()]))) == 1
    print(f'PIN: margin>=2x all rungs: {margins_ok} · consistent mapping: {consistent}')
    if not (margins_ok and consistent):
        json.dump({'verdict': 'NO-TEST', 'gate': 'mapping pin',
                   'pin': {str(n): [list(map(str, pin[n][0])), pin[n][1], pin[n][2], pin[n][3]] for n in pin}},
                  open(os.path.join(R, 'h14_lock5b_verdict.json'), 'w'), indent=1)
        print('NO-TEST: mapping pin failed'); return
    mapping = list(chosen.values())[0]

    # --- channels: per (rung, pair, letter) means, se, z ---
    channels = []   # (n, pair_idx, L, m, se, z, shots)
    Vs = {}         # per rung letter value arrays for sign-flip null
    for n, (arr, pairs) in data.items():
        p, q = pair_bits(arr, n, mapping)
        V = letter_vals(p, q)
        Vs[n] = V
        N = arr.shape[0]
        for L in 'XYZ':
            m = V[L].mean(axis=0)
            se = np.sqrt(np.maximum(1e-12, 1 - m**2) / N)
            for j in range(len(pairs)):
                channels.append((n, j, L, float(m[j]), float(se[j]), float(m[j]/se[j]), N))
    z = np.array([c[5] for c in channels])
    print(f'channels: {len(z)} · z range [{z.min():+.2f}, {z.max():+.2f}] · negative channels: {(z<0).sum()}')

    # --- P-A': per-channel negativity, n14+n15, Bonferroni ---
    import math
    sub = [c for c in channels if c[0] in (14, 15)]
    alpha_bonf = 0.01 / len(sub)
    thr = -abs(np.sqrt(2) * erfinv_approx(1 - 2*alpha_bonf))
    hits = [c for c in sub if c[5] < thr]
    print(f"P-A': {len(sub)} channels, z threshold {thr:.2f}, hits: {[(c[0],c[1],c[2],round(c[3],4)) for c in hits]}")

    # --- P-B': S = sum min(z,0)^2, sign-flip null (per-shot Rademacher, per rung) ---
    S_obs = float((np.minimum(z, 0)**2).sum())
    NSIM = 100000
    S_null = np.zeros(NSIM)
    for n, (arr, pairs) in data.items():
        N = arr.shape[0]
        V = Vs[n]
        Vmat = np.concatenate([V[L] for L in 'XYZ'], axis=1).astype(np.float32)  # (N, 3n)
        ses = Vmat.std(axis=0, ddof=0) / np.sqrt(N)
        flips = rng.choice([-1.0, 1.0], size=(NSIM, N)).astype(np.float32)
        mm = flips @ Vmat / N                        # (NSIM, 3n) null means
        zz = mm / np.maximum(ses, 1e-12)
        S_null += (np.minimum(zz, 0)**2).sum(axis=1)
    p_b = float((S_null >= S_obs).mean())
    print(f"P-B': S_obs {S_obs:.1f} vs null mean {S_null.mean():.1f} sd {S_null.std():.1f} -> p = {p_b:.5f}")

    # --- descriptive: odd-singlet-parity rate per rung ---
    parity = {}
    for n, (arr, pairs) in data.items():
        p, q = pair_bits(arr, n, mapping)
        singlet = (p == 1) & (q == 1)
        odd = (singlet.sum(axis=1) % 2 == 1).mean()
        parity[n] = float(odd)
    print('descriptive odd-singlet-parity per rung:', {k: round(v,4) for k,v in parity.items()})

    verdict = ('GHOST-CLASS-ANOMALY-PRESENT-ON-FEZ' if p_b < 0.01 else
               'NO-DISTRIBUTED-NEGATIVITY-ON-FEZ-AT-RESOLVED-SCALE')
    print('VERDICT (frozen rules):', verdict)
    json.dump({'verdict': verdict, 'mapping': [str(x) for x in mapping],
               'pin': {str(n): pin[n][3] for n in pin},
               'P_Aprime': {'n_channels': len(sub), 'z_thr': thr,
                            'hits': [(c[0], c[1], c[2], c[3], c[5]) for c in hits]},
               'P_Bprime': {'S_obs': S_obs, 'null_mean': float(S_null.mean()),
                            'null_sd': float(S_null.std()), 'p': p_b, 'nsim': NSIM},
               'neg_channels': int((z < 0).sum()), 'total_channels': len(z),
               'parity_odd_rate': parity,
               'channels': [{'n': c[0], 'pair': c[1], 'L': c[2], 'm': c[3], 'se': c[4], 'z': c[5]} for c in channels]},
              open(os.path.join(R, 'h14_lock5b_verdict.json'), 'w'), indent=1)
    print('-> results/h14_lock5b_verdict.json')

def erfinv_approx(x):
    a = 0.147
    ln = np.log(1 - x*x)
    t1 = 2/(np.pi*a) + ln/2
    return np.sign(x) * np.sqrt(np.sqrt(t1**2 - ln/a) - t1)

if __name__ == '__main__':
    main()
