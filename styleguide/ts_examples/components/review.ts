// <REVIEW> Файлы с расширением tsx и отображающие контент должны быть с большой буквы </REVIEW>
// <REVIEW> Данный файл является компонентой и должен по пути "/src/Components/{название папки}/{название файла}.tsx"</REVIEW>
// <REVIEW> Данный файл является контейнером и должен по пути"/src/Containers/{название папки}/{название файла}.tsx"</REVIEW>
// <REVIEW> данный файл должен находиться по пути "/src/pages/ResultsPage/ResultsPage.tsx"</REVIEW>
// <REVIEW> Стили должны передаваться через props параметры style или className </REVIEW>
// <REVIEW> Данный интерфейс является интерфейсом для компоненты и должен находиться в файле types.ts на одном уровне с компонентой</REVIEW>
// <REVIEW> Стили className должны быть модульными</REVIEW>
// <REVIEW> Разделяйте виды компонентов по их назначению: UI Kit: абстрактные UI-компоненты для повторного использования; Components: UI-компоненты, специфичные для модуля; Containers: компоненты, работающие с данными; Pages: компоненты-экраны.</REVIEW>
// <REVIEW> Типизация компонентов обязательна. Интерфейс для props должен включать className?: string и style?: React.CSSProperties.</REVIEW>
// <REVIEW> Для сложных компонентов используйте CSS Custom Properties с шаблоном именования: --<имя-элемента>-<название-стиля>-<модификатор>.</REVIEW>
// <REVIEW> В каталоге компонента должна быть соблюдена структура: index.ts (для экспорта), <ComponentName>.tsx (основной файл), <ComponentName>.module.css (стили), types.ts (типизация), utils.ts (утилиты).</REVIEW>
// <REVIEW> Данный компонент содержит много логики, его следует разделить на более мелкие атомарные компоненты</REVIEW>
// <REVIEW> Имя данного компонента не отражает его функциональность</REVIEW>