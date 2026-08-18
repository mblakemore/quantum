#!/usr/bin/env python3
"""H15 paired bake-off SUBMIT (Whisper C5075). ALT5 (free/open, runtime-verified plan=open).
Unsealed, claim-free, known-A diagnostic — Elder general#12730 authorisation class."""
import argparse, json, os, sys
HERE=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,HERE); sys.path.insert(0,os.path.join(HERE,"..","scripts"))
from h15_bakeoff2_paired_whisper_c5075 import build_all, rows, SEED, ARMS, N_ALT, N_NULL
ACCOUNT, BACKEND = "IBMQ_ALT5", "ibm_kingston"

def gate():
    from h15_n1_synapse_incircuit_whisper_c5074 import SIM
    from h15_bakeoff2_paired_whisper_c5075 import parse_n4, rule_from_bits
    c=build_all()
    r=SIM.run(c,shots=1,memory=True).result()
    mems=[r.get_memory(i)[0] for i in range(len(c))]
    alt={a:[0,0] for a in ARMS}; viol=0; nev=alw=0
    for (arm,kind,p,k),mem in zip(rows(),mems):
        resp=int(mem.split()[0])
        if arm in ARMS and kind=="ALT": alt[arm][0]+=resp; alt[arm][1]+=1
        if arm=="ABL_never": nev+=resp
        if arm=="ABL_always": alw+=resp
        if arm.startswith(("B_","C_")):
            _,a,b=parse_n4(mem)
            if rule_from_bits(a,b,"optimal")==1 and rule_from_bits(a,b,"simple")==0: viol+=1
    ok = all(alt[a][0]==N_ALT for a in ARMS) and nev==0 and alw==8 and viol==0
    print(f"SIM GATE ok={ok}  alt={ {k:v[0] for k,v in alt.items()} }  never={nev} always={alw} subset_viol={viol}")
    if not ok: sys.exit("SIM GATE FAILED")
    return c

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--fly",action="store_true"); a=ap.parse_args()
    c=gate()
    if not a.fly: return
    import ibm_multi_account as M
    from qiskit import transpile
    from qiskit_ibm_runtime import SamplerV2
    svc=M.service_for_submission(ACCOUNT); backend=svc.backend(BACKEND)
    tq=transpile(c,backend,optimization_level=1,seed_transpiler=SEED)
    snap=M.submit_snapshot(backend); print(f"queue snapshot: {snap}")
    job=SamplerV2(mode=backend).run([(t,) for t in tq],shots=1)
    jid=job.job_id(); print(f"JOB ID (ANNOUNCED AT SUBMIT): {jid}")
    json.dump({"card":"h15_bakeoff2_paired","cycle":"C5075","job_id":jid,"backend":BACKEND,
        "account":ACCOUNT,"rows":len(tq),"shots_per_row":1,"seed":SEED,"arms":list(ARMS),
        "n_alt_per_arm":N_ALT,"n_null_per_arm":N_NULL,
        "pairing":"ONE shared instance set across all arms; rule comparison computed offline from arm B's own recorded bells (identical rows AND shots)",
        "falsifier":"optimal-accept implies simple-accept on any single row's bells; a single violation invalidates the analysis",
        "queue_at_submit":snap},
        open(os.path.join(HERE,"..","results","h15_bakeoff2_manifest_c5075.json"),"w"),indent=1)
    print("manifest written")

if __name__=="__main__": main()
