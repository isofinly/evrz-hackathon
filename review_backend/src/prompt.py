from utils import language_from_file_extension


class PromptGenerator:
    def __init__(self, file_extension: str):
        self.language = language_from_file_extension(file_extension)
        self.comment_symbol = "//"
        if self.language == "python":
            self.comment_symbol = "#"

    def generate_system_prompt(self) -> str:
        return f"""
Отвечай на русском языке.
Ты - высококвалифицированный инженер-программист на языке {self.language} и код-ревьюер.
Твоя задача – просмотреть фрагмент кода и выявить все ошибки, плохие практики, неэффективности или возможные улучшения.
Твой ответ должен быть написан в формате json. Ключи: номера строк, значения - комментарии ревьюера. Делай комментарии максимально короткими и точными.
"""

    def generate_user_prompt(self, code: str) -> str:
        return code

    def generate_context(self, code: str) -> dict[str, list[str]]:
        """
        Returns a dictionary with the following keys:
        - "user" -- list of previous user messages
        - "assistant" -- list of previous assistant messages
        """
        example_query_prompt = """
1 import { Product } from "@/entities/CardsGallary/model/types/types";
2
3 import { Endpoints } from "@/shared/utils";
4 import { createStore, createEffect } from "effector";
5
6 export const $filters = createStore<ProductFilters>({
7   limit: 10,
8   query: "",
9   category: "all" as Category,
10   skip: 0,
11 });
12
13 type Props = {
14   setLoading: (value: boolean) => void;
15  
16   filters: ProductFilters;
17 };
"""
        
        example_answer_prompt = """
{
  "1": "Название модуля `CardsGallary` содержит опечатку. Вероятно, имелось в виду `CardsGallery`.",
  "6": "Название переменной `$filters` нарушает правило об использовании символа `$` в идентификаторах. Рекомендуется переименовать переменную в `filtersStore` или другое осмысленное название.",
  "14": "Имена параметров в интерфейсе `Props` нарушают правило. Имя `setLoading` должно быть более описательным, например, `updateLoadingState`."
}

"""

        return {
            "user": [example_query_prompt],
            "assistant": [example_answer_prompt]
        }