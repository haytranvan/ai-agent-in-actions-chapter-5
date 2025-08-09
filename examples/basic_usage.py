import asyncio
import os
import logging
from dotenv import load_dotenv

from openai import AsyncOpenAI
from agents.action_agent import ActionAgent
from actions.file_actions import FileActions


async def basic_examples():
    """Basic usage examples for the action agent"""
    
    # Load environment variables
    load_dotenv()
    
    # Get OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY environment variable is required")
        return
    
    # Create OpenAI client
    client = AsyncOpenAI(api_key=api_key)
    
    # Create an action agent
    agent = ActionAgent("example_agent", "Example Agent", "An example agent with file system actions")
    agent.set_openai_client(client)
    
    # Add permissions
    agent.add_permission("file.read")
    agent.add_permission("file.write")
    
    # Register file actions
    file_actions = FileActions()
    for action in file_actions.get_all_actions():
        agent.register_action(action)
    
    print("🚀 Basic Usage Examples")
    print("=" * 40)
    
    # Example 1: Simple file write
    print("\n1️⃣ Simple file write:")
    result = await agent.execute("Create a file called hello.txt with the content 'Hello, World!'")
    print(f"Result: {result}")
    
    # Example 2: Read the file back
    print("\n2️⃣ Read the file back:")
    result = await agent.execute("Read the file hello.txt")
    print(f"Result: {result}")
    
    # Example 3: List current directory
    print("\n3️⃣ List current directory:")
    result = await agent.execute("Show me what files are in the current directory")
    print(f"Result: {result}")
    
    # Example 4: Create a structured file
    print("\n4️⃣ Create a structured file:")
    result = await agent.execute("""
        Create a file called data.json with this content:
        {
            "name": "Action Agent",
            "version": "1.0.0",
            "features": ["file_read", "file_write", "directory_list"],
            "status": "active"
        }
    """)
    print(f"Result: {result}")
    
    # Example 5: Read and verify
    print("\n5️⃣ Read and verify the JSON file:")
    result = await agent.execute("Read the data.json file and show me its contents")
    print(f"Result: {result}")
    
    print("\n✅ Basic examples completed!")


async def advanced_examples():
    """Advanced usage examples"""
    
    # Load environment variables
    load_dotenv()
    
    # Get OpenAI API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        print("❌ OPENAI_API_KEY environment variable is required")
        return
    
    # Create OpenAI client
    client = AsyncOpenAI(api_key=api_key)
    
    # Create an action agent
    agent = ActionAgent("advanced_agent", "Advanced Agent", "An advanced agent with file system actions")
    agent.set_openai_client(client)
    
    # Add permissions
    agent.add_permission("file.read")
    agent.add_permission("file.write")
    
    # Register file actions
    file_actions = FileActions()
    for action in file_actions.get_all_actions():
        agent.register_action(action)
    
    print("\n🚀 Advanced Usage Examples")
    print("=" * 40)
    
    # Example 1: Direct action execution
    print("\n1️⃣ Direct action execution:")
    result = await agent.execute_direct_action("write_file", {
        "filename": "direct_test.txt",
        "content": "This was created using direct action execution"
    })
    print(f"Result: {result}")
    
    # Example 2: Complex workflow
    print("\n2️⃣ Complex workflow:")
    result = await agent.execute("""
        Create a log file called app.log with the content:
        [INFO] Application started
        [INFO] Loading configuration
        [INFO] Database connected
        [INFO] Server listening on port 8080
    """)
    print(f"Result: {result}")
    
    # Example 3: Error handling
    print("\n3️⃣ Error handling (trying to read non-existent file):")
    result = await agent.execute("Read the file non_existent_file.txt")
    print(f"Result: {result}")
    
    # Example 4: List with recursive option
    print("\n4️⃣ List directory recursively:")
    result = await agent.execute("List all files in the current directory recursively")
    print(f"Result: {result}")
    
    print("\n✅ Advanced examples completed!")


async def main():
    """Run all examples"""
    print("🤖 Action Agent Examples - Chapter 5: Empower Agent with Actions")
    print("=" * 70)
    
    # Run basic examples
    await basic_examples()
    
    # Run advanced examples
    await advanced_examples()
    
    print("\n🎉 All examples completed successfully!")
    print("\n💡 Key takeaways:")
    print("   - Agents can now perform real file system operations")
    print("   - Natural language is converted to specific actions")
    print("   - Actions are validated and executed safely")
    print("   - Error handling is built into the system")


if __name__ == "__main__":
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Run the examples
    asyncio.run(main())

