import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json
import re

from openai import AsyncOpenAI
from core.action import (
    ActionRegistry, ActionExecutor, ActionContext, 
    ActionResult, ActionDefinition
)


class ActionStep:
    """Represents a single action to be executed"""
    
    def __init__(self, action_name: str, parameters: Dict[str, Any], reason: str = ""):
        self.action_name = action_name
        self.parameters = parameters
        self.reason = reason
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action_name,
            "parameters": self.parameters,
            "reason": self.reason
        }


class WeatherCalendarAgent:
    """An agent that can check weather and manage calendar events"""
    
    def __init__(self, agent_id: str, name: str, description: str):
        self.agent_id = agent_id
        self.name = name
        self.description = description
        self.registry = ActionRegistry()
        self.executor = ActionExecutor(self.registry)
        self.client: Optional[AsyncOpenAI] = None
        self.permissions: List[str] = []
        self.logger = logging.getLogger(f"agent.{agent_id}")
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def set_openai_client(self, client: AsyncOpenAI) -> None:
        """Set the OpenAI client for the agent"""
        self.client = client
    
    def add_permission(self, permission: str) -> None:
        """Add a permission to the agent"""
        if permission not in self.permissions:
            self.permissions.append(permission)
    
    def has_permission(self, permission: str) -> bool:
        """Check if the agent has a specific permission"""
        return permission in self.permissions
    
    def register_action(self, action) -> None:
        """Register an action with the agent"""
        self.registry.register_action(action)
    
    async def execute(self, input_text: str) -> str:
        """Process natural language input and execute appropriate actions"""
        self.logger.info(f"Processing input: {input_text}")
        
        try:
            # Parse the input to determine what actions to take
            action_steps = await self._parse_input(input_text)
            
            if not action_steps:
                return "I couldn't determine what actions to take from your request. Please try rephrasing."
            
            # Execute the action steps
            results = []
            for step in action_steps:
                result = await self._execute_action_step(step)
                results.append(result)
            
            # Format the results
            return self._format_results(results)
            
        except Exception as e:
            self.logger.error(f"Error executing request: {str(e)}")
            return f"An error occurred: {str(e)}"
    
    async def _parse_input(self, input_text: str) -> List[ActionStep]:
        """Parse natural language input to determine actions to execute"""
        if not self.client:
            # Fallback to simple keyword-based parsing
            return self._simple_parse_input(input_text)
        
        try:
            # Get available actions
            available_actions = self.registry.list_actions()
            
            # Create prompt for action selection
            prompt = self._build_action_selection_prompt(input_text, available_actions)
            
            # Use OpenAI to determine actions
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an AI assistant that helps determine which actions to execute based on user input. Respond with JSON only."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1
            )
            
            # Parse the response
            content = response.choices[0].message.content
            return self._parse_ai_response(content)
            
        except Exception as e:
            self.logger.warning(f"AI parsing failed, falling back to simple parsing: {str(e)}")
            return self._simple_parse_input(input_text)
    
    def _simple_parse_input(self, input_text: str) -> List[ActionStep]:
        """Simple keyword-based action parsing as fallback"""
        input_lower = input_text.lower()
        steps = []
        
        # Weather operations
        if any(word in input_lower for word in ["weather", "temperature", "forecast"]):
            # Extract location using regex
            location_match = re.search(r'in\s+([^,\n]+)', input_text, re.IGNORECASE)
            location = location_match.group(1).strip() if location_match else "Hanoi"
            
            if "forecast" in input_lower:
                days_match = re.search(r'(\d+)\s*days?', input_text)
                days = int(days_match.group(1)) if days_match else 3
                steps.append(ActionStep(
                    action_name="get_forecast",
                    parameters={"location": location, "days": days},
                    reason="User requested weather forecast"
                ))
            else:
                steps.append(ActionStep(
                    action_name="get_weather",
                    parameters={"location": location},
                    reason="User requested current weather"
                ))
        
        # Calendar operations
        if any(word in input_lower for word in ["create", "add", "schedule", "event", "calendar"]):
            # Extract event details
            title_match = re.search(r'create\s+(?:an?\s+)?(?:event\s+)?(?:called\s+)?([^,\n]+)', input_text, re.IGNORECASE)
            title = title_match.group(1).strip() if title_match else "New Event"
            
            # Generate default times
            tomorrow = datetime.now() + timedelta(days=1)
            start_time = tomorrow.replace(hour=10, minute=0, second=0, microsecond=0).isoformat()
            end_time = tomorrow.replace(hour=11, minute=0, second=0, microsecond=0).isoformat()
            
            steps.append(ActionStep(
                action_name="create_event",
                parameters={
                    "title": title,
                    "start_time": start_time,
                    "end_time": end_time,
                    "weather_based": "weather" in input_lower
                },
                reason="User requested to create a calendar event"
            ))
        
        # List events
        if any(word in input_lower for word in ["list", "show", "events", "calendar"]):
            steps.append(ActionStep(
                action_name="list_events",
                parameters={},
                reason="User requested to list calendar events"
            ))
        
        # Activity suggestions
        if any(word in input_lower for word in ["suggest", "recommend", "activities", "what to do"]):
            # This will need weather data, so we'll chain actions
            location_match = re.search(r'in\s+([^,\n]+)', input_text, re.IGNORECASE)
            location = location_match.group(1).strip() if location_match else "Hanoi"
            
            steps.append(ActionStep(
                action_name="get_weather",
                parameters={"location": location},
                reason="Need weather data for activity suggestions"
            ))
        
        return steps
    
    def _build_action_selection_prompt(self, input_text: str, actions: List[ActionDefinition]) -> str:
        """Build a prompt for action selection"""
        action_descriptions = []
        for action in actions:
            params_str = ", ".join([f"{p.name}: {p.type}" for p in action.parameters])
            desc = f"- {action.name}: {action.description} (Parameters: {params_str})"
            action_descriptions.append(desc)
        
        return f"""
User input: "{input_text}"

Available actions:
{chr(10).join(action_descriptions)}

Based on the user input, determine which actions to execute. Respond with a JSON array of action steps:

[
  {{
    "action_name": "action_name",
    "parameters": {{"param1": "value1"}},
    "reason": "Why this action is needed"
  }}
]

Only include actions that are relevant to the user's request. If no actions are needed, return an empty array.
"""
    
    def _parse_ai_response(self, response: str) -> List[ActionStep]:
        """Parse the AI response to extract action steps"""
        try:
            # Try to parse as JSON
            data = json.loads(response)
            if isinstance(data, list):
                steps = []
                for item in data:
                    if isinstance(item, dict):
                        step = ActionStep(
                            action_name=item.get("action_name", ""),
                            parameters=item.get("parameters", {}),
                            reason=item.get("reason", "")
                        )
                        steps.append(step)
                return steps
        except json.JSONDecodeError:
            self.logger.warning("Failed to parse AI response as JSON")
        
        # Fallback to simple parsing
        return self._simple_parse_input(response)
    
    async def _execute_action_step(self, step: ActionStep) -> str:
        """Execute a single action step"""
        self.logger.info(f"Executing action: {step.action_name} with parameters: {step.parameters}")
        
        # Create action context
        ctx = ActionContext(
            agent_id=self.agent_id,
            user_id="user_001",  # In practice, this would come from authentication
            session_id="session_001",
            parameters=step.parameters,
            metadata={},
            permissions=self.permissions
        )
        
        # Execute the action
        result = await self.executor.execute_action(step.action_name, ctx)
        
        # Format the result
        if result.success:
            return f"✅ {step.action_name}: {self._format_action_result(step.action_name, result.data)}"
        else:
            return f"❌ {step.action_name} failed: {result.error}"
    
    def _format_action_result(self, action_name: str, data: Any) -> str:
        """Format action results for display"""
        if action_name == "get_weather":
            return f"🌤️ {data.get('location', 'Unknown')}: {data.get('temperature', 'N/A')}°C, {data.get('description', 'N/A')}"
        
        elif action_name == "get_forecast":
            forecast = data.get('forecast', [])
            if forecast:
                return f"📅 {len(forecast)} days forecast for {data.get('location', 'Unknown')}"
            return "No forecast data available"
        
        elif action_name == "create_event":
            return f"📅 Created event: {data.get('event', {}).get('title', 'Unknown')}"
        
        elif action_name == "list_events":
            count = data.get('count', 0)
            return f"📋 Found {count} events"
        
        elif action_name == "analyze_weather":
            score = data.get('suitability_score', 0)
            return f"📊 Weather suitability score: {score}/10"
        
        elif action_name == "suggest_activities":
            suggestions = data.get('suggestions', [])
            return f"🎯 {len(suggestions)} activity suggestions available"
        
        else:
            return str(data)
    
    def _format_results(self, results: List[str]) -> str:
        """Format the results of action execution"""
        if not results:
            return "No actions were executed."
        
        return "\n".join(results)
    
    def list_available_actions(self) -> List[ActionDefinition]:
        """List all available actions for this agent"""
        return self.registry.list_actions()
    
    async def execute_direct_action(self, action_name: str, parameters: Dict[str, Any]) -> ActionResult:
        """Execute an action directly without natural language parsing"""
        ctx = ActionContext(
            agent_id=self.agent_id,
            user_id="user_001",
            session_id="session_001",
            parameters=parameters,
            metadata={},
            permissions=self.permissions
        )
        
        return await self.executor.execute_action(action_name, ctx)
    
    async def weather_based_planning(self, location: str, days: int = 3) -> str:
        """Specialized method for weather-based calendar planning"""
        self.logger.info(f"Weather-based planning for {location} for {days} days")
        
        try:
            # Step 1: Get weather forecast
            forecast_result = await self.execute_direct_action("get_forecast", {
                "location": location,
                "days": days
            })
            
            if not forecast_result.success:
                return f"Failed to get weather forecast: {forecast_result.error}"
            
            forecast_data = forecast_result.data
            events_created = []
            
            # Step 2: Analyze each day and create appropriate events
            for day_forecast in forecast_data.get('forecast', []):
                date = day_forecast.get('date')
                temp_max = day_forecast.get('temp_max', 0)
                description = day_forecast.get('description', '').lower()
                rain_prob = day_forecast.get('rain_probability', 0)
                
                # Determine if it's good for outdoor activities
                is_good_weather = (
                    15 <= temp_max <= 30 and 
                    rain_prob < 30 and 
                    'rain' not in description and 
                    'storm' not in description
                )
                
                if is_good_weather:
                    # Create outdoor activity event
                    start_time = f"{date}T10:00:00"
                    end_time = f"{date}T12:00:00"
                    
                    event_result = await self.execute_direct_action("create_event", {
                        "title": "Outdoor Activity",
                        "start_time": start_time,
                        "end_time": end_time,
                        "description": f"Good weather day: {temp_max}°C, {description}",
                        "weather_based": True
                    })
                    
                    if event_result.success:
                        events_created.append(f"Outdoor activity on {date}")
                else:
                    # Create indoor activity event
                    start_time = f"{date}T14:00:00"
                    end_time = f"{date}T16:00:00"
                    
                    event_result = await self.execute_direct_action("create_event", {
                        "title": "Indoor Activity",
                        "start_time": start_time,
                        "end_time": end_time,
                        "description": f"Weather not ideal: {temp_max}°C, {description}, {rain_prob}% rain chance",
                        "weather_based": True
                    })
                    
                    if event_result.success:
                        events_created.append(f"Indoor activity on {date}")
            
            return f"Weather-based planning completed! Created {len(events_created)} events:\n" + "\n".join(events_created)
            
        except Exception as e:
            self.logger.error(f"Error in weather-based planning: {str(e)}")
            return f"Error in weather-based planning: {str(e)}"

