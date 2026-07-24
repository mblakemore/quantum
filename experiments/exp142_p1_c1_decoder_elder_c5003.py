#!/usr/bin/env python3
"""P1 First-Contact — FROZEN C1/SPRT single-copy decoder (Elder, for the C5003 pre-reg).

The classical-arm best-known-readout-robust decoder for the α=0.95 all-Paulis F119 re-fly. BLIND by
construction: identifies P from single-copy support-parity data; never takes the true P as input.
Committed BEFORE Ember seals (blind-protocol step 1). Elder's frozen lane pieces:

  (a) ALL-Paulis candidate set (Gate-A family fix): candidates = {I,X,Y,Z}^⊗n ∖ {I^⊗n}, 4^n−1 of them,
      in the committed canonical order below. (NOT the 3^n full-weight subset — the theorem's 1/(2^n+1)
      constant is verbatim only over ALL Paulis∖{I}; full-weight is a subset with a weaker floor.)
  (b) SUPPORT-parity fix (variable-weight): for a candidate P, the parity observable is over P's
      SUPPORT (qubits where P_i≠I) ONLY. Identity qubits are unmeasured/random and MUST NOT enter the
      parity (a low-weight P's I-qubits would inject fair coins and wash the signal — the reason the
      α=1 kit measured all-n was that P was full-weight; general P needs support-restriction).
  (c) α=0.95 true-basis rate: ideal support-parity even-rate for the true P on (I+0.95P)/2^n is
      p_ideal = (1+0.95)/2 = 0.975 (0.95 prob a +1-eig ⇒ even; 0.05 prob comp-basis ⇒ 1/2). The SPRT
      p0 is BILLED against the on-device single-copy rate PER-N (Ember rider 3: rate is a CURVE, not a
      flat tax) — p0(n) = 0.5 + 0.475·r_ro(n), r_ro(n) the measured single-copy readout retention at
      rung n from the flown control (NOT an average; a constant-p model understates n=8 erosion).
  (d) identify-P ≥ distinguish REDUCTION (Gate-A task-match): C1 = copies-to-identify is lower-bounded
      by the Def-2 distinguish floor Ω(2^n) via {run identify → verify ⟨P̂⟩}. C1 metric = median
      copies-to-stop; the Ω(2^n) floor is the theorem-over-access claim, C1 the measured best-known.

Def-2 distribution (Gate-A, verified verbatim from arXiv:2112.00778 App D.3.b / footnote):
  with prob ½  NULL:  ρ = I/2^n,            O = uniform Pauli∖{I},  |tr(Oρ)| = 0
  with prob ½  ALT:   ρ = (I + 0.95 s P)/2^n, O = P, s=±1, P uniform Pauli∖{I}, |tr(Oρ)| = 0.95
  (α=0.95 chosen off the authors' OPEN α=1 boundary; theorem covers "any constant < 1" verbatim.)
"""
import sys, math, itertools
import numpy as np

# ---- committed canonical candidate order: {I,X,Y,Z}^n minus all-I, lexicographic on "IXYZ" ----
def candidates(n):
    return ["".join(t) for t in itertools.product("IXYZ", repeat=n) if any(c != "I" for c in t)]

def support(P):                      # indices where P_i != I
    return [i for i, c in enumerate(P) if c != "I"]

def support_parity(bits, P):         # parity over P's support ONLY (identity qubits excluded)
    return int(sum(bits[i] for i in support(P))) & 1

def p_flip(w, q):                    # parity-readout flip prob over a weight-w support (odd # flips)
    return (1 - (1 - 2*q)**w) / 2

def p0_of(P, alpha, q):
    """PER-CANDIDATE α-and-weight true-basis support-parity even-prob. If candidate P were the true
    Pauli: ideal even-rate = (1+α)/2 (α from the shot-ensemble); readout flips the SUPPORT-parity w.p.
    p_flip(weight(P), q) — WEIGHT-DEPENDENT (a weight-8 support flips more than weight-2), so p0 is
    per-candidate, NOT a flat per-rung rate. (Distinct from Ember's TWO-copy Bell rate (1+α²)/2=0.9512;
    the C1 arm is SINGLE-copy → (1+α)/2=0.975 ideal.)"""
    e = (1 + alpha) / 2
    pf = p_flip(len([c for c in P if c != "I"]), q)
    return e * (1 - pf) + (1 - e) * pf

def wald_AB(n, eps_fa=0.01, eps_el=0.005):
    return math.log((4**n - 1) / eps_fa), math.log(eps_el)   # familywise-FA over 4^n-1 candidates

def sprt_identify(parities_by_cand, order, n, alpha, q):
    """Walk candidates in committed order; per-candidate Wald SPRT on its SUPPORT-parity stream, with
    the candidate's OWN weight-based p0. ACCEPT (LLR>=A)->P_hat; ELIMINATE (LLR<=B)->next."""
    A, B = wald_AB(n)
    used = 0
    for P in order:
        p0 = p0_of(P, alpha, q)                  # this candidate's own α+weight even-prob
        s_even, s_odd = math.log(p0/0.5), math.log((1-p0)/0.5)
        llr = 0.0
        for par in parities_by_cand[P]:          # par = support-parity for THIS candidate
            used += 1
            llr += s_even if par == 0 else s_odd
            if llr >= A: return P, used
            if llr <= B: break
    return None, used

