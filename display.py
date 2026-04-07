from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

from config import SCREEN_W, SCREEN_H, PREVIEW_PATH
from utils import now_local


def _draw_histogram(draw, slots, current_slot_from, x0, y0, width, height):
    # ── Histogram styling constants ─────────────────────
    BAR_GAP = 2
    BOTTOM_MARGIN = 15  # Padding at bottom to keep bars away from footer
    COLOR_BLACK = (0, 0, 0)
    COLOR_WHITE = (255, 255, 255)
    COLOR_RED = (255, 0, 0)

    if not slots:
        draw.text((x0 + 4, y0 + 4), "No day data", fill=COLOR_BLACK)
        return

    sorted_slots = sorted(slots, key=lambda slot: slot["valid_from"])
    prices = [slot["price"] for slot in sorted_slots]
    min_price = min(min(prices), 0)
    max_price = max(max(prices), 0)

    # Avoid divide-by-zero if all values are identical.
    if max_price == min_price:
        max_price = min_price + 1

    effective_height = height - BOTTOM_MARGIN
    zero_ratio = (0 - min_price) / (max_price - min_price)
    zero_y = y0 + effective_height - int(zero_ratio * effective_height)

    count = len(sorted_slots)
    bar_w = max(1, (width - count * BAR_GAP) // max(1, count))

    # ── Draw bars ─────────────────────────────────────
    for index, slot in enumerate(sorted_slots):
        bar_left = x0 + index * (bar_w + BAR_GAP)
        bar_right = bar_left + bar_w

        # Skip if bar exceeds bounds
        if bar_left >= x0 + width:
            break

        value = slot["price"]
        value_ratio = (value - min_price) / (max_price - min_price)
        value_y = y0 + effective_height - int(value_ratio * effective_height)

        top = min(zero_y, value_y)
        bottom = max(zero_y, value_y)

        is_current = current_slot_from and slot["valid_from"] == current_slot_from

        if bar_right > bar_left and bottom > top:
            # Use red for current slot, black for all values (positive and negative)
            fill = COLOR_RED if is_current else COLOR_BLACK
            draw.rectangle([(bar_left, top), (bar_right, bottom)], outline=None, fill=fill)

    # ── Draw time labels at bottom ──────────────────────
    font_small = ImageFont.load_default()
    label_hours = [6, 12, 18]
    label_slot_index = {}

    # Half-hour data has :00 and :30 entries; anchor labels to exact hour slots.
    for index, slot in enumerate(sorted_slots):
        slot_time_local = slot["valid_from"].astimezone()
        if (
            slot_time_local.hour in label_hours
            and slot_time_local.minute == 0
            and slot_time_local.hour not in label_slot_index
        ):
            label_slot_index[slot_time_local.hour] = index

    for label_hour in label_hours:
        index = label_slot_index.get(label_hour)
        if index is None:
            continue

        bar_left = x0 + index * (bar_w + BAR_GAP)
        label_text = str(label_hour)
        text_bbox = draw.textbbox((0, 0), label_text, font=font_small)
        text_w = text_bbox[2] - text_bbox[0]
        label_x = max(x0, min(bar_left, x0 + width - text_w))
        label_y = y0 + effective_height + 2
        draw.text((label_x, label_y), label_text, fill=COLOR_BLACK, font=font_small)


def draw_image(price, valid_from, valid_to, ip, day_slots=None):
    """
    Draw the display image and return a PIL Image object.
    Uses RGB mode for red/black/white e-ink display.
    """
    # ── Layout and styling constants ────────────────────
    PRICE_FONT_SIZE = 48
    FOOTER_FONT_SIZE = 12
    PRICE_POS = (10, 8)
    UNIT_POS = (300, 28)
    HISTOGRAM_X = 10
    HISTOGRAM_Y = 75
    HISTOGRAM_HEIGHT = 130
    FOOTER_Y = 220
    DIVIDER_Y = FOOTER_Y - 6
    FOOTER_LEFT_X = 10
    BAR_GAP = 2
    COLOR_BLACK = (0, 0, 0)
    COLOR_WHITE = (255, 255, 255)
    COLOR_RED = (255, 0, 0)

    image = Image.new("RGB", (SCREEN_W, SCREEN_H), COLOR_WHITE)
    draw  = ImageDraw.Draw(image)

    font_small = ImageFont.load_default()
    font_medium = None
    
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
            font_large = ImageFont.truetype(font_path, PRICE_FONT_SIZE)
            font_medium = ImageFont.truetype(font_path, FOOTER_FONT_SIZE)
            break
        except (OSError, IOError):
            continue
    
    # Fallback to default if no font found
    if font_large is None:
        font_large = ImageFont.load_default()
    if font_medium is None:
        font_medium = font_small

    now = now_local()

    # ── Large current price ────────────────────────────
    price_text = f"{price:.2f}p" if price is not None else "N/A"
    draw.text(PRICE_POS, price_text, fill=COLOR_BLACK, font=font_large)
    draw.text(UNIT_POS, "per kWh", fill=COLOR_BLACK, font=font_small)

    # ── Daily histogram (48 half-hour slots) ───────────
    _draw_histogram(
        draw=draw,
        slots=day_slots or [],
        current_slot_from=valid_from,
        x0=HISTOGRAM_X,
        y0=HISTOGRAM_Y,
        width=SCREEN_W - 20,
        height=HISTOGRAM_HEIGHT,
    )

    # ── Divider ────────────────────────────────────────
    draw.line([(0, DIVIDER_Y), (SCREEN_W, DIVIDER_Y)], fill=COLOR_BLACK, width=1)

    # ── Footer info ────────────────────────────────────
    updated_text = now.strftime("Updated: %H:%M %a %d %b")
    ip_text = f"IP: {ip}"
    ip_box = draw.textbbox((0, 0), ip_text, font=font_medium)
    ip_width = ip_box[2] - ip_box[0]
    draw.text((FOOTER_LEFT_X, FOOTER_Y), updated_text, fill=COLOR_BLACK, font=font_medium)
    draw.text((SCREEN_W - 10 - ip_width, FOOTER_Y), ip_text, fill=COLOR_BLACK, font=font_medium)

    return image


def save_preview(image):
    Path(PREVIEW_PATH).parent.mkdir(parents=True, exist_ok=True)
    image.save(PREVIEW_PATH)
    print(f"Preview saved to {PREVIEW_PATH}")
