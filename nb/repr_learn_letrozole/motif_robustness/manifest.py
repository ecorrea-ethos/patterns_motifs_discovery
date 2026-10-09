"""Run manifest: everything needed to say what produced a CSV (config hash, input hashes, git, versions, seeds, timings)."""
import hashlib
import json
import os
import platform
import subprocess
import sys
import time
from contextlib import contextmanager


def sha256_file(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for b in iter(lambda: f.read(chunk), b""):
            h.update(b)
    return h.hexdigest()


def config_hash(cfg):
    return hashlib.sha256(json.dumps(cfg, sort_keys=True, default=str).encode()).hexdigest()


def git_commit(cwd="."):
    try:
        out = subprocess.run(["git", "rev-parse", "HEAD"], cwd=cwd, capture_output=True, text=True, timeout=10)
        return out.stdout.strip() or "unknown"
    except Exception:
        return "unknown"


class Timer:
    """Per-phase wall time: `with timer.phase('name'): ...`"""
    def __init__(self):
        self.times = {}

    @contextmanager
    def phase(self, name):
        t0 = time.perf_counter()
        try:
            yield
        finally:
            self.times[name] = round(time.perf_counter() - t0, 2)


def build_manifest(cfg, input_files, timer=None, extra=None, repo_dir="."):
    import numpy, pandas, scipy
    man = {
        "config": cfg, "config_sha256": config_hash(cfg),
        "inputs_sha256": {os.path.basename(p): sha256_file(p) for p in input_files if os.path.exists(p)},
        "git_commit": git_commit(repo_dir),
        "python": sys.version.split()[0], "platform": platform.platform(),
        "packages": {"numpy": numpy.__version__, "pandas": pandas.__version__, "scipy": scipy.__version__},
        "PYTHONHASHSEED": os.environ.get("PYTHONHASHSEED", "random"),
        "seeds": cfg.get("seeds", {}),
        "phase_seconds": (timer.times if timer else {}),
    }
    if extra:
        man.update(extra)
    return man


def write_manifest(path, man):
    with open(path, "w") as f:
        json.dump(man, f, indent=2, sort_keys=True, default=str)
