import re
import subprocess
import sys
from pathlib import Path

# File paths
INIT_FILE_PATH = "xmrig/__init__.py"  # Replace with the actual path to __init__.py
PYPROJECT_FILE_PATH = "pyproject.toml"

# Regex patterns for version
VERSION_PATTERN = r'(?<=\b__version__ = ")[^"]+'
TOML_VERSION_PATTERN = r'(?<=version = ")[^"]+'

def get_current_version(file_path, pattern):
    """Extract the current version from a file."""
    with open(file_path, "r") as file:
        content = file.read()
    match = re.search(pattern, content)
    if match:
        return match.group(0)
    raise ValueError(f"Version pattern not found in {file_path}")

def update_version_in_file(file_path, pattern, new_version):
    """Update the version in a file."""
    with open(file_path, "r") as file:
        content = file.read()
    updated_content = re.sub(pattern, new_version, content)
    with open(file_path, "w") as file:
        file.write(updated_content)

def main():
    if len(sys.argv) != 2:
        print("Usage: python update_version.py <version>")
        sys.exit(1)
    
    new_version = sys.argv[1]

    # Check if the provided version matches semantic versioning
    if not re.match(r"^\d+\.\d+\.\d+$", new_version):
        print("Error: Version must follow semantic versioning (e.g., 1.2.3).")
        sys.exit(1)

    try:
        # Get the current versions
        init_version = get_current_version(INIT_FILE_PATH, VERSION_PATTERN)
        toml_version = get_current_version(PYPROJECT_FILE_PATH, TOML_VERSION_PATTERN)

        print(f"Current __init__.py version: {init_version}")
        print(f"Current pyproject.toml version: {toml_version}")

        # Check if versions need updating
        if init_version != new_version:
            print(f"Updating __init__.py to version {new_version}...")
            update_version_in_file(INIT_FILE_PATH, VERSION_PATTERN, new_version)
        
        if toml_version != new_version:
            print(f"Updating pyproject.toml to version {new_version}...")
            update_version_in_file(PYPROJECT_FILE_PATH, TOML_VERSION_PATTERN, new_version)

        # Commit changes
        subprocess.run(["git", "add", INIT_FILE_PATH, PYPROJECT_FILE_PATH], check=True)
        subprocess.run(["git", "commit", "-m", f"Bump version to {new_version}"], check=True)

        # Create git tag
        subprocess.run(["git", "tag", new_version], check=True)
        print(f"Version updated and git tag {new_version} created.")

    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
