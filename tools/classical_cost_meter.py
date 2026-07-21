#!/usr/bin/env python3
"""P-CCM Phase 1 — the classical cost meter: the instrument the classical cost map (Item 2) quotes.

WHAT THIS IS: a solver-agnostic harness that meters ONE unit of classical simulation work and
returns a frozen row. Every future crossover / race statement (Items 3-4) quotes rows produced
here, so the meter itself must be trustworthy before any curve is drawn. This file is Phase 1 only
(the meter + its self-test); the solver bench, instance generator, sweep, and card are Phases 2-5.

FOUR REQUIREMENTS drive the one architectural decision below (each fails without it):
  * Timeout / censoring: a native C++ solver (Aer) cannot be interrupted from Python (SIGALRM is
    only checked between bytecode ops; a thread-pool timeout returns control while the C++ keeps
    eating cores). Only a separate OS process can be SIGKILL'd to actually stop at the cap.
  * Shared-machine safety (C4415): this box is shared with Elder/Ember. A "timeout" that leaves
    the computation running IS the saturation failure mode. Killable child = abort discipline made
    real. `preflight_cpu()` is the pre-launch half; the SIGKILL cap is the abort half.
  * Peak memory: tracemalloc misses Aer's C++ allocations. Per-child `ru_maxrss` via os.wait4 is
    exact and un-contaminated by prior rows.
  * CPU accounting: per-child user+sys via os.wait4 rusage — no cross-row contamination.
=> DECISION: each solve runs in a forked child, reaped with os.wait4 (real rusage), killable with
   SIGKILL (real censoring). Solver-agnostic by construction (works for non-Aer G1 adversaries too).

CORRECTNESS GATE (the crown jewel): a row schema REQUIRES `verified`. The card builder (Phase 5)
must STRUCTURALLY refuse to place an unverified row on a cost curve — segregate, never drop (a fast
wrong solver poisons the map; the Exp144 detector lesson applied classically). For MPS the gate is
coupled to the cost axis: a too-small bond dimension chi returns the WRONG answer, so "verified" =
"returned the planted answer AT THIS chi", and the minimum chi that verifies IS the cost signal.
Verification is therefore per-(instance, chi) for MPS — never "verify small, trust large".

ENERGY HONESTY (gap G2): RAPL `energy_uj` is root-only since the CVE-2020-8694 side-channel patch
and is not chmod-fixable, so on most machines energy is unmeasurable by us. We emit
`energy_j: null, energy_method: "rapl_permission_denied"` rather than a fabricated estimate. A
TDP x busy-time number is produced ONLY when a TDP is explicitly supplied, and is labeled
`energy_bound_not_measured` (an upper bound, not a measurement). `intel-rapl` is the powercap
FRAMEWORK name, not the vendor — the fingerprint stamps the real vendor so no one misreads it.

THREADS: "CPU-seconds" is meaningless without the thread config. Every row records its declared
thread config; meter single-thread AND all-core; the Item-4 race config is declared here in advance.

Substrate: claude-fable-5, Whisper C4971. Freeze discipline mirrors tools/attenuation_map.py.
"""
import os, sys, json, time, signal, resource, platform, re, argparse

QROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
RAPL_BASE = "/sys/class/powercap/intel-rapl/intel-rapl:0"

# The Item-4 race config, DECLARED IN ADVANCE (plan §A phase 4, so it is not chosen post-hoc to
# favor either arm). All-core on the metering box, performance governor, single named solver run.
RACE_CONFIG = {"threads": os.cpu_count(), "governor_required": "performance",
               "note": "all-core; declared C4971 before any race; see plan Item 4"}


# ---------------------------------------------------------------------------- fingerprint / energy
def _cpu_vendor_model():
    model = "unknown"
    try:
        with open("/proc/cpuinfo") as f:
            for line in f:
                if line.startswith("model name"):
                    model = line.split(":", 1)[1].strip()
                    break
    except OSError:
        model = platform.processor() or "unknown"
    vendor = "unknown"
    m = model.lower()
    if "amd" in m:
        vendor = "AMD"
    elif "intel" in m:
        vendor = "Intel"
    return vendor, model


def hardware_fingerprint():
    """Stamped into every row so a number is never orphaned from the machine that produced it."""
    vendor, model = _cpu_vendor_model()
    mem_kb = None
    try:
        with open("/proc/meminfo") as f:
            for line in f:
                if line.startswith("MemTotal"):
                    mem_kb = int(line.split()[1]); break
    except OSError:
        pass
    gov = None
    try:
        with open("/sys/devices/system/cpu/cpu0/cpufreq/scaling_governor") as f:
            gov = f.read().strip()
    except OSError:
        pass
    return {
        "cpu_vendor": vendor,            # AMD here — NOT the powercap "intel-rapl" framework name
        "cpu_model": model,
        "logical_cores": os.cpu_count(),
        "ram_gb": round(mem_kb / 1024 / 1024, 1) if mem_kb else None,
        "governor": gov,
        "platform": platform.platform(),
        "python": platform.python_version(),
    }


