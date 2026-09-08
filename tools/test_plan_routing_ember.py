"""Falsify plan_routing — THE FUNCTION THE FLIGHT PATH CALLS, not a copy of it.

Ember 2026-09-08, board#415. Four branches: no threshold, the walled repeat's 0.5, a negative
control at an impossible threshold, and a backend whose properties() raises.

WHY IT EXISTS. G-EDGES was inline in the submit function, so the ONLY way to exercise it was to
fly — and a TypeError (`value >= None` when no threshold is set) therefore survived three real
flights, reported the whole time as "calibration UNREADABLE". The routing outcome was right by
accident; the stated reason was wrong, and the reason is what a reader acts on.

Needs IBM credentials and makes backend METADATA calls only. No QPU seconds, no job submission.
"""
import sys, importlib.util
spec = importlib.util.spec_from_file_location("df", "/droid/repos/quantum/tools/doorb_flight_ember_c4262.py")
df = importlib.util.module_from_spec(spec); sys.argv = ["t"]
try: spec.loader.exec_module(df)
except SystemExit: pass
from qiskit_ibm_runtime import QiskitRuntimeService
svc = QiskitRuntimeService(channel="ibm_quantum_platform", token=df.paid_token(), instance=df.PAID_CRN)
bk = svc.backend("ibm_marrakesh")

def run(thresh):
    out = []
    e, c, stamp = df.plan_routing(bk, thresh, say=out.append)
    return e, c, stamp, "\n".join(out)

print("=== [1] NO THRESHOLD (the case that printed a FALSE 'calibration UNREADABLE') ===")
e, c, stamp, said = run(None)
print(said)
assert "UNREADABLE" not in said, "STILL blames the calibration for an unset flag"
assert "BY CONFIGURATION" in said, said
assert e == [] and c is None, (e, c)
assert stamp.startswith("2026-"), f"stamp not captured with no threshold: {stamp!r}"
print(f"   -> stamp captured anyway: {stamp}")

print("\n=== [2] THRESHOLD 0.5 (the walled repeat's setting) ===")
e, c, stamp, said = run(0.5)
print(said)
assert len(e) == 6, e
assert c is not None, "coupling map not restricted"
assert stamp.startswith("2026-"), stamp

print("\n=== [3] NEGATIVE CONTROL: an impossible threshold must prune NOTHING ===")
e, c, stamp, said = run(99.0)
print(said)
assert e == [] and c is None, (e, c)
assert "no coupler at 2q error >= 99.0" in said, said

print("\n=== [4] UNREADABLE CALIBRATION still says so, and is UNKNOWN not a date ===")
class Broken:
    name = "broken"
    def properties(self): raise RuntimeError("simulated outage")
said4 = []
e, c, stamp = df.plan_routing(Broken(), 0.5, say=said4.append)
print("\n".join(said4))
print(f"   stamp: {stamp}")
assert stamp.startswith("UNKNOWN"), stamp
assert e == [] and c is None
print("\nALL ASSERTIONS PASSED")
