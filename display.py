from PIL import Image, ImageDraw, ImageFont
from config import SCREEN_W, SCREEN_H, PREVIEW_PATH
from utils import now_local


def draw_image(price, valid_from, valid_to, ip):
    """
    Draw the display image and return a PIL Image object.
    Uses default PIL fonts for now — replace with ImageFont.truetype()
    once you have a TTF font file for better rendering.
    """
    image = Image.new("1", (SCREEN_W, SCREEN_H), 255)  # white background
    draw  = ImageDraw.Draw(image)

    font_large  = ImageFont.load_default()
    font_small  = ImageFont.load_default()

    now = now_local()

    # ── Title ──────────────────────────────────────────
    draw.text((10, 10), "Octopus Agile", fill=0, font=font_small)

    # ── Divider ────────────────────────────────────────
    draw.line([(0, 28), (SCREEN_W, 28)], fill=0, width=1)

    # ── Price ──────────────────────────────────────────
    price_text = f"{price:.1f}p" if price is not None else "N/A"
    draw.text((180, 95),  price_text, fill=0, anchor="mm", font=font_large)
    draw.text((180, 125), "per kWh",  fill=0, anchor="mm", font=font_small)

    # ── Time slot ──────────────────────────────────────
    if valid_from and valid_to:
        slot_str = (
            f"{valid_from.astimezone().strftime('%H:%M')}"
            f" - "
            f"{valid_to.astimezone().strftime('%H:%M')}"
        )
        draw.text((180, 150), slot_str, fill=0, anchor="mm", font=font_small)

    # ── Divider ────────────────────────────────────────
    draw.line([(0, 170), (SCREEN_W, 170)], fill=0, width=1)

    # ── Date, update time, IP ──────────────────────────
    draw.text((10, 178), now.strftime("%a %d %b %Y"),    fill=0, font=font_small)
    draw.text((10, 193), now.strftime("Updated: %H:%M"), fill=0, font=font_small)
    draw.text((10, 208), f"IP: {ip}",                    fill=0, font=font_small)

    return image


def save_preview(image):
    image.save(PREVIEW_PATH)
    print(f"Preview saved to {PREVIEW_PATH}")
