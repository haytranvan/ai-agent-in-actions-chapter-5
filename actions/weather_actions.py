import asyncio
import aiohttp
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json

from core.action import (
    Action, ActionDefinition, ActionContext, ActionResult,
    ActionType, PermissionLevel, ParameterDefinition
)


class GetWeatherAction(Action):
    """Action to get current weather conditions"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "http://api.openweathermap.org/data/2.5"
        self.logger = logging.getLogger(__name__)
    
    def get_definition(self) -> ActionDefinition:
        return ActionDefinition(
            name="get_weather",
            description="Get current weather conditions for a location",
            type=ActionType.READ,
            permission_level=PermissionLevel.READ,
            parameters=[
                ParameterDefinition(
                    name="location",
                    type="string",
                    description="City name or coordinates (lat,lon)",
                    required=True
                ),
                ParameterDefinition(
                    name="units",
                    type="string",
                    description="Temperature units (metric, imperial, kelvin)",
                    required=False,
                    default="metric"
                )
            ],
            returns=[
                ParameterDefinition(
                    name="temperature",
                    type="float",
                    description="Current temperature"
                ),
                ParameterDefinition(
                    name="description",
                    type="string",
                    description="Weather description"
                ),
                ParameterDefinition(
                    name="humidity",
                    type="int",
                    description="Humidity percentage"
                ),
                ParameterDefinition(
                    name="wind_speed",
                    type="float",
                    description="Wind speed"
                )
            ],
            examples=[
                "get_weather location=Hanoi units=metric",
                "get_weather location=21.0285,105.8542"
            ]
        )
    
    async def execute(self, ctx: ActionContext) -> ActionResult:
        location = ctx.parameters.get("location")
        units = ctx.parameters.get("units", "metric")
        
        if not location:
            return ActionResult(
                success=False,
                error="location parameter is required"
            )
        
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
                        return ActionResult(
                            success=False,
                            error=f"Weather API error: {error_text}"
                        )
                    
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
                "visibility": data.get("visibility", "N/A"),
                "sunrise": datetime.fromtimestamp(data["sys"]["sunrise"]).strftime("%H:%M"),
                "sunset": datetime.fromtimestamp(data["sys"]["sunset"]).strftime("%H:%M"),
                "timestamp": datetime.now().isoformat()
            }
            
            return ActionResult(
                success=True,
                data=weather_info,
                metadata={
                    "units": units,
                    "api_response_time": response.headers.get("X-RateLimit-Remaining", "unknown")
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error fetching weather: {str(e)}")
            return ActionResult(
                success=False,
                error=f"Failed to fetch weather data: {str(e)}"
            )
    
    def validate(self, ctx: ActionContext) -> bool:
        location = ctx.parameters.get("location")
        if not location:
            return False
        
        units = ctx.parameters.get("units", "metric")
        if units not in ["metric", "imperial", "kelvin"]:
            return False
        
        return True
    
    def get_required_permissions(self) -> List[str]:
        return ["weather.read"]


class GetForecastAction(Action):
    """Action to get weather forecast"""
    
    def __init__(self, api_key: str):
        self.api_key = api_key
        self.base_url = "http://api.openweathermap.org/data/2.5"
        self.logger = logging.getLogger(__name__)
    
    def get_definition(self) -> ActionDefinition:
        return ActionDefinition(
            name="get_forecast",
            description="Get weather forecast for multiple days",
            type=ActionType.READ,
            permission_level=PermissionLevel.READ,
            parameters=[
                ParameterDefinition(
                    name="location",
                    type="string",
                    description="City name or coordinates",
                    required=True
                ),
                ParameterDefinition(
                    name="days",
                    type="int",
                    description="Number of days (1-5)",
                    required=False,
                    default=5
                ),
                ParameterDefinition(
                    name="units",
                    type="string",
                    description="Temperature units",
                    required=False,
                    default="metric"
                )
            ],
            returns=[
                ParameterDefinition(
                    name="forecast",
                    type="list",
                    description="List of daily forecasts"
                )
            ],
            examples=[
                "get_forecast location=Hanoi days=3",
                "get_forecast location=21.0285,105.8542 units=metric"
            ]
        )
    
    async def execute(self, ctx: ActionContext) -> ActionResult:
        location = ctx.parameters.get("location")
        days = min(ctx.parameters.get("days", 5), 5)  # Max 5 days
        units = ctx.parameters.get("units", "metric")
        
        if not location:
            return ActionResult(
                success=False,
                error="location parameter is required"
            )
        
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
                        return ActionResult(
                            success=False,
                            error=f"Forecast API error: {error_text}"
                        )
                    
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
            
            return ActionResult(
                success=True,
                data={
                    "location": data["city"]["name"],
                    "forecast": daily_forecasts,
                    "units": units
                },
                metadata={
                    "days_requested": days,
                    "days_returned": len(daily_forecasts)
                }
            )
            
        except Exception as e:
            self.logger.error(f"Error fetching forecast: {str(e)}")
            return ActionResult(
                success=False,
                error=f"Failed to fetch forecast data: {str(e)}"
            )
    
    def validate(self, ctx: ActionContext) -> bool:
        location = ctx.parameters.get("location")
        if not location:
            return False
        
        days = ctx.parameters.get("days", 5)
        if not isinstance(days, int) or days < 1 or days > 5:
            return False
        
        units = ctx.parameters.get("units", "metric")
        if units not in ["metric", "imperial", "kelvin"]:
            return False
        
        return True
    
    def get_required_permissions(self) -> List[str]:
        return ["weather.read"]


class AnalyzeWeatherAction(Action):
    """Action to analyze weather conditions for activities"""
    
    def get_definition(self) -> ActionDefinition:
        return ActionDefinition(
            name="analyze_weather",
            description="Analyze weather conditions and suggest activities",
            type=ActionType.READ,
            permission_level=PermissionLevel.READ,
            parameters=[
                ParameterDefinition(
                    name="weather_data",
                    type="dict",
                    description="Weather data to analyze",
                    required=True
                ),
                ParameterDefinition(
                    name="activity_type",
                    type="string",
                    description="Type of activity (outdoor, indoor, sports, etc.)",
                    required=False,
                    default="general"
                )
            ],
            returns=[
                ParameterDefinition(
                    name="recommendations",
                    type="list",
                    description="List of activity recommendations"
                ),
                ParameterDefinition(
                    name="suitability_score",
                    type="float",
                    description="Weather suitability score (0-10)"
                )
            ],
            examples=[
                "analyze_weather weather_data={...} activity_type=outdoor",
                "analyze_weather weather_data={...} activity_type=sports"
            ]
        )
    
    async def execute(self, ctx: ActionContext) -> ActionResult:
        weather_data = ctx.parameters.get("weather_data")
        activity_type = ctx.parameters.get("activity_type", "general")
        
        if not weather_data:
            return ActionResult(
                success=False,
                error="weather_data parameter is required"
            )
        
        try:
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
            
            return ActionResult(
                success=True,
                data={
                    "recommendations": recommendations,
                    "suitability_score": round(suitability_score, 1),
                    "weather_summary": {
                        "temperature": temp,
                        "description": description,
                        "humidity": humidity,
                        "wind_speed": wind_speed
                    }
                }
            )
            
        except Exception as e:
            return ActionResult(
                success=False,
                error=f"Failed to analyze weather: {str(e)}"
            )
    
    def validate(self, ctx: ActionContext) -> bool:
        weather_data = ctx.parameters.get("weather_data")
        if not weather_data or not isinstance(weather_data, dict):
            return False
        
        activity_type = ctx.parameters.get("activity_type", "general")
        valid_types = ["general", "outdoor", "indoor", "sports", "leisure"]
        if activity_type not in valid_types:
            return False
        
        return True
    
    def get_required_permissions(self) -> List[str]:
        return ["weather.analyze"]


class WeatherActions:
    """Container class for all weather-related actions"""
    
    def __init__(self, api_key: str):
        self.get_weather_action = GetWeatherAction(api_key)
        self.get_forecast_action = GetForecastAction(api_key)
        self.analyze_weather_action = AnalyzeWeatherAction()
    
    def get_all_actions(self) -> List[Action]:
        """Get all weather actions"""
        return [
            self.get_weather_action,
            self.get_forecast_action,
            self.analyze_weather_action
        ]

