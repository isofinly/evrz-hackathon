from asyncio.log import logger
import os
import re
import patoolib
import logging
import py7zr
import shutil
import tempfile
from src.review.review import FileReviewer
from pathlib import Path


def extract_archive(file_path: str, extract_dir: str) -> bool:
    """Extract archive files to the specified directory."""
    try:
        # Create extraction directory if it doesn't exist
        os.makedirs(extract_dir, exist_ok=True)
        logger.info(f"Extracting {file_path} to {extract_dir}")

        file_path_lower = file_path.lower()

        if file_path_lower.endswith(".7z"):
            # Use py7zr for .7z files
            with py7zr.SevenZipFile(file_path, mode="r") as z:
                z.extractall(path=extract_dir)
        elif file_path_lower.endswith(".zip"):
            import zipfile

            with zipfile.ZipFile(file_path, "r") as z:
                z.extractall(extract_dir)
        elif file_path_lower.endswith(".rar"):
            import rarfile

            with rarfile.RarFile(file_path, "r") as z:
                z.extractall(extract_dir)

        # Verify extraction was successful
        extracted_contents = list(Path(extract_dir).rglob("*"))
        if not extracted_contents:
            logger.error(f"No files were extracted to {extract_dir}")
            return False

        logger.info(
            f"Successfully extracted {len(extracted_contents)} items to {extract_dir}"
        )
        return True

    except Exception as e:
        logger.error(f"Failed to extract archive: {str(e)}", exc_info=True)
        return False


def get_project_structure(directory: str) -> str:
    """
    Generates a tree-like structure of the project directory.
    """
    structure = []
    for root, dirs, files in os.walk(directory):
        level = root.replace(directory, "").count(os.sep)
        indent = "│   " * level + "├── " if level > 0 else ""
        structure.append(f"{indent}{os.path.basename(root)}/")
        sub_indent = "│   " * (level + 1) + "├── "
        for file in files:
            structure.append(f"{sub_indent}{file}")
    return "\n".join(structure)


def find_block_end(lines: list[str], start_idx: int) -> int:
    """
    Find the end of a code block starting from a given line.
    Returns the index of the last line in the block.
    """
    # Stack to keep track of opening and closing brackets
    stack = []
    # Opening and closing bracket pairs
    brackets = {
        "{": "}",
        "(": ")",
        "[": "]",
        "function": "}",  # For JavaScript/TypeScript functions
        "class": "}",  # For class definitions
        "if": "}",  # For if statements
        "for": "}",  # For loops
        "while": "}",  # For while loops
    }

    # Check if the line contains any opening brackets or keywords
    first_line = lines[start_idx].strip()

    # Add initial brackets/keywords to stack
    for bracket in brackets:
        if bracket in first_line:
            stack.append(brackets[bracket])

    # If no brackets found, return just this line
    if not stack:
        return start_idx

    # Process subsequent lines
    current_idx = start_idx
    while current_idx < len(lines) - 1 and stack:
        current_idx += 1
        line = lines[current_idx].strip()

        # Add new opening brackets to stack
        for bracket in brackets:
            if bracket in line:
                stack.append(brackets[bracket])

        # Remove closing brackets from stack
        for closing in brackets.values():
            if closing in line:
                if stack and stack[-1] == closing:
                    stack.pop()

        # Break if we've found all closing brackets
        if not stack:
            break

    return current_idx


