#!/usr/bin/env python3
"""Door (b) COST PILOT — measure the billing rate in the many-rows-few-shots regime.

Ruled by Elder (general#7436) after I flagged that F-IND forces randomisation granularity
R=1, so the real flight is 6,388 rows x 1 shot — the corner where our cost model has never
been validated and where exp142 missed by 4.3x tonight (32,805 rows x 43 shots -> 126s
against a 29s model, which exhausted a paid tank and produced nothing).

This is the door (a) ANCHOR PATTERN APPLIED TO COST: measure in the regime you are about to
fly in, then size from the measurement instead of from an extrapolation.

** USES A PUBLIC P. THE SEAL IS NOT TOUCHED AND NOT CONSUMED. ** A cost measurement has no
business spending a commitment; the circuit SHAPE is what bills, and shape does not depend on
which Pauli was drawn (that is form (a)'s whole point — the secret rides in bound 1q
parameters and the structure is identical for every P).
"""
import argparse, datetime, json, math, os, re, sys
import numpy as np

ALT3_CRN = ("crn:v1:bluemix:public:quantum-computing:us-east:"
            "a/b290f963c84c4e34a5aa7704b4e39b66:952e28e1-bdbf-4593-aec7-e1520b4218a8::")
EXPECTED_BACKEND = "ibm_marrakesh"
RESERVE_S = 20            # generous: this is a measurement, not the science

EIGGATE = {("Z", +1): [], ("Z", -1): [("x",)],
           ("X", +1): [("h",)], ("X", -1): [("x",), ("h",)],
           ("Y", +1): [("h",), ("s",)], ("Y", -1): [("x",), ("h",), ("s",)],
           ("I", +1): [], ("I", -1): []}


def alt3_token():
    with open("/droid/repos/DC15W/.env") as f:
        for line in f:
            m = re.match(r"^IBMQ_ALT3=(.+)$", line.strip())
            if m:
                return m.group(1).strip().strip('"').strip("'")
    sys.exit("REFUSE: IBMQ_ALT3 not found")


def build_template(n):
    """Uniform template: one parameterised 1q layer per copy + the Bell layer.
    Structure identical for every P and every draw — form (a) maximal."""
    from qiskit import QuantumCircuit
    from qiskit.circuit import ParameterVector
    th = ParameterVector("t", 3 * 2 * n)      # u(theta,phi,lam) per qubit, 2n qubits
    qc = QuantumCircuit(2 * n, 2 * n)
    for q in range(2 * n):
        qc.u(th[3 * q], th[3 * q + 1], th[3 * q + 2], q)
    for i in range(n):
        qc.cx(i, n + i)
        qc.h(i)
    for i in range(n):
        qc.measure(i, i)                       # a-register: first n bits
        qc.measure(n + i, n + i)               # b-register: last n bits  (HALVES, registered)
    return qc, th


