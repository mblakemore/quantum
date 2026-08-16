#!/usr/bin/env python3
"""door(a) flight-4 independent blind decode (Whisper C5073) - proven flight-3 logic, M=80.
Re-derives the SWAP-overlap accept-parity + cal-PINS the convention; pools f_cal -> tau_Q; per-trial
accept/reject -> independent 80-trial score. Run on landing: python3 <this>."""
import json, numpy as np, sys, glob
sys.path.insert(0,'experiments')
from doora_flight3_tauq_whisper_c5073 import tau_q
n=8; SHOTS=316; p0=0.5+2**-(n+1)
RAW=glob.glob('results/doora_flight4_raw_*.json')
if not RAW: print('RAW not landed yet - rerun after Ember banks'); sys.exit()
d=json.load(open(RAW[0])); c=d['pubs'][0]['c']
rm=json.load(open(glob.glob('results/doora_flight4_rowmap*.json')[0]))
cal_pos=set(rm['cal_positions']); sealed=rm['sealed_positions']; TOT=rm['total_rows']
shots=np.array([[int(b) for b in s] for s in c]).reshape(TOT, SHOTS, 16)
def accept_freq(pos, pairing, reverse):
    blk=shots[pos]
    if reverse: blk=blk[:,::-1]
    a,b=(blk[:,:8],blk[:,8:]) if pairing=='halves' else (blk[:,0::2],blk[:,1::2])
    return (((a==1)&(b==1)).sum(axis=1)%2==0).mean()
best=None
for pairing in ['halves','interleaved']:
    for reverse in [False,True]:
        fcal=float(np.mean([accept_freq(p,pairing,reverse) for p in cal_pos]))
        if fcal>p0 and 2*fcal-1>0 and (best is None or fcal>best[0]): best=(fcal,pairing,reverse)
fcal,pairing,reverse=best
tau,uhat,p0v,p1v,ok=tau_q(n,fcal)
print('PINNED pairing=%s reverse=%s | f_cal=%.5f u_hat=%+.4f tau_Q=%.5f' % (pairing,reverse,fcal,uhat,tau))
if not ok: print('u_hat<=0 -> NO-DECODE'); sys.exit()
dec={}
for ps,name in sealed.items():
    dec[name]='ALT' if accept_freq(int(ps),pairing,reverse)>=tau else 'NULL'
nALT=sum(v=='ALT' for v in dec.values()); M=len(dec)
print('MY BLIND DECODE: %d ALT / %d NULL of %d trials (criterion 76/80)' % (nALT,M-nALT,M))
json.dump({'card':'doora_flight4_whisper_blind_decode','job':d['job_id'],'convention':{'pairing':pairing,'reverse':reverse},
 'f_cal':fcal,'u_hat':uhat,'tau_Q':tau,'n_ALT':nALT,'n_NULL':M-nALT,'decisions':dec},
 open('results/doora_flight4_whisper_blind_decode_c5073.json','w'),indent=1)
print('-> results/doora_flight4_whisper_blind_decode_c5073.json')
