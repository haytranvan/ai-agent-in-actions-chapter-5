import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json

from core.action import (
    Action, ActionDefinition, ActionContext, ActionResult,
    ActionType, PermissionLevel, ParameterDefinition
)


class CreateEventAction(Action):
    """Action to create calendar events"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.events = []  # In-memory storage for demo purposes
    
    def get_definition(self) -> ActionDefinition:
        return ActionDefinition(
            name="create_event",
            description="Create a new calendar event",
            type=ActionType.WRITE,
            permission_level=PermissionLevel.WRITE,
            parameters=[
                ParameterDefinition(
                    name="title",
                    type="string",
                    description="Event title",
                    required=True
                ),
                ParameterDefinition(
                    name="start_time",
                    type="string",
                    description="Event start time (ISO format)",
                    required=True
                ),
                ParameterDefinition(
                    name="end_time",
                    type="string",
                    description="Event end time (ISO format)",
                    required=True
                ),
                ParameterDefinition(
                    name="description",
                    type="string",
                    description="Event description",
                    required=False
                ),
                ParameterDefinition(
                    name="location",
                    type="string",
                    description="Event location",
                    required=False
                ),
                ParameterDefinition(
                    name="weather_based",
                    type="bool",
                    description="Whether event is weather-based",
                    required=False,
                    default=False
                )
            ],
            returns=[
                ParameterDefinition(
                    name="event_id",
                    type="string",
                    description="Created event ID"
                ),
                ParameterDefinition(
                    name="success",
                    type="bool",
                    description="Whether event was created successfully"
                )
            ],
            examples=[
                "create_event title=Outdoor Walk start_time=2024-01-15T10:00:00 end_time=2024-01-15T11:00:00",
                "create_event title=Indoor Movie start_time=2024-01-15T14:00:00 end_time=2024-01-15T16:00:00 weather_based=true"
            ]
        )
    
    async def execute(self, ctx: ActionContext) -> ActionResult:
        title = ctx.parameters.get("title")
        start_time = ctx.parameters.get("start_time")
        end_time = ctx.parameters.get("end_time")
        description = ctx.parameters.get("description", "")
        location = ctx.parameters.get("location", "")
        weather_based = ctx.parameters.get("weather_based", False)
        
        if not all([title, start_time, end_time]):
            return ActionResult(
                success=False,
                error="title, start_time, and end_time are required"
            )
        
        try:
            # Validate datetime format
            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
            end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            
            if start_dt >= end_dt:
                return ActionResult(
                    success=False,
                    error="start_time must be before end_time"
                )
            
            # Create event
            event_id = f"event_{len(self.events) + 1}_{int(datetime.now().timestamp())}"
            event = {
                "id": event_id,
                "title": title,
                "start_time": start_time,
                "end_time": end_time,
                "description": description,
                "location": location,
                "weather_based": weather_based,
                "created_at": datetime.now().isoformat(),
                "created_by": ctx.agent_id
            }
            
            self.events.append(event)
            
            self.logger.info(f"Created event: {title} at {start_time}")
            
            return ActionResult(
                success=True,
                data={
                    "event_id": event_id,
                    "success": True,
                    "event": event
                }
            )
            
        except ValueError as e:
            return ActionResult(
                success=False,
                error=f"Invalid datetime format: {str(e)}"
            )
        except Exception as e:
            return ActionResult(
                success=False,
                error=f"Failed to create event: {str(e)}"
            )
    
    def validate(self, ctx: ActionContext) -> bool:
        title = ctx.parameters.get("title")
        start_time = ctx.parameters.get("start_time")
        end_time = ctx.parameters.get("end_time")
        
        if not all([title, start_time, end_time]):
            return False
        
        # Basic validation
        if len(title.strip()) == 0:
            return False
        
        return True
    
    def get_required_permissions(self) -> List[str]:
        return ["calendar.write"]


class ListEventsAction(Action):
    """Action to list calendar events"""
    
    def __init__(self, events_storage):
        self.events = events_storage
        self.logger = logging.getLogger(__name__)
    
    def get_definition(self) -> ActionDefinition:
        return ActionDefinition(
            name="list_events",
            description="List calendar events",
            type=ActionType.READ,
            permission_level=PermissionLevel.READ,
            parameters=[
                ParameterDefinition(
                    name="start_date",
                    type="string",
                    description="Start date for filtering (YYYY-MM-DD)",
                    required=False
                ),
                ParameterDefinition(
                    name="end_date",
                    type="string",
                    description="End date for filtering (YYYY-MM-DD)",
                    required=False
                ),
                ParameterDefinition(
                    name="weather_based_only",
                    type="bool",
                    description="Show only weather-based events",
                    required=False,
                    default=False
                )
            ],
            returns=[
                ParameterDefinition(
                    name="events",
                    type="list",
                    description="List of calendar events"
                ),
                ParameterDefinition(
                    name="count",
                    type="int",
                    description="Number of events found"
                )
            ],
            examples=[
                "list_events start_date=2024-01-15 end_date=2024-01-16",
                "list_events weather_based_only=true"
            ]
        )
    
    async def execute(self, ctx: ActionContext) -> ActionResult:
        start_date = ctx.parameters.get("start_date")
        end_date = ctx.parameters.get("end_date")
        weather_based_only = ctx.parameters.get("weather_based_only", False)
        
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
            
            return ActionResult(
                success=True,
                data={
                    "events": filtered_events,
                    "count": len(filtered_events),
                    "filters_applied": {
                        "start_date": start_date,
                        "end_date": end_date,
                        "weather_based_only": weather_based_only
                    }
                }
            )
            
        except Exception as e:
            return ActionResult(
                success=False,
                error=f"Failed to list events: {str(e)}"
            )
    
    def validate(self, ctx: ActionContext) -> bool:
        start_date = ctx.parameters.get("start_date")
        end_date = ctx.parameters.get("end_date")
        
        # Validate date formats if provided
        if start_date:
            try:
                datetime.strptime(start_date, "%Y-%m-%d")
            except ValueError:
                return False
        
        if end_date:
            try:
                datetime.strptime(end_date, "%Y-%m-%d")
            except ValueError:
                return False
        
        return True
    
    def get_required_permissions(self) -> List[str]:
        return ["calendar.read"]


class SuggestActivitiesAction(Action):
    """Action to suggest activities based on weather"""
    
    def get_definition(self) -> ActionDefinition:
        return ActionDefinition(
            name="suggest_activities",
            description="Suggest activities based on weather conditions",
            type=ActionType.READ,
            permission_level=PermissionLevel.READ,
            parameters=[
                ParameterDefinition(
                    name="weather_data",
                    type="dict",
                    description="Weather data to base suggestions on",
                    required=True
                ),
                ParameterDefinition(
                    name="time_slot",
                    type="string",
                    description="Time slot for activities (morning, afternoon, evening)",
                    required=False,
                    default="afternoon"
                ),
                ParameterDefinition(
                    name="duration_hours",
                    type="int",
                    description="Preferred activity duration in hours",
                    required=False,
                    default=2
                )
            ],
            returns=[
                ParameterDefinition(
                    name="suggestions",
                    type="list",
                    description="List of suggested activities"
                ),
                ParameterDefinition(
                    name="best_time",
                    type="string",
                    description="Best time for outdoor activities"
                )
            ],
            examples=[
                "suggest_activities weather_data={...} time_slot=morning",
                "suggest_activities weather_data={...} duration_hours=3"
            ]
        )
    
    async def execute(self, ctx: ActionContext) -> ActionResult:
        weather_data = ctx.parameters.get("weather_data")
        time_slot = ctx.parameters.get("time_slot", "afternoon")
        duration_hours = ctx.parameters.get("duration_hours", 2)
        
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
            
            suggestions = []
            best_time = "afternoon"  # Default
            
            # Temperature-based suggestions
            if temp < 10:
                suggestions.extend([
                    "Indoor activities: Movie watching, Board games, Cooking class",
                    "Warm indoor sports: Swimming (indoor pool), Gym workout",
                    "Cultural activities: Museum visit, Library reading, Art gallery"
                ])
                best_time = "afternoon"  # Warmest part of day
            
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
            
            return ActionResult(
                success=True,
                data={
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
            )
            
        except Exception as e:
            return ActionResult(
                success=False,
                error=f"Failed to suggest activities: {str(e)}"
            )
    
    def validate(self, ctx: ActionContext) -> bool:
        weather_data = ctx.parameters.get("weather_data")
        if not weather_data or not isinstance(weather_data, dict):
            return False
        
        time_slot = ctx.parameters.get("time_slot", "afternoon")
        valid_slots = ["morning", "afternoon", "evening", "anytime"]
        if time_slot not in valid_slots:
            return False
        
        duration_hours = ctx.parameters.get("duration_hours", 2)
        if not isinstance(duration_hours, int) or duration_hours < 1 or duration_hours > 12:
            return False
        
        return True
    
    def get_required_permissions(self) -> List[str]:
        return ["calendar.read"]


class CalendarActions:
    """Container class for all calendar-related actions"""
    
    def __init__(self):
        self.events_storage = []  # Shared storage for events
        self.create_event_action = CreateEventAction()
        self.create_event_action.events = self.events_storage  # Share storage
        self.list_events_action = ListEventsAction(self.events_storage)
        self.suggest_activities_action = SuggestActivitiesAction()
    
    def get_all_actions(self) -> List[Action]:
        """Get all calendar actions"""
        return [
            self.create_event_action,
            self.list_events_action,
            self.suggest_activities_action
        ]