def u_params(pauli_char, s):
    """Euler angles taking |0> to the (pauli_char, s) eigenstate."""
    if pauli_char == "Z" or pauli_char == "I":
        return (0.0, 0.0, 0.0) if s > 0 else (math.pi, 0.0, 0.0)
    if pauli_char == "X":
        return (math.pi / 2, 0.0, math.pi) if s > 0 else (math.pi / 2, math.pi, 0.0)
    if pauli_char == "Y":
        return (math.pi / 2, math.pi / 2, math.pi) if s > 0 else (math.pi / 2, -math.pi / 2, 0.0)
    raise ValueError(pauli_char)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--n", type=int, default=16)
    ap.add_argument("--rows", type=int, default=200)
    ap.add_argument("--eps", type=float, default=0.3)
    ap.add_argument("--fly", action="store_true")
    a = ap.parse_args()

    from qiskit import transpile
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2

    n, alpha = a.n, 3 * a.eps
    P_public = "XYZ" * (n // 3) + "XYZ"[: n % 3]      # PUBLIC, declared, not the seal
    print(f"DOOR (b) COST PILOT — n={n}, rows={a.rows} x 1 shot, PUBLIC P={P_public}")
    print("  the seal is NOT touched: shape bills, and shape is P-independent under form (a)")

    svc = QiskitRuntimeService(channel="ibm_quantum_platform", token=alt3_token(),
                               instance=ALT3_CRN)
    u = svc.usage()
    if u["instance_id"] != ALT3_CRN or u["usage_limit_reached"]:
        sys.exit(f"REFUSE G-CRN: {u['instance_id'][-24:]} flagged={u['usage_limit_reached']}")
    print(f"  [PASS] G-CRN     ...{u['instance_id'][-24:]}  remaining "
          f"{u['usage_remaining_seconds']}s  flagged=False")

    bk = svc.backend(EXPECTED_BACKEND)
    if bk.name != EXPECTED_BACKEND:
        sys.exit(f"REFUSE G-BACKEND: {bk.name}")
    print(f"  [PASS] G-BACKEND {bk.name}")
    if u["usage_remaining_seconds"] <= RESERVE_S:
        sys.exit("REFUSE G-FIT: below reserve")
    print(f"  [PASS] G-FIT     {u['usage_remaining_seconds']}s > {RESERVE_S}s reserve")

    qc, th = build_template(n)
    t = transpile(qc, backend=bk, optimization_level=1)
    print(f"  template: {t.num_parameters} free params, ISA 2q={t.count_ops().get('cz',0)}")

    rng = np.random.default_rng(4262)
    free = [i for i, c in enumerate(P_public) if c != "I"]
    rows = []
    for _ in range(a.rows):
        vals = []
        for _copy in range(2):
            s = +1 if rng.random() < (1 + alpha) / 2 else -1
            si = [1] * n
            for i in free[:-1]:
                si[i] = int(rng.choice([1, -1]))
            if free:
                si[free[-1]] = s * int(np.prod([si[i] for i in free[:-1]])) if len(free) > 1 else s
            for i, c in enumerate(P_public):
                vals.extend(u_params(c, si[i]))
        rows.append(vals)
    # ---- PARAMETER ORDERING BY NAME, NEVER BY POSITION.
    # SamplerV2 coerces a bare array POSITIONALLY against circuit.parameters, which qiskit
    # sorts ALPHABETICALLY: t[0], t[1], t[10], t[11], t[2]... — NOT numeric order. An earlier
    # exp142 wave was VOIDED by exactly this (prereg: "pubs coerce those POSITIONALLY against
    # circuit.parameters (alphabetically sorted: lm,pm,pp,tm,tp), not template order"), losing
    # four flights' worth of shots. Build the row in the circuit's own parameter order by NAME.
    idx = {str(par): k for k, par in enumerate(t.parameters)}
    arr = []
    for r in rows:
        row = [0.0] * len(t.parameters)
        for k in range(len(r)):
            row[idx[f"t[{k}]"]] = r[k]
        arr.append(row)
    # can-fire check: alphabetical != numeric ordering must actually differ, or this guard is moot
    alpha_order = [str(par) for par in t.parameters]
    numeric_order = [f"t[{k}]" for k in range(len(t.parameters))]
    if alpha_order == numeric_order:
        print("  [note] alphabetical == numeric here; the reorder is a no-op at this size")
    else:
        first = next(i for i in range(len(alpha_order)) if alpha_order[i] != numeric_order[i])
        print(f"  [PASS] G-ORDER   alphabetical != numeric (first divergence at index {first}: "
              f"{alpha_order[first]} vs {numeric_order[first]}) — remapped by NAME")

    if not a.fly:
        print(f"\n  DRY — {len(rows)} rows x 1 shot prepared, nothing submitted.")
        return 0

    job = SamplerV2(mode=bk).run([(t, arr, 1)])
    print(f"\n  SUBMITTED  {job.job_id()}")
    import time
    for _ in range(40):
        if str(job.status()) in ("DONE", "ERROR", "CANCELLED"):
            break
        time.sleep(15)
    st = str(job.status())
    print(f"  status {st}")
    if st == "DONE":
        billed = job.usage()
        after = svc.usage()
        per_row = billed / a.rows
        print(f"  BILLED {billed}s for {a.rows} rows x 1 shot -> {per_row:.5f} s/row")
        print(f"  EXTRAPOLATED to the registered 6,388-row flight: {per_row*6388:.1f}s")
        print(f"  balance {after['usage_consumed_seconds']}/{after['usage_limit_seconds']} "
              f"remaining {after['usage_remaining_seconds']}s")
        json.dump({"n": n, "rows": a.rows, "shots_per_row": 1, "billed_s": billed,
                   "s_per_row": per_row, "extrapolated_6388_rows_s": per_row * 6388,
                   "job": job.job_id(), "public_P": P_public, "seal_untouched": True,
                   "utc": datetime.datetime.now(datetime.timezone.utc).isoformat()},
                  open("results/doorb_cost_pilot_ember_c4262.json", "w"), indent=1)
    return 0


if __name__ == "__main__":
    sys.exit(main())
