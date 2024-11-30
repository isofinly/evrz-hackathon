from pathlib import Path
from collections import defaultdict
from styleguide.py_styleguide import py_styleguide_prompts
from styleguide.csharp_styleguide import csharp_styleguide_prompts
from styleguide.ts_styleguide import ts_styleguide_prompts


def get_file_extension(file_path: Path) -> str:
    return file_path.suffix[1:]


def language_from_file_extension(file_extension: str) -> str:
    return {
        "py": "python",
        "cs": "csharp",
        "ts": "typescript",
        "tsx": "typescript",
        "css": "css",
        "scss": "scss",
    }[file_extension]


def file_extensions_from_language(language: str) -> list[str]:
    return {
        "python": ["py"],
        "csharp": ["cs"],
        "typescript": ["ts", "tsx"],
        "css": ["css"],
        "scss": ["scss"],
    }[language]


def code_from_chunk(chunk: dict) -> str:
    return chunk["declaration"].replace(f"<BODY {chunk['identifier']}>", chunk["body"])


def merge_json_responses(json_responses: list[dict]) -> str:
    result = {}
    for json_response in json_responses:
        for key, value in json_response.items():
            if key in result:
                result[key] += value
            else:
                result[key] = value
    return result


def add_line_numbers(code: str, start_line: int) -> str:
    return "\n".join(
        [f"{start_line + i + 1} {line}" for i, line in enumerate(code.split("\n"))]
    )


def get_styleguide_by_language(language: str) -> dict[str, str]:
    styleguide_prompts = {
        "python": py_styleguide_prompts,
        "csharp": csharp_styleguide_prompts,
        "typescript": ts_styleguide_prompts,
    }
    return styleguide_prompts.get(language, {})
