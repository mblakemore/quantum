#!/usr/bin/env python3
"""
H14 Lock 6 executor — the sentinel siphon.
Frozen: docs/h14-lock6-sentinel-siphon-protocol-FROZEN-whisper-c5072.md (f603169).
Run ONCE on the completed rescue corpus. G1 (kit identity) verified from source pre-run:
both kits' sentinel_circuit() are byte-identical Bell circuits (H-CX, 400 shots).
"""
import json, glob, os, math
import numpy as np

R = 'results'

def manifest_index():
    idx = {}
    for f in glob.glob(os.path.join(R, 'exp14*manifest*.json')) + \
             glob.glob(os.path.join(R, 'exp142_p1_*manifest*.json')):
        try: d = json.load(open(f))
        except Exception: continue
        if not isinstance(d, dict) or 'pubs' not in d: continue
        jids = [d[k] for k in ('job_id',) if k in d]
        if 'jobs' in d and isinstance(d['jobs'], list):
            for j in d['jobs']:
                if isinstance(j, dict) and 'job_id' in j: jids.append(j['job_id'])
        for j in jids: idx[j] = (f, d)
    return idx

def kind_of(p):
    if isinstance(p, dict): return p.get('kind', '?')
    return str(p)

def sentinel_positions(pubs):
    ks = [kind_of(p) for p in pubs]
    pos = [i for i, k in enumerate(ks) if 'sentinel' in k]
    return pos, ks

def eps_beta(rows):
    n = len(rows)
    c01 = sum(1 for r in rows if r in ('01', '10'))
    c00 = sum(1 for r in rows if r == '00')
    c11 = sum(1 for r in rows if r == '11')
    eps = c01 / n
    return eps, (c00 - c11) / n, n

def main():
    midx = manifest_index()
    jobs = []
    for f in sorted(glob.glob(os.path.join(R, 'h14_lock5_rescue_*.json'))):
        d = json.load(open(f))
        jid = d['job_id']
        if jid not in midx: continue
        mf, man = midx[jid]
        pos, ks = sentinel_positions(man['pubs'])
        if len(pos) < 2: continue
        first, last = pos[0], pos[-1]
        pdata = {p['pub_index']: p['data'] for p in d['pubs']}
        rec = {}
        ok = True
        for tag, i in (('start', first), ('end', last)):
            data = pdata.get(i)
            rows = next((v for v in (data or {}).values() if isinstance(v, list)), None)
            # G2: 2-bit rows, count matches manifest where stated
            if not rows or any(len(r) != 2 for r in rows[:5]):
                ok = False; break
            want = man['pubs'][i].get('shots') if isinstance(man['pubs'][i], dict) else None
            if want and len(rows) != want:
                ok = False; break
            rec[tag] = eps_beta(rows)
        if not ok: continue
        backend = man.get('backend', '?')
        jobs.append({'job_id': jid, 'backend': backend, 'manifest': os.path.basename(mf),
                     'eps_start': rec['start'][0], 'beta_start': rec['start'][1],
                     'eps_end': rec['end'][0], 'beta_end': rec['end'][1],
                     'n': rec['start'][2]})
    print(f'jobs entering (G2 passed, both sentinels): {len(jobs)}')
    by_dev = {}
    for j in jobs: by_dev.setdefault(j['backend'], []).append(j)
    out = {'G1': 'PASS (kits byte-identical, verified from source)', 'per_device': {}, 'jobs': jobs}
    for dev, js in sorted(by_dev.items()):
        N = len(js)
        d_eps = np.array([j['eps_end'] - j['eps_start'] for j in js])
        ses = np.array([math.sqrt(j['eps_start']*(1-j['eps_start'])/j['n'] +
                                  j['eps_end']*(1-j['eps_end'])/j['n']) for j in js])
        ses = np.maximum(ses, 1e-6)
        primary = N >= 10
        w = 1/ses**2
        mean_w = float((d_eps*w).sum()/w.sum()); se_mean = float(1/math.sqrt(w.sum()))
        z_mean = mean_w/se_mean
        T = float((((d_eps - mean_w)/ses)**2).sum()); dof = N - 1
        # chi2 tail via Wilson-Hilferty
        zwh = ((T/dof)**(1/3) - (1 - 2/(9*dof))) / math.sqrt(2/(9*dof)) if dof > 0 else 0.0
        eps_all = [j['eps_start'] for j in js] + [j['eps_end'] for j in js]
        res = {'N_jobs': N, 'primary': primary,
               'mean_deps_weighted': mean_w, 'se': se_mean, 'z_mean': z_mean,
               'overdispersion_T': T, 'dof': dof, 'z_WH': zwh,
               'eps_range': [float(min(eps_all)), float(max(eps_all))],
               'eps_median': float(np.median(eps_all))}
        out['per_device'][dev] = res
        flag = '' if primary else ' (descriptive only, <10 jobs)'
        print(f'{dev}: N={N}{flag} · eps median {res["eps_median"]:.4f} range {res["eps_range"][0]:.4f}-{res["eps_range"][1]:.4f}')
        print(f'   D1a overdispersion: T={T:.1f} dof={dof} z_WH={zwh:.2f} -> {"SIG" if zwh>2.326 and primary else "ns/desc"}')
        print(f'   D1b mean drift: {mean_w:+.5f} ± {se_mean:.5f} (z={z_mean:+.2f}) -> {"SIG" if abs(z_mean)>2.576 and primary else "ns/desc"}')
    # frozen verdict per device
    verdicts = {}
    for dev, r in out['per_device'].items():
        if not r['primary']: verdicts[dev] = 'DESCRIPTIVE-ONLY'
        elif r['z_WH'] > 2.326 and abs(r['z_mean']) <= 2.576: verdicts[dev] = 'WITHIN-JOB-DRIFT-VISIBLE'
        elif r['z_mean'] > 2.576: verdicts[dev] = 'MONOTONE-LOAD-SIGNATURE'
        elif r['z_mean'] < -2.576 and r['z_WH'] > 2.326: verdicts[dev] = 'WITHIN-JOB-DRIFT-VISIBLE (improving-mean, report as-is)'
        elif r['z_mean'] < -2.576: verdicts[dev] = 'MEAN-IMPROVEMENT (unregistered direction, report as-is)'
        else: verdicts[dev] = 'STABILITY-CERTIFIED-AT-RESOLUTION'
    out['verdicts'] = verdicts
    print('VERDICTS:', verdicts)
    json.dump(out, open(os.path.join(R, 'h14_lock6_verdict.json'), 'w'), indent=1)
    print('-> results/h14_lock6_verdict.json')

if __name__ == '__main__':
    main()
