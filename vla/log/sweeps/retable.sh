#!/bin/bash
# Rebuild a sweep table from the STEP logs in log/. Usage: retable.sh <logfile>...
printf "%-24s %-9s %-9s %s\n" log "@half" "final-qtr" "dff_max"
for f in "$@"; do
  awk -v f="$(basename $f)" '
    $1=="STEP" {last=$2; if(!($2 in seen)){seen[$2]=$7}}
    END {}' /dev/null 2>/dev/null
  awk -v f="$(basename $f)" '
    $1=="STEP" {s[$2]=$7; if($2>mx) mx=$2; if($17>m) m=$17}
    END {h=int(mx/2); q=int(mx*3/4); n=0; t=0;
         for (k in s) if (k+0>=q) {n++; t+=s[k]}
         printf "%-24s %-9.4f %-9.4f %.1f\n", f, s[h], t/n, m}' "$f"
done
