"""Storage implementations for the TODO CLI application."""

import json
from abc import ABC, abstractmethod
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any
from pydantic import TypeAdapter
from .models import Task

class StorageInterface(ABC):
    """Abstract base class for task storage implementations."""

    @classmethod
    @abstractmethod
    def get_parameters(cls) -> Dict[str, Any]:
        """Each storage backend must return the schema for validating user inputs"""
        pass

    @abstractmethod
    def add_task(self, task: Task) -> None:
        """Add a new task to storage."""
        pass

    @abstractmethod
    def get_task(self, task_id: int) -> Optional[Task]:
        """Retrieve a task by its ID."""
        pass

    @abstractmethod
    def list_tasks(self) -> List[Task]:
        """List all tasks in storage."""
        pass

    @abstractmethod
    def update_task(self, task: Task) -> None:
        """Update an existing task."""
        pass

    @abstractmethod
    def delete_task(self, task_id: int) -> None:
        """Delete a task by its ID."""
        pass


class JsonFileStorage(StorageInterface):
    """JSON file-based implementation of task storage."""

    @classmethod
    def get_parameters(cls) -> Dict[str, Any]:
        """Each storage backend must implement this class method to provide the schema for user input
           This is important for configuring the backend object with necessary parameters."""
        return  { "path": str }

    def __init__(self, parameters: dict[str, Any]):
        """Initialize JSON file storage.

        Args:
            parameters: This will have key value paris of all the parameter values required for
            initializing the storage backend.
        """
        # file_path: Path to the JSON file. Defaults to ~/.todo/tasks.json
        file_path = parameters["path"]

        if file_path is None:
            file_path = str(Path.home() / ".todo" / "tasks.json")
        self.file_path = Path(file_path)
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        """Create the storage file if it doesn't exist."""
        if not self.file_path.exists():
            self.file_path.write_text("[]")

    def _load_tasks(self) -> List[Task]:
        """Load all tasks from the JSON file."""
        content = self.file_path.read_text()
        if not content:
            return []
        
        raw_data = json.loads(content)
        task_adapter = TypeAdapter(List[Task])
        return task_adapter.validate_python(raw_data)

    def _save_tasks(self, tasks: List[Task]) -> None:
        """Save tasks to the JSON file."""
        task_list = [task.model_dump() for task in tasks]
        self.file_path.write_text(json.dumps(task_list, default=str, indent=2))

    def add_task(self, task: Task) -> None:
        tasks = self._load_tasks()
        tasks.append(task)
        self._save_tasks(tasks)

    def get_task(self, task_id: int) -> Optional[Task]:
        tasks = self._load_tasks()
        for task in tasks:
            if task.id == task_id:
                return task
        return None

    def list_tasks(self) -> List[Task]:
        return self._load_tasks()

    def update_task(self, task: Task) -> None:
        tasks = self._load_tasks()
        for i, t in enumerate(tasks):
            if t.id == task.id:
                tasks[i] = task
                self._save_tasks(tasks)
                return
        raise KeyError(f"Task with ID {task.id} not found")

    def delete_task(self, task_id: int) -> None:
        tasks = self._load_tasks()
        for i, task in enumerate(tasks):
            if task.id == task_id:
                tasks.pop(i)
                self._save_tasks(tasks)
                return
        raise KeyError(f"Task with ID {task_id} not found")