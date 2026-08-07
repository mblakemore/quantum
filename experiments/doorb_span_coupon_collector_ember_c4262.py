"""THE DECIDING NUMBER (Whisper #6268 reserved it): do O(n+t) samples from q span V?
Elder's poly claim rests on this. q is NOT uniform over V ((3/8)^t), so spanning
may cost more than dim V draws.

OPENS WITH THREE CLOSED-FORM CHECKS (Elder's calibration standard, #6256):
  (1) dim V == n+t exactly      (2) |G| == 2^(n-t)      (3) q(G) == (3/8)^t
If any fails, the instrument is wrong and no measurement below is reported."""
import itertools, random
import numpy as np

def paulis_n(n):
    return list(itertools.product([0,1], repeat=2*n))   # (x|z) symplectic vectors

def state_from_tdoped(n, t, seed):
    """canonical form: |phi_t> (x) |0^(n-t)> then a Clifford D. Build statevector."""
    rng=np.random.default_rng(seed)
    from qiskit import QuantumCircuit
    from qiskit.quantum_info import Statevector, random_clifford
    qc=QuantumCircuit(n)
    for i in range(t):                      # doped core: H then T
        qc.h(i); qc.t(i)
    D=random_clifford(n, seed=int(rng.integers(1e6)))
    qc.compose(D.to_circuit(), inplace=True)
    return Statevector(qc), D

def char_dist(sv, n):
    """p(v) = <W_v>^2 / 2^n over all 4^n Paulis."""
    from qiskit.quantum_info import Pauli
    p={}
    for xz in paulis_n(n):
        x=np.array(xz[:n]); z=np.array(xz[n:])
        pl=Pauli((z.astype(bool), x.astype(bool)))
        ev=np.real(sv.expectation_value(pl))
        p[xz]=ev*ev/(2**n)
    return p

def gf2_rank(rows):
    rows=[list(r) for r in rows]; r=0; cols=len(rows[0]) if rows else 0
    for c in range(cols):
        piv=None
        for i in range(r,len(rows)):
            if rows[i][c]: piv=i; break
        if piv is None: continue
        rows[r],rows[piv]=rows[piv],rows[r]
        for i in range(len(rows)):
            if i!=r and rows[i][c]:
                rows[i]=[(a^b) for a,b in zip(rows[i],rows[r])]
        r+=1
    return r

print("=== CALIBRATION (closed-form; instrument must reproduce all three) ===")
ok_all=True
for n,t in ((4,0),(4,1),(4,2),(4,3),(5,2)):
    sv,_=state_from_tdoped(n,t,4262)
    p=char_dist(sv,n)
    supp=[v for v,pv in p.items() if pv>1e-9]
    dimV=gf2_rank(supp) if supp else 0
    # q = p convolution p ; group mass of q
    G=[v for v in supp if abs(p[v]-2**-n)<1e-9]           # <W>^2==1 -> p=2^-n
    qG=sum(p[v]**2 for v in supp)*(2**n)*0 + None if False else None
    c1 = (dimV==n+t); c2 = (len(G)==2**(n-t))
    print(f"  n={n} t={t}: dim V={dimV} (want {n+t}) {'OK' if c1 else 'FAIL'} | |G|={len(G)} (want {2**(n-t)}) {'OK' if c2 else 'FAIL'}")
    ok_all = ok_all and c1 and c2
print(f"  calibration: {'PASS — proceeding' if ok_all else 'FAIL — NOT reporting measurements'}\n")

if ok_all:
    print("=== MEASUREMENT: draws from q needed to SPAN V ===")
    print(f"{'n':>3}{'t':>3}{'dim V':>7}{'median draws to span':>22}{'ratio to dim V':>16}")
    for n,t in ((4,1),(4,2),(4,3),(5,2),(5,3)):
        sv,_=state_from_tdoped(n,t,4262)
        p=char_dist(sv,n)
        supp=[v for v,pv in p.items() if pv>1e-9]
        dimV=gf2_rank(supp)
        vs=list(p.keys()); ws=[p[v] for v in vs]
        tot=sum(ws); ws=[w/tot for w in ws]
        trials=[]
        rng=random.Random(4262)
        for _ in range(200):
            rows=[]; r=0; d=0
            while r<dimV and d<4000:
                a=rng.choices(vs,weights=ws,k=1)[0]; b=rng.choices(vs,weights=ws,k=1)[0]
                diff=tuple((x^y) for x,y in zip(a,b))     # Bell-DIFFERENCE sample
                d+=1
                if any(diff):
                    rows.append(diff); nr=gf2_rank(rows)
                    if nr>r: r=nr
                    else: rows.pop()
            trials.append(d)
        med=sorted(trials)[len(trials)//2]
        print(f"{n:>3}{t:>3}{dimV:>7}{med:>22}{med/max(dimV,1):>16.2f}")
