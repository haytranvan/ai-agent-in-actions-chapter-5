#!/usr/bin/env python3
"""
Interactive Weather & Calendar Agent
Chapter 5: Empower Agent with Actions

Cho phép user chat và tương tác với agent
"""

import asyncio
import os
from dotenv import load_dotenv
from agents.weather_calendar_agent import WeatherCalendarAgent
from core.action import ActionRegistry
from actions.weather_actions import WeatherActions
from actions.calendar_actions import CalendarActions

class InteractiveAgent:
    """Interactive agent cho user tương tác"""
    
    def __init__(self):
        load_dotenv()
        
        # Initialize agent
        weather_api_key = os.getenv("WEATHER_API_KEY")
        if not weather_api_key:
            print("❌ WEATHER_API_KEY not found in .env file")
            return
        
        # Setup action registry
        self.registry = ActionRegistry()
        
        # Register weather actions
        weather_actions = WeatherActions(weather_api_key)
        for action in weather_actions.get_all_actions():
            self.registry.register_action(action)
        
        # Register calendar actions
        calendar_actions = CalendarActions()
        for action in calendar_actions.get_all_actions():
            self.registry.register_action(action)
        
        # Initialize agent
        self.agent = WeatherCalendarAgent(
            agent_id="weather_calendar_agent",
            name="Weather & Calendar Agent",
            description="An agent that can check weather and manage calendar events"
        )
        
        # Register actions with the agent
        for action in self.registry.list_actions():
            # Get the actual action object
            action_obj = self.registry.get_action(action.name)
            if action_obj:
                self.agent.register_action(action_obj)
        
        print("🤖 Interactive Weather & Calendar Agent")
        print("Chapter 5: Empower Agent with Actions")
        print("=" * 50)
        print("✅ Agent initialized successfully!")
        print("🌤️ Available features:")
        print("   • Check weather for any location")
        print("   • Get weather forecasts")
        print("   • Create calendar events")
        print("   • List calendar events")
        print("   • Weather-based activity suggestions")
        print("   • Complex workflows")
        print()
        print("💡 Example commands:")
        print("   • 'Check weather in Hanoi'")
        print("   • 'Get forecast for Ho Chi Minh City for 3 days'")
        print("   • 'Create event called Team Meeting tomorrow at 2pm'")
        print("   • 'Show me all calendar events'")
        print("   • 'What activities should I do today in Hanoi?'")
        print("   • 'Plan outdoor activities for this weekend in Da Nang'")
        print("   • 'help' - Show available commands")
        print("   • 'quit' - Exit the agent")
        print()
    
    async def chat_loop(self):
        """Main chat loop"""
        print("🚀 Agent is ready! Start chatting...")
        print()
        
        while True:
            try:
                # Get user input
                user_input = input("👤 You: ").strip()
                
                if not user_input:
                    continue
                
                # Handle special commands
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("👋 Goodbye! Thanks for using the agent!")
                    break
                
                if user_input.lower() in ['help', '?']:
                    self.show_help()
                    continue
                
                if user_input.lower() in ['clear', 'cls']:
                    os.system('clear' if os.name == 'posix' else 'cls')
                    continue
                
                if user_input.lower() in ['status', 'info']:
                    self.show_status()
                    continue
                
                # Process user input with agent
                print("🤖 Agent: Processing your request...")
                print()
                
                result = await self.agent.process_input(user_input)
                
                # Display result
                if result.success:
                    print(f"✅ Success: {result.data}")
                else:
                    print(f"❌ Error: {result.error}")
                
                print()
                
            except KeyboardInterrupt:
                print("\n👋 Goodbye! Thanks for using the agent!")
                break
            except Exception as e:
                print(f"❌ Unexpected error: {str(e)}")
                print()
    
    def show_help(self):
        """Show help information"""
        print("\n📚 HELP - Available Commands:")
        print("=" * 40)
        print("🌤️ Weather Commands:")
        print("   • 'Check weather in [location]'")
        print("   • 'Get weather for [location]'")
        print("   • 'What's the weather like in [location]?'")
        print("   • 'Get forecast for [location] for [X] days'")
        print("   • 'Weather forecast [location]'")
        print()
        print("📅 Calendar Commands:")
        print("   • 'Create event called [title] [time]'")
        print("   • 'Add event [title] on [date] at [time]'")
        print("   • 'Show me all calendar events'")
        print("   • 'List my events'")
        print("   • 'What events do I have?'")
        print()
        print("🎯 Activity Commands:")
        print("   • 'What activities should I do today in [location]?'")
        print("   • 'Suggest activities for [location]'")
        print("   • 'Plan outdoor activities for [location]'")
        print("   • 'What should I do this weekend in [location]?'")
        print()
        print("🔄 Complex Workflows:")
        print("   • 'Check weather and plan activities for [location]'")
        print("   • 'Get forecast and create outdoor events for [location]'")
        print("   • 'Weather-based planning for [location]'")
        print()
        print("⚙️ System Commands:")
        print("   • 'help' - Show this help")
        print("   • 'status' - Show agent status")
        print("   • 'clear' - Clear screen")
        print("   • 'quit' - Exit agent")
        print()
        print("💡 Tips:")
        print("   • Be specific with locations (e.g., 'Hanoi, Vietnam')")
        print("   • Use natural language (e.g., 'tomorrow at 2pm')")
        print("   • Ask for weather-based recommendations")
        print("   • Try complex workflows for advanced features")
        print()
    
    def show_status(self):
        """Show agent status"""
        print("\n📊 AGENT STATUS:")
        print("=" * 30)
        print(f"🌤️ Weather API: {'✅ Connected' if os.getenv('WEATHER_API_KEY') else '❌ Not configured'}")
        print(f"📅 Calendar: ✅ In-memory storage")
        print(f"🤖 Agent: ✅ Ready")
        print(f"📋 Actions: {len(self.registry.list_actions())} registered")
        print()
        print("Available Actions:")
        for action in self.registry.list_actions():
            print(f"   • {action.name}: {action.description}")
        print()

async def main():
    """Main function"""
    agent = InteractiveAgent()
    await agent.chat_loop()

if __name__ == "__main__":
    asyncio.run(main())
