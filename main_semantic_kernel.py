#!/usr/bin/env python3
"""
Semantic Kernel Weather & Calendar Agent
Demonstrating Native Functions vs Semantic Functions
"""

import asyncio
import os
import json
from dotenv import load_dotenv

from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from semantic_kernel.planners import ActionPlanner
from semantic_kernel.planners.basic_planner import BasicPlanner

from skills.weather_skill import WeatherSkill
from skills.calendar_skill import CalendarSkill
from skills.weather_semantic_functions import WeatherSemanticFunctions


async def setup_kernel():
    """Setup Semantic Kernel with skills"""
    # Load environment variables
    load_dotenv()
    
    # Initialize kernel
    kernel = Kernel()
    
    # Add OpenAI service
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY not found in environment variables")
    
    service = OpenAIChatCompletion(
        service_id="openai",
        ai_model_id="gpt-3.5-turbo",
        api_key=api_key
    )
    kernel.add_service(service)
    
    # Import native skills
    weather_api_key = os.getenv("WEATHER_API_KEY", "demo_key")
    weather_skill = WeatherSkill(weather_api_key)
    calendar_skill = CalendarSkill()
    
    kernel.import_skill(weather_skill, skill_name="weather")
    kernel.import_skill(calendar_skill, skill_name="calendar")
    
    # Import semantic functions
    semantic_functions = WeatherSemanticFunctions()
    kernel.import_skill(semantic_functions, skill_name="semantic_weather")
    
    return kernel


async def demo_native_functions(kernel):
    """Demo native functions (hard-coded logic)"""
    print("🌤️  === NATIVE FUNCTIONS DEMO ===")
    print("Using hard-coded logic for weather operations\n")
    
    # Get weather using native function
    context = kernel.create_new_context()
    context.variables["location"] = "Hanoi"
    context.variables["units"] = "metric"
    
    weather_result = await kernel.run_async(
        kernel.get_function("weather", "get_weather"),
        context
    )
    
    print("📍 Current Weather (Native Function):")
    print(weather_result.result)
    print("\n" + "="*50 + "\n")


async def demo_semantic_functions(kernel):
    """Demo semantic functions (LLM-powered)"""
    print("🧠 === SEMANTIC FUNCTIONS DEMO ===")
    print("Using LLM-powered prompts for analysis\n")
    
    # Sample weather data for semantic analysis
    sample_weather = {
        "temperature": 25,
        "description": "partly cloudy",
        "humidity": 65,
        "wind_speed": 8
    }
    
    context = kernel.create_new_context()
    context.variables["weather_data"] = json.dumps(sample_weather)
    context.variables["location"] = "Hanoi"
    context.variables["activity_type"] = "outdoor"
    context.variables["time_of_day"] = "afternoon"
    
    semantic_result = await kernel.run_async(
        kernel.get_function("semantic_weather", "semantic_weather_analysis"),
        context
    )
    
    print("🧠 Weather Analysis (Semantic Function):")
    print(semantic_result.result)
    print("\n" + "="*50 + "\n")


async def demo_action_planner(kernel):
    """Demo Semantic Kernel's Action Planner"""
    print("🎯 === ACTION PLANNER DEMO ===")
    print("Using Semantic Kernel's built-in planner\n")
    
    # Create planner
    planner = ActionPlanner(kernel)
    
    # Complex goal that requires multiple skills
    goal = "Check the weather in Hanoi, analyze it for outdoor activities, and create a calendar event for tomorrow afternoon"
    
    print(f"🎯 Goal: {goal}")
    print("\n📋 Generated Plan:")
    
    try:
        # Generate plan
        plan = await planner.create_plan_async(goal)
        
        # Display the plan
        for i, step in enumerate(plan.steps, 1):
            print(f"{i}. {step.name} - {step.description}")
        
        print(f"\n🚀 Executing Plan...")
        
        # Execute the plan
        result = await plan.invoke_async()
        
        print(f"\n✅ Plan Result:")
        print(result.result)
        
    except Exception as e:
        print(f"❌ Planning failed: {str(e)}")
        print("This is expected in demo mode without real API keys")
    
    print("\n" + "="*50 + "\n")


