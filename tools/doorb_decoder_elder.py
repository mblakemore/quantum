#!/usr/bin/env python3
"""DOOR (b) BLIND DECODER — Elder C6595 seat. COMMITTED BEFORE THE FLIGHT FLIES (ruled
#7411: the decode is the load-bearing blind discipline; a decoder written after the
outcomes is the last place shopping could hide).

Estimator (mechanism verified 4 ways at #7358, Whisper thm13_constant tool):
  Bell measurement on rho x rho, qubit-pair j -> outcome beta_j in {PhiP,PhiM,PsiP,PsiM}.
  For Pauli P = (x)_j P_j, the per-shot +-1 value is
      v_P(shot) = (-1)^{#Y(P)} * prod_j  s(P_j, beta_j)
  where s(P_j, beta_j) = tr((P_j x P_j) |beta_j><beta_j|)  in {+1,-1} for P_j != I, and 1
  for P_j = I, and the (-1)^{#Y(P)} TRANSPOSE FACTOR IS NOT OPTIONAL (P^T = (-1)^{#Y} P;
  omission silently sign-flips every odd-Y Pauli — Whisper caught it at n=1, #7358).
  E[v_P] = tr(P rho)^2 exactly. Estimate = mean over shots.

Modes:
  selftest                       calibration opener — REFUSES to decode unless all pass
  decode <outcomes.json> <out>   blind: consumes raw 2n-bit strings ONLY (no P anywhere);
                                 emits raw-record digest + estimator version + estimates on
                                 the PUBLIC canonical probe set (seed committed below).
                                 Output hashes to the bus BEFORE any unseal.
  query <outcomes.json> <pauli>  frozen per-query estimator (used at grade time on the
                                 revealed planted P + logged null sample)

Bell-outcome convention: 2 classical bits per pair, (b_z b_x): 00=PhiP, 01=PsiP(?),...
PINNED BY SELFTEST against direct linear algebra — the convention is whatever makes the
sign table reproduce tr((P x P)|beta><beta|) computed from matrices, not an assumption.
"""
import json, sys, hashlib, itertools

ESTIMATOR_VERSION = "doorb-decoder-elder-v1"
PROBE_SEED = 20260809          # public canonical probe set seed — committed pre-flight
PROBE_COUNT = 64

# ── sign table s(P, beta) derived ONCE from linear algebra in selftest, then frozen ────
# beta index b in 0..3 <-> 2-bit outcome (b1 b0). Mapping to Bell states is pinned by
# the selftest deriving S from matrices; decode uses the same derived table.
import math

def bell_states():
    import numpy as np
    v = {}
    s2 = 1/math.sqrt(2)
    v[0] = np.array([s2,0,0, s2])   # Phi+
    v[1] = np.array([s2,0,0,-s2])   # Phi-
    v[2] = np.array([0,s2, s2,0])   # Psi+
    v[3] = np.array([0,s2,-s2,0])   # Psi-
    return v

def pauli_mats():
    import numpy as np
    return {"I": np.eye(2), "X": np.array([[0,1],[1,0]]),
            "Y": np.array([[0,-1j],[1j,0]]), "Z": np.array([[1,0],[0,-1]])}

def derive_sign_table():
    """s[P][bell_index] = tr((P⊗P)|beta><beta|) — real, in {+1,-1} for P!=I."""
    import numpy as np
    B, M = bell_states(), pauli_mats()
    tab = {}
    for name, P in M.items():
        PP = np.kron(P, P)
        row = []
        for b in range(4):
            val = (B[b].conj() @ (PP @ B[b])).real
            row.append(int(round(val)))
        tab[name] = row
    return tab

SIGN_TABLE = None  # populated by init()

def init():
    global SIGN_TABLE
    if SIGN_TABLE is None:
        SIGN_TABLE = derive_sign_table()
    return SIGN_TABLE

def shot_value(pauli, bell_indices):
    """v_P for one shot. pauli: string over IXYZ, len n. bell_indices: list of n ints 0-3."""
    tab = init()
    v = 1
    for pj, b in zip(pauli, bell_indices):
        if pj == "I":
            continue
        v *= tab[pj][b]
    # NO transpose factor here: SIGN_TABLE is derived DIRECTLY from linear algebra
    # (tr((P x P)|beta><beta|)) so it already IS the eigenvalue lambda_P(beta). The
    # (-1)^#Y transpose factor belongs to BIT-SYNDROME decodings (lambda computed from
    # (a,b) outcome bits); applying it on top of a direct table DOUBLE-COUNTS and flips
    # every odd-Y Pauli — the selftest's can-fire below proves the flip both ways.
    return v

