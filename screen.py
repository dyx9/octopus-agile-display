# ─── Waveshare e-ink hardware interface ───────────────
# Uncomment all hardware lines when screen is physically connected.
# Until then the script runs in preview mode (saves a PNG instead).

# import sys, os
# sys.path.append(os.path.expanduser(
#     "~/e-Paper/RaspberryPi_JetsonNano/python/lib"))
# from waveshare_epd import epd3in52


def init_screen():
    # epd = epd3in52.EPD()
    # epd.init()
    # return epd
    print("Screen: running in preview mode (no hardware attached)")
    return None


def update_screen(epd, image):
    if epd is None:
        return  # preview mode — image saved as PNG instead
    # epd.display(epd.getbuffer(image))


def clear_screen(epd):
    if epd is None:
        return
    # epd.Clear()
