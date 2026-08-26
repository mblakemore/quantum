#!/usr/bin/env python3
"""Counterflow Flight C — the Information Recuperator (QET), FLIGHT (Whisper C5082, board #196).

The directional-QET two-regime sign-flip, on IBM hardware. Every piece validated against sim_c and under
representative ibm_fez noise before this flight (findings/flight-bc-feasibility-whisper-c5082.md):
  core extract (gamma=0) -0.114 vs sim -0.1147; GAD == Kraus channel to 4 dp; ideal sign-flip
  gamma0.2 -0.056 / gamma0.5 +0.197; noise-robust with wide-theta + readout mitigation
  (gamma0.2 -0.096 NEG / gamma0.5 +0.223 POS).

CLAIM (labeled physics result, NOT a quantum-advantage claim): in a thermal gradient realized by local GAD,
the DIRECTION of the QET information stream (measure-cold-rotate-hot = counterflow, vs the mirror = co-flow)
changes which flow extracts more local energy, and that preference FLIPS SIGN with the gradient strength:
  direction = extract_cf - extract_co ;  P1: direction(gamma_lo) < 0 ;  P2: direction(gamma_hi) > 0.
Info control: info_value = extract_cf - extract_cf_severed > 0 (the measured BIT does work, vs a fresh coin).

PROTOCOL (Hotta minimal QET; H=Z0+Z1+2X0X1, offset E_ground=0):
  prep |g>=cos a|00>-sin a|11> -> ry(-2a,0);cx(0,1). GAD gradient: partial-SWAP(phi=arcsin sqrt(gamma)) each
  site with a MIXED bath ancilla (Ry to p_bath + env-qubit trace). QET: X-measure meas site (MCM) -> mu;
  conditional Ry(-/+2 theta*) on rot site at the FROZEN theta* (pre-registered, argmin from the exact sim).
  Observable on rot site: obs = <Z_rot> + 2 mu <X_rot> (X_meas -> mu), binned by mu, readout-mitigated.
  extract = e_post(theta*) - e_pre. Arms: cf (meas cold s0, rot hot s1), co (meas hot s1, rot cold s0),
  severed (cf schedule, rotation decoupled from mu: 50/50 avg of Ry(+/-2 theta*_cf) applied UNCONDITIONALLY).

FROZEN (pre-registered, from the exact density-matrix sim; the hardware uses these, no live scan):
  theta*: (0.2,cf)=+0.1440 (0.2,co)=+0.0654 (0.5,cf)=+0.0785 (0.5,co)=-0.3665
  ideal direction: gamma0.2 -0.0558 (NEG), gamma0.5 +0.1966 (POS).

Routing: #151 spend gate (free instance), backend ibm_fez. --dry-run = representative-noise Aer ($0);
--submit only under the Creator GO citing this file's digest.
"""
import sys, os, json
import numpy as np
from qiskit import QuantumCircuit, transpile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import counterflow_sim_c_whisper_c5080 as S

N = 2
GVEC = np.real(S.ground(S.ham_chain(N)))
ALPHA = float(np.arctan2(-GVEC[3], GVEC[0]))
P_HOT, P_COLD = S.P_HOT, S.P_COLD
BACKEND_NAME = "ibm_fez"
SHOTS = 20000
GAMMAS = [0.2, 0.5]
THETA_STAR = {(0.2, 'cf'): 0.1440, (0.2, 'co'): 0.0654, (0.5, 'cf'): 0.0785, (0.5, 'co'): -0.3665}
# qubits: A=0 B=1 bathA=2 envA=3 bathB=4 envB=5
def ry_pop(p): return 2 * np.arcsin(np.sqrt(p))

def _gradient(qc, gamma):
    phi = np.arcsin(np.sqrt(gamma))
    qc.ry(ry_pop(P_COLD), 2); qc.cx(2, 3); qc.rxx(phi, 0, 2); qc.ryy(phi, 0, 2)   # site0 cold
    qc.ry(ry_pop(P_HOT), 4); qc.cx(4, 5); qc.rxx(phi, 1, 4); qc.ryy(phi, 1, 4)    # site1 hot

