import json
import os
from pathlib import Path


class ConfigManager:
    """Manages the application configuration"""

    def __init__(self, config_file="config.json"):
        """Initialize the configuration manager

        Args:
            config_file (str): Path to the configuration file
        """
        self.config_file = config_file
        self.config = self._load_config()

    def _load_config(self):
        """Load configuration from file

        Returns:
            dict: Configuration dictionary
        """
        if os.path.exists(self.config_file):
            try:
                with open(self.config_file, 'r') as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                return self._create_default_config()
        else:
            return self._create_default_config()

    def _create_default_config(self):
        """Create default configuration

        Returns:
            dict: Default configuration
        """
        return {
            "paths": {
                "hashcat": "",
                "john_dir": ""
            }
        }

    def save_config(self):
        """Save configuration to file"""
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.config, f, indent=4)
            return True
        except IOError as e:
            print(f"Error saving config: {e}")
            return False

    def get_path(self, tool_name):
        """Get the path for a specific tool

        Args:
            tool_name (str): Name of the tool ('hashcat' or 'john_dir')

        Returns:
            str: Path to the tool or empty string if not found
        """
        return self.config.get("paths", {}).get(tool_name, "")

    def set_path(self, tool_name, path):
        """Set the path for a specific tool

        Args:
            tool_name (str): Name of the tool ('hashcat' or 'john_dir')
            path (str): Path to the tool executable or directory
        """
        if "paths" not in self.config:
            self.config["paths"] = {}

        self.config["paths"][tool_name] = path