# Travel API Setup

1) Copy template and add your rotated keys/tokens:

```bash
cp .env.travel.example .env.travel
```

2) Edit `.env.travel` and set:

- `RAPIDAPI_KEY`
- `BOOKING_RAPIDAPI_HOST` (default already set)
- `FLIGHTS_SKY_RAPIDAPI_HOST` (default already set)
- optional OAuth tokens for future direct integrations

3) Run helpers:

```bash
scripts/booking_min_price_oneway.sh JFK LOS
scripts/flights_sky_details.sh "https://flights-sky.p.rapidapi.com/web/flights/details?..."
scripts/travel_api_assist.sh min-price-summary JFK LOS
scripts/travel_api_assist.sh details-summary "https://flights-sky.p.rapidapi.com/web/flights/details?..."
scripts/weather_yahoo_forecast.sh "Washington,DC" f
scripts/airbnb_search_placeid.sh ChIJ7cv00DwsDogRAMDACa2m4K8 2 USD
scripts/tourist_attraction_photos.sh 8797440 0 en_US USD
```

## Security

- Never paste real API keys/passwords in public channels.
- `.env.travel` is ignored by git via `*.env` pattern.
- Prefer OAuth/token-based access over sharing account passwords.
