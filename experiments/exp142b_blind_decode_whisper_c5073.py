#!/usr/bin/env python3
"""EXP142B blind decode + determinism attack, N-parametrized (Whisper C5073).
Generalizes the n=4 decode to any rung. Validated: reproduces n=4 ZYYZ 20/20 + attack PASS.
Usage: LADDER_N=6 python3 exp142b_blind_decode_whisper_c5073.py   (schedule + raw auto-located by N)."""
import json, os, sys, glob
import numpy as np
from collections import defaultdict, Counter
from math import log
HERE=os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0,HERE); sys.path.insert(0,os.path.join(HERE,"..","scripts"))
RES=os.path.join(HERE,"..","results")
N=int(os.environ.get("LADDER_N","4"))
ACCEPT=N*log(3)+log(100); ELIM=log(0.005)

def load():
    sched=json.load(open(os.path.join(RES,f"exp142b_n{N}_schedule.json")))
    conv_reps=[p for p in sched["pubs"] if isinstance(p,list)]
    man=json.load(open(os.path.join(RES,f"exp142b_n{N}_manifest.json")))
    job_order=[j if isinstance(j,str) else j.get("job_id") for j in man["jobs"]]
    flown=[]
    for jid in job_order:
        f=os.path.join(RES,f"exp142b_n{N}_raw_{jid}.json")
        if not os.path.exists(f): continue
        d=json.load(open(f))
        for p in d["pubs"]:
            c=p.get("c") or list(p.values())[0]
            if len(c[0])==N and len(c)>N*50: flown.append(c)
    return conv_reps,flown

def cal_p0():
    ev=tot=0
    for f in glob.glob(os.path.join(RES,f"exp142b_n{N}_raw_*.json")):
        for p in json.load(open(f))["pubs"]:
            c=p.get("c") or list(p.values())[0]
            if len(c[0])==N and 50<=len(c)<=200:
                for s in c: ev+=(sum(int(b) for b in s)%2==0); tot+=1
    return ev/tot if tot else 0.97

def main():
    conv_reps,flown=load()
    print(f"N={N}: {len(conv_reps)} schedule reps, {len(flown)} flown conv pubs")
    if not flown: print("NO FLOWN DATA YET (jobs not landed/banked) — rerun after landing"); return
    p0=cal_p0(); l_even,l_odd=log(p0/0.5),log((1-p0)/0.5)
    guesses,copies,cens=[],[],0; atk_max=0.0
    for rep,out in zip(conv_reps,flown):
        m=min(len(rep),len(out)); rep,out=rep[:m],out[:m]
        parity=[sum(int(b) for b in s)%2 for s in out]
        by=defaultdict(list)
        for row,s in zip(rep,out): by[row["A"]].append([int(b) for b in s])
        for A,rr in by.items():
            arr=np.array(rr); atk_max=max(atk_max, float(np.maximum(arr.mean(0),1-arr.mean(0)).max()))
        llr=defaultdict(float); alive=set(r["A"] for r in rep); g=st=None
        for j,(row,par) in enumerate(zip(rep,parity)):
            A=row["A"]
            if A not in alive: continue
            llr[A]+=(l_odd if par else l_even)
            if llr[A]>=ACCEPT: g,st=A,j+1; break
            if llr[A]<=ELIM: alive.discard(A)
        if g is None: cens+=1; g=max(alive,key=lambda a:llr[a]) if alive else "?"; st=len(rep)
        guesses.append(g); copies.append(st)
    gc=Counter(guesses); cons,nc=gc.most_common(1)[0]
    # attack null (per-basis 27-ish rows -> compare to fresh-b null via aggregate too)
    print(f"BLIND DECODE: guessed P={cons} ({nc}/{len(guesses)}), median copies={int(np.median(copies))}, censored {cens}/{len(guesses)}")
    print(f"ATTACK: max per-basis determinism {atk_max:.4f} (null-calibrate before verdict; n=4 ref 0.85=73rd pct)")
    json.dump({"card":f"exp142b_n{N}_blind_decode","N":N,"guessed_P":cons,"consensus":nc,
     "median_copies":int(np.median(copies)),"censored":cens,"attack_max_det":atk_max,"p0":p0},
     open(os.path.join(RES,f"exp142b_n{N}_blind_decode_whisper_c5073.json"),"w"),indent=1)
    print(f"-> results/exp142b_n{N}_blind_decode_whisper_c5073.json")

if __name__=="__main__": main()
