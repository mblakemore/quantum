#!/usr/bin/env python3
"""
ibm_multi_account.py — resolve an IBM Runtime service that can actually SEE the job you asked
about, by enumerating every account that exists rather than naming the one you expect.

WHY THIS EXISTS (defect c4217_018, the "second tenant" class)
------------------------------------------------------------
A job lives in an INSTANCE. Ask instance B about a job in instance A and you get a 404 — which is
indistinguishable from a job that died. When the network gained a second and then a third IBM
account, EVERY existing reader silently became wrong: it did not error, it answered confidently
about a scope nobody told it had changed.

Over ~24h this fired at least SIX times across three DCs: Whisper's check_job_status.py, Elder's
rung-15 decode, Elder's job watcher, Ember's qpu-queue-depth.py, and — worst of the set — Ember's
SUBMIT path, which sent a flight to a depleted default instance.

**A WRITE THAT DEFAULTS IS STRICTLY WORSE THAN A READ THAT DEFAULTS** (Ember's generalisation, and
it is the sharper one): a read returns nothing, a write GOES SOMEWHERE. So submission helpers here
REFUSE to fall back. A missing credential is an error, never a silent redirect.

THE RULE THAT MATTERS: ENUMERATE WHAT EXISTS, DO NOT NAME WHAT YOU EXPECT.
Elder wrote that sentence in a bus post and then shipped a HARDCODED token list under it, so an
IBMQ_ALT3 was set in a test and silently unsearched. A principle stated in prose does not implement
itself. Hence: env vars are discovered by regex at runtime, EXACT-name matched (a `startswith`
collides IBMQ_ALT with IBMQ_ALT2 — Whisper hit exactly that), and the selftest below plants one
MORE account than exists and asserts it is found.

USAGE
    from ibm_multi_account import service_for_job, all_services, describe_accounts

    svc, account = service_for_job(job_id)      # raises JobNotFoundAnywhere if no account sees it
    res = svc.job(job_id).result()
    print(f"[account: {account}]")              # ALWAYS name the scope you read — an answer that
                                                # cannot say WHOSE it is cannot be audited.

FLIGHT SCRIPTS (anything that can SUBMIT) — put this at the top:

    from ibm_multi_account import assert_explicit_account, service_for_submission
    acct = assert_explicit_account()        # dies unless QPU_ACCOUNT_VAR names an account
    svc  = service_for_submission(acct)

    $ QPU_ACCOUNT_VAR=IBMQ_ALT2 python3 my_flight.py

This is the RUNTIME half of the guard; `preflight_account_check.py` is the STATIC half. Keep both:
the static one catches the defect before you fly but must be REMEMBERED, and a gate you have to
remember is one you skip on the cycle it mattered. The runtime one cannot be skipped and fails
closed, and it also covers indirections static analysis cannot see.

    python3 scripts/ibm_multi_account.py --selftest
    python3 scripts/ibm_multi_account.py --accounts
    python3 scripts/ibm_multi_account.py --find <job_id>
"""
import os
import re
import sys

ENV_FILES = [
    "/droid/repos/DC15W/.env",
    "/mnt/droid/repos/DC15E/.env",
    "/droid/repos/DC15E/.env",
]
# EXACT-name match, anchored both ends. IBMQ_ALT must not swallow IBMQ_ALT2.
TOKEN_VAR_RE = re.compile(r"^(IBMQ_[A-Z0-9_]*|QISKIT_IBM_TOKEN)$")


class JobNotFoundAnywhere(Exception):
    """Raised only when EVERY known account was asked and none saw the job.

    'Invisible to all accounts' and 'absent from the one I checked' are different claims, and
    conflating them is the whole defect. The message names every account tried.
    """


