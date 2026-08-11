#!/usr/bin/env python3
"""H13 Cell 2 RE-FLY — STANDALONE ISOTROPY PRE-FLIGHT GATE. Whisper C5058, Creator's grant.

WHAT THIS DECIDES: tonight's Cell 2 NO-TEST traced to an IDLE-DELAY injection, which is DEPHASING
(anisotropic: kills X,Y, spares Z) where the design requires DEPOLARIZING (isotropic). The re-fly
(#77) replaces it with a PAULI TWIRL over {I,X,Y,Z} mixed across shots. Elder derived the gate's
power requirement (#9099): the check must resolve anisotropy at the ARM-GAP scale d=0.01148, which
needs ~20,000 shots/basis (MDE 0.0098). This flight runs ONLY that gate. If the twirl does not
produce isotropy on real silicon, the ~64s re-fly is dead before it is paid for.
GATE: per arm, max pairwise |C_ii - C_jj| over {XX,YY,ZZ} must be <= the arm gap 0.01148 + MDE.
Usage: QPU_ACCOUNT_VAR=IBMQ_ALT3 python3 scripts/h13_cell2_isotropy_gate_c5058.py [--dry-run]
"""
import json, math, os, sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.pop("QISKIT_IBM_INSTANCE", None)
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister, transpile

BASES, TWIRLS = ("X", "Y", "Z"), ("I", "X", "Y", "Z")
# PARTIAL depolarizing at strength P_DEPOL, built as a WEIGHTED Pauli mixture.
# A UNIFORM twirl over {I,X,Y,Z} is COMPLETE depolarization — it zeroes every correlator, which
# the dry run duly showed (C=0.0 everywhere). The channel we need is I with weight 1-3p/4 and
# each of X,Y,Z with weight p/4, giving C_ii = (1-p)*C_ideal, EQUAL across the three axes —
# which is exactly the isotropy the frozen ceiling's scalar model assumes and the idle delay broke.
P_DEPOL = 0.5
SHOTS_PER_CELL = 20000                       # Elder's MDE requirement (#9099): resolve 0.0115
WEIGHTS = {"I": 1 - 3 * P_DEPOL / 4, "X": P_DEPOL / 4, "Y": P_DEPOL / 4, "Z": P_DEPOL / 4}
SHOTS = {t: int(round(SHOTS_PER_CELL * w)) for t, w in WEIGHTS.items()}
ARM_GAP, EST_COST_S = 0.01148, 40.0

def rot(qc, q, b, inv=False):
    if b == "X": qc.h(q)
    elif b == "Y":
        if inv: qc.h(q); qc.s(q)
        else: qc.sdg(q); qc.h(q)

def pauli(qc, q, p):
    if p == "X": qc.x(q)
    elif p == "Y": qc.y(q)
    elif p == "Z": qc.z(q)

def ce(basis, tw):
    """cause-effect: measure Pauli i -> TWIRLED injection -> measure Pauli i."""
    q = QuantumRegister(1, "q"); c = ClassicalRegister(2, "c")
    qc = QuantumCircuit(q, c, name=f"CE_{basis}_{tw}")
    rot(qc, q[0], basis); qc.measure(q[0], c[0]); rot(qc, q[0], basis, inv=True)
    pauli(qc, q[0], tw)                      # ISOTROPIC injection: uniform mixture over {I,X,Y,Z}
    rot(qc, q[0], basis); qc.measure(q[0], c[1])
    return qc

def cc(basis, tw):
    """common cause: Phi+ pair, twirled injection on one wing, both wings measured."""
    q = QuantumRegister(2, "q"); c = ClassicalRegister(2, "c")
    qc = QuantumCircuit(q, c, name=f"CC_{basis}_{tw}")
    qc.h(q[0]); qc.cx(q[0], q[1])
    pauli(qc, q[0], tw)
    for k in (0, 1): rot(qc, q[k], basis)
    qc.measure(q[0], c[0]); qc.measure(q[1], c[1])
    return qc

def build():
    circs, labels = [], []
    for b in BASES:
        for t in TWIRLS:
            circs.append(ce(b, t)); labels.append({"arm": "CE", "basis": b, "twirl": t})
            circs.append(cc(b, t)); labels.append({"arm": "CC", "basis": b, "twirl": t})
    return circs, labels

IDEAL_SIGNS = {"CE": (+1, +1, +1),      # QM repeatability forces all-positive diagonals
               "CC": (+1, -1, +1)}      # Phi+ carries an intrinsic <YY> = -1

