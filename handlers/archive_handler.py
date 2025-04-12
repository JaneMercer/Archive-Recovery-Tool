import os
import zipfile
import rarfile
import py7zr  # needs `pip install py7zr`

class ArchiveHandler:
    SUPPORTED_TYPES = ['rar', 'zip', '7z']

    def __init__(self, filepath=None, archive_type='auto'):
        self.filepath = filepath
        self.archive_type = archive_type

        if self.archive_type == 'auto':
            self.archive_type = self.detect_type()

    def detect_type(self):
        """Auto-detect based on file extension"""
        ext = os.path.splitext(self.filepath)[1].lower().replace('.', '')
        return ext if ext in self.SUPPORTED_TYPES else None

    def validate(self):
        """Dispatch to the correct validator"""
        if not self.filepath or not os.path.isfile(self.filepath):
            return False, "No file selected or file does not exist."

        if self.archive_type == 'rar':
            return self._validate_rar()
        elif self.archive_type == 'zip':
            return self._validate_zip()
        elif self.archive_type == '7z':
            return self._validate_7z()
        else:
            return False, "Unsupported or unknown archive type."

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
        except Exception as e:
            return False, f"Error reading 7Z file: {e}"
