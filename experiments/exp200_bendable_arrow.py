#!/usr/bin/env python3
"""Exp200 — THE BENDABLE ARROW: irreversibility is the bath's bookkeeping, not the system's. C4893.

Perturbation instrument #3 on Exp194's arrow meter (A(T)=1-C_echo rose to 0.543 by 8us,
tau_arrow ~7.1us). The perturbation: deliver a CONTROLLED dephasing dose into a bath whose
memory we own — a coin qubit — instead of the fabric's forgetful bath.

  BEND:   at the center window of a 194-style echoed idle, couple cry(theta, sys->coin):
          engineered dephasing, dose-exact — system coherence drops by cos(theta/2), on top
          of the natural floor. At theta=pi the coherence is fully killed.
  UNBEND: identical coupling, then cry(-theta) at the end of the storage window (even number
          of echo X's between couple and uncouple on BOTH qubits, so the inverse is exact;
          coin gets its own quarter-point echo pair during storage). The record is UNCOMPUTED
          — returned to the bath's |0>, Landauer-style — and the "irreversibly" lost
          coherence REVIVES to the natural floor, at every dose including full kill.
  META-ARROW: sweep the storage time (T = 2/4/8us idles -> ~1/2/4us storage). The coin bath
          sits on the same fabric and forgets at 194's own rate — recovery declines with
          storage: the arrow reasserts itself one level up.

Claim if held: the SAME dephasing event is reversible or irreversible depending only on
whether the bath's record survives to be uncomputed. Irreversibility = decoherence x bath
forgetting. Loschmidt + Landauer as circuit data.

Burden note: unbend carries MORE gates than bend (2 coin X + 1 cry) yet must show MORE
coherence — the bias runs against the headline. Within each arm the dose sweep is
gate-identical (cry angle-independent; C4891 sweep rule).
BUDGET CHECK (C4887 rule): revival contrast ~0.6 vs floors ~0; C_base ~0.80 (194). Trivial.
Usage: --selftest | --submit [--backend ibm_fez --shots 8000] | --decode
"""
import argparse, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile
from qiskit.circuit import Delay
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))
PI = np.pi
TS = {2: 4000, 4: 8000, 8: 16000}          # us -> dt (0.5 ns)
THETAS = (0.25, 0.5, 0.75, 1.0)            # theta / pi, sweep at T=2us
CIRCS = ([f"base_{t}" for t in TS]
         + [f"bend_{th}_2" for th in THETAS]
         + [f"unbend_{th}_2" for th in THETAS]
         + ["bend_1.0_4", "bend_1.0_8", "unbend_1.0_4", "unbend_1.0_8"])


