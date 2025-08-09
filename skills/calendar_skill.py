import asyncio
import logging
from typing import Dict, Any, List
from datetime import datetime, timedelta
import json

from semantic_kernel.skill_definition import sk_function, sk_function_context_parameter
from semantic_kernel.orchestration.sk_context import SKContext


class CalendarSkill:
    """Semantic Kernel skill for calendar operations"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.events = []  # In-memory storage for demo purposes
    
    @sk_function(
        description="Create a new calendar event",
        name="create_event"
    )
    @sk_function_context_parameter(
        name="title",
        description="Event title",
        default_value="New Event"
    )
    @sk_function_context_parameter(
        name="start_time",
        description="Event start time (ISO format or relative like 'tomorrow 2pm')",
        default_value=""
    )
    @sk_function_context_parameter(
        name="end_time",
        description="Event end time (ISO format or relative like 'tomorrow 3pm')",
        default_value=""
    )
    @sk_function_context_parameter(
        name="description",
        description="Event description",
        default_value=""
    )
    @sk_function_context_parameter(
        name="location",
        description="Event location",
        default_value=""
    )
    @sk_function_context_parameter(
        name="weather_based",
        description="Whether event is weather-based",
        default_value="false"
    )
    async def create_event(self, context: SKContext) -> str:
        """Create a new calendar event"""
        title = context.variables.get("title", "New Event")
        start_time = context.variables.get("start_time", "")
        end_time = context.variables.get("end_time", "")
        description = context.variables.get("description", "")
        location = context.variables.get("location", "")
        weather_based = context.variables.get("weather_based", "false").lower() == "true"
        
        try:
            # Parse start and end times
            if not start_time:
                # Default to tomorrow at 10 AM
                start_dt = datetime.now() + timedelta(days=1)
                start_dt = start_dt.replace(hour=10, minute=0, second=0, microsecond=0)
            else:
                start_dt = self._parse_time(start_time)
            
            if not end_time:
                # Default to 1 hour after start
                end_dt = start_dt + timedelta(hours=1)
            else:
                end_dt = self._parse_time(end_time)
            
            if start_dt >= end_dt:
                return "Error: start_time must be before end_time"
            
            # Create event
            event_id = f"event_{len(self.events) + 1}_{int(datetime.now().timestamp())}"
            event = {
                "id": event_id,
                "title": title,
                "start_time": start_dt.isoformat(),
                "end_time": end_dt.isoformat(),
                "description": description,
                "location": location,
                "weather_based": weather_based,
                "created_at": datetime.now().isoformat()
            }
            
            self.events.append(event)
            
            self.logger.info(f"Created event: {title} at {start_dt}")
            
            result = {
                "event_id": event_id,
                "success": True,
                "event": event
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            return f"Failed to create event: {str(e)}"
    
    @sk_function(
        description="List calendar events",
        name="list_events"
    )
    @sk_function_context_parameter(
        name="start_date",
        description="Start date for filtering (YYYY-MM-DD)",
        default_value=""
    )
    @sk_function_context_parameter(
        name="end_date",
        description="End date for filtering (YYYY-MM-DD)",
        default_value=""
    )
    @sk_function_context_parameter(
        name="weather_based_only",
        description="Show only weather-based events",
        default_value="false"
    )
    async def list_events(self, context: SKContext) -> str:
        """List calendar events"""
        start_date = context.variables.get("start_date", "")
        end_date = context.variables.get("end_date", "")
        weather_based_only = context.variables.get("weather_based_only", "false").lower() == "true"
        
        try:
            filtered_events = []
            
            for event in self.events:
                # Apply weather-based filter
                if weather_based_only and not event.get("weather_based", False):
                    continue
                
                # Apply date filters
                if start_date or end_date:
                    event_start = datetime.fromisoformat(event["start_time"].replace('Z', '+00:00'))
                    event_date = event_start.date()
                    
                    if start_date:
                        start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
                        if event_date < start_dt:
                            continue
                    
                    if end_date:
                        end_dt = datetime.strptime(end_date, "%Y-%m-%d").date()
                        if event_date > end_dt:
                            continue
                
                filtered_events.append(event)
            
            # Sort by start time
            filtered_events.sort(key=lambda x: x["start_time"])
            
            result = {
                "events": filtered_events,
                "count": len(filtered_events),
                "filters_applied": {
                    "start_date": start_date,
                    "end_date": end_date,
                    "weather_based_only": weather_based_only
                }
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            return f"Failed to list events: {str(e)}"
    
    @sk_function(
        description="Suggest activities based on weather conditions",
        name="suggest_activities"
    )
    @sk_function_context_parameter(
        name="weather_data",
        description="Weather data to base suggestions on (JSON string)",
        default_value=""
    )
    @sk_function_context_parameter(
        name="time_slot",
        description="Time slot for activities (morning, afternoon, evening)",
        default_value="afternoon"
    )
    @sk_function_context_parameter(
        name="duration_hours",
        description="Preferred activity duration in hours",
        default_value="2"
    )
    async def suggest_activities(self, context: SKContext) -> str:
        """Suggest activities based on weather conditions"""
        weather_data_str = context.variables.get("weather_data", "{}")
        time_slot = context.variables.get("time_slot", "afternoon")
        duration_hours = int(context.variables.get("duration_hours", "2"))
        
        try:
            weather_data = json.loads(weather_data_str)
            
            # Extract weather conditions
            temp = weather_data.get("temperature", 0)
            description = weather_data.get("description", "").lower()
            humidity = weather_data.get("humidity", 50)
            wind_speed = weather_data.get("wind_speed", 0)
            
            suggestions = []
            best_time = "afternoon"  # Default
            
            # Temperature-based suggestions
            if temp < 10:
                suggestions.extend([
                    "Indoor activities: Movie watching, Board games, Cooking class",
                    "Warm indoor sports: Swimming (indoor pool), Gym workout",
                    "Cultural activities: Museum visit, Library reading, Art gallery"
                ])
                best_time = "afternoon"
            
            elif 10 <= temp <= 20:
                suggestions.extend([
                    "Light outdoor activities: Walking, Photography, Bird watching",
                    "Indoor activities: Coffee shop visit, Shopping mall, Indoor climbing",
                    "Mixed activities: Park visit with indoor backup plan"
                ])
                best_time = "afternoon"
            
            elif 20 <= temp <= 30:
                suggestions.extend([
                    "Outdoor activities: Hiking, Cycling, Picnic, Beach visit",
                    "Sports: Tennis, Basketball, Soccer, Golf",
                    "Recreation: Fishing, Kayaking, Rock climbing"
                ])
                best_time = "morning" if temp > 25 else "afternoon"
            
            else:  # temp > 30
                suggestions.extend([
                    "Early morning activities: Sunrise walk, Morning yoga, Early bird fishing",
                    "Indoor activities: Movie theater, Shopping mall, Indoor sports",
                    "Water activities: Swimming, Water park, Indoor pool"
                ])
                best_time = "morning"
            
            # Weather condition adjustments
            if "rain" in description or "storm" in description:
                suggestions = [
                    "Indoor activities: Movie watching, Board games, Indoor sports",
                    "Creative activities: Painting, Crafting, Music practice",
                    "Relaxation: Spa day, Reading, Meditation"
                ]
                best_time = "anytime"
            
            elif "sunny" in description or "clear" in description:
                if temp <= 30:
                    suggestions.extend([
                        "Sun protection activities: Beach with umbrella, Shaded park visit",
                        "Outdoor dining: Picnic, BBQ, Outdoor cafe"
                    ])
            
            # Wind adjustments
            if wind_speed > 15:
                suggestions = [
                    "Wind-protected activities: Indoor sports, Shopping, Museum visit",
                    "Low-wind activities: Indoor climbing, Gym workout, Library visit"
                ]
            
            # Duration-based suggestions
            if duration_hours >= 4:
                suggestions.extend([
                    "Extended activities: Day trip, Multi-activity session",
                    "Combination activities: Morning hike + afternoon relaxation"
                ])
            
            # Time slot specific suggestions
            if time_slot == "morning":
                suggestions.extend([
                    "Morning activities: Sunrise photography, Morning exercise, Breakfast outing"
                ])
            elif time_slot == "evening":
                suggestions.extend([
                    "Evening activities: Sunset walk, Dinner outing, Evening entertainment"
                ])
            
            result = {
                "suggestions": suggestions,
                "best_time": best_time,
                "weather_summary": {
                    "temperature": temp,
                    "description": description,
                    "humidity": humidity,
                    "wind_speed": wind_speed
                },
                "duration_hours": duration_hours,
                "time_slot": time_slot
            }
            
            return json.dumps(result, indent=2)
            
        except Exception as e:
            return f"Failed to suggest activities: {str(e)}"
    
    def _parse_time(self, time_str: str) -> datetime:
        """Parse time string to datetime"""
        time_str = time_str.lower().strip()
        
        # Handle relative times
        if "tomorrow" in time_str:
            base_date = datetime.now() + timedelta(days=1)
        elif "today" in time_str:
            base_date = datetime.now()
        else:
            # Try to parse as ISO format
            try:
                return datetime.fromisoformat(time_str.replace('Z', '+00:00'))
            except ValueError:
                # Default to tomorrow
                base_date = datetime.now() + timedelta(days=1)
        
        # Parse time
        if "am" in time_str or "pm" in time_str:
            # Handle 12-hour format
            if "am" in time_str:
                hour = int(time_str.split("am")[0].split()[-1])
                if hour == 12:
                    hour = 0
            else:  # pm
                hour = int(time_str.split("pm")[0].split()[-1])
                if hour != 12:
                    hour += 12
            
            return base_date.replace(hour=hour, minute=0, second=0, microsecond=0)
        else:
            # Default to 10 AM
            return base_date.replace(hour=10, minute=0, second=0, microsecond=0)
