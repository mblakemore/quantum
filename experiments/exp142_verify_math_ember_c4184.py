import numpy as np, itertools
I2=np.eye(2); X=np.array([[0,1],[1,0]],dtype=complex); Y=np.array([[0,-1j],[1j,0]]); Z=np.diag([1,-1]).astype(complex)
PAULI={'I':I2,'X':X,'Y':Y,'Z':Z}
def kron(ops):
    m=np.array([[1]],dtype=complex)
    for o in ops: m=np.kron(m,o)
    return m
def pauli_mat(s): return kron([PAULI[c] for c in s])

n=3
rng=np.random.default_rng(42)
results=[]
for trial in range(3):
    P=''.join(rng.choice(list('XYZ'),n))
    Pm=pauli_mat(P); d=2**n
    rho=(np.eye(d)+Pm)/d

    # CLAIM 1: rho_P == uniform mixture over even-parity product eigenstates
    mix=np.zeros((d,d),dtype=complex)
    cnt=0
    for b in itertools.product([0,1],repeat=n):
        if sum(b)%2: continue
        cnt+=1
        psi=np.array([1.0+0j])
        for i,c in enumerate(P):
            w,v=np.linalg.eigh(PAULI[c])
            # eigenvalue +1 for b=0, -1 for b=1
            idx=np.argmax(w) if b[i]==0 else np.argmin(w)
            psi=np.kron(psi,v[:,idx])
        mix+=np.outer(psi,psi.conj())
    mix/=cnt
    claim1=np.allclose(mix,rho,atol=1e-12)

    # CLAIM 1b: every proper-subset marginal maximally mixed (check all single and n-1 subsets)
    claim1b=True
    for k in range(1,n):
        for keep in itertools.combinations(range(n),k):
            t=rho.reshape([2]*(2*n))
            # partial trace over qubits not in keep
            trace_out=[q for q in range(n) if q not in keep]
            m=t
            for q in sorted(trace_out,reverse=True):
                m=np.trace(m,axis1=q,axis2=q+ (m.ndim//2))
            dk=2**k
            m=m.reshape(dk,dk)
            if not np.allclose(m,np.eye(dk)/dk,atol=1e-12): claim1b=False

    # CLAIM 2: transversal Bell measurement on rho x rho -> uniform over Q with QP=+PQ (or -,if odd Y count)
    D=d*d
    phi=np.zeros(D,dtype=complex)
    for j in range(d): phi[j*d+j]=1
    phi/=np.sqrt(d)
    probs={}
    for Q in itertools.product('IXYZ',repeat=n):
        Qs=''.join(Q); Qm=pauli_mat(Qs)
        bell=np.kron(Qm,np.eye(d))@phi
        p=np.real(bell.conj()@ (np.kron(rho,rho)@bell))
        probs[Qs]=p
    tot=sum(probs.values())
    # commutation of product paulis: anticommute count per site
    def commutes(Qs,Ps):
        anti=sum(1 for q,p in zip(Qs,Ps) if q!='I' and q!=p)
        return anti%2==0
    ycount=P.count('Y')
    support = [q for q,p in probs.items() if p>1e-12]
    expect_comm = (ycount%2==0)
    all_match=all(commutes(q,P)==expect_comm for q in support)
    uniform=np.allclose([probs[q] for q in support],1/len(support),atol=1e-10)
    results.append((P,claim1,claim1b,len(support),all_match,uniform,round(tot,6)))
    print(f"P={P} (Ycount={ycount}): claim1(mixture)={claim1} claim1b(marginals)={claim1b} "
          f"|support|={len(support)} (2^n*2^(n-?)...) outcomes_{'commute' if expect_comm else 'ANTIcommute'}_with_P={all_match} uniform={uniform} totprob={tot:.4f}")

# CLAIM 3: ~2n+O(1) shots identify P via F2 Gaussian elimination (sim over random commuting Q)
# Each outcome Q gives symplectic constraint <Q,P>=0 (mod known sign). Unknowns: P in {X,Y,Z}^n -> 2n bits (x,z per site, not both 0).
# Simulate: draw uniform Q from commuting set, count shots until unique P consistent.
def pauli_to_xz(s):
    x=[]; z=[]
    for c in s:
        x.append(1 if c in 'XY' else 0); z.append(1 if c in 'ZY' else 0)
    return np.array(x+z)%2
def symp(u,v,n):
    return (u[:n]@v[n:]+u[n:]@v[:n])%2
for n2 in [4,6,8]:
    shots_needed=[]
    for t in range(200):
        P2=''.join(rng.choice(list('XYZ'),n2)); pv=pauli_to_xz(P2)
        cons=[]; shots=0
        # candidate set implicitly: count rank; P identified when constraint matrix rank=... simulate directly
        while True:
            # draw uniform random Q from full Pauli group commuting appropriately: rejection sample
            while True:
                q=rng.integers(0,2,2*n2)
                if symp(q,pv,n2)== (0 if P2.count('Y')%2==0 else 1): break
            cons.append(q); shots+=1
            A=np.array(cons)%2
            # solve: find all pv' in {X,Y,Z}^n consistent -> brute force too big; use rank argument:
            # constraints linear in pv'; solution space dim = 2n - rank. P unique among XYZ-strings when rank>=2n-? 
            # do rank check: if rank == 2n-1 (P determined up to scalar since <q,P>=c linear system), declare
            r=np.linalg.matrix_rank(A.astype(float))  # over reals approximates F2 poorly; do F2 rank properly
            # F2 rank:
            M=A.copy()%2; rk=0; m=M.copy(); rows,cols=m.shape; c0=0
            for c in range(cols):
                piv=None
                for r2 in range(rk,rows):
                    if m[r2,c]: piv=r2; break
                if piv is None: continue
                m[[rk,piv]]=m[[piv,rk]]
                for r2 in range(rows):
                    if r2!=rk and m[r2,c]: m[r2]=(m[r2]+m[rk])%2
                rk+=1
            if rk>=2*n2-1: break  # solution space <=2, XYZ-constraint (no I) pins P
            if shots>10*n2: break
        shots_needed.append(shots)
    print(f"n={n2}: median shots to rank 2n-1 = {np.median(shots_needed)} (claim ~2n+O(1) = {2*n2}+O(1)), p90={np.percentile(shots_needed,90)}")