def grade(corrs, ns=None):
    """corrs[arm][basis] = twirl-averaged correlator. Isotropy = the three |C| agree.
    RESOLUTION PRECONDITION (Elder #9204): a measured sign is only meaningful where |C| is
    resolved away from zero — under a strong twirl the correlators shrink and the sign becomes
    noise. Assert sign only where |C|/se >= 5; below that report UNRESOLVED, NEVER a mismatch.
    Calling an unresolved sign a flip is a gate firing on noise — the inverse of tonight's
    fail-opens and just as wrong. At 20k pre-flight depth signs resolve past 30 sigma even at
    p=0.9; at 400 science shots the marginal cases are exactly where the frozen NO-CALL floor
    already abstains, so this check INHERITS that threshold rather than adding a second one."""
    out = {}
    for arm in ("CE", "CC"):
        # MAGNITUDES, not signed values: Phi+ carries an intrinsic <YY> = -1, so the CC arm's
        # signed spread is 1.0 by physics, not by channel asymmetry (dry run showed exactly that).
        # Isotropy means the channel ATTENUATES all three axes EQUALLY -> compare |C_ii|.
        vals = [abs(corrs[arm][b]) for b in BASES]
        spread = max(abs(vals[i] - vals[j]) for i in range(3) for j in range(i + 1, 3))
        out[arm] = {"C": {b: round(corrs[arm][b], 5) for b in BASES},
                    "abs_C": {b: round(abs(corrs[arm][b]), 5) for b in BASES},
                    "max_pairwise_spread_abs": round(spread, 5),
                    "gate_pass_isotropy": bool(spread <= ARM_GAP + 0.0098)}
        # SIGN CHECK (Ember #9200, free — the flight already bought this data). The discriminator
        # is sign(C_XX*C_YY*C_ZZ), a SIGN object, and a magnitude-only gate is blind to a sign
        # event: a channel attenuating all three axes EQUALLY while flipping one sign passes
        # isotropy and INVERTS the statistic. A correct depolarizing twirl cannot do that — but
        # this gate exists to detect an INCORRECT channel, and incorrect is not only anisotropic.
        N = (ns or {}).get(arm, SHOTS_PER_CELL)
        signs, zs, unresolved, mismatch = [], [], [], []
        for i, b in enumerate(BASES):
            C = corrs[arm][b]
            se = math.sqrt(max(1 - C * C, 1e-12) / N)
            z = abs(C) / se
            zs.append(round(z, 1))
            sg = 1 if C >= 0 else -1
            signs.append(sg)
            if z < 5: unresolved.append(b)
            elif sg != IDEAL_SIGNS[arm][i]: mismatch.append(b)
        out[arm]["signs"] = tuple(signs)
        out[arm]["signs_expected"] = IDEAL_SIGNS[arm]
        out[arm]["sign_z"] = zs
        out[arm]["unresolved_axes"] = unresolved
        out[arm]["sign_mismatch_axes"] = mismatch
        out[arm]["gate_pass_signs"] = bool(not mismatch)      # UNRESOLVED is not a mismatch
        # SIGNAL FLOOR — 3 of 3, NOT 2 of 3 (Elder #9215 closed the hole in my first version).
        # 2-of-3 passes a channel that destroys EXACTLY ONE axis, which is manifestly anisotropic,
        # by certifying it on the surviving pair. Deeper: you cannot certify UNIFORM attenuation
        # while one of the three attenuations is unmeasured. The deciding argument is not
        # conservatism but CONSUMER CONSISTENCY — the frozen decoder's NO-CALL rule already
        # abstains if ANY diagonal is unresolved, so a pre-flight certifying a channel the decoder
        # would then refuse to decode has certified the wrong thing. Same |C|/se>=5 in three
        # places: this gate, the sign precondition, and the decoder floor.
        # (added C5058 AFTER this gate returned a VACUOUS PASS on dead data)
        # All-zero correlators pass isotropy TRIVIALLY (equally dead on every axis) and pass the
        # sign check VACUOUSLY (nothing resolved, so nothing can mismatch). A gate that cannot
        # fail on a channel that destroyed all signal is not a gate. REQUIRE resolved signal:
        # ALL THREE axes with |C|/se >= 5, else NO-TEST — never PASS.
        n_res = 3 - len(unresolved)
        out[arm]["resolved_axes"] = n_res
        out[arm]["gate_no_test"] = bool(n_res < 3)
        out[arm]["gate_pass"] = bool(out[arm]["gate_pass_isotropy"] and out[arm]["gate_pass_signs"]
                                     and not out[arm]["gate_no_test"])
    return out

