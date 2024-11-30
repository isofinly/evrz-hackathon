from pathlib import Path
from parsers.make_chunks import chunk_code


class FileReviewer:
    def __init__(self, file_path: Path, result_path: Path):
        self.file_path = file_path
        self.result_path = result_path

    def review(self):
        pass


class ProjectReviewer:
    def __init__(self, project_path: Path, result_path: Path):
        self.project_path = project_path
        self.result_path = result_path

    def review(self) -> Path:
        pass
    

if __name__ == "__main__":
    print(chunk_code("print(a + b)", "py"))
