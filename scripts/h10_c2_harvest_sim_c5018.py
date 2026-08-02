#!/usr/bin/env python3
"""H10-C2 HARVESTING — $0 exact-sim campaign (Whisper C5018, Creator "Run the C2 scout").

Scout: docs/h10-c2-entanglement-harvesting-scout-whisper-c5018.md (design + frozen kill
conditions SS5). This script IS the campaign: exact evolution of an XX-chain "field" (L
qubits, ground state = the lattice vacuum) plus two UDW detector qubits, swept over
(d, T, lambda, Omega, switching), with the cone certified by the exact response front and
the A4 product-state control computed per candidate operating point.

Objects:
  field    H_f = J sum_j (X_j X_{j+1} + Y_j Y_{j+1})/2,  J=1, open chain, L=8
  detector H_d = Omega |e><e| per detector (|e> = |1>), ground |0>
  coupling H_int(t) = lam*env(t) [ X_{s1} X_d1 + X_{s2} X_d2 ]  (UDW, sigma_x x field-X)
  switching env: tophat (sudden) and sine ramp sin(pi t/T) (smooth; the VERIFIED
  Pozas-Kerstjens/Martin-Martinez pin predicts smooth >> sudden for spacelike windows —
  an imported prediction the sweep TESTS rather than assumes)
  front    delta<X_{s2}>(t) after a unit X kick at s1 on the vacuum (field only) — the
           empirical cone; eps_front(d,T) = max_{t<=T} |response|
Outputs per config: detector negativity N, concurrence, P_e (both), plus the front table
and A4 (field = |0..0> product) twins for the shortlist. Kill conditions are evaluated
exactly as frozen in scout SS5.
"""
import itertools, json, os, sys
import numpy as np
import scipy.sparse as sp
from scipy.sparse.linalg import expm_multiply, eigsh

# L=8 primary campaign (SS7); L=6 re-sweep is the depth-compliance leg (SS7c: L=8 prices
# over the C1-calibrated 475-gate ceiling; L=6 projects under). argv override: sys.argv[1].
L = int(sys.argv[1]) if len(sys.argv) > 1 else 8
J = 1.0
NQ = L + 2                      # field sites 0..L-1, detectors at axes L (d1), L+1 (d2)
DIM = 2 ** NQ

I2 = sp.identity(2, format="csr", dtype=complex)
Xs = sp.csr_matrix(np.array([[0, 1], [1, 0]], complex))
Ys = sp.csr_matrix(np.array([[0, -1j], [1j, 0]]))
Ns = sp.csr_matrix(np.diag([0, 1]).astype(complex))   # |e><e| with |e>=|1>

def op_at(op, q, n=NQ):
    mats = [I2] * n; mats[q] = op
    out = mats[0]
    for m in mats[1:]:
        out = sp.kron(out, m, format="csr")
    return out

def field_H(n=NQ, cut_bond=None):
    """cut_bond=j removes the (j, j+1) bond — the CUT evolution: same initial vacuum, zero
    exchange channel between the halves BY CONSTRUCTION. N under cut evolution isolates the
    vacuum-resource harvest; N_full - N_cut IS the exchange contribution, exactly — the
    operational sharpening of the scout SS2 lightcone fence (no tail bound to argue)."""
    H = sp.csr_matrix((2 ** n, 2 ** n), dtype=complex)
    for j in range(L - 1):
        if j == cut_bond: continue
        H = H + J / 2 * (op_at(Xs, j, n) @ op_at(Xs, j + 1, n)
                         + op_at(Ys, j, n) @ op_at(Ys, j + 1, n))
    return H

def vacuum():
    """Ground state of the field chain alone (2^L), embedded with detectors |00>."""
    Hf_only = sp.csr_matrix((2 ** L, 2 ** L), dtype=complex)
    XsL = lambda q: op_at(Xs, q, L); YsL = lambda q: op_at(Ys, q, L)
    for j in range(L - 1):
        Hf_only = Hf_only + J / 2 * (XsL(j) @ XsL(j + 1) + YsL(j) @ YsL(j + 1))
    w, v = eigsh(Hf_only, k=1, which="SA")
    vac = v[:, 0]
    psi = np.zeros(DIM, complex)
    psi[np.arange(2 ** L) * 4] = vac       # detectors = last two qubits, state |00>
    return psi, float(w[0]), vac

