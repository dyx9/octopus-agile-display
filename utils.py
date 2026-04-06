import socket
from datetime import datetime, timezone, timedelta


def get_ip():
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "No network"


def now_local():
    return datetime.now()


def now_utc():
    return datetime.now(timezone.utc)


def current_slot_times():
    """Return (period_from, period_to) for the current 30-min slot in UTC."""
    now         = datetime.now(timezone.utc)
    period_from = now.replace(
        minute=0 if now.minute < 30 else 30,
        second=0,
        microsecond=0
    )
    period_to   = period_from + timedelta(minutes=30)
    return period_from, period_to