def _rapl_read_uj():
    """Return (energy_uj, max_range_uj) or (None, None) if unreadable."""
    try:
        with open(os.path.join(RAPL_BASE, "energy_uj")) as f:
            e = int(f.read().strip())
        try:
            with open(os.path.join(RAPL_BASE, "max_energy_range_uj")) as f:
                mx = int(f.read().strip())
        except OSError:
            mx = None
        return e, mx
    except OSError:
        return None, None


def _energy_delta_j(e0, e1, mx):
    """RAPL is a wrapping counter; correct one wrap using max_energy_range_uj."""
    if e0 is None or e1 is None:
        return None
    d = e1 - e0
    if d < 0 and mx:
        d += mx
    return d / 1e6  # uJ -> J


# ------------------------------------------------------------------------------- shared-machine check
def preflight_cpu(threshold_per_core=0.75):
    """C4415 pre-launch half: report whether the SHARED box has CPU headroom for a sweep.

    Returns a dict; the sweep driver (Phase 4) decides go/no-go. Not a hard block here — a single
    metered row is cheap — but the number must be visible before a multi-row sweep is launched.
    """
    load1, load5, load15 = os.getloadavg()
    cores = os.cpu_count()
    per_core = load1 / cores if cores else load1
    return {"loadavg_1m": round(load1, 2), "loadavg_5m": round(load5, 2),
            "cores": cores, "load_per_core": round(per_core, 3),
            "headroom_ok": per_core < threshold_per_core,
            "threshold_per_core": threshold_per_core}


# --------------------------------------------------------------------------------------- the meter
def meter(worker, *, timeout_s, thread_config, tdp_watts=None, label=""):
    """Meter one unit of classical work in a forked child.

    worker: a zero-arg callable, executed in the CHILD. It MUST return a JSON-serializable dict
            containing at least {"verified": bool}. Any solver-specific fields (answer, chi, method,
            n, t_count, ...) are passed through into the row untouched. The worker owns correctness
            verification (statevector: exact amplitudes; MPS: planted answer at this chi).
    timeout_s: wall cap; on breach the child is SIGKILL'd and the row is censored (cost `>cap`).
    thread_config: dict recorded verbatim into the row (e.g. {"threads": 1} or RACE_CONFIG). The
            WORKER is responsible for honoring it (Aer via max_parallel_threads); the meter records.
    tdp_watts: if given, and RAPL is unreadable, emit a labeled TDP x busy-time UPPER BOUND. Never
            fabricated when None.
    """
    fp = hardware_fingerprint()
    r_read, r_write = os.pipe()
    e0, mx = _rapl_read_uj()
    t0 = time.perf_counter()
    pid = os.fork()

    if pid == 0:  # ---- child ----
        os.close(r_read)
        try:
            result = worker()
            if not isinstance(result, dict) or "verified" not in result:
                result = {"verified": False, "error": "worker did not return {'verified': ...}"}
            payload = json.dumps(result).encode()
        except Exception as exc:  # a crashing solver is an unverified row, not a harness crash
            payload = json.dumps({"verified": False, "error": f"{type(exc).__name__}: {exc}"}).encode()
        try:
            os.write(r_write, payload)
        finally:
            os.close(r_write)
            os._exit(0)

    # ---- parent ----
    os.close(r_write)
    killed = False
    status = None
    rusage = None
    poll = 0.02
    while True:
        wpid, wstatus, wru = os.wait4(pid, os.WNOHANG)
        if wpid == pid:
            status, rusage = wstatus, wru
            break
        if time.perf_counter() - t0 > timeout_s:
            try:
                os.kill(pid, signal.SIGKILL)
            except ProcessLookupError:
                pass
            wpid, status, rusage = os.wait4(pid, 0)  # reap for real rusage even when killed
            killed = True
            break
        time.sleep(poll)
    wall_s = time.perf_counter() - t0
    e1, _ = _rapl_read_uj()

    # read the child's result (empty if it was killed mid-work)
    raw = b""
    try:
        while True:
            chunk = os.read(r_read, 65536)
            if not chunk:
                break
            raw += chunk
    finally:
        os.close(r_read)
    try:
        child_result = json.loads(raw.decode()) if raw else {}
    except json.JSONDecodeError:
        child_result = {"verified": False, "error": "unparseable child payload"}

    cpu_user = rusage.ru_utime if rusage else None
    cpu_sys = rusage.ru_stime if rusage else None
    cpu_s = (cpu_user + cpu_sys) if rusage else None
    peak_rss_mb = round(rusage.ru_maxrss / 1024, 1) if rusage else None  # ru_maxrss is KB on Linux

    # energy: measured RAPL delta, else null+label, else an explicitly-labeled TDP upper bound
    energy_j = _energy_delta_j(e0, e1, mx)
    if energy_j is not None:
        energy_method = "rapl_measured"
    elif tdp_watts is not None:
        energy_j = round(tdp_watts * wall_s, 2)
        energy_method = "energy_bound_not_measured"  # TDP x busy-time UPPER BOUND (gap G2)
    else:
        energy_method = "rapl_permission_denied"

    # censored vs verified vs failed
    if killed:
        verified, censored = False, True
    else:
        verified, censored = bool(child_result.get("verified", False)), False

    row = {
        "label": label,
        "verified": verified,            # card builder REFUSES to curve a row with verified=False
        "censored": censored,            # timeout: record `>cap`, never drop (plan §A phase 4)
        "wall_s": round(wall_s, 4),
        "cpu_s": round(cpu_s, 4) if cpu_s is not None else None,
        "cpu_user_s": round(cpu_user, 4) if cpu_user is not None else None,
        "cpu_sys_s": round(cpu_sys, 4) if cpu_sys is not None else None,
        "peak_rss_mb": peak_rss_mb,
        "energy_j": energy_j,
        "energy_method": energy_method,
        "timeout_s": timeout_s,
        "thread_config": thread_config,
        "solver": child_result.get("solver"),
        "hardware": fp,
        "solver_fields": {k: v for k, v in child_result.items()
                          if k not in ("verified", "solver")},
    }
    return row


