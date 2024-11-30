import json
import re
import threading
from tqdm import tqdm
from concurrent.futures import ThreadPoolExecutor, as_completed

from pathlib import Path
from src.review.utils import (
    get_file_extension,
    merge_json_responses,
    get_styleguide_by_language,
    language_from_file_extension,
)
from src.review.prompt import PromptGenerator
from src.review.parsers.parser import parse_file
from src.review.parsers.project_parser import parse_project_structure
from src.review.rag import Data

from src.review.api import get_response
# from gemma_api import get_response


FILE_EXTENSIONS = ["py", "cs", "ts", "tsx", "css", "scss"]


DATA_PATH = Path(__file__).parent.parent.parent.parent / "data"

DATA = Data(DATA_PATH)


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

        self.prompt_generator = PromptGenerator(DATA, self.extension)

    def _review_interface(self, base_chunks: str) -> str:
        # TODO: add prompt
        pass

    def _save_result(self, review_comments: dict) -> None:
        with open(self.file_path, "r") as original:
            lines = original.readlines()

        for line_num, comment in review_comments.items():
            match = re.match(r"^\d+", line_num)
            line_idx = int(match.group() if match else "1") - 1
            line_idx = min(line_idx, len(lines) - 1)
            lines[line_idx] = (
                f"{self.comment_sign} <REVIEW>{comment}</REVIEW>\n{lines[line_idx]}"
            )

        with open(self.result_path, "w") as f:
            f.writelines(lines)

    def review(self) -> None:
        print(f"Reviewing {self.file_path}")
        print()

        base_chunks, declarations = parse_file(self.file_path)
        json_responses = []

        for chunk in declarations.values():
            system_prompt = self.prompt_generator.generate_system_prompt()
            user_prompt = self.prompt_generator.generate_user_prompt(chunk)
            context = self.prompt_generator.generate_context(str(chunk))

            review_json = get_response(system_prompt, user_prompt, context)
            review_json = review_json[
                review_json.index("{") : review_json.rindex("}") + 1
            ]

            # print(review_json)
            # print()

            try:
                json_responses.append(json.loads(review_json))
            except json.JSONDecodeError:
                print(
                    "!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!JSONDecodeError!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!"
                )

        self._save_result(merge_json_responses(json_responses))
        # print(f"Saved result to {self.result_path}")


class ProjectReviewer:
    def __init__(
        self, project_path: Path, result_path: Path, max_workers: int = 5
    ) -> None:
        self.project_path = project_path
        self.result_path = result_path
        self.result_path.mkdir(parents=True, exist_ok=True)
        self.max_workers = max_workers
        self.print_lock = threading.Lock()


    def _review_structure(self) -> None:
        project_structure = parse_project_structure(self.project_path)
        # TODO: review project structure
        pass

    def _review_file(self, file: Path) -> None:
        try:
            relative_path = file.relative_to(self.project_path)
            file_reviewer = FileReviewer(file, self.result_path / relative_path)
            file_reviewer.review()
        except Exception as e:
            with self.print_lock:
                print(f"Error reviewing {file}: {str(e)}")

    def review(self) -> None:
        files_to_review = [
            file for file in self.project_path.rglob("*")
            if file.is_file() and get_file_extension(file) in FILE_EXTENSIONS
        ]
            
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            future_to_file = {
                executor.submit(self._review_file, file): file 
                for file in files_to_review
            }
            
            # Process completed reviews with progress bar
            with tqdm(total=len(files_to_review)) as pbar:
                for future in as_completed(future_to_file):
                    file = future_to_file[future]
                    try:
                        future.result()  # This will raise any exceptions that occurred
                    except Exception as e:
                        with self.print_lock:
                            print(f"Review failed for {file}: {str(e)}")
                    pbar.update(1)


def review2() -> None:
    project_reviewer = ProjectReviewer(
        Path("../react-2/market-main"), Path("../react-2/REVIEW/market-main")
    )
    # project_reviewer = ProjectReviewer(Path("./TEST_PROJECT"), Path("./TEST_PROJECT/REVIEW"))
    project_reviewer.review()


if __name__ == "__main__":
    review2()
