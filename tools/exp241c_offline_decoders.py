#!/usr/bin/env python3
"""Exp241c (P7.0) — OFFLINE memory-decoder study on Exp241's already-flown sham streams. $0.

The sham arm recorded {syn0..syn{R-1}, out} per shot with NO in-circuit fixes. Because the code is a
bit-flip code and corrections are Pauli-X, any in-circuit decoder can be REPLAYED faithfully on these
shots via Pauli-frame tracking: syn(e^f) = syn(e) ^ syn(f) (linearity), out_corrected = out ^ f.
Built-in validation: the replayed MEMORYLESS decoder should reproduce the real corrected arm's F.

Decoders:
  D0  majority(out)                      — Exp241's sham metric (no syndrome use)
  M   memoryless in-circuit replica      — per round: c = corr(observed), f ^= c   (the flight control)
  A   debounce                           — apply c only if observed_r == observed_{r-1} != 0
  B   revert-phantom                     — like M; if observed_r == observed_{r-1} != 0, treat the
                                           previous fix as phantom-triggered: revert it
  ML  HMM forward over error patterns    — params (p,q,rf) grid-fit on train half; the ceiling

Split-sample: even shots = train (ML param fit), odd shots = test (ALL decoders evaluated on odd only).
Success = decoded logical == 1 (the encoded value). Paired comparison vs M with McNemar counts.
Substrate: claude-fable-5, Whisper C4951."""
import json, os, sys
import numpy as np
from itertools import product

HERE = os.path.dirname(os.path.abspath(__file__)); QROOT = os.path.join(HERE, "..")
JOB = "d9f3ov4jeosc73fjen3g"
CORR = {1: 0b001, 3: 0b010, 2: 0b100, 0: 0}          # observed syndrome value -> X-frame bit (d0,d1,d2)
F_CORRECTED_REAL = {2: 0.616, 3: 0.523375, 4: 0.44175}  # from exp241 decode json (validation target)

def syn_of(f):  # syndrome int of a 3-bit error/frame pattern (bit i = qubit d_i)
    e0, e1, e2 = f & 1, (f >> 1) & 1, (f >> 2) & 1
    return (e0 ^ e1) | ((e1 ^ e2) << 1)

def majority1(out3):  # logical readout: majority of |1> bits, ideal state |111>
    return 1 if bin(out3).count("1") >= 2 else 0

def replay(recs, out, rule):
    """recs: [R][shots] recorded syndrome ints; out: [shots] 3-bit ints. Returns success bool array."""
    R, n = len(recs), len(out)
    ok = np.zeros(n, dtype=bool)
    for s in range(n):
        f, prev_obs, prev_c = 0, None, 0
        for r in range(R):
            obs = recs[r][s] ^ syn_of(f)
            if rule == "M":
                f ^= CORR[obs]
            elif rule == "A":
                if prev_obs is not None and obs == prev_obs and obs != 0:
                    f ^= CORR[obs]
            elif rule == "B":
                if prev_obs is not None and obs == prev_obs and obs != 0 and prev_c:
                    f ^= prev_c          # revert the phantom-triggered previous fix
                    obs = recs[r][s] ^ syn_of(f)
                c = CORR[obs]; f ^= c; prev_c = c
            prev_obs = obs
        ok[s] = majority1(out[s] ^ f) == 1
    return ok

def hmm_loglik(recs_s, out_s, enc, p, q, rf):
    """Forward over 8 error states for one shot; returns log P(obs | encoded=enc)."""
    R = len(recs_s)
    alpha = np.full(8, -np.inf); alpha[0] = 0.0
    lp, l1p = np.log(p), np.log(1 - p)
    lq, l1q = np.log(q), np.log(1 - q)
    for r in range(R):
        new = np.full(8, -np.inf)
        for e in range(8):
            if alpha[e] == -np.inf: continue
            for de in range(8):
                nb = bin(de).count("1")
                ne = e ^ de
                t = alpha[e] + nb * lp + (3 - nb) * l1p
                new[ne] = np.logaddexp(new[ne], t)
        # emission: recorded syndrome bits vs syn_of(e), each ancilla bit flips w.p. q
        for e in range(8):
            if new[e] == -np.inf: continue
            d = bin(recs_s[r] ^ syn_of(e)).count("1")
            new[e] += d * lq + (2 - d) * l1q
        alpha = new
    lrf, l1rf = np.log(rf), np.log(1 - rf)
    tot = -np.inf
    ideal = 0b111 if enc == 1 else 0b000
    for e in range(8):
        if alpha[e] == -np.inf: continue
        d = bin(out_s ^ ideal ^ e).count("1")
        tot = np.logaddexp(tot, alpha[e] + d * lrf + (3 - d) * l1rf)
    return tot

