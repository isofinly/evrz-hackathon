from tree_sitter import Language, Parser
import tree_sitter_python as ts_python
import tree_sitter_c_sharp as ts_csharp
import tree_sitter_typescript as ts_typescript

LANGUAGE = {
    "py": Language(ts_python.language()),
    "cs": Language(ts_csharp.language()),
    "tsx": Language(ts_typescript.language_tsx()),
    "ts": Language(ts_typescript.language_typescript())
}


IMPORTANT_NODES = {
    "py": ["import_statement", "import_as_statement", "import_from_statement", "class_decloration", "function_decloration"]
}