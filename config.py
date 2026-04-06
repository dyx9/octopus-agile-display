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

PREVIEW_PATH = "preview.png"

REFRESH_INTERVAL = 1800   # seconds (30 minutes)
