#!/usr/bin/env python3
"""
Industrial-Grade File System Manager
-----------------------------------
A comprehensive file system management tool that provides:
- File operations (copy, move, rename, delete)
- Directory operations (list, create, delete)
- Bulk operations (extension change, recursive operations)
- Detailed file system analytics
- Robust error handling and logging
"""

import os
import sys
import shutil
import json
import csv
from pathlib import Path
from datetime import datetime
from typing import List, Dict, Tuple, Optional, Union
import logging

# ======================
# LOGGING CONFIGURATION
# ======================
class LogManager:
    """Centralized logging management for the application."""
    
    _configured = False
    
    @classmethod
    def configure_logging(cls, log_file: str = 'filesystem_manager.log', 
                         level: int = logging.DEBUG) -> None:
        """Configure application-wide logging."""
        if cls._configured:
            return
            
        # Create root logger
        logger = logging.getLogger()
        logger.setLevel(level)
        
        # File handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(logging.INFO)
        
        # Formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        cls._configured = True
        logging.info("Logging configured successfully")

# Initialize logging
LogManager.configure_logging()

# ======================
# CUSTOM EXCEPTIONS
# ======================
class FileSystemError(Exception):
    """Base exception for file system operations."""
    def __init__(self, message, error_code = None):
        super().__init__(message, error_code)

class UnsupportedOperationError(FileSystemError):
    """Raised when an unsupported operation is attempted."""
    def __init__(self, message, error_code = None):
        super().__init__(message, error_code)

class PathNotFoundError(FileSystemError):
    """Raised when a path doesn't exist."""
    def __init__(self, message, error_code = None):
        super().__init__(message, error_code)

class PermissionDeniedError(FileSystemError):
    """Raised when permission is denied."""
    def __init__(self, message, error_code = None):
        super().__init__(message, error_code)

class NotEmptyDirectoryError(FileSystemError):
    """Raised when trying to remove a non-empty directory."""
    def __init__(self, message, error_code = None):
        super().__init__(message, error_code)

