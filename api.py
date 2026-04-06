import requests
from datetime import datetime, timezone
from config import API_URL
from utils import current_slot_times


def get_current_price():
    """
    Fetch the Agile unit rate for the current 30-minute slot.
    Returns (price_inc_vat, valid_from, valid_to) or (None, None, None) on error.
    """
    try:
        period_from, period_to = current_slot_times()
        url = (
            f"{API_URL}"
            f"?period_from={period_from.strftime('%Y-%m-%dT%H:%MZ')}"
            f"&period_to={period_to.strftime('%Y-%m-%dT%H:%MZ')}"
        )
        r = requests.get(url, timeout=10)
        r.raise_for_status()
        results = r.json().get("results", [])

        if not results:
            print("No price data returned for current slot.")
            return None, None, None

        slot       = results[0]
        valid_from = datetime.fromisoformat(
            slot["valid_from"].replace("Z", "+00:00"))
        valid_to   = datetime.fromisoformat(
            slot["valid_to"].replace("Z", "+00:00"))
        return slot["value_inc_vat"], valid_from, valid_to

    except Exception as e:
        print(f"API error: {e}")
        return None, None, None
