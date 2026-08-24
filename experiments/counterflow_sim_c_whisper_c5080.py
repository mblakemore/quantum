#!/usr/bin/env python3
"""counterflow_sim_c_whisper_c5080.py — Design C ($0 tier): the Information
Recuperator — does the DIRECTION of the information stream matter in a thermal
gradient?  (v2 — the v1 selftest correctly killed a wrong currency: net-total
is positive on the ground state because Alice's deposit exceeds Bob's
extraction (F97: deposit +0.740); QET's claim is WHERE energy appears, never
net gain. The primary observable below is the F97/exp119 lineage one.)

Creator direction 2026-08-24: "sim A -> C -> B" (board #192).

MODEL. exp119's Hotta minimal QET Hamiltonian, verbatim (h=k=1):
    H = sum_i Z_i + 2 sum_<ij> X_i X_j + offset  (offset computed so E_ground=0)
Thermal gradient: local generalized amplitude damping (GAD) of the ground
state, hot site toward bath P_HOT, cold toward P_COLD, equal strength gamma.

OBSERVABLE (primary, the exp119/F97 lineage): the ROTATED site's local energy
    obs_r = Z_r + 2 X_r X_neighbors  (+ its couplings),
referenced to its ground-state expectation r0 = <obs_r>_ground (computed, not
hand-offset). Reported per arm:
    e_post  = <obs_r> after the conditioned rotation (theta scanned to argmin)
    extract = e_post - e_pre   (e_pre = <obs_r> after measurement, before
              rotation; negative = the rotation removed local energy)
    info_value = extract_conditioned - extract_severed  (what the BIT bought,
              at matched schedule and angle; severed = fresh fair coin)
LEDGER (secondary): net = <H_total>_after - before, deposits included.

ARMS. counterflow: measure COLD site, rotate HOT site (information flows
against the heat direction). co-flow: mirrored. severed twin of each. uncond:
no measurement, best fixed rotation (the no-communication baseline given its
best legal move — under-priced-baseline class).

SELFTESTS (ground state, gamma=0):
  S1: direction symmetry to machine precision AND e_post(theta*) = -0.1147
      (matches the standalone reproduction of exp119; theta* = 0.1614 matched
      exp119's frozen 0.161) AND extract < 0.
  S2: info_value < -0.01 (the bit is strictly worth something on the ground
      state — a coin cannot teleport energy; H10-B4's passive lesson).

3-SITE RELAY (the exp195c wheel unrolled spatially): chain hot(0)-mid(1)-
cold(2); relay counterflow = measure 2 rotate 1, measure 1 rotate 0 (the bit
hops AGAINST the heat); co-flow mirrored; severed twin; per-hop extraction at
each rotated site, greedy per-hop angles.

OUTPUT: results/counterflow_sim_c_c5080.json + stdout tables.
"""
import json
import os

import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "..", "results", "counterflow_sim_c_c5080.json")

Z = np.diag([1.0, -1.0])
X = np.array([[0.0, 1.0], [1.0, 0.0]])
I2 = np.eye(2)
THETAS = np.linspace(-np.pi / 2, np.pi / 2, 721)
P_HOT, P_COLD = 0.40, 0.05


def kron(*ops):
    out = np.array([[1.0 + 0j]])
    for o in ops:
        out = np.kron(out, o)
    return out


def op_at(op, site, n):
    return kron(*[op if i == site else I2 for i in range(n)])


def ham_chain(n):
    H = sum(op_at(Z, i, n) for i in range(n))
    for i in range(n - 1):
        H = H + 2 * op_at(X, i, n) @ op_at(X, i + 1, n)
    ev = np.linalg.eigvalsh(H)
    return H - ev[0] * np.eye(2 ** n)


def ground(H):
    ev, evec = np.linalg.eigh(H)
    assert abs(ev[0]) < 1e-10
    return evec[:, 0]


def local_obs(site, n):
    """Z_site + its coupling terms (no offset; referenced to ground value)."""
    obs = op_at(Z, site, n)
    for nb in (site - 1, site + 1):
        if 0 <= nb < n:
            obs = obs + 2 * op_at(X, site, n) @ op_at(X, nb, n)
    return obs


def gad_kraus(gamma, p_bath):
    g, p = gamma, p_bath
    return [np.sqrt(1 - p) * np.array([[1, 0], [0, np.sqrt(1 - g)]]),
            np.sqrt(1 - p) * np.array([[0, np.sqrt(g)], [0, 0]]),
            np.sqrt(p) * np.array([[np.sqrt(1 - g), 0], [0, 1]]),
            np.sqrt(p) * np.array([[0, 0], [np.sqrt(g), 0]])]


def apply_local(rho, kraus, site, n):
    out = np.zeros_like(rho)
    for K in kraus:
        Kf = op_at(K, site, n)
        out += Kf @ rho @ Kf.conj().T
    return out