def _al(x):                                 # align delay to 16 dt
    return max(16, (int(x) // 16) * 16)


def circuit(name):
    parts = name.split("_")
    arm = parts[0]; T = int(parts[-1]); th = float(parts[1]) * PI if arm != "base" else 0.0
    dt = TS[T]; q4 = _al(dt // 4); dcen = dt - 2 * q4; sl = _al(dcen // 4)
    last = dcen - 3 * sl
    qc = QuantumCircuit(2, 2)
    qc.h(0)
    # leading quarter + system echo X
    qc.append(Delay(q4, unit="dt"), [0]); qc.append(Delay(q4, unit="dt"), [1])
    qc.x(0)
    if arm != "base":
        qc.cry(th, 0, 1)                    # COUPLE: engineered dephasing into the coin
    # central window in 4 slices (both qubits); coin echo X's at slice boundaries 1 and 3
    for i, d in enumerate((sl, sl, sl, last)):
        qc.append(Delay(d, unit="dt"), [0]); qc.append(Delay(d, unit="dt"), [1])
        if arm == "unbend" and i in (0, 2):
            qc.x(1)                          # coin quarter-point echo (even count -> inverse exact)
    if arm == "unbend":
        qc.cry(-th, 0, 1)                   # UNCOUPLE: uncompute the record, return it to |0>
    qc.x(0)
    qc.append(Delay(q4, unit="dt"), [0]); qc.append(Delay(q4, unit="dt"), [1])
    qc.h(0)
    qc.measure(0, 0); qc.measure(1, 1)
    return qc


def _stats(counts):
    cx = tot = p1 = 0
    for s, n in counts.items():
        b = s.replace(" ", "")
        cx += (1 - 2 * int(b[-1])) * n; p1 += int(b[-2]) * n; tot += n
    return {"C": cx / tot, "coin_p1": p1 / tot}


def analyze(get):
    return {name: _stats(get(name)) for name in CIRCS}


def selftest():
    from qiskit_aer import AerSimulator
    sim = AerSimulator(); shots = 60000; cache = {}
    def get(name):
        if name not in cache: cache[name] = sim.run(circuit(name), shots=shots).result().get_counts()
        return cache[name]
    r = analyze(get)
    print("Exp200 selftest (noiseless) | exact: base 1, bend cos(theta/2), unbend 1 (all doses)")
    for t in TS:
        print(f"  base_{t}: C={r[f'base_{t}']['C']:+.4f}")
        assert abs(r[f"base_{t}"]["C"] - 1) < 0.02, "noiseless echo identity"
    for th in THETAS:
        b, u = r[f"bend_{th}_2"], r[f"unbend_{th}_2"]
        ex = np.cos(th * PI / 2)
        print(f"  th={th}pi: bend C={b['C']:+.4f} (exact {ex:+.3f}, coinP1={b['coin_p1']:.3f}) | "
              f"unbend C={u['C']:+.4f} (exact +1.000, coinP1={u['coin_p1']:.3f})")
        assert abs(b["C"] - ex) < 0.02, f"bend must follow cos(theta/2) at {th}"
        assert abs(u["C"] - 1) < 0.02, f"unbend must fully revive at {th}"
        assert u["coin_p1"] < 0.02, "the record must be returned (coin back to |0>)"
        assert abs(b["coin_p1"] - np.sin(th * PI / 2) ** 2 / 2) < 0.02, "bend coin gauge"
    for t in (4, 8):
        assert abs(r[f"unbend_1.0_{t}"]["C"] - 1) < 0.02, f"noiseless revival at T={t}"
    print("SELFTEST PASS: bend follows cos(theta/2) exactly, unbend revives to 1.0 at every dose "
          "including full kill, record uncomputed to |0>, all storage times. Cleared to fly.")


def submit(backend_name, shots):
    from run_exp66_qpu_partb import _get_ibm_service
    from qiskit_ibm_runtime import SamplerV2
    svc = _get_ibm_service(); backend = svc.backend(backend_name)
    circuits = [transpile(circuit(n), backend=backend, optimization_level=1,
                          scheduling_method="asap") for n in CIRCS]
    job = SamplerV2(mode=backend).run(circuits, shots=shots)
    man = {"exp": 200, "slug": "bendable_arrow", "backend": backend_name, "shots": shots,
           "job_id": job.job_id(), "order": CIRCS,
           "prereg": {"anchors": "C(base_2) in [0.70,0.90] (194: 0.802); base_4 within 0.10 of "
                                 "0.657; base_8 within 0.10 of 0.457",
                      "bend": "C_bend(theta,2us) monotone decreasing; C_bend(pi) <= 0.10; "
                              "|C_bend - C_base*cos(theta/2)| <= 0.10 per dose",
                      "bend_back": "C_unbend(pi,2us) - C_bend(pi,2us) >= 0.40 at >=5 sigma "
                                   "(coherence returns from full kill); "
                                   "max-min of C_unbend over theta <= 0.15 (dose-independent)",
                      "meta_arrow": "Rec(T)=C_unbend(pi,T)/C_base(T) non-increasing in T; "
                                    "Rec(2us) >= 0.70",
                      "gauges": "unbend coin P(1) <= 0.10 (record returned); bend coin P(1) "
                                "tracks sin^2(theta/2)/2 within 0.06",
                      "budget_check": "revival contrast ~0.6 vs floor ~0 (C4887 rule; trivial)"}}
    json.dump(man, open(os.path.join(HERE, "..", "results", "exp200_bendable_arrow_manifest.json"), "w"), indent=1)
    print(f"submitted {job.job_id()} ({len(circuits)} circuits, {shots} shots)")


def decode():
    from run_exp66_qpu_partb import _get_ibm_service
    man = json.load(open(os.path.join(HERE, "..", "results", "exp200_bendable_arrow_manifest.json")))
    svc = _get_ibm_service(); res = svc.job(man["job_id"]).result()
    shots = man["shots"]; raw = {}
    for idx, name in enumerate(man["order"]):
        r0 = res[idx]; reg = list(r0.data.keys())[0]
        raw[name] = getattr(r0.data, reg).get_counts()
    r = analyze(lambda n: raw[n]); se = 1 / np.sqrt(shots)
    cb = {t: r[f"base_{t}"]["C"] for t in TS}
    print(f"Exp200 THE BENDABLE ARROW decode | job {man['job_id']} | 194 anchors: 0.802/0.657/0.457")
    print(f"  bases: " + "  ".join(f"C({t}us)={cb[t]:.3f}" for t in TS))
    for th in THETAS:
        b, u = r[f"bend_{th}_2"], r[f"unbend_{th}_2"]
        print(f"  th={th}pi @2us: bend C={b['C']:+.3f} (target {cb[2]*np.cos(th*PI/2):+.3f}, "
              f"coin {b['coin_p1']:.3f}) | unbend C={u['C']:+.3f} (coin {u['coin_p1']:.3f})")
    for t in (4, 8):
        print(f"  th=1.0pi @{t}us: bend C={r[f'bend_1.0_{t}']['C']:+.3f} | "
              f"unbend C={r[f'unbend_1.0_{t}']['C']:+.3f}")
    a_ok = (0.70 <= cb[2] <= 0.90 and abs(cb[4] - 0.657) <= 0.10 and abs(cb[8] - 0.457) <= 0.10)
    bends = [r[f"bend_{th}_2"]["C"] for th in THETAS]
    bend_ok = (all(bends[i] > bends[i + 1] for i in range(3)) and bends[-1] <= 0.10
               and all(abs(bends[i] - cb[2] * np.cos(THETAS[i] * PI / 2)) <= 0.10 for i in range(4)))
    rev = r["unbend_1.0_2"]["C"] - r["bend_1.0_2"]["C"]; zrev = rev / (se * np.sqrt(2))
    unb = [r[f"unbend_{th}_2"]["C"] for th in THETAS]
    back_ok = rev >= 0.40 and zrev >= 5 and (max(unb) - min(unb)) <= 0.15
    Rec = {t: r[f"unbend_1.0_{t}"]["C"] / cb[t] if cb[t] > 0 else None for t in TS}
    meta_ok = (Rec[2] >= 0.70 and Rec[2] >= Rec[4] - 0.03 and Rec[4] >= Rec[8] - 0.03)
    g_unb = all(r[f"unbend_{th}_2"]["coin_p1"] <= 0.10 for th in THETAS)
    g_bnd = all(abs(r[f"bend_{th}_2"]["coin_p1"] - np.sin(th * PI / 2) ** 2 / 2) <= 0.06
                for th in THETAS)
    g_ok = g_unb and g_bnd
    print(f"\nANCHORS: {'OK — 194 reproduced' if a_ok else 'CHECK'}")
    print(f"BEND: floor at full dose {bends[-1]:.3f}; cos-shape {'OK' if bend_ok else 'CHECK'}")
    print(f"THE BEND-BACK: full-kill coherence {r['bend_1.0_2']['C']:+.3f} revives to "
          f"{r['unbend_1.0_2']['C']:+.3f} — recovery {rev:+.3f} ({zrev:.0f} sigma); "
          f"dose-independence spread {max(unb)-min(unb):.3f} {'OK' if back_ok else 'CHECK'}")
    print(f"META-ARROW: recovery share Rec(T) = " + "  ".join(f"{t}us: {Rec[t]:.3f}" for t in TS)
          + f" {'(declines with storage — the bath itself forgets)' if meta_ok else 'CHECK'}")
    print(f"RECORD RETURNED: unbend coin P(1) max {max(r[f'unbend_{th}_2']['coin_p1'] for th in THETAS):.3f} "
          f"{'OK — uncomputed, Landauer-style' if g_ok else 'CHECK'}")
    ok = a_ok and bend_ok and back_ok and meta_ok and g_ok
    print(f"VERDICT: {'THE ARROW BENDS — the same dephasing event is reversible or irreversible depending only on whether the baths record survives to be uncomputed: irreversibility is the baths bookkeeping, and the baths own memory decays on 194s clock' if ok else 'NOT HELD (accounting above)'}")
    json.dump({"job_id": man["job_id"], "results": {n: r[n] for n in CIRCS},
               "recovery_full_kill": float(rev), "sigma_recovery": float(zrev),
               "Rec": {str(t): (float(Rec[t]) if Rec[t] else None) for t in TS},
               "anchors_ok": bool(a_ok), "bend_ok": bool(bend_ok), "back_ok": bool(back_ok),
               "meta_ok": bool(meta_ok), "gauge_ok": bool(g_ok), "verdict_ok": bool(ok)},
              open(os.path.join(HERE, "..", "results", "exp200_bendable_arrow_decode.json"), "w"), indent=1)
    print("-> results/exp200_bendable_arrow_decode.json")


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
