from src.parsers.language import LANGUAGE
from src.parsers.make_chunks import chunk_code

from pathlib import Path

from typing import Tuple, Dict

def parse_file(file_path: str | Path) ->  Tuple[str, Dict]:
    """
        parse chunks of code from file

        return base chunk and declarations
    """

    if type(file_path) == str:
        file_path = Path(file_path)

    exension = file_path.suffix[1:]

    if exension not in LANGUAGE:
        return "", {}
    
    with open(file_path, "r") as f:
        code = f.read()

    base_chunk, declarations = chunk_code(code, exension)

    return base_chunk, declarations