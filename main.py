import tkinter as tk
from tkinter import filedialog
from gui.main_window import MainWindow
from config.config_manager import ConfigManager
from utils.path_validator import PathValidator
import os

def main():
    """Main entry point for the application"""

    # Initialize config manager
    config_manager = ConfigManager()

    # Initialize path validator
    path_validator = PathValidator()

    # Create root window
    root = tk.Tk()
    root.title("Archive Password Recovery")
    root.geometry("750x600")

    # Initialize the main window
    app = MainWindow(root, config_manager, path_validator)

    # Start the application
    root.mainloop()


if __name__ == "__main__":
    main()