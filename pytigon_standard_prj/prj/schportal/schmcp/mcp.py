"""Weather example tools for the MCP server.

Uses the free, no-API-key `Open-Meteo <https://open-meteo.com>`_ service:

* geocoding: ``https://geocoding-api.open-meteo.com/v1/search``
* forecast:  ``https://api.open-meteo.com/v1/forecast``

Two tools are registered, demonstrating both extension mechanisms provided by
``pytigon.schserw.mcp``:

* ``current_temperature`` — a standalone ``@tool`` function;
* ``WeatherForecastTools`` — an ``MCPToolset`` grouping ``forecast`` and
  ``geocode``.

Enable by importing this module at startup (see ``examples/__init__.py``).
"""

import logging

import httpx

from pytigon.schserw.mcp import MCPToolset, tool

print("MCP SERVER started")

logger = logging.getLogger(__name__)

GEOCODE_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"

# WMO weather interpretation codes -> short human readable description.
# https://open-meteo.com/en/docs (table at the bottom of the docs).
WMO_CODES = {
    0: "Clear sky",
    1: "Mainly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    56: "Light freezing drizzle",
    57: "Dense freezing drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    66: "Light freezing rain",
    67: "Heavy freezing rain",
    71: "Slight snow fall",
    73: "Moderate snow fall",
    75: "Heavy snow fall",
    77: "Snow grains",
    80: "Slight rain showers",
    81: "Moderate rain showers",
    82: "Violent rain showers",
    85: "Slight snow showers",
    86: "Heavy snow showers",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


def _wmo(code: int) -> str:
    return WMO_CODES.get(int(code), f"Unknown weather code {code}")


def _geocode(place: str) -> tuple[str, float, float]:
    """Resolve a place name to (name, latitude, longitude)."""
    resp = httpx.get(
        GEOCODE_URL,
        params={
            "name": place,
            "count": 1,
            "language": "en",
            "format": "json",
        },
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()
    results = data.get("results") or []
    if not results:
        raise ValueError(f"Unknown place: {place!r}")
    g = results[0]
    return g["name"], float(g["latitude"]), float(g["longitude"])


@tool()
async def current_temperature(place: str) -> str:
    """Return the current air temperature (°C) for a city/place name.

    Args:
        place: A city name, e.g. "Warsaw", "Kraków", "Berlin".
    """
    name, lat, lon = _geocode(place)
    resp = httpx.get(
        FORECAST_URL,
        params={
            "latitude": lat,
            "longitude": lon,
            "current": "temperature_2m,weather_code",
            "timezone": "auto",
        },
        timeout=15,
    )
    resp.raise_for_status()
    current = resp.json()["current"]
    temp = current["temperature_2m"]
    desc = _wmo(current["weather_code"])
    return f"{name}: {temp}°C, {desc}"


class WeatherForecastTools(MCPToolset):
    """Weather forecast tools grouped in a toolset.

    Every public method becomes an MCP tool; ``self`` is bound automatically
    and excluded from the tool's input schema.
    """

    async def geocode(self, place: str) -> dict:
        """Resolve a place name to geographic coordinates.

        Args:
            place: A city name, e.g. "Warsaw".

        Returns:
            A dict with ``name``, ``latitude`` and ``longitude``.
        """
        name, lat, lon = _geocode(place)
        return {"name": name, "latitude": lat, "longitude": lon}

    async def forecast(self, place: str, days: int = 3) -> list[dict]:
        """Return a multi-day weather forecast for a place.

        Args:
            place: A city name, e.g. "Warsaw".
            days: Number of forecast days (1..16, default 3).

        Returns:
            A list of per-day dicts with date, min/max temperature (°C),
            weather description and max precipitation probability (%).
        """
        days = max(1, min(16, int(days)))
        name, lat, lon = _geocode(place)
        resp = httpx.get(
            FORECAST_URL,
            params={
                "latitude": lat,
                "longitude": lon,
                "daily": (
                    "temperature_2m_max,temperature_2m_min,"
                    "weather_code,precipitation_probability_max"
                ),
                "timezone": "auto",
                "forecast_days": days,
            },
            timeout=15,
        )
        resp.raise_for_status()
        daily = resp.json()["daily"]
        out = []
        for i, date in enumerate(daily["time"]):
            out.append(
                {
                    "date": date,
                    "temperature_max": daily["temperature_2m_max"][i],
                    "temperature_min": daily["temperature_2m_min"][i],
                    "weather": _wmo(daily["weather_code"][i]),
                    "precipitation_probability_max": (
                        daily["precipitation_probability_max"][i]
                    ),
                }
            )
        return out
