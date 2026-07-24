#!/usr/bin/env python3
"""Exp142b conventional-arm emission delta (Ember C4215) — the F119 remedy re-fly kit.

Delta on the FROZEN exp142 kit; everything not here is inherited verbatim. Court-frozen spec:
  - shots=1, fresh even-parity b PER COPY (item 1): each copy is its own conv param row.
  - BLIND STATIC emission (catch #6): P is sealed, so we cannot vary copies/basis (leaks P).
    Emit a UNIFORM C copies per basis over the committed random basis order; C sized from the
    MEASURED readout q_n so the grade-time SPRT (Elder Wald A=n*ln3+ln100, B=ln0.005) confirms
    the true basis. emission-L = C*3^n per rep (flown; the SPRT BILLS copies-to-stop, ~3x less).
  - grid: n=4/6 at M=20, n=8 at M=5 (ALPHA). One sealed P per rung, M disjoint decode blocks.
  - canonical manifest: row-index + basis + shots only (P-independent; no P, no angles).
The GRADER (SPRT decoder + attack gate + meter) is Elder's frozen seat, not here. This module
only EMITS the blind conventional pubs. Reuses conv_template/conv_param_rows/named_rows verbatim.
"""
import numpy as np, itertools, sys, os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import exp142_flight_kit as K   # frozen kit: conv_template, conv_param_rows, named_rows, angle tables

GRID = {4: 20, 6: 20, 8: 5}     # ALPHA: (rung -> M)

def p_flip(n, e):
    return (1 - (1 - 2*e)**n) / 2

def confirm_C(n, q_n, pct=99.0, trials=20000, seed=99):
    """Uniform copies/basis = p99 of the MEASURED true-basis SPRT confirm-stop distribution.
    CATCH #7 (Whisper K7): the mean-sized C (A/E[step]+const) misses the HEAVY UPPER TAIL of the
    confirm-walk -> truncates 14-19% of TRUE-P reps. The right quantity is a high percentile of
    the confirm-stop time, NOT mean+const (Elder's cushion governs p99 here). Reproduces 44/64/92
    at q_n=0.02. q_n = measured per-copy readout (design-time 0.02)."""
    pf = p_flip(n, q_n); p0 = 1 - pf
    A = n*np.log(3) + np.log(100); B = np.log(0.005)
    s_even = np.log(p0/0.5); s_odd = np.log((1-p0)/0.5)
    rng = np.random.default_rng(seed + n)
    stops = np.empty(trials, dtype=int)
    for t in range(trials):
        llr = 0.0; c = 0
        while True:                                       # true-basis SPRT walk to CONFIRM (>=A)
            c += 1
            llr += s_even if rng.random() < p0 else s_odd
            if llr >= A: stops[t] = c; break
            if llr <= B: stops[t] = c; break              # true basis false-elim (rare ~0.3%)
    return int(np.ceil(np.percentile(stops, pct)))

def build_conv_rep(n, P, C, rng):
    """One decode block (rep): committed random basis order, C fresh-b shots=1 copies per basis.
    Returns (pubs, manifest_pubs). pub = (circuit, named_rows, shots=1)."""
    qc, cparams = K.conv_template(n)
    bases = ["".join(t) for t in itertools.product("XYZ", repeat=n)]
    order = bases[:]; rng.shuffle(order)                  # committed order (seed drives it)
    schedule = [A for A in order for _ in range(C)]       # C copies per basis, in order
    rows, bstrs = K.conv_param_rows(P, schedule, rng)     # one FRESH-b row per schedule entry
    pubs, man = [], []
    for lo in range(0, len(rows), K.CONV_CHUNK_ROWS):
        chunk = rows[lo:lo + K.CONV_CHUNK_ROWS]
        pubs.append((qc, K.named_rows(cparams, chunk), 1))            # shots == 1 (delta item 1)
        man.append({"kind": "conv_v2", "row_lo": lo, "rows": len(chunk), "shots": 1})
    return pubs, man, order, bstrs