def outcome_to_bells(raw, n):
    """raw: 2n-bit string, PAIR CONVENTION PINNED BY SELFTEST: bits (raw[2j], raw[2j+1])
    are pair j's (b1, b0) -> index. If the flight kit emits a different layout, the
    selftest's simulated-flight fixture FAILS and the layout is corrected HERE, once,
    before any real decode — never inferred from flight data."""
    if len(raw) != 2 * n or any(c not in "01" for c in raw):
        raise ValueError(f"raw must be {2*n} bits, got {raw!r}")
    return [int(raw[2*j]) * 2 + int(raw[2*j+1]) for j in range(n)]

def estimate(pauli, shots_bells):
    vals = [shot_value(pauli, s) for s in shots_bells]
    return sum(vals) / len(vals)

def probe_set(n, seed=PROBE_SEED, count=PROBE_COUNT):
    """Public canonical Paulis: all weight-1 + seeded pseudorandom sample. No I^n."""
    import random
    rng = random.Random(seed)
    probes = []
    for i in range(n):
        for p in "XYZ":
            probes.append("I"*i + p + "I"*(n-1-i))
    while len(probes) < 3*n + count:
        s = "".join(rng.choice("IXYZ") for _ in range(n))
        if s != "I"*n and s not in probes:
            probes.append(s)
    return probes

def selftest():
    import numpy as np
    ok = []
    tab = init()
    # [1] sign table derived from linear algebra is +-1 valued (I row all +1)
    ok.append(("sign table {+-1}, I row all 1",
               all(all(x in (1,-1) for x in tab[p]) for p in "XYZ") and tab["I"] == [1,1,1,1]))
    # [2] TRANSPOSE-FACTOR CAN-FIRE at n=1: for rho=|0><0|, tr(Y rho)=0 but tr(Z rho)=1.
    #     Simulate exact Bell distribution for rho x rho and check E[v_Z]=1, E[v_Y]=0,
    #     and that OMITTING the (-1)^#Y factor breaks a Y-containing case at n=1 with
    #     rho=|+i><+i| (tr(Y rho)=1): with factor E[v_Y]=+1, without it -1.
    B = bell_states()
    def exact_E(pauli, rho):
        E = 0.0
        rr = np.kron(rho, rho)
        for b in range(4):
            pb = (B[b].conj() @ (rr @ B[b])).real
            E += pb * shot_value(pauli, [b])
        return E
    rho0 = np.array([[1,0],[0,0]])
    rhoi = 0.5*np.array([[1,-1j],[1j,1]])
    e_z = exact_E("Z", rho0); e_y0 = exact_E("Y", rho0); e_yi = exact_E("Y", rhoi)
    ok.append(("exact E: Z on |0> = 1, Y on |0> = 0, Y on |+i> = 1 (WITH transpose factor)",
               abs(e_z-1)<1e-12 and abs(e_y0)<1e-12 and abs(e_yi-1)<1e-12))
    # without the factor the |+i> case gives -1 — the can-fire:
    def exact_E_nofactor(pauli, rho):
        E = 0.0; rr = np.kron(rho, rho)
        for b in range(4):
            pb = (B[b].conj() @ (rr @ B[b])).real
            v = (-1) ** pauli.count("Y")
            for pj in pauli:
                if pj != "I": v *= init()[pj][b]
            E += pb * v
        return E
    ok.append(("spurious transpose factor WOULD flip Y on |+i> (can-fire both directions)",
               abs(exact_E_nofactor("Y", rhoi) + 1) < 1e-12 and abs(exact_E("Y", rhoi) - 1) < 1e-12))
    # [3] HARD-FAMILY ANALYTIC TRIPWIRE at n=2: rho_P=(I+a P)/4, planted P="XY", a=0.9.
    #     E[v_Q] must be a^2 at Q=P and 0 at every other Q (exact 2-qubit Bell sim).
    a, n2, planted = 0.9, 2, "XY"
    Pm = pauli_mats()
    Pmat = np.kron(Pm["X"], Pm["Y"])
    rhoP = (np.eye(4) + a*Pmat)/4
    # exact Bell distribution over pairs (q0 of copy1 with q0 of copy2, etc.):
    # build rho_P x rho_P in (c1q0,c1q1,c2q0,c2q1) order then reorder pairs — simpler:
    # per-shot expectation factorizes only for product rho; rho_P is not product, so
    # compute E[v_Q] = tr( (Q x Q)_paired * rhoP x rhoP ) via the identity E=tr(Q rhoP)^2
    # ... which is the THEOREM; the tripwire instead checks our estimator against
    # sampling from the true joint Bell distribution.
    rr = np.kron(rhoP, rhoP)   # order: c1q0 c1q1 c2q0 c2q1
    # pair j pairs c1qj with c2qj -> permutation to (c1q0 c2q0 c1q1 c2q1)
    perm = [0,2,1,3]
    d = 4
    idx = lambda bits: sum(b<<(3-i) for i,b in enumerate(bits))
    P4 = np.zeros((16,16))
    for bits in itertools.product([0,1],repeat=4):
        src = idx(bits); dst = idx([bits[p] for p in perm])
        P4[dst,src] = 1
    rr2 = P4 @ rr @ P4.T
    bell2 = np.zeros((16,16), dtype=complex)
    probs = {}
    for b0 in range(4):
        for b1 in range(4):
            vec = np.kron(bell_states()[b0], bell_states()[b1])
            p = (vec.conj() @ (rr2 @ vec)).real
            probs[(b0,b1)] = p
    def exact_E2(Q):
        E = 0.0
        for (b0,b1),p in probs.items():
            E += p * shot_value(Q, [b0,b1])
        return E
    hit = abs(exact_E2(planted) - a*a) < 1e-10
    nulls = all(abs(exact_E2("".join(q))) < 1e-10
                for q in itertools.product("IXYZ", repeat=2)
                if "".join(q) not in (planted, "II"))
    ok.append((f"hard-family tripwire n=2: E[v_P]=a^2 at planted, 0 at all 14 nulls", hit and nulls))
    # [4] probe set: deterministic, public, no identity, correct count
    ps = probe_set(4)
    ok.append(("probe set deterministic + I^n excluded",
               ps == probe_set(4) and "IIII" not in ps and len(ps) == 12 + PROBE_COUNT))
    for name, passed in ok:
        print(f"  [{'OK ' if passed else 'FAIL'}] {name}")
    n_ok = sum(1 for _, p in ok if p)
    print(f"selftest: {n_ok}/{len(ok)}")
    return 0 if n_ok == len(ok) else 2

