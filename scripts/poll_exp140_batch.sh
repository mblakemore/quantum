#!/bin/bash
cd /droid/repos/quantum
JOBS="d9c49fp6dkoc73fh61ag d9c49ic1osis73bjbvq0 d9c49ks1osis73bjbvsg"
declare -A DONE
for i in $(seq 1 300); do   # up to ~5h
  allgraded=1
  for J in $JOBS; do
    [ "${DONE[$J]}" = "1" ] && continue
    ST=$(timeout 60 python3 -c "from qiskit_ibm_runtime import QiskitRuntimeService; print(QiskitRuntimeService().job('$J').status())" 2>/dev/null | tail -1)
    case "$ST" in
      *DONE*) echo "=== $J DONE — grading ==="; timeout 180 python3 scripts/grade_exp140.py $J 2>&1 | grep -vE "Deprecat|warn"; DONE[$J]=1;;
      *ERROR*|*CANCEL*) echo "=== $J $ST — skip ==="; DONE[$J]=1;;
      *) echo "[poll $i] $J=$ST"; allgraded=0;;
    esac
  done
  [ "$allgraded" = "1" ] && { echo "=== all 3 jobs resolved ==="; exit 0; }
  sleep 60
done
echo "batch poll timed out"; exit 2
