#!/usr/bin/env python3
"""
Real Interactive Weather Agent
Chapter 5: Empower Agent with Actions

Bạn có thể thực sự chat với agent này!
"""

import asyncio
import aiohttp
import os
from datetime import datetime
from dotenv import load_dotenv

class RealInteractiveAgent:
    """Real interactive weather agent - bạn có thể chat thật!"""
    
    def __init__(self):
        load_dotenv()
        self.api_key = os.getenv("WEATHER_API_KEY")
        self.base_url = "http://api.openweathermap.org/data/2.5"
        self.session = None
        
        if not self.api_key:
            print("❌ WEATHER_API_KEY not found in .env file")
            return
        
        print("🤖 Real Interactive Weather Agent")
        print("Chapter 5: Empower Agent with Actions")
        print("=" * 50)
        print("✅ Agent ready for real interaction!")
        print()
        print("🌤️ Try these commands:")
        print("   • 'weather Hanoi'")
        print("   • 'forecast Ho Chi Minh City 3'")
        print("   • 'What's the weather like in Da Nang?'")
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
                    humidity = data["main"]["humidity"]
                    wind = data["wind"]["speed"]
                    feels_like = data["main"]["feels_like"]
                    
                    return f"🌤️ {location}: {temp}°C (feels like {feels_like}°C)\n☁️ {description}\n💧 Humidity: {humidity}%\n💨 Wind: {wind} m/s"
                else:
                    return f"❌ Sorry, I couldn't find weather data for '{location}'. Try a different city name."
        except Exception as e:
            return f"❌ Sorry, there was an error getting weather for '{location}': {str(e)}"
    
    async def get_forecast(self, location: str, days: int = 5) -> str:
        """Get weather forecast"""
        url = f"{self.base_url}/forecast"
        params = {
            "q": location,
            "appid": self.api_key,
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
                    
                    return result
                else:
                    return f"❌ Sorry, I couldn't find forecast data for '{location}'. Try a different city name."
        except Exception as e:
            return f"❌ Sorry, there was an error getting forecast for '{location}': {str(e)}"
    
    def show_help(self):
        """Show help"""
        print("\n📚 HELP - Available Commands:")
        print("=" * 40)
        print("🌤️ Weather Commands:")
        print("   • weather [city] - Get current weather")
        print("   • forecast [city] [days] - Get weather forecast")
        print()
        print("🧠 Natural Language:")
        print("   • 'What's the weather like in [city]?'")
        print("   • 'How's the weather in [city] today?'")
        print("   • 'Get me a [X]-day forecast for [city]'")
        print("   • 'Tell me about the weather in [city]'")
        print()
        print("🌍 Example Cities:")
        print("   • Hanoi, Vietnam")
        print("   • Ho Chi Minh City, Vietnam")
        print("   • Da Nang, Vietnam")
        print("   • Bangkok, Thailand")
        print("   • Singapore")
        print("   • Tokyo, Japan")
        print()
        print("⚙️ System Commands:")
        print("   • help - Show this help")
        print("   • quit/exit - Exit the agent")
        print()
        print("💡 Tips:")
        print("   • Be specific with city names")
        print("   • Try different cities around the world")
        print("   • Ask for forecasts up to 5 days")
        print("   • Use natural language - I understand!")
        print()
    
    async def process_command(self, user_input: str) -> str:
        """Process user command and return response"""
        user_input = user_input.strip().lower()
        
        # Handle system commands
        if user_input in ['quit', 'exit', 'bye']:
            return "👋 Goodbye! Thanks for chatting with me!"
        
        if user_input in ['help', '?']:
            self.show_help()
            return "📚 Help displayed above!"
        
        # Handle weather commands
        if user_input.startswith('weather '):
            location = user_input.replace('weather ', '').strip()
            if location:
                return await self.get_weather(location)
            else:
                return "❌ Please specify a city: weather [city]"
        
        # Handle forecast commands
        if user_input.startswith('forecast '):
            parts = user_input.replace('forecast ', '').split()
            if len(parts) >= 1:
                location = parts[0]
                days = int(parts[1]) if len(parts) > 1 else 5
                return await self.get_forecast(location, days)
            else:
                return "❌ Please specify a city: forecast [city] [days]"
        
        # Handle natural language
        if any(word in user_input for word in ['weather', 'temperature', 'climate']):
            # Extract city name from natural language
            cities = ['hanoi', 'ho chi minh', 'da nang', 'bangkok', 'singapore', 'tokyo']
            found_city = None
            
            for city in cities:
                if city in user_input:
                    found_city = city
                    break
            
            if found_city:
                return await self.get_weather(found_city)
            else:
                return "❌ I understand you want weather info, but please specify a city. Try: 'weather Hanoi' or 'What's the weather like in Ho Chi Minh City?'"
        
        if 'forecast' in user_input:
            # Extract city and days from natural language
            cities = ['hanoi', 'ho chi minh', 'da nang', 'bangkok', 'singapore', 'tokyo']
            found_city = None
            
            for city in cities:
                if city in user_input:
                    found_city = city
                    break
            
            if found_city:
                # Extract days if mentioned
                days = 5  # default
                if '3 day' in user_input or '3-day' in user_input:
                    days = 3
                elif '5 day' in user_input or '5-day' in user_input:
                    days = 5
                
                return await self.get_forecast(found_city, days)
            else:
                return "❌ I understand you want a forecast, but please specify a city. Try: 'forecast Hanoi 3' or 'Get me a 3-day forecast for Ho Chi Minh City'"
        
        # Default response
        return "🤔 I'm not sure what you mean. Try:\n• 'weather Hanoi'\n• 'forecast Ho Chi Minh City 3'\n• 'What's the weather like in Da Nang?'\n• Type 'help' for more options"
    
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
    agent = RealInteractiveAgent()
    await agent.chat_loop()

if __name__ == "__main__":
    asyncio.run(main())
