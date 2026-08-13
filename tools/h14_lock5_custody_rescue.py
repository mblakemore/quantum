#!/usr/bin/env python3
"""
H14 Lock 5, stage 0 — custody rescue of exp142/exp144 shot-level records (Whisper C5071).

Banks raw measurement records VERBATIM from IBM jobs whose local artifacts are manifest-only.
Computes NOTHING (A2 stage-0 precedent: "the banking script writes counts verbatim and
computes nothing"). Freeze-before-decode discipline: no estimator runs here.

EXCLUDED BY FENCE (results/exp142_wave1_INVALID_DO_NOT_DECODE.md + VOID c4262):
  - attempt-1 poisoned:  d9c8047550hc73dl1ap0, d9c807k1osis73bjh0e0  (data GARBAGE, do not poll)
  - attempt-1/2 cancelled: d9c80bnngvls73a94eug, d9c80ev550hc73dl1bcg,
      d9c89a41osis73bjha6g, d9c89bf550hc73dl1l40, d9c89cv550hc73dl1l6g, d9c89e96dkoc73fhb9lg
  - exp142c VOID (c4262): all six d9rrm* ids

Usage: python3 tools/h14_lock5_custody_rescue.py <jobs.json>
  jobs.json: [{"job_id": ..., "tag": "exp142_wave1_n10"}, ...]
Output: results/h14_lock5_rescue_<tag>_<jobid>.json  (skips ids already rescued)
"""
import json, sys, os, time, datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'scripts'))
from ibm_multi_account import service_for_job

FENCED = {
    'd9c8047550hc73dl1ap0', 'd9c807k1osis73bjh0e0',
    'd9c80bnngvls73a94eug', 'd9c80ev550hc73dl1bcg',
    'd9c89a41osis73bjha6g', 'd9c89bf550hc73dl1l40',
    'd9c89cv550hc73dl1l6g', 'd9c89e96dkoc73fhb9lg',
    'd9rrm4opdb6s73e5a9qg', 'd9rrm51dsedc73ah1t80', 'd9rrm58pdb6s73e5a9rg',
    'd9rrm5npemts73ct0e3g', 'd9rrm5opdb6s73e5a9t0', 'd9rrm5pdsedc73ah1ta0',
}

def bank_pub(pubres):
    """Extract every data field of a pub result verbatim as bitstring lists."""
    out = {}
    for name in pubres.data:
        arr = pubres.data[name]
        try:
            out[name] = arr.get_bitstrings()
        except AttributeError:
            out[name] = repr(arr)[:2000]
    return out

def main():
    jobs = json.load(open(sys.argv[1]))
    ok = fail = skip = 0
    for spec in jobs:
        jid, tag = spec['job_id'], spec['tag']
        if jid in FENCED:
            print(f'{jid} {tag}: FENCED — skipped'); skip += 1; continue
        dest = f'results/h14_lock5_rescue_{tag}_{jid}.json'
        if os.path.exists(dest):
            print(f'{jid} {tag}: already rescued'); skip += 1; continue
        try:
            svc, acct = service_for_job(jid)
            job = svc.job(jid)
            st = str(job.status())
            if 'DONE' not in st.upper():
                print(f'{jid} {tag}: status {st} — no results to bank'); fail += 1; continue
            res = job.result()
            pubs = [{'pub_index': i, 'data': bank_pub(p)} for i, p in enumerate(res)]
            rec = {
                'rescue': 'h14_lock5_stage0', 'cycle': 'C5071', 'seat': 'whisper',
                'job_id': jid, 'tag': tag, 'account': acct,
                'fetched_utc': datetime.datetime.now(datetime.timezone.utc).isoformat(),
                'note': 'verbatim raw measurement records; nothing computed (freeze-before-decode)',
                'pubs': pubs,
            }
            tmp = dest + '.tmp'
            with open(tmp, 'w') as f: json.dump(rec, f)
            os.replace(tmp, dest)
            nshots = sum(len(v) for p in pubs for v in p['data'].values() if isinstance(v, list))
            print(f'{jid} {tag}: BANKED {len(pubs)} pubs, {nshots} rows, {os.path.getsize(dest)} bytes [{acct}]')
            ok += 1
        except Exception as e:
            print(f'{jid} {tag}: FAILED {type(e).__name__}: {str(e)[:200]}'); fail += 1
        time.sleep(1)
    print(f'== rescue complete: {ok} banked, {fail} failed, {skip} skipped')

if __name__ == '__main__':
    main()
