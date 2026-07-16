import numpy as np, itertools

I2=np.eye(2); X=np.array([[0,1],[1,0]],dtype=complex); Y=np.array([[0,-1j],[1j,0]]); Z=np.diag([1,-1]).astype(complex)
PAULI={'I':I2,'X':X,'Y':Y,'Z':Z}

def kron(*ops):
    r=np.array([[1]],dtype=complex)
    for o in ops: r=np.kron(r,o)
    return r

def pauli_op(s): return kron(*[PAULI[c] for c in s])

# Bell basis on one pair: |B_xz> = (I ⊗ X^x Z^z)|Phi+>
phip=np.array([1,0,0,1],dtype=complex)/np.sqrt(2)
def bell_state(x,z):
    op=kron(I2, X if x else I2) @ kron(I2, Z if z else I2)
    return op@phip

bells={(x,z):bell_state(x,z) for x in (0,1) for z in (0,1)}
# map bell outcome (x,z) to single-qubit Pauli label: (0,0)=I,(1,0)=X,(1,1)=Y,(0,1)=Z
lab={(0,0):'I',(1,0):'X',(1,1):'Y',(0,1):'Z'}

def verify(Pstr):
    n=len(Pstr)
    P=pauli_op(Pstr)
    rho=(np.eye(2**n)+P)/2**n
    # two copies: qubit order copy1 (q0..qn-1), copy2 (q0'..qn-1')
    rho2=np.kron(rho,rho)
    # transversal Bell measurement: pair (i, i+n)
    # build projector for outcome (x_i,z_i)_i as tensor over pairs, permuted into copy1/copy2 ordering
    dim=2**(2*n)
    # permutation: pair-ordered index (q0,q0',q1,q1',...) -> copy-ordered (q0..qn-1, q0'..qn-1')
    # We'll construct outcome vectors in pair ordering then permute axes.
    results={}
    total=0
    yc=Pstr.count('Y')
    ok=True
    for outs in itertools.product([(0,0),(1,0),(1,1),(0,1)],repeat=n):
        v=np.array([1],dtype=complex)
        for o in outs: v=np.kron(v,bells[o])
        # v is in ordering (q0,q0',q1,q1',...): reshape and transpose to copy ordering
        t=v.reshape([2]*(2*n))
        perm=[2*i for i in range(n)]+[2*i+1 for i in range(n)]
        t=np.transpose(t,perm)
        v2=t.reshape(dim)
        p=np.real(np.conj(v2)@rho2@v2)
        if p>1e-12:
            Q=''.join(lab[o] for o in outs)
            results[Q]=p; total+=p
    # check claim: support = Paulis Q that commute with P (or anticommute if odd Y-count), uniform
    # commutation of product paulis: sign = prod over sites of (+1 if commute at site else -1)
    def commutes(Q,Ps):
        s=1
        for q,p in zip(Q,Ps):
            if q!='I' and p!='I' and q!=p: s*=-1
        return s==1
    want_comm = (yc%2==0)
    support=set(results)
    expected={ ''.join(q) for q in itertools.product('IXYZ',repeat=n) if commutes(q,Pstr)==want_comm }
    uniform = np.allclose(list(results.values()), total/len(results))
    print(f"P={Pstr} (Y-count {yc}): support {'==' if support==expected else '!='} expected ({'commuting' if want_comm else 'anticommuting'} set, {len(expected)}), uniform={uniform}, total_p={total:.4f}")
    return support==expected and uniform

allok=True
for Pstr in ['XX','XY','YY','ZZ','XZ','XYZ','YYY','XYZX','YZXY']:
    allok &= verify(Pstr)
print("\nALL PASS" if allok else "\nMISMATCH FOUND")
