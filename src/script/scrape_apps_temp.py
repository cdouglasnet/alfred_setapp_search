#!/usr/bin/env python3
"""Scrape SetApp app cards from apps_temp.html into apps_scraped.json."""

import json
import re
import html
from pathlib import Path


def parse_uid(icon_src: str):
    match = re.search(r"/app/(\d+)/", icon_src or "")
    return int(match.group(1)) if match else None


def main() -> None:
    base_dir = Path(__file__).resolve().parent.parent
    html_path = base_dir / "data" / "apps_temp.html"
    output_path = base_dir / "data" / "apps_scraped.json"

    content = html_path.read_text(encoding="utf-8")
    apps = []

    card_re = re.compile(
        r'<a\s+class="application-card_applicationCard__[^"]*"\s+href="(?P<href>[^"]*)">(?P<body>.*?)</a>',
        re.DOTALL,
    )

    for match in card_re.finditer(content):
        href = (match.group("href") or "").strip()
        body = match.group("body") or ""
        arg = f"https://setapp.com{href}" if href.startswith("/") else href

        title_match = re.search(r"<h3[^>]*>(.*?)</h3>", body, re.DOTALL)
        title = html.unescape(title_match.group(1)).strip() if title_match else ""

        subtitle_match = re.search(r'<div\s+class="application-card_description__[^"]*">(.*?)</div>', body, re.DOTALL)
        subtitle = html.unescape(subtitle_match.group(1)).strip() if subtitle_match else ""

        src_match = re.search(r'\ssrc="([^"]+)"', body)
        icon_src = src_match.group(1).strip() if src_match else ""

        rating = None
        platforms = ""
        rating_match = re.search(r"<span>\s*(\d+)\s*<!--", body, re.DOTALL)
        if rating_match:
            rating = int(rating_match.group(1))

        platforms_match = re.search(r'<span\s+class="application-card_platforms__[^"]*">(.*?)</span>', body, re.DOTALL)
        if platforms_match:
            platforms = html.unescape(platforms_match.group(1)).strip()

        badge_match = re.search(r'<span\s+class="badge_root___qdsk[^"]*application-card_badge__[^"]*"[^>]*>(.*?)</span>', body, re.DOTALL)
        badge_text = html.unescape(badge_match.group(1)).strip() if badge_match else ""

        apps.append(
            {
                "uid": parse_uid(icon_src),
                "title": title,
                "subtitle": subtitle,
                "iconSrc": icon_src,
                "arg": arg,
                "rating": rating,
                "platforms": platforms,
                "status": "" if badge_text == "AI+" else badge_text,
                "ai": "AI+" if badge_text == "AI+" else "",
            }
        )

    payload = {"items": apps}
    output_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Scraped {len(apps)} apps -> {output_path}")


if __name__ == "__main__":
    main()


