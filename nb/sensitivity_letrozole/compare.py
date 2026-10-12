import glob, re, numpy as np, pandas as pd
from sklearn.metrics import adjusted_rand_score as ari, normalized_mutual_info_score as nmi
V = {}
for f in glob.glob('final_table_letrozole_k*_*.xlsx'):
    m = re.search(r'k(\d+)_(\w+)\.xlsx', f); V[m.group(2)] = (int(m.group(1)), f)
order = [v for v in ['full','win12','win18','win24'] if v in V]
rows, lab = [], {}
for v in order:
    k, f = V[v]; t = pd.read_excel(f); p = t[t.iloc[:, 3].notna()]
    r, vd, od = p.iloc[:, 8], p.iloc[:, 11], p.iloc[:, 13]
    robust = (r == 5) & (od != 'Same-day bundle')
    npz = np.load(f'nmf_k{k}_letrozole_{v}.npz', allow_pickle=True); lab[v] = npz['labels']
    sizes = np.bincount(npz['labels'], minlength=k) / len(npz['labels']) * 100
    rows.append(dict(run=v, k=k, vocab=len(npz['cols']), patterns=len(p), solid=int((vd == 'Solid').sum()),
        solid_pct=round(100 * (vd == 'Solid').mean()), five_of_five=int((r == 5).sum()), same_day=int((od == 'Same-day bundle').sum()),
        robust_5of5_dated=int(robust.sum()), robust_pct=round(100 * robust.mean()), median_lift=round(p.iloc[:, 10].median(), 1),
        largest_bundle_pct=round(sizes.max(), 1), smallest_bundle_pct=round(sizes.min(), 1)))
S = pd.DataFrame(rows).set_index('run'); print(S.T.to_string())
print('\npairwise ARI / NMI (same patients)')
M = pd.DataFrame({a: {b: f'{ari(lab[a], lab[b]):.2f}/{nmi(lab[a], lab[b]):.2f}' for b in order} for a in order}); print(M.to_string())
S.to_csv('sensitivity_summary.csv')
