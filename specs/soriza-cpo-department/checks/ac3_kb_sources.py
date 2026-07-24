# /// script
# requires-python = ">=3.11"
# dependencies = ["pyyaml"]
# ///
"""AC3 — sources.yaml carries the exact design-group source identities plus the
anthropic memory entry, and index.md lists every mirror. Run from the hydrated
main checkout — after the post-#44 /harness-layer:kb sync — since mirrors and
index.md are gitignored; adjust a URL marker only if #44 recorded a documented
same-topic swap."""

from pathlib import Path

import yaml

m = yaml.safe_load(Path("ai-docs/sources.yaml").read_text())
d = m.get("design", [])
assert len(d) == 5 and all(e["fetched"] and e["file"].startswith("design/") for e in d), d
urls = [e["url"] for e in d]
for marker in ["w3.org/WAI/WCAG22/quickref", "web.dev/learn/design", "fonts.google.com/knowledge"]:
    assert sum(marker in u for u in urls) == 1, "missing/duplicate source: " + marker
assert sum("nngroup.com/articles/" in u for u in urls) == 2, (
    "expected exactly the two NN/g articles"
)
assert any("nngroup.com" in u and "homepage" in u for u in urls), (
    "NN/g homepage cornerstone missing"
)
idx = Path("ai-docs/index.md").read_text()
for e in d:
    assert e["file"] in idx, "index.md missing entry for " + e["file"]
mem = [e for e in m["anthropic"] if "code.claude.com/docs/en/memory" in e["url"]]
assert len(mem) == 1 and mem[0]["fetched"] and mem[0]["file"].startswith("anthropic/"), mem
assert mem[0]["file"] in idx, "index.md missing entry for " + mem[0]["file"]
print("AC3 ok")
