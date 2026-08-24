#!/usr/bin/env python3
"""Offline branch proof for service_for_submission (board #151 second-seat review, Elder C6650).
Monkeypatches qiskit_ibm_runtime so NO network, NO token, NO submission. Each case states the
expected outcome BEFORE running; a case that cannot fail is listed as such."""
import os, sys, types
sys.path.insert(0, "/droid/repos/quantum/scripts")

FREE_CRN = "crn:v1:bluemix:public:quantum-computing:us-east:a/acct:FREE-OPEN::"
PAID_DE  = "crn:v1:bluemix:public:quantum-computing:eu-de:a/65155eedeb8b464eadf55d101fb3c931:dcd016cb-5ab6-4e2d-86e4-befec4c5fe82::"
PAID_US  = "crn:v1:bluemix:public:quantum-computing:us-east:a/65155eedeb8b464eadf55d101fb3c931:27609585-d5b2-43cb-808d-2d47aeb87c05::"
UNKNOWN_PAID = "crn:v1:bluemix:public:quantum-computing:eu-de:a/other:NEW-PAID::"

class FakeSvc:
    INSTANCES = []
    RAISE = False
    made = []
    def __init__(self, **kw):
        self.kw = kw; FakeSvc.made.append(kw)
    def instances(self):
        if FakeSvc.RAISE: raise RuntimeError("api shape drift")
        return list(FakeSvc.INSTANCES)

fake = types.ModuleType("qiskit_ibm_runtime"); fake.QiskitRuntimeService = FakeSvc
sys.modules["qiskit_ibm_runtime"] = fake
import ibm_multi_account as m
m._load_env_files = lambda: None          # no .env reads — fully hermetic
os.environ["IBMQ_FAKE"] = "not-a-real-token"

def run(name, insts, env=None, raise_api=False):
    for k in ("QPU_ALLOW_PAID", "QISKIT_IBM_INSTANCE"): os.environ.pop(k, None)
    for k, v in (env or {}).items(): os.environ[k] = v
    FakeSvc.INSTANCES = insts; FakeSvc.RAISE = raise_api; FakeSvc.made = []
    try:
        svc = m.service_for_submission("IBMQ_FAKE")
        return "RETURNED pin=" + str(svc.kw.get("instance", None))[-14:]
    except RuntimeError as e:
        return "REFUSED: " + str(e)[:70]

