import time
from config import REFRESH_INTERVAL
from api import get_current_price
from utils import get_ip
from display import draw_image, save_preview
from screen import init_screen, update_screen


def main():
    print("Starting Agile display...")
    epd = init_screen()

    while True:
        price, valid_from, valid_to = get_current_price()
        ip = get_ip()

        print(f"Price: {price}p | Slot: {valid_from} - {valid_to} | IP: {ip}")

        image = draw_image(price, valid_from, valid_to, ip)
        save_preview(image)
        update_screen(epd, image)

        print(f"Sleeping {REFRESH_INTERVAL // 60} minutes...\n")
        time.sleep(REFRESH_INTERVAL)


if __name__ == "__main__":
    main()
