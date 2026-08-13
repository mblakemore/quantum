#!/usr/bin/env python3
"""
H14 Lock 5 executor — THE GHOST ON A SECOND DIE (Whisper C5071).
Frozen protocol: docs/h14-lock5-ghost-second-die-protocol-FROZEN-whisper-c5071.md (quantum@72edcac).

Decodes ONLY the wave1-7 kingston `cal` pubs from the stage-0 rescue records.
Pin -> gates -> P-A / P-B / P-C, verdict per the frozen rules. One code path.
"""
import json, glob, os, sys, itertools, random, math

R = 'results'
WAVE_MANIFESTS = {
    (1, 4): 'exp142_wave1_n4_manifest.json', (1, 6): 'exp142_wave1_n6_manifest.json',
    (1, 8): 'exp142_wave1_n8_manifest.json', (1, 10): 'exp142_wave1_n10_manifest.json',
    (2, 4): 'exp142_wave2_n4_manifest.json', (2, 6): 'exp142_wave2_n6_manifest.json',
    (2, 8): 'exp142_wave2_n8_manifest_aug_elder.json', (2, 10): 'exp142_wave2_n10_manifest_aug_elder.json',
    (3, 4): 'exp142_wave3_n4_manifest_aug_elder.json', (3, 6): 'exp142_wave3_n6_manifest_aug_elder.json',
    (3, 8): 'exp142_wave3_n8_manifest_ember.json', (3, 10): 'exp142_wave3_n10_manifest_ember.json',
    (4, 8): 'exp142_wave4_n8_manifest_ember.json', (4, 10): 'exp142_wave4_n10_manifest_aug_elder.json',
    (5, 10): 'exp142_wave5_n10_manifest_ember.json',
    (6, 10): 'exp142_wave6_n10_manifest_ember.json',
    (7, 10): 'exp142_wave7_n10_manifest_aug_elder.json',
}

# Bell eigenvalue tables: outcome bits (p, q) per pair; roles resolved by the pin.
# v[L](phase_bit, parity_bit): Phi+ (0,0): XX+1 ZZ+1 YY-1 | Phi- (1,0): XX-1 ZZ+1 YY+1
#                              Psi+ (0,1): XX+1 ZZ-1 YY+1 | Psi- (1,1): XX-1 ZZ-1 YY-1
def v_letter(L, phase, parity):
    if L == 'X': return -1 if phase else 1
    if L == 'Z': return -1 if parity else 1
    return -(-1 if phase else 1) * (-1 if parity else 1)  # Y = -(XX*ZZ)

def load_family():
    """Load rescued cal-pub shot data joined to manifests. Returns per-job records."""
    fam = []
    for (w, n), mf in sorted(WAVE_MANIFESTS.items()):
        try: man = json.load(open(os.path.join(R, mf)))
        except Exception: continue
        jid = man['job_id']
        rescues = glob.glob(os.path.join(R, f'h14_lock5_rescue_*{jid}*.json'))
        if not rescues: continue
        resc = json.load(open(rescues[0]))
        cal_specs = [(i, p) for i, p in enumerate(man['pubs']) if p.get('kind') == 'cal']
        pubs_by_idx = {p['pub_index']: p['data'] for p in resc['pubs']}
        cals = []
        for i, spec in cal_specs:
            data = pubs_by_idx.get(i)
            if not data: continue
            field = next((v for v in data.values() if isinstance(v, list)), None)
            if field: cals.append({'pauli': spec['pauli'], 'b': spec['b'], 'bits': field})
        if cals:
            fam.append({'wave': w, 'n': n, 'job_id': jid,
                        'bell_pairs': man['bell_pairs'], 'cals': cals})
    return fam

def decode_shot(bits, n, mapping):
    """bits: measured 2n-bit string. mapping: (reverse, layout, roleswap).
    Returns list of (phase, parity) per logical pair 0..n-1."""
    rev, layout, roleswap = mapping
    s = bits[::-1] if rev else bits
    out = []
    for j in range(n):
        if layout == 'interleave': a, b = s[2*j], s[2*j+1]
        else:                      a, b = s[j], s[n+j]
        p, q = (int(a), int(b))
        if roleswap: p, q = q, p
        out.append((p, q))
    return out

