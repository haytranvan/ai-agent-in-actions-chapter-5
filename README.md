# 🌤️ Weather & Calendar Agent with Semantic Kernel

**Chapter 5: Empower Agent with Actions** - Using Microsoft's Semantic Kernel Framework

An intelligent agent that can check weather conditions and create corresponding calendar events, demonstrating the power of **Semantic Kernel** in empowering agents with actions.

## 🎯 **Project Overview**

This project demonstrates **Chapter 5: Empower Agent with Actions** from the "AI Agent in Action" book, using **Microsoft's Semantic Kernel** framework. The agent combines:

- **Weather API Integration** (OpenWeatherMap)
- **Calendar Management** (In-memory storage)
- **Semantic Kernel Skills** (Native + Semantic Functions)
- **Action Planning** (Automatic skill orchestration)

## 🔧 **Native Functions vs Semantic Functions**

### **Native Functions** 🔧
```python
@sk_function(description="Get current weather")
async def get_weather(self, context: SKContext) -> str:
    # Hard-coded logic
    # Direct API calls
    # Deterministic behavior
    return weather_data
```

**Characteristics:**
- ✅ **Fast execution** (no LLM calls)
- ✅ **Deterministic results**
- ✅ **Low cost** (no token usage)
- ✅ **Reliable and predictable**
- ❌ **Limited flexibility**
- ❌ **Hard to modify logic**

### **Semantic Functions** 🧠
```python
# weather_analysis.skprompt
You are a weather expert. Analyze the weather data and provide recommendations:
Weather Data: {{$weather_data}}
Location: {{$location}}
```

**Characteristics:**
- ✅ **Natural language understanding**
- ✅ **Highly flexible and creative**
- ✅ **Easy to modify via prompts**
- ✅ **Context-aware responses**
- ❌ **Slower execution** (LLM calls)
- ❌ **Higher cost** (token usage)

## 🏗️ **Architecture**

```
Semantic Kernel
├── Kernel (Central Orchestrator)
├── Skills
│   ├── WeatherSkill (Native Functions)
│   │   ├── get_weather()
│   │   ├── get_forecast()
│   │   └── analyze_weather()
│   ├── CalendarSkill (Native Functions)
│   │   ├── create_event()
│   │   ├── list_events()
│   │   └── suggest_activities()
│   └── WeatherSemanticFunctions (Semantic Functions)
│       ├── semantic_weather_analysis()
│       ├── semantic_weather_planning()
│       └── semantic_activity_suggestion()
├── Action Planner (Automatic Skill Orchestration)
└── Context Management
```

## 🚀 **Features**

### **Weather Operations**
- 🌡️ **Current Weather**: Get real-time weather conditions
- 📅 **Weather Forecast**: Multi-day weather predictions
- 🧠 **Weather Analysis**: Intelligent activity recommendations
- 🎯 **Semantic Analysis**: LLM-powered weather interpretation

### **Calendar Management**
- 📅 **Event Creation**: Create weather-based calendar events
- 📋 **Event Listing**: List and filter calendar events
- 🎨 **Activity Suggestions**: Weather-aware activity recommendations
- 🔗 **Weather Integration**: Link events to weather conditions

### **Semantic Kernel Features**
- 🔧 **Native Skills**: Fast, reliable, structured operations
- 🧠 **Semantic Functions**: LLM-powered, flexible reasoning
- 🎯 **Action Planner**: Automatic skill orchestration
- 🔗 **Skill Chaining**: Manual multi-step workflows
- 📝 **Prompt Management**: Structured prompt templates

## 🛠️ **Setup**

### **1. Install Dependencies**
```bash
pip install -r requirements.txt
```

### **2. Environment Variables**
Create `.env` file:
```env
OPENAI_API_KEY=your_openai_api_key
WEATHER_API_KEY=your_openweathermap_api_key
```

### **3. Run the Demo**
```bash
python main_semantic_kernel.py
```

