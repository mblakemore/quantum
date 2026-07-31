#!/usr/bin/env python3
"""Exp241c-a — T1-AWARE asymmetric ML decoder vs memoryless, offline on Exp241 sham streams. $0.
Option (a) of the Exp247 redesign decision (Creator go, C4952).
Asymmetric HMM: error bit e_i=1 means qubit i flipped from its encoded |1> to |0> (T1 decay, rate p10);
e_i: 1->0 with p01 (re-excitation). enc=0 hypothesis: rates swap roles. Decision rule (pre-stated):
ML_T1 beats memoryless M by >3sigma paired at BOTH R3 and R4 -> Exp247 redesigned as STATIC flight
with offline decoding; else P7 stands down. Substrate claude-fable-5, Whisper C4952."""
import numpy as np, json, os, sys
from itertools import product
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from exp241c_offline_decoders import syn_of, majority1, replay, CORR
QROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")

def loglik_t1(recs_s, out_s, enc, p10, p01, q, rf):
    R = len(recs_s)
    alpha = np.full(8, -np.inf); alpha[0] = 0.0
    lq, l1q, lrf, l1rf = np.log(q), np.log(1-q), np.log(rf), np.log(1-rf)
    # per-bit transition probs depend on current e_i and hypothesis
    # enc=1: e_i 0->1 w.p. p10 (decay), 1->0 w.p. p01 ; enc=0: swapped
    a, b = (p10, p01) if enc == 1 else (p01, p10)
    la, l1a, lb, l1b = np.log(a), np.log(1-a), np.log(b), np.log(1-b)
    for r in range(R):
        new = np.full(8, -np.inf)
        for e in range(8):
            if alpha[e] == -np.inf: continue
            for ne in range(8):
                t = alpha[e]
                for i in range(3):
                    ei, nei = (e>>i)&1, (ne>>i)&1
                    if ei==0: t += la if nei==1 else l1a
                    else:     t += lb if nei==0 else l1b
                new[ne] = np.logaddexp(new[ne], t)
        for e in range(8):
            if new[e] == -np.inf: continue
            d = bin(recs_s[r] ^ syn_of(e)).count("1")
            new[e] += d*lq + (2-d)*l1q
        alpha = new
    ideal = 0b111 if enc==1 else 0b000
    tot = -np.inf
    for e in range(8):
        if alpha[e] == -np.inf: continue
        d = bin(out_s ^ ideal ^ e).count("1")
        tot = np.logaddexp(tot, alpha[e] + d*lrf + (3-d)*l1rf)
    return tot

def main():
    from qiskit_ibm_runtime import QiskitRuntimeService
    # ACCOUNT SCOPE (C5016 reader audit): fetches a PINNED historical Exp241-era job
    # living on the SAVED DEFAULT account (flown pre-ALT-migration). Do NOT re-point
    # to ALT -- it would 404. A pinned-ID fetch fails LOUD on the wrong account,
    # unlike ambient readers whose wrong-scope output still looks right, so this is
    # labeled rather than re-plumbed. Cross-account lookup if ever needed:
    # scripts/check_job_status.py sweeps both instances.
    res = QiskitRuntimeService().job("d9f3ov4jeosc73fjen3g").result()
    report = {}
    for R, idx in [(3,10),(4,13)]:
        db = res[idx].data
        regs = sorted(k for k in db.__dict__ if k.startswith("syn"))
        recs = [np.array([int(x,2) for x in getattr(db,k).get_bitstrings()]) for k in regs]
        out = np.array([int(x,2) for x in db.out.get_bitstrings()])
        n = len(out); test = np.arange(n)%2==1; train=~test
        sub = np.random.RandomState(1).choice(np.where(train)[0], size=400, replace=False)
        best, bp = -np.inf, None
        for p10,p01,q,rf in product((0.08,0.12,0.16,0.22),(0.005,0.02,0.05),(0.05,0.10,0.18),(0.02,0.05,0.10)):
            ll = sum(loglik_t1([rc[s] for rc in recs], out[s], 1, p10,p01,q,rf) for s in sub)
            if ll > best: best, bp = ll, (p10,p01,q,rf)
        m = replay(recs, out, "M")
        ml = np.zeros(n, bool)
        for s in np.where(test)[0]:
            l1 = loglik_t1([rc[s] for rc in recs], out[s], 1, *bp)
            l0 = loglik_t1([rc[s] for rc in recs], out[s], 0, *bp)
            ml[s] = l1 >= l0
        mt, mlt = m[test], ml[test]
        b01, b10 = int((~mt & mlt).sum()), int((mt & ~mlt).sum())
        z = (b01-b10)/np.sqrt(b01+b10) if (b01+b10)>0 else 0.0
        row = {"params(p10,p01,q,rf)": bp, "F_M": round(float(mt.mean()),4),
               "F_ML_T1": round(float(mlt.mean()),4), "mcnemar(+,-)": [b01,b10], "z": round(float(z),2)}
        report[f"R{R}"] = row
        print(f"R={R}: M={row['F_M']}  ML_T1={row['F_ML_T1']}  params={bp}  McNemar {b01}/{b10}  z={z:+.2f}")
    json.dump(report, open(os.path.join(QROOT,"results","exp241c_t1_ml.json"),"w"), indent=1)
    print("card -> results/exp241c_t1_ml.json")

if __name__ == "__main__":
    main()
