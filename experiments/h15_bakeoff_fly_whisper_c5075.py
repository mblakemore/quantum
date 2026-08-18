#!/usr/bin/env python3
"""H15 bake-off SUBMIT (Whisper C5075). ALT5 (free/open — Creator correction 2026-08-18,
verified against the runtime: plan=open, same as ALT4). Unsealed, claim-free, known-A diagnostic;
same authorisation class as the R1 probes (Elder general#12730), no seal-bound GO."""
import argparse, json, os, sys
HERE=os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0,HERE); sys.path.insert(0,os.path.join(HERE,"..","scripts"))
from h15_bakeoff_whisper_c5075 import build_all, decode, accuracy, rows, SEED
ACCOUNT, BACKEND = "IBMQ_ALT5", "ibm_kingston"

def gate():
    from h15_n1_synapse_incircuit_whisper_c5074 import SIM
    circs=build_all()
    r=SIM.run(circs,shots=1,memory=True).result()
    mems=[r.get_memory(i)[0] for i in range(len(circs))]
    d=decode(mems)
    ok=(d["ABL_never"]["ALT"][0]==0 and d["ABL_always"]["ALT"][0]==8)
    print(f"SIM GATE ok={ok}  arms={sorted(d)}")
    if not ok: sys.exit("SIM GATE FAILED")
    return circs

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("--fly",action="store_true"); a=ap.parse_args()
    circs=gate()
    if not a.fly: return
    import ibm_multi_account as M
    from qiskit import transpile
    from qiskit_ibm_runtime import SamplerV2
    svc=M.service_for_submission(ACCOUNT); backend=svc.backend(BACKEND)
    tqcs=transpile(circs,backend,optimization_level=1,seed_transpiler=SEED)
    snap=M.submit_snapshot(backend); print(f"queue snapshot: {snap}")
    job=SamplerV2(mode=backend).run([(t,) for t in tqcs],shots=1)
    jid=job.job_id(); print(f"JOB ID (ANNOUNCED AT SUBMIT): {jid}")
    json.dump({"card":"h15_bakeoff","cycle":"C5075","job_id":jid,"backend":BACKEND,
               "account":ACCOUNT,"rows":len(tqcs),"shots_per_row":1,"seed":SEED,
               "arms":["A_toffoli_simple","B_realtime_simple","C_realtime_optimal"],
               "authorisation":"unsealed claim-free diagnostic (Elder general#12730 class); ALT5 free/open per Creator correction, runtime-verified plan=open",
               "queue_at_submit":snap},
              open(os.path.join(HERE,"..","results","h15_bakeoff_manifest_c5075.json"),"w"),indent=1)
    print("manifest written")

if __name__=="__main__": main()