def main():
    dry = "--dry-run" in sys.argv
    circs, labels = build()
    tot = sum(SHOTS[l["twirl"]] for l in labels)
    print(f"[build] {len(circs)} circuits; p_depol={P_DEPOL}; per-twirl shots {SHOTS}; total {tot:,} shot-circuits")
    print(f"[build] predicted isotropic correlator = (1-p)*C_ideal = {1-P_DEPOL:.3f} x C_ideal, EQUAL on all three axes")
    if dry:
        from qiskit_aer import AerSimulator
        sim = AerSimulator(); tc = transpile(circs, sim, optimization_level=1, seed_transpiler=20260811)
        res = [sim.run([c], shots=SHOTS[l["twirl"]]).result() for l, c in zip(labels, tc)]
        acc = {"CE": {b: [] for b in BASES}, "CC": {b: [] for b in BASES}}
        for lab, c, r1 in zip(labels, tc, res):
            counts = r1.get_counts(c); tot = sum(counts.values())
            e = sum(((-1) ** (int(k.replace(" ", "")[0]) + int(k.replace(" ", "")[1]))) * v for k, v in counts.items()) / tot
            acc[lab["arm"]][lab["basis"]].append((e, SHOTS[lab["twirl"]]))
        corrs = {a: {b: sum(e * w for e, w in v) / sum(w for _, w in v) for b, v in d.items()} for a, d in acc.items()}
        g = grade(corrs)
        for arm in ("CE", "CC"):
            print(f"  {arm}: C={g[arm]['C']}  |C| spread={g[arm]['max_pairwise_spread_abs']}  "
                  f"signs={g[arm]['signs']} (want {g[arm]['signs_expected']})  "
                  f"z={g[arm]['sign_z']} iso={'PASS' if g[arm]['gate_pass_isotropy'] else 'FAIL'} "
                  f"sign={'PASS' if g[arm]['gate_pass_signs'] else 'FAIL'}"
                  + (f" UNRESOLVED={g[arm]['unresolved_axes']}" if g[arm]['unresolved_axes'] else ""))
        print("  (ideal twirl: the four Paulis average to a depolarizing channel -> the three diagonals agree)")
        return
    from ibm_multi_account import assert_explicit_account, service_for_submission, _load_env_files
    _load_env_files()
    acct = assert_explicit_account()
    if acct != "IBMQ_ALT4": raise SystemExit(f"declares IBMQ_ALT4 (ALT3 exhausted; ALT4 issued by the Creator general#9238); got {acct} — REFUSING.")
    svc = service_for_submission(acct)
    u = svc.usage(); remaining = float(u["usage_limit_seconds"]) - float(u["usage_consumed_seconds"])
    if u.get("usage_limit_reached") or remaining < EST_COST_S:
        raise SystemExit(f"FIT GATE REFUSES: remaining={remaining}s < est {EST_COST_S}s")
    print(f"[fit gate] {acct}: {remaining:.1f}s >= est {EST_COST_S}s — OK")
    backend = svc.backend("ibm_marrakesh")
    props = backend.properties(); ro = {}
    for qq in range(backend.num_qubits):
        try: ro[qq] = props.readout_error(qq)
        except Exception: pass
    adj = {}
    for x, y in backend.coupling_map: adj.setdefault(x, set()).add(y); adj.setdefault(y, set()).add(x)
    q_ce = min(ro, key=ro.get)
    best, bs = None, 9e9
    for a, b_ in backend.coupling_map:
        if a in ro and b_ in ro and a != q_ce and b_ != q_ce:
            try: s = ro[a] + ro[b_] + props.gate_error("cz", (a, b_))
            except Exception: continue
            if s < bs: best, bs = (a, b_), s
    print(f"[layout] CE q{q_ce} | CC {best} — live, never cached")
    tc = [transpile(c, backend, initial_layout=([q_ce] if c.num_qubits == 1 else list(best)),
                    optimization_level=1, seed_transpiler=20260811) for c in circs]
    mx = max(sum(v for k, v in c.count_ops().items() if k in ("cz", "cx", "ecr")) for c in tc)
    print(f"[transpiled-count gate] max 2q = {mx} (premise-free gate; well under the ~7-gate 0.95 ceiling for CE)")
    from qiskit_ibm_runtime import SamplerV2
    sampler = SamplerV2(mode=backend)
    # PER-PUB SHOT ALLOCATION — this IS the weighted mixture. The first flight passed a single
    # uniform shots= to sampler.run(), so every twirl got 12500 shots: a UNIFORM twirl, i.e.
    # COMPLETE depolarization, and every correlator landed at ~0.002 instead of ~0.46. The dry
    # run had ALREADY caught uniform-twirl-zeroes-everything and I fixed only the SIMULATION
    # path; the submission path kept the bug. A fix applied to one code path is not applied to
    # the system.
    pubs = [(c, None, SHOTS[l["twirl"]]) for c, l in zip(tc, labels)]
    job = sampler.run(pubs)
    
    print(f"[submitted] job_id={job.job_id()}")
    man = {"cell": "H13-Cell2-REFLY-isotropy-gate", "board": 77, "account": acct, "backend": backend.name,
           "job_id": job.job_id(), "shots_per_twirl": SHOTS, "p_depol": P_DEPOL, "labels": labels, "arm_gap": ARM_GAP,
           "layout": {"CE": q_ce, "CC": list(best)}, "max_2q": mx,
           "gate": "per arm, max pairwise |C_ii - C_jj| <= arm_gap + MDE  (isotropy of the twirled injection)",
           "fit_gate": {"remaining_at_submit": remaining, "est": EST_COST_S}}
    p = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), f"results/h13_cell2_isotropy_manifest_{job.job_id()}.json")
    json.dump(man, open(p, "w"), indent=1); print(f"[manifest] {p}")

if __name__ == "__main__":
    main()