async def demo_skill_chaining(kernel):
    """Demo chaining multiple skills together"""
    print("🔗 === SKILL CHAINING DEMO ===")
    print("Chaining weather and calendar skills\n")
    
    try:
        # Step 1: Get weather
        context1 = kernel.create_new_context()
        context1.variables["location"] = "Hanoi"
        
        weather_result = await kernel.run_async(
            kernel.get_function("weather", "get_weather"),
            context1
        )
        
        print("📍 Step 1: Get Weather")
        print(weather_result.result)
        
        # Step 2: Analyze weather for activities
        context2 = kernel.create_new_context()
        context2.variables["weather_data"] = weather_result.result
        context2.variables["activity_type"] = "outdoor"
        
        analysis_result = await kernel.run_async(
            kernel.get_function("weather", "analyze_weather"),
            context2
        )
        
        print("\n🧠 Step 2: Analyze Weather")
        print(analysis_result.result)
        
        # Step 3: Create calendar event based on weather
        context3 = kernel.create_new_context()
        context3.variables["title"] = "Outdoor Activity - Weather Based"
        context3.variables["start_time"] = "tomorrow 2pm"
        context3.variables["end_time"] = "tomorrow 4pm"
        context3.variables["description"] = "Weather-based outdoor activity"
        context3.variables["weather_based"] = "true"
        
        calendar_result = await kernel.run_async(
            kernel.get_function("calendar", "create_event"),
            context3
        )
        
        print("\n📅 Step 3: Create Calendar Event")
        print(calendar_result.result)
        
    except Exception as e:
        print(f"❌ Skill chaining failed: {str(e)}")
        print("This is expected in demo mode without real API keys")
    
    print("\n" + "="*50 + "\n")


async def compare_native_vs_semantic(kernel):
    """Compare native vs semantic function approaches"""
    print("⚖️  === NATIVE vs SEMANTIC COMPARISON ===")
    
    # Sample data
    weather_data = {
        "temperature": 28,
        "description": "sunny",
        "humidity": 45,
        "wind_speed": 5
    }
    
    print("\n🌡️  Sample Weather Data:")
    print(json.dumps(weather_data, indent=2))
    
    print("\n🔧 NATIVE FUNCTION APPROACH:")
    print("✅ Pros:")
    print("   - Fast execution (no LLM calls)")
    print("   - Deterministic results")
    print("   - Low cost (no token usage)")
    print("   - Reliable and predictable")
    print("   - Good for structured data processing")
    
    print("\n❌ Cons:")
    print("   - Limited flexibility")
    print("   - Hard to modify logic")
    print("   - No natural language understanding")
    print("   - Requires programming skills to change")
    
    print("\n🧠 SEMANTIC FUNCTION APPROACH:")
    print("✅ Pros:")
    print("   - Natural language understanding")
    print("   - Highly flexible and creative")
    print("   - Easy to modify via prompts")
    print("   - Context-aware responses")
    print("   - Can handle complex reasoning")
    
    print("\n❌ Cons:")
    print("   - Slower execution (LLM calls)")
    print("   - Higher cost (token usage)")
    print("   - Less predictable results")
    print("   - Requires prompt engineering")
    print("   - May hallucinate or be inconsistent")
    
    print("\n🎯 WHEN TO USE EACH:")
    print("🔧 Native Functions:")
    print("   - Data processing and calculations")
    print("   - API integrations")
    print("   - Structured operations")
    print("   - Performance-critical tasks")
    
    print("\n🧠 Semantic Functions:")
    print("   - Natural language understanding")
    print("   - Creative content generation")
    print("   - Complex reasoning tasks")
    print("   - User interaction and explanations")
    
    print("\n" + "="*50 + "\n")


async def main():
    """Main demo function"""
    print("🚀 Semantic Kernel Weather & Calendar Agent")
    print("Chapter 5: Empower Agent with Actions")
    print("="*60)
    
    try:
        # Setup kernel
        kernel = await setup_kernel()
        
        # Run demos
        await demo_native_functions(kernel)
        await demo_semantic_functions(kernel)
        await demo_action_planner(kernel)
        await demo_skill_chaining(kernel)
        await compare_native_vs_semantic(kernel)
        
        print("✅ Demo completed successfully!")
        print("\n📚 Key Takeaways:")
        print("1. Native Functions: Fast, reliable, structured")
        print("2. Semantic Functions: Flexible, creative, LLM-powered")
        print("3. Action Planner: Automatically chains skills")
        print("4. Skill Chaining: Manual orchestration of multiple skills")
        print("5. Semantic Kernel: Microsoft's framework for AI agents")
        
    except Exception as e:
        print(f"❌ Demo failed: {str(e)}")
        print("\n💡 Note: Some features require valid API keys to work properly")


if __name__ == "__main__":
    asyncio.run(main())