HF = field_H()
DET_H = lambda Om: Om * (op_at(Ns, L) + op_at(Ns, L + 1))
def build_static(Om, cut_bond=None):
    return (HF if cut_bond is None else field_H(cut_bond=cut_bond)) + DET_H(Om)

def couple_op(s1, s2):
    return op_at(Xs, s1) @ op_at(Xs, L) + op_at(Xs, s2) @ op_at(Xs, L + 1)

def evolve(psi0, H0, Hc, lam, T, env, nsteps=32):
    psi = psi0.copy()
    dt = T / nsteps
    for k in range(nsteps):
        tm = (k + 0.5) * dt
        ek = 1.0 if env == "tophat" else float(np.sin(np.pi * tm / T))
        Hk = H0 + lam * ek * Hc
        psi = expm_multiply(-1j * dt * Hk, psi)
    return psi

def det_rho(psi):
    m = psi.reshape(2 ** L, 4)
    return m.conj().T @ m

def negativity(rho):
    pt = rho.reshape(2, 2, 2, 2).transpose(0, 3, 2, 1).reshape(4, 4)  # partial transpose on d2
    ev = np.linalg.eigvalsh(pt)
    return float(-2 * ev[ev < 0].sum() / 2)     # = sum |negative eigenvalues|

def concurrence(rho):
    YY = np.kron(np.array([[0, -1j], [1j, 0]]), np.array([[0, -1j], [1j, 0]]))
    R = rho @ YY @ rho.conj() @ YY
    ev = np.sqrt(np.abs(np.sort(np.linalg.eigvals(R).real)[::-1]))
    return float(max(0.0, ev[0] - ev[1] - ev[2] - ev[3]))

def front_table(s1, ts):
    """Field-only exact causal front: R(q,t) = |<vac| [X_q(t), X_{s1}] |vac>| = 2|Im <vac|
    X_q(t) X_{s1}|vac>| — the retarded X-X commutator, which is EXACTLY the channel the
    UDW detectors couple through (both couplings are X-type), so the fence bounds the very
    operator that could carry exchange.

    TWO DEAD-OBSERVABLE LESSONS FROM THE FIRST RUNS, kept in place:
    (1) <X_{s2}(t)> after a FULL X kick is a three-X correlator — X-parity-ODD on the XX
        chain, identically zero by symmetry at ANY (d,t); it faked 'spacelike' everywhere.
        Resolution: the linear-response amplitude goes as sin(2*eps) — the pi/2 kick sits at
        the NULL; the hardware arm uses eps = pi/4 where it is maximal.
    (2) delta<Z_q(t)> after the kick is ALSO identically zero at half filling — the added
        particle and added hole spread with opposite density sign and cancel by
        particle-hole symmetry.
    A cone certifier must be checked NONZERO on a causal case before its zeros mean
    anything — a certifier that reads zero everywhere certifies nothing."""
    HfL = sp.csr_matrix((2 ** L, 2 ** L), dtype=complex)
    XL = lambda q: op_at(Xs, q, L); YL = lambda q: op_at(Ys, q, L)
    for j in range(L - 1):
        HfL = HfL + J / 2 * (XL(j) @ XL(j + 1) + YL(j) @ YL(j + 1))
    _, E0f, vac = (lambda t: t)(vacuum())
    kicked = op_at(Xs, s1, L) @ vac
    out = {}
    psi = kicked.copy(); ph = vac.copy()
    t_prev = 0.0
    for t in ts:
        step = t - t_prev
        psi = expm_multiply(-1j * step * HfL, psi)
        ph = expm_multiply(-1j * step * HfL, ph); t_prev = t
        out[round(t, 3)] = {q: float(2 * abs(np.imag(np.vdot(ph, op_at(Xs, q, L) @ psi))))
                            for q in range(L)}
    return out