# ------------------------------------------------------------------------------------- self-test
# Exercises meter + gate end-to-end on a tiny KNOWN-ANSWER Clifford instance (a GHZ chain). NOT the
# Item-3 hidden-shift generator (that shares a freeze with Item 3 and gets its own file). The test
# deliberately includes a POISONED solver and a TIMEOUT worker so all three row states are SEEN:
# verified (eligible), unverified (segregated), censored (>cap). Guards seen to fail = rule 4 / G9.

def _ghz_expected(n):
    """The only two bitstrings a correct GHZ_n simulation may put weight on."""
    return {"0" * n, "1" * n}


def _make_ghz_worker(n, method, chi=None, poison=False):
    def worker():
        from qiskit import QuantumCircuit, transpile
        from qiskit_aer import AerSimulator
        qc = QuantumCircuit(n)
        qc.h(0)
        for i in range(n - 1):
            qc.cx(i, i + 1)
        qc.measure_all()
        opts = {"method": method, "max_parallel_threads": 1}
        if method == "matrix_product_state" and chi is not None:
            # cap bond dimension so a too-small chi is SEEN to fail verification (MPS gate coupling)
            opts["matrix_product_state_max_bond_dimension"] = chi
        sim = AerSimulator(**opts)
        tqc = transpile(qc, sim)
        counts = sim.run(tqc, shots=2048, seed_simulator=7).result().get_counts()
        support = {k.replace(" ", "") for k in counts}
        if poison:  # a wrong solver: claim verified while returning a bogus answer
            return {"solver": f"{method}(POISONED)", "verified": True,
                    "support": ["deadbeef"], "n": n}
        verified = support.issubset(_ghz_expected(n)) and support == _ghz_expected(n)
        return {"solver": method + (f"(chi={chi})" if chi else ""), "verified": verified,
                "support": sorted(support), "n": n, "chi": chi}
    return worker


def _timeout_worker():
    def worker():
        import time as _t
        _t.sleep(60)  # far past the test's 2s cap -> must be SIGKILL'd and censored
        return {"verified": True}
    return worker