# ======================
# CORE FUNCTIONALITY
# ======================
class FileSystemManager:
    """Core class for file system operations."""
    
    def __init__(self):
        self.operation_stats = {
            'files_processed': 0,
            'directories_processed': 0,
            'successful_operations': 0,
            'failed_operations': 0
        }
    
    def reset_stats(self) -> None:
        """Reset operation statistics."""
        self.operation_stats = {
            'files_processed': 0,
            'directories_processed': 0,
            'successful_operations': 0,
            'failed_operations': 0
        }
    
    def validate_path(self, path: Union[str, Path], should_exist: bool = True) -> Path:
        """
        Validate and normalize a path.
        
        Args:
            path: The path to validate
            should_exist: Whether the path should exist
            
        Returns:
            Normalized Path object
            
        Raises:
            PathNotFoundError: If should_exist is True and path doesn't exist
        """
        path = Path(path).resolve()
        if should_exist and not path.exists():
            raise PathNotFoundError(f"Path '{path}' does not exist")
        return path
    
    def get_file_info(self, file_path: Path) -> Dict:
        """Get detailed information about a file."""
        try:
            stat = file_path.stat()
            return {
                'path': str(file_path),
                'name': file_path.name,
                'size': stat.st_size,
                'created': datetime.fromtimestamp(stat.st_ctime).isoformat(),
                'modified': datetime.fromtimestamp(stat.st_mtime).isoformat(),
                'accessed': datetime.fromtimestamp(stat.st_atime).isoformat(),
                'is_dir': file_path.is_dir(),
                'is_file': file_path.is_file()
            }
        except Exception as e:
            logging.error(f"Error getting info for {file_path}: {e}")
            raise FileSystemError(f"Could not get info for {file_path}") from e
    
    def list_directory(self, directory: Union[str, Path], recursive: bool = False) -> List[Dict]:
        """
        List contents of a directory.
        
        Args:
            directory: Path to directory
            recursive: Whether to list recursively
            
        Returns:
            List of file/directory information dictionaries
        """
        directory = self.validate_path(directory)
        results = []
        
        try:
            for item in directory.iterdir():
                try:
                    if recursive and item.is_dir():
                        results.extend(self.list_directory(item, recursive=True))
                    results.append(self.get_file_info(item))
                    self.operation_stats['files_processed'] += 1
                except Exception as e:
                    logging.warning(f"Could not process {item}: {e}")
                    self.operation_stats['failed_operations'] += 1
            
            self.operation_stats['directories_processed'] += 1
            self.operation_stats['successful_operations'] += 1
            return results
        except Exception as e:
            logging.error(f"Error listing directory {directory}: {e}")
            self.operation_stats['failed_operations'] += 1
            raise FileSystemError(f"Could not list directory {directory}") from e
    
    def copy_file(self, source: Union[str, Path], destination: Union[str, Path], 
                  overwrite: bool = False) -> None:
        """
        Copy a file from source to destination.
        
        Args:
            source: Source file path
            destination: Destination path
            overwrite: Whether to overwrite if destination exists
            
        Raises:
            FileSystemError: If operation fails
        """
        source = self.validate_path(source)
        destination = self.validate_path(destination.parent if destination.is_file() else destination, False)
        
        try:
            if destination.is_dir():
                destination = destination / source.name
            
            if destination.exists() and not overwrite:
                raise FileSystemError(f"Destination file {destination} already exists")
            
            shutil.copy2(source, destination)
            self.operation_stats['files_processed'] += 1
            self.operation_stats['successful_operations'] += 1
            logging.info(f"Copied {source} to {destination}")
        except Exception as e:
            logging.error(f"Error copying {source} to {destination}: {e}")
            self.operation_stats['failed_operations'] += 1
            raise FileSystemError(f"Could not copy {source} to {destination}") from e
    
    def move_file(self, source: Union[str, Path], destination: Union[str, Path], 
                  overwrite: bool = False) -> None:
        """
        Move a file from source to destination.
        
        Args:
            source: Source file path
            destination: Destination path
            overwrite: Whether to overwrite if destination exists
            
        Raises:
            FileSystemError: If operation fails
        """
        source = self.validate_path(source)
        destination = self.validate_path(destination.parent if destination.is_file() else destination, False)
        
        try:
            if destination.is_dir():
                destination = destination / source.name
            
            if destination.exists():
                if overwrite:
                    destination.unlink()
                else:
                    raise FileSystemError(f"Destination file {destination} already exists")
            
            shutil.move(source, destination)
            self.operation_stats['files_processed'] += 1
            self.operation_stats['successful_operations'] += 1
            logging.info(f"Moved {source} to {destination}")
        except Exception as e:
            logging.error(f"Error moving {source} to {destination}: {e}")
            self.operation_stats['failed_operations'] += 1
            raise FileSystemError(f"Could not move {source} to {destination}") from e
    
    def delete_file(self, file_path: Union[str, Path]) -> None:
        """
        Delete a file.
        
        Args:
            file_path: Path to file to delete
            
        Raises:
            FileSystemError: If operation fails
        """
        file_path = self.validate_path(file_path)
        
        try:
            if file_path.is_dir():
                raise FileSystemError(f"Path {file_path} is a directory")
            
            file_path.unlink()
            self.operation_stats['files_processed'] += 1
            self.operation_stats['successful_operations'] += 1
            logging.info(f"Deleted file {file_path}")
        except Exception as e:
            logging.error(f"Error deleting file {file_path}: {e}")
            self.operation_stats['failed_operations'] += 1
            raise FileSystemError(f"Could not delete file {file_path}") from e
    
    def create_directory(self, dir_path: Union[str, Path], parents: bool = True, 
                        exist_ok: bool = True) -> None:
        """
        Create a directory.
        
        Args:
            dir_path: Path to directory to create
            parents: Whether to create parent directories
            exist_ok: Whether to ignore if directory already exists
            
        Raises:
            FileSystemError: If operation fails
        """
        dir_path = self.validate_path(dir_path, should_exist=False)
        
        try:
            dir_path.mkdir(parents=parents, exist_ok=exist_ok)
            self.operation_stats['directories_processed'] += 1
            self.operation_stats['successful_operations'] += 1
            logging.info(f"Created directory {dir_path}")
        except Exception as e:
            logging.error(f"Error creating directory {dir_path}: {e}")
            self.operation_stats['failed_operations'] += 1
            raise FileSystemError(f"Could not create directory {dir_path}") from e
    
    def delete_directory(self, dir_path: Union[str, Path], recursive: bool = False) -> None:
        """
        Delete a directory.
        
        Args:
            dir_path: Path to directory to delete
            recursive: Whether to delete contents recursively
            
        Raises:
            FileSystemError: If operation fails
        """
        dir_path = self.validate_path(dir_path)
        
        try:
            if not dir_path.is_dir():
                raise FileSystemError(f"Path {dir_path} is not a directory")
            
            if recursive:
                shutil.rmtree(dir_path)
            else:
                try:
                    dir_path.rmdir()
                except OSError as e:
                    raise NotEmptyDirectoryError(f"Directory {dir_path} is not empty") from e
            
            self.operation_stats['directories_processed'] += 1
            self.operation_stats['successful_operations'] += 1
            logging.info(f"Deleted directory {dir_path}")
        except Exception as e:
            logging.error(f"Error deleting directory {dir_path}: {e}")
            self.operation_stats['failed_operations'] += 1
            raise FileSystemError(f"Could not delete directory {dir_path}") from e
    
    def rename_file(self, source: Union[str, Path], new_name: str) -> None:
        """
        Rename a file.
        
        Args:
            source: Path to file to rename
            new_name: New name for the file
            
        Raises:
            FileSystemError: If operation fails
        """
        source = self.validate_path(source)
        new_path = source.parent / new_name
        
        try:
            source.rename(new_path)
            self.operation_stats['files_processed'] += 1
            self.operation_stats['successful_operations'] += 1
            logging.info(f"Renamed {source} to {new_path}")
        except Exception as e:
            logging.error(f"Error renaming {source} to {new_name}: {e}")
            self.operation_stats['failed_operations'] += 1
            raise FileSystemError(f"Could not rename {source} to {new_name}") from e
    
    def change_extension(self, file_path: Union[str, Path], new_extension: str) -> None:
        """
        Change a file's extension.
        
        Args:
            file_path: Path to file
            new_extension: New extension (with dot, e.g. '.txt')
            
        Raises:
            FileSystemError: If operation fails
        """
        file_path = self.validate_path(file_path)
        
        if not new_extension.startswith('.'):
            new_extension = f'.{new_extension}'
        
        try:
            new_path = file_path.with_suffix(new_extension)
            if new_path.exists():
                raise FileSystemError(f"Destination file {new_path} already exists")
            
            file_path.rename(new_path)
            self.operation_stats['files_processed'] += 1
            self.operation_stats['successful_operations'] += 1
            logging.info(f"Changed extension for {file_path} to {new_extension}")
        except Exception as e:
            logging.error(f"Error changing extension for {file_path}: {e}")
            self.operation_stats['failed_operations'] += 1
            raise FileSystemError(f"Could not change extension for {file_path}") from e
    
    def bulk_change_extensions(self, directory: Union[str, Path], 
                              current_extensions: List[str], 
                              new_extension: str, 
                              recursive: bool = False) -> None:
        """
        Change extensions for multiple files.
        
        Args:
            directory: Directory to process
            current_extensions: List of extensions to change (with dots, e.g. ['.txt', '.doc'])
            new_extension: New extension (with dot, e.g. '.md')
            recursive: Whether to process subdirectories
            
        Returns:
            Dictionary with operation statistics
        """
        directory = self.validate_path(directory)
        self.reset_stats()
        
        if not new_extension.startswith('.'):
            new_extension = f'.{new_extension}'
        
        current_extensions = [ext if ext.startswith('.') else f'.{ext}' 
                            for ext in current_extensions]
        
        try:
            for root, dirs, files in os.walk(directory) if recursive else [(directory, [], os.listdir(directory))]:
                root_path = Path(root)
                for file in files:
                    file_path = root_path / file
                    if file_path.suffix.lower() in current_extensions:
                        try:
                            new_path = file_path.with_suffix(new_extension)
                            if not new_path.exists():
                                file_path.rename(new_path)
                                self.operation_stats['successful_operations'] += 1
                                logging.info(f"Changed {file_path} to {new_path}")
                            else:
                                logging.warning(f"Skipped {file_path} - target exists")
                                self.operation_stats['failed_operations'] += 1
                            self.operation_stats['files_processed'] += 1
                        except Exception as e:
                            logging.error(f"Error processing {file_path}: {e}")
                            self.operation_stats['failed_operations'] += 1
            
            return self.operation_stats
        except Exception as e:
            logging.error(f"Error in bulk extension change: {e}")
            raise FileSystemError("Bulk extension change failed") from e
    
    def create_empty_file(self, file_path: Union[str, Path], 
                          content: Optional[Union[str, bytes]] = None) -> None:
        """
        Create an empty file.
        
        Args:
            file_path: Path to file to create
            content: Optional content to write to the file
            
        Raises:
            FileSystemError: If operation fails
        """
        file_path = self.validate_path(file_path, should_exist=False)
        
        try:
            if file_path.suffix == '.json':
                with open(file_path, 'w') as f:
                    json.dump({}, f)
            elif file_path.suffix == '.csv':
                with open(file_path, 'w', newline='') as f:
                    pass  # Just create empty file
            else:
                mode = 'wb' if isinstance(content, bytes) else 'w'
                with open(file_path, mode) as f:
                    if content:
                        f.write(content)
            
            self.operation_stats['files_processed'] += 1
            self.operation_stats['successful_operations'] += 1
            logging.info(f"Created file {file_path}")
        except Exception as e:
            logging.error(f"Error creating file {file_path}: {e}")
            self.operation_stats['failed_operations'] += 1
            raise FileSystemError(f"Could not create file {file_path}") from e
    
    def get_directory_size(self, directory: Union[str, Path], 
                          recursive: bool = True) -> int:
        """
        Calculate the size of a directory.
        
        Args:
            directory: Path to directory
            recursive: Whether to include subdirectories
            
        Returns:
            Size in bytes
            
        Raises:
            FileSystemError: If operation fails
        """
        directory = self.validate_path(directory)
        total_size = 0
        
        try:
            if recursive:
                for root, dirs, files in os.walk(directory):
                    for file in files:
                        try:
                            file_path = Path(root) / file
                            total_size += file_path.stat().st_size
                            self.operation_stats['files_processed'] += 1
                        except Exception as e:
                            logging.warning(f"Could not process {file_path}: {e}")
                            self.operation_stats['failed_operations'] += 1
            else:
                for item in directory.iterdir():
                    try:
                        if item.is_file():
                            total_size += item.stat().st_size
                            self.operation_stats['files_processed'] += 1
                    except Exception as e:
                        logging.warning(f"Could not process {item}: {e}")
                        self.operation_stats['failed_operations'] += 1
            
            self.operation_stats['directories_processed'] += 1
            self.operation_stats['successful_operations'] += 1
            return total_size
        except Exception as e:
            logging.error(f"Error calculating size for {directory}: {e}")
            self.operation_stats['failed_operations'] += 1
            raise FileSystemError(f"Could not calculate size for {directory}") from e
    
    def clean_directory(self, directory: Union[str, Path], 
                        confirm: bool = True) -> None:
        """
        Remove all contents from a directory.
        
        Args:
            directory: Path to directory to clean
            confirm: Whether to prompt for confirmation
            
        Raises:
            FileSystemError: If operation fails
        """
        directory = self.validate_path(directory)
        self.reset_stats()
        
        if confirm:
            response = input(f"Are you sure you want to delete all contents of {directory}? (y/n): ")
            if response.lower() not in ('y', 'yes'):
                logging.info("Operation cancelled by user")
                return
        
        try:
            for item in directory.iterdir():
                try:
                    if item.is_file():
                        item.unlink()
                        self.operation_stats['files_processed'] += 1
                    elif item.is_dir():
                        shutil.rmtree(item)
                        self.operation_stats['directories_processed'] += 1
                    self.operation_stats['successful_operations'] += 1
                    logging.info(f"Removed {item}")
                except Exception as e:
                    logging.error(f"Could not remove {item}: {e}")
                    self.operation_stats['failed_operations'] += 1
            
            logging.info(f"Cleaned directory {directory}")
        except Exception as e:
            logging.error(f"Error cleaning directory {directory}: {e}")
            raise FileSystemError(f"Could not clean directory {directory}") from e

