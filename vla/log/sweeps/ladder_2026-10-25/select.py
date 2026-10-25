"""3c selection (user rule, 2026-10-25): which register ladder the main run continues with.
usage: python select.py RUN:TAU ... (control first); reads eval_<RUN>.log and <RUN>.curve in this directory.
1. guard, long coherent generation: EVALL last-window fluency >= control - 3, EVALL drift >= control drift - 3,
   EVALH own >= control - 0.05 (the control always passes);
2. primary: lowest held-out EVAL (400 fineweb docs);
3. tiebreak: of the runs within 0.01 of the best, the highest memory in the oldest age bin of the forgetting curve.
Prints the table and the decision; the last line is 'DECISION <run> <tau>'."""
import os, re, sys
D = os.path.dirname(os.path.abspath(__file__))
def last(path, pat):
    m = [re.search(pat, l) for l in open(path)]
    m = [x for x in m if x]
    if not m:
        raise SystemExit(f'{path}: no line matches {pat!r}')
    return m[-1]
rows = []
for a in sys.argv[1:]:
    run, tau = a.split(':')
    ev, cv = f'{D}/eval_{run}.log', f'{D}/{run}.curve'
    e = float(last(ev, r'^EVAL step +\d+ corpus fineweb +clean +([\d.]+)').group(1))
    m = last(ev, r'^EVALL .*fluency ([\d./-]+) drift ([+-][\d.]+)')
    fl, dr = float(m.group(1).split('/')[-1]), float(m.group(2))
    own = float(last(ev, r'^EVALH .* own ([+-][\d.]+)').group(1))
    mem = last(cv, r'^age .*mean age +([\d.]+)K +memory ([+-][\d.]+) \+- ([\d.]+)')
    held = float(last(cv, r'held-out improvement ([+-][\d.]+)').group(1))
    rows.append(dict(run=run, tau=tau, eval=e, fl=fl, drift=dr, own=own, age=float(mem.group(1)),
                     mem=float(mem.group(2)), se=float(mem.group(3)), held=held))
c = rows[0]
for r in rows:
    r['ok'] = r is c or (r['fl'] >= c['fl'] - 3 and r['drift'] >= c['drift'] - 3 and r['own'] >= c['own'] - 0.05)
print(f'{"run":18} {"ctx_tau":12} {"EVAL":>7} {"EVALL fl":>8} {"drift":>6} {"own":>7} {"held":>7} {"old-bin memory":>22} guard')
for r in rows:
    print(f'{r["run"]:18} {r["tau"]:12} {r["eval"]:7.4f} {r["fl"]:8.1f} {r["drift"]:+6.1f} {r["own"]:+7.3f} '
          f'{r["held"]:+7.4f} {r["mem"]:+8.4f} +-{r["se"]:.4f} @{r["age"]:5.0f}K {"pass" if r["ok"] else "FAIL"}')
ok = [r for r in rows if r['ok']]
best = min(r['eval'] for r in ok)
tied = [r for r in ok if r['eval'] <= best + 0.01]
win = max(tied, key=lambda r: r['mem']) if len(tied) > 1 else tied[0]
why = (f'lowest EVAL {win["eval"]:.4f}' if len(tied) == 1 else
       f'EVAL within 0.01 of the best ({", ".join(r["run"] for r in tied)}); highest old-bin memory {win["mem"]:+.4f}')
print(f'winner {win["run"]}: {why}')
print(f'DECISION {win["run"]} {win["tau"]}')
