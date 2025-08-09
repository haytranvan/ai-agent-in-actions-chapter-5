import asyncio
import aiohttp
import logging
from typing import Dict, Any, List
from datetime import datetime
import json

from semantic_kernel.skill_definition import sk_function, sk_function_context_parameter
from semantic_kernel.orchestration.sk_context import SKContext


class WeatherSkill:
    """Semantic Kernel skill for weather operations"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "http://api.openweathermap.org/data/2.5"
        self.logger = logging.getLogger(__name__)
    
    @sk_function(
        description="Get current weather conditions for a location",
        name="get_weather"
    )
    @sk_function_context_parameter(
        name="location",
        description="City name or coordinates (lat,lon)",
        default_value="Hanoi"
    )
    @sk_function_context_parameter(
        name="units",
        description="Temperature units (metric, imperial, kelvin)",
        default_value="metric"
    )
    async def get_weather(self, context: SKContext) -> str:
        """Get current weather for a location"""
        location = context.variables.get("location", "Hanoi")
        units = context.variables.get("units", "metric")
        
        try:
            # Build API URL
            url = f"{self.base_url}/weather"
            params = {
                "q": location,
                "appid": self.api_key,
                "units": units
            }
            
            # Make API request
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        return f"Weather API error: {error_text}"
                    
                    data = await response.json()
            
            # Extract weather information
            weather_info = {
                "location": data.get("name", location),
                "temperature": data["main"]["temp"],
                "feels_like": data["main"]["feels_like"],
                "description": data["weather"][0]["description"],
                "humidity": data["main"]["humidity"],
                "wind_speed": data["wind"]["speed"],
                "pressure": data["main"]["pressure"],
                "sunrise": datetime.fromtimestamp(data["sys"]["sunrise"]).strftime("%H:%M"),
                "sunset": datetime.fromtimestamp(data["sys"]["sunset"]).strftime("%H:%M")
            }
            
            return json.dumps(weather_info, indent=2)
            
        except Exception as e:
            self.logger.error(f"Error fetching weather: {str(e)}")
            return f"Failed to fetch weather data: {str(e)}"
    
    @sk_function(
        description="Get weather forecast for multiple days",
        name="get_forecast"
    )
    @sk_function_context_parameter(
        name="location",
        description="City name or coordinates",
        default_value="Hanoi"
    )
    @sk_function_context_parameter(
        name="days",
        description="Number of days (1-5)",
        default_value="3"
    )
    @sk_function_context_parameter(
        name="units",
        description="Temperature units",
        default_value="metric"
    )
    async def get_forecast(self, context: SKContext) -> str:
        """Get weather forecast for a location"""
        location = context.variables.get("location", "Hanoi")
        days = min(int(context.variables.get("days", "3")), 5)
        units = context.variables.get("units", "metric")
        
        try:
            # Build API URL
            url = f"{self.base_url}/forecast"
            params = {
                "q": location,
                "appid": self.api_key,
                "units": units,
                "cnt": days * 8  # 8 forecasts per day
            }
            
            # Make API request
            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status != 200:
                        error_text = await response.text()
                        return f"Forecast API error: {error_text}"
                    
                    data = await response.json()
            
            # Process forecast data
            daily_forecasts = []
            current_date = None
            daily_data = {}
            
            for item in data["list"]:
                date = datetime.fromtimestamp(item["dt"]).date()
                
                if current_date != date:
                    if current_date and daily_data:
                        daily_forecasts.append(daily_data)
                    current_date = date
                    daily_data = {
                        "date": date.strftime("%Y-%m-%d"),
                        "day": date.strftime("%A"),
                        "temp_min": item["main"]["temp_min"],
                        "temp_max": item["main"]["temp_max"],
                        "description": item["weather"][0]["description"],
                        "humidity": item["main"]["humidity"],
                        "wind_speed": item["wind"]["speed"],
                        "rain_probability": item.get("pop", 0) * 100
                    }
                else:
                    # Update min/max temperatures
                    daily_data["temp_min"] = min(daily_data["temp_min"], item["main"]["temp_min"])
                    daily_data["temp_max"] = max(daily_data["temp_max"], item["main"]["temp_max"])
            
            # Add the last day
            if daily_data:
                daily_forecasts.append(daily_data)
            
            result = {
                "location": data["city"]["name"],
                "forecast": daily_forecasts,
                "units": units
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            self.logger.error(f"Error fetching forecast: {str(e)}")
            return f"Failed to fetch forecast data: {str(e)}"
    
    @sk_function(
        description="Analyze weather conditions and suggest activities",
        name="analyze_weather"
    )
    @sk_function_context_parameter(
        name="weather_data",
        description="Weather data to analyze (JSON string)",
        default_value=""
    )
    @sk_function_context_parameter(
        name="activity_type",
        description="Type of activity (outdoor, indoor, sports, etc.)",
        default_value="general"
    )
    async def analyze_weather(self, context: SKContext) -> str:
        """Analyze weather conditions for activities"""
        weather_data_str = context.variables.get("weather_data", "{}")
        activity_type = context.variables.get("activity_type", "general")
        
        try:
            weather_data = json.loads(weather_data_str)
            
            # Extract weather conditions
            temp = weather_data.get("temperature", 0)
            description = weather_data.get("description", "").lower()
            humidity = weather_data.get("humidity", 50)
            wind_speed = weather_data.get("wind_speed", 0)
            
            # Analyze conditions
            recommendations = []
            suitability_score = 7.0  # Base score
            
            # Temperature analysis
            if 15 <= temp <= 30:
                recommendations.append("Temperature is comfortable for outdoor activities")
                suitability_score += 1
            elif temp < 10:
                recommendations.append("Temperature is cold, consider indoor activities")
                suitability_score -= 2
            elif temp > 35:
                recommendations.append("Temperature is very hot, avoid strenuous outdoor activities")
                suitability_score -= 2
            
            # Weather condition analysis
            if "rain" in description or "drizzle" in description:
                recommendations.append("Rain expected - indoor activities recommended")
                suitability_score -= 2
            elif "sunny" in description or "clear" in description:
                recommendations.append("Clear weather - great for outdoor activities")
                suitability_score += 1
            elif "cloudy" in description:
                recommendations.append("Cloudy weather - moderate outdoor activities suitable")
            
            # Wind analysis
            if wind_speed > 20:
                recommendations.append("High winds - avoid outdoor activities")
                suitability_score -= 1
            elif wind_speed < 5:
                recommendations.append("Light winds - perfect for outdoor activities")
                suitability_score += 0.5
            
            # Humidity analysis
            if humidity > 80:
                recommendations.append("High humidity - consider indoor activities")
                suitability_score -= 1
            elif 40 <= humidity <= 60:
                recommendations.append("Comfortable humidity levels")
                suitability_score += 0.5
            
            # Activity-specific recommendations
            if activity_type == "outdoor":
                if suitability_score >= 7:
                    recommendations.append("Excellent conditions for outdoor activities")
                elif suitability_score >= 5:
                    recommendations.append("Moderate conditions for outdoor activities")
                else:
                    recommendations.append("Poor conditions for outdoor activities - consider indoor alternatives")
            
            elif activity_type == "sports":
                if "rain" in description or "storm" in description:
                    recommendations.append("Weather not suitable for outdoor sports")
                    suitability_score -= 1
                elif temp > 30:
                    recommendations.append("High temperature - consider early morning or evening sports")
                    suitability_score -= 1
            
            # Clamp score to 0-10 range
            suitability_score = max(0, min(10, suitability_score))
            
            result = {
                "recommendations": recommendations,
                "suitability_score": round(suitability_score, 1),
                "weather_summary": {
                    "temperature": temp,
                    "description": description,
                    "humidity": humidity,
                    "wind_speed": wind_speed
                }
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            return f"Failed to analyze weather: {str(e)}"