# ======================
# USER INTERFACE
# ======================
class FileSystemCLI:
    """Command-line interface for file system operations."""
    
    def __init__(self):
        self.fs = FileSystemManager()
        self.operations = {
            'list': self._list_directory,
            'copy': self._copy_file,
            'move': self._move_file,
            'delete': self._delete_file,
            'rename': self._rename_file,
            'mkdir': self._create_directory,
            'rmdir': self._delete_directory,
            'ext': self._change_extension,
            'bulk_ext': self._bulk_change_extensions,
            'create': self._create_file,
            'size': self._get_size,
            'clean': self._clean_directory,
            'help': self._show_help,
            'exit': self._exit
        }
    
    def run(self) -> None:
        """Run the CLI interface."""
        print("\n" + "=" * 50)
        print("FILE SYSTEM MANAGER".center(50))
        print("=" * 50)
        print("\nType 'help' for available commands\n")
        
        while True:
            try:
                command = input("\n> ").strip().lower()
                if not command:
                    continue
                
                if command in self.operations:
                    self.operations[command]()
                else:
                    print("Invalid command. Type 'help' for available commands.")
            except KeyboardInterrupt:
                print("\nOperation cancelled by user.")
                sys.exit(0)
            except Exception as e:
                print(f"Error: {e}")
    
    def _list_directory(self) -> None:
        """List directory contents."""
        path = input("Directory path (leave blank for current): ").strip() or "."
        recursive = input("Recursive? (y/n): ").lower() in ('y', 'yes')
        
        try:
            contents = self.fs.list_directory(path, recursive=recursive)
            for item in contents:
                print(f"{'DIR' if item['is_dir'] else 'FILE'} - {item['path']} ({item['size']} bytes)")
        except FileSystemError as e:
            print(f"Error: {e}")
    
    def _copy_file(self) -> None:
        """Copy a file."""
        source = input("Source file: ").strip()
        destination = input("Destination: ").strip()
        overwrite = input("Overwrite if exists? (y/n): ").lower() in ('y', 'yes')
        
        try:
            self.fs.copy_file(source, destination, overwrite=overwrite)
            print("File copied successfully.")
        except FileSystemError as e:
            print(f"Error: {e}")
    
    def _move_file(self) -> None:
        """Move a file."""
        source = input("Source file: ").strip()
        destination = input("Destination: ").strip()
        overwrite = input("Overwrite if exists? (y/n): ").lower() in ('y', 'yes')
        
        try:
            self.fs.move_file(source, destination, overwrite=overwrite)
            print("File moved successfully.")
        except FileSystemError as e:
            print(f"Error: {e}")
    
    def _delete_file(self) -> None:
        """Delete a file."""
        path = input("File to delete: ").strip()
        confirm = input(f"Are you sure you want to delete {path}? (y/n): ").lower() in ('y', 'yes')
        
        if not confirm:
            print("Operation cancelled.")
            return
        
        try:
            self.fs.delete_file(path)
            print("File deleted successfully.")
        except FileSystemError as e:
            print(f"Error: {e}")
    
    def _rename_file(self) -> None:
        """Rename a file."""
        source = input("File to rename: ").strip()
        new_name = input("New name: ").strip()
        
        try:
            self.fs.rename_file(source, new_name)
            print("File renamed successfully.")
        except FileSystemError as e:
            print(f"Error: {e}")
    
    def _create_directory(self) -> None:
        """Create a directory."""
        path = input("Directory path: ").strip()
        parents = input("Create parent directories if needed? (y/n): ").lower() in ('y', 'yes')
        
        try:
            self.fs.create_directory(path, parents=parents)
            print("Directory created successfully.")
        except FileSystemError as e:
            print(f"Error: {e}")
    
    def _delete_directory(self) -> None:
        """Delete a directory."""
        path = input("Directory to delete: ").strip()
        recursive = input("Delete contents recursively? (y/n): ").lower() in ('y', 'yes')
        confirm = input(f"Are you sure you want to delete {path}? (y/n): ").lower() in ('y', 'yes')
        
        if not confirm:
            print("Operation cancelled.")
            return
        
        try:
            self.fs.delete_directory(path, recursive=recursive)
            print("Directory deleted successfully.")
        except FileSystemError as e:
            print(f"Error: {e}")
    
    def _change_extension(self) -> None:
        """Change a file's extension."""
        path = input("File path: ").strip()
        new_ext = input("New extension (with dot, e.g. '.txt'): ").strip()
        
        try:
            self.fs.change_extension(path, new_ext)
            print("Extension changed successfully.")
        except FileSystemError as e:
            print(f"Error: {e}")
    
    def _bulk_change_extensions(self) -> None:
        """Bulk change file extensions."""
        directory = input("Directory path: ").strip()
        current_exts = input("Current extensions (comma separated, e.g. '.txt,.doc'): ").strip().split(',')
        new_ext = input("New extension (with dot, e.g. '.md'): ").strip()
        recursive = input("Process subdirectories? (y/n): ").lower() in ('y', 'yes')
        
        try:
            stats = self.fs.bulk_change_extensions(
                directory=directory,
                current_extensions=current_exts,
                new_extension=new_ext,
                recursive=recursive
            )
            print("\nOperation completed:")
            print(f"Files processed: {stats['files_processed']}")
            print(f"Successful changes: {stats['successful_operations']}")
            print(f"Failed changes: {stats['failed_operations']}")
        except FileSystemError as e:
            print(f"Error: {e}")
    
    def _create_file(self) -> None:
        """Create an empty file."""
        path = input("File path: ").strip()
        content = input("Optional content (leave blank for empty file): ").strip() or None
        
        try:
            self.fs.create_empty_file(path, content=content)
            print("File created successfully.")
        except FileSystemError as e:
            print(f"Error: {e}")
    
    def _get_size(self) -> None:
        """Get directory size."""
        path = input("Directory path: ").strip()
        recursive = input("Include subdirectories? (y/n): ").lower() in ('y', 'yes')
        
        try:
            size_bytes = self.fs.get_directory_size(path, recursive=recursive)
            size_kb = size_bytes / 1024
            size_mb = size_kb / 1024
            size_gb = size_mb / 1024
            
            print(f"\nSize of {path}:")
            print(f"Bytes: {size_bytes:,}")
            print(f"KB: {size_kb:,.2f}")
            print(f"MB: {size_mb:,.2f}")
            print(f"GB: {size_gb:,.4f}")
        except FileSystemError as e:
            print(f"Error: {e}")
    
    def _clean_directory(self) -> None:
        """Clean directory contents."""
        path = input("Directory to clean: ").strip()
        confirm = input(f"Are you sure you want to delete ALL contents of {path}? (y/n): ").lower() in ('y', 'yes')
        
        if not confirm:
            print("Operation cancelled.")
            return
        
        try:
            self.fs.clean_directory(path, confirm=False)
            print("Directory cleaned successfully.")
        except FileSystemError as e:
            print(f"Error: {e}")
    
    def _show_help(self) -> None:
        """Show help information."""
        print("\nAvailable commands:")
        print("list - List directory contents")
        print("copy - Copy a file")
        print("move - Move a file")
        print("delete - Delete a file")
        print("rename - Rename a file")
        print("mkdir - Create a directory")
        print("rmdir - Delete a directory")
        print("ext - Change a file's extension")
        print("bulk_ext - Bulk change file extensions")
        print("create - Create an empty file")
        print("size - Get directory size")
        print("clean - Clean directory contents")
        print("help - Show this help")
        print("exit - Exit the program")
    
    def _exit(self) -> None:
        """Exit the program."""
        print("Goodbye!")
        sys.exit(0)

# ======================
# MAIN EXECUTION
# ======================
if __name__ == "__main__":
    try:
        cli = FileSystemCLI()
        cli.run()
    except Exception as e:
        logging.error(f"Application error: {e}")
        print(f"Fatal error: {e}")
        sys.exit(1)
