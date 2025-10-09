#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import sys
import hashlib
import re
from urllib.parse import urlparse
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

# Add workflow directory to Python path so bundled modules can be found
WORKFLOW_DIR = os.environ.get("alfred_workflow_dir", os.getcwd())
SCRIPT_DIR = os.path.join(WORKFLOW_DIR, "script")

# Add both directories to Python path
for path in [WORKFLOW_DIR, SCRIPT_DIR]:
    if path not in sys.path:
        sys.path.insert(0, path)

# Add these imports to resolve the "unresolved reference" errors
import builtins
from typing import Union, List, Dict, Any

import api
import utils

# ---- Paths & Config ---------------------------------------------------------

ICON_TIMEOUT = 6


# ---- Helpers ----------------------------------------------------------------

def alfred_cache_dir():
    for key in ("alfred_workflow_cache", "ALFRED_WORKFLOW_CACHE",
                "alfred_workflow_data", "ALFRED_WORKFLOW_DATA"):
        p = os.environ.get(key)
        if p:
            os.makedirs(p, exist_ok=True)
            return p
    p = os.path.join(WORKFLOW_DIR, ".cache")
    os.makedirs(p, exist_ok=True)
    return p

def safe_filename_from_url(url: str) -> str:
    parsed = urlparse(url)
    path = parsed.path or "index"
    base = os.path.basename(path)
    name, ext = os.path.splitext(base)
    if not ext:
        ext = ".png"
    if not name:
        name = "icon"
    h = hashlib.md5(url.encode("utf-8")).hexdigest()[:8]
    return f"{h}{ext}"

def download_icon(url: str, cache_dir: str) -> str:
    if not url or not re.match(r"^https?://", url, re.I):
        return ""
    fname = safe_filename_from_url(url)
    local_path = os.path.join(cache_dir, fname)
    if os.path.exists(local_path) and os.path.getsize(local_path) > 0:
        return local_path
    try:
        req = Request(url, headers={"User-Agent": "Alfred-Workflow/1.0"})
        with urlopen(req, timeout=ICON_TIMEOUT) as resp:
            data = resp.read()
        if data:
            with open(local_path, "wb") as f:
                f.write(data)
            return local_path
    except Exception as e:
        utils.log_error(f"Failed to download icon from {url}: {str(e)}")
    return ""

def _normalize_items(raw):
    """Accepts:
       - {"items":[...]}
       - [...]
       - {...}  (single object)
    Returns list of normalized dicts.
    """
    if isinstance(raw, dict) and "items" in raw:
        seq = raw["items"]
    elif isinstance(raw, list):
        seq = raw
    elif isinstance(raw, dict):
        seq = [raw]
    else:
        seq = []

    normed = []
    for it in seq:
        normed.append({
            "uid": it.get("uid"),  # may be int or str
            "title": (it.get("title") or "").strip(),
            "subtitle": (it.get("subtitle") or "").strip(),
            "iconSrc": (it.get("iconSrc") or "").strip(),
            "arg": (it.get("arg") or "").strip(),
            "rating": it.get("rating", None),
            "platforms": (it.get("platforms") or "").strip(),
        })
    return normed

def load_apps():
    """Load apps using the API module with fallback mechanisms"""
    try:
        utils.log_info("Loading apps data")
        data = api.get_apps_data()
        apps = _normalize_items(data)
        utils.log_info(f"Successfully loaded {len(apps)} apps")
        return apps
    except Exception as e:
        utils.log_error(f"Failed to load apps: {str(e)}")
        return [{
            "uid": None,
            "title": "Error loading apps",
            "subtitle": f"{type(e).__name__}: {e}",
            "iconSrc": "",
            "arg": "",
            "rating": None,
            "platforms": "",
        }]

# Keep your existing load_items function as a fallback if needed
def load_items(json_path: str):
    try:
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return _normalize_items(data)
    except Exception as e:
        utils.log_error(f"Failed to load items from {json_path}: {str(e)}")
        return [{
            "uid": None,
            "title": "Error loading JSON",
            "subtitle": f"{type(e).__name__}: {e}",
            "iconSrc": "",
            "arg": "",
            "rating": None,
            "platforms": "",
        }]

