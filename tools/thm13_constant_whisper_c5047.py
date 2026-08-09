"""MEASURE Theorem 13's constant.
Vectorised via the symplectic encoding:  P <-> (x,z) bits, I=(0,0) X=(1,0) Z=(0,1) Y=(1,1)
  lambda_P(Q) = (-1)^(x_P.z_P)          [ = (-1)^#Y(P), the transpose factor ]
              * (-1)^(x_P.z_Q + z_P.x_Q) [ = commutation sign, symplectic form ]
  Bell outcome prob for pure psi:  p(Q) = |psi^T Q^dag psi|^2 / d     (d-dim, not d^2)
Both identities are CHECKED against direct linear algebra at n=2,3 before use.
"""
import numpy as np, itertools, math
I2=np.eye(2); Xm=np.array([[0,1],[1,0]],complex)
Ym=np.array([[0,-1j],[1j,0]]); Zm=np.array([[1,0],[0,-1]],complex)
PD={'I':I2,'X':Xm,'Y':Ym,'Z':Zm}; BITS={'I':(0,0),'X':(1,0),'Z':(0,1),'Y':(1,1)}
def pauli(l):
    M=np.array([[1]],complex)
    for c in l: M=np.kron(M,PD[c])
    return M
def enc(labs):
    x=np.array([[BITS[c][0] for c in l] for l in labs],dtype=np.int64)
    z=np.array([[BITS[c][1] for c in l] for l in labs],dtype=np.int64)
    return x,z
def signmat(x,z):
    self_=(x*z).sum(1)%2                       # #Y(P) mod 2
    cross=(x@z.T + z@x.T)%2                    # symplectic form
    return (1-2*self_)[:,None]*(1-2*cross)     # +-1, shape (|A|,|A|)

# ---- validate both shortcuts against direct linear algebra -----------------
for n in (2,3):
    labs=[''.join(t) for t in itertools.product('IXYZ',repeat=n)]
    d=2**n; L=signmat(*enc(labs))
    phi=np.zeros(d*d,complex)
    for i in range(d): phi[i*d+i]=1/np.sqrt(d)
    okL=True
    for i,p in enumerate(labs):
        PP=np.kron(pauli(p),pauli(p))
        for j,q in enumerate(labs):
            v=np.kron(pauli(q),np.eye(d))@phi
            if abs(np.vdot(v,PP@v).real-L[i,j])>1e-9: okL=False
    rng0=np.random.default_rng(3)
    psi=rng0.normal(size=d)+1j*rng0.normal(size=d); psi/=np.linalg.norm(psi)
    pp=np.kron(psi,psi)
    direct=np.array([abs(np.vdot(np.kron(pauli(q),np.eye(d))@phi,pp))**2 for q in labs])
    fast=np.array([abs(psi@(pauli(q).conj().T@psi))**2/d for q in labs])
    print(f"  check n={n}: sign matrix exact={okL}   "
          f"prob formula max err={np.abs(direct-fast).max():.2e}   sum p={fast.sum():.6f}")

# ---- measure ---------------------------------------------------------------
EPS,DELTA=0.3,0.05
rng=np.random.default_rng(23)
print(f"\n  eps={EPS} delta={DELTA}; a trial FAILS if ANY of the 4^n estimates misses by >eps\n")
for n,TR in ((4,400),(5,400),(6,200),(7,120)):
    labs=[''.join(t) for t in itertools.product('IXYZ',repeat=n)]
    d=2**n
    psi=rng.normal(size=d)+1j*rng.normal(size=d); psi/=np.linalg.norm(psi)
    L=signmat(*enc(labs)).astype(np.float32)
    ytrue=np.array([abs(np.vdot(psi,pauli(p)@psi).real)**2 for p in labs])
    pr=np.array([abs(psi@(pauli(q).conj().T@psi))**2/d for q in labs])
    pr=np.maximum(pr,0); pr/=pr.sum()
    st=np.sqrt(ytrue).astype(np.float32)
    sder=2*math.log(2*(4**n)/DELTA)/EPS**4
    out=[]
    for m in (0.15,0.20,0.25,0.30,0.40,0.60,1.0):
        ns=max(1,int(sder*m)); f=0
        for _ in range(TR):
            yh=(L@rng.multinomial(ns,pr).astype(np.float32))/ns
            if np.abs(np.sqrt(np.maximum(yh,0))-st).max()>EPS: f+=1
        out.append((m,ns,f/TR))
    print(f"  n={n}  derived-sufficient = {sder:.0f} shots  (trials={TR})")
    print("        "+"  ".join(f"{m:.2f}x:{r:>5.1%}" for m,_,r in out))
    x=next((m for m,_,r in out if r<=0.05),None)
    print(f"        -> crosses 5% at ~{x:.2f}x of derived  =>  proof conservative by ~{1/x:.1f}x\n"
          if x else "        -> no crossing in grid\n")
