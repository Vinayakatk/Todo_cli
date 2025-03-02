# TODO CLI Technical Documentation

## Table of Contents
- [User Guide](#user-guide)
  - [Installation](#installation)
  - [Configuration](#configuration)
  - [Usage](#usage)
    - [Adding Tasks](#adding-tasks)
    - [Listing Tasks](#listing-tasks)
    - [Completing Tasks](#completing-tasks)
    - [Deleting Tasks](#deleting-tasks)
- [Developer Guide](#developer-guide)
  - [Architecture](#architecture)
  - [Project Structure](#project-structure)
  - [Core Components](#core-components)
  - [Extending the Application](#extending-the-application)

## User Guide

### Installation

You can install the TODO CLI application using one of the following method:

#### Install from Source (Recommended for Developers)

1. Clone the repository:
```bash
git clone git@github.com:Vinayakatk/Todo_cli.git
cd Todo_cli
```

2. Create and activate a virtual environment:
```bash
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
```

3. Install in development mode:
```bash
pip install -e .
```

This will install all required dependencies and the CLI tool. The `-e` flag installs the package in "editable" mode, which is useful for development.

#### System Requirements

- Python 3.6 or higher
- pip package manager

#### Verifying Installation

After installation, verify that the CLI tool is available:

```bash
todo --help
```

You should see the help message with available commands.

### Configuration

The TODO CLI application can be configured using the next command which walk you through the configuration process:

```bash
todo storage configure
```

### Usage

#### Adding Tasks
```bash
todo add "Complete documentation" -d "Write user and developer guides"
```

#### Listing Tasks
```bash
todo list
```

#### Completing Tasks
```bash
todo complete <task-id>
```

#### Deleting Tasks
```bash
todo delete <task-id>
```

## Developer Guide

### Architecture

The application follows a layered architecture pattern with modular storage backends:

1. **CLI Layer** (`cli.py`)
   - Handles command-line interface and user interaction
   - Uses Click for command parsing
   - Formats output using Rich library

2. **Service Layer** (`service.py`)
   - Implements business logic
   - Manages task operations
   - Coordinates between CLI and storage layers
   - Handles task validation and state management
   - Extensible design for adding new service implementation

3. **Storage Layer**
   - Provides abstract interface (`storage.py`)
   - Extensible storage backend implementations:
     - Default JSON file storage (included in `storage.py`)
   - Extensible design for adding new storage backends

4. **Configuration System** (`config.py`)
   - Manages storage backend selection
   - Handles application settings
   - Provides storage backend registration mechanism
   - Validates the backend schema against user settings

### Project Structure

```
todo_cli/
├── todo_cli/
│   ├── __init__.py
│   ├── cli.py          # Command-line interface
│   ├── config.py       # Configuration management
│   ├── models.py       # Data models
│   ├── service.py      # Business logic
│   ├── storage.py      # Storage interface and JSON implementation
├── tests/
│   ├── __init__.py
│   ├── test_models.py  # Model unit tests
│   ├── test_service.py # Service layer tests
│   ├── test_storage.py # Base storage tests
├── requirements.txt    # Project dependencies
├── pyproject.toml     # Project metadata and build configuration
├── LICENSE.md         # License information
└── README.md         # Project documentation

```

### Core Components

#### Models

The `Task` model (`models.py`) represents a todo item with the following attributes:
- `id`: Unique identifier
- `title`: Task title
- `description`: Optional task description
- `status`: Task status (OPEN/COMPLETED)
- `created_at`: Creation timestamp
- `completed_at`: Completion timestamp

#### Storage System

The storage system is designed to be extensible:

1. Abstract Base Class (`Storage`):
```python
class StorageInterface(ABC):
    @abstractmethod
    def add_task(self, task: Task) -> None: pass
    @abstractmethod
    def get_task(self, task_id: str) -> Optional[Task]: pass
    @abstractmethod
    def list_tasks(self) -> List[Task]: pass
    @abstractmethod
    def update_task(self, task: Task) -> None: pass
    @abstractmethod
    def delete_task(self, task_id: str) -> None: pass
```

2. JSON File Implementation (`JsonFileStorage`):
- Stores tasks in a JSON file
- Handles file creation and data serialization
- Thread-safe file operations

### Extending the Application

#### Adding a New Storage Backend

1. Create a new class implementing the `Storage` interface:

```python
from todo_cli.storage import StorageInterface


class MyCustomStorage(StorageInterface):
    def __init__(self, connection_string: str):
        # Initialize your storage
        pass

    def add_task(self, task: Task) -> None:
        # Implement task creation
        pass

    # Implement other required methods
```

2. Register the backend in `config.py`:
```python
    STORAGE_BACKENDS: Dict[str, Type[Storage]] = {
        "json": JsonFileStorage,
        "mystorage": StorageClass
    }
```

#### Adding New Backend in CLI

1. Add a new function in `cli.py`:
```python
def todo_<backend_name>() -> Dict[str, Any]:
    """This function is called by 'todo config storage' after selection for specific backend
    The function has to return key value pairs of parameter_name: parameter_value 
    {
        parameter_name1: parameter_value1,
        parameter_name2: parameter_value3
        .....
    
    }
    Example for mysql: 
    
    {
        host: ipaddress,
        port: 65
        user_name: xxxxx
        password: yyyy
    }
    
    """
```
2. hook the new function in `cli.py` inside `UserConfig` to return parameter values as `Dict[str, Any]`:

```python
class UserConfig:
    """This class is responsible for fetching user config from CLI and returning the key-value pairs."""
    @staticmethod
    def get_user_config(storage_type: str) -> Dict[str, Any]:
        if storage_type == "json":
            # function that handles json specific input from user and returns all necessary parameters
            return todo_json()
        else:
            return {}
```
#### The Service is designed to be extensible supporting different implementation:

1. Abstract Base Class (`TodoServiceInterface`):
```python
class TodoServiceInterface(ABC):
    """Abstract base class for TODO task management services."""
    @abstractmethod
    def create_task(self, title: str, description: Optional[str] = None) -> Task:
        pass
    
    @abstractmethod
    def get_task(self, task_id: int) -> Optional[Task]:
        pass

    @abstractmethod
    def list_tasks(self) -> List[Task]:
        pass

    @abstractmethod
    def complete_task(self, task_id: int) -> Task:
        pass

    @abstractmethod
    def delete_task(self, task_id: int) -> None:
        pass

```

2. Default Service Implementation (`TodoService`):
- Handles files and databases  


#### Error Handling

The application uses standard Python exceptions for error handling:
- `KeyError`: For key not found errors from configs 
- `ValueError`: For validation errors in business logic
- Custom exceptions can be added for specific cases

#### Testing

To run tests:
```bash
python -m pytest tests/
```

When adding new features:
1. Write unit tests for new components
2. Ensure existing tests pass
3. Update documentation as needed

## Contributing

1. Fork the repository
2. Create a feature branch
3. Implement changes with tests
4. Submit a pull request

Please follow the existing code style and include appropriate documentation updates.
