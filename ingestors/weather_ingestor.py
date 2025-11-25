import requests
from datetime import datetime


def fetch_weather(locations, provider='open-meteo'):
    """Fetch weather data for multiple locations.
    
    Args:
        locations: List of dicts with 'name', 'lat', 'lon' keys
        provider: Weather provider (currently only 'open-meteo' supported)
    
    Returns:
        List of weather summaries in a format compatible with the pipeline
    """
    if provider != 'open-meteo':
        raise ValueError(f"Unsupported weather provider: {provider}")
    
    summaries = []
    for loc in locations:
        try:
            weather_data = _fetch_open_meteo(loc['lat'], loc['lon'])
            summary = _format_weather_summary(loc['name'], weather_data)
            summaries.append({
                'title': f"Weather for {loc['name']}",
                'summary': summary,
                'link': f"https://open-meteo.com/en/docs#latitude={loc['lat']}&longitude={loc['lon']}"
            })
        except Exception as e:
            summaries.append({
                'title': f"Weather for {loc['name']}",
                'summary': f"Unable to fetch weather data: {str(e)}",
                'link': ''
            })
    
    return summaries


def _fetch_open_meteo(lat, lon):
    """Fetch weather from Open-Meteo API (free, no API key needed)."""
    url = "https://api.open-meteo.com/v1/forecast"
    params = {
        'latitude': lat,
        'longitude': lon,
        'current': 'temperature_2m,relative_humidity_2m,apparent_temperature,precipitation,weather_code,wind_speed_10m',
        'daily': 'temperature_2m_max,temperature_2m_min,precipitation_sum,weather_code',
        'temperature_unit': 'fahrenheit',
        'wind_speed_unit': 'mph',
        'precipitation_unit': 'inch',
        'timezone': 'auto',
        'forecast_days': 3
    }
    
    response = requests.get(url, params=params, timeout=10)
    response.raise_for_status()
    return response.json()


def _format_weather_summary(location_name, data):
    """Format weather data into a readable summary."""
    current = data.get('current', {})
    daily = data.get('daily', {})
    
    temp = current.get('temperature_2m', 'N/A')
    feels_like = current.get('apparent_temperature', 'N/A')
    humidity = current.get('relative_humidity_2m', 'N/A')
    precip = current.get('precipitation', 0)
    wind_speed = current.get('wind_speed_10m', 'N/A')
    
    summary = f"Current conditions in {location_name}: "
    summary += f"Temperature {temp}°F (feels like {feels_like}°F), "
    summary += f"Humidity {humidity}%, Wind {wind_speed} mph"
    
    if precip > 0:
        summary += f", Precipitation {precip} inches"
    
    # Add forecast if available
    if daily and 'temperature_2m_max' in daily:
        summary += f". Today's forecast: High {daily['temperature_2m_max'][0]}°F, "
        summary += f"Low {daily['temperature_2m_min'][0]}°F"
        
        if daily.get('precipitation_sum') and daily['precipitation_sum'][0] > 0:
            summary += f", Expected precipitation {daily['precipitation_sum'][0]} inches"
    
    return summary
