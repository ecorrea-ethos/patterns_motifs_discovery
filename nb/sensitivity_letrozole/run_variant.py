"""Build a plain script from a letrozole NMF+PrefixSpan notebook for one (variant, window), extended K_GRID.
usage: run_variant.py <full|win12|win18|win24>   ->  writes script_<v>.py, then run it with `ipython script_<v>.py`.
(No Jupyter kernel: the sandbox forbids the local ports a kernel needs.)  Outputs stay in this folder."""
import sys, re, json
v = sys.argv[1]
src = '../repr_learn_letrozole/Letrozole_NMF_PrefixSpan_%s.ipynb' % ('full' if v == 'full' else 'windowed')
wm = None if v == 'full' else int(v[3:])
nb = json.load(open(src))
out = ["import matplotlib; matplotlib.use('Agg')", "from IPython.display import display", "import time as _t; _T0=_t.time()"]
for i, c in enumerate(nb['cells']):
    if c['cell_type'] != 'code': continue
    s = ''.join(c['source'])
    if i == 2:
        s = re.sub(r"^VARIANT\s*=.*$", f"VARIANT       = '{v}'", s, flags=re.M)
        s = re.sub(r"^WINDOW_MONTHS\s*=.*$", f"WINDOW_MONTHS = {wm}", s, flags=re.M)
    if i == 32:
        assert 'K_GRID      = list(range(3, 15))' in s
        s = s.replace('K_GRID      = list(range(3, 15))', 'K_GRID      = list(range(3, 25))')
    out.append(f"print('### CELL {i}  t=%.0fs' % (_t.time()-_T0), flush=True)\n" + s)
open(f'script_{v}.py', 'w').write('\n\n'.join(out) + "\nprint('### DONE', flush=True)\n")
