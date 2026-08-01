#!/usr/bin/env python3
"""H10-C1 WINDING METER — $0 exact-sim campaign (Whisper C5016, Creator go "Run them").

Purpose (scout §6.2): establish IN EXACT THEORY, before any prereg, whether a measurable
size-winding window exists at our scale for a Hamiltonian WE choose (non-commuting, no ML),
and freeze the numbers the arms' bars would come from.

Objects (Schuster et al. PRX 12, 031013 conventions, checked against the paper's text):
  thermal operator      O(t) = Q(t) rho^{1/2},  Q = X on site 0,  rho = e^{-bH}/Z  (one side)
  Pauli coefficients    c_chi = Tr[chi O] / sqrt(2^N)         (chi = N-site Pauli strings)
  size distribution     q(S)  = sum_{|chi|=S} |c_chi|^2       (normalized to 1 after /sum)
  WINDING distribution  f(S)  = sum_{|chi|=S} c_chi^2         (complex; carries the phases)
  two-point function    G_b   = Tr[rho^{1/2} Q rho^{1/2} Q]
  perfect winding       arg f(S) linear in S  (slope -2*alpha)

KNOWN-ANSWER GATES (today's method — the instrument proves itself before it measures):
  KA1: sum_S f(S) must equal G_b  (analytic identity; conventions wrong => mismatch)
  KA2: at beta=0, rho^{1/2} ~ I => all c_chi real => every winding phase == 0 exactly

CAMPAIGN:
  A. chaotic H (mixed-field Ising, J=1, hx=1.05, hz=0.5), N=4: scan (beta,t); fit
     arg f(S) ~ -2*alpha*S; report window where weight is spread AND fit is linear.
  B. unwinding check: C(g) = sum_S f(S) e^{i g S}; argmax_g |C| vs the fit's 2*alpha.
  C. commuting twin (hx=0): the KSY-artifact arm — winding may look 'perfect' here;
     that is the point (fly the artifact, labeled).
  D. beta=0 arm: winding must be ABSENT (KA2 doubles as the arm's prediction).
"""
import itertools, json
import numpy as np

I2 = np.eye(2); X = np.array([[0,1],[1,0]],complex)
Y = np.array([[0,-1j],[1j,0]]); Z = np.diag([1,-1]).astype(complex)
P1 = {'I':I2,'X':X,'Y':Y,'Z':Z}

def kron(*ops):
    out = np.array([[1]],complex)
    for o in ops: out = np.kron(out,o)
    return out

def ising(N, J=1.0, hx=1.05, hz=0.5):
    H = np.zeros((2**N,2**N),complex)
    for i in range(N-1):
        H += J*kron(*[Z if k in (i,i+1) else I2 for k in range(N)])
    for i in range(N):
        H += hx*kron(*[X if k==i else I2 for k in range(N)])
        H += hz*kron(*[Z if k==i else I2 for k in range(N)])
    return H

def paulis(N):
    for combo in itertools.product('IXYZ',repeat=N):
        yield ''.join(combo), kron(*[P1[c] for c in combo])

def winding(H, beta, t, N, Q):
    w,v = np.linalg.eigh(H)
    rho_h = (v*np.exp(-beta*w/2))@v.conj().T          # e^{-bH/2}
    rho_h /= np.sqrt(np.trace(rho_h@rho_h).real)       # normalize so Tr[rho]=1 overall
    U = (v*np.exp(-1j*w*t))@v.conj().T
    Qt = U@Q@U.conj().T
    O = Qt@rho_h
    fS = {}; qS = {}
    for name,chi in paulis(N):
        c = np.trace(chi@O)/np.sqrt(2**N)
        S = sum(ch!='I' for ch in name)
        fS[S] = fS.get(S,0)+c*c
        qS[S] = qS.get(S,0)+abs(c)**2
    Gb = np.trace(rho_h@Q@rho_h@Q)
    return fS,qS,Gb

def fit_alpha(fS, wmin=1e-4):
    Ss = sorted(S for S in fS if S>0 and abs(fS[S])>wmin)
    if len(Ss)<3: return None,None,Ss
    ph = np.unwrap([np.angle(fS[S]) for S in Ss])
    A = np.vstack([Ss,np.ones(len(Ss))]).T
    coef,res,*_ = np.linalg.lstsq(A,ph,rcond=None)
    resid = float(np.sqrt(np.mean((A@coef-ph)**2)))
    return -coef[0]/2.0, resid, Ss        # slope = -2 alpha

