from parsers.language import LANGUAGE
from tree_sitter import Parser


DECLARATION = {
    "py": ["class_definition", "function_definition"],
    "cs": [
        "class_declaration",
        "method_declaration",
        "function_declaration",
        "interface_declaration",
    ],
    "ts": [
        "class_declaration",
        "function_declaration",
        "interface_declaration",
        "type_alias_declaration",
    ],
    "tsx": [
        "class_declaration",
        "function_declaration",
        "interface_declaration",
        "type_alias_declaration",
    ],
}

EXPORT = {
    "py": ["export_statement"],
    "cs": ["export_statement"],
    "ts": ["export_statement"],
    "tsx": ["export_statement"],
}

IMPORT = {
    "py": ["import_statement", "import_as_statement", "import_from_statement"],
    "cs": ["using_statement"],
    "ts": ["import_statement", "import_as_statement", "import_from_statement"],
    "tsx": ["import_statement", "import_as_statement", "import_from_statement"],
}

STATEMENT = {
    "py": ["block"],
    "cs": ["block"],
    "ts": ["statement_block", "interface_body"],
    "tsx": ["statement_block", "interface_body"],
}


def chunk_code(code: str, extension: str):
    base_chunk = ""
    declarations = dict()

    def chunk(node):
        nonlocal base_chunk
        nonlocal declarations

        print(node.type)

        if node.type in IMPORT[extension]:
            base_chunk += (
                "<IMPORT>"
                + concatenate_lines(code_lines, node.start_point, node.end_point)
                + "</IMPORT>\n"
            )
            return
        elif node.type in DECLARATION[extension] or (
            node.type == "variable_declarator"
            and any([child.type == "arrow_function" for child in node.children])
        ):
            identifier, declaration, body = chunk_declaration(
                code_lines, node, extension
            )
            declarations[identifier] = {
                "identifier": identifier,
                "declaration": declaration,
                "body": body,
            }
            base_chunk += declaration
        elif not node.children:
            base_chunk += concatenate_lines(
                code_lines, node.start_point, node.end_point
            )
        else:
            for child in node.children:
                chunk(child)

    tree = Parser(LANGUAGE[extension]).parse(bytes(code, "utf-8"))
    code_lines = code.split("\n")

    chunk(tree.root_node)

    return base_chunk, declarations


def chunk_declaration(code_lines, node, extension):
    identifier = None
    declaration = ""
    body = ""

    def chunk(node):
        nonlocal identifier
        nonlocal declaration
        nonlocal body

        if "identifier" in node.type and identifier is None:
            identifier = concatenate_lines(code_lines, node.start_point, node.end_point)
            declaration += identifier
            return
        elif node.type in STATEMENT[extension]:
            body = concatenate_lines(code_lines, node.start_point, node.end_point)
            declaration += f"<BODY {identifier}></BODY>\n"
            return

        if not node.children:
            declaration += concatenate_lines(
                code_lines, node.start_point, node.end_point
            )
        else:
            for child in node.children:
                chunk(child)

    chunk(node)

    return identifier, declaration, body


def concatenate_lines(code_lines, start_point, end_point):
    if start_point[0] == end_point[0]:
        return code_lines[start_point[0]][start_point[1] : end_point[1]] + " "
    string = code_lines[start_point[0]][start_point[1] :] + "\n"
    for i in range(start_point[0] + 1, end_point[0]):
        string += code_lines[i] + "\n"
    string += code_lines[end_point[0]][: end_point[1]]
    if len(code_lines[end_point[0]]) == end_point[1]:
        string += "\n"
    return string + " "
