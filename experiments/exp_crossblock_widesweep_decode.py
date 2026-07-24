#!/usr/bin/env python3
"""P2 depth-sweep decode (C5002-B). Job d9hjfbkhonhs73ad58vg (kingston). Pins the {53,26} mechanism +
resolves phys73: |<Z>| across 160/200/240/280. MONOTONE-decreasing => decoherent; NON-MONOTONE /
oscillation (a rise anywhere) => COHERENT (a unitary phi*depth rotation, Elder #1136). Verdict per qubit."""
import json, os
HERE=os.path.dirname(os.path.abspath(__file__)); QROOT=os.path.join(HERE,"..")
JOB="d9hjfbkhonhs73ad58vg"
MAN=json.load(open(os.path.join(QROOT,"results","exp_crossblock_widesweep_manifest.json")))
DRIFTERS=MAN["drifters"]; DEPTHS=MAN["depths"]
def main():
    import numpy as np
    from qiskit_ibm_runtime import QiskitRuntimeService
    job=QiskitRuntimeService().job(JOB); res=job.result()
    idx={m["block"]:i for i,m in enumerate(MAN["pubs_meta"])}
    def counts(t):
        d=res[idx[t]].data; return d[list(d.keys())[0]].get_counts()
    c0,c1=counts("cal0"),counts("cal1"); n0,n1=sum(c0.values()),sum(c1.values())
    def ro(q):
        p01=sum(v for k,v in c0.items() if k.replace(" ","")[-1-q]=="1")/n0
        p10=sum(v for k,v in c1.items() if k.replace(" ","")[-1-q]=="0")/n1
        return p01,p10
    def absZ(t,q):
        cc=counts(t); n=sum(cc.values())
        p1=sum(v for k,v in cc.items() if k.replace(" ","")[-1-q]=="1")/n
        p01,p10=ro(q); vis=max(1e-6,1-p01-p10); return abs((1-2*p1)/vis)
    out={"card":"exp_crossblock_widesweep_decode","job":JOB,"cal_epoch":MAN["cal_epoch"],"drifters":{}}
    for q in DRIFTERS:
        seq=[round(absZ(f"twin_d{D}",q),4) for D in DEPTHS]
        # monotone-decreasing? allow small noise tol
        mn=min(seq); mn_i=seq.index(mn); post=seq[mn_i+1:]
        revival=len(post)>0 and (max(post)-mn)>0.04   # rises after the minimum
        out["drifters"][q]={"depths":DEPTHS,"absZ":seq,"min_at_depth":DEPTHS[mn_i],
            "revival_amplitude":round((max(post)-mn) if post else 0.0,4),
            "mechanism":"COHERENT (|<Z>| REVIVES past node)" if revival else "no revival in range (decoherent OR node beyond 400)"}
    json.dump(out,open(os.path.join(QROOT,"results","exp_crossblock_widesweep_decoded.json"),"w"),indent=1)
    for q,dd in out["drifters"].items():
        print("phys%s: absZ=%s -> %s" % (q, dd["absZ"], dd["mechanism"]))
    print(f"usage={job.usage()}s")
if __name__=="__main__": main()
