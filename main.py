import asyncio
import os
import logging
from dotenv import load_dotenv

from openai import AsyncOpenAI
from agents.weather_calendar_agent import WeatherCalendarAgent
from actions.weather_actions import WeatherActions
from actions.calendar_actions import CalendarActions


async def main():
    # Load environment variables
    load_dotenv()
    
    # Get API keys
    openai_api_key = os.getenv("OPENAI_API_KEY")
    weather_api_key = os.getenv("WEATHER_API_KEY")
    
    if not openai_api_key:
        print("❌ OPENAI_API_KEY environment variable is required")
        print("Please create a .env file with your OpenAI API key")
        return
    
    if not weather_api_key:
        print("❌ WEATHER_API_KEY environment variable is required")
        print("Please get a free API key from https://openweathermap.org/api")
        return
    
    # Create OpenAI client
    client = AsyncOpenAI(api_key=openai_api_key)
    
    # Create weather calendar agent
    agent = WeatherCalendarAgent("weather_calendar_agent", "Weather Calendar Agent", "Agent for weather and calendar management")
    agent.set_openai_client(client)
    
    # Add permissions
    agent.add_permission("weather.read")
    agent.add_permission("weather.analyze")
    agent.add_permission("calendar.read")
    agent.add_permission("calendar.write")
    
    # Register weather actions
    weather_actions = WeatherActions(weather_api_key)
    for action in weather_actions.get_all_actions():
        agent.register_action(action)
    
    # Register calendar actions
    calendar_actions = CalendarActions()
    for action in calendar_actions.get_all_actions():
        agent.register_action(action)
    
    # Demo the system
    print("🌤️ Weather & Calendar Agent Demo - Chapter 5: Empower Agent with Actions")
    print("=" * 70)
    
    # Demo 1: Check current weather
    print("\n🌡️ Demo 1: Check current weather")
    result = await agent.execute("Check the weather in Hanoi, Vietnam")
    print(f"Result: {result}")
    
    # Demo 2: Get weather forecast
    print("\n📅 Demo 2: Get weather forecast")
    result = await agent.execute("Get weather forecast for Hanoi for the next 3 days")
    print(f"Result: {result}")
    
    # Demo 3: Create a calendar event
    print("\n📅 Demo 3: Create a calendar event")
    result = await agent.execute("Create an event called 'Team Meeting' for tomorrow at 2 PM")
    print(f"Result: {result}")
    
    # Demo 4: List calendar events
    print("\n📋 Demo 4: List calendar events")
    result = await agent.execute("Show me all calendar events")
    print(f"Result: {result}")
    
    # Demo 5: Weather-based planning
    print("\n🎯 Demo 5: Weather-based planning")
    result = await agent.weather_based_planning("Hanoi", 3)
    print(f"Result: {result}")
    
    # Demo 6: Activity suggestions
    print("\n🎯 Demo 6: Activity suggestions")
    result = await agent.execute("What activities would you recommend for today in Hanoi? Check the weather and suggest appropriate activities")
    print(f"Result: {result}")
    
    # Demo 7: Complex workflow
    print("\n🔄 Demo 7: Complex workflow")
    result = await agent.execute("""
        Check the weather in Hanoi for the next 2 days,
        and create calendar events for outdoor activities 
        when the weather is good (sunny, no rain, temperature between 15-30°C)
    """)
    print(f"Result: {result}")
    
    # Show available actions
    print("\n🔧 Available Actions:")
    available_actions = agent.list_available_actions()
    for action in available_actions:
        print(f"- {action.name}: {action.description} (Type: {action.type}, Permission: {action.permission_level})")
    
    print("\n✅ Demo completed! The agent successfully performed weather and calendar operations.")
    print("\n💡 This demonstrates how agents can be empowered with real-world API integrations")
    print("   to perform complex tasks like weather-based calendar planning!")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run the demo
    asyncio.run(main())