def ry(theta):
    return np.array([[np.cos(theta / 2), -np.sin(theta / 2)],
                     [np.sin(theta / 2), np.cos(theta / 2)]], dtype=complex)


def ev(rho, O):
    return float(np.real(np.trace(rho @ O)))


def measure_x(rho, site, n):
    outs = []
    for mu, sign in ((+1, +1), (-1, -1)):
        P = op_at((I2 + sign * X) / 2, site, n)
        pr = float(np.real(np.trace(P @ rho @ P)))
        if pr > 1e-15:
            outs.append((pr, P @ rho @ P / pr, mu))
    return outs


def arm(rho0, H, obs, meas_site, rot_site, n):
    """Conditioned arm: returns dict with theta*, e_pre, e_post, extract,
    net_total, plus the severed twin at the same theta."""
    e_tot0 = ev(rho0, H)
    branches = measure_x(rho0, meas_site, n)
    e_pre = sum(pr * ev(post, obs) for pr, post, _ in branches)
    best = (0.0, np.inf, None)
    for th in THETAS:
        e_post, rot_branches = 0.0, []
        for pr, post, mu in branches:
            R = op_at(ry(2 * mu * th), rot_site, n)
            nr = R @ post @ R.conj().T
            rot_branches.append((pr, nr))
            e_post += pr * ev(nr, obs)
        if e_post < best[1]:
            best = (float(th), float(e_post), rot_branches)
    th, e_post, rot_branches = best
    net = sum(pr * ev(nr, H) for pr, nr in rot_branches) - e_tot0
    # severed twin: same schedule and angle, fresh fair coin for the bit
    e_post_sev, net_sev = 0.0, 0.0
    for pr, post, _mu in branches:
        for coin in (+1, -1):
            R = op_at(ry(2 * coin * th), rot_site, n)
            nr = R @ post @ R.conj().T
            e_post_sev += 0.5 * pr * ev(nr, obs)
            net_sev += 0.5 * pr * ev(nr, H)
    net_sev -= e_tot0
    return dict(theta=th, e_pre=e_pre, e_post=e_post, extract=e_post - e_pre,
                extract_severed=e_post_sev - e_pre,
                info_value=(e_post - e_pre) - (e_post_sev - e_pre),
                net_total=net, net_total_severed=net_sev)


def arm_uncond(rho0, H, obs, rot_site, n):
    e_pre = ev(rho0, obs)
    best = (0.0, np.inf)
    for th in THETAS:
        R = op_at(ry(2 * th), rot_site, n)
        e_post = ev(R @ rho0 @ R.conj().T, obs)
        if e_post < best[1]:
            best = (float(th), float(e_post))
    return dict(theta=best[0], extract=best[1] - e_pre)


def biased(psi, n, gamma, baths):
    rho = np.outer(psi, psi.conj())
    for site, p in enumerate(baths):
        rho = apply_local(rho, gad_kraus(gamma, p), site, n)
    return rho


def relay(rho0, H, n, hops, coins=False, angles=None):
    """Sequential (measure, rotate) hops; greedy per-hop argmin on the rotated
    site's local obs. Returns per-hop extracts, final rho, angles used."""
    rho_c, used, extracts = rho0, [], []
    for i, (meas, rot) in enumerate(hops):
        obs = local_obs(rot, n)
        branches = measure_x(rho_c, meas, n)
        e_pre = sum(pr * ev(post, obs) for pr, post, _ in branches)
        if coins:
            th = angles[i]
            nxt, e_post = np.zeros_like(rho_c), 0.0
            for pr, post, _mu in branches:
                for coin in (+1, -1):
                    R = op_at(ry(2 * coin * th), rot, n)
                    nr = R @ post @ R.conj().T
                    nxt += 0.5 * pr * nr
                    e_post += 0.5 * pr * ev(nr, obs)
            rho_c = nxt
        else:
            best = (0.0, np.inf, None)
            for th in THETAS:
                e_post, rbs = 0.0, []
                for pr, post, mu in branches:
                    R = op_at(ry(2 * mu * th), rot, n)
                    nr = R @ post @ R.conj().T
                    rbs.append((pr, nr))
                    e_post += pr * ev(nr, obs)
                if e_post < best[1]:
                    best = (float(th), e_post, rbs)
            th, e_post, rbs = best
            rho_c = sum(pr * nr for pr, nr in rbs)
        used.append(th)
        extracts.append(float(e_post - e_pre))
    return extracts, rho_c, used


