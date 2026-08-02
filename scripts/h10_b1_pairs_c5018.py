#!/usr/bin/env python3
"""H10-B1 game pairs — COMMITTED generator (Whisper C5018).

Repairs the second instance of the ephemeral-code gap (the C1 lesson): the C5016 game
reproduction stored names only for the six non-Pauli pairs; the generator ran inline and
was never committed, which blocked Elder's SDP co-check (general#3619). The definitions
below are transcribed from the SOURCE (Stromberg et al., PRR 6, 023071 / arXiv:2211.01283,
Box 1 — page 6 of the PDF, fetched and read this cycle; cite-check discipline, not memory):

    Box 1.  M^I_+ = {(I,I),(I,X),(I,Z),(X,I),(X,X),(X,Z),(Z,I),(Z,X),(Z,Z)}
            M^I_- = {(Y,I),(Y,X),(Y,Z),(I,Y),(X,Y),(Z,Y)}
            M^II_+ = { ((X-Y)/sqrt2, (X+Y)/sqrt2), ((X+Y)/sqrt2, (X-Y)/sqrt2),
                       ((Z-Y)/sqrt2, (Z+Y)/sqrt2), ((Z+Y)/sqrt2, (Z-Y)/sqrt2) }
            M^II_- = { ((I+iY)/sqrt2, (I-iY)/sqrt2), ((I-iY)/sqrt2, (I+iY)/sqrt2) }
            M+ = M^I_+ u M^II_+   (13 pairs) ;  M- = M^I_- u M^II_-   (8 pairs)

Class promise: (U,V) in M+/- iff U V^T = +/- U^T V; equivalently the branch operator
(U V^T -/+ U^T V)/2 vanishes identically. Self-verification below checks every pair's
promised-off branch at machine precision and the 13/8 split — pinned to the C5016
reproduction artifact (21/21 ok, counts 13/8).

MII naming order = Box 1 listing order (matches the C5016 artifact's MII+_0..3 / MII-_0..1).
"""
import json, os, sys
import numpy as np

I2 = np.eye(2, dtype=complex)
X = np.array([[0, 1], [1, 0]], complex)
Y = np.array([[0, -1j], [1j, 0]])
Z = np.diag([1, -1]).astype(complex)
s2 = np.sqrt(2)

P = {"I": I2, "X": X, "Y": Y, "Z": Z}
PAIRS = []
for a in "IXZ":
    for b in "IXZ":
        PAIRS.append((f"({a},{b})", P[a], P[b], "M+"))
for a, b in (("Y", "I"), ("Y", "X"), ("Y", "Z"), ("I", "Y"), ("X", "Y"), ("Z", "Y")):
    PAIRS.append((f"({a},{b})", P[a], P[b], "M-"))
XmY, XpY = (X - Y) / s2, (X + Y) / s2
ZmY, ZpY = (Z - Y) / s2, (Z + Y) / s2
IpY, ImY = (I2 + 1j * Y) / s2, (I2 - 1j * Y) / s2
PAIRS += [("MII+_0", XmY, XpY, "M+"), ("MII+_1", XpY, XmY, "M+"),
          ("MII+_2", ZmY, ZpY, "M+"), ("MII+_3", ZpY, ZmY, "M+"),
          ("MII-_0", IpY, ImY, "M-"), ("MII-_1", ImY, IpY, "M-")]

def verify():
    ok = True; counts = {"M+": 0, "M-": 0}
    for name, U, V, lab in PAIRS:
        # unitarity of each element
        for M in (U, V):
            if np.linalg.norm(M @ M.conj().T - I2) > 1e-12: ok = False
        plus = (U @ V.T + U.T @ V) / 2
        minus = (U @ V.T - U.T @ V) / 2
        off = minus if lab == "M+" else plus
        on = plus if lab == "M+" else minus
        if np.linalg.norm(off) > 1e-12:
            print(f"PROMISE VIOLATION {name}: off-branch {np.linalg.norm(off):.2e}"); ok = False
        if np.linalg.norm(on) < 1e-12:
            print(f"DEGENERATE {name}: on-branch vanishes too"); ok = False
        counts[lab] += 1
    split_ok = counts == {"M+": 13, "M-": 8}
    print(f"pairs: {len(PAIRS)}  split: {counts}  promises: {'OK' if ok else 'FAIL'}"
          f"  split-vs-C5016-artifact: {'OK' if split_ok else 'FAIL'}")
    return ok and split_ok and len(PAIRS) == 21

def export():
    out = {"source": "Stromberg et al. PRR 6, 023071 (arXiv:2211.01283) Box 1, transcribed from PDF",
           "pairs": [{"name": n, "label": lab,
                      "U_re": U.real.tolist(), "U_im": U.imag.tolist(),
                      "V_re": V.real.tolist(), "V_im": V.imag.tolist()}
                     for n, U, V, lab in PAIRS]}
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "results",
                        "h10_b1_pairs_c5018.json")
    json.dump(out, open(path, "w"), indent=1)
    print("->", path)

if __name__ == "__main__":
    if not verify(): sys.exit(1)
    export()
