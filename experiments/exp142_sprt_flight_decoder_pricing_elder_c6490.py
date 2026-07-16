import numpy as np
rng=np.random.default_rng(7)
# n=8: q_true = P(odd parity on true basis) from readout flips: parity flips if odd # of bit flips
# r=1.5% per-bit -> P(odd flips)= (1-(1-2r)^n)/2
n=8; r=0.015
q=(1-(1-2*r)**n)/2
print(f"n={n}, per-bit readout r={r} -> q_true (odd-parity rate on TRUE basis) = {q:.3f}")
LLe=np.log((1-q)/0.5); LLo=np.log(q/0.5)
Nb=3**n
def sprt_run(A,B,trials=200):
    tot=[];succ=0
    for _ in range(trials):
        order=rng.permutation(Nb); true_idx=order[0]*0  # position of true basis uniform: pick random slot
        pos=rng.integers(0,Nb)
        shots=0; found=None
        for i in range(Nb):
            is_true=(i==pos)
            llr=0.0
            while True:
                shots+=1
                odd = rng.random() < (q if is_true else 0.5)
                llr += LLo if odd else LLe
                if llr>=A: found=('accept',is_true); break
                if llr<=B: break  # eliminate
            if found: break
        succ += (found is not None and found[1])
        tot.append(shots)
    return np.mean(tot),succ/trials
for A,B in [(np.log(Nb*100),-3),(np.log(Nb*100),-4.6),(np.log(Nb*100),-6)]:
    m,s=sprt_run(A,B)
    print(f"SPRT A={A:.1f} B={B}: mean shots={m:,.0f} ({m/Nb:.2f}x 3^n), success={s:.2%}")
# fixed-m threshold comparison
from math import comb,log
def fixed_m_cost(alpha_fw=0.01,beta=0.01):
    a_loc=alpha_fw/Nb
    for m in range(5,200):
        # best threshold t
        for t in range(m//2+1,m+1):
            aa=sum(comb(m,k) for k in range(t,m+1))*0.5**m
            bb=sum(comb(m,k)*( (1-q)**k*q**(m-k) ) for k in range(0,t))
            if aa<=a_loc and bb<=beta: return m,t
    return None
mt=fixed_m_cost()
print(f"fixed-m threshold: m={mt[0]}/basis -> expected total ≈ {mt[0]*Nb//2:,} (half of bases tried before true) vs SPRT above")
