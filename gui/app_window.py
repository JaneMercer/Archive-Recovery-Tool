import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import os


class ApplicationWindow:
    """Main application window class"""

    def __init__(self, root, config_manager, path_validator):
        """Initialize the application window

        Args:
            root (tk.Tk): The root Tkinter window
            config_manager (ConfigManager): The configuration manager
            path_validator (PathValidator): The path validator
        """
        self.root = root
        self.config_manager = config_manager
        self.path_validator = path_validator

        # Get saved paths if they exist
        self.hashcat_path = self.config_manager.get_path("hashcat")
        self.john_dir = self.config_manager.get_path("john_dir")

        self._init_ui()

    def _init_ui(self):
        """Initialize the user interface"""
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Create and place widgets
        ttk.Label(main_frame, text="Configure Tool Paths", font=("TkDefaultFont", 14, "bold")).grid(
            row=0, column=0, columnspan=3, pady=10, sticky=tk.W
        )

        # Hashcat section
        ttk.Label(main_frame, text="Hashcat Executable:").grid(
            row=1, column=0, sticky=tk.W, pady=5
        )

        self.hashcat_path_var = tk.StringVar(value=self.hashcat_path if self.hashcat_path else "")
        hashcat_entry = ttk.Entry(main_frame, textvariable=self.hashcat_path_var, width=50)
        hashcat_entry.grid(row=1, column=1, sticky=tk.W + tk.E, padx=5, pady=5)

        ttk.Button(main_frame, text="Browse", command=self._browse_hashcat).grid(
            row=1, column=2, padx=5, pady=5
        )

        ttk.Button(main_frame, text="Test Hashcat", command=self._test_hashcat).grid(
            row=2, column=1, sticky=tk.W, pady=5
        )

        # John the Ripper section
        ttk.Label(main_frame, text="John the Ripper Directory:").grid(
            row=3, column=0, sticky=tk.W, pady=5
        )

        self.john_dir_var = tk.StringVar(value=self.john_dir if self.john_dir else "")
        john_entry = ttk.Entry(main_frame, textvariable=self.john_dir_var, width=50)
        john_entry.grid(row=3, column=1, sticky=tk.W + tk.E, padx=5, pady=5)

        ttk.Button(main_frame, text="Browse", command=self._browse_john_dir).grid(
            row=3, column=2, padx=5, pady=5
        )

        ttk.Button(main_frame, text="Test John Directory", command=self._test_john_dir).grid(
            row=4, column=1, sticky=tk.W, pady=5
        )

        # Info section
        info_frame = ttk.LabelFrame(main_frame, text="Information", padding=10)
        info_frame.grid(row=5, column=0, columnspan=3, sticky=tk.W + tk.E, pady=10)

        info_text = (
            "• For hashcat, select the hashcat.exe executable file\n"
            "• For John the Ripper, select the directory containing john.exe, zip2john.exe, etc."
        )
        ttk.Label(info_frame, text=info_text, justify=tk.LEFT).pack(anchor=tk.W)

        # Save button
        ttk.Button(main_frame, text="Save Configuration", command=self._save_config).grid(
            row=6, column=1, pady=20
        )

        # Configure grid column weights
        main_frame.columnconfigure(1, weight=1)

    def _browse_hashcat(self):
        """Open file dialog to browse for hashcat executable"""
        filename = filedialog.askopenfilename(
            title="Select Hashcat Executable",
            filetypes=[("Executable files", "*.exe"), ("All files", "*.*")]
        )
        if filename:
            self.hashcat_path_var.set(filename)

    def _browse_john_dir(self):
        """Open directory dialog to browse for John the Ripper directory"""
        directory = filedialog.askdirectory(
            title="Select John the Ripper Directory"
        )
        if directory:
            self.john_dir_var.set(directory)

    def _test_hashcat(self):
        """Test if the hashcat path is valid"""
        path = self.hashcat_path_var.get()
        if not path:
            messagebox.showerror("Error", "Hashcat path cannot be empty")
            return

        if self.path_validator.is_valid_hashcat(path):
            messagebox.showinfo("Success", "Hashcat executable is valid")
        else:
            messagebox.showerror(
                "Error",
                "Invalid hashcat executable. Please ensure you've selected the correct hashcat.exe file."
            )

    def _test_john_dir(self):
        """Test if the John the Ripper directory is valid"""
        directory = self.john_dir_var.get()
        if not directory:
            messagebox.showerror("Error", "John the Ripper directory path cannot be empty")
            return

        if self.path_validator.is_valid_john_directory(directory):
            messagebox.showinfo(
                "Success",
                "John the Ripper directory contains the necessary executables"
            )
        else:
            messagebox.showerror(
                "Error",
                "Invalid John the Ripper directory. The directory should contain john.exe, zip2john.exe, "
                "rar2john.exe and preferably 7z2john.pl or similar for 7z support."
            )

    def _save_config(self):
        """Save the configuration"""
        hashcat_path = self.hashcat_path_var.get()
        john_dir = self.john_dir_var.get()

        # Validate paths before saving
        if hashcat_path and not self.path_validator.is_valid_hashcat(hashcat_path):
            messagebox.showerror("Error", "Invalid hashcat executable path")
            return

        if john_dir and not self.path_validator.is_valid_john_directory(john_dir):
            messagebox.showerror("Error", "Invalid John the Ripper directory")
            return

        # Save paths to configuration
        self.config_manager.set_path("hashcat", hashcat_path)
        self.config_manager.set_path("john_dir", john_dir)
        self.config_manager.save_config()

        messagebox.showinfo("Success", "Configuration saved successfully")