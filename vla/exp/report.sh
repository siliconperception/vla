#!/bin/bash
# usage: report.sh <mnemonic> <expid>   -- one 5K-checkpoint report, appended to PLAN.txt
M=$1; E=$2; L=log/exp.$M
cd /proj/devices/vla
S=$(grep -a '^TEXT step' $L | tail -1 | awk '{print $3}')
{
echo ""
echo "--------------------------------------------------------------------------------"
echo "$E  $M  step $S   $(date '+%Y-%m-%d %H:%M')"
echo "--------------------------------------------------------------------------------"
echo "loss/grad/state:"
grep '^STEP' $L | awk -v s=$S '$2%5000==0 {printf "  step %6d  loss %7.4f  grad %6.3f  dff_std %6.3f  dff_max %8.1f  dff_zeros %6.4f\n",$2,$7,$9,$15,$17,$19}'
grep '^STEP' $L | tail -10 | awk '{t+=$7;n++} END {printf "  mean(last10) %.4f   tokens %.2f M   (unigram floor 7.549)\n",t/n,'"$S"'*250/1e6}'
echo "token efficiency (sustained crossings):"
conda run --no-capture-output -n dev python - "$L" <<'PY' 2>/dev/null
import sys, numpy as np
S=[];L=[]
for ln in open(sys.argv[1]):
    f=ln.split()
    if f and f[0]=='STEP': S.append(int(f[1])); L.append(float(f[6]))
S=np.array(S); L=np.array(L)
if len(L)>=10:
    m=np.convolve(L,np.ones(10)/10,mode='valid'); ms=S[9:]
    base={7.549:3980,7.0:5940,6.5:15680,6.3:30120,6.1:49700,5.9:84980,5.8:99980}
    for t in (7.549,7.0,6.5,6.3,6.1,5.9,5.8):
        idx=[i for i in range(len(m)) if (m[i:]<t).all()]
        if idx:
            d=ms[idx[0]]-base[t]
            print(f'  L<{t:5.3f}  step {ms[idx[0]]:6d}  {ms[idx[0]]*250/1e6:6.2f} M tok   baseline {base[t]:6d}  ({d:+d})')
PY
echo "free-running generation (3 samples; cycle>0.6 degenerate, healthy 0.08-0.11):"
cp -f checkpoint/$M.pt checkpoint/.$M._gc 2>/dev/null
conda run --no-capture-output -n dev python exp/gencheck.py checkpoint/.$M._gc 80 3 2>/dev/null
rm -f checkpoint/.$M._gc
} | LC_ALL=C tr -c '\11\12\15\40-\176' '?' >> PLAN.txt
# generated samples can contain any token in the vocabulary, including non-ASCII;
# PLAN.txt is specified as ASCII, so non-printables are mapped to '?' on the way in.
