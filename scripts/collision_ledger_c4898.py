#!/usr/bin/env python3
"""Collision-corrected ledger — derivation check against banked Exp203 data. C4898, 0 QPU.

POST-HOC ANALYSIS (labeled): validates the XOR acceptance law and quantifies the
coherence-column deviation on the already-flown Exp203 decode. No gate is re-graded;
Exp203's registered NOT HELD stands. Output feeds docs/collision-corrected-ledger and the
frozen 203b prediction set.

Model:
  e_r(theta) = (1 - cos(theta/2))/2          record parity-flip probability (ideal)
  p_n        = 1 - acc(0)                    fabric parity-flip probability (in-job anchor)
  XOR LAW:   acc(theta) = (1-p_n)(1-e_r) + p_n*e_r
             (naive/refuted: acc(0)*(1-e_r) — independent-survival instead of XOR)
  Parameter-free checkpoint: acc(pi) = 1/2 for ANY p_n.
  Coherence (Pauli-static collision model, parameters c0/m_odd measured at theta=0):
     post(theta) = [(1-p_n)(1-e_r)*c0 - p_n*e_r*m_odd] / acc(theta)
     where m_odd = (X1_unpost(0) - acc(0)*c0) / p_n   (parity-odd ensemble coherence)
"""
import json, os
import numpy as np

HERE = os.path.dirname(os.path.abspath(__file__))
d = json.load(open(os.path.join(HERE, "..", "results", "exp203_auditor_rewinder_decode.json")))
R = d["results"]
PI = np.pi
DOSES = (0.0, 0.25, 0.5, 0.75, 1.0)

lc = {t: R[f"lc_{t}_2"] for t in DOSES}
acc0 = lc[0.0]["acceptance"]
c0 = lc[0.0]["X1_post"]
u0 = lc[0.0]["X1_unpost"]
p_n = 1 - acc0
m_odd = (u0 - acc0 * c0) / p_n
print(f"anchors (theta=0, in-job): acc0={acc0:.4f}  c0={c0:.4f}  unpost0={u0:.4f}")
print(f"derived: p_n={p_n:.4f}  m_odd={m_odd:.4f} "
      f"(parity-odd shots retain +{m_odd:.2f} of X1 -> flips concentrate on the q2/q3 pair)")

print("\nACCEPTANCE COLUMN — XOR law vs naive (post-hoc on Exp203):")
print(f"{'t':>5} {'e_r':>7} {'meas':>7} {'XOR':>7} {'resid':>7} {'naive':>7} {'resid':>7}")
xor_res, naive_res = [], []
for t in DOSES:
    e = (1 - np.cos(t * PI / 2)) / 2
    xor = (1 - p_n) * (1 - e) + p_n * e
    nv = acc0 * (1 - e)
    m = lc[t]["acceptance"]
    xor_res.append(m - xor); naive_res.append(m - nv)
    print(f"{t:>5} {e:>7.4f} {m:>7.4f} {xor:>7.4f} {m-xor:>+7.4f} {nv:>7.4f} {m-nv:>+7.4f}")
print(f"max |resid|: XOR {max(abs(v) for v in xor_res):.4f}  "
      f"naive {max(abs(v) for v in naive_res):.4f}")
print(f"checkpoint acc(pi)=1/2 (any p_n): measured {lc[1.0]['acceptance']:.4f}")

print("\nCOHERENCE COLUMN — Pauli-static collision model vs measured:")
print(f"{'t':>5} {'meas':>7} {'model':>7} {'resid':>7} {'collision wt':>12} {'B_req':>7}")
for t in DOSES:
    e = (1 - np.cos(t * PI / 2)) / 2
    acc_m = lc[t]["acceptance"]
    num = (1 - p_n) * (1 - e) * c0 - p_n * e * m_odd
    model = num / acc_m
    m = lc[t]["X1_post"]
    w_coll = p_n * e
    # collision-class coherence B required to reproduce the measurement exactly
    B_req = (m * acc_m - (1 - p_n) * (1 - e) * c0) / w_coll if w_coll > 1e-9 else float("nan")
    print(f"{t:>5} {m:>7.4f} {model:>7.4f} {m-model:>+7.4f} {w_coll:>12.4f} {B_req:>7.3f}")
print(f"\nPauli-static model demands collision shots at B = -m_odd = {-m_odd:+.3f};")
print("measured B_req climbs to +0.3 — every static Pauli bookkeeping gives the minus sign,")
print("so the deviation is a MEASUREMENT of non-Pauli (coherent/temporally structured) noise")
print("in the parity-flip process — the 199/F111 class, appearing in the ledger's")
print("coherence column. Twirled compilation should restore the minus sign (203b test).")

# refund column under the XOR model
lu = {t: R[f"lu_{t}_2"] for t in DOSES}
print(f"\nREFUND COLUMN: acc_lu(pi)/acc_lu(0) = {lu[1.0]['acceptance']/lu[0.0]['acceptance']:.4f} "
      f"(XOR model with record removed: 1.000; shortfall consistent with measured coin "
      f"residue {lu[1.0]['coin_p1']:.3f} at 2us — partial record return, priced not assumed)")
