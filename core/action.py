from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
from enum import Enum
from datetime import datetime
from pydantic import BaseModel
import asyncio
import logging


class ActionType(str, Enum):
    """Types of actions that can be performed"""
    READ = "read"
    WRITE = "write"
    EXECUTE = "execute"
    INTEGRATE = "integrate"


class PermissionLevel(str, Enum):
    """Permission levels for actions"""
    READ = "read"
    WRITE = "write"
    ADMIN = "admin"


class ParameterDefinition(BaseModel):
    """Definition of a parameter for an action"""
    name: str
    type: str
    description: str
    required: bool = True
    default: Optional[Any] = None
    validation: Optional[str] = None


class ActionDefinition(BaseModel):
    """Definition of an action"""
    name: str
    description: str
    type: ActionType
    permission_level: PermissionLevel
    parameters: List[ParameterDefinition] = []
    returns: List[ParameterDefinition] = []
    examples: List[str] = []
    metadata: Dict[str, Any] = {}


class ActionResult(BaseModel):
    """Result of an action execution"""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = {}
    timestamp: datetime = datetime.now()
    duration: Optional[float] = None


class ActionContext(BaseModel):
    """Context for action execution"""
    agent_id: str
    user_id: str
    session_id: str
    parameters: Dict[str, Any] = {}
    metadata: Dict[str, Any] = {}
    permissions: List[str] = []


class Action(ABC):
    """Base class for all actions"""
    
    @abstractmethod
    def get_definition(self) -> ActionDefinition:
        """Return the action definition"""
        pass
    
    @abstractmethod
    async def execute(self, ctx: ActionContext) -> ActionResult:
        """Execute the action"""
        pass
    
    @abstractmethod
    def validate(self, ctx: ActionContext) -> bool:
        """Validate if the action can be executed"""
        pass
    
    @abstractmethod
    def get_required_permissions(self) -> List[str]:
        """Return required permissions for this action"""
        pass


class ActionRegistry:
    """Registry for managing all available actions"""
    
    def __init__(self):
        self.actions: Dict[str, Action] = {}
        self.logger = logging.getLogger(__name__)
    
    def register_action(self, action: Action) -> None:
        """Register a new action"""
        definition = action.get_definition()
        if definition.name in self.actions:
            self.logger.warning(f"Action {definition.name} already registered, overwriting")
        
        self.actions[definition.name] = action
        self.logger.info(f"Registered action: {definition.name} ({definition.type})")
    
    def get_action(self, name: str) -> Optional[Action]:
        """Get an action by name"""
        return self.actions.get(name)
    
    def list_actions(self) -> List[ActionDefinition]:
        """List all registered actions"""
        return [action.get_definition() for action in self.actions.values()]
    
    def get_actions_by_type(self, action_type: ActionType) -> List[Action]:
        """Get actions of a specific type"""
        return [
            action for action in self.actions.values()
            if action.get_definition().type == action_type
        ]
    
    def get_actions_by_permission(self, level: PermissionLevel) -> List[Action]:
        """Get actions that require specific permission level"""
        return [
            action for action in self.actions.values()
            if action.get_definition().permission_level == level
        ]
    
    def unregister_action(self, name: str) -> None:
        """Unregister an action"""
        if name in self.actions:
            del self.actions[name]
            self.logger.info(f"Unregistered action: {name}")
        else:
            self.logger.warning(f"Action {name} not found in registry")


class ActionExecutor:
    """Executes actions with safety checks and logging"""
    
    def __init__(self, registry: ActionRegistry):
        self.registry = registry
        self.logger = logging.getLogger(__name__)
    
    async def execute_action(self, action_name: str, ctx: ActionContext) -> ActionResult:
        """Execute an action with full safety checks"""
        start_time = datetime.now()
        
        try:
            # Get the action
            action = self.registry.get_action(action_name)
            if not action:
                return ActionResult(
                    success=False,
                    error=f"Action '{action_name}' not found"
                )
            
            # Validate permissions
            if not self._check_permissions(action, ctx):
                return ActionResult(
                    success=False,
                    error=f"Insufficient permissions for action '{action_name}'"
                )
            
            # Validate action parameters
            if not action.validate(ctx):
                return ActionResult(
                    success=False,
                    error=f"Validation failed for action '{action_name}'"
                )
            
            # Execute the action
            self.logger.info(f"Executing action: {action_name} with parameters: {ctx.parameters}")
            result = await action.execute(ctx)
            
            # Calculate duration
            duration = (datetime.now() - start_time).total_seconds()
            result.duration = duration
            
            # Log the result
            if result.success:
                self.logger.info(f"Action {action_name} completed successfully in {duration:.2f}s")
            else:
                self.logger.error(f"Action {action_name} failed: {result.error}")
            
            return result
            
        except Exception as e:
            duration = (datetime.now() - start_time).total_seconds()
            self.logger.error(f"Exception in action {action_name}: {str(e)}")
            return ActionResult(
                success=False,
                error=f"Exception occurred: {str(e)}",
                duration=duration
            )
    
    def _check_permissions(self, action: Action, ctx: ActionContext) -> bool:
        """Check if the context has required permissions for the action"""
        required_permissions = action.get_required_permissions()
        if not required_permissions:
            return True
        
        user_permissions = set(ctx.permissions)
        required_permissions_set = set(required_permissions)
        
        return required_permissions_set.issubset(user_permissions)


class ActionChain:
    """Manages chains of actions that need to be executed in sequence"""
    
    def __init__(self, executor: ActionExecutor):
        self.executor = executor
        self.logger = logging.getLogger(__name__)
    
    async def execute_chain(self, actions: List[Dict[str, Any]], ctx: ActionContext) -> List[ActionResult]:
        """Execute a chain of actions in sequence"""
        results = []
        
        for i, action_spec in enumerate(actions):
            action_name = action_spec.get("action")
            parameters = action_spec.get("parameters", {})
            
            # Create context for this action
            action_ctx = ActionContext(
                agent_id=ctx.agent_id,
                user_id=ctx.user_id,
                session_id=ctx.session_id,
                parameters=parameters,
                metadata=ctx.metadata,
                permissions=ctx.permissions
            )
            
            self.logger.info(f"Executing action {i+1}/{len(actions)}: {action_name}")
            result = await self.executor.execute_action(action_name, action_ctx)
            results.append(result)
            
            # If an action fails, we can choose to stop or continue
            if not result.success:
                self.logger.warning(f"Action {action_name} failed, stopping chain")
                break
        
        return results

