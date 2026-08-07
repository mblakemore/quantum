"""RE-DERIVE the u>=0.70 gate for THIS circuit class (two-copy purity witness),
instead of inheriting it from the retired steth card. $0, analytic."""
import math
def z(p):  # inverse normal, Acklam-lite via bisection
    lo,hi=-10,10
    for _ in range(200):
        m=(lo+hi)/2
        c=0.5*(1+math.erf(m/math.sqrt(2)))
        if c<p: lo=m
        else: hi=m
    return (lo+hi)/2
ZA, ZB = z(0.975), z(0.90)          # two-sided alpha=0.05, power 90%
print("PURITY WITNESS (Elder #6216): accept prob = (1 + tr rho^2)/2")
print("  NULL  maximally mixed : p0 = 1/2 + 2^-(n+1)")
print("  ALT   pure, decohered : p1 = (1 + u)/2\n")
n=8
p0=0.5+2**-(n+1)
print(f"n={n}: p0 = {p0:.5f}\n")
print(f"{'u':>6} {'p1':>8} {'gap':>8} {'SHOTS for a=0.05,pow=0.90':>28} {'copies (2/shot)':>17}")
prev=None
for u in (0.95,0.90,0.85,0.80,0.75,0.7148,0.70,0.65,0.60,0.50,0.40,0.30,0.20,0.10):
    p1=(1+u)/2; d=p1-p0
    pbar=(p0+p1)/2
    num=(ZA*math.sqrt(2*pbar*(1-pbar)) + ZB*math.sqrt(p0*(1-p0)+p1*(1-p1)))**2
    N=num/d**2
    print(f"{u:>6.3f} {p1:>8.4f} {d:>8.4f} {N:>28.0f} {2*N:>17.0f}")
print()
print("THE POINT: shots ~ 1/gap^2 ~ 1/u^2. There is NO discontinuity at 0.70.")
print("u=0.70 costs 1.00x the shots of u=0.70 (by definition); u=0.50 costs")
u50=( (ZA*math.sqrt(2*((p0+(1.5)/2)/2)*(1-((p0+(1.5)/2)/2))) + ZB*math.sqrt(p0*(1-p0)+((1+0.5)/2)*(1-(1+0.5)/2)))**2 )/(((1+0.5)/2)-p0)**2
u70=( (ZA*math.sqrt(2*((p0+(1.7)/2)/2)*(1-((p0+(1.7)/2)/2))) + ZB*math.sqrt(p0*(1-p0)+((1+0.7)/2)*(1-(1+0.7)/2)))**2 )/(((1+0.7)/2)-p0)**2
print(f"  u=0.50 needs {u50/u70:.2f}x the shots of u=0.70 — a COST RATIO, not a failure.")
