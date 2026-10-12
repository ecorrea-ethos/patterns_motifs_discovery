#!/bin/bash
cd "$(dirname "$0")"
export MPLBACKEND=Agg
for v in win12 win18 win24 full; do
  /opt/miniconda3/envs/ethos_llm/bin/ipython script_$v.py > log_$v.txt 2>&1
  echo "$v exit $?" >> run_all.status
done
echo ALLDONE >> run_all.status