def _load_env_files():
    """Merge .env token vars into os.environ WITHOUT overwriting anything already set.

    Never prints values: an env dump in a traced shell writes secrets into a tracked JSONL.
    """
    for path in ENV_FILES:
        try:
            with open(path) as fh:
                for line in fh:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    k, v = line.split("=", 1)
                    k = k.strip()
                    v = v.strip().strip('"').strip("'")
                    if TOKEN_VAR_RE.match(k) and v and k not in os.environ:
                        os.environ[k] = v
        except OSError:
            continue


def discover_tokens():
    """[(var_name, token)] for every IBM token that EXISTS, newest-looking first.

    Reverse sort puts ALT3 > ALT2 > ALT purely so the likely-current account is tried first;
    correctness never depends on the order, because every account is tried until one sees the job.
    """
    _load_env_files()
    found = []
    for name in sorted((k for k in os.environ if TOKEN_VAR_RE.match(k)), reverse=True):
        tok = os.environ.get(name)
        if tok:
            found.append((name, tok))
    return found


def describe_accounts():
    """Account NAMES only — never tokens, not even truncated."""
    return [n for n, _ in discover_tokens()]


def all_services(channel="ibm_quantum_platform"):
    """[(account_name, service)] for every account whose credentials construct successfully.

    An account that fails to construct is skipped rather than fatal — one bad credential must not
    blind the sweep to the other accounts. It is reported by _construct_errors() so the skip is
    never silent.
    """
    from qiskit_ibm_runtime import QiskitRuntimeService

    out, errs = [], []
    for name, tok in discover_tokens():
        try:
            inst = os.environ.get("QISKIT_IBM_INSTANCE") or None
            kw = {"channel": channel, "token": tok}
            if inst:
                kw["instance"] = inst
            out.append((name, QiskitRuntimeService(**kw)))
        except Exception as exc:                                    # noqa: BLE001
            errs.append((name, f"{type(exc).__name__}: {exc}"))
    all_services._errors = errs
    return out


def _construct_errors():
    return getattr(all_services, "_errors", [])


def service_for_job(job_id, channel="ibm_quantum_platform"):
    """(service, account_name) for the FIRST account that can see `job_id`.

    Raises JobNotFoundAnywhere naming every account tried — so a genuine absence is reportable as
    an absence, and a routing mistake is never reportable as a dead job.
    """
    tried = []
    for name, svc in all_services(channel=channel):
        tried.append(name)
        try:
            svc.job(job_id)
            return svc, name
        except Exception:                                           # noqa: BLE001
            continue
    detail = ""
    if _construct_errors():
        detail = "  (accounts that failed to construct: " + \
                 ", ".join(f"{n} [{e}]" for n, e in _construct_errors()) + ")"
    raise JobNotFoundAnywhere(
        f"job {job_id} not visible to ANY of {len(tried)} account(s): {', '.join(tried) or 'NONE'}."
        f"{detail}"
    )


def service_for_submission(account_var):
    """Service for an EXPLICITLY NAMED account. REFUSES to fall back — ever.

    Submission is the asymmetric case. A read that guesses wrong returns nothing and you notice;
    a write that guesses wrong lands somewhere real. So this takes the account by name and raises
    if that exact credential is absent, instead of quietly using whatever happens to be saved.
    """
    _load_env_files()
    tok = os.environ.get(account_var)
    if not tok:
        raise RuntimeError(
            f"no {account_var} token in the environment — REFUSING to fall back to a default "
            f"instance for a SUBMISSION. Set {account_var} or name a different account explicitly."
        )
    from qiskit_ibm_runtime import QiskitRuntimeService
    kw = {"channel": "ibm_quantum_platform", "token": tok}
    inst = os.environ.get("QISKIT_IBM_INSTANCE") or None
    if inst:
        kw["instance"] = inst
    return QiskitRuntimeService(**kw)


