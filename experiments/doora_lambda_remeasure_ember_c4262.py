"""Re-measure lambda_eff from LIVE calibration for the circuit classes at issue.
READ-ONLY. Whisper #6212 assigned; I also used the borrowed value in my own #6180."""
import sys, math, statistics as st
sys.path.insert(0,'experiments'); sys.path.insert(0,'scripts')
from run_exp66_qpu_partb import _get_ibm_service
from exp142_flight_kit import pick_layouts
bk=_get_ibm_service().backend('ibm_marrakesh'); t=bk.target
twoq="cz" if "cz" in t.operation_names else "ecr"
errs=[getattr(i,"error",None) for i in t[twoq].values()]
errs=[e for e in errs if e is not None and e<1]
print(f"DEVICE-WIDE {twoq} error, n={len(errs)} edges")
print(f"  median {st.median(errs):.3e}   mean {st.mean(errs):.3e}   p10 {sorted(errs)[len(errs)//10]:.3e}")
print(f"  BORROWED value in use: 1.16e-3 (steth v5b, different circuit class)\n")
# the edges P1 / a stabilizer flight would actually be assigned
for n in (4,6,8):
    _,_,pairs=pick_layouts(bk,n)
    pe=[t[twoq][p].error for p in pairs if p in t[twoq]]
    pe=[e for e in pe if e is not None]
    if pe: print(f"  n={n} SELECTED pairs: mean {st.mean(pe):.3e}  worst {max(pe):.3e}")
print()
sel=st.mean([t[twoq][p].error for p in pick_layouts(bk,8)[2] if p in t[twoq] and t[twoq][p].error is not None])
print(f"LAMBDA_EFF measured on selected edges (n=8): {sel:.3e}   vs borrowed 1.16e-3  -> ratio {sel/1.16e-3:.2f}x\n")
print("ROBUSTNESS OF MY OWN #6180 CLAIM (P1 clears the budget):")
for lam,label in ((1.16e-3,"borrowed"),(sel,"measured-selected"),(st.median(errs),"device median"),(1.16e-2,"10x pessimistic")):
    budget=math.log(1/0.70)/lam
    print(f"  lambda={lam:.3e} ({label:18}) budget={budget:6.0f} gates | P1 n=8 uses 8 -> u={math.exp(-lam*8):.4f} {'PASS' if math.exp(-lam*8)>=0.70 else 'FAIL'}")
print()
print("DOOR (a) SENSITIVITY — stabilizer prep measured 41 (n=8) to ~64+ two-qubit gates:")
for lam,label in ((1.16e-3,"borrowed"),(sel,"measured-selected"),(1.16e-2,"10x pessimistic")):
    for g,gl in ((41,"n=8 generic"),(64,"n=8 A-G"),(200,"n=16 extrapolated")):
        u=math.exp(-lam*g)
        print(f"  lambda={lam:.3e} ({label:18}) {gl:18} {g:3}g -> u={u:.4f} {'PASS' if u>=0.70 else 'FAIL'}")
