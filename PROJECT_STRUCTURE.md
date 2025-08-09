# Project Structure - Empower Agent with Actions (Python)

## Overview
This project demonstrates how to empower AI agents with actions, allowing them to perform real-world tasks beyond just responding to queries.

## Directory Structure

```
ai-agent-in-action-chapter-5/
├── __init__.py                 # Root package initialization
├── main.py                     # Main demo script
├── requirements.txt            # Python dependencies
├── README.md                   # Project documentation
├── SETUP.md                    # Setup guide
├── env.example                 # Environment variables template
├── PROJECT_STRUCTURE.md        # This file
│
├── core/                       # Core framework components
│   ├── __init__.py            # Core package initialization
│   └── action.py              # Action framework (base classes, registry, executor)
│
├── agents/                     # Agent implementations
│   ├── __init__.py            # Agents package initialization
│   └── action_agent.py        # Main action agent implementation
│
├── actions/                    # Action implementations
│   ├── __init__.py            # Actions package initialization
│   └── file_actions.py        # File system actions (read, write, list, delete)
│
└── examples/                   # Usage examples
    ├── __init__.py            # Examples package initialization
    └── basic_usage.py         # Basic and advanced usage examples
```

## Key Components

### Core Framework (`core/`)
- **Action Framework**: Base classes for defining and executing actions
- **Action Registry**: Manages all available actions
- **Action Executor**: Handles action execution with safety checks
- **Permission System**: Controls access to different action types

### Agents (`agents/`)
- **ActionAgent**: Main agent that can execute actions based on natural language
- **Natural Language Processing**: Converts user input to specific actions
- **Permission Management**: Handles agent permissions

### Actions (`actions/`)
- **File System Actions**: Read, write, list, and delete files
- **Extensible Framework**: Easy to add new action types
- **Safety Features**: Validation and error handling

### Examples (`examples/`)
- **Basic Examples**: Simple file operations
- **Advanced Examples**: Complex workflows and error handling
- **Direct Action Execution**: Bypassing natural language parsing

## File Descriptions

### Main Files
- `main.py`: Demo script showing the agent in action
- `requirements.txt`: Python package dependencies
- `README.md`: Comprehensive project documentation
- `SETUP.md`: Step-by-step setup instructions
- `env.example`: Environment variables template

### Core Files
- `core/action.py`: Complete action framework implementation
- `agents/action_agent.py`: Main agent with natural language processing
- `actions/file_actions.py`: File system action implementations
- `examples/basic_usage.py`: Usage examples and demonstrations

## Dependencies

### Required Packages
- `openai`: OpenAI API client
- `pydantic`: Data validation and serialization
- `python-dotenv`: Environment variable management
- `aiofiles`: Async file operations
- `fastapi`: Web framework (for future web interface)
- `uvicorn`: ASGI server
- `pytest`: Testing framework

### Optional Packages
- `black`: Code formatting
- `isort`: Import sorting
- `pytest-asyncio`: Async testing support

## Usage

### Quick Start
```bash
# Install dependencies
pip install -r requirements.txt

# Set up environment
cp env.example .env
# Edit .env with your OpenAI API key

# Run demo
python main.py

# Run examples
python examples/basic_usage.py
```

### Development
```bash
# Install development dependencies
pip install pytest black isort

# Run tests
pytest

# Format code
black .
isort .
```

## Architecture

### Action Flow
1. **User Input**: Natural language request
2. **Parsing**: Convert to action steps using AI
3. **Validation**: Check permissions and parameters
4. **Execution**: Perform the actual action
5. **Result**: Return formatted response

### Safety Features
- **Permission System**: Role-based access control
- **Input Validation**: Parameter sanitization
- **Error Handling**: Graceful failure management
- **Logging**: Comprehensive audit trail

## Extensibility

### Adding New Actions
1. Create new action class inheriting from `Action`
2. Implement required methods
3. Register with agent
4. Add permissions if needed

### Adding New Agents
1. Create agent class with action registry
2. Implement natural language processing
3. Configure permissions
4. Register actions

## Future Enhancements
- Database actions
- Email actions
- HTTP request actions
- System command actions
- Web interface
- Action chaining
- Workflow orchestration

