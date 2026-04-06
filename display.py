from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

from config import SCREEN_W, SCREEN_H, PREVIEW_PATH
from utils import now_local


def _draw_histogram(draw, slots, current_slot_from, x0, y0, width, height):
    if not slots:
        draw.text((x0 + 4, y0 + 4), "No day data", fill=0)
        return

    sorted_slots = sorted(slots, key=lambda slot: slot["valid_from"])
    prices = [slot["price"] for slot in sorted_slots]
    min_price = min(min(prices), 0)
    max_price = max(max(prices), 0)

    # Avoid divide-by-zero if all values are identical.
    if max_price == min_price:
        max_price = min_price + 1

    zero_ratio = (0 - min_price) / (max_price - min_price)
    zero_y = y0 + height - int(zero_ratio * height)
    draw.line([(x0, zero_y), (x0 + width, zero_y)], fill=0, width=1)

    count = len(sorted_slots)
    gap = 2  # 2px gap between bars for clear separation
    bar_w = max(1, (width - count * gap) // max(1, count))

    for index, slot in enumerate(sorted_slots):
        bar_left = x0 + index * (bar_w + gap)
        bar_right = bar_left + bar_w

        # Skip if bar exceeds bounds
        if bar_left >= x0 + width:
            break

        value = slot["price"]
        value_ratio = (value - min_price) / (max_price - min_price)
        value_y = y0 + height - int(value_ratio * height)

        top = min(zero_y, value_y)
        bottom = max(zero_y, value_y)

        if bar_right > bar_left and bottom > top:
            fill = 0 if value >= 0 else 255
            draw.rectangle([(bar_left, top), (bar_right, bottom)], outline=0, fill=fill)

        if current_slot_from and slot["valid_from"] == current_slot_from:
            draw.rectangle([(bar_left, y0), (bar_right, y0 + height)], outline=0, width=1)


def draw_image(price, valid_from, valid_to, ip, day_slots=None):
    """
    Draw the display image and return a PIL Image object.
    Uses default PIL fonts for now — replace with ImageFont.truetype()
    once you have a TTF font file for better rendering.
    """
    image = Image.new("1", (SCREEN_W, SCREEN_H), 255)  # white background
    draw  = ImageDraw.Draw(image)

    font_small = ImageFont.load_default()
    
    # Load a large TrueType font for the price
    # Try Linux paths first (Raspberry Pi target), then macOS (for dev preview)
    font_large = None
    font_paths = [
        "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",  # Linux/Raspberry Pi
        "/System/Library/Fonts/Helvetica.ttc",  # macOS
        "/Library/Fonts/Arial.ttf",  # macOS alternative
    ]
    
    for font_path in font_paths:
        try:
            font_large = ImageFont.truetype(font_path, 48)
            break
        except (OSError, IOError):
            continue
    
    # Fallback to default if no font found
    if font_large is None:
        font_large = ImageFont.load_default()

    now = now_local()

    # ── Large current price ────────────────────────────
    price_text = f"{price:.1f}p" if price is not None else "N/A"
    draw.text((10, 8), price_text, fill=0, font=font_large)
    draw.text((300, 28), "per kWh", fill=0, font=font_small)

    # ── Daily histogram (48 half-hour slots) ───────────
    _draw_histogram(
        draw=draw,
        slots=day_slots or [],
        current_slot_from=valid_from,
        x0=10,
        y0=75,
        width=SCREEN_W - 20,
        height=100,
    )

    # ── Divider ────────────────────────────────────────
    draw.line([(0, 183), (SCREEN_W, 183)], fill=0, width=1)

    # ── Date, update time, IP ──────────────────────────
    draw.text((10, 191), now.strftime("%a %d %b %Y"),    fill=0, font=font_small)
    draw.text((10, 203), now.strftime("Updated: %H:%M"), fill=0, font=font_small)
    draw.text((10, 215), f"IP: {ip}",                    fill=0, font=font_small)

    return image


def save_preview(image):
    Path(PREVIEW_PATH).parent.mkdir(parents=True, exist_ok=True)
    image.save(PREVIEW_PATH)
    print(f"Preview saved to {PREVIEW_PATH}")
