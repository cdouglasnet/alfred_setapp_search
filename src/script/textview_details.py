#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import os
import sys
import hashlib
import re
from urllib.parse import urlparse

def alfred_cache_dir():
    """Get Alfred cache directory - same function as in main.py"""
    for key in ("alfred_workflow_cache", "ALFRED_WORKFLOW_CACHE",
                "alfred_workflow_data", "ALFRED_WORKFLOW_DATA"):
        p = os.environ.get(key)
        if p:
            os.makedirs(p, exist_ok=True)
            return p
    # Fallback to workflow directory
    workflow_dir = os.environ.get("alfred_workflow_dir", os.getcwd())
    p = os.path.join(workflow_dir, ".cache")
    os.makedirs(p, exist_ok=True)
    return p

def safe_filename_from_url(url: str) -> str:
    """Generate safe filename from URL - same function as in main.py"""
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

def get_cached_icon_path(icon_url: str) -> str:
    """Get the cached icon path if it exists"""
    if not icon_url or not re.match(r"^https?://", icon_url, re.I):
        return ""

    cache_dir = alfred_cache_dir()
    fname = safe_filename_from_url(icon_url)
    local_path = os.path.join(cache_dir, fname)

    # Return path if file exists and has content
    if os.path.exists(local_path) and os.path.getsize(local_path) > 0:
        return local_path
    return ""

def build_mods_info(arg_url, rating, platforms, uid):
    """Build modifier key information for display in TextView - adapted from main.py"""
    rating_txt = f"Rating: {rating}/100" if isinstance(rating, (int, float)) else "Rating: N/A"
    platforms_txt = f"Platforms: {platforms}" if platforms else "Platforms: N/A"

    mods_info = []

    # Enter → Open SetApp page
    if arg_url:
        mods_info.append("• **Enter**: Open SetApp page in browser")
        mods_info.append(f"  → {arg_url}")

    # Alt → Show rating
    mods_info.append(f"• **⌥ (Option)**: Show rating information")
    mods_info.append(f"  → {rating_txt}")

    # Cmd → Show platforms
    mods_info.append(f"• **⌘ (Command)**: Show platform information")
    mods_info.append(f"  → {platforms_txt}")

    # Cmd+Alt → Show both
    mods_info.append(f"• **⌘⌥ (Cmd+Option)**: Show both rating and platforms")
    mods_info.append(f"  → {rating_txt} · {platforms_txt}")

    # Shift → Open SetApp deep link
    if uid is not None and str(uid).strip():
        mods_info.append(f"• **⇧ (Shift)**: Launch via SetApp deep link")
        mods_info.append(f"  → setapp://launch/{uid}")

    return mods_info

def get_app_details_textview():
    """
    Generate Alfred TextView JSON response with detailed app information
    Uses environment variables set by the main script
    """

    # Get variables from environment (set by Alfred workflow)
    uid = os.environ.get('setapp_uid', '')
    title = os.environ.get('setapp_title', '')
    subtitle = os.environ.get('setapp_subtitle', '')
    icon_src = os.environ.get('setapp_iconSrc', '')
    arg_url = os.environ.get('setapp_arg', '')
    rating = os.environ.get('setapp_rating', '')
    platforms = os.environ.get('setapp_platforms', '')
    status_text = os.environ.get('setapp_status', '')
    ai_text = os.environ.get('setapp_ai', '')
    deeplink = os.environ.get('setapp_deeplink', '')

    # Build the detailed response text
    response_lines = []

    # App title with cached icon using proper markdown format for Alfred
    if title:
        cached_icon_path = get_cached_icon_path(icon_src)
        if cached_icon_path:
            # Use markdown image format that Alfred TextView supports
            response_lines.append(f"![App Icon]({cached_icon_path})")
            response_lines.append("")
            response_lines.append(f"# {title}")
        else:
            response_lines.append(f"# 📱 {title}")
        response_lines.append("\n")
        response_lines.append("=" * (len(title) + 6))
        response_lines.append("\n")

    if subtitle:
        response_lines.append(f"📝 {subtitle}")
        response_lines.append("")

    # App details
    if rating:
        try:
            rating_num = int(rating)
            stars = "⭐" * (rating_num // 20)  # Convert to 5-star scale
            response_lines.append(f"Rating: {rating}/100 {stars}")
        except ValueError:
            response_lines.append(f"Rating: {rating}")

    response_lines.append("\n")

    if platforms:
        response_lines.append(f"💻 Platforms: {platforms}")

    if ai_text:
        response_lines.append(f"🤖 AI: {ai_text}")

    if status_text:
        response_lines.append(f"📌 Status: {status_text}")

    response_lines.append("")

    # URLs and links
    if arg_url:
        response_lines.append(f"🌐 SetApp Page: {arg_url}")
        response_lines.append("\n")

    if deeplink:
        response_lines.append(f"🚀 Deep Link: {deeplink}")
        response_lines.append("\n")

    # if icon_src:
    #     response_lines.append(f"🖼️  Icon URL: {icon_src}")
    #     response_lines.append("\n")

    if uid:
        response_lines.append(f"🔢 App ID: {uid}")
        response_lines.append("\n")

    # Add modifier key information
    response_lines.append("# 🔑 Modifier Key Actions:\n")
    mods_info = build_mods_info(arg_url, rating, platforms, uid)
    response_lines.extend(mods_info)

    # Add usage instructions
    response_lines.append("")
    response_lines.append("# 📋 Actions:\n")
    response_lines.append("### Enter: Open SetApp page in browser\n")
    response_lines.append("### ⇧ + Enter: Launch app via SetApp deep link\n")
    response_lines.append("### ⌘ + Enter: Start Over\n")

    response_text = "\n".join(response_lines)

    # Create the Alfred TextView JSON response
    textview_response = {
        "variables": {
            "setapp_uid": uid,
            "setapp_title": title,
            "setapp_subtitle": subtitle,
            "setapp_iconSrc": icon_src,
            "setapp_arg": arg_url,
            "setapp_rating": rating,
            "setapp_platforms": platforms,
            "setapp_status": status_text,
            "setapp_ai": ai_text,
            "setapp_deeplink": deeplink
        },
        "rerun": 0,  # Don't auto-refresh
        "response": response_text,
        "footer": f"SetApp App Details - {title}" if title else "SetApp App Details",
        "behaviour": {
            "response": "replace",  # Replace content instead of append
            "scroll": "start",      # Scroll to top
            "inputfield": "clear"   # Clear input field
        }
    }

    # Add image to response if cached icon exists
    cached_icon_path = get_cached_icon_path(icon_src)
    if cached_icon_path:
        textview_response["image"] = {
            "path": cached_icon_path
        }

    return textview_response

def main():
    """Main function to output TextView JSON"""
    try:
        result = get_app_details_textview()
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except Exception as e:
        # Error response for Alfred
        error_response = {
            "variables": {},
            "rerun": 0,
            "response": f"Error generating app details:\n{str(e)}",
            "footer": "Error - SetApp App Details",
            "behaviour": {
                "response": "replace",
                "scroll": "start",
                "inputfield": "clear"
            }
        }
        print(json.dumps(error_response, ensure_ascii=False, indent=2))

if __name__ == "__main__":
    main()
