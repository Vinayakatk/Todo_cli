"""Command-line interface for the TODO CLI application."""

from typing import Optional, List, Dict, Any
import os
import json
import click
from rich.console import Console
from rich.table import Table
from rich.prompt import IntPrompt, Prompt, Confirm
from pathlib import Path
from .models import TaskStatus
from .service import TodoService, TodoServiceInterface
from .config import StorageConfig

console = Console()

class UserConfig:
    """This class is responsible for fetching user config from CLI and returning the key-value pairs."""
    @staticmethod
    def get_user_config(storage_type: str) -> Dict[str, Any]:
        if storage_type == "json":
            # function that handles json specific input from user and returns all necessary parameters
            return todo_json()
        else:
            return {}


def get_service() -> TodoServiceInterface:
    """Create and return a TodoService instance with configured storage."""
    from .config import StorageConfig
    return TodoService(StorageConfig.get_storage())

def format_task_table(tasks) -> Table:
    """Create a rich table for displaying tasks."""
    table = Table(show_header=True)
    table.add_column("ID")
    table.add_column("Title")
    table.add_column("Description")
    table.add_column("Status")
    table.add_column("Created")
    table.add_column("Completed")

    for task in tasks:
        completed_at = task.completed_at.strftime("%Y-%m-%d %H:%M") if task.completed_at else "-"
        table.add_row(
            str(task.id),
            task.title,
            task.description or "-",
            task.status.value,
            task.created_at.strftime("%Y-%m-%d %H:%M"),
            completed_at,
            style="dim" if task.status == TaskStatus.COMPLETED else ""
        )

    return table


def todo_json() -> Dict[str, Any]:
    """ This function is to configure the json backend and get the parameter values from user
        Returns: -> Dict[str, Any] The key value pairs of parameters
         "json": {
            "path": "path to the data file"
         }
    """
    backend_config = {}
    selected_storage = 'json'
    storage_class = StorageConfig.STORAGE_BACKENDS[selected_storage]
    # For file-based storages, handle path configuration
    default_path = str(Path.home() / ".todo" / f"tasks.{selected_storage}")
    console.print("\nSelect one of two options by pressing according number...")
    console.print("1. Use default path", f"({default_path})")
    console.print("2. Provide path")

    path_choice = Prompt.ask(
        "Path configuration",
        choices=["1", "2"],
        show_choices=False
    )

    if path_choice == "1":
        # Use default path
        backend_config[selected_storage] = {"path": default_path}
        console.print(f"File will be created at default path ({default_path})")

    else:
        # Custom path
        console.print("\nProvide path...")
        custom_path = Prompt.ask(f"Storage path (start your path with {Path.home()})")

        if str(Path.home()) not in custom_path:
            console.print(f"Please, start path to your .json file with {Path.home()}")
            return

        backend_config[selected_storage] = {"path": custom_path }

    return backend_config


def parse_task_id(task_id):
    """convert task_id to an integer. Throw error if task_id cannot be converted to an integer."""
    try:
        return int(task_id)
    except ValueError:
        console.print("❌ Error: task_id should be an integer", style="red")
        return None


@click.group()
def cli():
    """A simple command-line TODO list manager.

    Configuration:\n
    The application storage can be configured using todo config command:\n\n
            $ todo config storage


    Usage Examples:\n
        Add a task:\n
            $ todo add "Complete documentation" -d "Write user and developer guides"

        List all tasks:\n
            $ todo list

        Complete a task:\n
            $ todo complete <task-id>

        Delete a task:\n
            $ todo delete <task-id>
    """
    pass


@cli.command()
@click.argument("title")
@click.option("-d", "--description", help="Optional task description")
def add(title: str, description: Optional[str]):
    """Add a new task with the given title and optional description."""
    service = get_service()
    task = service.create_task(title, description)
    console.print(f"✅ Created task: {task.title} (ID: {task.id})")


@cli.command()
def list():
    """List all tasks."""
    service = get_service()
    tasks = service.list_tasks()
    if not tasks:
        console.print("No tasks found.")
        return

    table = format_task_table(tasks)
    console.print(table)


@cli.command()
@click.argument("task_id")
def complete(task_id: str):
    """Mark a task as completed."""
    service = get_service()
    value = parse_task_id(task_id)
    if value is None:
        return
    try:
        task = service.complete_task(value)
        console.print(f"✅ Marked task as completed: {task.title}")
    except KeyError as e:
        console.print(f"❌ Error: {str(e)}", style="red")


@cli.command()
@click.argument("task_id")
def delete(task_id: str):
    """Delete a task."""
    service = get_service()
    value = parse_task_id(task_id)
    if value is None:
        return
    try:
        service.delete_task(value)
        console.print(f"✅ Deleted task with ID: {task_id}")
    except KeyError as e:
        console.print(f"❌ Error: {str(e)}", style="red")


@cli.group()
def config():
    """Configure storage backend settings."""
    pass


@config.command(name="show")
def show():
    """show the content and path of the config file location"""
    config_path = os.path.expanduser("~/.todo/config.json")

    try:
        # Open and read the JSON file
        with open(config_path, "r") as file:
            config_data = json.load(file)

        # Print the JSON content
        console.print(json.dumps(config_data, indent=4))

    except FileNotFoundError:
        console.print(f"❌ Error: Config file not found at {config_path}")
    except json.JSONDecodeError:
        console.print(f"❌ Error: Invalid JSON format at {config_path}")


@config.command(name="storage")
def storage():
    """Configure storage backend settings."""
    try:
        # Display available storage types
        storage_types = StorageConfig.STORAGE_BACKENDS.keys()
        # unpacks the keys from the dictionary
        storage_choices = [*storage_types]
        console.print("\nChoose preferable storage for you by pressing according number...")
        for i, storage_type in enumerate(storage_types, 1):
            console.print(f"{i}. {str(storage_type)}")

        # Get user selection
        selection = IntPrompt.ask(
            "Select storage type",
            choices=[str(i) for i, storage_type in enumerate(storage_types, 1)],
            show_choices=True
        )
        selected_storage = storage_choices[int(selection) - 1]
        console.print(f"selected: {selected_storage}")
        # Call the CLI backend handles for further processing
        backend_config = UserConfig.get_user_config(selected_storage)
        # Update the use section
        backend_config["use"] = {"storage": selected_storage}

        # Save configuration
        StorageConfig.update_config(backend_config)
        console.print(f"✅ Successfully configured {selected_storage} storage backend")

    except Exception as e:
        console.print(f"❌ Error: {str(e)}", style="red")


if __name__ == "__main__":
    cli()