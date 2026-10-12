"""Round 1. For every bundle: all 3-of-5 entity combinations (unordered), the 3 entities + letrozole, and the 5-entity set;
for every pattern row of the final table: its steps ANDed (PubMed cannot test order). Writes lit_results.json; prints counts + top hits."""
import json
from pubmed import q, T, ENT, PAT
import itertools
out=[]
def run(kind,key,concepts,extra=None):
    term=' AND '.join(T[c] for c in concepts)
    n,arts=q(term); out.append(dict(kind=kind,key=key,concepts='+'.join(concepts),count=n,top=json.dumps(arts)))
    print(f'{kind:9}{key:5} n={n:<7} {"+".join(concepts)}'); 
    for a in arts[:3]: print('      ',a[0],a[1],a[2],'|',a[3])
for b,es in ENT.items():
    for tri in itertools.combinations(es,3): run('ent3',b,list(tri))
    run('ent3+LTZ',b,list(es[:3])+['letro']); run('ent5',b,es)
for r,cs in PAT.items(): run('pattern',f'r{r}',cs)
json.dump(out,open('lit_results.json','w'))
