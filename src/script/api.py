# src/script/api.py
import json
import os
import time
import requests
from datetime import datetime, timedelta
import utils

CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "cache")
CACHE_FILE = os.path.join(CACHE_DIR, "apps_cache.json")
CACHE_EXPIRY = 86400  # 24 hours in seconds
FALLBACK_DATA = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "apps.json")

def ensure_cache_dir():
    """Ensure the cache directory exists"""
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)

def get_apps_data():
    """Get apps data with a cascading fallback strategy:
    1. Try to fetch from SetApp API/website
    2. If that fails, try to use cached data (if not expired)
    3. If that fails, use embedded fallback data
    """
    # First try: Fetch fresh data
    try:
        apps = fetch_apps_from_api()
        # Save to cache
        ensure_cache_dir()
        with open(CACHE_FILE, 'w') as f:
            json.dump({
                'timestamp': time.time(),
                'data': apps
            }, f)
        return apps
    except Exception as e:
        utils.log_error(f"API fetch failed: {str(e)}")

    # Second try: Use cache if not expired
    try:
        if os.path.exists(CACHE_FILE):
            with open(CACHE_FILE, 'r') as f:
                cache = json.load(f)

            # Check if cache is still valid
            if time.time() - cache['timestamp'] < CACHE_EXPIRY:
                return cache['data']
            else:
                utils.log_info("Cache expired")
    except Exception as e:
        utils.log_error(f"Cache read failed: {str(e)}")

    # Last resort: Use embedded data
    try:
        with open(FALLBACK_DATA, 'r') as f:
            return json.load(f)
    except Exception as e:
        utils.log_error(f"Fallback data read failed: {str(e)}")
        return []

def fetch_apps_from_api():
    """Fetch apps data from SetApp API or website"""
    # TODO: Implement actual API call or web scraping
    # For now, this is a placeholder
    raise NotImplementedError("API fetch not yet implemented")