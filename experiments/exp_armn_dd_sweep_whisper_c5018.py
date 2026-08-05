#!/usr/bin/env python3
"""DD/SCHEDULING SWEEP on the channel idles (Whisper C5018, Creator "try the DD/scheduling lever").

WHY THIS AND NOT SOMETHING ELSE: the ladder (d9pr2ia42q2c73b8blcg) measured the witness loss as
IDLE-DOMINATED — 9 CZ + readout cost 0.08 of purity, while EACH of two channel idles costs
~0.12. Witness sits at u = 0.680 against the frozen u >= 0.7 gate: a 0.02 gap. Two levers
remain and both are idle levers; THIS ONE COSTS NO DRIFT SIGNAL (the other, shortening the
delay, trades away the very thing being witnessed).

The current DD is ALAP-padded X-X, chosen by inheritance rather than by test.

PRE-REGISTERED COMPARISON (frozen before submission):
  arm        sequence            note
  none       bare delay          control — DD can HURT when pulse error > the noise it cancels
  xx         X-X                 the incumbent (the 0.680 baseline)
  xy4        X-Y-X-Y             cancels dephasing AND amplitude noise to first order
  xy8        XY4 twice           more pulses: better cancellation, more pulse error
All four on the SAME shallow_2 witness (9 CZ, two channel idles), same 6 candidates, same
shots. The only variable is the pulse sequence in the idle windows.

PRE-REGISTERED DECISION RULE (before data):
  * Compare each arm's POOLED mean purity across 6 candidates against the xx incumbent.
  * An arm WINS iff pooled u >= 0.700 (the frozen gate) AND its pooled advantage over xx
    exceeds the pooled MDE. Pooled MDE at these shots ~0.013 (computed and EMITTED in the
    manifest, not assumed).
  * If NO arm reaches 0.700: report the best pooled u and the REMAINING GAP as a bound, and
    the lever is exhausted — the honest next move is the delay-length trade, priced.
  * If `none` beats `xx`: DD is COSTING purity on this hardware, which is a publishable
    negative about the incumbent and must be reported as such rather than buried.
  * No arm is chosen after the data by any criterion not written here.

This is MEASUREMENT, not a decision function — no fireability attestation needed (Elder #5001).
"""
import json, os, sys, datetime
import numpy as np
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
QROOT = os.path.join(HERE, ".."); RES = os.path.join(QROOT, "results")
sys.path.insert(0, os.path.join(QROOT, "scripts"))
from exp_armn_shallow_witness_whisper_c5018 import three_neighbour_plan, build_witness
from exp_armn_flight_compile_whisper_c5018 import CENSUS_JOB, BACKEND, ACCOUNT, CAL_SHOTS
from exp_crossblock_widesweep import build_twins, SEED, NPHYS
SHOTS = 8000
CENSUS_DECODE = os.path.join(RES, f"armn_fez_census_decode_{CENSUS_JOB}.json")


def dd_pass(backend, seq):
    from qiskit.transpiler import PassManager
    from qiskit.transpiler.passes import ALAPScheduleAnalysis, PadDynamicalDecoupling
    from qiskit.circuit.library import XGate, YGate
    d = backend.target.durations()
    # Y is not a native gate on this backend so it carries no duration. Physically Y is an X
    # with a 90-degree phase offset on the drive — SAME PULSE LENGTH — so registering
    # duration(y) = duration(x) per qubit is a statement about the hardware, not a fudge.
    # Stated here and emitted in the manifest rather than left implicit.
    try:
        upd = []
        for qq in range(NPHYS):
            try:
                upd.append(("y", qq, d.get("x", qq)))
            except Exception:
                pass
        if upd:
            d.update(upd)
    except Exception as e:
        print(f"[dd] duration registration failed: {e}")
    if seq == "none":
        return PassManager([ALAPScheduleAnalysis(d)])
    g = {"xx": [XGate(), XGate()],
         "xy4": [XGate(), YGate(), XGate(), YGate()],
         "xy8": [XGate(), YGate(), XGate(), YGate(), YGate(), XGate(), YGate(), XGate()]}[seq]
    return PassManager([ALAPScheduleAnalysis(d), PadDynamicalDecoupling(d, g)])


