# Weather rules

Read `data/weather.json` (Open-Meteo, Chicago, °F, mph, America/Chicago time). If `current.time` is more than ~3 hours old, run `scripts/fetch-weather.sh` first.

## Morning drive (7:20 AM)
- Snow (codes 71–77, 85–86), freezing drizzle or rain (56, 57, 66, 67), or temp ≤ 32°F with any precipitation → **suggest leaving by 7:05**, and say why.
- Fog (45, 48) or heavy rain (65, 82) → mention it in one line.
- Otherwise, don't mention the drive at all.

## Outdoor plans (walks, markets, bike rides)
- Precipitation probability ≥ 50% or temp < 35°F during the event → flag it and suggest an indoor swap or a different time. Khang decides; you never move the event.
- Wind ≥ 20 mph → mention it for bike rides.

## Evenings
- Sunset in November is ~4:30 PM: it's dark when Khang leaves work. Only mention this if it matters for a plan.

## WMO weather codes
0 clear · 1–3 partly cloudy to overcast · 45/48 fog · 51–57 drizzle · 61–67 rain · 71–77 snow · 80–82 rain showers · 85–86 snow showers · 95–99 thunderstorm