def main():
    from qiskit_ibm_runtime import QiskitRuntimeService
    # ACCOUNT SCOPE (C5016 reader audit): fetches a PINNED historical Exp241-era job
    # living on the SAVED DEFAULT account (flown pre-ALT-migration). Do NOT re-point
    # to ALT -- it would 404. A pinned-ID fetch fails LOUD on the wrong account,
    # unlike ambient readers whose wrong-scope output still looks right, so this is
    # labeled rather than re-plumbed. Cross-account lookup if ever needed:
    # scripts/check_job_status.py sweeps both instances.
    res = QiskitRuntimeService().job(JOB).result()
    # pub order per exp241 submit: for R in 0..4: corrected, sham, bare
    report = {}
    for R, idx in [(2, 7), (3, 10), (4, 13)]:
        db = res[idx].data
        regs = sorted(k for k in db.__dict__ if k.startswith("syn"))
        assert len(regs) == R, (R, regs)
        recs = [np.array([int(b, 2) for b in getattr(db, k).get_bitstrings()]) for k in regs]
        out = np.array([int(b, 2) for b in db.out.get_bitstrings()])
        n = len(out); test = np.arange(n) % 2 == 1; train = ~test
        # ML param grid-fit on train (encoded=1 ground truth)
        best, bp = -np.inf, None
        sub = np.random.RandomState(0).choice(np.where(train)[0], size=min(400, train.sum()), replace=False)
        for p, q, rf in product((0.02, 0.05, 0.09, 0.14), (0.08, 0.15, 0.25, 0.35), (0.02, 0.05, 0.10)):
            ll = sum(hmm_loglik([rc[s] for rc in recs], out[s], 1, p, q, rf) for s in sub)
            if ll > best: best, bp = ll, (p, q, rf)
        # evaluate all decoders on TEST half
        d0 = np.array([majority1(o) == 1 for o in out])
        arms = {"D0_majority": d0, "M_memoryless": replay(recs, out, "M"),
                "A_debounce": replay(recs, out, "A"), "B_revert": replay(recs, out, "B")}
        ml = np.zeros(n, dtype=bool)
        for s in np.where(test)[0]:
            l1 = hmm_loglik([rc[s] for rc in recs], out[s], 1, *bp)
            l0 = hmm_loglik([rc[s] for rc in recs], out[s], 0, *bp)
            ml[s] = l1 >= l0
        arms["ML_hmm"] = ml
        row = {"shots_test": int(test.sum()), "ml_params(p,q,rf)": bp,
               "replayM_vs_realcorrected": [round(float(arms["M_memoryless"].mean()), 4), F_CORRECTED_REAL[R]]}
        for k, v in arms.items():
            row[k] = round(float(v[test].mean()), 4)
        # paired McNemar vs M on test half
        m = arms["M_memoryless"][test]
        for k in ("A_debounce", "B_revert", "ML_hmm", "D0_majority"):
            a = arms[k][test]
            b01, b10 = int((~m & a).sum()), int((m & ~a).sum())
            row[f"mcnemar_{k}_vs_M(+,-)"] = [b01, b10]
        report[f"R{R}"] = row
        print(f"R={R}: " + " ".join(f"{k}={row[k]}" for k in arms))
        print(f"   replay-validation: replayed M (all shots) = {arms['M_memoryless'].mean():.4f} vs real corrected arm = {F_CORRECTED_REAL[R]}")
        print(f"   ML params {bp}; McNemar(+,-) vs M: A={row['mcnemar_A_debounce_vs_M(+,-)']} B={row['mcnemar_B_revert_vs_M(+,-)']} ML={row['mcnemar_ML_hmm_vs_M(+,-)']}")
    json.dump(report, open(os.path.join(QROOT, "results", "exp241c_offline_decoders.json"), "w"), indent=1)
    print("card -> results/exp241c_offline_decoders.json")

if __name__ == "__main__":
    sys.exit(main())
