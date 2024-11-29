from asyncio.log import logger
import os
import re
import patoolib
import logging
import py7zr
import shutil
import tempfile


def extract_archive(archive_path: str, extract_dir: str) -> bool:
    """
    Extract archive using appropriate extractor based on file type.
    Returns True if extraction was successful.
    """
    try:
        file_lower = archive_path.lower()

        # Handle 7z files separately with py7zr
        if file_lower.endswith('.7z'):
            with py7zr.SevenZipFile(archive_path, mode='r') as z:
                z.extractall(extract_dir)
            return True

        # Handle other archive types with patool
        elif any(file_lower.endswith(ext) for ext in ['.zip', '.rar']):
            patoolib.extract_archive(archive_path, outdir=extract_dir)
            return True

        return False

    except Exception as e:
        logger.error(f"Failed to extract archive {archive_path}: {e}", exc_info=True)
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
        '{': '}',
        '(': ')',
        '[': ']',
        'function': '}',  # For JavaScript/TypeScript functions
        'class': '}',     # For class definitions
        'if': '}',        # For if statements
        'for': '}',       # For loops
        'while': '}'      # For while loops
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
    is_type_def = first_line_stripped.startswith('type ') or first_line_stripped.startswith('interface ')
    is_export = first_line_stripped.startswith('export ')

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
            if '<REVIEW>' in current_line:
                break

            # 2. Found end of type definition
            if is_type_def and current_stripped.endswith(';'):
                block_lines.append(current_line)
                break

            # 3. Found end of export statement
            if is_export and current_stripped.endswith(';'):
                block_lines.append(current_line)
                break

            # 4. Found closing brace at base indentation
            if (current_stripped == '}' and current_indent <= base_indent):
                block_lines.append(current_line)
                break

            # 5. Next line has same or less indentation and current block is complete
            if block_lines and current_indent <= base_indent:
                # Check if current line starts a new block/statement
                if any(current_stripped.startswith(keyword) for keyword in [
                    'type', 'interface', 'export', 'function', 'class', 'const', 'let', 'var'
                ]):
                    break

        block_lines.append(current_line)
        current_idx += 1

    # Handle case where we reached end of file
    if current_idx == len(lines) and block_lines:
        current_idx -= 1

    return current_idx, ''.join(block_lines)


def parse_review_tags(directory: str) -> list:
    """
    Parses files for <REVIEW>content</REVIEW> tags and returns the diffs.
    """
    diffs = []
    review_pattern = re.compile(
        r'(?:\/\/|\/\*|\#|\{\/\*|\{\#)?\s*<REVIEW>(.*?)<\/REVIEW>'
    )

    # Define supported file extensions
    text_extensions = {
        # Web development
        '.js', '.jsx', '.ts', '.tsx', '.vue', '.svelte',
        '.html', '.htm', '.css', '.scss', '.sass', '.less',

        # Backend languages
        '.py', '.java', '.php', '.rb', '.go', '.rs',
        '.cpp', '.c', '.h', '.cs', '.kt', '.scala',

        # Configuration and data
        '.json', '.yml', '.yaml', '.xml', '.toml',
        '.ini', '.conf', '.config', '.env',

        # Documentation and text
        '.md', '.markdown', '.txt', '.rst',

        # Shell and scripts
        '.sh', '.bash', '.zsh', '.fish',

        # Other development files
        '.gradle', '.maven', '.gitignore', '.dockerignore',
        'Dockerfile', 'Makefile', '.editorconfig'
    }

    def process_file(file_path: str, base_dir: str) -> None:
        """Process a single file for review tags."""
        try:
            rel_path = os.path.relpath(file_path, base_dir)
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()

            i = 0
            while i < len(lines):
                line = lines[i]
                match = review_pattern.search(line)

                if match:
                    review_content = match.group(1).strip()

                    # Find the block starting from the next line
                    if i + 1 < len(lines):
                        block_end, block_content = find_code_block(lines, i + 1)

                        if block_content.strip():  # Only add if block is not empty
                            # Remove trailing semicolon if it exists
                            block_content = block_content.rstrip()
                            if block_content.endswith(';'):
                                block_content = block_content[:-1]

                            diffs.append({
                                'file': rel_path,
                                'line_number': i + 2,
                                'review': review_content,
                                'original': block_content,
                                'replacement': "<<<REPLACEMENT BLOCK NEEDED>>>"
                            })

                        i = block_end  # Skip to end of block

                i += 1

        except Exception as e:
            logger.warning(f"Could not process file {file_path}: {e}")

    # Check if directory is actually a file
    if os.path.isfile(directory):
        process_file(directory, os.path.dirname(directory))
        return diffs

    # Walk through directory
    for root, _, files in os.walk(directory):
        for file in files:
            file_lower = file.lower()
            # Check if file extension is supported or exact filename matches
            if any(file_lower.endswith(ext) for ext in text_extensions) or file_lower in text_extensions:
                file_path = os.path.join(root, file)
                process_file(file_path, directory)

    return diffs


def generate_diff(file_path: str, line: str, line_number: int, review_comment: str) -> str:
    """
    Generates a diff string with the review comment and the line to be reviewed.
    """
    return (
        f"File: {file_path} (line {line_number})\n"
        f"Review: {review_comment}\n"
        f"- {line}\n"
        f"+ <<<REPLACEMENT NEEDED>>>"
    )
