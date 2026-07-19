#!/usr/bin/env python3
"""Exp205 — THE BLIND ANTENNA: the shielded sensor, where the blind spot is the signal. C4902.

Horizons-4 Invention 3 (rank 6), on the Creator's standing go. Composes Exp199 (the
shield's blind spot = global coherent Z-rotation) with F108's Fisher court: a global Z
field is exactly what a phase sensor reads — so the [[4,2,2]] block's blind spot IS its
antenna. Derived pre-flight (selftest asserts all exactly):

  * The Bell(x)Bell code state reads a global field Rz(phi)^4 at 2*phi per logical readout
    (each pair is a 2-GHZ): X1bar_unpost = cos(2 phi) — native 2x super-resolution.
  * The acceptance is Exp199's non-monotone curve reappearing as the SENSOR'S APERTURE:
    acc(phi) = (1 + cos^2(2 phi))/2 — narrowest (1/2) exactly at the steepest operating
    point, returning to 1 at pi/2 (199's addback, now a signed prediction of a sensing
    apparatus, re-certified in-sweep).
  * THE SHARPENED FRINGE (the jewel): postselection removes the flat component —
    X1bar_post = 2c/(1+c^2), c = cos(2 phi) — DOUBLING the slope at phi* = pi/4.
    Ideal Fisher per accepted shot at phi*: slope^2/var = 16 — equal to a bare 4-GHZ
    (F=16) from a 2-CX probe with error detection; per raw shot 16 x 0.5 = 8.

Arms (9 phase points phi = j*pi/16, j=0..8):
  bare   1q |+>, Rz(phi), X readout            — SQL reference, k=1, F<=1
  ghz4   4q GHZ, Rz(phi)^4, X^4 parity readout  — bare super-resolution reference, k=4
  logical Bell(x)Bell block, Rz(phi)^4, X-basis  — the shielded sensor, k=2; unpost AND
         post decodes from the same shots (203 pattern)
27 circuits, 8000 shots.

FROZEN GATES:
  G1 FRINGES: fixed-frequency fits (A, delta free; k fixed 1/4/2): V_bare >= 0.85,
     V_ghz4 >= 0.40, V_log(unpost) >= 0.50; |delta| <= 0.15 rad each; residuals <= 0.08.
  G2 SUPER-RESOLUTION STRUCTURE: free-k scan per arm — dominant k = 1/4/2 respectively
     (amplitude ratio vs next harmonic >= 2). The frequency cannot be faked by visibility.
  G3 THE APERTURE: acc(phi) tracks a*(1+V_a cos^2(2 phi))-form: frozen as acc tracks
     acc0*(1+c_hat^2)/2 /(1... operational form: |acc(phi)/acc(0) - (1+ch^2)/(2)| <= 0.06
     with ch = C_unpost(phi)/C_unpost(0) (in-arm, parametric — no fit); non-monotone:
     acc(pi/4) < acc(0) - 0.10 AND acc(pi/2) > acc(pi/4) + 0.10 (the 199 addback).
  G4 THE SHARPENED FRINGE (invention gate): X1_post tracks 2c/(1+c^2) with c = V_p cos(2
     phi), single fitted V_p, residual <= 0.08; finite-difference slope at pi/4:
     |slope_post| >= 2*|slope_bare| at >=5 sigma; Fisher per accepted shot at pi/4
     (delta method) >= 4x bare's best at >=3 sigma.
  G5 THROUGHPUT + COMPARISON (reported, filed): F_post x acc vs F_bare and vs F_ghz4;
     filed prediction (conf 0.6): F_ghz4-per-shot > F_post-per-accepted on a good window
     (16V^2 vs 16Vp^2-ish with ghz4's V the fragile one — the measurement decides).
Registered verdict = G1-G4 (G5 reported).
BUDGET CHECK (C4887): shallow probes (2-3 CX), visibilities from 196-class blocks ~0.9;
filed: V_bare in [0.90,0.99]; V_log in [0.70,0.92]; V_ghz4 in [0.45,0.85]; slope ratio
post/bare in [2.5,4.5]; F_post-per-accepted in [6,15].
Usage: --selftest | --submit [--backend ibm_fez --shots 8000] | --decode
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
PI = np.pi
PHIS = tuple(j * PI / 16 for j in range(17))   # [0, pi]: enough span to resolve k=1/2/4
                                                # (pi/4 = index 4, pi/2 = index 8; spacing pi/16)
ARMS = ("bare", "ghz4", "logical")


def circuit(arm, phi):
    if arm == "bare":
        qc = QuantumCircuit(1, 1)
        qc.h(0)
        qc.barrier()
        qc.rz(phi, 0)
        qc.barrier()
        qc.h(0); qc.measure(0, 0)
        return qc
    if arm == "ghz4":
        qc = QuantumCircuit(4, 4)
        qc.h(0)
        for q in range(1, 4): qc.cx(0, q)
        qc.barrier()
        for q in range(4): qc.rz(phi, q)
        qc.barrier()
        for q in range(4): qc.h(q)
        for q in range(4): qc.measure(q, q)
        return qc
    qc = QuantumCircuit(4, 4)
    qc.h(0); qc.cx(0, 1)                      # Bell (x) Bell = |+bar 0bar>
    qc.h(2); qc.cx(2, 3)
    qc.barrier()
    for q in range(4): qc.rz(phi, q)          # the field — 199's blind-spot drive
    qc.barrier()
    for q in range(4): qc.h(q)
    for q in range(4): qc.measure(q, q)
    return qc


def _stats(counts, arm):
    if arm == "bare":
        c = tot = 0
        for s, n in counts.items():
            c += (1 - 2 * int(s.replace(" ", "")[-1])) * n; tot += n
        return {"M": c / tot, "n": tot}
    if arm == "ghz4":
        c = tot = 0
        for s, n in counts.items():
            b = s.replace(" ", "")
            par = int(b[-1]) ^ int(b[-2]) ^ int(b[-3]) ^ int(b[-4])
            c += (1 - 2 * par) * n; tot += n
        return {"M": c / tot, "n": tot}
    acc = rej = xu = xp = 0
    for s, n in counts.items():
        b = s.replace(" ", "")
        v = [int(b[-1 - i]) for i in range(4)]
        x1 = 1 - 2 * (v[0] ^ v[1])
        xu += x1 * n
        if (v[0] ^ v[1] ^ v[2] ^ v[3]) == 0:
            acc += n; xp += x1 * n
        else:
            rej += n
    tot = acc + rej
    return {"M": xu / tot, "M_post": xp / acc if acc else 0.0,
            "acceptance": acc / tot, "n": tot, "n_acc": acc}


def fit_fixed_k(phis, ys, k):
    """LSQ fit y = A cos(k phi + delta): returns A>=0, delta, max residual."""
    X = np.column_stack([np.cos(k * np.array(phis)), -np.sin(k * np.array(phis))])
    coef, *_ = np.linalg.lstsq(X, np.array(ys), rcond=None)
    A = float(np.hypot(*coef)); delta = float(np.arctan2(coef[1], coef[0]))
    resid = float(np.max(np.abs(np.array(ys) - A * np.cos(k * np.array(phis) + delta))))
    return A, delta, resid

def free_k_scan(phis, ys, cands=(1, 2, 4)):
    """JOINT orthogonalized multi-harmonic fit over the three physical candidate
    frequencies + DC (independent single-harmonic fits double-count shared variance and
    alias on a coarse grid — C4902 selftest catch). Returns (dominant k, its amplitude,
    ratio to the next candidate)."""
    phis = np.array(phis)
    cols = [np.ones_like(phis)]
    for k in cands:
        cols += [np.cos(k * phis), np.sin(k * phis)]
    X = np.column_stack(cols)
    coef, *_ = np.linalg.lstsq(X, np.array(ys), rcond=None)
    amps = {}
    for i, k in enumerate(cands):
        a, b = coef[1 + 2 * i], coef[2 + 2 * i]
        amps[k] = float(np.hypot(a, b))
    dom = max(amps, key=amps.get)
    rest = max(v for kk, v in amps.items() if kk != dom)
    return dom, amps[dom], amps[dom] / rest if rest > 1e-9 else np.inf

def analyze(get):
    return {(arm, phi): _stats(get(arm, phi), arm) for arm in ARMS for phi in PHIS}


def selftest():
    from qiskit_aer import AerSimulator
    sim = AerSimulator(); shots = 40000; cache = {}
    def get(arm, phi):
        key = (arm, phi)
        if key not in cache:
            cache[key] = sim.run(circuit(arm, phi), shots=shots).result().get_counts()
        return cache[key]
    r = analyze(get)
    print("Exp205 selftest | bare cos(phi); ghz4 cos(4phi); log unpost cos(2phi), "
          "post 2c/(1+c^2), acc (1+c^2)/2")
    for phi in PHIS:
        c = np.cos(2 * phi)
        lg = r[("logical", phi)]
        assert abs(r[("bare", phi)]["M"] - np.cos(phi)) < 0.02
        assert abs(r[("ghz4", phi)]["M"] - np.cos(4 * phi)) < 0.02
        assert abs(lg["M"] - c) < 0.02, f"unpost at {phi}"
        assert abs(lg["M_post"] - 2 * c / (1 + c * c)) < 0.03, f"post at {phi}"
        assert abs(lg["acceptance"] - (1 + c * c) / 2) < 0.02, f"aperture at {phi}"
    # slopes at pi/4 by central difference (phis are pi/16-spaced; pi/4 = index 4)
    h = PI / 16
    sp = (r[("logical", PHIS[5])]["M_post"] - r[("logical", PHIS[3])]["M_post"]) / (2 * h)
    sb = (r[("bare", PHIS[5])]["M"] - r[("bare", PHIS[3])]["M"]) / (2 * h)
    print(f"  slopes at pi/4: post {sp:+.3f} (ideal -4/(1+..): about -3.8 discretized), "
          f"bare {sb:+.3f} (~-0.71); ratio {abs(sp/sb):.2f}")
    assert abs(sp) > 2.5 * abs(sb), "sharpened fringe must at least 2.5x the bare slope"
    for arm, kexp in (("bare", 1), ("ghz4", 4), ("logical", 2)):
        ys = [r[(arm, phi)]["M"] for phi in PHIS]
        dom, A, ratio = free_k_scan(PHIS, ys)
        assert dom == kexp, f"{arm}: dominant k {dom} != {kexp}"
        print(f"  {arm:>7}: dominant k={dom} (amp {A:.3f}, ratio {ratio:.1f})")
    print("SELFTEST PASS: 2x native super-resolution, the 199 aperture as sensing "
          "curve, the sharpened fringe 2c/(1+c^2) with >2.5x bare slope, frequency "
          "structure un-fakeable. Cleared to fly.")


def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    names = [[arm, float(phi)] for arm in ARMS for phi in PHIS]
    circuits = audit = seed_used = None
    for seed in range(20):
        cand = [transpile(circuit(arm, phi), backend=backend, optimization_level=3,
                          seed_transpiler=seed) for arm, phi in names]
        aud = {}
        for (arm, phi), qc in zip(names, cand):
            n2 = sum(1 for inst in qc.data if inst.operation.num_qubits == 2)
            aud.setdefault(arm, set()).add(n2)
        if all(len(v) == 1 for v in aud.values()):
            circuits, seed_used = cand, seed
            audit = {a: sorted(v) for a, v in aud.items()}
            break
        print(f"  seed {seed}: non-uniform { {a: sorted(v) for a, v in aud.items()} } — next")
    if circuits is None:
        print("AUDIT ABORT: no phi-uniform seed in 0-19"); sys.exit(1)
    for a, v in audit.items():
        print(f"  audit {a}: 2q={v} (phi-uniform, seed {seed_used})")
    job = SamplerV2(mode=backend).run(circuits, shots=shots)
    out = os.path.join(HERE, "..", "results", "exp205_blind_antenna_manifest.json")
    man = {"exp": 205, "slug": "blind_antenna", "backend": backend_name, "shots": shots,
           "job_id": job.job_id(), "order": names, "seed_transpiler": seed_used}
    json.dump(man, open(out, "w"), indent=1)
    man["audit_2q"] = audit
    man["prereg"] = {
        "G1_fringes": "fixed-k fits: V_bare>=0.85, V_ghz4>=0.40, V_log_unpost>=0.50; "
                      "|delta|<=0.15 rad; residuals<=0.08",
        "G2_structure": "free-k dominant frequency = 1/4/2 per arm, amp ratio >= 2",
        "G3_aperture": "|acc(phi)/acc(0) - (1+ch^2)/2| <= 0.06 with ch = M(phi)/M(0) "
                       "in-arm parametric; acc(pi/4) < acc(0)-0.10; acc(pi/2) > "
                       "acc(pi/4)+0.10 (199 addback as aperture, re-certified in-sweep)",
        "G4_sharpened_fringe": "M_post tracks 2c/(1+c^2), c=V_p cos(2phi), resid<=0.08; "
                               "|slope_post(pi/4)| >= 2x|slope_bare| at >=5 sigma; "
                               "F_post-per-accepted(pi/4) >= 4x F_bare_best at >=3 sigma",
        "G5_reported": "F x acc throughput; ghz4 comparison; filed conf 0.6: "
                       "F_ghz4-per-shot > F_post-per-accepted on a good window",
        "registered_verdict": "G1-G4",
        "budget_predictions": "V_bare in [0.90,0.99]; V_log in [0.70,0.92]; V_ghz4 in "
                              "[0.45,0.85]; slope ratio post/bare in [2.5,4.5]; "
                              "F_post-per-accepted in [6,15]"}
    json.dump(man, open(out, "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits, {shots} shots) -> {out}")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    man = json.load(open(os.path.join(HERE, "..", "results", "exp205_blind_antenna_manifest.json")))
    svc = _get_ibm_service(); res = svc.job(man["job_id"]).result()
    shots = man["shots"]; raw = {}
    for idx, (arm, phi) in enumerate(man["order"]):
        r0 = res[idx]; reg = list(r0.data.keys())[0]
        raw[(arm, float(phi))] = getattr(r0.data, reg).get_counts()
    r = analyze(lambda arm, phi: raw[(arm, phi)])
    se = 1 / np.sqrt(shots)
    print(f"Exp205 THE BLIND ANTENNA decode | job {man['job_id']}")
    for phi in PHIS:
        lg = r[("logical", phi)]
        print(f"  phi={phi/PI:.3f}pi: bare={r[('bare', phi)]['M']:+.3f} "
              f"ghz4={r[('ghz4', phi)]['M']:+.3f} | log unpost={lg['M']:+.3f} "
              f"post={lg['M_post']:+.3f} acc={lg['acceptance']:.3f}")
    fits = {}
    for arm, k in (("bare", 1), ("ghz4", 4), ("logical", 2)):
        ys = [r[(arm, phi)]["M"] for phi in PHIS]
        fits[arm] = fit_fixed_k(PHIS, ys, k)
    Vb, db, rb = fits["bare"]; Vg, dg, rg = fits["ghz4"]; Vl, dl, rl = fits["logical"]
    g1 = (Vb >= 0.85 and Vg >= 0.40 and Vl >= 0.50
          and all(abs(d) <= 0.15 for d in (db, dg, dl))
          and all(x <= 0.08 for x in (rb, rg, rl)))
    g2 = True
    doms = {}
    for arm, kexp in (("bare", 1), ("ghz4", 4), ("logical", 2)):
        ys = [r[(arm, phi)]["M"] for phi in PHIS]
        dom, A, ratio = free_k_scan(PHIS, ys)
        doms[arm] = (dom, round(ratio, 2))
        g2 = g2 and dom == kexp and ratio >= 2
    acc0 = r[("logical", 0.0)]["acceptance"]
    ap_res = []
    for phi in PHIS:
        ch = r[("logical", phi)]["M"] / r[("logical", 0.0)]["M"]
        ap_res.append(r[("logical", phi)]["acceptance"] / acc0 - (1 + ch * ch) / 2)
    a_q = r[("logical", PHIS[4])]["acceptance"]
    g3 = (all(abs(v) <= 0.06 for v in ap_res)
          and a_q < acc0 - 0.10 and r[("logical", PHIS[8])]["acceptance"] > a_q + 0.10)
    # G4: sharpened fringe
    def post_model(Vp):
        out = []
        for phi in PHIS:
            c = Vp * np.cos(2 * phi)
            out.append(2 * c / (1 + c * c))
        return np.array(out)
    ys_post = np.array([r[("logical", phi)]["M_post"] for phi in PHIS])
    Vps = np.linspace(0.3, 1.0, 141)
    best = min(Vps, key=lambda v: np.max(np.abs(ys_post - post_model(v))))
    res_post = float(np.max(np.abs(ys_post - post_model(best))))
    h = PI / 16
    sp = (r[("logical", PHIS[5])]["M_post"] - r[("logical", PHIS[3])]["M_post"]) / (2 * h)
    sb = (r[("bare", PHIS[5])]["M"] - r[("bare", PHIS[3])]["M"]) / (2 * h)
    n_acc = min(r[("logical", PHIS[3])]["n_acc"], r[("logical", PHIS[5])]["n_acc"])
    se_sp = np.sqrt(2) / (2 * h) / np.sqrt(max(n_acc, 1))
    z_slope = (abs(sp) - 2 * abs(sb)) / se_sp
    F_post = sp ** 2 / max(1 - r[("logical", PHIS[4])]["M_post"] ** 2, 1e-3)
    F_bare = Vb ** 2                          # best-point Fisher of a cos fringe
    se_F = 2 * abs(sp) * se_sp
    z_F = (F_post - 4 * F_bare) / se_F
    g4 = res_post <= 0.08 and abs(sp) >= 2 * abs(sb) and z_slope >= 5 and z_F >= 3
    F_ghz4 = 16 * Vg ** 2
    thr = F_post * r[("logical", PHIS[4])]["acceptance"]
    print(f"\nG1 FRINGES: V_bare={Vb:.3f} V_ghz4={Vg:.3f} V_log={Vl:.3f} "
          f"resid {rb:.3f}/{rg:.3f}/{rl:.3f} {'OK' if g1 else 'MISS'}")
    print(f"G2 STRUCTURE: dominant k {doms} {'OK' if g2 else 'MISS'}")
    print(f"G3 APERTURE: max resid {max(abs(v) for v in ap_res):.3f}; "
          f"acc0={acc0:.3f} -> acc(pi/4)={a_q:.3f} -> acc(pi/2)="
          f"{r[('logical', PHIS[8])]['acceptance']:.3f} {'OK' if g3 else 'MISS'}")
    print(f"G4 SHARPENED FRINGE: V_p={best:.3f} resid={res_post:.3f}; slope post "
          f"{sp:+.3f} vs bare {sb:+.3f} (ratio {abs(sp/sb):.2f}, {z_slope:.1f} sigma); "
          f"F_post={F_post:.2f}/accepted vs 4x F_bare={4*F_bare:.2f} ({z_F:.1f} sigma) "
          f"{'OK' if g4 else 'MISS'}")
    print(f"G5 REPORTED: F_post x acc = {thr:.2f}/raw | F_ghz4 = {F_ghz4:.2f}/shot | "
          f"F_bare = {F_bare:.2f}/shot")
    ok = g1 and g2 and g3 and g4
    print(f"VERDICT: {'THE BLIND ANTENNA — the shields blind spot is a working sensor: '
          'native 2x super-resolution, the 199 aperture as its lens, and postselection '
          'sharpens the fringe past 2x bare slope with Fisher-per-accepted beating 4x '
          'bare' if ok else 'NOT HELD (accounting above)'}")
    json.dump({"job_id": man["job_id"],
               "results": {f"{a}_{phi:.4f}": r[(a, phi)] for a in ARMS for phi in PHIS},
               "fits": {"bare": fits["bare"], "ghz4": fits["ghz4"], "logical": fits["logical"]},
               "V_p": float(best), "post_resid": res_post,
               "slope_post": float(sp), "slope_bare": float(sb), "z_slope": float(z_slope),
               "F_post_acc": float(F_post), "F_bare": float(F_bare),
               "F_ghz4": float(F_ghz4), "throughput": float(thr), "z_F": float(z_F),
               "g1": bool(g1), "g2": bool(g2), "g3": bool(g3), "g4": bool(g4),
               "verdict_ok": bool(ok)},
              open(os.path.join(HERE, "..", "results", "exp205_blind_antenna_decode.json"), "w"), indent=1)
    print("-> results/exp205_blind_antenna_decode.json")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--selftest", action="store_true"); ap.add_argument("--submit", action="store_true")
    ap.add_argument("--decode", action="store_true")
    ap.add_argument("--backend", default="ibm_fez"); ap.add_argument("--shots", type=int, default=8000)
    a = ap.parse_args()
    if a.selftest: selftest()
    elif a.submit: submit(a.backend, a.shots)
    elif a.decode: decode()
    else: ap.print_help()
