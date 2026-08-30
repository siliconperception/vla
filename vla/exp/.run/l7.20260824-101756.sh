#!/bin/bash
# 2026-08-24 11:30  C1 = 7x7 instead of 3x17, at matched depth-product.
#
# 3x17 = 51 convs, 7x7 = 49 convs, so trainable weight count is held ~constant
# (this is a SHAPE experiment, not the capacity experiment -- capacity is last).
# What changes is how the 30M parameters are arranged: 7 recurrent DFF states of
# 7 convs each, vs 3 states of 17.  More states = more places to hold
# information and a longer clock ladder; fewer convs per state = smaller
# receptive field per write (RF radius 7 vs 17 on a 16x16 grid, so a 7-deep
# stack no longer covers the grid in one write -- C-1 = 15 convs are needed).
#
# --clock_base MUST change with n_layers and this is not a second variable.
# The ladder is periods = base**li (vla.py:204), so p_max = base**(L-1) and
# reach is set by p_max.  base 13.15 at L=3 gives p_max 173.  The SAME base at
# L=7 gives 13.15**6 = 5.2M steps: the deep layers would never write once in a
# 1024-token document, which is a broken model, not a shape test.  Holding
# p_max=173 needs base = 173**(1/6) = 2.36 (check: 2.36**6 = 172.8).  So the
# reach target is held fixed and only the arrangement varies.
cd /proj/devices/vla

M=c1_7x7
echo "=== START $M (100000 steps, 7x7, clock_base 2.36 holds p_max=173) $(date '+%H:%M')"
./exp/watch.sh $M C1 > /dev/null 2>&1 & WP=$!
./exp/run.sh $M 100000 --n_layers 7 --depth 7 --clock_base 2.36
sleep 25; kill $WP 2>/dev/null
cp -f checkpoint/$M.pt checkpoint/$M.final.pt 2>/dev/null

echo "=== SCORE $M vs b5 (one process, scorer seed cancels) $(date '+%H:%M')"
conda run --no-capture-output -n dev python exp/score.py \
    checkpoint/$M.final.pt checkpoint/b5_long.final.pt \
    --corpus web --docs 400 --minlen 512 --maxlen 1024 2>/dev/null \
    | grep -E "^checkpoint|^c1|^b5|^----" | tee -a PLAN.txt
conda run --no-capture-output -n dev python exp/gencheck.py checkpoint/$M.final.pt 80 3 \
    2>/dev/null | tee -a PLAN.txt

echo "=== REACH $M $(date '+%H:%M')"
conda run --no-capture-output -n dev python exp/reach.py --load checkpoint/$M.final.pt \
    --corpus web --docs 800 --rows 500 --minlen 512 --maxlen 1024 --len 1024 \
    --periods 64,512 2>/dev/null | grep -E "full-history|^  P=" | tee -a PLAN.txt
echo "=== END $M $(date '+%H:%M')"
echo "L7 COMPLETE $(date)"
