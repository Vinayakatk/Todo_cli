"""Service layer for the TODO CLI application."""

from abc import ABC, abstractmethod
from datetime import datetime
from typing import List, Optional
import uuid

from .models import Task, TaskStatus
from .storage import StorageInterface


class TodoServiceInterface(ABC):
    """Abstract base class for TODO task management services."""

    @abstractmethod
    def create_task(self, title: str, description: Optional[str] = None) -> Task:
        """Create a new task.

        Args:
            title: Title of the task
            description: Optional description of the task

        Returns:
            The created task
        """
        pass

    @abstractmethod
    def get_task(self, task_id: int) -> Optional[Task]:
        """Retrieve a task by its ID.

        Args:
            task_id: ID of the task to retrieve

        Returns:
            The task if found, None otherwise
        """
        pass

    @abstractmethod
    def list_tasks(self) -> List[Task]:
        """List all tasks.

        Returns:
            List of all tasks
        """
        pass

    @abstractmethod
    def complete_task(self, task_id: int) -> Task:
        """Mark a task as completed.

        Args:
            task_id: ID of the task to complete

        Returns:
            The updated task

        Raises:
            KeyError: If the task is not found
        """
        pass

    @abstractmethod
    def delete_task(self, task_id: int) -> None:
        """Delete a task.

        Args:
            task_id: ID of the task to delete

        Raises:
            KeyError: If the task is not found
        """
        pass


class TodoService(TodoServiceInterface):
    """Local implementation of TodoService using file-based storage."""

    def __init__(self, storage: StorageInterface):
        """Initialize the local TODO service.

        Args:
            storage: Storage implementation to use for task persistence
        """
        self.storage = storage

    def create_task(self, title: str, description: Optional[str] = None) -> Task:
        task = Task(
            id=uuid.uuid4().int,
            title=title,
            description=description
        )
        self.storage.add_task(task)
        return task

    def get_task(self, task_id: int) -> Optional[Task]:
        return self.storage.get_task(task_id)

    def list_tasks(self) -> List[Task]:
        return self.storage.list_tasks()

    def complete_task(self, task_id: int) -> Task:
        task = self.storage.get_task(task_id)
        if task is None:
            raise KeyError(f"Task with ID {task_id} not found")

        task.status = TaskStatus.COMPLETED
        task.completed_at = datetime.now()
        self.storage.update_task(task)
        return task

    def delete_task(self, task_id: int) -> None:
        self.storage.delete_task(task_id)


class RESTTodoService(TodoServiceInterface):
    """REST API implementation of TodoService."""

    def __init__(self, base_url: str, api_key: Optional[str] = None):
        """Initialize the REST TODO service.

        Args:
            base_url: Base URL of the REST API
            api_key: Optional API key for authentication
        """
        self.base_url = base_url.rstrip('/')
        self.api_key = api_key

    def create_task(self, title: str, description: Optional[str] = None) -> Task:
        # TODO: Implement REST API call for task creation
        raise NotImplementedError("REST API implementation not available yet")

    def get_task(self, task_id: int) -> Optional[Task]:
        # TODO: Implement REST API call for task retrieval
        raise NotImplementedError("REST API implementation not available yet")

    def list_tasks(self) -> List[Task]:
        # TODO: Implement REST API call for listing tasks
        raise NotImplementedError("REST API implementation not available yet")

    def complete_task(self, task_id: int) -> Task:
        # TODO: Implement REST API call for task completion
        raise NotImplementedError("REST API implementation not available yet")

    def delete_task(self, task_id: int) -> None:
        # TODO: Implement REST API call for task deletion
        raise NotImplementedError("REST API implementation not available yet")