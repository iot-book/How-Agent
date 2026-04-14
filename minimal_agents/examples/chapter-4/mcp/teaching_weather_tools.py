"""Shared weather tool definitions for chapter 4 MCP teaching demos."""

from __future__ import annotations

WEATHER_DATA = {
    "Beijing": "Sunny, 18C",
    "Shanghai": "Cloudy, 22C",
    "Guangzhou": "Rainy, 26C",
    "Shenzhen": "Overcast, 27C",
}


def get_weather(city: str) -> str:
    """Query weather information for a city."""
    return WEATHER_DATA.get(city, f"No weather data for {city}")


def list_supported_cities() -> list[str]:
    """Return supported city names."""
    return list(WEATHER_DATA.keys())
