import asyncio
import os
import logging
from dotenv import load_dotenv

from openai import AsyncOpenAI
from agents.weather_calendar_agent import WeatherCalendarAgent
from actions.weather_actions import WeatherActions
from actions.calendar_actions import CalendarActions


async def basic_weather_examples():
    """Basic weather checking examples"""
    
    # Load environment variables
    load_dotenv()
    
    # Get API keys
    openai_api_key = os.getenv("OPENAI_API_KEY")
    weather_api_key = os.getenv("WEATHER_API_KEY")
    
    if not openai_api_key or not weather_api_key:
        print("❌ API keys required. Please check your .env file")
        return
    
    # Create agent
    agent = WeatherCalendarAgent("weather_example_agent", "Weather Example Agent", "Agent for weather examples")
    agent.set_openai_client(AsyncOpenAI(api_key=openai_api_key))
    
    # Add permissions and register actions
    agent.add_permission("weather.read")
    weather_actions = WeatherActions(weather_api_key)
    for action in weather_actions.get_all_actions():
        agent.register_action(action)
    
    print("🌤️ Basic Weather Examples")
    print("=" * 40)
    
    # Example 1: Current weather
    print("\n1️⃣ Current weather check:")
    result = await agent.execute("What's the weather like in Hanoi right now?")
    print(f"Result: {result}")
    
    # Example 2: Weather forecast
    print("\n2️⃣ Weather forecast:")
    result = await agent.execute("Get a 5-day weather forecast for Ho Chi Minh City")
    print(f"Result: {result}")
    
    # Example 3: Weather analysis
    print("\n3️⃣ Weather analysis:")
    result = await agent.execute("Analyze the weather in Da Nang for outdoor activities")
    print(f"Result: {result}")


async def calendar_examples():
    """Calendar management examples"""
    
    # Load environment variables
    load_dotenv()
    
    # Get API keys
    openai_api_key = os.getenv("OPENAI_API_KEY")
    weather_api_key = os.getenv("WEATHER_API_KEY")
    
    if not openai_api_key or not weather_api_key:
        print("❌ API keys required. Please check your .env file")
        return
    
    # Create agent
    agent = WeatherCalendarAgent("calendar_example_agent", "Calendar Example Agent", "Agent for calendar examples")
    agent.set_openai_client(AsyncOpenAI(api_key=openai_api_key))
    
    # Add permissions and register actions
    agent.add_permission("calendar.read")
    agent.add_permission("calendar.write")
    agent.add_permission("weather.read")
    
    weather_actions = WeatherActions(weather_api_key)
    for action in weather_actions.get_all_actions():
        agent.register_action(action)
    
    calendar_actions = CalendarActions()
    for action in calendar_actions.get_all_actions():
        agent.register_action(action)
    
    print("\n📅 Calendar Examples")
    print("=" * 40)
    
    # Example 1: Create event
    print("\n1️⃣ Create calendar event:")
    result = await agent.execute("Create an event called 'Morning Walk' for tomorrow at 7 AM")
    print(f"Result: {result}")
    
    # Example 2: List events
    print("\n2️⃣ List calendar events:")
    result = await agent.execute("Show me all my calendar events")
    print(f"Result: {result}")
    
    # Example 3: Create weather-based event
    print("\n3️⃣ Create weather-based event:")
    result = await agent.execute("Create an outdoor picnic event for this weekend if the weather is good")
    print(f"Result: {result}")