def channel_means(fam, mapping):
    """Per (physical pair, letter): pooled sum/count of v over all cal shots.
    planted letter channel -> key 'C'; off letters keyed by their letter."""
    acc = {}
    for job in fam:
        n, pairs = job['n'], job['bell_pairs']
        for cal in job['cals']:
            pl, shots = cal['pauli'], cal['bits']
            for bits in shots:
                if len(bits) != 2*n: continue
                dec = decode_shot(bits, n, mapping)
                for j in range(n):
                    pq = tuple(pairs[j]); P = pl[j]
                    for L in 'XYZ':
                        val = v_letter(L, *dec[j])
                        key = (pq, 'C') if L == P else (pq, L)
                        s0, c0 = acc.get(key, (0, 0)); acc[key] = (s0 + val, c0 + 1)
    return acc

def main():
    fam = load_family()
    jobs_present = [(j['wave'], j['n']) for j in fam]
    print(f'jobs with rescued cal data: {len(fam)} -> {jobs_present}')
    if not fam:
        print('NO-TEST: no rescued cal data'); return

    # --- PIN step 1: synthesized known-answer (ideal Bell stats for |s>|s>) ---
    # For planted P with any sign: ideal per-pair distribution over (phase,parity):
    # P=Z: outcomes Phi+/Phi- equally (ZZ=+1): (0,0),(1,0) each 1/2
    # P=X: XX=+1 -> Phi+ (0,0), Psi+ (0,1) each 1/2
    # P=Y: YY=+1 -> Phi- (1,0), Psi+ (0,1) each 1/2
    ideal = {'Z': [(0,0),(1,0)], 'X': [(0,0),(0,1)], 'Y': [(1,0),(0,1)]}
    synth_ok = True
    for P in 'XYZ':
        cs = [v_letter(P, *o) for o in ideal[P]]
        offs = [[v_letter(L, *o) for o in ideal[P]] for L in 'XYZ' if L != P]
        if not all(c == 1 for c in cs): synth_ok = False
        if not all(sum(o) == 0 for o in offs): synth_ok = False
    print(f'PIN-1 synthesized ideal: {"PASS" if synth_ok else "FAIL"}')
    if not synth_ok: print('NO-TEST: synthesized pin failed'); return

    # --- PIN step 2: resolve discrete mapping by planted-channel c (known-answer fit) ---
    best = None
    for mapping in itertools.product([False, True], ['interleave', 'block'], [False, True]):
        acc = channel_means(fam, mapping)
        cs = [s/c for (pq, k), (s, c) in acc.items() if k == 'C' and c > 0]
        if not cs: continue
        cs.sort(); med = cs[len(cs)//2]
        if best is None or med > best[1]: best = (mapping, med)
    mapping, med_c = best
    print(f'PIN-2 mapping resolved: reverse={mapping[0]} layout={mapping[1]} roleswap={mapping[2]} -> median c = {med_c:+.4f}')

    acc = channel_means(fam, mapping)
    # per-job median c gate
    per_job_ok, worst = True, 1.0
    for job in fam:
        jacc = channel_means([job], mapping)
        cs = sorted(s/c for (pq, k), (s, c) in jacc.items() if k == 'C' and c > 0)
        if not cs: continue
        m = cs[len(cs)//2]; worst = min(worst, m)
        if m < 0.5:
            per_job_ok = False
            print(f'  gate FAIL: wave{job["wave"]} n{job["n"]} median c = {m:+.3f}')
    print(f'PIN-2 per-job gate (median c >= +0.5 all jobs): {"PASS" if per_job_ok else "FAIL"} (worst {worst:+.3f})')
    if not per_job_ok:
        print('NO-TEST: cal-identity gate failed — instrument far from its own cal plant')
        json.dump({'verdict': 'NO-TEST', 'gate': 'cal-identity', 'worst_median_c': worst,
                   'mapping': list(mapping)}, open(os.path.join(R, 'h14_lock5_verdict.json'), 'w'), indent=1)
        return

    # --- assemble per-unique-pair table ---
    pairs = sorted(set(pq for (pq, k) in acc))
    table = []
    for pq in pairs:
        sC, nC = acc.get((pq, 'C'), (0, 0))
        if nC == 0: continue
        comps, ses, ns = [], [], []
        for L in 'XYZ':
            if (pq, L) in acc:
                s0, c0 = acc[(pq, L)]
                m = s0 / c0
                comps.append(m); ses.append(math.sqrt(max(1e-12, 1 - m*m) / c0)); ns.append(c0)
        c_val = sC / nC
        gmag = math.sqrt(sum(m*m for m in comps))
        table.append({'pair': list(pq), 'c': c_val, 'n_c': nC, 'g_comps': comps,
                      'g_se': ses, 'g_n': ns, 'g_mag': gmag})
    # power gate: per-component se <= 0.02
    surviving = [t for t in table if t['g_se'] and max(t['g_se']) <= 0.02]
    print(f'pairs total {len(table)}, surviving power gate (se<=0.02): {len(surviving)}')
    if len(surviving) < 8:
        print('UNDERPOWERED: <8 surviving pairs — no verdict (frozen rule)')
        json.dump({'verdict': 'UNDERPOWERED', 'surviving': len(surviving), 'table': table,
                   'mapping': list(mapping)}, open(os.path.join(R, 'h14_lock5_verdict.json'), 'w'), indent=1)
        return

    # --- P-A: global chi^2 of g components vs shot-noise se ---
    chi2 = sum((m/se)**2 for t in surviving for m, se in zip(t['g_comps'], t['g_se']))
    dof = sum(len(t['g_comps']) for t in surviving)
    # normal-approx tail via Wilson-Hilferty
    zwh = ((chi2/dof)**(1/3) - (1 - 2/(9*dof))) / math.sqrt(2/(9*dof))
    ratio = math.sqrt(chi2/dof)
    print(f'P-A: chi2 {chi2:.1f} / dof {dof} -> structure {ratio:.2f}x shot noise, z_WH {zwh:.2f}')
    pa_sig = zwh > 2.326  # alpha=0.01 one-sided

    # --- P-C: Spearman(|g|, 1-c) with permutation p ---
    def spearman(xs, ys):
        def rank(v):
            idx = sorted(range(len(v)), key=lambda i: v[i]); r = [0]*len(v)
            for k, i in enumerate(idx): r[i] = k
            return r
        rx, ry = rank(xs), rank(ys); n = len(xs)
        mx = (n-1)/2; num = sum((a-mx)*(b-mx) for a, b in zip(rx, ry))
        den = sum((a-mx)**2 for a in rx)
        return num/den if den else 0.0
    xs = [t['g_mag'] for t in surviving]; ys = [1 - t['c'] for t in surviving]
    rho = spearman(xs, ys)
    rng = random.Random(5071)
    perm = [spearman(xs, rng.sample(ys, len(ys))) for _ in range(10000)]
    p_pos = sum(1 for r in perm if r >= rho) / len(perm)
    print(f'P-C: Spearman rho(|g|, 1-c) = {rho:+.3f}, permutation p(one-sided pos) = {p_pos:.4f} over {len(surviving)} pairs')

    # --- P-B: adjacency — offline proxy availability check ---
    pb_note = 'NOT-EVALUABLE offline (coupling map not banked); frozen fallback: reported as such'

    verdict = ('GHOST-GENERALIZES-QUALITY-LINKED' if pa_sig and p_pos < 0.01 else
               'GHOST-PRESENT-LINK-INDETERMINATE' if pa_sig else
               'MARRAKESH-LOCAL-AT-RESOLVED-SCALE')
    print(f'VERDICT (frozen rules): {verdict}')
    json.dump({'verdict': verdict, 'mapping': list(mapping), 'median_c': med_c,
               'jobs': jobs_present, 'P_A': {'chi2': chi2, 'dof': dof, 'ratio': ratio, 'z_WH': zwh},
               'P_B': pb_note, 'P_C': {'rho': rho, 'p_perm_pos': p_pos},
               'surviving_pairs': len(surviving), 'table': table},
              open(os.path.join(R, 'h14_lock5_verdict.json'), 'w'), indent=1)
    print('-> results/h14_lock5_verdict.json')

if __name__ == '__main__':
    main()
