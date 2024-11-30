from pathlib import Path

from src.review.utils import (
    language_from_file_extension,
    add_line_numbers,
    code_from_chunk,
)
from src.review.parsers.make_chunks import Chunk

from src.review.rag import Data

class PromptGenerator:
    def __init__(self, data: Data, file_extension: str):
        self.file_extension = file_extension
        self.language = language_from_file_extension(file_extension)
        self.comment_symbol = "//"
        if self.language == "python":
            self.comment_symbol = "#"

        self.data = data


    def generate_system_prompt(self) -> str:
        return f"""
Отвечай на русском языке.
Ты – опытный инженер-программист и профессиональный код-ревьюер с глубокими знаниями {self.language}.
Твоя задача – проанализировать предоставленный фрагмент кода, указать все ошибки, плохие практики, неэффективности и предложить улучшения.
Над фрагментом кода, которой тебе предстоит проверить, находится путь к файлу относительно корня проекта.
ОТСУТСТВИЕ ИМПОРТОВ НЕ СЧИТАЙ ОШИБКОЙ.
Ответ должен быть строго в формате JSON, где:
- Ключ – номер первой строки перед проблемой.
- Значение – комментарий ревьюера с кратким описанием проблемы и предложением возможного ее решения.

**Требования к комментариям:**
- Используй короткие и точные формулировки.
- Избегай фигурных скобок внутри текста комментария.
- Не повторяй комментарии для одинаковых ошибок.
"""

    def generate_user_prompt(self, chunk: Chunk, relative_path: Path) -> str:
        code = add_line_numbers(str(chunk), chunk.get_start_line())
        return f"{relative_path}\n{code}"

    def generate_context(self, code: str) -> dict[str, list[str]]:
        """
        Returns a dictionary with the following keys:
        - "user" -- list of previous user messages
        - "assistant" -- list of previous assistant messages
        """

        examples = self.data.get_review(code, extension=self.file_extension, n_results=7)
        # print(examples)

        return {
            "user": [ex["query"] for ex in examples],
            "assistant": [ex["answer"] for ex in examples],
        }
