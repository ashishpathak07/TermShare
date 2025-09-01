"""
Utility functions for TermShare
"""

import os
import sys
import random
import string
from typing import List, Tuple

def generate_random_string(length: int = 8) -> str:
    """Generate a random string of specified length"""
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

def validate_port(port: int) -> bool:
    """Validate if a port number is within the valid range"""
    return 1 <= port <= 65535

def parse_ftp_listing(listing: List[str]) -> List[Tuple]:
    """
    Parse FTP directory listing into a structured format
    Returns list of tuples (name, size, type, modified)
    """
    parsed = []
    for line in listing:
        parts = line.split()
        if len(parts) >= 9:
            # Standard UNIX format
            perms, _, _, size, mon, day, time_year, *name_parts = parts
            name = " ".join(name_parts)
            file_type = "DIR" if perms.startswith("d") else "FILE"
            modified = f"{mon} {day} {time_year}"
            parsed.append((name, size, file_type, modified))
    return parsed

def get_file_size_str(size_bytes: int) -> str:
    """Convert file size in bytes to human readable string"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024.0:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024.0
    return f"{size_bytes:.2f} TB"

def is_linux() -> bool:
    """Check if the system is Linux"""
    return sys.platform.startswith('linux')

def ensure_directory_exists(path: str) -> bool:
    """Ensure that a directory exists, create if it doesn't"""
    try:
        os.makedirs(path, exist_ok=True)
        return True
    except OSError:
        return False