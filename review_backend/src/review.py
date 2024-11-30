import json
import re

from pathlib import Path
from utils import (
    get_file_extension,
    code_from_chunk,
    merge_json_responses,
    get_styleguide_by_language,
    language_from_file_extension,
)
from prompt import PromptGenerator
from parsers.parser import parse_file
from parsers.project_parser import parse_project_structure

# from api import get_response
from gemma_api import get_response


FILE_EXTENSIONS = ["py", "cs", "ts", "tsx", "css", "scss"]


class FileReviewer:
    def __init__(self, file_path: Path, result_path: Path) -> None:
        self.file_path = file_path
        self.result_path = result_path
        
        self.result_path.parent.mkdir(parents=True, exist_ok=True)
        self.result_path.touch(exist_ok=True)
        
        self.extension = file_path.name.split(".")[-1]
        self.comment_sign = "#" if self.extension == "py" else "//"
        self.styleguide_prompts = get_styleguide_by_language(
            language_from_file_extension(self.extension)
        )

    def _review_interface(self, base_chunks: str) -> str:
        # TODO: add prompt
        pass

    def _save_result(self, review_comments: dict) -> None:
        with open(self.result_path, "w") as f:
            with open(self.file_path, "r") as original:
                lines = original.readlines()

            for lines, comment in review_comments.items():
                match = re.match(r'^\d+', lines)
                line_num = match.group() if match else '0'
                
                line_idx = int(line_num) - 1
                line_idx = min(line_idx, len(lines) - 1)
                lines[line_idx] = (
                    f"{self.comment_sign} <REVIEW>{comment}</REVIEW>\n{lines[line_idx]}"
                )

            f.writelines(lines)

    def review(self) -> None:
        print(f"Reviewing {self.file_path}")

        base_chunks, declarations = parse_file(self.file_path)
        prompt_generator = PromptGenerator(self.extension)
        json_responses = []

        for chunk in declarations.values():
            code = code_from_chunk(chunk)
            system_prompt = prompt_generator.generate_system_prompt()
            user_prompt = prompt_generator.generate_user_prompt(code)
            context = prompt_generator.generate_context(code)

            review_json = get_response(system_prompt, user_prompt, context)
            review_json = review_json[
                review_json.index("{") : review_json.rindex("}") + 1
            ]

            # print(review_json)

            json_responses.append(json.loads(review_json))

        self._save_result(merge_json_responses(json_responses))
        print(f"Saved result to {self.result_path}")


class ProjectReviewer:
    def __init__(self, project_path: Path, result_path: Path) -> None:
        self.project_path = project_path
        self.result_path = result_path
        self.result_path.mkdir(parents=True, exist_ok=True)

    def _review_structure(self) -> None:
        project_structure = parse_project_structure(self.project_path)
        # TODO: review project structure
        pass

    def review(self) -> None:
        for file in self.project_path.rglob("*"):
            if not file.is_file() or get_file_extension(file) not in FILE_EXTENSIONS:
                continue
            relative_path = file.relative_to(self.project_path)
            print(self.result_path / relative_path)
            file_reviewer = FileReviewer(file, self.result_path / relative_path)
            file_reviewer.review()


if __name__ == "__main__":
    project_reviewer = ProjectReviewer(Path("./react-2/abctasks-client-main1"), Path("./react-2/REVIEW/abctasks-client-main1"))
    project_reviewer.review()
