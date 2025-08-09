#!/usr/bin/env python3
"""
Semantic Kernel Interactive Weather Agent
Chapter 5: Empower Agent with Actions

Sử dụng Semantic Kernel framework thực sự với LLM-powered parsing
"""

import asyncio
import aiohttp
import os
import json
from datetime import datetime
from dotenv import load_dotenv
from semantic_kernel import Kernel
from semantic_kernel.functions import kernel_function
from semantic_kernel.functions import kernel_arguments
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion

class WeatherPlugin:
    """Weather plugin cho Semantic Kernel"""
    
    def __init__(self, weather_api_key: str):
        self.weather_api_key = weather_api_key
        self.base_url = "http://api.openweathermap.org/data/2.5"
    
    @kernel_function(
        description="Get current weather for a location",
        name="get_weather"
    )
    async def get_weather(self, location: str) -> str:
        """Get current weather using OpenWeatherMap API"""
        try:
            # Geocoding first
            geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={location}&limit=1&appid={self.weather_api_key}"
            async with aiohttp.ClientSession() as session:
                async with session.get(geo_url) as response:
                    if response.status != 200:
                        return f"❌ Error getting coordinates for {location}"
                    
                    geo_data = await response.json()
                    if not geo_data:
                        return f"❌ Location '{location}' not found"
                    
                    lat, lon = geo_data[0]['lat'], geo_data[0]['lon']
                    
                    # Get weather data
                    weather_url = f"{self.base_url}/weather?lat={lat}&lon={lon}&appid={self.weather_api_key}&units=metric&lang=vi"
                    async with session.get(weather_url) as weather_response:
                        if weather_response.status != 200:
                            return f"❌ Error getting weather for {location}"
                        
                        weather_data = await weather_response.json()
                        
                        temp = weather_data['main']['temp']
                        feels_like = weather_data['main']['feels_like']
                        humidity = weather_data['main']['humidity']
                        wind_speed = weather_data['wind']['speed']
                        description = weather_data['weather'][0]['description']
                        
                        # Recommendation logic
                        recommendation = ""
                        if 'rain' in description.lower():
                            recommendation = "🌂 Bring an umbrella!"
                        elif temp > 30:
                            recommendation = "🥵 Stay hydrated, avoid peak sun hours!"
                        elif temp < 15:
                            recommendation = "🧥 Bring a jacket!"
                        else:
                            recommendation = "😊 Nice weather for outdoor activities!"
                        
                        return f"""🌤️ {location}: {temp}°C (feels like {feels_like}°C)
☁️ {description}
💧 Humidity: {humidity}%
💨 Wind: {wind_speed} m/s
{recommendation}"""
                        
        except Exception as e:
            return f"❌ Error: {str(e)}"
    
    @kernel_function(
        description="Get weather forecast for a location",
        name="get_forecast"
    )
    async def get_forecast(self, location: str, days: int = 5) -> str:
        """Get weather forecast using OpenWeatherMap API"""
        try:
            # Geocoding first
            geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={location}&limit=1&appid={self.weather_api_key}"
            async with aiohttp.ClientSession() as session:
                async with session.get(geo_url) as response:
                    if response.status != 200:
                        return f"❌ Error getting coordinates for {location}"
                    
                    geo_data = await response.json()
                    if not geo_data:
                        return f"❌ Location '{location}' not found"
                    
                    lat, lon = geo_data[0]['lat'], geo_data[0]['lon']
                    
                    # Get forecast data
                    forecast_url = f"{self.base_url}/forecast?lat={lat}&lon={lon}&appid={self.weather_api_key}&units=metric&lang=vi"
                    async with session.get(forecast_url) as forecast_response:
                        if forecast_response.status != 200:
                            return f"❌ Error getting forecast for {location}"
                        
                        forecast_data = await forecast_response.json()
                        
                        # Group by day
                        daily_forecasts = {}
                        for item in forecast_data['list']:
                            date = datetime.fromtimestamp(item['dt']).strftime('%A')
                            if date not in daily_forecasts:
                                daily_forecasts[date] = {
                                    'min_temp': float('inf'),
                                    'max_temp': float('-inf'),
                                    'description': item['weather'][0]['description'],
                                    'rain_chance': item.get('pop', 0) * 100
                                }
                            
                            temp = item['main']['temp']
                            daily_forecasts[date]['min_temp'] = min(daily_forecasts[date]['min_temp'], temp)
                            daily_forecasts[date]['max_temp'] = max(daily_forecasts[date]['max_temp'], temp)
                        
                        # Format output
                        result = f"📅 {days}-day forecast for {location}:\n"
                        count = 0
                        for day, data in list(daily_forecasts.items())[:days]:
                            count += 1
                            result += f"   📅 {day}: {data['min_temp']:.1f}°C - {data['max_temp']:.1f}°C\n"
                            result += f"      {data['description']} | 🌧️ {data['rain_chance']:.0f}% chance of rain\n"
                        
                        # Overall recommendation
                        avg_temp = sum([(d['min_temp'] + d['max_temp'])/2 for d in list(daily_forecasts.values())[:days]]) / min(days, len(daily_forecasts))
                        if avg_temp > 30:
                            result += "\n🌡️ Overall: Hot weather expected, plan indoor activities during peak hours."
                        elif avg_temp < 15:
                            result += "\n🌡️ Overall: Cool weather, good for outdoor activities."
                        else:
                            result += "\n🌡️ Overall: Pleasant weather, great for outdoor activities."
                        
                        return result
                        
        except Exception as e:
            return f"❌ Error: {str(e)}"

