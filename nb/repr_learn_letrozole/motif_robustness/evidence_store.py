"""Per-motif arrays persisted for later plots (Phase 11). Keyed by (component, family_id, name)."""
import numpy as np


class EvidenceStore:
    def __init__(self):
        self.data = {}

    @staticmethod
    def key(comp, fid, name):
        return f"c{int(comp)}/f{int(fid):03d}/{name}"

    def put(self, comp, fid, name, arr):
        self.data[self.key(comp, fid, name)] = np.asarray(arr)

    def get(self, comp, fid, name):
        return self.data[self.key(comp, fid, name)]

    def save(self, path):
        np.savez_compressed(path, **{k.replace("/", "__"): v for k, v in self.data.items()})

    @classmethod
    def load(cls, path):
        es = cls()
        with np.load(path, allow_pickle=False) as z:
            for k in z.files:
                es.data[k.replace("__", "/")] = z[k]
        return es