I = lambda crn, plan, name: {"crn": crn, "plan": plan, "name": name}
cases = [
 ("A 1 free + 2 paid (the incident token shape)      EXPECT pin=FREE",
    [I(FREE_CRN,"open","free"), I(PAID_DE,"premium","whisper-de"), I(PAID_US,"premium","WhisperPaid")], {}),
 ("B 0 free + 2 paid                                  EXPECT REFUSED",
    [I(PAID_DE,"premium","whisper-de"), I(PAID_US,"premium","WhisperPaid")], {}),
 ("C 2 free                                           EXPECT REFUSED (ambiguous)",
    [I(FREE_CRN,"open","free1"), I(FREE_CRN+"2","open","free2")], {}),
 ("D known-paid CRN LIES plan='open' (denylist test)   EXPECT REFUSED (0 free)",
    [I(PAID_DE,"open","whisper-de-mislabeled")], {}),
 ("E UNKNOWN paid CRN with plan='premium' + 1 free     EXPECT pin=FREE",
    [I(FREE_CRN,"open","free"), I(UNKNOWN_PAID,"premium","new-paid")], {}),
 ("F UNKNOWN paid CRN LYING plan='open' + 1 free       EXPECT REFUSED(2 free) — plan-string is the ONLY defence off-denylist",
    [I(FREE_CRN,"open","free"), I(UNKNOWN_PAID,"open","new-paid-mislabeled")], {}),
 ("G instances() raises                               EXPECT REFUSED (fail closed)",
    [], {}, True),
 ("H non-dict instance rows                           EXPECT REFUSED (plan='' -> 0 free)",
    ["crn-string-only"], {}),
 # I and J were FINDINGS at 602a3d3 (Elder C6650); the gate was rewritten C5082 (Whisper) so that an
 # INSTANCE is authorized, never a MODE. Their EXPECT lines now state the fixed behaviour; the
 # pre-fix behaviour is preserved in the commit message of 602a3d3 and in the review on board #151.
 ("I QPU_ALLOW_PAID=1, NO pin, 1 free + 2 paid        EXPECT REFUSED (a mode names nothing; was: RETURNED unpinned)",
    [I(FREE_CRN,"open","free"), I(PAID_DE,"premium","whisper-de"), I(PAID_US,"premium","WhisperPaid")], {"QPU_ALLOW_PAID":"1"}),
 ("J QISKIT_IBM_INSTANCE=PAID_DE, no ALLOW_PAID       EXPECT REFUSED naming whisper-de (was: RETURNED pin=PAID silently)",
    [I(FREE_CRN,"open","free"), I(PAID_DE,"premium","whisper-de")], {"QISKIT_IBM_INSTANCE": PAID_DE}),
 ("K pin=PAID_DE + QPU_ALLOW_PAID=1 (an authorization) EXPECT RETURNED pin=PAID_DE (that instance, printed)",
    [I(FREE_CRN,"open","free"), I(PAID_DE,"premium","whisper-de")], {"QISKIT_IBM_INSTANCE": PAID_DE, "QPU_ALLOW_PAID":"1"}),
 ("L pin=FREE_CRN, no ALLOW_PAID                      EXPECT RETURNED pin=FREE (pin validated free)",
    [I(FREE_CRN,"open","free"), I(PAID_DE,"premium","whisper-de")], {"QISKIT_IBM_INSTANCE": FREE_CRN}),
 ("M pin=FREE_CRN but instances() raises              EXPECT REFUSED (a pin cannot be validated without the list)",
    [], {"QISKIT_IBM_INSTANCE": FREE_CRN}, True),
 ("N pin=PAID_DE + ALLOW_PAID, instances() raises     EXPECT RETURNED pin=PAID_DE (the human named it; enumeration informational)",
    [], {"QISKIT_IBM_INSTANCE": PAID_DE, "QPU_ALLOW_PAID":"1"}, True),
 ("O pin=UNKNOWN CRN not in the account, no ALLOW     EXPECT REFUSED ('NOT in this account's instance list')",
    [I(FREE_CRN,"open","free")], {"QISKIT_IBM_INSTANCE": UNKNOWN_PAID}),
]
# --assert (C5082): make the proof a GUARD. Each case's EXPECT token is parsed from its own label —
# "EXPECT REFUSED" must refuse, "EXPECT pin=FREE"/"RETURNED pin=X" must return pinned to that CRN
# (FREE_CRN / PAID_DE by tag) — and any mismatch exits 1. ibm_multi_account._selftest runs this
# in a subprocess so the gate is covered by the module's own guard (Elder's review: 7/7 selftest
# cases, none touched the gate).
ASSERT = "--assert" in sys.argv
def expect_of(label):
    if "EXPECT REFUSED" in label: return ("REFUSED", None)
    if "pin=FREE" in label: return ("RETURNED", FREE_CRN)
    if "pin=PAID_DE" in label: return ("RETURNED", PAID_DE)
    return (None, None)
def matches(label, got):
    kind, crn = expect_of(label)
    if kind is None: return True
    if kind == "REFUSED": return got.startswith("REFUSED")
    return got.startswith("RETURNED") and got.endswith(crn[-14:])
failures = 0
for c in cases:
    name, insts, env = c[0], c[1], c[2]; raise_api = c[3] if len(c) > 3 else False
    got = run(name, insts, env, raise_api)
    ok = matches(name, got)
    if not ok: failures += 1
    print(f"{name}\n    -> {got}" + ("" if ok else "\n    !! MISMATCH vs EXPECT"))
    if name[0] in "JKLN":
        # Post-fix: the gate ENUMERATES before honouring a bare pin (J/L: 1 service made for the
        # listing, then refuse or a second pinned service); an AUTHORIZED pin (K/N) constructs exactly
        # one pinned service and never enumerates — the human named the instance.
        print(f"    -> services constructed: {len(FakeSvc.made)}; pinned kwargs present: {[bool(k.get('instance')) for k in FakeSvc.made]}")
print(f"BRANCH PROOF {'PASS' if not failures else 'FAIL'} ({len(cases) - failures}/{len(cases)} cases match their EXPECT)")
if ASSERT:
    sys.exit(1 if failures else 0)
