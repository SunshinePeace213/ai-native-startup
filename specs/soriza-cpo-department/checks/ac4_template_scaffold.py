# /// script
# requires-python = ">=3.11"
# ///
"""AC4 — projects/_template contains exactly the client scaffold, and all nine
section-brief skeletons carry both a "One job" and a "One desired action"
field."""

from pathlib import Path

t = Path("projects/_template")
files = sorted(str(p.relative_to(t)) for p in t.rglob("*") if p.is_file())
lib = [
    f"section-briefs/_library/{n}.md"
    for n in [
        "content-blog",
        "cta-band",
        "features-solutions",
        "footer",
        "header-navigation",
        "hero",
        "logo-tape",
        "pricing-plans",
        "testimonials",
    ]
]
expected = sorted(
    [
        "intake.md",
        "brief.md",
        "sitemap-ia.md",
        "asset-checklist.md",
        "decision-log.md",
        "wireframes/README.md",
        "section-briefs/README.md",
    ]
    + lib
)
assert files == expected, (files, expected)
for s in lib:
    text = (t / s).read_text()
    assert "One job" in text and "One desired action" in text, s
print("AC4 ok")
