import os
import subprocess
import platform


class PathValidator:
    """Validates tool paths"""

    def is_valid_executable(self, path):
        """Check if the path points to an executable file

        Args:
            path (str): Path to check

        Returns:
            bool: True if path is a valid executable, False otherwise
        """
        if not path or not os.path.exists(path):
            return False

        if not os.path.isfile(path):
            return False

        # Check if file is executable
        if platform.system() == "Windows":
            return path.lower().endswith(('.exe', '.bat', '.cmd'))
        else:
            return os.access(path, os.X_OK)

    def is_valid_hashcat(self, path):
        """Check if the path points to a valid hashcat executable

        Args:
            path (str): Path to check

        Returns:
            bool: True if valid hashcat executable, False otherwise
        """
        if not os.path.exists(path):
            return False

        if not os.path.isfile(path):
            return False

        # Just check if the file exists and has the right extension
        if platform.system() == "Windows" and not path.lower().endswith('.exe'):
            return False

        # Try running hashcat with --help to validate (more reliable than --version)
        try:
            result = subprocess.run(
                [path, "--help"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                timeout=5
            )

            # Check if output contains "hashcat" or related keywords
            output = (result.stdout.decode('utf-8', errors='ignore') +
                      result.stderr.decode('utf-8', errors='ignore')).lower()

            # Look for common hashcat terms
            return any(term in output for term in ["hashcat", "hash type", "attack mode", "opencl"])
        except (subprocess.SubprocessError, OSError) as e:
            print(f"Error validating hashcat: {e}")
            return False

    def is_valid_john_directory(self, directory_path):
        """Check if the directory contains necessary John the Ripper executables

        Args:
            directory_path (str): Path to the John the Ripper directory

        Returns:
            bool: True if directory contains necessary executables, False otherwise
        """
        if not directory_path or not os.path.exists(directory_path) or not os.path.isdir(directory_path):
            return False

        # Define essential John the Ripper executables we need for archive handling
        essential_files = []
        if platform.system() == "Windows":
            essential_files = ["john.exe", "zip2john.exe", "rar2john.exe"]
            # Check for 7z2john.pl (it's often a Perl script)
            optional_files = ["7z2john.pl", "7z2john.exe"]
        else:
            essential_files = ["john", "zip2john", "rar2john"]
            optional_files = ["7z2john.pl", "7z2john"]

        # Check if all essential files exist
        for file in essential_files:
            if not os.path.isfile(os.path.join(directory_path, file)):
                return False

        # Check if at least one of the optional files exists for 7z support
        has_7z_support = any(os.path.isfile(os.path.join(directory_path, file)) for file in optional_files)

        return True