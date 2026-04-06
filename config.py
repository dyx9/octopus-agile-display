# ─── All settings in one place ────────────────────────
REGION    = "C"           # Change to your DNO region code
                          # C=London, D=South East, E=East Midlands,
                          # F=Yorkshire, G=North West, P=Scotland, K=South West
PRODUCT   = "AGILE-24-10-01"
TARIFF    = f"E-1R-{PRODUCT}-{REGION}"
API_URL   = (
    f"https://api.octopus.energy/v1/products/{PRODUCT}/"
    f"electricity-tariffs/{TARIFF}/standard-unit-rates/"
)

SCREEN_W  = 360
SCREEN_H  = 240

PREVIEW_PATH = "artifacts/preview.png"

PRICE_CACHE_PATH = "artifacts/price_cache.json"

DAILY_PRICES_CSV_PATH = "artifacts/daily_prices.csv"

# Agile prices are typically published between 16:00 and 20:00 local time.
EVENING_REFRESH_START_HOUR = 16
EVENING_REFRESH_END_HOUR = 20
EVENING_REFRESH_INTERVAL = 900  # seconds (15 minutes)
