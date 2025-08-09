import asyncio
import logging
from typing import Dict, Any, List, Optional
from datetime import datetime
import json
import re

from openai import AsyncOpenAI
from core.action import (
    ActionRegistry, ActionExecutor, ActionContext, 
    ActionResult, ActionDefinition
)


class ActionStep:
    """Represents a single action to be executed"""
    
    def __init__(self, action_name: str, parameters: Dict[str, Any], reason: str = ""):
        self.action_name = action_name
        self.parameters = parameters
        self.reason = reason
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            "action": self.action_name,
            "parameters": self.parameters,
            "reason": self.reason
        }


class ActionAgent:
    """An agent that can execute actions based on natural language input"""
    
    def __init__(self, agent_id: str, name: str, description: str):
        self.agent_id = agent_id
        self.name = name
        self.description = description
        self.registry = ActionRegistry()
        self.executor = ActionExecutor(self.registry)
        self.client: Optional[AsyncOpenAI] = None
        self.permissions: List[str] = []
        self.logger = logging.getLogger(f"agent.{agent_id}")
        
        # Configure logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
    
    def set_openai_client(self, client: AsyncOpenAI) -> None:
        """Set the OpenAI client for the agent"""
        self.client = client
    
    def add_permission(self, permission: str) -> None:
        """Add a permission to the agent"""
        if permission not in self.permissions:
            self.permissions.append(permission)
    
    def has_permission(self, permission: str) -> bool:
        """Check if the agent has a specific permission"""
        return permission in self.permissions
    
    def register_action(self, action) -> None:
        """Register an action with the agent"""
        self.registry.register_action(action)
    
    async def execute(self, input_text: str) -> str:
        """Process natural language input and execute appropriate actions"""
        self.logger.info(f"Processing input: {input_text}")
        
        try:
            # Parse the input to determine what actions to take
            action_steps = await self._parse_input(input_text)
            
            if not action_steps:
                return "I couldn't determine what actions to take from your request. Please try rephrasing."
            
            # Execute the action steps
            results = []
            for step in action_steps:
                result = await self._execute_action_step(step)
                results.append(result)
            
            # Format the results
            return self._format_results(results)
            
        except Exception as e:
            self.logger.error(f"Error executing request: {str(e)}")
            return f"An error occurred: {str(e)}"
    
    async def _parse_input(self, input_text: str) -> List[ActionStep]:
        """Parse natural language input to determine actions to execute"""
        if not self.client:
            # Fallback to simple keyword-based parsing
            return self._simple_parse_input(input_text)
        
        try:
            # Get available actions
            available_actions = self.registry.list_actions()
            
            # Create prompt for action selection
            prompt = self._build_action_selection_prompt(input_text, available_actions)
            
            # Use OpenAI to determine actions
            response = await self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {
                        "role": "system",
                        "content": "You are an AI assistant that helps determine which actions to execute based on user input. Respond with JSON only."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.1
            )
            
            # Parse the response
            content = response.choices[0].message.content
            return self._parse_ai_response(content)
            
        except Exception as e:
            self.logger.warning(f"AI parsing failed, falling back to simple parsing: {str(e)}")
            return self._simple_parse_input(input_text)
    
    def _simple_parse_input(self, input_text: str) -> List[ActionStep]:
        """Simple keyword-based action parsing as fallback"""
        input_lower = input_text.lower()
        steps = []
        
        # File operations
        if any(word in input_lower for word in ["read", "show", "display"]) and any(word in input_lower for word in ["file", "content"]):
            # Extract filename using regex
            filename_match = re.search(r'(\w+\.\w+)', input_text)
            if filename_match:
                filename = filename_match.group(1)
                steps.append(ActionStep(
                    action_name="read_file",
                    parameters={"filename": filename},
                    reason="User requested to read a file"
                ))
        
        if any(word in input_lower for word in ["write", "create", "save"]) and any(word in input_lower for word in ["file", "content"]):
            # Extract filename and content
            filename_match = re.search(r'(\w+\.\w+)', input_text)
            if filename_match:
                filename = filename_match.group(1)
                # Extract content after "with the content:" or similar
                content_match = re.search(r'content[:\s]+(.+)', input_text, re.IGNORECASE | re.DOTALL)
                content = content_match.group(1).strip() if content_match else "Default content"
                
                steps.append(ActionStep(
                    action_name="write_file",
                    parameters={"filename": filename, "content": content},
                    reason="User requested to write to a file"
                ))
        
        if any(word in input_lower for word in ["list", "show", "directory", "files"]):
            steps.append(ActionStep(
                action_name="list_directory",
                parameters={"path": "."},
                reason="User requested to list directory contents"
            ))
        
        return steps
    
    def _build_action_selection_prompt(self, input_text: str, actions: List[ActionDefinition]) -> str:
        """Build a prompt for action selection"""
        action_descriptions = []
        for action in actions:
            params_str = ", ".join([f"{p.name}: {p.type}" for p in action.parameters])
            desc = f"- {action.name}: {action.description} (Parameters: {params_str})"
            action_descriptions.append(desc)
        
        return f"""
User input: "{input_text}"

Available actions:
{chr(10).join(action_descriptions)}

Based on the user input, determine which actions to execute. Respond with a JSON array of action steps:

[
  {{
    "action_name": "action_name",
    "parameters": {{"param1": "value1"}},
    "reason": "Why this action is needed"
  }}
]

Only include actions that are relevant to the user's request. If no actions are needed, return an empty array.
"""
    
    def _parse_ai_response(self, response: str) -> List[ActionStep]:
        """Parse the AI response to extract action steps"""
        try:
            # Try to parse as JSON
            data = json.loads(response)
            if isinstance(data, list):
                steps = []
                for item in data:
                    if isinstance(item, dict):
                        step = ActionStep(
                            action_name=item.get("action_name", ""),
                            parameters=item.get("parameters", {}),
                            reason=item.get("reason", "")
                        )
                        steps.append(step)
                return steps
        except json.JSONDecodeError:
            self.logger.warning("Failed to parse AI response as JSON")
        
        # Fallback to simple parsing
        return self._simple_parse_input(response)
    
    async def _execute_action_step(self, step: ActionStep) -> str:
        """Execute a single action step"""
        self.logger.info(f"Executing action: {step.action_name} with parameters: {step.parameters}")
        
        # Create action context
        ctx = ActionContext(
            agent_id=self.agent_id,
            user_id="user_001",  # In practice, this would come from authentication
            session_id="session_001",
            parameters=step.parameters,
            metadata={},
            permissions=self.permissions
        )
        
        # Execute the action
        result = await self.executor.execute_action(step.action_name, ctx)
        
        # Format the result
        if result.success:
            return f"✅ {step.action_name}: {result.data}"
        else:
            return f"❌ {step.action_name} failed: {result.error}"
    
    def _format_results(self, results: List[str]) -> str:
        """Format the results of action execution"""
        if not results:
            return "No actions were executed."
        
        return "\n".join(results)
    
    def list_available_actions(self) -> List[ActionDefinition]:
        """List all available actions for this agent"""
        return self.registry.list_actions()
    
    async def execute_direct_action(self, action_name: str, parameters: Dict[str, Any]) -> ActionResult:
        """Execute an action directly without natural language parsing"""
        ctx = ActionContext(
            agent_id=self.agent_id,
            user_id="user_001",
            session_id="session_001",
            parameters=parameters,
            metadata={},
            permissions=self.permissions
        )
        
        return await self.executor.execute_action(action_name, ctx)

