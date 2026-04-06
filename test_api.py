"""
Standalone test — fetches and prints the current Agile price slot.
Run with: python3 test_api.py
"""
import requests
from datetime import datetime, timezone, timedelta

REGION  = "C"             # Change to your DNO region code
PRODUCT = "AGILE-24-10-01"
TARIFF  = f"E-1R-{PRODUCT}-{REGION}"


def get_current_slot_url():
    now         = datetime.now(timezone.utc)
    period_from = now.replace(
        minute=0 if now.minute < 30 else 30,
        second=0,
        microsecond=0
    )
    period_to   = period_from + timedelta(minutes=30)
    return (
        f"https://api.octopus.energy/v1/products/{PRODUCT}/"
        f"electricity-tariffs/{TARIFF}/standard-unit-rates/"
        f"?period_from={period_from.strftime('%Y-%m-%dT%H:%MZ')}"
        f"&period_to={period_to.strftime('%Y-%m-%dT%H:%MZ')}"
    )


def test():
    url = get_current_slot_url()
    print(f"Fetching from:\n{url}\n")

    r = requests.get(url, timeout=10)
    r.raise_for_status()
    results = r.json().get("results", [])

    if not results:
        print("No price found for current slot — prices may not be published yet.")
        return

    slot       = results[0]
    valid_from = datetime.fromisoformat(
        slot["valid_from"].replace("Z", "+00:00"))
    valid_to   = datetime.fromisoformat(
        slot["valid_to"].replace("Z", "+00:00"))
    price      = slot["value_inc_vat"]

    print(f"Current slot : {valid_from.astimezone().strftime('%a %d %b %H:%M')} "
          f"- {valid_to.astimezone().strftime('%H:%M')}")
    print(f"Price        : {price:.2f}p per kWh")


if __name__ == "__main__":
    test()