def main():
    results = {"primary": "extract = <obs_rot> post-rotation minus "
                          "post-measurement; info_value = extract minus "
                          "severed twin; ledger net = d<H_total>",
               "two_site": [], "three_site": []}

    # ---- 2-site ----
    n = 2
    H = ham_chain(n)
    psi = ground(H)
    rho_g = np.outer(psi, psi.conj())

    a_ch = arm(rho_g, H, local_obs(1, n), 0, 1, n)
    a_hc = arm(rho_g, H, local_obs(0, n), 1, 0, n)
    # reference each obs to its ground expectation (computed, not offset by
    # hand): e_post - r0 is the "below local ground" quantity exp119 certifies
    r0 = ev(rho_g, local_obs(1, n))
    s1 = (abs(a_ch["e_post"] - a_hc["e_post"]) < 1e-10
          and abs((a_ch["e_post"] - r0) - (-0.114746)) < 5e-4
          and a_ch["extract"] < 0)
    s2 = a_ch["info_value"] < -0.01
    print(f"S1 ground: e_post_rel={a_ch['e_post'] - r0:.6f} (ref -0.114746), "
          f"sym={abs(a_ch['e_post'] - a_hc['e_post']):.1e}, "
          f"extract={a_ch['extract']:.4f} -> {'PASS' if s1 else 'FAIL'}")
    print(f"S2 bit value on ground: info_value={a_ch['info_value']:.4f} "
          f"-> {'PASS' if s2 else 'FAIL'}")
    if not (s1 and s2):
        raise SystemExit("selftest failed")
    results["selftest"] = {"e_post": a_ch["e_post"],
                           "info_value": a_ch["info_value"]}

    print(f"\n2-SITE gradient (hot(0) bath {P_HOT}, cold(1) bath {P_COLD}); "
          f"counterflow = measure cold -> rotate hot:")
    print(f"{'gamma':>6} {'extr_cf':>9} {'extr_co':>9} {'DIR (cf-co)':>11} "
          f"{'infoval_cf':>10} {'infoval_co':>10} {'uncond_hot':>10} "
          f"{'net_cf':>8} {'net_co':>8}")
    for gamma in (0.0, 0.1, 0.2, 0.3, 0.5, 0.7):
        rho = biased(psi, n, gamma, [P_HOT, P_COLD])
        cf = arm(rho, H, local_obs(0, n), 1, 0, n)   # measure cold(1), rotate hot(0)
        co = arm(rho, H, local_obs(1, n), 0, 1, n)   # measure hot(0), rotate cold(1)
        un = arm_uncond(rho, H, local_obs(0, n), 0, n)
        row = dict(gamma=gamma, cf=cf, co=co, uncond_hot=un,
                   direction=cf["extract"] - co["extract"])
        results["two_site"].append(row)
        print(f"{gamma:>6.2f} {cf['extract']:>9.5f} {co['extract']:>9.5f} "
              f"{row['direction']:>11.5f} {cf['info_value']:>10.5f} "
              f"{co['info_value']:>10.5f} {un['extract']:>10.5f} "
              f"{cf['net_total']:>8.4f} {co['net_total']:>8.4f}")

    # ---- 3-site relay ----
    n = 3
    H3 = ham_chain(n)
    psi3 = ground(H3)
    print(f"\n3-SITE RELAY (hot(0)-mid(1)-cold(2), baths "
          f"[{P_HOT}, {(P_HOT + P_COLD) / 2}, {P_COLD}]); per-hop extracts sum:")
    print(f"{'gamma':>6} {'relay_cf':>9} {'relay_co':>9} {'DIR':>9} "
          f"{'sev_cf':>9} {'infoval_cf':>10}")
    for gamma in (0.0, 0.2, 0.5):
        rho = biased(psi3, n, gamma, [P_HOT, (P_HOT + P_COLD) / 2, P_COLD])
        ex_cf, _, ang_cf = relay(rho, H3, n, [(2, 1), (1, 0)])
        ex_co, _, _ = relay(rho, H3, n, [(0, 1), (1, 2)])
        ex_sv, _, _ = relay(rho, H3, n, [(2, 1), (1, 0)], coins=True,
                            angles=ang_cf)
        row = dict(gamma=gamma, relay_cf=sum(ex_cf), relay_co=sum(ex_co),
                   direction=sum(ex_cf) - sum(ex_co), severed_cf=sum(ex_sv),
                   info_value_cf=sum(ex_cf) - sum(ex_sv),
                   per_hop_cf=ex_cf, per_hop_co=ex_co)
        results["three_site"].append(row)
        print(f"{gamma:>6.2f} {sum(ex_cf):>9.5f} {sum(ex_co):>9.5f} "
              f"{row['direction']:>9.5f} {sum(ex_sv):>9.5f} "
              f"{row['info_value_cf']:>10.5f}")

    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as f:
        json.dump(results, f, indent=2, default=float)
    print(f"\nwrote {os.path.relpath(OUT, HERE + '/..')}")


if __name__ == "__main__":
    main()
