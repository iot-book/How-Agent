"""Shared weather tool for chapter 3 teaching demos."""

from __future__ import annotations

WEATHER_DATA = {
    "Beijing": {"city": "Beijing", "weather": "Sunny", "temperature_c": 18},
    "Shanghai": {"city": "Shanghai", "weather": "Cloudy", "temperature_c": 25},
    "Guangzhou": {"city": "Guangzhou", "weather": "Rainy", "temperature_c": 26},
}


def get_weather(city: str) -> dict:
    """Get weather data for a supported city."""
    return WEATHER_DATA.get(city, {"city": city, "error": "weather not found"})