## 📚 **Usage Examples**

### **Native Functions Demo**
```python
# Fast, deterministic weather operations
context = kernel.create_new_context()
context.variables["location"] = "Hanoi"
weather_result = await kernel.run_async(
    kernel.get_function("weather", "get_weather"),
    context
)
```

### **Semantic Functions Demo**
```python
# LLM-powered weather analysis
context.variables["weather_data"] = weather_json
context.variables["activity_type"] = "outdoor"
semantic_result = await kernel.run_async(
    kernel.get_function("semantic_weather", "semantic_weather_analysis"),
    context
)
```

### **Action Planner Demo**
```python
# Automatic skill orchestration
planner = ActionPlanner(kernel)
goal = "Check weather in Hanoi and create calendar event"
plan = await planner.create_plan_async(goal)
result = await plan.invoke_async()
```

### **Skill Chaining Demo**
```python
# Manual multi-step workflow
# 1. Get weather
# 2. Analyze for activities
# 3. Create calendar event
```

## 🎯 **Key Concepts from Chapter 5**

### **1. Semantic Kernel Framework**
- **Kernel**: Central orchestrator for skills and services
- **Skills**: Collections of functions (native + semantic)
- **Planners**: Automatic skill orchestration
- **Context**: Shared state and variables

### **2. Native vs Semantic Functions**
- **Native**: Hard-coded logic, fast, reliable
- **Semantic**: LLM-powered, flexible, creative

### **3. Action Empowerment**
- **Skill Integration**: Connect agents to external systems
- **Planning**: Automatic goal decomposition
- **Orchestration**: Coordinated skill execution
- **Context Management**: Shared state across skills

### **4. Real-world Applications**
- **API Integration**: Weather, calendar, file systems
- **Data Processing**: Structured operations
- **Natural Language**: User interaction and reasoning
- **Workflow Automation**: Multi-step processes

## 📁 **Project Structure**

```
ai-agent-in-action-chapter-5/
├── skills/
│   ├── weather_skill.py          # Native weather functions
│   ├── calendar_skill.py         # Native calendar functions
│   └── weather_semantic_functions.py  # Semantic functions
├── prompts/                      # Prompt templates
│   ├── weather_analysis.skprompt
│   ├── weather_planning.skprompt
│   └── activity_suggestion.skprompt
├── main_semantic_kernel.py       # Main demo script
├── requirements.txt              # Dependencies
├── .env.example                  # Environment template
└── README.md                     # This file
```

## 🔍 **Comparison: Native vs Semantic Functions**

| Aspect | Native Functions | Semantic Functions |
|--------|------------------|-------------------|
| **Speed** | ⚡ Fast | 🐌 Slower (LLM calls) |
| **Cost** | 💰 Low | 💸 Higher (tokens) |
| **Reliability** | ✅ Predictable | ❓ Variable |
| **Flexibility** | 🔒 Limited | 🎨 High |
| **Maintenance** | 🔧 Code changes | 📝 Prompt changes |
| **Use Cases** | Data processing, APIs | Reasoning, creativity |

## 🎓 **Learning Objectives**

1. **Understand Semantic Kernel**: Microsoft's AI agent framework
2. **Native Functions**: Fast, reliable, structured operations
3. **Semantic Functions**: LLM-powered, flexible reasoning
4. **Action Planning**: Automatic skill orchestration
5. **Skill Integration**: Connecting agents to external systems
6. **Real-world Applications**: Weather + Calendar integration

## 🚀 **Next Steps**

1. **Add Real APIs**: Connect to actual weather and calendar services
2. **Expand Skills**: Add more native and semantic functions
3. **Advanced Planning**: Implement complex workflow planning
4. **User Interface**: Build web or chat interface
5. **Production Deployment**: Scale for real-world usage

---

**Built with ❤️ using Semantic Kernel for Chapter 5: Empower Agent with Actions**
