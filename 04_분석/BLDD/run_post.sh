#!/bin/bash
# BLDD (blood and immune disorder deaths, D50-D89) principal chain
set -x
S="${ST_ROOT:-$(cd "$(dirname "$0")/../.." && pwd)}"; cd "$S"; RS="$S/01_스크립트/rslot.sh"; T=BLDD
GR="$S/04_분석/BLDD/graph_593.graph"; export ST_VER=std3_main ST_THREADS=1 ST_GRAPH="$GR"
q(){ while [ "$(jobs -rp | wc -l)" -ge 1 ]; do sleep 10; done; }
ld(){ while [ "$(sysctl -n vm.loadavg | awk '{print int($2)}')" -gt 14 ]; do sleep 30; done; }
python3 01_스크립트/87_window_grid.py $T std3_main; (cd 01_스크립트 && TAG=$T $RS Rscript 85_window_maps.R $T std3_main); python3 01_스크립트/86_yearly_maps_ehsa_bldd.py $T std3_main
python3 01_스크립트/88g_sens_prep.py $T std3_main TRANS,GCA || exit 1
cd 01_스크립트; export TAG=$T NCO=TRANS,GCA
L=../04_분석/$T
for G in 1 2 3 4 5 6; do q; ld; GROUP=$G $RS Rscript 88g_sens_suite.R > $L/run_<suffix>_88g_$G.log 2>&1 & sleep 5; done
q; ld; $RS Rscript 88h_ppc_varpart.R > $L/run_<suffix>_88h.log 2>&1 &
for G in nb struct kh review; do q; ld; $RS Rscript 88k_struct_kh_bldd.R $G > $L/run_<suffix>_88k_$G.log 2>&1 & sleep 5; done
wait
if grep -q 'KH_typeII FAILED' $L/run_<suffix>_88k_kh.log; then mv $L/results_std3_main/S43_part_KH_typeII.csv $L/results_std3_main/S43_part_KH_typeII_failed_init.csv.bak; KH_INIT=0 $RS Rscript 88k_struct_kh_bldd.R kh > $L/run_<suffix>_88k_kh_init0.log 2>&1; fi
cd ..; TAG=$T ST_VER=std3_main python3 01_스크립트/89g_sens_combine.py $T std3_main > 04_분석/$T/run_<suffix>_89g.log 2>&1
echo "POST rc=$?"; grep -l "FAILED" 04_분석/$T/run_<suffix>_88*.log; true
