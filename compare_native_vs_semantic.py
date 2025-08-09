#!/usr/bin/env python3
"""
Compare Native Function vs Semantic Kernel
Chapter 5: Empower Agent with Actions

Demo so sánh 2 approaches để hiểu rõ sự khác biệt
"""

import asyncio
import aiohttp
import os
from datetime import datetime
from dotenv import load_dotenv

class NativeFunctionAgent:
    """Native Function Agent - Hard-coded rules"""
    
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("WEATHER_API_KEY")
        self.base_url = "http://api.openweathermap.org/data/2.5"
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def parse_command(self, user_input: str) -> dict:
        """Native parsing - Hard-coded rules"""
        user_input = user_input.lower()
        
        # Rule 1: Exact command matching
        if user_input.startswith('weather '):
            location = user_input.replace('weather ', '').strip()
            return {
                "action": "get_weather",
                "location": location,
                "method": "exact_command",
                "confidence": "high"
            }
        
        # Rule 2: Keyword matching
        if 'weather' in user_input:
            cities = ['hanoi', 'ho chi minh', 'da nang']
            for city in cities:
                if city in user_input:
                    return {
                        "action": "get_weather",
                        "location": city,
                        "method": "keyword_matching",
                        "confidence": "medium"
                    }
        
        # Rule 3: Forecast matching
        if user_input.startswith('forecast '):
            parts = user_input.replace('forecast ', '').split()
            if len(parts) >= 1:
                location = parts[0]
                days = int(parts[1]) if len(parts) > 1 else 5
                return {
                    "action": "get_forecast",
                    "location": location,
                    "days": days,
                    "method": "exact_command",
                    "confidence": "high"
                }
        
        return None
    
    async def get_weather(self, location: str) -> str:
        """Get current weather"""
        url = f"{self.base_url}/weather"
        params = {
            "q": location,
            "appid": self.api_key,
            "units": "metric"
        }
        
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    temp = data["main"]["temp"]
                    description = data["weather"][0]["description"]
                    return f"🌤️ {location}: {temp}°C, {description}"
                else:
                    return f"❌ Error: Could not get weather for {location}"
        except Exception as e:
            return f"❌ Error: {str(e)}"

class SemanticKernelAgent:
    """Semantic Kernel Agent - LLM-powered understanding"""
    
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("WEATHER_API_KEY")
        self.base_url = "http://api.openweathermap.org/data/2.5"
        self.session = None
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    def parse_command(self, user_input: str) -> dict:
        """Semantic parsing - Simulated LLM understanding"""
        user_input = user_input.lower()
        
        # Simulate LLM understanding with more flexible patterns
        if any(word in user_input for word in ['weather', 'temperature', 'climate', 'hot', 'cold', 'rain', 'sunny']):
            # Extract location from various patterns
            cities = ['hanoi', 'ho chi minh', 'da nang', 'bangkok', 'singapore']
            found_city = None
            
            for city in cities:
                if city in user_input:
                    found_city = city
                    break
            
            if found_city:
                return {
                    "action": "get_weather",
                    "location": found_city,
                    "method": "semantic_understanding",
                    "confidence": "high",
                    "understanding": f"User wants weather info for {found_city}"
                }
        
        if any(word in user_input for word in ['forecast', 'prediction', 'week', 'days', 'future']):
            cities = ['hanoi', 'ho chi minh', 'da nang', 'bangkok', 'singapore']
            found_city = None
            
            for city in cities:
                if city in user_input:
                    found_city = city
                    break
            
            if found_city:
                # Extract days from natural language
                days = 5
                if '3' in user_input or 'three' in user_input:
                    days = 3
                elif '7' in user_input or 'week' in user_input:
                    days = 7
                
                return {
                    "action": "get_forecast",
                    "location": found_city,
                    "days": days,
                    "method": "semantic_understanding",
                    "confidence": "high",
                    "understanding": f"User wants {days}-day forecast for {found_city}"
                }
        
        return None
    
    async def get_weather(self, location: str) -> str:
        """Get current weather"""
        url = f"{self.base_url}/weather"
        params = {
            "q": location,
            "appid": self.api_key,
            "units": "metric"
        }
        
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    temp = data["main"]["temp"]
                    description = data["weather"][0]["description"]
                    feels_like = data["main"]["feels_like"]
                    
                    # Enhanced response with recommendations
                    response = f"🌤️ {location}: {temp}°C (feels like {feels_like}°C)\n☁️ {description}\n"
                    
                    if 'rain' in description.lower():
                        response += "🌂 Recommendation: Bring an umbrella!\n"
                    elif temp > 30:
                        response += "🥤 Recommendation: Stay hydrated!\n"
                    else:
                        response += "😊 Great weather for activities!\n"
                    
                    return response
                else:
                    return f"❌ Error: Could not get weather for {location}"
        except Exception as e:
            return f"❌ Error: {str(e)}"

