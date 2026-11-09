#!/bin/bash
# Fetch Chicago weather from Open-Meteo (free, no key) into data/weather.json.
# This script is the only thing that should write to data/weather.json.
set -euo pipefail
cd "$(dirname "$0")/.."

URL="https://api.open-meteo.com/v1/forecast?latitude=41.88&longitude=-87.63\
&current=temperature_2m,weather_code,wind_speed_10m,precipitation\
&hourly=temperature_2m,relative_humidity_2m,precipitation_probability,weather_code,wind_speed_10m\
&daily=temperature_2m_max,temperature_2m_min,precipitation_probability_max,weather_code,sunrise,sunset\
&temperature_unit=fahrenheit&wind_speed_unit=mph&timezone=America%2FChicago&forecast_days=7"

mkdir -p data
tmp="$(mktemp)"
curl -sf -m 20 "$URL" > "$tmp"
mv "$tmp" data/weather.json
echo "Weather updated: data/weather.json"