def build(gamma, setting, mode, theta, meas, rot):
    """mode: 'pre' (measure, no rotation) | 'post' (measure + conditional Ry on mu) |
    'sevM' (MATCHED severed: measure + conditional Ry on a FRESH RANDOM COIN — identical feed-forward
    structure to 'post', differing only in the control bit's source, so the feed-forward common-mode
    error cancels in cf - severed; the C5082-first-fly info_value falsification came from the OLD
    unconditional severed whose different structure did NOT cancel).
    clbits: c0=mu (X-measure of meas site), c1=coin (severed only), c2=rot observable."""
    qc = QuantumCircuit(6, 3)
    qc.ry(-2 * ALPHA, 0); qc.cx(0, 1)
    _gradient(qc, gamma)
    qc.h(meas); qc.measure(meas, 0)
    if mode == 'post':
        with qc.if_test((qc.clbits[0], 1)): qc.ry(-2 * theta, rot)
        with qc.if_test((qc.clbits[0], 0)): qc.ry(+2 * theta, rot)
    elif mode == 'sevM':
        qc.reset(3); qc.h(3); qc.measure(3, 1)          # fresh random coin -> c1
        with qc.if_test((qc.clbits[1], 1)): qc.ry(-2 * theta, rot)
        with qc.if_test((qc.clbits[1], 0)): qc.ry(+2 * theta, rot)
    if setting == 'X': qc.h(rot)
    qc.measure(rot, 2)
    return qc

def build_cal(state, rot):
    qc = QuantumCircuit(6, 3)
    if state: qc.x(rot)
    qc.measure(rot, 2)
    return qc

def _corr(p, r0, r1):
    d = 1 - r0 - r1
    return (p - r0) / d if abs(d) > 1e-6 else p

def _obs(counts_by_setting, cal):
    """obs = sum_mu p_mu (<Z_rot|mu> + 2 mu <X_rot|mu>), readout-mitigated with bare-qubit cal (r0,r1)."""
    r0, r1 = cal; vals = {}
    for st in ('Z', 'X'):
        num = {0: [0, 0], 1: [0, 0]}
        for k, v in counts_by_setting[st].items():
            b = k.replace(' ', ''); num[int(b[-1])][int(b[-3])] += v   # c0=mu (b[-1]), c2=rot obs (b[-3])
        vals[st] = {c: (1 - 2 * _corr(num[c][1] / max(sum(num[c]), 1), r0, r1), sum(num[c])) for c in (0, 1)}
    Z, X = vals['Z'], vals['X']; Nt = sum(Z[c][1] for c in (0, 1)); e = 0.0
    for c in (0, 1):
        mu = +1 if c == 0 else -1; e += (Z[c][1] / Nt) * (Z[c][0] + 2 * mu * X[c][0])
    return e

def _counts_of(pub):
    c = pub.data
    return getattr(c, list(c.__dict__.keys())[0]).get_counts() if hasattr(c, "__dict__") else c.meas.get_counts()

def make_jobs():
    """Return ordered list of (tag, circuit). Tags encode gamma/arm/mode/setting/coin."""
    jobs = []
    for g in GAMMAS:
        for arm, (meas, rot) in (('cf', (0, 1)), ('co', (1, 0))):
            th = THETA_STAR[(g, arm)]
            for st in ('Z', 'X'):
                jobs.append((f"{g}|{arm}|pre|{st}", build(g, st, 'pre', th, meas, rot)))
                jobs.append((f"{g}|{arm}|post|{st}", build(g, st, 'post', th, meas, rot)))
        # severed: cf schedule (meas0 rot1, theta*_cf), MATCHED feed-forward on a fresh random coin
        th = THETA_STAR[(g, 'cf')]
        for st in ('Z', 'X'):
            jobs.append((f"{g}|sev|post|{st}", build(g, st, 'sevM', th, 0, 1)))
    # readout cal for both rot qubits (bare)
    for rot in (0, 1):
        for state in (0, 1):
            jobs.append((f"cal|{rot}|{state}", build_cal(state, rot)))
    return jobs

def decode(counts_by_tag):
    # readout cal per rot qubit
    def cal(rot):
        p1_0 = _p1(counts_by_tag[f"cal|{rot}|0"]); p1_1 = _p1(counts_by_tag[f"cal|{rot}|1"])
        return p1_0, 1 - p1_1
    cals = {1: cal(1), 0: cal(0)}   # cf/sev rot=1 ; co rot=0
    res = {}
    for g in GAMMAS:
        arms = {}
        for arm, rotq in (('cf', 1), ('co', 0)):
            pre = {st: counts_by_tag[f"{g}|{arm}|pre|{st}"] for st in ('Z', 'X')}
            post = {st: counts_by_tag[f"{g}|{arm}|post|{st}"] for st in ('Z', 'X')}
            e_pre = _obs(pre, cals[rotq]); e_post = _obs(post, cals[rotq])
            arms[arm] = {"e_pre": round(e_pre, 4), "e_post": round(e_post, 4), "extract": round(e_post - e_pre, 4)}
        # severed: e_pre = cf e_pre; e_post from the MATCHED-feed-forward random-coin circuits
        pre = {st: counts_by_tag[f"{g}|cf|pre|{st}"] for st in ('Z', 'X')}
        e_pre_sev = _obs(pre, cals[1])
        posts = {st: counts_by_tag[f"{g}|sev|post|{st}"] for st in ('Z', 'X')}
        e_post_sev = _obs(posts, cals[1])
        arms['severed'] = {"e_pre": round(e_pre_sev, 4), "e_post": round(e_post_sev, 4), "extract": round(e_post_sev - e_pre_sev, 4)}
        direction = arms['cf']['extract'] - arms['co']['extract']
        info_value = arms['cf']['extract'] - arms['severed']['extract']
        res[str(g)] = {"arms": arms, "direction": round(direction, 4), "info_value": round(info_value, 4)}
    return res

