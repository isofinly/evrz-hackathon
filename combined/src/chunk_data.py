import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.resolve()))
print(sys.path[-1])

from src.review.parsers.parser import parse_file
from src.review.parsers.language import LANGUAGE
from argparse import ArgumentParser

from pathlib import Path

parser = ArgumentParser()
parser.add_argument(
    "-i",
    "--input",
    type=str,
    help="Path to file or directory with files",
    required=True,
)
parser.add_argument(
    "-o", "--output", type=str, help="Path to output file", required=True
)


if __name__ == "__main__":
    args = parser.parse_args()

    path = Path(args.input).resolve()
    output_path = Path(args.output).resolve()

    for file_path in path.rglob("*"):
        if file_path.suffix[1:] not in LANGUAGE:
            continue
        file_path = file_path.relative_to(path)

        base_chunk, declarations = parse_file(path / file_path)

        out_file_path = output_path / file_path

        out_base_path = out_file_path / "__base__.json"
        out_base_path.parent.mkdir(parents=True, exist_ok=True)
        base_chunk.to_json(out_base_path)

        for identifier, declaration in declarations.items():
            out_identifier_path = out_file_path / f"{identifier}.json"
            out_identifier_path.parent.mkdir(parents=True, exist_ok=True)
            declaration.to_json(out_identifier_path)
