import numpy as np, itertools, random

# --- Part A: proper-subset marginals of rho_P are maximally mixed ---
I2=np.eye(2); X=np.array([[0,1],[1,0]],dtype=complex); Y=np.array([[0,-1j],[1j,0]]); Z=np.diag([1,-1]).astype(complex)
PAULI={'I':I2,'X':X,'Y':Y,'Z':Z}
def kron(*ops):
    r=np.array([[1]],dtype=complex)
    for o in ops: r=np.kron(r,o)
    return r
def ptrace_keep(rho,n,keep):
    t=rho.reshape([2]*(2*n))
    drop=[i for i in range(n) if i not in keep]
    for d in sorted(drop,reverse=True):
        t=np.trace(t,axis1=d,axis2=d+ (t.ndim//2))
    k=len(keep); return t.reshape(2**k,2**k)
okA=True
for Pstr in ['XYZ','YYZ','XYZX']:
    n=len(Pstr); P=kron(*[PAULI[c] for c in Pstr]); rho=(np.eye(2**n)+P)/2**n
    for r in range(1,n):
        for keep in itertools.combinations(range(n),r):
            m=ptrace_keep(rho,n,list(keep))
            if not np.allclose(m, np.eye(2**len(keep))/2**len(keep)): okA=False; print("FAIL",Pstr,keep)
print("Part A (proper-subset marginals maximally mixed): " + ("ALL PASS" if okA else "FAIL"))

# --- Part B: MC of ideal quantum shots-to-ID (uniform Q from (anti)commuting set) ---
rng=np.random.default_rng(6490)
def trial(n, cands):
    P=rng.integers(0,3,n)  # 0=X,1=Y,2=Z
    # sample Q uniform over 4^n Paulis conditioned on fixed symplectic value vs P
    # per-site: Q_i in {I,X,Y,Z} (0..3 with 0=I, 1=X,2=Y,3=Z); mismatch bit = (Q_i!=I) & (Q_i != P_i+1)
    consistent=np.ones(len(cands),bool)
    shots=0; c_hyp=None
    # candidate mismatch precompute per shot
    while True:
        while True:
            Q=rng.integers(0,4,n)
            par=int(np.sum((Q!=0)&(Q!=P+1))%2)
            # true parity is same every shot: 0 if even Y-count handled implicitly — accept Q whose parity vs P equals target
            # target = parity of first accepted shot? No: physically ALL outcomes share the same parity vs P.
            # even-Y P -> all Q commute (par 0); odd-Y -> par 1. Compute Y-count:
            target = int(np.sum(P==1)%2)
            if par==target: break
        shots+=1
        # update consistency: candidate P' consistent iff parity(Q,P') equal across all shots (shared c) 
        parc = ((Q[None,:]!=0)&(Q[None,:]!=cands+1)).sum(1)%2
        if shots==1:
            first_par=parc.copy()
        else:
            consistent &= (parc==first_par)
        if consistent.sum()==1: return shots
def run(n,trials):
    cands=np.array(list(itertools.product(range(3),repeat=n)))
    res=[trial(n,cands) for _ in range(trials)]
    return np.mean(res)
for n,t in [(4,400),(6,300),(8,150),(10,60)]:
    print(f"n={n}: mean ideal quantum shots = {run(n,t):.1f}  (Whisper table: {dict([(4,8.7),(6,12.6),(8,16.5),(10,20.5)])[n]})")
