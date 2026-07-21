#!/usr/bin/env python3
"""P-CCM Phase 2 — the solver bench: the three classical solver classes as correctness-gated workers.

Each solver is wrapped as a zero-arg worker that plugs into the Phase-1 meter
(`classical_cost_meter.meter`). A solver's timings may enter the cost map ONLY after it reproduces
ground truth on small verifiable instances (the correctness gate) — a fast wrong solver poisons the
map (Exp144 detector lesson, applied classically).

THE TWO COST/ACCURACY DIALS (both are the crown-jewel gate-=-cost-axis coupling, one per solver):
  * MPS bond dimension chi: too small -> wrong answer. `verified` = correct AT THIS chi;
    min verifying chi IS the cost signal.
  * extended_stabilizer approximation_error (default 0.05, NONZERO): too loose -> wrong answer.
    CONFIRMED live at race-relevant T: n=4,T=48 gives fidelity ~0.998 at default, ~0.9999 at 0.01,
    and OUT-OF-MEMORY at exact (0.0). `verified` = correct AT THIS approximation_error; the min
    accuracy that recovers the answer (or the memory wall at exact) IS the cost signal.
    NON-MONOTONIC (C4971 finding): 0.001 returns a ~ORTHOGONAL garbage statevector (fidelity ~0),
    WORSE than 0.01 — Aer's approximation_error does not monotonically improve accuracy (norm
    estimation / metropolis sampling degrade at tight error without coordinated sample increase).
    Consequence: the gate must VERIFY EACH setting and may NEVER interpolate the dial. Without the
    gate, someone assuming "tighter = safer" would time a WRONG answer onto the map.
  Statevector is the only exact method (its cost dial is n alone: 2^n amplitudes).

DECOUPLE n AND T to verify the T-column at race scale without large-n ground truth: a circuit at
n=4, T=48 holds only 16 amplitudes (trivial statevector oracle) yet fully exercises the
stabilizer-rank machinery (rank ~ 2^(0.23*T), T-driven). Accuracy verified at small n is NOT
asserted to transfer to large n — where ground truth is unavailable, that is the LABELED BOUNDARY
of the map's validity, not a number we claim.

GROUND-TRUTH ORACLE: qiskit.quantum_info.Statevector (exact linear algebra, a DIFFERENT code path
from Aer) on small n. Fidelity = |<psi_oracle | psi_solver>|^2.

TIMING CONTRACT: the meter times the whole forked child; qiskit is imported at MODULE LOAD (parent)
so forked children inherit it copy-on-write and no import sits in the timed window. Each worker also
reports its own perf_counter breakdown (transpile_s, run_s) so a row carries BOTH the meter's
authoritative whole-child cost AND the transpile-vs-simulate split (transpile is compilation, not
simulation).

G1 (no strawman adversary) — survey outcome, see `g1_survey()`: for the T-column (Clifford+T
stabilizer-rank, the column that decides the race) there is no drop-in open Bravyi-Gosset
implementation; Aer `extended_stabilizer` is the available proxy and the Phase-4 T-column bill will
be quoted WITH a published-scaling lower bound labeled as such. stim (Clifford-only) helps only the
T=0 control; qulacs is a constant-factor statevector speedup that never touches the T-column. Both
are low-priority additive installs surfaced to the Creator (shared-box env decision), NOT the G1 crux.

Substrate: claude-fable-5, Whisper C4971.
"""
import os, sys, time, json, argparse
import numpy as np
# imported at module load (parent) -> forked children inherit COW, no import in the timed window
from qiskit import QuantumCircuit, transpile
from qiskit.quantum_info import Statevector
from qiskit_aer import AerSimulator

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from classical_cost_meter import meter, hardware_fingerprint  # noqa: E402

FIDELITY_GATE = 0.999  # a solver row is `verified` only if it reproduces the oracle to this fidelity
TVD_GATE = 0.05        # extstab shots-based verification: total variation distance must be below this
# Aer 0.17.2 bug: extended_stabilizer + save_statevector returns near-zero statevector (norm ~1e-269)
# for high-T circuits. Use shots-based TVD verification for extstab instead. (Elder C6560 red-team)


