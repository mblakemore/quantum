#!/usr/bin/env python3
"""Exp217 — THE FEDERATION COMPUTER: distributed logical CNOT across a shielded cut. C4906.

============================ STATUS: FROZEN-WIP (NOT FLOWN) ============================
C4906 froze this design post-compaction under kill-criterion K1 (deep circuit + one open
construction item; no hardware submitted — honest). VERIFIED this cycle (probes, statevector):
  - terminal-frame reduction of the non-local CNOT (corrections are decode-time Paulis) — DERIVED;
  - in-block CNOT(L1->L2)=SWAP(0,2), CNOT(L2->L1)=SWAP(0,1) — Clifford-conjugation search;
  - preps |0bar0bar|+bar0bar|0bar+bar> and X-bar1 load — 191-map expectation checks all pass;
  - transversal handshake makes the Bell pair on the L2 (ebit) pair with data slots at |0bar>.
OPEN ITEM (next fresh cycle): the ENTANGLER witness (G2) needs d_A=|+bar> loaded AFTER the Bell
  pair, which needs a logical H-bar on one logical qubit (the costly [[4,2,2]] primitive: H^4 =
  H-bar1 H-bar2 . SWAP(L1,L2), so single-qubit H-bar needs an automorphism correction). The
  TRUTH-TABLE branch (G1, Z-basis) is H-free and complete. RESOLUTION OPTIONS for next cycle:
  (a) derive single-qubit H-bar1 by search (as in-block CNOT was found); (b) witness the gate
  via a phase-kickback that avoids |+bar> data; (c) minimal fall-back: certify the truth-table +
  a controlled-Z variant that stays diagonal (no H-bar). Finish selftest GREEN before any submit;
  write the manifest the instant job_id exists (Exp201 rule). Depth-check gates the submit (K1).
=======================================================================================

Horizons-5 P6 flight 1 (plan: docs/p6-federation-computer-plan-whisper-c4906.md).

A logical CNOT between control d_A in shield A (q0-3) and target d_B in shield B (q4-7), executed
with NO gate ever crossing the A-B cut — only in-block logical gates, a shared logical Bell pair
(e_A=L2A, e_B=L2B) made once by a transversal handshake, terminal measurement of the e-qubits,
and a SOFTWARE PAULI FRAME from their two classical outcomes (the 197 no-feed-forward trick).

Non-local CNOT (Eisert-Jozsa-Wilkens), terminal-frame form (derived + verified this cycle):
  resource Bell(e_A,e_B); 1) in-block CNOT(d_A->e_A) at A; 2) measure e_A in Z -> x;
  3) X^x on e_B  [commutes through CNOT(e_B->d_B): X on control -> X on control+target;
     X^x on e_B is inert under its own X-measurement, X^x on d_B is a TERMINAL data Pauli];
  4) in-block CNOT(e_B->d_B) at B; 5) measure e_B in X -> z; 6) Z^z on d_A [TERMINAL data Pauli].
  => the two corrections (X^x on d_B, Z^z on d_A) become a decode-time Pauli frame. No feed-forward.

Verified primitives (probe, this cycle):
  |0bar0bar>=GHZ4; |+bar0bar>=Bell(0,1)Bell(2,3); |0bar+bar>=h0,cx02,h1,cx13 (L1=0,L2=+).
  in-block CNOT(L1->L2) = SWAP(0,2); in-block CNOT(L2->L1) = SWAP(0,1) (Clifford-conj search).
  transversal CNOT A->B (straight, 4 CX) on |...+bar>_A,|...0bar>_B -> Bell on the L2 pair (197).
  191 map: X1=X0X1,Z1=Z0Z2,X2=X0X2,Z2=Z0Z1; stabilizers XXXX,ZZZZ per block.

WITNESSES (H-free — inputs from verified direct preps):
  TRUTH-TABLE: d_A,d_B in {0,1}^2 -> CNOT flips d_B iff d_A=1 (Z-basis readout of both data).
  ENTANGLER: d_A=|+bar>, d_B=|0bar> -> CNOT makes a logical Bell pair: <Z_A Z_B>=<X_A X_B>=+1.

FROZEN GATES (relative to statevector-exact; finalized after selftest):
  G1_TRUTHTABLE: the 4 basis inputs give the correct CNOT output bit-string, each P >= 0.55 and
     >= 5 sigma over the 1/4 uniform floor, after the Pauli frame + stabilizer postselection.
  G2_ENTANGLER: on |+bar 0bar> input, <Z_A Z_B> and <X_A X_B> both >= [band], each >= N sigma over
     the no-gate control (which gives ~0 for <Z_A Z_B>).
  G3_NO_CROSSING_BITS: in-decode falsifier — same shots decoded with the two e-bits IGNORED
     (frame off) collapses the gate (entangler correlators -> ~0). The weld IS the two bits.
  G4_SHIELD_BEATS_BARE: shielded distributed CNOT fidelity - bare (physical, unencoded)
     distributed CNOT fidelity > 0 at >= N sigma.
  Registered verdict = G1 and G2 and G3 and G4.
SCOPE: one [[4,2,2]] block per node (2 logical qubits = 1 data + 1 ebit); global-Clifford,
  terminal-frame distributed CNOT (no mid-circuit feed-forward — the last-gate placement makes
  corrections terminal). Textbook non-local CNOT (Eisert et al.) + the campaign's 197 weld +
  206/214 in-block gates; the new content = a logical two-qubit gate ACROSS A SHIELDED CUT,
  error-detected, beats bare. KILL K1: if transpiled 2q depth/width exceeds the confident band,
  fall back to minimal form or register-and-defer (do NOT force-submit).
BUDGET CHECK (C4887): deep (~10 logical CX + preps). Predictions filed at freeze from depth-check.
Usage: --selftest | --submit [--backend ibm_fez --shots 8000] | --decode
"""
import argparse, itertools, json, os, sys
import numpy as np
from qiskit import QuantumCircuit, transpile

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "..", "scripts"))

