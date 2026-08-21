#!/bin/bash
# usage: ckpt_report.sh <mnem>   -- analysis at the latest checkpoint
M=$1; L=log/exp.$M
echo "=== $M @ $(grep -a '^TEXT step' $L | tail -1 | awk '{print $3}') steps  ($(date +%H:%M))"
echo "-- loss / gradient / state (every 1000 steps):"
grep '^STEP' $L | awk '$2%1000==0 {printf "   step %6d  loss %7.4f  grad %7.3f  dff_std %6.3f  dff_max %9.1f  dff_zeros %6.4f\n",$2,$7,$9,$15,$17,$19}'
echo "-- last 10 monitor lines: mean loss / slope"
grep '^STEP' $L | tail -10 | awk '{s+=$7; n++} END {printf "   mean(last10) %.4f  (openwebtext unigram floor 7.549)\n", s/n}'
echo "-- free-running generation health (3 fresh samples; cycle>0.6 = degenerate):"
cp -f checkpoint.pt.$M checkpoint.pt.$M._gc 2>/dev/null
conda run --no-capture-output -n dev python exp/gencheck.py checkpoint.pt.$M._gc 80 3 2>/dev/null
rm -f checkpoint.pt.$M._gc
echo "-- in-training sample:"
grep -a '^GEN:' $L | tail -1 | cut -c1-1200
echo
echo "-- real training text for comparison:"
grep -a '^TXT-SAMPLE:' $L | tail -1 | cut -c1-400