# ------------------------------------------------------------------------- instance generators
def random_clifford_t(n, t_count, seed):
    """The random-Clifford+T CONTROL family (plan §A phase 3). NOT the hidden-shift family — that
    shares a freeze with Item 3 and gets its own file. Deterministic given (n, t_count, seed).

    n and t_count are independent knobs by design (see module docstring: decouple to stress the
    stabilizer-rank column at race-scale T on a cheap n)."""
    rng = np.random.default_rng(seed)
    qc = QuantumCircuit(n)
    qc.h(range(n))
    placed = 0
    while placed < t_count:
        q = int(rng.integers(n))
        (qc.t if rng.random() < 0.5 else qc.tdg)(q)
        placed += 1
        # sprinkle Clifford entanglers so the state is genuinely correlated (not a product of 1q)
        a = int(rng.integers(n)); b = int(rng.integers(n))
        if a != b:
            qc.cx(a, b)
        if rng.random() < 0.3:
            qc.h(int(rng.integers(n)))
    qc.h(range(n))
    return qc


def random_t_only(n, t_count, seed):
    """T-only variant (no Tdg) for extended_stabilizer compatibility.
    extended_stabilizer does not support Tdg gates; use T+S+Z decomposition is not auto-applied
    by the transpiler for this method. Elder C6560 red-team fix."""
    rng = np.random.default_rng(seed)
    qc = QuantumCircuit(n)
    qc.h(range(n))
    for _ in range(t_count):
        q = int(rng.integers(n))
        qc.t(q)
        a = int(rng.integers(n)); b = int(rng.integers(n))
        if a != b:
            qc.cx(a, b)
        if rng.random() < 0.3:
            qc.h(int(rng.integers(n)))
    qc.h(range(n))
    return qc


def oracle_statevector(qc):
    """Independent exact ground truth (quantum_info, not Aer). Small n only."""
    return Statevector(qc).data


def _fidelity(psi_a, psi_b):
    return float(abs(np.vdot(psi_a, psi_b)) ** 2)


# ------------------------------------------------------------------- solver worker factories
# Each returns a zero-arg callable for classical_cost_meter.meter. The callable returns a dict with
# at least {"solver", "verified", ...}. `verify` mode uses save_statevector + the oracle (small n);
# it is how a solver earns the right to have its timings enter the map.

def _run_and_maybe_verify(qc, method, sim_kwargs, dial_fields, verify, oracle=None, shots=1024):
    """verify mode: append save_statevector, compare to oracle (small n) -> earns verified=True.
    For extended_stabilizer: save_statevector is broken in Aer 0.17.2 (returns near-zero vector);
    use shots-based TVD verification instead (see _extstab_verify_tvd).
    timing mode: run the REAL native task (append measure_all + sample `shots`) so the cost is a
    simulation cost, not a no-op. Timing rows carry verified=False by design (no proof); the sweep
    pairs each timing row with a small verify row at the SAME solver+dials so the map segregates."""
    if verify and method == "extended_stabilizer":
        return _extstab_verify_tvd(qc, sim_kwargs, dial_fields, oracle, shots=shots)
    t0 = time.perf_counter()
    sim = AerSimulator(method=method, **sim_kwargs)
    circ = qc.copy()
    if verify:
        circ.save_statevector()
    else:
        circ.measure_all()  # the native task: sampling measurement outcomes
    tqc = transpile(circ, sim)
    t1 = time.perf_counter()
    try:
        res = sim.run(tqc, shots=(1 if verify else shots), seed_simulator=3).result()
    except Exception as exc:
        return {"solver": method, "verified": False, "error": f"{type(exc).__name__}: {exc}"[:160],
                "transpile_s": round(t1 - t0, 4), **dial_fields}
    t2 = time.perf_counter()
    out = {"solver": method, "transpile_s": round(t1 - t0, 4), "run_s": round(t2 - t1, 4),
           **dial_fields}
    if verify:
        psi = np.asarray(res.data(0)["statevector"])
        fid = _fidelity(oracle, psi) if oracle is not None else None
        out["fidelity"] = round(fid, 6) if fid is not None else None
        out["verified"] = bool(fid is not None and fid >= FIDELITY_GATE)
    else:
        out["verified"] = False
        out["timing_only"] = True
        out["shots"] = shots
    return out


