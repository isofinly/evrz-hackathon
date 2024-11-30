ts_styleguide_prompts = {
    "project_structure": """
    Имена файлов и директорий PascalCase, например MyFile.cs
    """,
    "naming": """
    Имена классов, методов, перечислений, публичных полей, публичных свойств, пространств имен: PascalCase.
    Имена локальных переменных, параметров: camelCase
    Имена приватных, защищенных, внутренних и защищенных внутренних полей и свойств: _camelCase.
    Имена модификаторов такие как const, static, readonly, etc. не влияют на именование.
    Имена интерфейсов начинаются с I, например IInterface.
    """,
    "file_structure": """
    Название файла должно быть таким же, как название главного класса в файле, например MyClass.cs
    В общем случае предпочтительно иметь один основной класс в файле.
    Модификаторы доступа используются в следующем порядке: public protected internal private new abstract virtual override sealed static readonly extern unsafe volatile async.
    Namespace using для пространств имен располагаются вверху, перед любыми пространствами имен, после импортов
    Импорты располагаются в самом начале файла
    """,
    "imports": """
    Импорты располагаются в самом начале файла
    """,
    "general": """
    В коде не должно быть неразрешенных TODO
    Код с атрибутом Obsolete , по возможности, должен быть удален
    Обязательное наличие комментариев для моделей, сущностей и т.д.
    Не должно быть закомментированного или неиспользуемого кода
    Не используйте using для сокращения длинных имен типов
    Пространства имен не должны быть более двух уровней вложенности
    Для общего кода библиотеки/модуля используйте пространства имен. Для кода лист-приложения, такого как unity_app, пространства имен не нужны.
    """,
    "classes": """
    Группируйте члены класса в следующем порядке:
        1) Вложенные классы, перечисления, делегаты и события.
        2) Статические, константные и неизменяемые поля.
        3) Поля и свойства.
        4) Конструкторы и финализаторы.
        5) Методы.
    В каждой группе элементы должны быть в следующем порядке:
        1) Public.
        2) Internal.
        3) Protected internal.
        4) Protected.
        5) Private.
    Группируйте реализации интерфейсов вместе.
    
    Структуры всегда передаются и возвращаются по значению.
    Почти всегда используйте классы вместо структур.
    """,
    "functions": """
    Если лямбда-функция нетривиальна, или повторно используется в нескольких местах, она, должна быть именованной функцией.
    Используйте out для возвращаемых значений, которые не являются также входными параметрами.
    Параметры out должны быть расположены после всех других параметров в определении метода.
    ref должен использоваться редко, когда необходимо изменять входной параметр.
    Не используйте ref как оптимизацию для передачи структур.
    Предпочтительно возвращать boolean success и структуру out.
    """,
    "types": """
    Предпочтительно использовать массивы для многомерных массивов.
    Предпочтительно использовать List<> вместо массивов для публичных переменных, свойств и возвращаемых типов
    Используйте массивы, когда размер контейнера известен и фиксирован при конструировании.
    Используйте var, когда тип очевиден - например, var apple = new Apple();, или var request = Factory.Create<HttpRequest>();
    """,
}
