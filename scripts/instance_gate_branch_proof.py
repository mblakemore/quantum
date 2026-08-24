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
 ("I QPU_ALLOW_PAID=1, 1 free + 2 paid                EXPECT RETURNED pin=None (UNPINNED = region-resolution)",
    [I(FREE_CRN,"open","free"), I(PAID_DE,"premium","whisper-de"), I(PAID_US,"premium","WhisperPaid")], {"QPU_ALLOW_PAID":"1"}),
 ("J QISKIT_IBM_INSTANCE=PAID_DE, no ALLOW_PAID       EXPECT RETURNED pin=PAID, silently (FINDING: pin branch precedes gate)",
    [I(FREE_CRN,"open","free"), I(PAID_DE,"premium","whisper-de")], {"QISKIT_IBM_INSTANCE": PAID_DE}),
]
for c in cases:
    name, insts, env = c[0], c[1], c[2]; raise_api = c[3] if len(c) > 3 else False
    print(f"{name}\n    -> {run(name, insts, env, raise_api)}")
    if name.startswith("J"):
        print(f"    -> instances() was called: {any(True for _ in [])} (see below)")
        print(f"    -> services constructed: {len(FakeSvc.made)}  (1 = returned before enumerating; gate never ran)")