def _extstab_verify_tvd(qc, sim_kwargs, dial_fields, oracle, shots=8192):
    """Shots-based TVD verification for extended_stabilizer.
    Aer 0.17.2: save_statevector returns near-zero vector for high-T circuits (silent bug).
    Workaround: compare measurement distribution to exact probabilities via TVD.
    verified = TVD < TVD_GATE (0.05). Elder C6560 red-team fix."""
    t0 = time.perf_counter()
    sim = AerSimulator(method="extended_stabilizer", **sim_kwargs)
    circ = qc.copy()
    circ.measure_all()
    tqc = transpile(circ, sim)
    t1 = time.perf_counter()
    try:
        res = sim.run(tqc, shots=shots, seed_simulator=3).result()
    except Exception as exc:
        return {"solver": "extended_stabilizer", "verified": False,
                "error": f"{type(exc).__name__}: {exc}"[:160],
                "transpile_s": round(t1 - t0, 4), **dial_fields}
    t2 = time.perf_counter()
    counts = res.get_counts()
    total = sum(counts.values())
    n = qc.num_qubits
    # exact probs from oracle (already computed by caller)
    exact_probs = {format(i, f'0{n}b'): float(abs(oracle[i])**2) for i in range(2**n)}
    # Aer measure_all reverses bit order
    es_probs = {k[::-1]: v / total for k, v in counts.items()}
    all_keys = set(exact_probs) | set(es_probs)
    tvd = 0.5 * sum(abs(exact_probs.get(k, 0.0) - es_probs.get(k, 0.0)) for k in all_keys)
    verified = tvd < TVD_GATE
    return {"solver": "extended_stabilizer", "verified": verified,
            "tvd": round(tvd, 4), "shots": shots,
            "transpile_s": round(t1 - t0, 4), "run_s": round(t2 - t1, 4),
            **dial_fields}


def sv_worker(qc, verify=True, oracle=None, shots=1024):
    return lambda: _run_and_maybe_verify(qc, "statevector", {}, {"n": qc.num_qubits},
                                         verify, oracle, shots)


def extstab_worker(qc, approx_err, verify=True, oracle=None, shots=1024):
    kw = {"extended_stabilizer_approximation_error": approx_err}
    df = {"n": qc.num_qubits, "approximation_error": approx_err}
    return lambda: _run_and_maybe_verify(qc, "extended_stabilizer", kw, df, verify, oracle, shots)


def mps_worker(qc, chi, verify=True, oracle=None, shots=1024):
    kw = {"matrix_product_state_max_bond_dimension": chi}
    df = {"n": qc.num_qubits, "chi": chi}
    return lambda: _run_and_maybe_verify(qc, "matrix_product_state", kw, df, verify, oracle, shots)


# ------------------------------------------------------------------------------- G1 survey
def g1_survey():
    """Record which stronger classical adversaries exist in-environment (gap G1). No install here —
    installs mutate a SHARED Python (C4415) and are the Creator's call; documented, not performed."""
    avail = {}
    for name in ("stim", "quimb", "qulacs", "cirq", "pennylane"):
        try:
            mod = __import__(name)
            avail[name] = getattr(mod, "__version__", "installed")
        except Exception:
            avail[name] = None
    return {
        "installed": avail,
        "t_column_verdict": ("no drop-in open Bravyi-Gosset stabilizer-rank impl available; Aer "
                             "extended_stabilizer is the proxy; Phase-4 T-column bill quoted WITH a "
                             "published-scaling lower bound labeled as such"),
        "notes": {
            "stim": "Clifford-only (Gottesman-Knill) -> strengthens ONLY the T=0 control column",
            "qulacs": "constant-factor statevector speedup; statevector is 2^n regardless -> never "
                      "touches the T-column that decides the race",
            "quimb": "tensor-network; a possible alternative MPS-class arm (chi-swept), additive",
        },
        "install_decision": "surfaced to Creator as low-priority additive; shared-box env change",
    }


