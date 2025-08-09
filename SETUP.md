# Setup Guide - Empower Agent with Actions (Python)

## Prerequisites

1. **Python 3.8 or later**
   ```bash
   # Check your Python version
   python --version
   
   # If you need to install Python, visit: https://python.org/downloads/
   ```

2. **OpenAI API Key**
   - Sign up at [OpenAI](https://platform.openai.com/)
   - Create an API key in your dashboard
   - You'll need credits in your account

## Quick Start

1. **Clone and navigate to the project**
   ```bash
   cd ai-agent-in-action-chapter-5
   ```

2. **Create a virtual environment (recommended)**
   ```bash
   # Create virtual environment
   python -m venv venv
   
   # Activate virtual environment
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set up environment variables**
   ```bash
   # Copy the example environment file
   cp env.example .env
   
   # Edit .env and add your OpenAI API key
   nano .env  # or use your preferred editor
   ```

5. **Run the demo**
   ```bash
   python main.py
   ```

## Running Examples

### Basic Demo
```bash
python main.py
```

### Basic Usage Examples
```bash
python examples/basic_usage.py
```

## Project Structure

```
├── agents/           # Agent implementations
│   └── action_agent.py
├── actions/          # Action definitions
│   └── file_actions.py
├── core/            # Core system components
│   └── action.py
├── examples/        # Usage examples
│   └── basic_usage.py
├── main.py          # Main demo
├── requirements.txt # Python dependencies
├── env.example      # Environment template
└── README.md        # Project documentation
```

## Available Actions

### File System Actions
- `read_file` - Read content from files
- `write_file` - Write content to files  
- `list_directory` - List files in directories
- `delete_file` - Delete files safely

### Future Actions (To be implemented)
- Database operations
- Email sending
- HTTP requests
- System commands
- Webhook calls

## Customization

### Adding New Actions

1. Create a new action class that inherits from `Action`
2. Implement the required methods
3. Register the action with your agent

Example:
```python
from core.action import Action, ActionDefinition, ActionContext, ActionResult, ActionType, PermissionLevel

class MyCustomAction(Action):
    def get_definition(self) -> ActionDefinition:
        return ActionDefinition(
            name="my_custom_action",
            description="My custom action description",
            type=ActionType.WRITE,
            permission_level=PermissionLevel.WRITE,
            # ... other fields
        )
    
    async def execute(self, ctx: ActionContext) -> ActionResult:
        # Implementation here
        pass
    
    def validate(self, ctx: ActionContext) -> bool:
        # Validation logic here
        pass
    
    def get_required_permissions(self) -> List[str]:
        return ["custom.permission"]
```

### Using the Action
```python
agent = ActionAgent("my_agent", "My Agent", "Description")
agent.register_action(MyCustomAction())
result = await agent.execute("Use my custom action")
```

## Troubleshooting

### Common Issues

1. **"OPENAI_API_KEY environment variable is required"**
   - Make sure you've created a `.env` file
   - Verify your API key is correct
   - Check that you have credits in your OpenAI account

2. **"Module not found" errors**
   - Make sure you've installed dependencies: `pip install -r requirements.txt`
   - Check that you're in the correct directory
   - Verify your virtual environment is activated

3. **Permission errors**
   - Ensure the agent has the required permissions
   - Check file system permissions for file operations

4. **Import errors**
   - Make sure you're running from the project root directory
   - Check that all `__init__.py` files exist in subdirectories

### Debug Mode

To see more detailed logging, you can modify the logging level:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Development

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest tests/
```

### Code Formatting
```bash
# Install formatting tools
pip install black isort

# Format code
black .
isort .
```

## Next Steps

1. **Extend with more actions**: Add database, email, or API actions
2. **Improve AI parsing**: Enhance the natural language to action mapping
3. **Add security**: Implement more robust permission and validation systems
4. **Create a web interface**: Build a REST API or web UI for the agent
5. **Add persistence**: Store action history and results

## Contributing

Feel free to:
- Add new actions
- Improve error handling
- Enhance the AI parsing logic
- Add tests
- Improve documentation

## Performance Tips

- Use async/await for I/O operations
- Implement proper error handling
- Use type hints for better code quality
- Consider using connection pooling for database actions
- Implement rate limiting for API actions
