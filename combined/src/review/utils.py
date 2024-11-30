from asyncio.log import logger
from pathlib import Path
from collections import defaultdict
from src.review.styleguide.py_styleguide import py_styleguide_prompts
from src.review.styleguide.csharp_styleguide import csharp_styleguide_prompts
from src.review.styleguide.ts_styleguide import ts_styleguide_prompts
import re


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


def parse_review_tags(review_dir: Path) -> list[dict]:
    """Parse review tags and their context from reviewed files."""
    diffs = []

    for file_path in review_dir.rglob("*"):
        if not file_path.is_file():
            continue

        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Get original file path from review output
            original_file = str(file_path).replace(str(review_dir), "").lstrip("/")

            # Find all review blocks
            review_blocks = re.finditer(
                r"//<REVIEW>(.*?)</REVIEW>\s*\n(.*?)(?=\n|$)", content, re.DOTALL
            )

            for match in review_blocks:
                review_comment = match.group(1).strip()
                affected_code = match.group(2).strip()

                # Try to determine the language for syntax highlighting
                try:
                    language = language_from_file_extension(file_path.suffix[1:])
                except KeyError:
                    language = "text"

                diffs.append(
                    {
                        "file": original_file,
                        "line_number": content[: match.start()].count("\n") + 1,
                        "review": review_comment,
                        "original": affected_code,
                        "replacement": "# TODO: Implement suggested changes",
                        "language": language,
                    }
                )

        except Exception as e:
            logger.error(f"Error parsing review file {file_path}: {e}")

    return diffs