class SemanticKernelAgent:
    """Semantic Kernel agent thực sự sử dụng framework"""
    
    def __init__(self):
        load_dotenv()
        self.weather_api_key = os.getenv("WEATHER_API_KEY")
        self.openai_api_key = os.getenv("OPENAI_API_KEY")
        
        if not self.weather_api_key:
            print("❌ WEATHER_API_KEY not found in .env file")
            return
        
        if not self.openai_api_key:
            print("❌ OPENAI_API_KEY not found in .env file")
            print("⚠️ Cannot initialize Semantic Kernel without OpenAI API key")
            return
        
        # Initialize Semantic Kernel
        self.kernel = Kernel()
        
        # Add OpenAI chat completion service
        self.kernel.add_service(
            OpenAIChatCompletion(
                service_id="chat",
                ai_model_id="gpt-3.5-turbo",
                api_key=self.openai_api_key
            )
        )
        
        # Add weather plugin
        weather_plugin = WeatherPlugin(self.weather_api_key)
        self.kernel.add_plugin(weather_plugin, "weather")
        
        # Add semantic functions for intent parsing
        self._add_semantic_functions()
        
        print("🧠 Semantic Kernel Interactive Weather Agent")
        print("Chapter 5: Empower Agent with Actions")
        print("=" * 60)
        print("✅ Agent initialized with Semantic Kernel!")
        print("🤖 LLM Parsing: ✅ Enabled")
        print("🔌 Plugins: weather")
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
    
    def _add_semantic_functions(self):
        """Add semantic functions for intent parsing"""
        
        # Function to parse user intent
        intent_prompt = """You are a weather assistant. Parse this user input and extract the user's intent.

User input: {{$input}}

Available actions:
1. get_weather - Get current weather for a location
2. get_forecast - Get weather forecast for a location

Respond in JSON format only:
{
    "action": "get_weather|get_forecast",
    "location": "city_name",
    "days": number (only for forecast, default 5),
    "intent": "brief description of what user wants"
}

Examples:
- "What's the weather like in Hanoi?" → {"action": "get_weather", "location": "Hanoi", "intent": "check current weather"}
- "Get me a 3-day forecast for Ho Chi Minh City" → {"action": "get_forecast", "location": "Ho Chi Minh City", "days": 3, "intent": "get 3-day forecast"}
- "Should I bring an umbrella?" → {"action": "get_weather", "location": "Hanoi", "intent": "check if umbrella needed"}

JSON response:"""

        self.kernel.add_function(
            prompt=intent_prompt,
            function_name="parse_intent",
            plugin_name="intent_parser"
        )
    
    async def parse_with_llm(self, user_input: str) -> dict:
        """Parse user input using Semantic Kernel semantic function"""
        try:
            # Use Semantic Kernel to parse intent
            result = await self.kernel.invoke(
                plugin_name="intent_parser",
                function_name="parse_intent",
                arguments=kernel_arguments.KernelArguments(input=user_input)
            )
            
            # Parse JSON response
            response_text = str(result)
            if "```json" in response_text:
                json_start = response_text.find("```json") + 7
                json_end = response_text.find("```", json_start)
                json_str = response_text[json_start:json_end].strip()
            else:
                json_str = response_text.strip()
            
            parsed = json.loads(json_str)
            return parsed
            
        except Exception as e:
            print(f"⚠️ LLM parsing failed: {str(e)}")
            return None
    
    def show_help(self):
        """Show help information"""
        help_text = """
🤖 **Available Commands:**

🌤️ **Weather Commands:**
   • 'thời tiết hà nội' - Check current weather in Hanoi
   • 'dự báo ho chi minh 3 ngày' - Get 3-day forecast for Ho Chi Minh
   • 'weather bangkok' - Check weather in Bangkok
   • 'forecast singapore 7 days' - Get 7-day forecast for Singapore

🎯 **Natural Language:**
   • 'Should I bring an umbrella to Da Nang?'
   • 'Is it a good day for outdoor activities in Tokyo?'
   • 'What should I pack for my trip to Singapore?'

🛠️ **System Commands:**
   • 'help' - Show this help
   • 'quit' or 'exit' - Exit the program

💡 **Tips:**
   • Use Vietnamese or English
   • Be specific about location
   • Ask for recommendations
"""
        print(help_text)
    
    async def process_command(self, user_input: str) -> str:
        """Process user command using Semantic Kernel"""
        user_input = user_input.strip().lower()
        
        if user_input in ['quit', 'exit', 'q']:
            return "quit"
        
        if user_input in ['help', 'h', '?']:
            self.show_help()
            return ""
        
        if not user_input:
            return "Please enter a command or type 'help' for assistance."
        
        print("🤖 Agent: 🧠 Using Semantic Kernel to understand your request...")
        
        # Parse intent using Semantic Kernel
        parsed = await self.parse_with_llm(user_input)
        
        if parsed:
            print(f"🎯 Understanding: {parsed}")
            
            try:
                if parsed['action'] == 'get_weather':
                    location = parsed.get('location', 'Hanoi')
                    result = await self.kernel.invoke(
                        plugin_name="weather",
                        function_name="get_weather",
                        arguments=kernel_arguments.KernelArguments(location=location)
                    )
                    return str(result)
                
                elif parsed['action'] == 'get_forecast':
                    location = parsed.get('location', 'Hanoi')
                    days = parsed.get('days', 5)
                    result = await self.kernel.invoke(
                        plugin_name="weather",
                        function_name="get_forecast",
                        arguments=kernel_arguments.KernelArguments(location=location, days=days)
                    )
                    return str(result)
                
                else:
                    return f"❌ Unknown action: {parsed['action']}"
                    
            except Exception as e:
                return f"❌ Error executing action: {str(e)}"
        else:
            return "🤔 I'm not sure what you mean. Try:\n• 'What's the weather like in Hanoi?'\n• 'Get me a 3-day forecast for Ho Chi Minh City'\n• Type 'help' for more options"
    
    async def chat_loop(self):
        """Main chat loop"""
        print("🚀 Agent is ready! Start chatting...")
        print()
        
        while True:
            try:
                user_input = input("👤 You: ").strip()
                if not user_input:
                    continue
                
                response = await self.process_command(user_input)
                
                if response == "quit":
                    print("👋 Goodbye! Have a great day!")
                    break
                
                if response:
                    print(f"🤖 Agent: {response}")
                print()
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye! Have a great day!")
                break
            except Exception as e:
                print(f"❌ Error: {str(e)}")
                print()

async def main():
    """Main function"""
    agent = SemanticKernelAgent()
    if hasattr(agent, 'kernel'):
        await agent.chat_loop()
    else:
        print("❌ Failed to initialize agent")

if __name__ == "__main__":
    asyncio.run(main())