def _self_test():
    print("=" * 78)
    print("classical_cost_meter self-test  (meter + correctness gate, guards seen to fail)")
    print("=" * 78)
    fp = hardware_fingerprint()
    print(f"machine: {fp['cpu_vendor']} {fp['cpu_model']}  {fp['logical_cores']}c "
          f"{fp['ram_gb']}GB gov={fp['governor']}")
    pf = preflight_cpu()
    print(f"preflight: load/core={pf['load_per_core']} headroom_ok={pf['headroom_ok']}\n")

    tc = {"threads": 1}
    checks = []

    # 1. correct statevector -> verified True
    r = meter(_make_ghz_worker(6, "statevector"), timeout_s=30, thread_config=tc, label="sv_ghz6")
    ok = r["verified"] and not r["censored"]
    checks.append(("statevector correct -> verified", ok))
    print(f"[{'PASS' if ok else 'FAIL'}] sv_ghz6: verified={r['verified']} "
          f"wall={r['wall_s']}s cpu={r['cpu_s']}s rss={r['peak_rss_mb']}MB "
          f"energy={r['energy_j']}({r['energy_method']})")

    # 2. extended_stabilizer correct -> verified True (Clifford is exact here)
    r = meter(_make_ghz_worker(6, "extended_stabilizer"), timeout_s=30, thread_config=tc,
              label="extstab_ghz6")
    ok = r["verified"] and not r["censored"]
    checks.append(("extended_stabilizer correct -> verified", ok))
    print(f"[{'PASS' if ok else 'FAIL'}] extstab_ghz6: verified={r['verified']} wall={r['wall_s']}s")

    # 3. MPS at sufficient chi (GHZ needs chi>=2) -> verified True; the chi rides in the row
    r = meter(_make_ghz_worker(6, "matrix_product_state", chi=8), timeout_s=30, thread_config=tc,
              label="mps_ghz6_chi8")
    ok = r["verified"] and r["solver_fields"].get("chi") == 8
    checks.append(("mps sufficient chi -> verified (chi recorded)", ok))
    print(f"[{'PASS' if ok else 'FAIL'}] mps_ghz6_chi8: verified={r['verified']} "
          f"chi={r['solver_fields'].get('chi')}")

    # 4. POISONED solver -> gate must catch it (unverified despite claiming verified? No: the worker
    #    claims verified=True with a bogus answer; the GATE is the card builder refusing bad rows.
    #    Here we prove the row PRESERVES the bogus answer so downstream refusal is possible, and that
    #    an HONEST verifier would reject it — we assert support != expected.)
    r = meter(_make_ghz_worker(6, "statevector", poison=True), timeout_s=30, thread_config=tc,
              label="poisoned")
    bogus = r["solver_fields"].get("support") == ["deadbeef"]
    # the poisoned worker lies (verified=True) — this documents WHY verification must be computed by
    # the worker from ground truth, and WHY a second seat replicates (roles: Ember replicates rows).
    checks.append(("poisoned answer preserved in row for audit", bogus))
    print(f"[{'PASS' if bogus else 'FAIL'}] poisoned: worker-claimed verified={r['verified']} "
          f"support={r['solver_fields'].get('support')}  <- lie is visible for 2nd-seat catch")

    # 5b. MPS gate-cost coupling SEEN: too-small chi truncates GHZ to a WRONG answer (verified=
    #     False), and the minimum chi that verifies IS the cost signal. Proves the gate and the cost
    #     axis are the same measurement for MPS (the "verify small, trust large" shortcut is invalid).
    min_verified_chi = None
    chi_row = {}
    for chi in (1, 2, 8):
        rr = meter(_make_ghz_worker(8, "matrix_product_state", chi=chi), timeout_s=30,
                   thread_config=tc, label=f"mps_chi{chi}")
        chi_row[chi] = rr["verified"]
        if rr["verified"] and min_verified_chi is None:
            min_verified_chi = chi
    ok = (chi_row.get(1) is False) and (chi_row.get(2) is True) and min_verified_chi == 2
    checks.append(("mps min-verifying chi is the cost signal (chi=1 fails, chi=2 passes)", ok))
    print(f"[{'PASS' if ok else 'FAIL'}] mps chi-gate: verified-by-chi={chi_row} "
          f"-> min verifying chi={min_verified_chi} (= the GHZ_8 cost signal)")

    # 5. timeout -> SIGKILL'd and censored (the abort discipline, SEEN to fire)
    t = time.perf_counter()
    r = meter(_timeout_worker(), timeout_s=2, thread_config=tc, label="timeout")
    elapsed = time.perf_counter() - t
    ok = r["censored"] and not r["verified"] and elapsed < 10  # killed near cap, not after 60s
    checks.append(("timeout -> censored + killed near cap", ok))
    print(f"[{'PASS' if ok else 'FAIL'}] timeout: censored={r['censored']} "
          f"killed after {elapsed:.1f}s (cap 2s, worker sleeps 60s)")

    print("\n" + "-" * 78)
    npass = sum(1 for _, ok in checks if ok)
    for name, ok in checks:
        print(f"  {'PASS' if ok else 'FAIL'}  {name}")
    print(f"{npass}/{len(checks)} checks passed")
    print("-" * 78)
    return 0 if npass == len(checks) else 1


if __name__ == "__main__":
    ap = argparse.ArgumentParser(description="P-CCM Phase 1 classical cost meter")
    ap.add_argument("--selftest", action="store_true", help="run meter + gate self-test")
    ap.add_argument("--fingerprint", action="store_true", help="print hardware fingerprint JSON")
    args = ap.parse_args()
    if args.fingerprint:
        print(json.dumps({"hardware": hardware_fingerprint(), "preflight": preflight_cpu(),
                          "race_config": RACE_CONFIG}, indent=2))
        sys.exit(0)
    sys.exit(_self_test())
