import os
import zipfile
from typing import Optional

import rarfile
import py7zr


class ArchiveHandler:
    SUPPORTED_TYPES = ['rar', 'zip', '7z']

    # File signatures for better detection
    FILE_SIGNATURES = {
        b'PK\x03\x04': 'zip',
        b'Rar!\x1a\x07': 'rar',
        b'7z\xbc\xaf\x27\x1c': '7z'
    }

    def __init__(self, filepath=None, archive_type='auto'):
        self.filepath = filepath
        self.archive_type = archive_type
        self._detected_type = None

        if self.archive_type == 'auto':
            self._detected_type = self.detect_type()
            self.archive_type = self._detected_type or 'unknown'

    def detect_type(self) -> Optional[str]:
        """Detect archive type using file signature and extension"""
        if not self.filepath or not os.path.isfile(self.filepath):
            return None

        # Try signature detection first
        try:
            with open(self.filepath, 'rb') as f:
                file_start = f.read(16)  # Read enough bytes for signatures

                for signature, archive_type in self.FILE_SIGNATURES.items():
                    if file_start.startswith(signature):
                        return archive_type
        except (IOError, PermissionError) as e:
            # Handle file access errors
            print(f"Error reading file: {e}")
            return None

        # Fall back to extension
        ext = os.path.splitext(self.filepath)[1].lower().replace('.', '')
        return ext if ext in self.SUPPORTED_TYPES else None

    def validate(self):
        """Validate if file exists and is password protected"""
        if not self.filepath or not os.path.isfile(self.filepath):
            return False, "No file selected or file does not exist."

        if self.archive_type not in self.SUPPORTED_TYPES:
            return False, f"Unsupported archive type: {self.archive_type}"

        try:
            validator_method = getattr(self, f"_validate_{self.archive_type}")
            return validator_method()
        except AttributeError:
            return False, f"Validation for {self.archive_type} not implemented."
        except Exception as e:
            return False, f"Unexpected error during validation: {str(e)}"

    def _validate_rar(self):
        try:
            with rarfile.RarFile(self.filepath) as rf:
                if rf.needs_password():
                    return True, "This RAR archive is password protected."
                else:
                    return False, "This RAR archive is NOT password protected."
        except rarfile.BadRarFile:
            return False, "Not a valid RAR file."
        except Exception as e:
            return False, f"Error reading RAR file: {e}"

    def _validate_zip(self):
        try:
            with zipfile.ZipFile(self.filepath, 'r') as zf:
                for zinfo in zf.infolist():
                    if zinfo.flag_bits & 0x1:
                        return True, "This ZIP archive is password protected."
                return False, "This ZIP archive is NOT password protected."
        except zipfile.BadZipFile:
            return False, "Not a valid ZIP file."
        except Exception as e:
            return False, f"Error reading ZIP file: {e}"

    def _validate_7z(self):
        try:
            with py7zr.SevenZipFile(self.filepath, mode='r') as archive:
                if archive.password_protected:
                    return True, "This 7Z archive is password protected."
                else:
                    return False, "This 7Z archive is NOT password protected."
        except py7zr.Bad7zFile:
            return False, "Not a valid 7Z file."
        except Exception as e:
            return False, f"Error reading 7Z file: {e}"
