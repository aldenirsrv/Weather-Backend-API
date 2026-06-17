from datetime import date

import requests
from fastapi import HTTPException


def resolve_location(location: str) -> dict:
    """
    Resolves city, town, landmark, or general location text into coordinates.
    Uses Open-Meteo Geocoding API.
    """
    url = "https://geocoding-api.open-meteo.com/v1/search"

    response = requests.get(
        url,
        params={
            "name": location,
            "count": 1,
            "language": "en",
            "format": "json",
        },
        timeout=10,
    )

    if response.status_code != 200:
        raise HTTPException(status_code=502, detail="Failed to resolve location")

    data = response.json()
    results = data.get("results", [])

    if not results:
        raise HTTPException(
            status_code=404,
            detail=f"Location '{location}' was not found",
        )

    result = results[0]

    return {
        "name": result.get("name"),
        "country": result.get("country"),
        "latitude": result.get("latitude"),
        "longitude": result.get("longitude"),
    }


def fetch_weather(latitude: float, longitude: float, start_date: date, end_date: date) -> dict:
    """
    Retrieves real weather forecast data from Open-Meteo.
    """
    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "current": [
            "temperature_2m",
            "relative_humidity_2m",
            "apparent_temperature",
            "wind_speed_10m",
        ],
        "daily": [
            "temperature_2m_max",
            "temperature_2m_min",
            "precipitation_probability_max",
            "wind_speed_10m_max",
        ],
        "timezone": "auto",
    }

    response = requests.get(url, params=params, timeout=10)

    if response.status_code != 200:
        raise HTTPException(status_code=502, detail="Failed to retrieve weather data")

    return response.json()