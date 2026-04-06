import json
from datetime import datetime, timezone
from pathlib import Path

import requests

from config import API_URL, PRICE_CACHE_PATH


def _slot_from_api_entry(entry):
    valid_from = datetime.fromisoformat(entry["valid_from"].replace("Z", "+00:00"))
    valid_to = datetime.fromisoformat(entry["valid_to"].replace("Z", "+00:00"))
    return {
        "price": entry["value_inc_vat"],
        "valid_from": valid_from,
        "valid_to": valid_to,
    }


def _slot_sort_key(slot):
    return slot["valid_from"]


def get_prices_for_period(period_from, period_to):
    """Fetch Agile unit rates for a UTC period and return normalized slot dicts."""
    try:
        params = {
            "period_from": period_from.strftime("%Y-%m-%dT%H:%MZ"),
            "period_to": period_to.strftime("%Y-%m-%dT%H:%MZ"),
            "page_size": 200,
        }
        response = requests.get(API_URL, params=params, timeout=10)
        response.raise_for_status()

        results = response.json().get("results", [])
        slots = [_slot_from_api_entry(entry) for entry in results]
        slots.sort(key=_slot_sort_key)
        return slots
    except Exception as error:
        print(f"API error: {error}")
        return []


def load_price_cache(cache_path=PRICE_CACHE_PATH):
    """Load cache JSON from disk and return (slots, last_fetch_utc)."""
    path = Path(cache_path)
    if not path.exists():
        return [], None

    try:
        payload = json.loads(path.read_text())
        slots = []
        for entry in payload.get("slots", []):
            slots.append(
                {
                    "price": entry["price"],
                    "valid_from": datetime.fromisoformat(entry["valid_from"]),
                    "valid_to": datetime.fromisoformat(entry["valid_to"]),
                }
            )

        last_fetch_raw = payload.get("last_fetch_utc")
        last_fetch_utc = datetime.fromisoformat(last_fetch_raw) if last_fetch_raw else None
        return slots, last_fetch_utc
    except Exception as error:
        print(f"Cache load error: {error}")
        return [], None


def save_price_cache(slots, last_fetch_utc, cache_path=PRICE_CACHE_PATH):
    """Persist cache JSON to disk."""
    path = Path(cache_path)
    serializable = {
        "last_fetch_utc": last_fetch_utc.isoformat() if last_fetch_utc else None,
        "slots": [
            {
                "price": slot["price"],
                "valid_from": slot["valid_from"].isoformat(),
                "valid_to": slot["valid_to"].isoformat(),
            }
            for slot in sorted(slots, key=_slot_sort_key)
        ],
    }

    path.write_text(json.dumps(serializable, indent=2))