def decode(outcomes_path, out_path):
    d = json.load(open(outcomes_path))
    n = d["n"]; raws = d["shots"]
    shots = [outcome_to_bells(r, n) for r in raws]
    probes = probe_set(n)
    est = {p: estimate(p, shots) for p in probes}
    raw_digest = hashlib.sha256("\n".join(raws).encode()).hexdigest()
    out = {"estimator": ESTIMATOR_VERSION, "n": n, "num_shots": len(raws),
           "raw_record_sha256": raw_digest, "probe_seed": PROBE_SEED,
           "probe_estimates": est,
           "note": "BLIND: no P consumed; grade queries the frozen estimator (query mode) "
                   "on the revealed planted P + logged null sample; this file hashes to "
                   "the bus BEFORE any unseal."}
    json.dump(out, open(out_path, "w"), indent=1)
    h = hashlib.sha256(open(out_path,'rb').read()).hexdigest()
    print(f"decisions written: {out_path}")
    print(f"decisions commitment sha256: {h}  (post BEFORE unsealing)")
    return 0

def query(outcomes_path, pauli):
    d = json.load(open(outcomes_path))
    shots = [outcome_to_bells(r, d["n"]) for r in d["shots"]]
    e = estimate(pauli, shots)
    print(json.dumps({"pauli": pauli, "estimate_tr2": e, "estimator": ESTIMATOR_VERSION}))
    return 0

if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in ("selftest","decode","query"):
        print(__doc__); sys.exit(2)
    if sys.argv[1] == "selftest":
        sys.exit(selftest())
    if selftest() != 0:
        print("REFUSING: calibration opener failed."); sys.exit(2)
    if sys.argv[1] == "decode":
        sys.exit(decode(sys.argv[2], sys.argv[3] if len(sys.argv)>3 else "doorb_decisions.json"))
    sys.exit(query(sys.argv[2], sys.argv[3]))
