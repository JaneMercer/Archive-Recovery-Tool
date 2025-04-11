import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk
import os
import shutil
from gui.settings_window import SettingsWindow


class MainWindow:
    """Main application window with recovery workflow"""

    def __init__(self, root, config_manager, path_validator):
        """Initialize the main application window

        Args:
            root (tk.Tk): The root Tkinter window
            config_manager (ConfigManager): The configuration manager
            path_validator (PathValidator): The path validator
        """
        self.root = root
        self.config_manager = config_manager
        self.path_validator = path_validator

        # Get saved paths for default wordlist location
        self.hashcat_path = self.config_manager.get_path("hashcat")
        self.john_dir = self.config_manager.get_path("john_dir")

        # Create variables for form fields
        self.archive_path_var = tk.StringVar()
        self.wordlist_path_var = tk.StringVar()
        self.output_path_var = tk.StringVar()
        self.archive_type_var = tk.StringVar(value="auto")
        self.brute_force_var = tk.BooleanVar(value=False)
        self.min_length_var = tk.IntVar(value=1)
        self.max_length_var = tk.IntVar(value=8)
        self.charset_var = tk.StringVar(value="abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789")

        # Initialize UI
        self._init_ui()

    def _init_ui(self):
        """Initialize the user interface"""
        # Create main frame
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Title
        title_frame = ttk.Frame(main_frame)
        title_frame.grid(row=0, column=0, columnspan=3, sticky=tk.W + tk.E, pady=(0, 10))

        ttk.Label(
            title_frame,
            text="Archive Password Recovery",
            font=("TkDefaultFont", 16, "bold")
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            title_frame,
            text="⚙️ Settings",
            command=self._open_settings
        ).pack(side=tk.RIGHT, padx=5)

        # Archive path section
        ttk.Label(main_frame, text="Archive File:").grid(
            row=1, column=0, sticky=tk.W, pady=5
        )

        archive_frame = ttk.Frame(main_frame)
        archive_frame.grid(row=1, column=1, columnspan=2, sticky=tk.W + tk.E, pady=5)

        ttk.Entry(
            archive_frame,
            textvariable=self.archive_path_var,
            width=50
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        ttk.Button(
            archive_frame,
            text="Browse",
            command=self._browse_archive
        ).pack(side=tk.RIGHT)

        # Archive type selection
        ttk.Label(main_frame, text="Archive Type:").grid(
            row=2, column=0, sticky=tk.W, pady=5
        )

        archive_type_frame = ttk.Frame(main_frame)
        archive_type_frame.grid(row=2, column=1, columnspan=2, sticky=tk.W, pady=5)

        archive_types = [("Auto-detect", "auto"), ("RAR", "rar"), ("ZIP", "zip"), ("7Z", "7z")]
        for i, (text, value) in enumerate(archive_types):
            ttk.Radiobutton(
                archive_type_frame,
                text=text,
                variable=self.archive_type_var,
                value=value
            ).grid(row=0, column=i, padx=10)

        # Attack method section
        attack_frame = ttk.LabelFrame(main_frame, text="Attack Method", padding=10)
        attack_frame.grid(row=3, column=0, columnspan=3, sticky=tk.W + tk.E, pady=10)

        # Wordlist section
        wordlist_option = ttk.Frame(attack_frame)
        wordlist_option.pack(fill=tk.X, expand=True, pady=5)

        ttk.Radiobutton(
            wordlist_option,
            text="Dictionary Attack",
            variable=self.brute_force_var,
            value=False,
            command=self._toggle_attack_method
        ).pack(side=tk.LEFT)

        ttk.Label(wordlist_option, text="Wordlist File:").pack(side=tk.LEFT, padx=(20, 5))

        self.wordlist_entry = ttk.Entry(
            wordlist_option,
            textvariable=self.wordlist_path_var,
            width=30
        )
        self.wordlist_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        self.wordlist_browse_btn = ttk.Button(
            wordlist_option,
            text="Browse",
            command=self._browse_wordlist
        )
        self.wordlist_browse_btn.pack(side=tk.RIGHT)

        # Brute force section
        bruteforce_option = ttk.Frame(attack_frame)
        bruteforce_option.pack(fill=tk.X, expand=True, pady=5)

        ttk.Radiobutton(
            bruteforce_option,
            text="Brute Force Attack",
            variable=self.brute_force_var,
            value=True,
            command=self._toggle_attack_method
        ).pack(side=tk.LEFT)

        # Brute force settings
        self.bruteforce_settings = ttk.Frame(attack_frame)
        self.bruteforce_settings.pack(fill=tk.X, expand=True, pady=5)

        ttk.Label(self.bruteforce_settings, text="Min Length:").grid(row=0, column=0, padx=(30, 5), pady=5)
        self.min_length_spin = ttk.Spinbox(
            self.bruteforce_settings,
            from_=1,
            to=12,
            width=5,
            textvariable=self.min_length_var
        )
        self.min_length_spin.grid(row=0, column=1, padx=5, pady=5)

        ttk.Label(self.bruteforce_settings, text="Max Length:").grid(row=0, column=2, padx=(15, 5), pady=5)
        self.max_length_spin = ttk.Spinbox(
            self.bruteforce_settings,
            from_=1,
            to=12,
            width=5,
            textvariable=self.max_length_var
        )
        self.max_length_spin.grid(row=0, column=3, padx=5, pady=5)

        ttk.Label(self.bruteforce_settings, text="Character Set:").grid(row=1, column=0, padx=(30, 5), pady=5,
                                                                        sticky=tk.W)
        charset_frame = ttk.Frame(self.bruteforce_settings)
        charset_frame.grid(row=1, column=1, columnspan=3, sticky=tk.W + tk.E, pady=5)

        # Store radio buttons in a list for later access
        self.charset_radios = []

        predefined_charsets = [
            ("a-z", "abcdefghijklmnopqrstuvwxyz"),
            ("A-Z", "ABCDEFGHIJKLMNOPQRSTUVWXYZ"),
            ("0-9", "0123456789"),
            ("a-z,0-9", "abcdefghijklmnopqrstuvwxyz0123456789"),
            ("All", "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+[]{}|;:,.<>?/\\\"'`~")
        ]

        for i, (text, value) in enumerate(predefined_charsets):
            radio = ttk.Radiobutton(
                charset_frame,
                text=text,
                command=lambda v=value: self.charset_var.set(v)
            )
            radio.grid(row=0, column=i, padx=5)
            self.charset_radios.append(radio)

        # Output path section
        ttk.Label(main_frame, text="Output Path:").grid(
            row=4, column=0, sticky=tk.W, pady=5
        )

        output_frame = ttk.Frame(main_frame)
        output_frame.grid(row=4, column=1, columnspan=2, sticky=tk.W + tk.E, pady=5)

        ttk.Entry(
            output_frame,
            textvariable=self.output_path_var,
            width=50
        ).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 5))

        ttk.Button(
            output_frame,
            text="Browse",
            command=self._browse_output
        ).pack(side=tk.RIGHT)

        # Action buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=5, column=0, columnspan=3, sticky=tk.E, pady=15)

        ttk.Button(
            button_frame,
            text="Extract Hash Only",
            command=self._extract_hash
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            button_frame,
            text="Start Recovery",
            command=self._start_recovery
        ).pack(side=tk.LEFT, padx=5)

        # Status bar
        status_frame = ttk.Frame(main_frame)
        status_frame.grid(row=6, column=0, columnspan=3, sticky=tk.W + tk.E, pady=5)

        self.status_label = ttk.Label(
            status_frame,
            text="Ready",
            relief=tk.SUNKEN,
            anchor=tk.W
        )
        self.status_label.pack(fill=tk.X)

        # Configure grid weights
        main_frame.columnconfigure(1, weight=1)

        # Initially disable brute force settings
        self._toggle_attack_method()

        # Set default wordlist if hashcat is configured
        if self.hashcat_path:
            hashcat_dir = os.path.dirname(self.hashcat_path)
            example_dict = os.path.join(hashcat_dir, "example0.dict")
            if os.path.exists(example_dict):
                self.wordlist_path_var.set(example_dict)

    def _open_settings(self):
        """Open the settings window"""
        # Create a new toplevel window
        settings_window = tk.Toplevel(self.root)
        settings_window.title("Tool Settings")
        settings_window.geometry("650x450")
        settings_window.transient(self.root)  # Make it a transient window (always on top of parent)
        settings_window.grab_set()  # Modal window

        # Initialize the settings window
        app_window = SettingsWindow(settings_window, self.config_manager, self.path_validator)

        # Wait for the window to be closed
        self.root.wait_window(settings_window)

        # Refresh paths after settings window is closed
        self.hashcat_path = self.config_manager.get_path("hashcat")
        self.john_dir = self.config_manager.get_path("john_dir")

    def _browse_archive(self):
        """Open file dialog to browse for archive file"""
        filetypes = [
            ("Archive files", "*.rar *.zip *.7z"),
            ("RAR archives", "*.rar"),
            ("ZIP archives", "*.zip"),
            ("7Z archives", "*.7z"),
            ("All files", "*.*")
        ]

        filename = filedialog.askopenfilename(
            title="Select Archive File",
            filetypes=filetypes
        )

        if filename:
            self.archive_path_var.set(filename)

            # Auto-set output directory to same location as archive
            if not self.output_path_var.get():
                archive_dir = os.path.dirname(filename)
                self.output_path_var.set(archive_dir)

            # Auto-detect archive type
            if self.archive_type_var.get() == "auto":
                lower_filename = filename.lower()
                if lower_filename.endswith(".rar"):
                    self.archive_type_var.set("rar")
                elif lower_filename.endswith(".zip"):
                    self.archive_type_var.set("zip")
                elif lower_filename.endswith(".7z"):
                    self.archive_type_var.set("7z")

    def _browse_wordlist(self):
        """Open file dialog to browse for wordlist file"""
        filetypes = [
            ("Dictionary files", "*.dict *.txt *.lst"),
            ("All files", "*.*")
        ]

        filename = filedialog.askopenfilename(
            title="Select Wordlist File",
            filetypes=filetypes
        )

        if filename:
            self.wordlist_path_var.set(filename)

    def _browse_output(self):
        """Open directory dialog to browse for output location"""
        directory = filedialog.askdirectory(
            title="Select Output Directory"
        )

        if directory:
            self.output_path_var.set(directory)

    def _toggle_attack_method(self):
        """Toggle between dictionary and brute force attack methods"""
        if self.brute_force_var.get():
            # Enable brute force settings, disable wordlist
            self.wordlist_entry.config(state="disabled")
            self.wordlist_browse_btn.config(state="disabled")

            # Enable specific bruteforce widgets
            self.min_length_spin.config(state="normal")
            self.max_length_spin.config(state="normal")
            for radio in self.charset_radios:
                radio.config(state="normal")
        else:
            # Enable wordlist, disable brute force settings
            self.wordlist_entry.config(state="normal")
            self.wordlist_browse_btn.config(state="normal")

            # Disable specific bruteforce widgets
            self.min_length_spin.config(state="disabled")
            self.max_length_spin.config(state="disabled")
            for radio in self.charset_radios:
                radio.config(state="disabled")

    def _extract_hash(self):
        """Extract hash from the archive without cracking"""
        # This will be implemented later
        messagebox.showinfo("Info", "Hash extraction will be implemented in the next phase")

    def _start_recovery(self):
        """Start the password recovery process"""
        # This will be implemented later
        messagebox.showinfo("Info", "Password recovery will be implemented in the next phase")