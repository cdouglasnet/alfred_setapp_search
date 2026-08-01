#!/usr/bin/env python3
"""Set membership=false for apps listed in standalone_pasted.html."""

import html
import json
import re
from pathlib import Path
from urllib.parse import urlparse


CARD_RE = re.compile(
    r'<a\s+class="application-card_applicationCard__[^"]*"\s+href="(?P<href>[^"]*)">(?P<body>.*?)</a>',
    re.DOTALL,
)


def extract_slug(url_or_path: str) -> str:
    raw = (url_or_path or "").strip()
    if not raw:
        return ""
    parsed = urlparse(raw)
    path = parsed.path if parsed.scheme else raw
    if path.startswith("/apps/"):
        path = path[len("/apps/") :]
    return path.strip("/").lower()


def extract_standalone_slugs(html_content: str) -> set[str]:
    slugs: set[str] = set()
    for match in CARD_RE.finditer(html_content):
        href = html.unescape((match.group("href") or "").strip())
        slug = extract_slug(href)
        if slug:
            slugs.add(slug)
    return slugs


def main() -> None:
    base_dir = Path(__file__).resolve().parent.parent
    html_path = base_dir / "data" / "standalone_pasted.html"
    apps_path = base_dir / "data" / "apps_scraped.json"

    standalone_html = html_path.read_text(encoding="utf-8")
    standalone_slugs = extract_standalone_slugs(standalone_html)

    payload = json.loads(apps_path.read_text(encoding="utf-8"))
    items = payload.get("items", [])
    if not isinstance(items, list):
        raise ValueError("Expected apps_scraped.json to contain an 'items' list")

    updated = 0
    matched_slugs: set[str] = set()

    for item in items:
        if not isinstance(item, dict):
            continue
        slug = extract_slug(str(item.get("arg", "")))
        if slug and slug in standalone_slugs:
            matched_slugs.add(slug)
            if item.get("membership") is not False:
                item["membership"] = False
                updated += 1

    apps_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    unmatched = sorted(standalone_slugs - matched_slugs)
    print(
        f"Standalone slugs: {len(standalone_slugs)} | "
        f"Matched apps: {len(matched_slugs)} | "
        f"Updated membership=false: {updated}"
    )
    if unmatched:
        print("Standalone slugs not found in apps_scraped.json:")
        for slug in unmatched:
            print(f"- {slug}")


if __name__ == "__main__":
    main()