def find_code_block(lines: list[str], start_idx: int) -> tuple[int, str]:
    """
    Find a complete code block starting from a given line.
    Returns tuple of (end_line_index, block_content).
    """
    block_lines = []
    current_idx = start_idx

    # Skip empty lines at the start
    while current_idx < len(lines) and not lines[current_idx].strip():
        current_idx += 1

    if current_idx >= len(lines):
        return start_idx, ""

    # Get initial line and its indentation
    first_line = lines[current_idx]
    base_indent = len(first_line) - len(first_line.lstrip())

    # Check for special cases in the first line
    first_line_stripped = first_line.strip()
    is_type_def = first_line_stripped.startswith(
        "type "
    ) or first_line_stripped.startswith("interface ")
    is_export = first_line_stripped.startswith("export ")

    while current_idx < len(lines):
        current_line = lines[current_idx]
        current_stripped = current_line.strip()

        # Skip empty lines at the start
        if not block_lines and not current_stripped:
            current_idx += 1
            continue

        # Add line to block
        if current_stripped:
            current_indent = len(current_line) - len(current_line.lstrip())

            # Stop conditions:
            # 1. Found another review tag
            if "<REVIEW>" in current_line:
                break

            # 2. Found end of type definition
            if is_type_def and current_stripped.endswith(";"):
                block_lines.append(current_line)
                break

            # 3. Found end of export statement
            if is_export and current_stripped.endswith(";"):
                block_lines.append(current_line)
                break

            # 4. Found closing brace at base indentation
            if current_stripped == "}" and current_indent <= base_indent:
                block_lines.append(current_line)
                break

            # 5. Next line has same or less indentation and current block is complete
            if block_lines and current_indent <= base_indent:
                # Check if current line starts a new block/statement
                if any(
                    current_stripped.startswith(keyword)
                    for keyword in [
                        "type",
                        "interface",
                        "export",
                        "function",
                        "class",
                        "const",
                        "let",
                        "var",
                    ]
                ):
                    break

        block_lines.append(current_line)
        current_idx += 1

    # Handle case where we reached end of file
    if current_idx == len(lines) and block_lines:
        current_idx -= 1

    return current_idx, "".join(block_lines)


def parse_review_tags(directory: str) -> list:
    """
    Parses files for <REVIEW>content</REVIEW> tags and returns the reviews with code context.
    """
    reviews = []
    review_pattern = re.compile(
        r"(?:\/\/|\/\*|\#|\{\/\*|\{\#)?\s*<REVIEW>(.*?)<\/REVIEW>"
    )

    def process_file(file_path: Path, base_dir: Path) -> None:
        try:
            rel_path = file_path.relative_to(base_dir)
            with open(file_path, "r", encoding="utf-8") as f:
                lines = f.readlines()

            i = 0
            while i < len(lines):
                line = lines[i]
                match = review_pattern.search(line)
                if match:
                    review_content = match.group(1).strip()

                    # Look ahead for the code block
                    code_lines = []
                    next_idx = i + 1
                    brace_count = 0
                    in_type_def = False

                    while next_idx < len(lines):
                        next_line = lines[next_idx].rstrip()

                        # Start of type definition
                        if "type" in next_line or "interface" in next_line:
                            in_type_def = True

                        if in_type_def:
                            code_lines.append(next_line)
                            brace_count += next_line.count("{") - next_line.count("}")
                            if brace_count == 0 and len(code_lines) > 0:
                                # End of type definition
                                break
                        elif not next_line.startswith(("//<REVIEW>", "// <REVIEW>")):
                            # Regular code line
                            if next_line.strip():
                                code_lines.append(next_line)
                                break

                        next_idx += 1

                    code_block = "\n".join(code_lines).rstrip() if code_lines else ""

                    # Extract suggested code if present
                    suggested_code = None
                    if "`" in review_content:
                        code_match = re.search(r"`(.*?)`", review_content)
                        if code_match:
                            suggested_code = code_match.group(1)

                    reviews.append({
                        "file": str(rel_path),
                        "line_number": i + 2,  # +2 because we want to show the actual code line number
                        "review": review_content,
                        "code": code_block,
                        "suggested_code": suggested_code
                    })
                i += 1

        except Exception as e:
            logger.warning(f"Could not process file {file_path}: {e}")

    # Process directory or single file
    directory_path = Path(directory)
    if directory_path.is_file():
        process_file(directory_path, directory_path.parent)
    else:
        for file_path in directory_path.rglob("*"):
            if file_path.is_file():
                try:
                    content = file_path.read_text(encoding="utf-8")
                    if "<REVIEW>" in content:
                        process_file(file_path, directory_path)
                except Exception as e:
                    logger.warning(f"Could not read file {file_path}: {e}")

    return reviews