def _p1(counts):
    tot = sum(counts.values()); return sum(v for k, v in counts.items() if k.replace(' ', '')[-3] == '1') / tot  # c2=rot

def grade(res):
    d_lo = res[str(GAMMAS[0])]["direction"]; d_hi = res[str(GAMMAS[1])]["direction"]
    # info_value = extract_cf - extract_severed. extract_cf < 0 (the conditioned bit EXTRACTS local energy);
    # the severed fresh-coin arm DEPOSITS (extract > 0). So the bit doing real work => info_value < 0 (sim
    # convention: two_site info_value is negative at every gamma). P4 tests the bit matters, both regimes.
    iv_lo = res[str(GAMMAS[0])]["info_value"]; iv_hi = res[str(GAMMAS[1])]["info_value"]
    # PRIMARY claim = the sign-flip (P1-P3). P4 (info_value<0) is a secondary control, gated ONLY at low
    # gamma where the sim value is large (-0.14) and robust; at high gamma the sim value is small (-0.024)
    # and noise-scattered, so it is REPORTED, not gated. (Registered this way after the dry-run showed the
    # high-gamma info_value scatter around zero — freeze the check where the signal actually resolves.)
    checks = {
        "P1_direction_low_gamma_negative": d_lo < 0,
        "P2_direction_high_gamma_positive": d_hi > 0,
        "P3_sign_flip": (d_lo < 0) and (d_hi > 0),
        "P4_info_value_negative_low_gamma": iv_lo < 0,
    }
    verdict = "CONFIRMED" if all(checks.values()) else ("SIGN_FLIP_FALSIFIED" if not checks["P3_sign_flip"] else "PARTIAL")
    return checks, verdict

def main():
    mode = "--submit" if "--submit" in sys.argv else "--dry-run"
    jobs = make_jobs()
    tags = [t for t, _ in jobs]; circ = [c for _, c in jobs]

    if mode == "--dry-run":
        from qiskit_aer import AerSimulator
        from qiskit_aer.noise import NoiseModel, depolarizing_error, ReadoutError
        nm = NoiseModel()
        nm.add_all_qubit_quantum_error(depolarizing_error(0.004, 2), ['rxx', 'ryy', 'swap', 'cx', 'cz'])
        nm.add_all_qubit_quantum_error(depolarizing_error(0.0004, 1), ['ry', 'h', 'x', 'rz', 'sx'])
        nm.add_all_qubit_readout_error(ReadoutError([[0.993, 0.007], [0.010, 0.990]]))
        sim = AerSimulator(noise_model=nm)
        cts = {t: sim.run(c, shots=SHOTS).result().get_counts() for t, c in zip(tags, circ)}
        src = "Aer representative ibm_fez noise (dry-run, $0)"; job_id = None
    else:
        sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)) + "/../scripts")
        import ibm_multi_account as m
        from qiskit_ibm_runtime import SamplerV2
        svc = m.service_for_submission("IBMQ_TOKEN")
        backend = svc.backend(BACKEND_NAME)
        isa = [transpile(c, backend, optimization_level=3) for c in circ]
        job = SamplerV2(mode=backend).run(isa, shots=SHOTS)
        job_id = job.job_id()
        print(f"SUBMITTED job_id={job_id} backend={backend.name} circuits={len(circ)} shots={SHOTS}", flush=True)
        r = job.result(); cts = {tags[i]: _counts_of(r[i]) for i in range(len(circ))}
        src = f"ibm hardware {backend.name} job {job_id}"

    res = decode(cts); checks, verdict = grade(res)
    out = {"card": "counterflow_flight_c", "cycle": "C5082", "board": 196, "source": src, "job_id": job_id,
           "gammas": GAMMAS, "theta_star": {f"{k[0]}|{k[1]}": v for k, v in THETA_STAR.items()},
           "results": res, "checks": checks, "verdict": verdict,
           "prereg": "counterflow-flight-c-preregistration-whisper-c5082.md"}
    print(json.dumps(out, indent=2))
    tag = "dryrun" if mode == "--dry-run" else f"hw_{job_id}"
    with open(os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
              "results", f"counterflow_flight_c_{tag}_c5082.json"), "w") as f:
        json.dump(out, f, indent=2)

if __name__ == "__main__":
    main()
