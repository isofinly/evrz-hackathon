from pathlib import Path


def parse_project_structure(root_path: str | Path) -> str:
    """
    Parse project directory structure and return formatted string representation.

    Args:
        root_path: Path to project root directory

    Returns:
        Formatted string showing directory structure with dashes as indentation
    """
    root = Path(root_path)
    result = [root.name]
    ignored = ["__pycache__"]  # TODO: add

    def process_directory(directory: Path, depth: int = 0):
        items = sorted(directory.iterdir(), key=lambda x: (not x.is_dir(), x.name))

        for item in items:
            if item.name.startswith(".") or item.name in ignored:
                continue

            prefix = "-" * (depth + 1)
            result.append(f"{prefix}{item.name}")

            if item.is_dir():
                process_directory(item, depth + 1)

    process_directory(root)
    return "\n".join(result)
