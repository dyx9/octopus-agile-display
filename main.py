import time
from datetime import datetime, timedelta, timezone

from config import (
    EVENING_REFRESH_END_HOUR,
    EVENING_REFRESH_INTERVAL,
    EVENING_REFRESH_START_HOUR,
)
from api import (
    get_prices_for_period,
    load_price_cache,
    save_daily_prices_csv,
    save_price_cache,
)
from utils import get_ip, current_slot_times, now_local, now_utc, seconds_until_next_slot_boundary
from display import draw_image, save_preview
from screen import init_screen, update_screen


def main():
    print("Starting Agile display...")
    epd = init_screen()
    slots, last_fetch_utc = load_price_cache()

    def index_slots(items):
        return {slot["valid_from"]: slot for slot in items}

    def refresh_cache(reason):
        nonlocal slots, last_fetch_utc

        utc_now = now_utc()
        local_now = now_local()
        local_midnight = local_now.replace(hour=0, minute=0, second=0, microsecond=0)

        period_from = local_midnight.astimezone(timezone.utc)
        period_to = (local_midnight + timedelta(days=2)).astimezone(timezone.utc)
        fetched = get_prices_for_period(period_from, period_to)

        if fetched:
            merged = index_slots(slots)
            merged.update(index_slots(fetched))

            # Keep only this and next day (local) to avoid unbounded cache growth.
            window_start = period_from
            window_end = period_to
            slots = [
                slot
                for slot in merged.values()
                if window_start <= slot["valid_from"] < window_end
            ]
            last_fetch_utc = utc_now
            save_price_cache(slots, last_fetch_utc)
            print(f"Fetched {len(fetched)} slots ({reason}).")
        else:
            print(f"Price fetch returned no data ({reason}); using cached values.")

    def needs_evening_refresh(local_now):
        if not (EVENING_REFRESH_START_HOUR <= local_now.hour < EVENING_REFRESH_END_HOUR):
            return False
        if last_fetch_utc is None:
            return True
        age = (now_utc() - last_fetch_utc).total_seconds()
        return age >= EVENING_REFRESH_INTERVAL

    def get_slot_price(slot_from):
        indexed = index_slots(slots)
        slot = indexed.get(slot_from)
        if not slot:
            return None, slot_from, slot_from + timedelta(minutes=30)
        return slot["price"], slot["valid_from"], slot["valid_to"]

    def day_slots_for_local_date(local_date):
        day_slots = []
        for slot in slots:
            if slot["valid_from"].astimezone().date() == local_date:
                day_slots.append(slot)
        return sorted(day_slots, key=lambda slot: slot["valid_from"])

    refresh_cache("startup")

    while True:
        local_now = now_local()
        slot_from, _ = current_slot_times()

        if needs_evening_refresh(local_now):
            refresh_cache("evening refresh window")

        price, valid_from, valid_to = get_slot_price(slot_from)

        if price is None:
            refresh_cache("missing current slot")
            price, valid_from, valid_to = get_slot_price(slot_from)

        day_slots = day_slots_for_local_date(local_now.date())
        save_daily_prices_csv(day_slots)

        ip = get_ip()

        print(f"Price: {price}p | Slot: {valid_from} - {valid_to} | IP: {ip}")

        image = draw_image(price, valid_from, valid_to, ip, day_slots=day_slots)
        save_preview(image)
        update_screen(epd, image)

        sleep_seconds = seconds_until_next_slot_boundary()
        print(f"Sleeping {sleep_seconds // 60} minutes...\n")
        time.sleep(sleep_seconds)


if __name__ == "__main__":
    main()
