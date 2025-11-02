import os


def size_to_string(value: float) -> str:
    if value < 0:
        raise ValueError("Size must be non-negative")

    units = ["B", "KiB", "MiB", "GiB", "TiB"]
    index = 0
    while value >= 1024 and index < len(units) - 1:
        value /= 1024.0
        index += 1

    return f"{value:.2f} {units[index]}"


def is_valid_destination_file_path(destination_file_path: str) -> bool:
    if not destination_file_path or destination_file_path.isspace():
        return False

    # Get directory of destination
    dest_dir = os.path.dirname(destination_file_path) or "."

    # Check if directory exists
    if not os.path.exists(dest_dir):
        return False

    # Check if destination path is a directory
    if os.path.isdir(destination_file_path):
        return False

    # Check write permissions
    if not os.access(dest_dir, os.W_OK):
        return False

    return True

def is_valid_destination_directory_path(destination_directory_path: str) -> bool:
    if not destination_directory_path or destination_directory_path.isspace():
        return False

    # Check if directory exists
    if not os.path.exists(destination_directory_path):
        return False

    # Check if destination path is not a directory
    if not os.path.isdir(destination_directory_path):
        return False

    # Check write permissions
    if not os.access(destination_directory_path, os.W_OK):
        return False

    return True
