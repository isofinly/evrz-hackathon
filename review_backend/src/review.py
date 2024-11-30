from pathlib import Path
from utils import get_project_language
from prompt import PromptGenerator
from parsers.parser import parse_file


class FileReviewer:
    def __init__(self, file_path: Path, result_path: Path):
        self.file_path = file_path
        self.result_path = result_path
        self.extension = file_path.name.split(".")[-1]
        
    def _review_interface(self, base_chunks: str) -> str:
        pass

    def review(self):
        base_chunks, declarations = parse_file(self.file_path)
        prompt_generator = PromptGenerator(self.extension)
        
        # system_prompt = prompt_generator.generate_system_prompt()
        # user_prompt = prompt_generator.generate_user_prompt(code)
        # context = prompt_generator.generate_context(code)


class ProjectReviewer:
    def __init__(self, project_path: Path, result_path: Path):
        self.project_path = project_path
        self.result_path = result_path
        self.language = get_project_language(project_path)
        
    def _review_structure(self):
        pass
        
    def review(self):
        for file in self.project_path.glob("**/*.py"):
            relative_path = file.relative_to(self.project_path)
            file_reviewer = FileReviewer(file, self.result_path / relative_path)
            file_reviewer.review()
    

if __name__ == "__main__":
    project_reviewer = ProjectReviewer(Path("."), Path("."))
    project_reviewer.review()
