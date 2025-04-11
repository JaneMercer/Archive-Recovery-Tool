import tkinter as tk
from tkinter import filedialog
from gui.app_window import ApplicationWindow
from config.config_manager import ConfigManager
from utils.path_validator import PathValidator
import os


def ensure_directories_exist():
    """Ensure that all required directories exist"""
    directories = ['gui', 'config', 'utils']
    for directory in directories:
        os.makedirs(directory, exist_ok=True)


def main():
    """Main entry point for the application"""
    # Ensure all directories exist
    ensure_directories_exist()

    # Initialize config manager
    config_manager = ConfigManager()

    # Initialize path validator
    path_validator = PathValidator()

    # Create root window
    root = tk.Tk()
    root.title("Archive Password Recovery")
    root.geometry("650x450")

    # Initialize the main application window
    app = ApplicationWindow(root, config_manager, path_validator)

    # Start the application
    root.mainloop()


if __name__ == "__main__":
    main()