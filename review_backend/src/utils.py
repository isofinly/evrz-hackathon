from pathlib import Path
from collections import defaultdict


def get_project_language(project_path: Path) -> str:
    language_count: dict[str, int] = defaultdict(int)
    for file in project_path.iterdir():
        if file.is_file() and file.name.endswith((".py", ".cs", ".ts", "tsx")):
            language_count[file.name.split(".")[-1]] += 1
    return max(language_count, key=language_count.get)


def language_from_file_extension(file_extension: str) -> str:
    return {
        "py": "python",
        "cs": "csharp",
        "ts": "typescript",
        "tsx": "typescript",
    }[file_extension]
    