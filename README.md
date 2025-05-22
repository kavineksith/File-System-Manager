# File System Manager

![Python Version](https://img.shields.io/badge/python-3.10%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)

A robust, feature-rich file system management tool designed for both programmatic use and command-line interaction. This tool provides comprehensive file operations with detailed logging, error handling, and analytics capabilities.

## Features

- **File Operations**: Copy, move, rename, and delete files with validation
- **Directory Management**: Create, delete, list, and clean directories
- **Bulk Processing**: Change extensions for multiple files at once
- **Detailed Analytics**: Track operation statistics and file system metrics
- **Error Handling**: Comprehensive exception handling with detailed logging
- **CLI Interface**: User-friendly command-line interface for interactive use
- **Logging**: Configurable logging for all operations

## Installation

1. Ensure you have Python 3.10 or later installed
2. Clone this repository or download the script
3. (Optional) Create a virtual environment

## Usage

### As a Command Line Tool

Run the script directly:

```bash
python3 filesystem_manager.py
```

Available commands in the interactive CLI:
- `list`: List directory contents
- `copy`: Copy a file
- `move`: Move a file
- `delete`: Delete a file
- `rename`: Rename a file
- `mkdir`: Create a directory
- `rmdir`: Delete a directory
- `ext`: Change a file's extension
- `bulk_ext`: Bulk change file extensions
- `create`: Create an empty file
- `size`: Get directory size
- `clean`: Clean directory contents
- `help`: Show help information
- `exit`: Exit the program

### As a Python Module

Import and use the `FileSystemManager` class in your Python code:

```python
from filesystem_manager import FileSystemManager

fs = FileSystemManager()

# Example: List directory contents
contents = fs.list_directory('/path/to/directory', recursive=True)

# Example: Copy a file
fs.copy_file('/path/to/source', '/path/to/destination', overwrite=True)
```

## Examples

### Bulk Change File Extensions

```python
stats = fs.bulk_change_extensions(
    directory='/path/to/files',
    current_extensions=['.txt', '.doc'],
    new_extension='.md',
    recursive=True
)
```

### Get Directory Size

```python
size_bytes = fs.get_directory_size('/path/to/directory', recursive=True)
```

### Clean Directory

```python
fs.clean_directory('/path/to/directory', confirm=False)  # Use with caution!
```

## Logging

The tool automatically logs all operations to `filesystem_manager.log` with timestamps and operation details. You can configure logging by modifying the `LogManager` class.

## Error Handling

The tool raises specific exceptions for different error conditions:
- `FileSystemError`: Base exception for all file system operations
- `PathNotFoundError`: When a path doesn't exist
- `PermissionDeniedError`: When permission is denied
- `NotEmptyDirectoryError`: When trying to remove a non-empty directory
- `UnsupportedOperationError`: For unsupported operations

## License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## ⚠️ Disclaimer

This software is provided "as is" without warranty of any kind, express or implied. The authors are not responsible for any legal implications of generated license files or repository management actions.  **This is a personal project intended for educational purposes. The developer makes no guarantees about the reliability or security of this software. Use at your own risk.**

## Disclaimer (Sumarized)

⚠️ **Use with caution!** This tool performs direct filesystem operations. Always:
- Backup important data before performing bulk operations
- Double-check paths before deleting or overwriting files
- Use the confirmation prompts when available

The developers are not responsible for any data loss or damage caused by this tool.