def selftest():
    """Ideal-sim checks: (1) shots==1 everywhere; (2) fresh-b per copy (b varies within a basis);
    (3) uniform C copies/basis; (4) conventional physics preserved (true-basis parity even,
    wrong ~50/50) — same angle-table guard as the frozen kit, unaffected by the shots delta."""
    from qiskit_aer import AerSimulator
    sim = AerSimulator(); rng = np.random.default_rng(142)
    n, P = 4, "XZYY"; C = 6
    pubs, man, order, bstrs = build_conv_rep(n, P, C, rng)
    # (1) shots==1
    assert all(p[2] == 1 for p in pubs), "shots != 1"
    assert all(m["shots"] == 1 for m in man), "manifest shots != 1"
    # (3) uniform C: total rows == C * 3^n
    total = sum(m["rows"] for m in man)
    assert total == C * 3**n, f"rows {total} != C*3^n {C*3**n}"
    # (2) fresh-b: the C copies of the FIRST basis have differing b-strings (not all identical)
    first_basis_bs = bstrs[:C]
    assert len(set(first_basis_bs)) > 1, "b not fresh across copies of a basis"
    # (4) conventional physics on the true basis vs a wrong basis (ideal sim, 1 shot x many copies)
    qc, params = K.conv_template(n)
    for A, expect in [(P, "even"), ("XZYX", "mixed")]:
        odd = 0; reps = 400
        for _ in range(reps):
            r, bs = K.conv_param_rows(P, [A], rng)
            bound = qc.assign_parameters(dict(zip(params, r[0])))
            out = sim.run(bound, shots=1, memory=True).result().get_memory()[0].replace(" ", "")
            b = np.array([int(c) for c in bs[0]])
            parity = (np.array([int(c) for c in out[::-1]]).sum() - b.sum()) % 2
            odd += parity
        rate = odd / reps
        if expect == "even":
            assert rate == 0.0, f"true-basis odd-rate {rate} (must be 0)"
        else:
            assert 0.35 < rate < 0.65, f"wrong-basis odd-rate {rate} (must be ~0.5)"
    print("  selftest PASS: shots==1, fresh-b per copy, uniform C=%d, true-basis parity EVEN, "
          "wrong-basis ~0.5 (angle table intact)." % C)
    # (5) CENSORING GUARD (catch #7): C=confirm_C(p99) must truncate <2.5% of TRUE-P confirm-walks.
    for nn in (4, 6, 8):
        Cn = confirm_C(nn, 0.02)
        pf = p_flip(nn, 0.02); p0 = 1 - pf
        A = nn*np.log(3) + np.log(100); B = np.log(0.005)
        se, so = np.log(p0/0.5), np.log((1-p0)/0.5)
        rg = np.random.default_rng(7*nn); trunc = 0; TT = 8000
        for _ in range(TT):
            llr = 0.0
            for c in range(Cn):                            # capped at C copies for this basis
                llr += se if rg.random() < p0 else so
                if llr >= A: break                         # confirmed within C
                if llr <= B: break                         # (false-elim, separate)
            else:
                trunc += 1                                 # never resolved in C -> truncated
        rate = trunc/TT
        assert rate < 0.025, f"n={nn} C={Cn}: true-basis truncation {rate:.3f} >= 2.5%"
        print(f"    censoring guard n={nn}: C=p99={Cn}  true-basis truncation {rate*100:.2f}% [<2.5% PASS]")

def scan(q_n=0.02):
    """FREE budget scan (no submission): per-rung C, emission-L=C*3^n, shots, PUB counts, at
    the ALPHA grid. q_n design-time 0.02; re-sizes from measured cal q_n at submit."""
    print(f"  ALPHA grid scan @ q_n={q_n} (design-time; re-sizes from measured q_n at flight):")
    tot_shots = 0
    for n, M in GRID.items():
        C = confirm_C(n, q_n)
        L = C * 3**n                     # emission-L per rep (flown)
        rep_pubs = -(-L // K.CONV_CHUNK_ROWS)      # ceil
        shots = L * M
        tot_shots += shots
        print(f"   n={n} M={M}: C={C:3d}  emission-L=C*3^n={L:7d}/rep  {rep_pubs} PUBs/rep  "
              f"conv shots={shots:,}")
    print(f"   CONV TOTAL ~{tot_shots:,} shots (+ quantum arm ~4.6k + cals/sentinels). "
          f"With C=p99 (catch #7 fix) this is ~520-720s > the ~300-500s ALPHA envelope -> Creator "
          f"re-ack or n=8 sub-trim (M=5->3, or n=8 censored-LB). Re-sizes from measured q_n at flight.")

if __name__ == "__main__":
    if "--selftest" in sys.argv:
        selftest()
    elif "--scan" in sys.argv:
        scan()
    else:
        selftest(); scan()
