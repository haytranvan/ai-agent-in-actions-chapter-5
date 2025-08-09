import os
from semantic_kernel.skill_definition import sk_function, sk_function_context_parameter
from semantic_kernel.orchestration.sk_context import SKContext


class WeatherSemanticFunctions:
    """Semantic functions for weather analysis using prompts"""
    
    def __init__(self):
        self.prompts_dir = "prompts"
        os.makedirs(self.prompts_dir, exist_ok=True)
        self._create_prompts()
    
    def _create_prompts(self):
        """Create prompt files for semantic functions"""
        
        # Weather Analysis Prompt
        weather_analysis_prompt = """You are a weather expert and activity planner. Analyze the weather data and provide comprehensive recommendations.

Weather Data: {{$weather_data}}
Location: {{$location}}
Activity Type: {{$activity_type}}
Time of Day: {{$time_of_day}}

Please provide a detailed analysis including:

1. **Weather Summary**: Brief overview of current conditions
2. **Activity Recommendations**: Specific activities suitable for these conditions
3. **Safety Considerations**: Any weather-related safety concerns
4. **Alternative Plans**: Backup activities if weather is unfavorable
5. **Best Timing**: Optimal time slots for activities
6. **Preparation Tips**: What to bring or prepare

Format your response as JSON with the following structure:
{
  "weather_summary": "brief description",
  "recommendations": ["activity1", "activity2", "activity3"],
  "safety_notes": ["note1", "note2"],
  "alternatives": ["alternative1", "alternative2"],
  "best_timing": "morning/afternoon/evening",
  "preparation": ["item1", "item2", "item3"],
  "confidence_score": 0-10
}"""
        
        with open(f"{self.prompts_dir}/weather_analysis.skprompt", "w") as f:
            f.write(weather_analysis_prompt)
        
        # Weather Planning Prompt
        weather_planning_prompt = """You are an intelligent weather-based planning assistant. Create a comprehensive plan based on weather conditions.

Current Weather: {{$current_weather}}
Forecast: {{$forecast_data}}
User Preferences: {{$user_preferences}}
Available Time: {{$available_time}}

Create a detailed plan that includes:

1. **Immediate Activities**: What to do right now
2. **Short-term Planning**: Next few hours
3. **Long-term Planning**: Next few days
4. **Calendar Integration**: Suggested calendar events
5. **Resource Requirements**: What's needed for activities
6. **Risk Assessment**: Weather-related risks and mitigations

Provide your response as a structured plan with specific recommendations."""
        
        with open(f"{self.prompts_dir}/weather_planning.skprompt", "w") as f:
            f.write(weather_planning_prompt)
        
        # Activity Suggestion Prompt
        activity_suggestion_prompt = """You are an activity recommendation expert. Suggest activities based on weather and user context.

Weather Conditions: {{$weather_conditions}}
User Interests: {{$user_interests}}
Available Time: {{$available_time}}
Budget Level: {{$budget_level}}
Group Size: {{$group_size}}

Generate personalized activity suggestions that consider:

1. **Weather Appropriateness**: Activities suitable for current conditions
2. **Personal Interests**: Aligned with user preferences
3. **Time Constraints**: Fitting within available time
4. **Budget Considerations**: Within specified budget
5. **Group Dynamics**: Suitable for group size
6. **Location Options**: Indoor/outdoor alternatives

Format as a list of activities with details for each."""
        
        with open(f"{self.prompts_dir}/activity_suggestion.skprompt", "w") as f:
            f.write(activity_suggestion_prompt)
    
    @sk_function(
        description="Analyze weather using semantic function",
        name="semantic_weather_analysis"
    )
    @sk_function_context_parameter(
        name="weather_data",
        description="Weather data to analyze",
        default_value=""
    )
    @sk_function_context_parameter(
        name="location",
        description="Location name",
        default_value="Hanoi"
    )
    @sk_function_context_parameter(
        name="activity_type",
        description="Type of activity",
        default_value="general"
    )
    @sk_function_context_parameter(
        name="time_of_day",
        description="Time of day for activities",
        default_value="afternoon"
    )
    async def semantic_weather_analysis(self, context: SKContext) -> str:
        """Semantic function for weather analysis using prompts"""
        # This would be handled by Semantic Kernel's prompt engine
        # For demo purposes, we'll return a placeholder
        weather_data = context.variables.get("weather_data", "{}")
        location = context.variables.get("location", "Hanoi")
        activity_type = context.variables.get("activity_type", "general")
        time_of_day = context.variables.get("time_of_day", "afternoon")
        
        return f"""
Semantic Weather Analysis for {location}:
- Activity Type: {activity_type}
- Time of Day: {time_of_day}
- Weather Data: {weather_data}

This would be processed by LLM using the weather_analysis.skprompt template.
The LLM would provide creative, context-aware recommendations based on the prompt.
"""
    
    @sk_function(
        description="Create weather-based plans using semantic function",
        name="semantic_weather_planning"
    )
    @sk_function_context_parameter(
        name="current_weather",
        description="Current weather conditions",
        default_value=""
    )
    @sk_function_context_parameter(
        name="forecast_data",
        description="Weather forecast data",
        default_value=""
    )
    @sk_function_context_parameter(
        name="user_preferences",
        description="User activity preferences",
        default_value=""
    )
    async def semantic_weather_planning(self, context: SKContext) -> str:
        """Semantic function for weather-based planning"""
        current_weather = context.variables.get("current_weather", "{}")
        forecast_data = context.variables.get("forecast_data", "{}")
        user_preferences = context.variables.get("user_preferences", "{}")
        
        return f"""
Semantic Weather Planning:
- Current Weather: {current_weather}
- Forecast: {forecast_data}
- User Preferences: {user_preferences}

This would use the weather_planning.skprompt to create comprehensive plans.
The LLM would generate creative, personalized planning suggestions.
"""
    
    @sk_function(
        description="Suggest activities using semantic function",
        name="semantic_activity_suggestion"
    )
    @sk_function_context_parameter(
        name="weather_conditions",
        description="Current weather conditions",
        default_value=""
    )
    @sk_function_context_parameter(
        name="user_interests",
        description="User interests and preferences",
        default_value=""
    )
    @sk_function_context_parameter(
        name="available_time",
        description="Available time for activities",
        default_value="2 hours"
    )
    async def semantic_activity_suggestion(self, context: SKContext) -> str:
        """Semantic function for activity suggestions"""
        weather_conditions = context.variables.get("weather_conditions", "{}")
        user_interests = context.variables.get("user_interests", "{}")
        available_time = context.variables.get("available_time", "2 hours")
        
        return f"""
Semantic Activity Suggestions:
- Weather: {weather_conditions}
- Interests: {user_interests}
- Time Available: {available_time}

This would use the activity_suggestion.skprompt to generate personalized recommendations.
The LLM would consider context and provide creative suggestions.
"""
