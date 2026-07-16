#!/bin/bash
cd /droid/repos/quantum
JOBS="d9c4kgv550hc73dksojg d9c4kj41osis73bjcf00 d9c4klh6dkoc73fh6g9g"
declare -A DONE
for i in $(seq 1 300); do
  allg=1
  for J in $JOBS; do
    [ "${DONE[$J]}" = "1" ] && continue
    ST=$(timeout 60 python3 -c "from qiskit_ibm_runtime import QiskitRuntimeService; print(QiskitRuntimeService().job('$J').status())" 2>/dev/null | tail -1)
    case "$ST" in
      *DONE*) echo "=== $J DONE ==="; timeout 180 python3 scripts/grade_exp140b.py $J 2>&1 | grep -vE "Deprecat|warn"; DONE[$J]=1;;
      *ERROR*|*CANCEL*) echo "=== $J $ST ==="; DONE[$J]=1;;
      *) echo "[poll $i] $J=$ST"; allg=0;;
    esac
  done
  [ "$allg" = "1" ] && { echo "=== all resolved ==="; exit 0; }
  sleep 60
done
echo "timed out"; exit 2