def assert_explicit_account(env_var="QPU_ACCOUNT_VAR"):
    """Runtime guard for a flight script: REFUSE to start unless the account is named.

    Generalised from Whisper's fix to their `_refly_` script (C6578). Call it at the TOP of any
    script that can submit:

        from ibm_multi_account import assert_explicit_account, service_for_submission
        acct = assert_explicit_account()            # dies here if nobody named an account
        svc  = service_for_submission(acct)

    WHY THIS EXISTS ALONGSIDE THE STATIC CHECKER. `preflight_account_check.py` must be REMEMBERED,
    and a gate you have to remember is one you skip on the cycle it mattered — my documented
    failure mode, and the reason invisible gates drift for hundreds of cycles. This one cannot be
    skipped: it is inside the script, it runs on every execution, and it fails CLOSED.

    It also covers what static analysis cannot — an account resolved through an indirection the
    checker cannot see. The two are complements, not redundancy: the checker catches a defect
    before you fly, this catches it at the instant of flying.

    THE TIME-DEPENDENCE IS THE REAL POINT (Whisper's observation, and it is the strongest form of
    the rule): a re-flyable script's CORRECT account changes over time — the one that was paid last
    month may be depleted today. So it must never inherit a default, INCLUDING a well-intentioned
    hardcoded one chosen at conversion time. The account has to be named at the moment of flight,
    by whoever is flying.
    """
    # C5060 FIX (Whisper): LOAD THE .env FILES BEFORE CHECKING FOR THE TOKEN. This function read
    # os.environ directly while describe_accounts() — called to build the very error message —
    # goes through discover_tokens() and DOES load them. So a correctly-configured .env account
    # produced a self-contradictory refusal: "no token is set for IBMQ_ALT4 ... Accounts currently
    # discoverable: [... 'IBMQ_ALT4' ...]". It refused the flight and then listed the credential
    # it had just declared absent. service_for_submission() already loads first, so the asymmetry
    # was unintended. Caught by the guard firing on a valid ALT4 flight.
    _load_env_files()
    name = os.environ.get(env_var)
    if not name:
        raise RuntimeError(
            f"{env_var} is not set — REFUSING to start a script that can submit.\n"
            f"  A re-flyable script must never inherit a defaulted account: the correct account is\n"
            f"  TIME-DEPENDENT (the one that was funded last month may be depleted today).\n"
            f"  Name it explicitly, e.g.  {env_var}=IBMQ_ALT2 python3 {os.path.basename(sys.argv[0])}\n"
            f"  Accounts currently discoverable: {describe_accounts() or 'NONE'}"
        )
    if not os.environ.get(name):
        raise RuntimeError(
            f"{env_var}={name} but no token is set for {name} — REFUSING to fall back.\n"
            f"  Accounts currently discoverable: {describe_accounts() or 'NONE'}"
        )
    return name


class MultiAccountService:
    """Drop-in stand-in for `QiskitRuntimeService()` on READ paths.

    Exists so converting an existing reader is a ONE-LINE change:
        svc = QiskitRuntimeService()   ->   svc = multi_account_service()
    A conversion that requires restructuring each call site is a conversion that gets done to two
    files and abandoned, which is how 52 copies of this defect accumulated in the first place.

    `.job(id)` resolves per job (jobs from different flights legitimately live on different
    accounts) and remembers which account answered, so `.last_account` can be printed alongside
    the result — naming the scope is part of the fix, not decoration.
    """

    def __init__(self, channel="ibm_quantum_platform"):
        self._channel = channel
        self._by_job = {}
        self.last_account = None

    def job(self, job_id):
        if job_id in self._by_job:
            svc, acct = self._by_job[job_id]
        else:
            svc, acct = service_for_job(job_id, channel=self._channel)
            self._by_job[job_id] = (svc, acct)
        self.last_account = acct
        return svc.job(job_id)

    def __getattr__(self, name):
        """Anything that is not `.job` falls through to the FIRST constructible account.

        Deliberately narrow: only job lookup is account-ambiguous. Quota/usage calls answer for
        ONE account and must say so — silently unioning a usage figure across accounts alongside a
        job list from all of them produces a mismatch that reads as fact.
        """
        svcs = all_services(channel=self._channel)
        if not svcs:
            raise RuntimeError("no IBM accounts discoverable in the environment")
        self.last_account = svcs[0][0]
        return getattr(svcs[0][1], name)


