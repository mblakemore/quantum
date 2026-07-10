# STATIC Duel — play against a real quantum opponent, with your own key

The [demo page](https://mblakemore.github.io/quantum/demo/static-duel/) works out of the box in
**REPLAY mode**: the quantum bot's odds are the statistics we measured on `ibm_marrakesh` in July
2026 (Exp106, job `d983ek52su3c739ip92g` — pre-registration and analysis in this repo).

**LIVE mode** makes the quantum opponent real: every roll the quantum bot makes consumes one
actual measured shot from a fresh job on an IBM quantum computer — *your* job, on *your* free
account. Nothing is hosted by us; your API key never leaves your machine.

## Quickstart (~5 minutes, free)

1. **Get a free IBM Quantum account and API token** — <https://quantum.ibm.com> (the free open
   plan includes quantum time each month; one refill of this demo uses ~2–3 seconds of it).
2. **Install the toolkit** (Python 3.10+):
   ```
   pip install qiskit qiskit-ibm-runtime
   ```
3. **Clone this repo and set your token** (or use a
   [saved account](https://docs.quantum.ibm.com/guides/setup-channel)):
   ```
   git clone https://github.com/mblakemore/quantum && cd quantum
   export QISKIT_IBM_TOKEN=<your token>
   ```
4. **Bank a pool of real shots, then serve them** (it prints the cost and asks before spending):
   ```
   python3 scripts/quantum_duel_server.py --submit --serve
   ```
   One job = 32 switch circuits × 256 shots ≈ 2–3 seconds of your quota ≈ thousands of
   demo rounds. The server **never** spends on its own — when the pool runs low it tells you
   and waits for you to rerun `--submit`.
5. **Open the demo and click "try LIVE"** — either the
   [GitHub Pages version](https://mblakemore.github.io/quantum/demo/static-duel/) (modern
   browsers allow pages to talk to `localhost`) or your local copy
   (`demo/static-duel/index.html`). The banner shows your job ID; from then on, every quantum
   roll is one of your measurements.

No key? `python3 scripts/quantum_duel_server.py --dry-run --serve` exercises the plumbing with
a test pool (clearly labeled — it is *not* real shots; REPLAY mode in the page is already
faithful to the measured statistics).

## What you're actually running

The two "censor machines" are completely depolarizing channels — each provably transmits zero
information, and so does *every* definite-order arrangement of the two (our control arm measured
0.00012 bits). The switch circuit puts the two censors in a superposition of orders; the secret
survives only in the correlation between the message qubit and the order-control qubit
(0.0436 bits/use measured). Your LIVE job runs exactly those circuits. Details: the Exp106
pre-registration (`experiments/exp106-capacity-activation-preregistration.md`), the plain-English
version (`ELI5_SUMMARY.md` §18), and the print-and-play tabletop game (`demo/casebook-pnp/`).

## Security notes

- Your token is read from the standard qiskit locations only (`QISKIT_IBM_TOKEN` env var or your
  saved `~/.qiskit` account). This tool never writes, logs, or transmits it anywhere except to
  IBM's API via the official SDK.
- The shot server binds to `localhost` only and serves only measurement records
  (`{t, s, m}` bits) — no credentials, no account data.
- `--submit` always prints the cost estimate and asks for confirmation (`--yes` to skip in
  scripts). It submits exactly one job per invocation.