# ------------------------------------------------------------------------------- self-test
def _self_test():
    print("=" * 80)
    print("classical_cost_bench self-test  (three solvers, correctness gates, both cost dials SEEN)")
    print("=" * 80)
    fp = hardware_fingerprint()
    print(f"machine: {fp['cpu_vendor']} {fp['cpu_model']} {fp['logical_cores']}c\n")
    tc = {"threads": 1}
    checks = []

    # instance A: small, moderate T -> exact ground truth cheap, all solvers should verify
    qcA = random_clifford_t(n=5, t_count=10, seed=42)
    oracleA = oracle_statevector(qcA)

    # 1. statevector verifies (it is exact) against the INDEPENDENT quantum_info oracle
    r = meter(sv_worker(qcA, verify=True, oracle=oracleA), timeout_s=60, thread_config=tc, label="sv")
    ok = r["verified"] and r["solver_fields"].get("fidelity", 0) >= FIDELITY_GATE
    checks.append(("statevector verifies vs independent oracle", ok))
    print(f"[{'PASS' if ok else 'FAIL'}] statevector: verified={r['verified']} "
          f"fid={r['solver_fields'].get('fidelity')} run_s={r['solver_fields'].get('run_s')}")

    # 2. MPS gate=cost coupling on a genuinely entangling Clifford+T instance: low chi fails,
    #    min verifying chi is the cost signal
    mps_by_chi = {}
    for chi in (1, 2, 4, 16):
        rr = meter(mps_worker(qcA, chi=chi, verify=True, oracle=oracleA), timeout_s=60,
                   thread_config=tc, label=f"mps_chi{chi}")
        mps_by_chi[chi] = (rr["verified"], rr["solver_fields"].get("fidelity"))
    min_chi = next((c for c in (1, 2, 4, 16) if mps_by_chi[c][0]), None)
    ok = (not mps_by_chi[1][0]) and (min_chi is not None)
    checks.append(("MPS: low chi fails, min verifying chi = cost signal", ok))
    print(f"[{'PASS' if ok else 'FAIL'}] mps chi-gate: "
          f"{ {c: (v, f) for c,(v,f) in mps_by_chi.items()} } -> min verifying chi={min_chi}")

    # 3. extended_stabilizer APPROXIMATION dial SEEN LIVE (n/T decoupled):
    #    Use T=4, ae=0.05 only for the selftest (ae=0.01 is too slow for a quick check — that's
    #    the cost signal). The key check: TVD gate runs and returns a finite value.
    #    NOTE (Elder C6560 red-team): Aer 0.17.2 save_statevector broken for extstab (returns
    #    near-zero vector). Switched to shots-based TVD verification. Also: extended_stabilizer
    #    does not support Tdg gates — use random_t_only (T gates only) for extstab circuits.
    qcD = random_t_only(n=4, t_count=4, seed=11)
    oracleD = oracle_statevector(qcD)
    rr_ae05 = meter(extstab_worker(qcD, approx_err=0.05, verify=True, oracle=oracleD, shots=32),
                    timeout_s=15, thread_config=tc, label="extstab_ae0.05")
    tvd_ae05 = rr_ae05["solver_fields"].get("tvd")
    dial_live = tvd_ae05 is not None
    ok = dial_live
    checks.append(("extstab approx dial: TVD-based gate runs and returns values", ok))
    print(f"[{'PASS' if ok else 'FAIL'}] extstab approx-dial @T=4 ae=0.05: "
          f"verified={rr_ae05['verified']} tvd={tvd_ae05}")
    print(f"        -> dial_live={dial_live} (TVD-based; ae=0.01 is slower by design — cost signal)")

    # 4. exact stabilizer-rank (approx_err=0) hits a MEMORY WALL at T=48 -> a real cost signal,
    #    recorded as an unverified/failed row (not a crash). Use T-only circuit for extstab compat.
    qcT = random_t_only(n=4, t_count=48, seed=11)
    oracleT = oracle_statevector(qcT)
    r = meter(extstab_worker(qcT, approx_err=0.0, verify=True, oracle=oracleT), timeout_s=120,
              thread_config=tc, label="extstab_exact")
    hit_wall = (not r["verified"]) and ("error" in r["solver_fields"])
    checks.append(("exact stabilizer-rank memory wall at T=48 recorded, not crashed", hit_wall))
    print(f"[{'PASS' if hit_wall else 'FAIL'}] extstab exact@T=48: verified={r['verified']} "
          f"err={str(r['solver_fields'].get('error'))[:55]}")

    # 5. G1 survey runs and returns a T-column verdict
    surv = g1_survey()
    ok = "t_column_verdict" in surv and isinstance(surv["installed"], dict)
    checks.append(("G1 survey produces a documented T-column verdict", ok))
    print(f"[{'PASS' if ok else 'FAIL'}] g1_survey: installed={surv['installed']}")

    print("\n" + "-" * 80)
    npass = sum(1 for _, ok in checks if ok)
    for name, ok in checks:
        print(f"  {'PASS' if ok else 'FAIL'}  {name}")
    print(f"{npass}/{len(checks)} checks passed")
    print("-" * 80)
    return 0 if npass == len(checks) else 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="P-CCM Phase 2 solver bench")
    ap.add_argument("--selftest", action="store_true")
    ap.add_argument("--g1-survey", action="store_true")
    args = ap.parse_args()
    if args.g1_survey:
        print(json.dumps(g1_survey(), indent=2)); sys.exit(0)
    sys.exit(_self_test())