def two_copy_Q(bell_constraint_rate_stream, n, r_bell):
    """Q meter: two-copy Bell symplectic-constraint rate (Ember G3 arm). O(1)-ish; copies-to-confirm
    billed against the on-device Bell rate r_bell(n) (0.933/0.882/0.846), NOT ideal 1.0."""
    A = math.log((4**n - 1)/0.01)
    s_pass = math.log(r_bell/0.5); s_fail = math.log((1-r_bell)/0.5)
    llr = 0.0; used = 0
    for hit in bell_constraint_rate_stream:
        used += 1
        llr += s_pass if hit else s_fail
        if llr >= A: return used
    return used

# ---- decode driver (blind): flown data -> C1 (identify) + Q (two-copy) meters, P-blind ----
def decode(flown, n, alpha, q_single, r_bell):
    """flown: {candidate_P: [support-parity bits]} per candidate (single-copy measurements in each
    candidate's eigenbasis) + flown['_bell'] the two-copy constraint stream. NO true-P input.
    alpha=0.95 (spec); q_single = SINGLE-copy readout error/qubit (per-n from flown control); r_bell =
    two-copy Bell constraint-rate (per-n, Ember G3, distinct from the single-copy arm)."""
    order = candidates(n)
    P_hat, c1 = sprt_identify({P: flown[P] for P in order}, order, n, alpha, q_single)
    q = two_copy_Q(flown.get("_bell", []), n, r_bell)
    return {"n": n, "P_hat": P_hat, "C1_copies_to_identify": c1, "Q_copies": q,
            "alpha": alpha, "q_single": q_single, "r_bell_used": r_bell,
            "p0_of_Phat": (p0_of(P_hat, alpha, q_single) if P_hat else None),
            "candidates": 4**n - 1,
            "note": "C1>=Omega(2^n) via identify>=distinguish; C1 arm bills SINGLE-copy per-candidate "
                    "weight p0=(1+a)/2 flip-adj; Q arm bills TWO-copy Bell (1+a^2)/2; margin=C1/Q per-n"}

if __name__ == "__main__":
    print("P1 FROZEN C1/SPRT decoder — BLIND, all-Paulis, support-parity, α=0.95, PER-CANDIDATE-weight p0.")
    a = 0.95
    for n, qs in [(4, 0.004), (6, 0.005), (8, 0.006)]:   # illustrative single-copy readout/qubit
        A, B = wald_AB(n)
        # p0 for a weight-n (worst) vs weight-2 candidate at this q
        p0_hi = p0_of("X"*n, a, qs); p0_lo = p0_of("X"*2 + "I"*(n-2), a, qs)
        print(f"  n={n}: cand={4**n-1}  p0(w={n})={p0_hi:.3f}  p0(w=2)={p0_lo:.3f}  (ideal 0.975) Wald A={A:.2f} B={B:.2f}")
    print("  C1 single-copy (1+α)/2=0.975 ideal ≠ Ember two-copy Bell (1+α²)/2=0.9512 — distinct arms.")
    print("  Def-2 distribution + identify≥distinguish reduction as in the C5003 pre-reg (Gate-A verbatim).")


# ============================================================================================
# COVERING-DECODE driver (Elder, post-#1247 — keeps emission at 3^n, Creator ~240-job auth intact).
# The 3^n FULL-WEIGHT bases are a COVERING SET for all 4^n-1 candidates: a candidate P (support S) is
# read from any full-weight basis A that AGREES with P on S (3^(n-w) such bases). So emit 3^n
# full-weight bases (NOT 4^n-1 per-candidate), and EXTRACT every candidate's support-parity from the
# covering measurements. C1 = DISTINCT full-weight COPIES consumed (a copy reused across candidates it
# covers is ONE copy) — the honest best-known-classical count; per-candidate-basis emission OR
# per-candidate-bit counting would INFLATE C1 = inflate our own advantage (Ember c4215_002 tripwire).
# Frozen SPRT logic (p0_of / wald_AB / support_parity) UNCHANGED — this is the emission->decode map.
# ============================================================================================
def full_weight_bases(n):
    return ["".join(t) for t in itertools.product("XYZ", repeat=n)]      # 3^n, committed lex order

def covers(A, P):                     # full-weight basis A covers candidate P iff A agrees with P on P's support
    return all(A[i] == P[i] for i in support(P))