def main(submit=False):
    from ibm_multi_account import service_for_submission
    from qiskit_ibm_runtime import SamplerV2
    from qiskit import QuantumCircuit, transpile
    svc = service_for_submission(ACCOUNT)
    u = svc.usage(); pool = u["usage_remaining_seconds"]
    print(f"POOL ({ACCOUNT}): {pool}s")
    backend = svc.backend(BACKEND)
    cal = str(backend.properties().last_update_date)
    twins, register = build_twins(backend)
    from exp_armn_flight_compile_whisper_c5018 import pad_duration_dt
    delay_dt = pad_duration_dt(backend, twins)
    cen = json.load(open(CENSUS_DECODE)); drifters = set(cen["drifter_set"])
    cands = []
    for q in sorted(int(x) for x in cen["readout"]):
        pl = three_neighbour_plan(backend, q, drifters | {q})
        if pl: cands.append((q, pl, q in drifters))
    cands = [c for c in cands if c[2]][:3] + [c for c in cands if not c[2]][:3]
    print(f"[candidates] {[c[0] for c in cands]}")
    pubs, meta = [], []
    for st, tag in ((0, "cal0"), (1, "cal1")):
        qc = QuantumCircuit(NPHYS)
        if st: qc.x(range(NPHYS))
        qc.measure_all()
        pubs.append((transpile(qc, backend, optimization_level=0), None, CAL_SHOTS))
        meta.append({"block": tag, "shots": CAL_SHOTS})
    xinfo = {}
    for seq in ("none", "xx", "xy4", "xy8"):
        pm = dd_pass(backend, seq)
        for q, pl, isd in cands:
            sched_dur = None
            base = transpile(build_witness(backend, q, pl, delay_dt, 2, deep=False),
                             backend, optimization_level=1, seed_transpiler=SEED)
            t = pm.run(base)
            # Y is non-ISA on this target. Y = Rz(pi/2)-X-Rz(-pi/2) EXACTLY, and Rz is a
            # VIRTUAL (zero-duration) frame change on IBM hardware — so this substitution
            # preserves the DD schedule exactly while making the circuit executable.
            if any(i.operation.name == "y" for i in t.data):
                from qiskit.circuit import QuantumCircuit as _QC
                nt = _QC(*t.qregs, *t.cregs)
                for inst in t.data:
                    if inst.operation.name == "y":
                        qb = inst.qubits[0]
                        nt.rz(np.pi/2, qb); nt.x(qb); nt.rz(-np.pi/2, qb)
                    else:
                        nt.append(inst.operation, inst.qubits, inst.clbits)
                # do NOT re-run the DD pass: the padding is already in place, and re-running
                # would re-insert Y. Rz is zero-duration so the baked schedule is unchanged.
                assert not any(i.operation.name == "y" for i in nt.data), "Y survived"
                sched_dur = t.duration          # captured from the SCHEDULED circuit
                t = nt
            npulse = sum(1 for i in t.data if i.operation.name in ("x", "y"))
            dur = sched_dur if seq in ("xy4", "xy8") else t.duration
            xinfo.setdefault(seq, []).append(npulse)
            pubs.append((t, None, SHOTS))
            meta.append({"block": f"{seq}_q{q}", "seq": seq, "q": q,
                         "role": "drifter" if isd else "quiet", "shots": SHOTS,
                         "pulses": npulse, "scheduled_duration_dt": dur})
    for s, v in xinfo.items():
        print(f"[pulses] {s:>4}: {sorted(set(v))} per circuit")
    p_ref = 0.16
    se_u = 2*np.sqrt(p_ref*(1-p_ref)/SHOTS)
    mde1 = 2.8*np.sqrt(2)*se_u; mde6 = mde1/np.sqrt(len(cands))
    shots_total = sum(m["shots"] for m in meta)
    print(f"[power] se(u)~{se_u:.4f} MDE single ~{mde1:.4f} pooled({len(cands)}) ~{mde6:.4f}"
          f"  | gap to gate 0.020")
    print(f"[cost] {len(pubs)} pubs / {shots_total} shots ~ {shots_total/100000*35:.0f} QPU-s"
          f" (pool {pool}s)")
    man = {"card": "armn_dd_sweep", "cycle": "C5018", "substrate": "claude-fable-5",
           "backend": BACKEND, "account": ACCOUNT, "cal_epoch_at_build": cal,
           "basis": "ladder d9pr2ia42q2c73b8blcg: idle-dominated, witness u=0.680 vs 0.700 gate",
           "arms": ["none", "xx (incumbent)", "xy4", "xy8"], "pulses_per_circuit": xinfo,
           "candidates": [c[0] for c in cands], "delay_dt": delay_dt,
           "y_duration_note": ("Y is non-native on this backend; duration(y) registered = "
                               "duration(x) per qubit, physically justified (same drive pulse "
                               "length, 90-degree phase offset). Emitted, not implicit."),
           "power": {"se_u": round(se_u, 5), "mde_single": round(mde1, 4),
                     "mde_pooled": round(mde6, 4), "gap_to_gate": 0.020,
                     "note": "pooled MDE < gap, so the comparison can resolve a gate-clearing move"},
           "decision_rule": ("arm WINS iff pooled u >= 0.700 AND advantage over xx > pooled MDE; "
                             "if none reaches 0.700 report best pooled u and the remaining gap as "
                             "a BOUND and the lever is exhausted; if `none` beats `xx`, DD is "
                             "COSTING purity and that negative is reported, not buried; no arm "
                             "chosen by any criterion not written here"),
           "cost": {"pubs": len(pubs), "shots": shots_total,
                    "projected_qpu_s": round(shots_total/100000*35)},
           "pubs_meta": meta}
    if submit:
        job = SamplerV2(mode=backend).run(pubs)
        man["job_id"] = job.job_id()
        man["submit_iso"] = datetime.datetime.now(datetime.UTC).isoformat()
        p = os.path.join(RES, f"armn_dd_manifest_{job.job_id()}.json")
        json.dump(man, open(p, "w"), indent=1); print(f"SUBMITTED {job.job_id()} -> {p}")
    else:
        p = os.path.join(RES, "armn_dd_build_c5018.json")
        json.dump(man, open(p, "w"), indent=1); print(f"[build] $0 -> {p}")


if __name__ == "__main__":
    main(submit="--submit" in sys.argv)
