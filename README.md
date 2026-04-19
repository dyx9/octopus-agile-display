# Octopus Agile E-Ink Display for Raspberry Pi

Small Raspberry Pi project that shows Octopus Agile electricity prices on a Waveshare 3.52 inch red/black/white e-ink screen.

## 1. Introduction

What it does:

- Fetches half-hour Agile prices from the Octopus API.
- Shows current price and a daily histogram on the e-ink display.
- Caches data locally so it can continue displaying during short API/network issues.
- Supports `--simulate` mode for development without hardware.

Runtime artifacts:

- `artifacts/preview.png`
- `artifacts/price_cache.json`
- `artifacts/daily_prices.csv`

## 2. Requirements

### Hardware

- Raspberry Pi (tested target: Raspberry Pi 3 Model B)
- Waveshare 3.52 inch e-Paper HAT (B), 360x240, red/black/white

### Software

- Linux on Raspberry Pi for real hardware mode
- Python 3.13+
- `uv` for Python environment and dependency management
- System packages: `git`, `wget`, `unzip`
- SPI enabled on the Pi

### Install steps

#### Step 1: Enable SPI

```bash
sudo raspi-config
# Interface Options -> SPI -> Yes
```

#### Step 2: Install system packages

```bash
sudo apt-get update
sudo apt-get install -y git wget unzip
```

#### Step 3: Install uv

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Open a new shell after installation.

#### Step 4: Install project dependencies with uv

From this repository root:

```bash
uv sync
```

Notes:

- Python dependencies are declared in `pyproject.toml`.
- `spidev` is Linux-only in project dependencies, so it installs on Raspberry Pi and is skipped on macOS.

#### Step 5: Install Waveshare driver package (B variant)

```bash
cd ~
wget https://files.waveshare.com/wiki/3.52inch%20e-Paper%20HAT%20(B)/3in52_e-Paper_B.zip
unzip 3in52_e-Paper_B.zip
```

Default library path expected by this project:

```text
~/3in52_e-Paper_B/RaspberryPi_JetsonNano/python/lib
```

If your path differs, update `WAVESHARE_LIB_PATH` in `config.py`, or set the `WAVESHARE_LIB_PATH` environment variable.

## 3. How To Use

### Configure region

Edit `config.py` and set `REGION` to your DNO region code:

- C = London
- D = South East
- E = East Midlands
- F = Yorkshire
- G = North West
- K = South West
- P = Scotland

### Quick API sanity test (no screen required)

```bash
uv run python test_api.py
```

### Preview mode (development machine, no hardware)

```bash
uv run python main.py --simulate
```

This writes preview output to `artifacts/preview.png` every cycle.

### Run on Raspberry Pi (foreground)

```bash
uv run python main.py
```

### Run on Raspberry Pi in background with nohup

Use this if you want the program to keep running after you close SSH/session:

```bash
cd /home/pi/agile-display
nohup /home/pi/.local/bin/uv run python main.py > artifacts/nohup.log 2>&1 &
echo $! > artifacts/agile-display.pid
```

Useful process management commands:

```bash
tail -f /home/pi/agile-display/artifacts/nohup.log
kill "$(cat /home/pi/agile-display/artifacts/agile-display.pid)"
```

### Optional: auto-start on boot

Auto-start is optional. If you prefer manual start, skip this section.

```bash
crontab -e
# Add:
@reboot sleep 30 && cd /home/pi/agile-display && /home/pi/.local/bin/uv run python main.py >> artifacts/boot.log 2>&1
```

## Project Files

| File        | Purpose                      |
| ----------- | ---------------------------- |
| config.py   | Settings and paths           |
| api.py      | Octopus API and cache I/O    |
| display.py  | Image rendering              |
| screen.py   | Waveshare hardware interface |
| utils.py    | Time and network helpers     |
| main.py     | Main loop and scheduling     |
| test_api.py | API smoke test               |
