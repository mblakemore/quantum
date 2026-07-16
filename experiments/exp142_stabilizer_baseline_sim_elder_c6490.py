import numpy as np, itertools

rng=np.random.default_rng(20260716)

def sympl_prod(a,b,n):
    # a,b: (...,2n) bit arrays, form = x.z' + z.x' mod 2
    return (a[...,:n]&b[...,n:]).sum(-1)%2 ^ (a[...,n:]&b[...,:n]).sum(-1)%2

def rand_max_isotropic(n):
    gens=[]
    while len(gens)<n:
        v=rng.integers(0,2,2*n)
        if not v.any(): continue
        if gens:
            G=np.array(gens)
            if sympl_prod(G,v[None,:].repeat(len(gens),0),n).any(): continue
            # independence: reduce v against span via gaussian elim
            M=np.vstack([G,v])
            r=np.linalg.matrix_rank(M.astype(float))  # over reals is not F2! do F2 elim
            if f2_rank(M)!=len(gens)+1: continue
        gens.append(v)
    return np.array(gens)

def f2_rank(M):
    M=M.copy()%2; r=0
    for c in range(M.shape[1]):
        piv=None
        for i in range(r,M.shape[0]):
            if M[i,c]: piv=i;break
        if piv is None: continue
        M[[r,piv]]=M[[piv,r]]
        for i in range(M.shape[0]):
            if i!=r and M[i,c]: M[i]^=M[r]
        r+=1
        if r==M.shape[0]: break
    return r

def f2_solve(G,y):
    # solve a·G = y (a: n bits, G: n x 2n), returns a or None
    n=G.shape[0]; A=np.concatenate([G.T, y[:,None]],axis=1)%2  # 2n x (n+1)
    A=A.copy(); piv=[]
    r=0
    for c in range(n):
        p=None
        for i in range(r,A.shape[0]):
            if A[i,c]: p=i;break
        if p is None: piv.append(None); continue
        A[[r,p]]=A[[p,r]]
        for i in range(A.shape[0]):
            if i!=r and A[i,c]: A[i]^=A[r]
        piv.append(r); r+=1
    a=np.zeros(n,dtype=int)
    # back-substitute: for each col with pivot row, a[c]=A[pivrow,-1]; check consistency rows
    for c,p in enumerate(piv):
        if p is not None: a[c]=A[p,-1]
    # verify
    if ((a@G)%2!=y%2).any(): return None
    return a

def candidates_fullweight(n):
    # encode X=(1,0) Y=(1,1) Z=(0,1) per site -> 2n bits [x | z]
    combos=np.array(list(itertools.product([(1,0),(1,1),(0,1)],repeat=n)))
    x=combos[:,:,0]; z=combos[:,:,1]
    return np.concatenate([x,z],axis=1)

def stab_trial(n,C):
    m=len(C)
    idxP=rng.integers(0,m); P=C[idxP]
    alive=np.ones(m,bool)
    shots=0
    while alive.sum()>1:
        G=rand_max_isotropic(n)
        shots+=1
        # covered candidates: commute with all generators
        # sympl of each candidate with each generator:
        s=( (C[:,None,:n]&G[None,:,n:]).sum(-1) + (C[:,None,n:]&G[None,:,:n]).sum(-1) )%2
        covered=(s==0).all(axis=1)&alive
        if not covered.any(): continue
        aP=f2_solve(G,P) if covered[idxP] else None
        e=rng.integers(0,2,n)
        if aP is not None and (e@aP)%2==1:
            flip=np.where(aP==1)[0][0]; e[flip]^=1  # enforce eig(P)=+1
        for i in np.where(covered)[0]:
            if i==idxP: continue
            a=f2_solve(G,C[i])
            if a is not None and (e@a)%2==1:
                alive[i]=False
    return shots

def product_trial(n):
    # eliminate-on-first-odd over all 3^n bases, threshold confirm true basis
    wrong=3**n-1
    sh=rng.geometric(0.5,size=wrong).sum()
    return sh + int(1.6*n+7)

print("PRODUCT-BASIS elimination MC (reconcile Finding 2):")
for n in [8,10]:
    t=[product_trial(n) for _ in range(30)]
    print(f"  n={n}: mean shots = {np.mean(t):,.0f}  (analytic ~2*3^n = {2*3**n:,}; Whisper table: {6782 if n==8 else 64069:,})")

print("\nSTABILIZER-basis elimination MC:")
for n,tr in [(4,30),(6,15),(8,5)]:
    C=candidates_fullweight(n)
    t=[stab_trial(n,C) for _ in range(tr)]
    print(f"  n={n}: mean shots = {np.mean(t):,.0f} (vs product-elim ~{2*3**n:,}; 2^(n+1)*n*ln3 estimate = {int(2**(n+1)*n*np.log(3)):,})")
