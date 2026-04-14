"""Teaching demo: minimal local stdio MCP weather server."""

from teaching_weather_tools import (
    get_weather as get_weather_impl,
    list_supported_cities as list_supported_cities_impl,
)
from mcp.server.fastmcp import FastMCP

mcp = FastMCP("weather-server")


@mcp.tool()
def get_weather(city: str) -> str:
    """Query weather information for a city."""
    return get_weather_impl(city)


@mcp.tool()
def list_supported_cities() -> list[str]:
    """Return supported city names."""
    return list_supported_cities_impl()


if __name__ == "__main__":
    mcp.run(transport="stdio")
