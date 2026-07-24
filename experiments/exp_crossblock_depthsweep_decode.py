#!/usr/bin/env python3
"""P2 depth-sweep decode (C5002-B). Job d9hj9krsbqfc73eq5ds0 (kingston). Pins the {53,26} mechanism +
resolves phys73: |<Z>| across 160/200/240/280. MONOTONE-decreasing => decoherent; NON-MONOTONE /
oscillation (a rise anywhere) => COHERENT (a unitary phi*depth rotation, Elder #1136). Verdict per qubit."""
import json, os
HERE=os.path.dirname(os.path.abspath(__file__)); QROOT=os.path.join(HERE,"..")
JOB="d9hj9krsbqfc73eq5ds0"
MAN=json.load(open(os.path.join(QROOT,"results","exp_crossblock_depthsweep_manifest.json")))
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
    out={"card":"exp_crossblock_depthsweep_decode","job":JOB,"cal_epoch":MAN["cal_epoch"],"drifters":{}}
    for q in DRIFTERS:
        seq=[round(absZ(f"twin_d{D}",q),4) for D in DEPTHS]
        # monotone-decreasing? allow small noise tol
        diffs=[seq[i+1]-seq[i] for i in range(len(seq)-1)]
        rises=[d for d in diffs if d>0.03]
        mono=len(rises)==0
        out["drifters"][q]={"depths":DEPTHS,"absZ":seq,"diffs":[round(d,4) for d in diffs],
            "n_rises_gt0.03":len(rises),
            "mechanism":"DECOHERENT (monotone decay)" if mono else "COHERENT (non-monotone/oscillation -> unitary phi*depth)"}
    json.dump(out,open(os.path.join(QROOT,"results","exp_crossblock_depthsweep_decoded.json"),"w"),indent=1)
    for q,d in out["drifters"].items(): print(f"phys{q}: absZ={d[\'absZ\']} -> {d[\'mechanism\']}")
    print(f"usage={job.usage()}s")
if __name__=="__main__": main()
