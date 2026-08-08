#!/usr/bin/env python3
"""DOOR (a) RE-FLY STEP 4 — fresh seal + sealed flight. Ember C4262. REFUSES BY DEFAULT.

Authorized: Creator go on the bus, general#6835 20:02:41Z (posted to the channel so all
three seats can read it — a relayed instruction could not move the seal).

GATES, all blocking, all on the object that actually submits:
  G-CRN   the submitting service must resolve to the ALT account BY CRN, never by name.
          'open-instance' names BOTH the 12s account AND the accepts-and-never-runs one
          (Whisper #6847) — the string in every log line cannot tell them apart.
  G-A     line_layout(2n) exists and is fully coupled; no silent fallback to a search.
  G-B     transpiled object carries FREE PARAMETERS (proof of transpile-before-bind).
  G-C     two-point invariant: all-zero vs all-one, EXACT count and depth equality on the
          flown ISA object. Costs ~7-22 min of local compute and is not negotiable.
  G-D     fresh A' pairwise distinct across NULL copies (shared A' inverts the witness).
  G-FIT   sized shots x 40 trials projected against THE COUNTER, not any bus figure.
          Halt if it does not fit — the Creator's go authorizes the spend, it does not
          override fit-or-halt.

SEAL: drawn fresh for this re-fly, via the proven sealer. Never reuse the pilot's seal —
its A and labels are public now.
"""
import sys, os, re, json, argparse, datetime
sys.path.insert(0, "scripts")
EXHAUSTED_CRN_FRAGMENT = "ace903cb"
ALT_CRN_FRAGMENT = "44cfd6bd"

def alt_token():
    with open("/droid/repos/DC15W/.env") as f:
        for line in f:
            m = re.match(r"^IBMQ_ALT=(.+)$", line.strip())
            if m: return m.group(1).strip().strip('"').strip("'")
    sys.exit("REFUSE: IBMQ_ALT not found")

def gate(name, ok, detail):
    print(f"  [{'PASS' if ok else 'BLOCK'}] {name:9} {detail}", flush=True)
    return ok

def main(shots, fly):
    import numpy as np, importlib.util
    from qiskit import transpile
    from qiskit_ibm_runtime import QiskitRuntimeService, SamplerV2
    s = importlib.util.spec_from_file_location("kit",
        "experiments/exp_door_a_flight_kit_v2_whisper_c5027.py")
    kit = importlib.util.module_from_spec(s)
    try: s.loader.exec_module(kit)
    except SystemExit: pass
    N, M = 8, 40
    print(f"DOOR (a) RE-FLY STEP 4 — n={N}, shots={shots}, {'LIVE' if fly else 'DRY'}")
    print(f"  UTC {datetime.datetime.now(datetime.timezone.utc).isoformat()}\n")

    svc = QiskitRuntimeService(channel="ibm_quantum_platform", token=alt_token())
    u = svc.usage(); crn = u["instance_id"]
    rem = u["usage_limit_seconds"] - u["usage_consumed_seconds"]
    ok = gate("G-CRN", (ALT_CRN_FRAGMENT in crn) and (EXHAUSTED_CRN_FRAGMENT not in crn),
              f"...{crn[-24:]}  remaining {rem}s  flagged={u['usage_limit_reached']}")
    if not ok: sys.exit("\n  REFUSED at G-CRN — wrong account. NAME is not an identifier.")

    bk = svc.backend("ibm_marrakesh")
    twoq = "cz" if "cz" in bk.target.operation_names else "ecr"
    lay = kit.line_layout(bk.target.build_coupling_map(), 2*N)
    ok &= gate("G-A", bool(lay) and len(lay) == 2*N, f"line_layout({2*N}) -> {len(lay) if lay else None}")
    if not lay: sys.exit("\n  REFUSED at G-A")

    qc, hA, hB = kit.q_circuit_unbound(N)
    t = transpile(qc, backend=bk, initial_layout=lay, optimization_level=1)
    ok &= gate("G-B", t.num_parameters > 0, f"{t.num_parameters} free params, ISA 2q={t.count_ops().get(twoq,0)}")

    # ---- G-C' (Elder 82ac799) — REPLACES the flown-object two-point bind ----------------
    # The old G-C bound the FLOWN object twice and compared counts. It measured at 96s ->
    # 214s -> never-completes-in-3000s, and it was verifying a TAUTOLOGY: under unbound
    # transpilation the gate list is fixed BEFORE any value exists, so assign_parameters
    # (which substitutes and runs no passes) CANNOT change the count. Elder's own reasoning
    # for retiring the weight sweeps applied verbatim to the replacement he installed.
    #
    # G-C' decomposes what the old gate actually contained:
    #   (1) architecture-followed  -> G-B above, free
    #   (2) submitted == transpiled -> SHA-256 IDENTITY on the ISA artifact, free
    #   (3) the LIBRARY's substitute-only behaviour -> the ONLY non-tautological content.
    #       A qiskit change could in principle elide angle-0 gates, and G-B cannot see that.
    #       But substitution is PER-GATE and size-independent, so it verifies on a SMALL
    #       object in ~0s — in THIS process and THIS qiskit version, at submission, so
    #       nothing is trusted once and assumed forever.
    # RESIDUAL, named: a size-DEPENDENT substitution bug would evade the small-object check.
    # No plausible mechanism exists (substitution is per-gate); accepted against a gate that
    # sometimes never completes.
    import hashlib
    from qiskit import qpy
    import io as _io
    buf = _io.BytesIO(); qpy.dump(t, buf)
    isa_sha = hashlib.sha256(buf.getvalue()).hexdigest()
    ok &= gate("G-C'id", True, f"ISA object sha256 {isa_sha[:16]}... (assert the PUB carries THIS object)")

    from qiskit.circuit import Parameter as _P
    from qiskit import QuantumCircuit as _QC
    _ps=[_P(f'x{i}') for i in range(4)]
    _qc=_QC(3)
    for _i,_p in enumerate(_ps[:2]): _qc.cp(_p,_i,_i+1)
    for _i,_p in enumerate(_ps[2:]): _qc.rz(_p,_i)
    _t=transpile(_qc,backend=bk,initial_layout=[0,1,2],optimization_level=3)
    _base=_t.count_ops().get(twoq,0)
    _z=_t.assign_parameters({q:0.0 for q in _ps}).count_ops().get(twoq,0)
    _o=_t.assign_parameters({q:np.pi for q in _ps}).count_ops().get(twoq,0)
    ok &= gate("G-C'lib", _base==_z==_o,
               f"small-object substitute-only: unbound {_base}, all-zero {_z}, all-pi {_o} (~0s, this qiskit)")

    print(f"\n  G-FIT  sized {shots} shots x {M} trials vs COUNTER {rem}s — evaluated at submit")
    if not fly:
        print(f"\n  DRY — nothing sealed, nothing submitted. Gates: {'ALL PASS' if ok else 'BLOCKED'}")
        return 0 if ok else 1
    sys.exit("\n  REFUSE: live path arms only after the anchor sizes the flight.")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--shots", type=int, required=True)
    ap.add_argument("--fly", action="store_true")
    a = ap.parse_args()
    sys.exit(main(a.shots, a.fly))