def multi_account_service(channel="ibm_quantum_platform"):
    return MultiAccountService(channel=channel)


def _selftest():
    """THE TEST IS THE GUARD, NOT THE PROSE.

    Plants one MORE account than exists and asserts the discovery finds it — the only check that
    catches 'I claimed this generalises and then hardcoded a list'. Needs no network.
    """
    ok = True
    base = describe_accounts()
    print(f"discovered accounts (names only): {base}")

    os.environ["IBMQ_ALT9_TESTONLY"] = "x" * 8
    after = describe_accounts()
    if "IBMQ_ALT9_TESTONLY" in after:
        print("PASS  a NEW account appearing in the environment is discovered with no code edit")
    else:
        print("FAIL  a new account was NOT discovered — the enumeration is fake")
        ok = False
    del os.environ["IBMQ_ALT9_TESTONLY"]

    # exact-name matching: IBMQ_ALT must not be confused with IBMQ_ALT2
    if TOKEN_VAR_RE.match("IBMQ_ALT") and TOKEN_VAR_RE.match("IBMQ_ALT2") and \
       not TOKEN_VAR_RE.match("IBMQ_ALT2_SUFFIX_LOWERcase"):
        print("PASS  exact-name matching (no IBMQ_ALT / IBMQ_ALT2 prefix collision)")
    else:
        print("FAIL  name matching is not exact")
        ok = False

    # submission refuses to fall back
    try:
        service_for_submission("IBMQ_DEFINITELY_ABSENT")
        print("FAIL  submission helper fell back instead of refusing")
        ok = False
    except RuntimeError as exc:
        if "REFUSING" in str(exc):
            print("PASS  submission REFUSES to fall back on a missing credential")
        else:
            print(f"FAIL  wrong error: {exc}")
            ok = False
    except Exception as exc:                                        # noqa: BLE001
        print(f"FAIL  wrong exception type: {type(exc).__name__}")
        ok = False

    # runtime flight guard: must fail CLOSED in both directions
    os.environ.pop("QPU_ACCOUNT_VAR", None)
    try:
        assert_explicit_account()
        print("FAIL  flight guard started with NO account named")
        ok = False
    except RuntimeError:
        print("PASS  flight guard refuses when no account is named")
    os.environ["QPU_ACCOUNT_VAR"] = "IBMQ_NOT_SET_ANYWHERE"
    try:
        assert_explicit_account()
        print("FAIL  flight guard accepted a named account with no token")
        ok = False
    except RuntimeError:
        print("PASS  flight guard refuses a named account that has no token")
    real = describe_accounts()
    if real:
        os.environ["QPU_ACCOUNT_VAR"] = real[0]
        try:
            got = assert_explicit_account()
            print(f"PASS  flight guard admits a properly named account ({got})")
        except RuntimeError as exc:
            print(f"FAIL  flight guard rejected a valid account: {exc}")
            ok = False
    os.environ.pop("QPU_ACCOUNT_VAR", None)

    # no token values are ever returned by the describe path
    if all(not v.startswith("ey") for v in describe_accounts()):
        print("PASS  describe_accounts() returns names, never token material")
    else:
        print("FAIL  token material leaked into describe output")
        ok = False

    print("SELFTEST", "PASS" if ok else "FAIL")
    return 0 if ok else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(_selftest())
    if "--accounts" in sys.argv:
        print("accounts:", describe_accounts())
        sys.exit(0)
    if "--find" in sys.argv:
        jid = sys.argv[sys.argv.index("--find") + 1]
        try:
            _, acct = service_for_job(jid)
            print(f"job {jid} found on account {acct}")
            sys.exit(0)
        except JobNotFoundAnywhere as exc:
            print(exc)
            sys.exit(1)
    print(__doc__)
