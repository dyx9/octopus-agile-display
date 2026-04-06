# Agile Display

Raspberry Pi e-ink display for Octopus Agile tariff prices.

## Hardware

- Raspberry Pi 3 Model B
- Waveshare 3.52" e-Paper HAT (360x240) — red/black/white version

## Setup

Requires Python 3.13+ (see `pyproject.toml`).

### 1. Enable SPI

```bash
sudo raspi-config
# Interface Options → SPI → Yes
```

### 2. Install dependencies

```bash
sudo apt install python3-pip python3-pillow git -y
pip3 install requests --break-system-packages
```

### 3. Install Waveshare library

```bash
cd ~
git clone https://github.com/waveshare/e-Paper.git
```

### 4. Set your region

Edit `config.py` and set `REGION` to your DNO region code:

- C = London
- D = South East
- E = East Midlands
- F = Yorkshire
- G = North West
- K = South West
- P = Scotland

### 5. Test API (no screen needed)

```bash
python3 test_api.py
```

### 6. Run in preview mode (no screen needed)

```bash
python3 main.py
# Saves artifacts/preview.png each cycle
```

Runtime files are written to `artifacts/`:

- `artifacts/preview.png`
- `artifacts/price_cache.json`

### 7. When screen arrives

Uncomment the hardware lines in `screen.py`.

## Files

| File        | Purpose                      |
| ----------- | ---------------------------- |
| config.py   | All settings                 |
| api.py      | Octopus API fetching         |
| display.py  | Image drawing                |
| screen.py   | Waveshare hardware interface |
| utils.py    | IP address, time helpers     |
| main.py     | Entry point, main loop       |
| test_api.py | Standalone API test          |

## Auto-start on boot

```bash
crontab -e
# Add:
@reboot sleep 30 && python3 /home/pi/agile-display/main.py &
```