def run():
    N=4; Q=kron(X,I2,I2,I2)
    out={"N":N,"Q":"X on site 0","H":"mixed-field Ising J=1 hx=1.05 hz=0.5",
         "known_answer":{}, "campaign":[]}
    H=ising(N)

    # KA1+KA2 at (beta=0, t=1.3)
    fS,qS,Gb = winding(H,0.0,1.3,N,Q)
    ka1 = abs(sum(fS.values())-Gb)
    maxph0 = max(abs(np.angle(fS[S])) for S in fS if abs(fS[S])>1e-9)
    out["known_answer"]={"KA1_sumf_minus_Gb_beta0": float(ka1),
                         "KA2_max_winding_phase_beta0": float(maxph0)}
    # KA1 must also hold at finite beta
    fS,qS,Gb = winding(H,1.0,1.3,N,Q)
    out["known_answer"]["KA1_sumf_minus_Gb_beta1"]=float(abs(sum(fS.values())-Gb))

    # A: (beta,t) scan on chaotic H
    for beta in (0.3,0.6,1.0,1.6):
        for t in (0.6,1.0,1.5,2.2,3.0):
            fS,qS,Gb = winding(H,beta,t,N,Q)
            alpha,resid,Ss = fit_alpha(fS)
            # B: unwinding — argmax_g |sum f(S) e^{igS}|
            gs = np.linspace(-3.2,3.2,1281)
            Cg = [abs(sum(fS[S]*np.exp(1j*g*S) for S in fS)) for g in gs]
            gstar = float(gs[int(np.argmax(Cg))])
            spread = sum(1 for S in fS if S>0 and abs(fS[S])>1e-3)
            out["campaign"].append({"H":"chaotic","beta":beta,"t":t,
                "Gb":float(Gb.real),"alpha_fit":None if alpha is None else float(alpha),
                "phase_fit_rms":resid if resid is None else float(resid),
                "g_star":gstar,"two_alpha":None if alpha is None else float(2*alpha),
                "S_support":spread,
                "unwind_gain":float(max(Cg)/abs(sum(fS.values()))) })
    # C: commuting twin
    Hc=ising(N,hx=0.0)
    for beta,t in ((1.0,1.5),(1.0,3.0)):
        fS,qS,Gb=winding(Hc,beta,t,N,Q)
        alpha,resid,Ss=fit_alpha(fS)
        out["campaign"].append({"H":"commuting_twin","beta":beta,"t":t,
            "Gb":float(Gb.real),"alpha_fit":None if alpha is None else float(alpha),
            "phase_fit_rms":resid if resid is None else float(resid),
            "S_support":sum(1 for S in fS if S>0 and abs(fS[S])>1e-3)})
    json.dump(out,open("../results/h10_c1_winding_sim_c5016.json","w"),indent=1)
    print("KNOWN-ANSWER:",out["known_answer"])
    ok=(out["known_answer"]["KA1_sumf_minus_Gb_beta0"]<1e-9 and
        out["known_answer"]["KA1_sumf_minus_Gb_beta1"]<1e-9 and
        out["known_answer"]["KA2_max_winding_phase_beta0"]<1e-9)
    print("GATES:","PASS" if ok else "FAIL — DO NOT READ THE CAMPAIGN")
    if ok:
        best=[r for r in out["campaign"] if r["H"]=="chaotic" and r["alpha_fit"] is not None]
        best.sort(key=lambda r:(r["phase_fit_rms"] if r["phase_fit_rms"] else 9))
        for r in best[:5]:
            print(f"  beta={r['beta']:.1f} t={r['t']:.1f}  alpha={r['alpha_fit']:+.3f} "
                  f"rms={r['phase_fit_rms']:.3f}  g*={r['g_star']:+.2f} vs 2a={r['two_alpha']:+.2f} "
                  f"S_supp={r['S_support']} gain={r['unwind_gain']:.2f} Gb={r['Gb']:.3f}")
    return 0

if __name__=="__main__":
    import os; os.chdir(os.path.dirname(os.path.abspath(__file__)))
    raise SystemExit(run())