def covering_decode(fw_shots, n, alpha, q):
    """fw_shots: {full_weight_basis A: [shot_bits,...]} — the 3^n emitted bases, C shots each. BLIND.
    Walks all 4^n-1 candidates (frozen SPRT, per-candidate weight p0); each candidate's parity stream
    is EXTRACTED from its covering bases; C1 = DISTINCT (basis,shot) copies consumed across the walk."""
    A_wald, B_wald = wald_AB(n)
    order = candidates(n); fwb = full_weight_bases(n)
    cov = {P: [Ab for Ab in fwb if covers(Ab, P)] for P in order}         # covering bases per candidate
    consumed = set()                                                     # DISTINCT (basis, shot_idx) copies
    P_hat = None
    for P in order:
        p0 = p0_of(P, alpha, q); s_even, s_odd = math.log(p0/0.5), math.log((1-p0)/0.5)
        llr = 0.0; stop = False
        # consume covering shots in committed order: basis-lex, then shot-index
        for Ab in cov[P]:
            for si, bits in enumerate(fw_shots[Ab]):
                consumed.add((Ab, si))                                    # one physical copy (reused across candidates it covers)
                par = support_parity(bits, P)
                llr += s_even if par == 0 else s_odd
                if llr >= A_wald: P_hat = P; stop = True; break
                if llr <= B_wald: stop = True; break                      # eliminate -> next candidate
            if stop: break
        if P_hat is not None: break
    return {"n": n, "P_hat": P_hat, "C1_distinct_copies": len(consumed),
            "emission_bases": 3**n, "candidates_walked": 4**n - 1, "alpha": alpha,
            "note": "emission=3^n covering (Creator ~240 auth INTACT); C1=distinct copies (honest, "
                    "not per-candidate-bit sum); frozen SPRT logic unchanged"}


# ============================================================================================
# FLOWN-DATA DETERMINISM RED-TEAM (Elder decode lane, per Whisper #1259 attack-reframe). BLIND.
# The exp142b determinism attack read a FIXED-BASIS-BATCH's deterministic parity to identify P cheaply.
# The α=0.95 shot-ensemble (shots=1, fresh-per-row) defeats it STRUCTURALLY — but this confirms the
# EXECUTED data actually reflects that (no hardware/pipeline bug collapsed freshness into a leak).
# Two blind statistics; post-reveal, both must show NO recovery of the true P:
#   (1) within-basis MODAL frequency: fresh (I+0.95P)/2^n over a basis spreads outcomes over ~2^(n-1)
#       even-parity states -> modal freq LOW; a fixed-draw batch collapses to ~1 outcome -> modal ~1.0.
#   (2) determinism-attack GUESS: pick the candidate whose support-parity is most anomalously
#       deterministic in its SINGLE most-deterministic covering basis (what the attack would exploit).
#       On fresh data this is ~chance; post-reveal, guess==true_P >> chance = a delivery leak.
# ============================================================================================
def determinism_redteam(fw_shots, n):
    fwb = full_weight_bases(n)
    # (1) within-basis modal frequency (fixed-batch leak signature)
    modal = {}
    for A in fwb:
        shots = fw_shots[A]
        if not shots: continue
        keyed = {}
        for b in shots:
            k = tuple(b); keyed[k] = keyed.get(k, 0) + 1
        modal[A] = max(keyed.values()) / len(shots)
    max_modal = max(modal.values()) if modal else 0.0
    fresh_expected = 1.0 / (2 ** (n - 1))                 # even-parity states share the mass ~uniformly
    leak_by_modal = max_modal > 0.5                        # way above fresh_expected for n>=2 => fixed batch
    # (2) determinism-attack guess (blind): candidate most-deterministic in its best single covering basis
    best_cand, best_det = None, 0.0
    for P in candidates(n):
        for A in fwb:
            if not covers(A, P): continue
            pars = [support_parity(b, P) for b in fw_shots[A]]
            if not pars: continue
            det = abs(sum(1 for x in pars if x == 0) / len(pars) - 0.5)  # distance from chance in ONE basis
            if det > best_det: best_det, best_cand = det, P
    # LEAK CRITERION = statistic (1) ONLY. The fixed-batch signature (modal>>fresh_expected) is what
    # enables CHEAP recovery beating the Ω(2^n) floor. Statistic (2) attack_guess is INFORMATIONAL, NOT
    # a leak criterion: on fresh data the attack DOES recover P — via the legitimate α-signal at FLOOR
    # cost (that is the C1 signal, not a leak). Only recovery CHEAPER than the floor (a fixed-batch
    # shortcut) is a leak, and that shows up as modal>>fresh_expected. Do NOT read guess==true_P as a leak.
    return {"n": n, "max_within_basis_modal_freq": round(max_modal, 4),
            "fresh_expected_modal": round(fresh_expected, 4),
            "LEAK": bool(leak_by_modal),                  # <-- the verdict: fixed-batch determinism only
            "attack_guess_INFORMATIONAL": best_cand, "attack_single_basis_det": round(best_det, 4),
            "verdict_note": "LEAK iff max_within_basis_modal_freq >> fresh_expected (fixed-batch shortcut "
                            "beats the floor). attack_guess is INFORMATIONAL — legit floor-cost recovery of "
                            "true_P is NOT a leak; only fixed-batch CHEAP recovery is, detected by modal."}