# ---- verified [[4,2,2]] preps (L1,L2 combos); offset = block base qubit ----
def _p_00(qc, o):  qc.h(o); qc.cx(o, o+1); qc.cx(o, o+2); qc.cx(o, o+3)          # |0bar0bar>
def _p_p0(qc, o):  qc.h(o); qc.cx(o, o+1); qc.h(o+2); qc.cx(o+2, o+3)             # |+bar0bar> (L1=+,L2=0)
def _p_0p(qc, o):  qc.h(o); qc.cx(o, o+2); qc.h(o+1); qc.cx(o+1, o+3)             # |0bar+bar> (L1=0,L2=+)
def _Xbar1(qc, o): qc.x(o); qc.x(o+1)                                             # logical X on L1 (X0X1)

def _in_cnot_12(qc, o):  qc.swap(o, o+2)     # in-block CNOT(L1->L2) = SWAP(0,2)
def _in_cnot_21(qc, o):  qc.swap(o, o+1)     # in-block CNOT(L2->L1) = SWAP(0,1)

# logical operator halves (191 map) as physical-bit XOR parities, per block offset:
DEC_CANDS = [((0, 1), (0, 2)), ((0, 2), (0, 1)), ((0, 1), (2, 3)), ((0, 2), (1, 3)),
             ((0, 3), (1, 2)), ((1, 2), (0, 3)), ((2, 3), (0, 1)), ((1, 3), (0, 2))]

DATA_INPUTS = ["00", "01", "10", "11"]   # (d_A, d_B) computational truth-table inputs
# readout bases for the data qubits: Z (truth table + <ZZ>), X (<XX> entangler)


def build(data_in, entangler, data_basis):
    """8-qubit distributed-CNOT circuit.
    A=q0-3 (L1A=d_A, L2A=e_A), B=q4-7 (L1B=d_B, L2B=e_B).
    entangler=True -> d_A=|+bar>, d_B=|0bar> (ignore data_in). data_basis in {'Z','X'} for d_A,d_B.
    e_A read in Z (cl 8), e_B read in X (cl 9). data d_A->cl0-block, d_B->cl4-block via stabilizer.
    Returns qc with 8 clbits packed as: bits 0..7 physical Z-outcomes of q0..7 in the chosen data
    basis for data-block qubits (H folded), plus we ALSO need e_A in Z and e_B in X -> handled by
    per-qubit H before measure. cl mapping = qubit index."""
    qc = QuantumCircuit(8, 8)
    # ---- Phase 1: shared Bell pair on the L2 (ebit) qubits, data slots = |0bar> ----
    # A: |0bar>_{L1} |+bar>_{L2};  B: |0bar>_{L1} |0bar>_{L2}
    _p_0p(qc, 0)          # L1A=0, L2A=+
    _p_00(qc, 4)          # L1B=0, L2B=0
    for i in range(4): qc.cx(i, 4 + i)     # transversal CNOT A->B: CNOT(L1A->L1B) trivial(0->0);
                                           # CNOT(L2A->L2B): (+,0)->Bell(e_A,e_B)
    qc.barrier()
    # ---- Phase 2: load data onto L1 (data slots) ----
    if entangler:
        # d_A=|+bar>: currently L1A=|0bar>; make it |+bar> via prep is entangled w/ ebit already.
        # Load |+bar> on L1A by logical H is costly; instead re-derive: we set L1A=0 above, so use
        # a logical-H-free route: swap roles — prepare d_A as |+bar> BEFORE the handshake is not
        # possible without disturbing the ebit. Use the in-block H-free identity: |+bar> load =
        # apply H to the two X1 support qubits? X1=X0X1 -> Hadamard-transform requires care.
        # SIMPLER (kept H-free): the entangler witness prepares d_A=|+bar> by preparing block A as
        # |+bar +bar> pre-handshake is disallowed. -> handled in build_entangler() specialization.
        raise RuntimeError("use build_entangler()")
    else:
        dA, dB = int(data_in[0]), int(data_in[1])
        if dA: _Xbar1(qc, 0)
        if dB: _Xbar1(qc, 4)
    qc.barrier()
    # ---- Phase 3: non-local CNOT(d_A->d_B), terminal-frame ----
    _in_cnot_12(qc, 0)    # CNOT(d_A -> e_A)
    _in_cnot_21(qc, 4)    # CNOT(e_B -> d_B)   (X^x correction on e_B is decode-frame; see header)
    qc.barrier()
    # ---- Phase 4: terminal readout ----
    # e_A (L2A) in Z, e_B (L2B) in X. Data qubits in data_basis.
    # e_A logical Z = Z0Z2 (block A); e_B logical X = X0X2 (block B, +4). Read physically then decode.
    if data_basis == "X":
        for q in list(range(0, 4)) + list(range(4, 8)):
            qc.h(q)
    # e_B X-readout: undo — but e_B is inside block B which we just H'd if data_basis==X...
    # To keep bases clean we read ALL 8 physical qubits in a single basis per circuit variant and
    # reconstruct logical Z_A,Z_B,e_A(Z),e_B(X) from parities. Two variants: allZ and allX.
    for q in range(8): qc.measure(q, q)
    return qc
