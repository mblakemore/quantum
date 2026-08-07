"""How much WORSE are the pinned edges today? Cost = 2q error + both readout errors
(exactly pick_layouts' own metric). READ-ONLY."""
import sys, json
sys.path.insert(0,'experiments'); sys.path.insert(0,'scripts')
from run_exp66_qpu_partb import _get_ibm_service
from exp142_flight_kit import pick_layouts

PIN=json.load(open('results/p1_kit_confirm.json'))['pinned_edges']
bk=_get_ibm_service().backend('ibm_marrakesh')
t=bk.target
twoq="cz" if "cz" in t.operation_names else "ecr"
ro={q:(t["measure"][(q,)].error or 0.0) for (q,) in t["measure"].keys()}
cost={}
for (a,b),inst in t[twoq].items():
    e=getattr(inst,"error",None)
    if e is not None: cost[(a,b)]=e+ro.get(a,0)+ro.get(b,0); cost[(b,a)]=cost[(a,b)]

def tot(edges):
    out=[]
    for a,b in edges:
        c=cost.get((a,b))
        out.append(c)
    return out

for n in (4,6,8):
    was=[tuple(e) for e in PIN[str(n)]]
    _,_,now=pick_layouts(bk,n); now=[tuple(e) for e in now]
    cw,cn=tot(was),tot(now)
    miss=[e for e,c in zip(was,cw) if c is None]
    cwv=[c for c in cw if c is not None]; cnv=[c for c in cn if c is not None]
    print(f"n={n}")
    if miss: print(f"  ⚠ pinned edges NO LONGER IN COUPLING MAP / no cal data: {miss}")
    print(f"  pinned  worst {max(cwv):.5f}  mean {sum(cwv)/len(cwv):.5f}")
    print(f"  today   worst {max(cnv):.5f}  mean {sum(cnv)/len(cnv):.5f}")
    print(f"  ratio   worst {max(cwv)/max(cnv):.2f}x   mean {(sum(cwv)/len(cwv))/(sum(cnv)/len(cnv)):.2f}x  (pinned/today)")
    print(f"  pinned per-edge: {[f'{c:.4f}' if c is not None else 'NONE' for c in cw]}")
    print()
