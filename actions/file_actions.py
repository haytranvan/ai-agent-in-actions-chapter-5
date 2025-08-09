import os
import asyncio
import aiofiles
from pathlib import Path
from typing import Dict, Any, List
import logging

from core.action import (
    Action, ActionDefinition, ActionContext, ActionResult,
    ActionType, PermissionLevel, ParameterDefinition
)


class ReadFileAction(Action):
    """Action to read content from a file"""
    
    def get_definition(self) -> ActionDefinition:
        return ActionDefinition(
            name="read_file",
            description="Read content from a file",
            type=ActionType.READ,
            permission_level=PermissionLevel.READ,
            parameters=[
                ParameterDefinition(
                    name="filename",
                    type="string",
                    description="Path to the file to read",
                    required=True,
                    validation="file_exists"
                )
            ],
            returns=[
                ParameterDefinition(
                    name="content",
                    type="string",
                    description="Content of the file"
                ),
                ParameterDefinition(
                    name="size",
                    type="int",
                    description="Size of the file in bytes"
                )
            ],
            examples=[
                "read_file filename=config.json",
                "read_file filename=/path/to/document.txt"
            ]
        )
    
    async def execute(self, ctx: ActionContext) -> ActionResult:
        filename = ctx.parameters.get("filename")
        if not filename:
            return ActionResult(
                success=False,
                error="filename parameter is required"
            )
        
        try:
            # Check if file exists
            if not os.path.exists(filename):
                return ActionResult(
                    success=False,
                    error=f"File '{filename}' does not exist"
                )
            
            # Read file content
            async with aiofiles.open(filename, 'r', encoding='utf-8') as f:
                content = await f.read()
            
            # Get file info
            file_info = os.stat(filename)
            
            return ActionResult(
                success=True,
                data={
                    "content": content,
                    "size": file_info.st_size,
                    "path": filename,
                    "modified": file_info.st_mtime
                },
                metadata={
                    "file_size": file_info.st_size,
                    "file_type": Path(filename).suffix
                }
            )
            
        except Exception as e:
            return ActionResult(
                success=False,
                error=f"Failed to read file: {str(e)}"
            )
    
    def validate(self, ctx: ActionContext) -> bool:
        filename = ctx.parameters.get("filename")
        if not filename:
            return False
        
        # Basic path validation
        if ".." in filename:
            return False
        
        return True
    
    def get_required_permissions(self) -> List[str]:
        return ["file.read"]


class WriteFileAction(Action):
    """Action to write content to a file"""
    
    def get_definition(self) -> ActionDefinition:
        return ActionDefinition(
            name="write_file",
            description="Write content to a file",
            type=ActionType.WRITE,
            permission_level=PermissionLevel.WRITE,
            parameters=[
                ParameterDefinition(
                    name="filename",
                    type="string",
                    description="Path to the file to write",
                    required=True,
                    validation="valid_path"
                ),
                ParameterDefinition(
                    name="content",
                    type="string",
                    description="Content to write to the file",
                    required=True
                ),
                ParameterDefinition(
                    name="overwrite",
                    type="bool",
                    description="Whether to overwrite existing file",
                    required=False,
                    default=False
                )
            ],
            returns=[
                ParameterDefinition(
                    name="success",
                    type="bool",
                    description="Whether the write operation was successful"
                ),
                ParameterDefinition(
                    name="bytes_written",
                    type="int",
                    description="Number of bytes written"
                )
            ],
            examples=[
                "write_file filename=output.txt content=Hello World",
                "write_file filename=log.txt content=Log entry overwrite=true"
            ]
        )
    
    async def execute(self, ctx: ActionContext) -> ActionResult:
        filename = ctx.parameters.get("filename")
        content = ctx.parameters.get("content")
        overwrite = ctx.parameters.get("overwrite", False)
        
        if not filename or not content:
            return ActionResult(
                success=False,
                error="filename and content parameters are required"
            )
        
        try:
            # Check if file exists and overwrite is not allowed
            if not overwrite and os.path.exists(filename):
                return ActionResult(
                    success=False,
                    error=f"File '{filename}' already exists and overwrite is not allowed"
                )
            
            # Create directory if it doesn't exist
            os.makedirs(os.path.dirname(filename), exist_ok=True)
            
            # Write file
            async with aiofiles.open(filename, 'w', encoding='utf-8') as f:
                await f.write(content)
            
            return ActionResult(
                success=True,
                data={
                    "success": True,
                    "bytes_written": len(content),
                    "filename": filename
                },
                metadata={
                    "file_size": len(content)
                }
            )
            
        except Exception as e:
            return ActionResult(
                success=False,
                error=f"Failed to write file: {str(e)}"
            )
    
    def validate(self, ctx: ActionContext) -> bool:
        filename = ctx.parameters.get("filename")
        content = ctx.parameters.get("content")
        
        if not filename or not content:
            return False
        
        # Basic path validation
        if ".." in filename:
            return False
        
        # Check if content is not empty
        if not content.strip():
            return False
        
        return True
    
    def get_required_permissions(self) -> List[str]:
        return ["file.write"]


