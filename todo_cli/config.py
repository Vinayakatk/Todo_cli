"""Configuration management for the TODO CLI application."""

import json
from pathlib import Path
from typing import Dict, Type, Any
from rich.console import Console
from .storage import JsonFileStorage, StorageInterface

console = Console()

class StorageConfig():
    """Configuration for storage backends."""
    # Default storage settings
    DEFAULT_STORAGE_TYPE = "json"
    DEFAULT_CONFIG_PATH = str(Path.home() / ".todo" / "config.json")
    DEFAULT_CONFIG = {
        "json": {
            "path": str(Path.home() / ".todo" / "tasks.json")
        },
        "use": {
            "storage": "json"
        }
    }

    # Map of storage type identifiers to their implementations
    STORAGE_BACKENDS: Dict[str, Type[StorageInterface]] = {
        "json": JsonFileStorage
    }

    @classmethod
    def _ensure_config_exists(cls) -> None:
        """Ensure the config file exists, create it with defaults if it doesn't."""
        config_path = Path(cls.DEFAULT_CONFIG_PATH)
        if not config_path.exists():
            config_path.parent.mkdir(parents=True, exist_ok=True)
            with open(config_path, 'w') as f:
                json.dump(cls.DEFAULT_CONFIG, f, indent=4)


    @classmethod
    def _load_config(cls) -> Dict[str, Any]:
        """Load the configuration from the config file."""
        cls._ensure_config_exists()
        with open(cls.DEFAULT_CONFIG_PATH) as f:
            return json.load(f)


    @classmethod
    def get_storage(cls) -> StorageInterface:
        """Create and return a configured storage instance based on config.json.

        Returns:
            Configured storage instance
        """
        config = cls._load_config()
        storage_type = config["use"]["storage"]

        if storage_type not in cls.STORAGE_BACKENDS:
            raise ValueError(
                f"Unsupported storage type: {storage_type}. "
                f"Available types: {', '.join(cls.STORAGE_BACKENDS.keys())}"
            )

        storage_class = cls.STORAGE_BACKENDS[storage_type]
        # This is the json with all the parameters for particular backend
        storage_config = config[storage_type]
        # pass the dict with parameter values to the storage backend class
        return storage_class(storage_config)


    @classmethod
    def update_config(cls, new_config: Dict[str, Any]) -> None:
        """Update the configuration file with new settings.

        Args:
            new_config: New configuration dictionary to merge with existing config
        """
        StorageConfig.validate_storage_config(new_config)
        config = cls._load_config()
        config.update(new_config)
        with open(cls.DEFAULT_CONFIG_PATH, 'w') as f:
            json.dump(config, f, indent=4)


    @classmethod
    def get_config(cls, storage_type: str) -> Dict[str, Any]:
        """Update the configuration file with new settings.

        Args:
            storage_type: type of the storage for which the config needs to be returned
        """
        config = cls._load_config()
        if storage_type not in config:
            return {}
        return config[storage_type]


    @classmethod
    def validate_storage_config(cls, storage_config: Dict[str, Any]) -> None:
        """ validate the config against the plugin schema for correctness of all parameters.

        Args:
            storage_config: config of the storage backend
        """
        storage_type = storage_config["use"]["storage"]
        if storage_type not in cls.STORAGE_BACKENDS:
            raise ValueError(
                f"Unsupported storage type: {storage_type}. "
                f"Available types: {', '.join(cls.STORAGE_BACKENDS.keys())}"
            )
        storage_class = cls.STORAGE_BACKENDS[storage_type]
        # This is the json with all the parameters for particular backend
        storage_config_keys = set(storage_config[storage_type].keys())
        parameter_keys = set(storage_class.get_parameters().keys())
        if parameter_keys != storage_config_keys:
            console.print(f"❌ Error: Mismatch in the schema for storage {storage_type}, "
                          f"\n misssing {parameter_keys - storage_config_keys}", style="red")
        else:
            console.print(f"✅ All Parameters match for configured {storage_type} storage backend")