def run():
    psi0, E0, vac = vacuum()
    prod = np.zeros(DIM, complex); prod[0] = 1.0     # field |0..0> x detectors |00>
    s1 = 2 if L >= 8 else 1
    DLIST = (3, 4, 5) if L >= 8 else (2, 3)
    out = {"L": L, "J": J, "s1": s1, "E0_field": E0,
           "convention": "detectors = last two qubits; |e>=|1>; ground |00>",
           "rows": [], "front": {}, "A4_shortlist": [], "convergence": {}}
    # cone table: response front for each distance of interest
    ts = [0.25 * k for k in range(1, 13)]
    ft = front_table(s1, ts)
    out["front"] = {"ts": ts, "response": ft}
    Hc_cache = {}
    for d in DLIST:
        s2 = s1 + d
        Hc_cache[d] = couple_op(s1, s2)
    for Om in (0.5, 1.0, 1.5):
        H0 = build_static(Om)
        for d in DLIST:
            s2 = s1 + d
            eps = {round(t, 3): abs(ft[round(t, 3)][s2]) for t in ts}
            for T in (0.5, 1.0, 1.5, 2.0, 2.5):
                ef = max(v for k, v in eps.items() if k <= T + 1e-9)
                cutb = s1 + d // 2                      # bond between the detector sites
                H0cut = build_static(Om, cut_bond=cutb)
                for lam in (0.2, 0.4, 0.6):
                    for env in ("tophat", "sine"):
                        psi = evolve(psi0, H0, Hc_cache[d], lam, T, env)
                        rho = det_rho(psi)
                        N = negativity(rho); C = concurrence(rho)
                        pe1 = float(np.real(rho[1, 1] + rho[3, 3]))
                        pe2 = float(np.real(rho[2, 2] + rho[3, 3]))
                        psic = evolve(psi0, H0cut, Hc_cache[d], lam, T, env)
                        Ncut = negativity(det_rho(psic))
                        out["rows"].append({"Om": Om, "d": d, "T": T, "lam": lam, "env": env,
                                            "N": N, "C": C, "Pe1": pe1, "Pe2": pe2,
                                            "N_cut": Ncut,
                                            "exch_frac": (abs(N - Ncut) / N if N > 1e-12 else None),
                                            "eps_front": ef,
                                            "front_ratio": (ef / N if N > 1e-12 else None)})
    # convergence check on one mid config
    cfg = dict(Om=1.0, d=DLIST[1], T=1.5, lam=0.4, env="sine")
    for ns in (32, 64):
        psi = evolve(psi0, build_static(cfg["Om"]), Hc_cache[cfg["d"]], cfg["lam"],
                     cfg["T"], cfg["env"], nsteps=ns)
        out["convergence"][f"nsteps{ns}"] = negativity(det_rho(psi))
    # shortlist: best CUT-evolution harvests (zero exchange channel by construction),
    # ranked by N_cut — the registrable signal; + A4 product-state twins (cut evolution)
    ok = [r for r in out["rows"] if r["N_cut"] > 1e-6]
    ok.sort(key=lambda r: -r["N_cut"])
    for r in ok[:8]:
        cutb = s1 + r["d"] // 2
        psiA4 = evolve(prod, build_static(r["Om"], cut_bond=cutb), Hc_cache[r["d"]],
                       r["lam"], r["T"], r["env"])
        rhoA4 = det_rho(psiA4)
        out["A4_shortlist"].append({**{k: r[k] for k in ("Om", "d", "T", "lam", "env", "N",
                                                          "N_cut", "exch_frac", "eps_front")},
                                    "N_product_control": negativity(rhoA4),
                                    "C_product_control": concurrence(rhoA4)})
    suffix = "" if L == 8 else f"_L{L}"
    json.dump(out, open(os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                     "..", "results", f"h10_c2_harvest_sim_c5018{suffix}.json"),
                        "w"), indent=1, default=float)
    print(f"vacuum E0 = {E0:.4f}; configs = {len(out['rows'])}; "
          f"convergence 32v64: {out['convergence']}")
    print("top CUT-evolution harvests (zero exchange by construction):")
    for r in out["A4_shortlist"]:
        print(f"  Om={r['Om']} d={r['d']} T={r['T']} lam={r['lam']} {r['env']:6s} "
              f"N_cut={r['N_cut']:.5f} (N_full={r['N']:.5f}, exch_frac={r['exch_frac']:.2f}) "
              f"N_A4={r['N_product_control']:.5f}")
    if not out["A4_shortlist"]:
        best = sorted(out["rows"], key=lambda r: -r["N"])[:5]
        print("NO cut-evolution harvest found; best full rows:")
        for r in best:
            print(f"  Om={r['Om']} d={r['d']} T={r['T']} lam={r['lam']} {r['env']} "
                  f"N={r['N']:.5f} N_cut={r['N_cut']:.6f}")
    return 0

if __name__ == "__main__":
    sys.exit(run())
