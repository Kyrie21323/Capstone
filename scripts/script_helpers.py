#!/usr/bin/env python3
"""
Shared Utilities for Scripts

This module provides common functionality used across all scripts,
including path setup, database access, and helper functions.
"""

import sys
import os
from pathlib import Path
from typing import Optional


def setup_python_path():
    """
    Add src directory to Python path for importing app modules.
    
    This ensures all scripts can import from the src directory
    regardless of where they're run from.
    
    Returns:
        Path: The project root directory
    """
    project_root = Path(__file__).parent.parent
    src_path = project_root / 'src'
    
    # Add to path if not already present
    if str(src_path) not in sys.path:
        sys.path.insert(0, str(src_path))
    
    return project_root


def get_project_root() -> Path:
    """
    Get the project root directory.
    
    Returns:
        Path: The project root directory
    """
    return Path(__file__).parent.parent


def get_database_path() -> Optional[Path]:
    """
    Find the database file in common locations.
    
    Returns:
        Path: Path to the database file, or None if not found
    """
    project_root = get_project_root()
    
    possible_paths = [
        project_root / "instance" / "nfc_networking.db",
        project_root / "src" / "instance" / "nfc_networking.db",
    ]
    
    for path in possible_paths:
        if path.exists():
            return path
    
    return None


def print_section(title: str, emoji: str = "📋"):
    """
    Print a formatted section header.
    
    Args:
        title: Section title
        emoji: Emoji to display before title
    """
    print(f"\n{emoji} {title}")
    print("=" * 60)


def print_success(message: str):
    """Print a success message."""
    print(f"✅ {message}")


def print_error(message: str):
    """Print an error message."""
    print(f"❌ {message}")


def print_warning(message: str):
    """Print a warning message."""
    print(f"⚠️  {message}")


def print_info(message: str):
    """Print an info message."""
    print(f"💡 {message}")


def confirm_action(prompt: str, default: bool = False) -> bool:
    """
    Ask user for confirmation.
    
    Args:
        prompt: Question to ask the user
        default: Default value if user just presses Enter
        
    Returns:
        bool: True if user confirmed, False otherwise
    """
    suffix = " [Y/n]: " if default else " [y/N]: "
    response = input(prompt + suffix).strip().lower()
    
    if not response:
        return default
    
    return response in ['y', 'yes']