def query_text():
    # argv
    if len(sys.argv) > 1:
        return " ".join(sys.argv[1:]).strip()
    # env fallbacks
    for key in ("alfred_query", "query"):
        v = os.environ.get(key)
        if v:
            return v.strip()
    # stdin fallback
    try:
        if not sys.stdin.isatty():
            data = sys.stdin.read().strip()
            if data:
                return data
    except Exception:
        pass
    return ""

def match(item, q):
    if not q:
        return True
    hay = f"{item.get('title','')} {item.get('subtitle','')}".lower()
    return all(part in hay for part in q.lower().split())

def build_mods(arg_url, rating, platforms, uid):
    rating_txt = f"Rating: {rating}/100" if isinstance(rating, (int, float)) else "Rating: N/A"
    platforms_txt = f"Platforms: {platforms}" if platforms else "Platforms: N/A"

    mods = {
        # Alt → show rating (same URL)
        "alt": {
            "valid": True,
            "arg": arg_url,
            "subtitle": rating_txt
        },
        # Cmd → show platforms (same URL)
        "cmd": {
            "valid": True,
            "arg": arg_url,
            "subtitle": platforms_txt
        },
        # Cmd+Alt → show both (same URL)
        "cmd+alt": {
            "valid": True,
            "arg": arg_url,
            "subtitle": f"{rating_txt} · {platforms_txt}"
        }
    }

    # Shift → open Setapp deep link using uid
    if uid is not None and str(uid).strip():
        mods["shift"] = {
            "valid": True,
            "arg": f"setapp://launch/{uid}",
            "subtitle": f"Open SetApp DeepLink | setapp://launch/{uid} where (uid {uid})"
        }

    return mods

# ---- Main -------------------------------------------------------------------

def main():
    try:
        q = query_text()
        utils.log_info(f"Query: '{q}'")

        # Use the new load_apps function instead of load_items
        items = load_apps()
        cache_dir = alfred_cache_dir()

        alfred_items = []

        for idx, it in enumerate(items):
            if not match(it, q):
                continue

            icon_path = download_icon(it.get("iconSrc", ""), cache_dir)
            rating = it.get("rating")
            platforms = it.get("platforms", "")
            uid_val = it.get("uid")
            base_subtitle = it.get("subtitle") or ""
            if not base_subtitle:
                parts = []
                if rating is not None:
                    parts.append(f"Rating: {rating}/100")
                if platforms:
                    parts.append(f"Platforms: {platforms}")
                base_subtitle = " · ".join(parts) if parts else ""

            # Prefer provided uid; otherwise stable fallback
            alfred_uid = f"app-{uid_val}" if uid_val is not None else f"app-{idx}"

            item_obj = {
                "uid": str(alfred_uid),
                "title": it.get("title") or "(Untitled)",
                "subtitle": base_subtitle,
                "arg": it.get("arg") or "",
                "icon": {"path": icon_path} if icon_path else {},
                "quicklookurl": it.get("arg") or "",
                "mods": build_mods(it.get("arg") or "", rating, platforms, uid_val),
                # Let Alfred filter if you enable "Alfred filters results" in the node
                "match": " ".join([
                    it.get("title", ""),
                    it.get("subtitle", ""),
                    str(rating or ""),
                    platforms or ""
                ]).strip()
            }

            if not item_obj["arg"]:
                item_obj["valid"] = False
                item_obj["subtitle"] = (item_obj["subtitle"] + "  •  (No URL provided)").strip()

            alfred_items.append(item_obj)

        if not alfred_items:
            alfred_items = [{
                "title": "No matches",
                "subtitle": "Try a different search.",
                "valid": False
            }]

        utils.log_info(f"Returning {len(alfred_items)} items to Alfred")
        print(json.dumps({"items": alfred_items}, ensure_ascii=False))

    except Exception as e:
        utils.log_error(f"Main execution failed: {str(e)}")
        # Return error to Alfred
        error_items = [{
            "title": "Workflow Error",
            "subtitle": f"An error occurred: {str(e)}",
            "valid": False
        }]
        print(json.dumps({"items": error_items}, ensure_ascii=False))

if __name__ == "__main__":
    main()