async def combined_workflow_examples():
    """Combined weather and calendar workflow examples"""
    
    # Load environment variables
    load_dotenv()
    
    # Get API keys
    openai_api_key = os.getenv("OPENAI_API_KEY")
    weather_api_key = os.getenv("WEATHER_API_KEY")
    
    if not openai_api_key or not weather_api_key:
        print("❌ API keys required. Please check your .env file")
        return
    
    # Create agent
    agent = WeatherCalendarAgent("workflow_example_agent", "Workflow Example Agent", "Agent for workflow examples")
    agent.set_openai_client(AsyncOpenAI(api_key=openai_api_key))
    
    # Add permissions and register actions
    agent.add_permission("weather.read")
    agent.add_permission("weather.analyze")
    agent.add_permission("calendar.read")
    agent.add_permission("calendar.write")
    
    weather_actions = WeatherActions(weather_api_key)
    for action in weather_actions.get_all_actions():
        agent.register_action(action)
    
    calendar_actions = CalendarActions()
    for action in calendar_actions.get_all_actions():
        agent.register_action(action)
    
    print("\n🔄 Combined Workflow Examples")
    print("=" * 40)
    
    # Example 1: Weather-based planning
    print("\n1️⃣ Weather-based planning:")
    result = await agent.weather_based_planning("Hanoi", 3)
    print(f"Result: {result}")
    
    # Example 2: Activity recommendations
    print("\n2️⃣ Activity recommendations:")
    result = await agent.execute("""
        Check the weather in Ho Chi Minh City and suggest 
        appropriate activities for this weekend. Create calendar 
        events for the best activities.
    """)
    print(f"Result: {result}")
    
    # Example 3: Complex workflow
    print("\n3️⃣ Complex workflow:")
    result = await agent.execute("""
        For the next 5 days in Da Nang:
        1. Check the weather forecast
        2. Create outdoor activities on sunny days
        3. Create indoor activities on rainy days
        4. List all created events
    """)
    print(f"Result: {result}")


async def advanced_examples():
    """Advanced usage examples"""
    
    # Load environment variables
    load_dotenv()
    
    # Get API keys
    openai_api_key = os.getenv("OPENAI_API_KEY")
    weather_api_key = os.getenv("WEATHER_API_KEY")
    
    if not openai_api_key or not weather_api_key:
        print("❌ API keys required. Please check your .env file")
        return
    
    # Create agent
    agent = WeatherCalendarAgent("advanced_example_agent", "Advanced Example Agent", "Agent for advanced examples")
    agent.set_openai_client(AsyncOpenAI(api_key=openai_api_key))
    
    # Add permissions and register actions
    agent.add_permission("weather.read")
    agent.add_permission("weather.analyze")
    agent.add_permission("calendar.read")
    agent.add_permission("calendar.write")
    
    weather_actions = WeatherActions(weather_api_key)
    for action in weather_actions.get_all_actions():
        agent.register_action(action)
    
    calendar_actions = CalendarActions()
    for action in calendar_actions.get_all_actions():
        agent.register_action(action)
    
    print("\n🚀 Advanced Examples")
    print("=" * 40)
    
    # Example 1: Direct action execution
    print("\n1️⃣ Direct action execution:")
    result = await agent.execute_direct_action("get_weather", {"location": "Hanoi"})
    print(f"Weather data: {result.data}")
    
    # Example 2: Multiple locations
    print("\n2️⃣ Multiple locations:")
    cities = ["Hanoi", "Ho Chi Minh City", "Da Nang"]
    for city in cities:
        result = await agent.execute(f"Check weather in {city}")
        print(f"{city}: {result}")
    
    # Example 3: Error handling
    print("\n3️⃣ Error handling:")
    result = await agent.execute("Check weather in NonExistentCity123")
    print(f"Error result: {result}")


async def main():
    """Run all examples"""
    print("🌤️ Weather & Calendar Agent Examples - Chapter 5: Empower Agent with Actions")
    print("=" * 80)
    
    # Run basic weather examples
    await basic_weather_examples()
    
    # Run calendar examples
    await calendar_examples()
    
    # Run combined workflow examples
    await combined_workflow_examples()
    
    # Run advanced examples
    await advanced_examples()
    
    print("\n🎉 All examples completed successfully!")
    print("\n💡 Key takeaways:")
    print("   - Agents can fetch real-time weather data from APIs")
    print("   - Agents can create and manage calendar events")
    print("   - Agents can combine multiple actions for complex workflows")
    print("   - Weather-based decision making is now automated")
    print("   - Natural language processing enables intuitive interaction")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run the examples
    asyncio.run(main())

