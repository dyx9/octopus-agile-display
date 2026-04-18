import os
import sys


WAVESHARE_LIB_PATH = os.path.expanduser("~/3in52_e-Paper_B/RaspberryPi_JetsonNano/python/lib")


def _load_driver():
    if WAVESHARE_LIB_PATH not in sys.path:
        sys.path.append(WAVESHARE_LIB_PATH)
    try:
        from waveshare_epd import epd3in52b  # pyright: ignore[reportMissingImports]
    except ImportError as exc:
        raise RuntimeError(
            "Waveshare driver not available. Use --simulate on dev machines, "
            "or install the driver on the Raspberry Pi."
        ) from exc

    return epd3in52b


def init_screen(simulate=False):
    if simulate:
        print("Screen: running in simulation mode (preview only)")
        return None

    epd3in52b = _load_driver()
    epd = epd3in52b.EPD()
    epd.init()
    print("screen init")
    return epd


def update_screen(epd, image):
    if epd is None:
        return
    epd.init()

    image = image.rotate(180)
    # Black layer: anything that isn't red (convert to 1-bit)
    black_image = image.copy()
    pixels = black_image.load()
    for y in range(black_image.height):
        for x in range(black_image.width):
            r, g, b = pixels[x, y]
            # If it's a red pixel, make it white on the black layer
            if r > 128 and g < 128 and b < 128:
                pixels[x, y] = (255, 255, 255)
    black_mono = black_image.convert('1')

    # Red layer: only red pixels
    red_image = image.copy()
    pixels = red_image.load()
    for y in range(red_image.height):
        for x in range(red_image.width):
            r, g, b = pixels[x, y]
            # Red pixel → black on red layer; everything else → white
            pixels[x, y] = (0, 0, 0) if (r > 128 and g < 128 and b < 128) else (255, 255, 255)
    red_mono = red_image.convert('1')

    epd.display(epd.getbuffer(black_mono), epd.getbuffer(red_mono))
    epd.TurnOnDisplay()
    print("screen updated")

def clear_screen(epd):
    if epd is None:
        return
    epd.Clear()
    print("screen cleared")
