"""Build the self-contained HTML animation of the chest pain trajectory graph.

The AHA notebook (last two cells, "7 · Animation export") writes trajectory_k{K}_{TAG}.json from the graph of cells 58-60 and calls build().
Standalone:   python trajectory_anim.py trajectory_k8_chestpain_AHA.json [out.html]      (any python 3, no packages)

The HTML has no external request: d3 (vendor/d3.v7.min.js, v7.9.0, ISC license, Mike Bostock; downloaded from cdn.jsdelivr.net/npm/d3@7/dist/d3.min.js,
sha256 f2094bbf6141b359722c4fe454eb6c4b0f0e42cc10cc7af921fc158fceb86539) and the data are inlined into trajectory_anim_template.html.
"""
import json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
KEYS = {"title", "n_patients", "k", "tag", "anchor", "tf_days", "ticks", "lanes", "nodes", "edges"}


def build(json_path, out_html=None):
    path = lambda p: p if os.path.isabs(p) else os.path.join(HERE, p)
    data = json.load(open(json_path, encoding="utf-8"))
    missing = KEYS - set(data)
    assert not missing, f"{json_path}: missing keys {sorted(missing)}"
    lanes = {l["name"] for l in data["lanes"]}
    ids = {n["id"] for n in data["nodes"]}
    assert all(n["lane"] in lanes for n in data["nodes"]), "a node sits in a lane that is not listed"
    assert all(e["source"] in ids and e["target"] in ids for e in data["edges"]), "an edge points to an unknown node"
    template = open(path("trajectory_anim_template.html"), encoding="utf-8").read()
    d3 = open(path("vendor/d3.v7.min.js"), encoding="utf-8").read()
    assert "</script" not in d3, "d3 contains </script"
    blob = json.dumps(data, ensure_ascii=False).replace("</", "<\\/")      # keeps a stray </script out of the data block
    for marker in ("/*__D3__*/", "/*__DATA__*/"):
        assert template.count(marker) == 1, f"template must contain {marker} exactly once"
    html = template.replace("/*__D3__*/", d3).replace("/*__DATA__*/", blob)
    out_html = out_html or os.path.splitext(json_path)[0] + "_animation.html"
    with open(out_html, "w", encoding="utf-8") as f:
        f.write(html)
    return os.path.abspath(out_html)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    out = build(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
    print(f"wrote {out} ({os.path.getsize(out) / 1024:,.0f} KB)")
