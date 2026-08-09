#!/usr/bin/env python3
"""Door (b) hard-ensemble prep — exactness check (Whisper C5048, $0 sim).

Verifies: rho_P = (I + 3*eps*P)/2^n is EXACTLY the classical mixture
  with prob (1+3eps)/2 : a uniformly random +1 PRODUCT eigenstate of P
  with prob (1-3eps)/2 : a uniformly random -1 PRODUCT eigenstate of P
(each tensor-Pauli eigenstate factorizes locally; I-factors take a random Z-basis state).
Therefore the ruled ensemble (#7389) needs ZERO two-qubit gates to prepare:
per-shot randomized single-qubit preps, seeded and recorded.

Two fences this construction demands (in the prereg, as asserts):
  F-IND: the two copies' random draws must be INDEPENDENT (separate seeds, both
         recorded). Correlated draws deliver E[sigma x sigma] != rho x rho with an
         EXTRA P-correlation term - an error in the flattering direction.
  F-BIAS: the mixing bias (1+3eps)/2 vs (1-3eps)/2 is the load-bearing line. A
         sign-randomization bug (uniform instead of biased) delivers EXACTLY I/2^n
         - a candidate mechanism for the exp142c wash class. Deserves an n=1
         selftest assert next to the transpose-factor assert.
"""
import numpy as np, itertools, sys
I=np.eye(2); X=np.array([[0,1],[1,0]]); Y=np.array([[0,-1j],[1j,0]]); Z=np.diag([1,-1]).astype(complex)
PA={'I':I,'X':X,'Y':Y,'Z':Z}
def kron(*o):
    r=o[0]
    for m in o[1:]: r=np.kron(r,m)
    return r
def local_eigvecs(p):
    w,v=np.linalg.eigh(PA[p])
    if p=='I': return {(+1):[v[:,0],v[:,1]],(-1):[]}
    return {(+1):[v[:,np.argmax(w)]],(-1):[v[:,np.argmin(w)]]}
def check(pstr, eps=0.3):
    n=len(pstr); P=kron(*[PA[c] for c in pstr])
    target=(np.eye(2**n)+3*eps*P)/2**n
    states=[]
    for choices in itertools.product(*[[('+',w) for w in local_eigvecs(c)[+1]]+[('-',w) for w in local_eigvecs(c)[-1]] for c in pstr]):
        sign=1; vec=np.array([1.0+0j])
        for s,w in choices:
            if s=='-': sign*=-1
            vec=np.kron(vec,w)
        states.append((sign,np.outer(vec,vec.conj())))
    plus=[r for s,r in states if s>0]; minus=[r for s,r in states if s<0]
    mix=(1+3*eps)/2*sum(plus)/len(plus)+((1-3*eps)/2*sum(minus)/len(minus) if minus else 0)
    return float(np.abs(mix-target).max())
if __name__=="__main__":
    fams=sys.argv[1:] or ['ZZ','XZ','YX','ZI','XI','XYZ','ZIZ']
    for f in fams:
        d=check(f)
        print(f"{f}: max_dev {d:.2e}  {'OK' if d<1e-12 else 'FAIL'}")
    assert all(check(f)<1e-12 for f in fams)
    print("EXACT: ruled ensemble = zero-2q randomized product preps")