class ListDirectoryAction(Action):
    """Action to list files and directories"""
    
    def get_definition(self) -> ActionDefinition:
        return ActionDefinition(
            name="list_directory",
            description="List files and directories in a path",
            type=ActionType.READ,
            permission_level=PermissionLevel.READ,
            parameters=[
                ParameterDefinition(
                    name="path",
                    type="string",
                    description="Directory path to list",
                    required=False,
                    default="."
                ),
                ParameterDefinition(
                    name="recursive",
                    type="bool",
                    description="Whether to list recursively",
                    required=False,
                    default=False
                )
            ],
            returns=[
                ParameterDefinition(
                    name="files",
                    type="list",
                    description="List of file names"
                ),
                ParameterDefinition(
                    name="directories",
                    type="list",
                    description="List of directory names"
                )
            ],
            examples=[
                "list_directory path=.",
                "list_directory path=/tmp recursive=true"
            ]
        )
    
    async def execute(self, ctx: ActionContext) -> ActionResult:
        path = ctx.parameters.get("path", ".")
        recursive = ctx.parameters.get("recursive", False)
        
        try:
            # Check if path exists and is a directory
            if not os.path.exists(path):
                return ActionResult(
                    success=False,
                    error=f"Path '{path}' does not exist"
                )
            
            if not os.path.isdir(path):
                return ActionResult(
                    success=False,
                    error=f"Path '{path}' is not a directory"
                )
            
            files = []
            directories = []
            
            if recursive:
                # Recursive listing
                for root, dirs, filenames in os.walk(path):
                    # Get relative paths
                    rel_root = os.path.relpath(root, path)
                    if rel_root == ".":
                        rel_root = ""
                    
                    for dirname in dirs:
                        dir_path = os.path.join(rel_root, dirname) if rel_root else dirname
                        directories.append(dir_path)
                    
                    for filename in filenames:
                        file_path = os.path.join(rel_root, filename) if rel_root else filename
                        files.append(file_path)
            else:
                # Non-recursive listing
                for item in os.listdir(path):
                    item_path = os.path.join(path, item)
                    if os.path.isdir(item_path):
                        directories.append(item)
                    else:
                        files.append(item)
            
            return ActionResult(
                success=True,
                data={
                    "files": files,
                    "directories": directories,
                    "path": path,
                    "recursive": recursive
                },
                metadata={
                    "file_count": len(files),
                    "directory_count": len(directories)
                }
            )
            
        except Exception as e:
            return ActionResult(
                success=False,
                error=f"Failed to list directory: {str(e)}"
            )
    
    def validate(self, ctx: ActionContext) -> bool:
        path = ctx.parameters.get("path", ".")
        
        # Basic path validation
        if ".." in path:
            return False
        
        return True
    
    def get_required_permissions(self) -> List[str]:
        return ["file.read"]


class DeleteFileAction(Action):
    """Action to delete a file safely"""
    
    def get_definition(self) -> ActionDefinition:
        return ActionDefinition(
            name="delete_file",
            description="Delete a file safely",
            type=ActionType.WRITE,
            permission_level=PermissionLevel.WRITE,
            parameters=[
                ParameterDefinition(
                    name="filename",
                    type="string",
                    description="Path to the file to delete",
                    required=True,
                    validation="file_exists"
                ),
                ParameterDefinition(
                    name="confirm",
                    type="bool",
                    description="Confirmation that file should be deleted",
                    required=True
                )
            ],
            returns=[
                ParameterDefinition(
                    name="success",
                    type="bool",
                    description="Whether the delete operation was successful"
                )
            ],
            examples=[
                "delete_file filename=temp.txt confirm=true"
            ]
        )
    
    async def execute(self, ctx: ActionContext) -> ActionResult:
        filename = ctx.parameters.get("filename")
        confirm = ctx.parameters.get("confirm", False)
        
        if not filename:
            return ActionResult(
                success=False,
                error="filename parameter is required"
            )
        
        if not confirm:
            return ActionResult(
                success=False,
                error="confirmation is required to delete files"
            )
        
        try:
            # Check if file exists
            if not os.path.exists(filename):
                return ActionResult(
                    success=False,
                    error=f"File '{filename}' does not exist"
                )
            
            # Check if it's actually a file
            if not os.path.isfile(filename):
                return ActionResult(
                    success=False,
                    error=f"'{filename}' is not a file"
                )
            
            # Delete the file
            os.remove(filename)
            
            return ActionResult(
                success=True,
                data={
                    "success": True,
                    "filename": filename
                }
            )
            
        except Exception as e:
            return ActionResult(
                success=False,
                error=f"Failed to delete file: {str(e)}"
            )
    
    def validate(self, ctx: ActionContext) -> bool:
        filename = ctx.parameters.get("filename")
        confirm = ctx.parameters.get("confirm", False)
        
        if not filename or not confirm:
            return False
        
        # Basic path validation
        if ".." in filename:
            return False
        
        return True
    
    def get_required_permissions(self) -> List[str]:
        return ["file.write"]


class FileActions:
    """Container class for all file-related actions"""
    
    def __init__(self):
        self.read_action = ReadFileAction()
        self.write_action = WriteFileAction()
        self.list_action = ListDirectoryAction()
        self.delete_action = DeleteFileAction()
    
    def get_all_actions(self) -> List[Action]:
        """Get all file actions"""
        return [
            self.read_action,
            self.write_action,
            self.list_action,
            self.delete_action
        ]

