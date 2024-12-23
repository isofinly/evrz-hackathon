py_styleguide_prompts = {
    "project_structure": """
    Имена файлов Python должны иметь расширение .py и не должны содержать дефисов (-).
    в корне лежит .gitignore
    в корне лежит .editorconfig 
    в корне лежит .gitattributes
    в deployment лежат файлы для CI/CD    
    в docs хранится техническая документация
    Используется "Гексагональная" архитектура, первичные и вторичные адаптеры у нас в одном каталоге
    В слое приложения лежит все что относится к бизнес логике (сущности, DTO, константы, DS модель, сервисы)
    """,
    "strings": """
    Используйте f-строку, оператор % или метод format для форматирования строк, даже если все параметры являются строками
    Избегайте использования операторов + и += для накопления строки внутри цикла
    """,
    "naming": """
    названия таблиц начинаются с маленьких букв, используется snake_case
    Правила именования сущностей: module_name, package_name, ClassName, method_name, ExceptionName, function_name, GLOBAL_CONSTANT_NAME, global_var_name, instance_var_name, function_parameter_name, local_var_name, query_proper_noun_for_thing, send_acronym_via_https
    Имена функций, переменных и файлов должны быть осмысленными; избегайте аббревиатур
    Не использовать однобуквенные имена переменных кроме счетчиков, итераторво и переменных в лямбда-функциях
    """,
    "imports": """
    Используйте import для пакетов и модулей, а не для отдельных типов, классов или функций.
    Импортируйте каждый модуль, используя полный путь к местоположению модуля.
    Импорты должны быть на отдельных строках; есть исключения для импортов типов и импортов из collections.abc.
    Импорты всегда находятся в начале файла
    Импорты должны быть сгруппированы от наиболее общего к наиболее специфичному:
    """,
    "general": """
    Максимальная длина строки 80 символов.
    Не использовать print для логгирования
    Избегайте изменяемого глобального состояния.
    Используйте стандартные итераторы и операторы для типов, которые их поддерживают, таких как списки, словари и файлы.
    Используйте генераторные выражения вместо map() или filter() с лямбда-функциями.
    Conditional expressions хорошо подходят для простых случаев
    Используйте “implicit” false, если это возможно
    Не полагайтесь на атомарность встроенных типов
    Не используйте getattr(), __del__
    Между верхнеуровневыми определениями (функциями или классами) должно быть две пустые строки. Между методами и между строкой документации класса и первым методом должна быть одна пустая строка. Нет пустой строки после строки def.
    """,
    "classes": """
    Используйте декораторы мудро, когда есть явный преимущество. Избегайте staticmethod и ограничьте использование classmethod
    Getters and setters должны следовать рекомендациям по именованию, таким как get_foo() и set_foo()
    """,
    "functions": """
    Используйте декораторы, когда есть явное преимущество. Избегайте staticmethod и ограничьте использование classmethod
    Если лямбда нетривиальна, она должна быть именованной функцией
    Предпочитайте маленькие и сфокусированные функции.
    """,
    "exceptions": """
    Используйте встроенные классы исключений, когда это имеет смысл
    Не используйте assert вместо условий или для проверки предусловий
    Никогда не используйте всеобъемлющие except: утверждения, или ловите Exception или StandardError, если только вы не повторно поднимаете исключение
    Минимизируйте количество кода в блоке try/except
    Используйте finally для выполнения кода, независимо от того, поднимается ли исключение в блоке try
    """,
}
