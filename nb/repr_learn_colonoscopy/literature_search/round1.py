"""Round 1: every group: all 3-of-5 entity combinations (unordered) and the full entity set; every pattern row: its steps ANDed.
Writes lit_results.json; prints counts and the top 3 hits of each query (redirect to round1.log)."""
import itertools, json
from pubmed import q, T, ENT, PAT
out = []
def run(kind, key, concepts):
    term = ' AND '.join(T[c] for c in concepts)
    n, arts = q(term); out.append(dict(kind=kind, key=key, concepts='+'.join(concepts), query=term, count=n, top=arts))
    print(f'{kind:9}{key:7} n={n:<7} {"+".join(concepts)}', flush=True)
    for a in arts[:3]: print('      ', a[0], a[1], a[2], '|', a[3], flush=True)
for b, es in ENT.items():
    for tri in itertools.combinations(es, 3): run('ent3', b, list(tri))
    if len(es) > 3: run('ent_all', b, es)
for r, cs in PAT.items(): run('pattern', f'r{r}', cs)
json.dump(out, open('lit_results.json', 'w'))
