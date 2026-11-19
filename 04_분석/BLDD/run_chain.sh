#!/bin/bash
# BLDD (blood and immune disorder deaths, D50-D89) principal chain
#  주 E = 성×18연령 간접표준화(55E → BLDD_Estd25.csv E_std). 비교 결과(NCO): 운수사고 사망(TRANS)·위암 진료(GCA). 민감도 sens_g577·sens_no80·sens_crude·sens_y24.
set -x
S="${ST_ROOT:-$(cd "$(dirname "$0")/../.." && pwd)}"; cd "$S"; RS="$S/01_스크립트/rslot.sh"
GR="$S/04_분석/BLDD/graph_593.graph"; T=BLDD; D=261114; NW=2; NMV=200
q(){ while [ "$(jobs -rp | wc -l)" -ge 2 ]; do sleep 10; done; }
ld(){ while [ "$(sysctl -n vm.loadavg | awk '{print int($2)}')" -gt 14 ]; do sleep 30; done; }
export ST_VER=std3_main ST_THREADS=1 ST_GRAPH="$GR"
ld; (cd 01_스크립트 && ST_MV_STOP=1 $RS Rscript 81_fit_inla.R $T) > 04_분석/$T/run_<suffix>_81a.log 2>&1 || exit 1
STEP=$(( (NMV + NW - 1) / NW ))
for k in $(seq 0 $((NW-1))); do a=$(( k*STEP+1 )); b=$(( (k+1)*STEP )); [ $b -gt $NMV ] && b=$NMV; ld; (cd 01_스크립트 && ST_MV_RANGE=$a-$b $RS Rscript 81_fit_inla.R $T) > 04_분석/$T/run_<suffix>_81_mv_$a.log 2>&1 & sleep 20; done
wait
(cd 01_스크립트 && $RS Rscript 81_fit_inla.R $T) > 04_분석/$T/run_<suffix>_81b.log 2>&1 || exit 1
(cd 01_스크립트 && $RS Rscript 55K_bldd_likelihood.R) > 04_분석/$T/run_55K.log 2>&1
for V in sens_g577 sens_no80 sens_crude sens_y24; do ld; ST_VER=$V python3 01_스크립트/80_build_disease_panel_v.py $T && (cd 01_스크립트 && ST_VER=$V ST_THREADS=1 ST_MV_N=2 ST_GRAPH=$([ $V = sens_g577 ] || echo "$GR") $RS Rscript 81_fit_inla.R $T); done > 04_분석/$T/run_sens3.log 2>&1
python3 01_스크립트/82_core_report.py $T $D > 04_분석/$T/run_<suffix>_82.log 2>&1
python3 01_스크립트/83_check_report.py $T $D >> 04_분석/$T/run_<suffix>_82.log 2>&1
echo "CHAIN done"
python3 01_스크립트/87_window_grid.py $T std3_main; (cd 01_스크립트 && TAG=$T ST_VER=std3_main $RS Rscript 85_window_maps.R $T std3_main); python3 01_스크립트/86_yearly_maps_ehsa_bldd.py $T std3_main
python3 01_스크립트/88g_sens_prep.py $T std3_main TRANS,GCA || exit 1
cd 01_스크립트; export TAG=$T NCO=TRANS,GCA
L=../04_분석/$T
for G in 1 2 3 4 5 6; do q; ld; GROUP=$G $RS Rscript 88g_sens_suite.R > $L/run_<suffix>_88g_$G.log 2>&1 & sleep 5; done
q; ld; $RS Rscript 88h_ppc_varpart.R > $L/run_<suffix>_88h.log 2>&1 &
for G in nb struct kh review; do q; ld; $RS Rscript 88k_struct_kh_bldd.R $G > $L/run_<suffix>_88k_$G.log 2>&1 & sleep 5; done
wait
if grep -q 'KH_typeII FAILED' $L/run_<suffix>_88k_kh.log; then mv $L/results_std3_main/S43_part_KH_typeII.csv $L/results_std3_main/S43_part_KH_typeII_failed_init.csv.bak; KH_INIT=0 $RS Rscript 88k_struct_kh_bldd.R kh > $L/run_<suffix>_88k_kh_init0.log 2>&1; fi
cd ..; TAG=$T ST_VER=std3_main python3 01_스크립트/89g_sens_combine.py $T std3_main > 04_분석/$T/run_<suffix>_89g.log 2>&1
echo "ALL rc=$?"; grep -l "FAILED" 04_분석/$T/run_<suffix>_88*.log; true