async def compare_approaches():
    """Compare Native Function vs Semantic Kernel approaches"""
    
    print("🔍 Comparing Native Function vs Semantic Kernel")
    print("Chapter 5: Empower Agent with Actions")
    print("=" * 60)
    print()
    
    # Test cases
    test_cases = [
        "weather Hanoi",
        "What's the weather like in Ho Chi Minh City?",
        "forecast Da Nang 3",
        "Get me a 3-day forecast for Bangkok",
        "Is it raining in Singapore?",
        "How hot is it in Tokyo?",
        "Tell me about the weather in Hanoi",
        "wea hcm",  # Abbreviated
        "thời tiết đà nẵng",  # Vietnamese
        "What should I pack for my trip to Bangkok?"
    ]
    
    async with NativeFunctionAgent() as native_agent, SemanticKernelAgent() as semantic_agent:
        
        for i, test_input in enumerate(test_cases, 1):
            print(f"🧪 Test {i}: '{test_input}'")
            print("-" * 50)
            
            # Native Function approach
            print("🔧 Native Function:")
            native_result = native_agent.parse_command(test_input)
            if native_result:
                print(f"   ✅ Parsed: {native_result}")
                if native_result["action"] == "get_weather":
                    weather = await native_agent.get_weather(native_result["location"])
                    print(f"   📊 Result: {weather}")
            else:
                print("   ❌ Could not understand")
            
            print()
            
            # Semantic Kernel approach
            print("🧠 Semantic Kernel:")
            semantic_result = semantic_agent.parse_command(test_input)
            if semantic_result:
                print(f"   ✅ Parsed: {semantic_result}")
                if semantic_result["action"] == "get_weather":
                    weather = await semantic_agent.get_weather(semantic_result["location"])
                    print(f"   📊 Result: {weather}")
            else:
                print("   ❌ Could not understand")
            
            print()
            print("=" * 60)
            print()
    
    # Summary comparison
    print("📊 SUMMARY COMPARISON:")
    print("=" * 40)
    print()
    print("🔧 NATIVE FUNCTION:")
    print("✅ Pros:")
    print("   • Fast execution (no LLM calls)")
    print("   • Deterministic results")
    print("   • Low cost (no token usage)")
    print("   • Reliable and predictable")
    print("   • Good for structured commands")
    print()
    print("❌ Cons:")
    print("   • Limited flexibility")
    print("   • Hard to modify logic")
    print("   • No natural language understanding")
    print("   • Requires exact command format")
    print("   • Cannot handle variations well")
    print()
    print("🧠 SEMANTIC KERNEL:")
    print("✅ Pros:")
    print("   • Natural language understanding")
    print("   • Highly flexible and creative")
    print("   • Easy to modify via prompts")
    print("   • Context-aware responses")
    print("   • Can handle complex reasoning")
    print("   • Understands variations and synonyms")
    print()
    print("❌ Cons:")
    print("   • Slower execution (LLM calls)")
    print("   • Higher cost (token usage)")
    print("   • Less predictable results")
    print("   • Requires prompt engineering")
    print("   • May hallucinate or be inconsistent")
    print()
    print("🎯 WHEN TO USE EACH:")
    print("🔧 Native Functions:")
    print("   • Simple, structured commands")
    print("   • Performance-critical applications")
    print("   • Cost-sensitive projects")
    print("   • Deterministic requirements")
    print()
    print("🧠 Semantic Functions:")
    print("   • Natural language interfaces")
    print("   • Complex user interactions")
    print("   • Creative content generation")
    print("   • Flexible reasoning tasks")
    print()
    print("💡 For Chapter 5: Empower Agent with Actions")
    print("   • Start with Native Functions for core actions")
    print("   • Add Semantic Functions for natural language")
    print("   • Combine both for best user experience")
    print("   • Use fallback mechanisms for reliability")

if __name__ == "__main__":
    asyncio.run(compare_approaches())
