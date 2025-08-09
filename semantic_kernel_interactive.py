#!/usr/bin/env python3
"""
Semantic Kernel Interactive Weather Agent
Chapter 5: Empower Agent with Actions

Sử dụng Semantic Kernel với LLM-powered parsing
"""

import asyncio
import aiohttp
import os
import json
from datetime import datetime
from dotenv import load_dotenv
from openai import AsyncOpenAI

class SemanticKernelAgent:
    """Semantic Kernel agent với LLM-powered parsing"""
    
    def __init__(self):
        load_dotenv()
        self.weather_api_key = os.getenv("WEATHER_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        self.base_url = "http://api.openweathermap.org/data/2.5"
        self.session = None
        
        if not self.weather_api_key:
            print("❌ WEATHER_API_KEY not found in .env file")
            return
        
        if not self.openai_api_key:
            print("❌ OPENAI_API_KEY not found in .env file")
            print("⚠️ Will use fallback native parsing")
            self.use_llm = False
        else:
            self.client = AsyncOpenAI(api_key=self.openai_api_key)
            self.use_llm = True
        
        print("🧠 Semantic Kernel Interactive Weather Agent")
        print("Chapter 5: Empower Agent with Actions")
        print("=" * 60)
        print("✅ Agent initialized!")
        print(f"🤖 LLM Parsing: {'✅ Enabled' if self.use_llm else '❌ Disabled (fallback to native)'}")
        print()
        print("🌤️ Try these natural language commands:")
        print("   • 'What's the weather like in Hanoi?'")
        print("   • 'Should I bring an umbrella to Ho Chi Minh City?'")
        print("   • 'Get me a 3-day forecast for Da Nang'")
        print("   • 'Is it a good day for outdoor activities in Bangkok?'")
        print("   • 'What should I pack for my trip to Singapore?'")
        print("   • 'help' - Show all commands")
        print("   • 'quit' - Exit")
        print()
        print("🚀 Start chatting with the agent below:")
        print()
    
    async def __aenter__(self):
        self.session = aiohttp.ClientSession()
        return self
        
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if self.session:
            await self.session.close()
    
    async def parse_with_llm(self, user_input: str) -> dict:
        """Parse user input using LLM (Semantic Function)"""
        prompt = f"""
You are a weather assistant. Parse this user input and extract the user's intent.

User input: "{user_input}"

Available actions:
1. get_weather - Get current weather for a location
2. get_forecast - Get weather forecast for a location

Respond in JSON format only:
{{
    "action": "get_weather|get_forecast",
    "location": "city_name",
    "days": number (only for forecast, default 5),
    "intent": "brief description of what user wants"
}}

Examples:
- "What's the weather like in Hanoi?" → {{"action": "get_weather", "location": "Hanoi", "intent": "check current weather"}}
- "Get me a 3-day forecast for Ho Chi Minh City" → {{"action": "get_forecast", "location": "Ho Chi Minh City", "days": 3, "intent": "get 3-day forecast"}}
- "Should I bring an umbrella?" → {{"action": "get_weather", "location": "Hanoi", "intent": "check if umbrella needed"}}

JSON response:
"""
        
        try:
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are a helpful weather assistant. Always respond with valid JSON only."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=200
            )
            
            content = response.choices[0].message.content.strip()
            # Extract JSON from response
            if content.startswith('```json'):
                content = content[7:-3]
            elif content.startswith('```'):
                content = content[3:-3]
            
            return json.loads(content)
            
        except Exception as e:
            print(f"⚠️ LLM parsing failed: {str(e)}")
            return None
    
    def parse_native_fallback(self, user_input: str) -> dict:
        """Native parsing fallback (when LLM fails)"""
        user_input = user_input.lower()
        
        # Simple keyword matching
        if 'weather' in user_input:
            cities = ['hanoi', 'ho chi minh', 'da nang', 'bangkok', 'singapore', 'tokyo']
            for city in cities:
                if city in user_input:
                    return {
                        "action": "get_weather",
                        "location": city,
                        "intent": "check current weather"
                    }
        
        if 'forecast' in user_input:
            cities = ['hanoi', 'ho chi minh', 'da nang', 'bangkok', 'singapore', 'tokyo']
            for city in cities:
                if city in user_input:
                    days = 5
                    if '3' in user_input:
                        days = 3
                    return {
                        "action": "get_forecast",
                        "location": city,
                        "days": days,
                        "intent": "get weather forecast"
                    }
        
        return None
    
    async def get_weather(self, location: str) -> str:
        """Get current weather"""
        url = f"{self.base_url}/weather"
        params = {
            "q": location,
            "appid": self.weather_api_key,
            "units": "metric"
        }
        
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    temp = data["main"]["temp"]
                    description = data["weather"][0]["description"]
                    humidity = data["main"]["humidity"]
                    wind = data["wind"]["speed"]
                    feels_like = data["main"]["feels_like"]
                    
                    # Enhanced response with recommendations
                    response = f"🌤️ {location}: {temp}°C (feels like {feels_like}°C)\n☁️ {description}\n💧 Humidity: {humidity}%\n💨 Wind: {wind} m/s\n"
                    
                    # Add recommendations based on weather
                    if 'rain' in description.lower():
                        response += "🌂 Recommendation: Bring an umbrella!\n"
                    elif temp > 30:
                        response += "🥤 Recommendation: Stay hydrated, it's hot!\n"
                    elif temp < 15:
                        response += "🧥 Recommendation: Wear warm clothes!\n"
                    else:
                        response += "😊 Great weather for outdoor activities!\n"
                    
                    return response
                else:
                    return f"❌ Sorry, I couldn't find weather data for '{location}'. Try a different city name."
        except Exception as e:
            return f"❌ Sorry, there was an error getting weather for '{location}': {str(e)}"
    
    async def get_forecast(self, location: str, days: int = 5) -> str:
        """Get weather forecast"""
        url = f"{self.base_url}/forecast"
        params = {
            "q": location,
            "appid": self.weather_api_key,
            "units": "metric",
            "cnt": days * 8
        }
        
        try:
            async with self.session.get(url, params=params) as response:
                if response.status == 200:
                    data = await response.json()
                    
                    result = f"📅 {days}-day forecast for {location}:\n"
                    
                    # Group by day
                    daily_data = {}
                    for item in data["list"]:
                        date = datetime.fromtimestamp(item["dt"]).strftime("%Y-%m-%d")
                        if date not in daily_data:
                            daily_data[date] = {
                                "temp_min": item["main"]["temp_min"],
                                "temp_max": item["main"]["temp_max"],
                                "description": item["weather"][0]["description"],
                                "rain_prob": item.get("pop", 0) * 100
                            }
                        else:
                            daily_data[date]["temp_min"] = min(daily_data[date]["temp_min"], item["main"]["temp_min"])
                            daily_data[date]["temp_max"] = max(daily_data[date]["temp_max"], item["main"]["temp_max"])
                    
                    for date, info in list(daily_data.items())[:days]:
                        day_name = datetime.strptime(date, "%Y-%m-%d").strftime("%A")
                        result += f"   📅 {day_name}: {info['temp_min']:.1f}°C - {info['temp_max']:.1f}°C\n"
                        result += f"      {info['description']} | 🌧️ {info['rain_prob']:.0f}% chance of rain\n"
                    
                    # Add overall recommendation
                    avg_temp = sum([(info['temp_min'] + info['temp_max'])/2 for info in daily_data.values()]) / len(daily_data)
                    if avg_temp > 30:
                        result += "\n🌡️ Overall: Hot weather expected, plan indoor activities during peak hours.\n"
                    elif avg_temp < 15:
                        result += "\n❄️ Overall: Cool weather expected, bring warm clothes.\n"
                    else:
                        result += "\n😊 Overall: Pleasant weather for outdoor activities!\n"
                    
                    return result
                else:
                    return f"❌ Sorry, I couldn't find forecast data for '{location}'. Try a different city name."
        except Exception as e:
            return f"❌ Sorry, there was an error getting forecast for '{location}': {str(e)}"
    
    def show_help(self):
        """Show help"""
        print("\n📚 HELP - Natural Language Commands:")
        print("=" * 50)
        print("🌤️ Weather Questions:")
        print("   • 'What's the weather like in [city]?'")
        print("   • 'How's the weather in [city] today?'")
        print("   • 'Should I bring an umbrella to [city]?'")
        print("   • 'Is it raining in [city]?'")
        print()
        print("📅 Forecast Questions:")
        print("   • 'Get me a [X]-day forecast for [city]'")
        print("   • 'What's the weather forecast for [city]?'")
        print("   • 'Tell me about the weather in [city] this week'")
        print()
        print("🎯 Activity Planning:")
        print("   • 'Is it a good day for outdoor activities in [city]?'")
        print("   • 'What should I pack for my trip to [city]?'")
        print("   • 'Can I go hiking in [city] today?'")
        print()
        print("🌍 Supported Cities:")
        print("   • Hanoi, Ho Chi Minh City, Da Nang (Vietnam)")
        print("   • Bangkok (Thailand), Singapore, Tokyo (Japan)")
        print()
        print("⚙️ System Commands:")
        print("   • help - Show this help")
        print("   • quit/exit - Exit the agent")
        print()
        print("💡 Tips:")
        print("   • Use natural language - I understand context!")
        print("   • Ask for recommendations and advice")
        print("   • I'll provide weather-based suggestions")
        print()
    
    async def process_command(self, user_input: str) -> str:
        """Process user command using Semantic Kernel"""
        user_input = user_input.strip()
        
        # Handle system commands
        if user_input.lower() in ['quit', 'exit', 'bye']:
            return "👋 Goodbye! Thanks for chatting with me!"
        
        if user_input.lower() in ['help', '?']:
            self.show_help()
            return "📚 Help displayed above!"
        
        # Parse with LLM (Semantic Function) or fallback to native
        if self.use_llm:
            print("🧠 Using LLM to understand your request...")
            parsed = await self.parse_with_llm(user_input)
            if not parsed:
                print("⚠️ LLM parsing failed, using native fallback...")
                parsed = self.parse_native_fallback(user_input)
        else:
            print("🔧 Using native parsing...")
            parsed = self.parse_native_fallback(user_input)
        
        if not parsed:
            return "🤔 I'm not sure what you mean. Try:\n• 'What's the weather like in Hanoi?'\n• 'Get me a 3-day forecast for Ho Chi Minh City'\n• Type 'help' for more options"
        
        # Execute the parsed action
        print(f"🎯 Understanding: {parsed['intent']}")
        
        if parsed["action"] == "get_weather":
            return await self.get_weather(parsed["location"])
        elif parsed["action"] == "get_forecast":
            days = parsed.get("days", 5)
            return await self.get_forecast(parsed["location"], days)
        else:
            return "❌ I understand what you want, but I can only help with weather and forecast requests."
    
    async def chat_loop(self):
        """Main interactive chat loop"""
        print("🚀 Agent is ready! Start chatting...")
        print()
        
        async with self:
            while True:
                try:
                    # Get user input
                    user_input = input("👤 You: ").strip()
                    
                    if not user_input:
                        continue
                    
                    # Process the command
                    print("🤖 Agent: ", end="", flush=True)
                    response = await self.process_command(user_input)
                    print(response)
                    print()
                    
                except KeyboardInterrupt:
                    print("\n👋 Goodbye! Thanks for chatting with me!")
                    break
                except Exception as e:
                    print(f"❌ Unexpected error: {str(e)}")
                    print()

async def main():
    """Main function"""
    agent = SemanticKernelAgent()
    await agent.chat_loop()

if __name__ == "__main__":
    asyncio.run(main())
