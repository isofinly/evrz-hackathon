from src.parsers.language import LANGUAGE
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

    tree = Parser(LANGUAGE[extension]).parse(bytes(code, "utf-8"))
    
    code_lines = code.split("\n")
    base_chunk = Chunk(code_lines)

    declarations = dict()

    def chunk(node):
        nonlocal base_chunk
        nonlocal declarations

        base_chunk.consume(node.start_point)


        if node.type in DECLARATION[extension] or (
            node.type == "variable_declarator"
            and any([child.type == "arrow_function" for child in node.children])
        ):
            identifier, declaration_chunk, body_chunk = chunk_declaration(
                node, base_chunk, extension
            )
            declarations[str(identifier)] = {
                "identifier": identifier,
                "declaration": declaration_chunk,
                "body": body_chunk,
            }

        elif not node.children:
            base_chunk.consume(node.end_point)
        else:
            for child in node.children:
                chunk(child)

    chunk(tree.root_node)

    return base_chunk, declarations


def chunk_declaration(node, base_chunk, extension):
    identifier = None
    declaration_chunk = base_chunk.fork()
    body_chunk = None


    def chunk(node):
        nonlocal identifier
        nonlocal declaration_chunk
        nonlocal body_chunk
        
        base_chunk.consume(node.start_point)
        declaration_chunk.consume(node.start_point)

        if "identifier" in node.type and identifier is None:
            identifier = base_chunk.fork()
            identifier.consume(node.end_point)
            base_chunk.consume(node.end_point)
            declaration_chunk.consume(node.end_point)

            return
        
        if node.type in STATEMENT[extension]:
            body_chunk = declaration_chunk.fork()
            base_chunk.add_tag(f"<BODY {identifier}>")
            declaration_chunk.add_tag(f"<BODY {identifier}>")
            body_chunk.consume(node.end_point)
            base_chunk.skip(node.end_point)
            declaration_chunk.skip(node.end_point)

            return

        if not node.children:
            base_chunk.consume(node.end_point)
            declaration_chunk.consume(node.end_point)
        else:
            for child in node.children:
                chunk(child)

    chunk(node)

    return identifier, declaration_chunk, body_chunk

class Chunk:
    def __init__(self, code_lines, chunk_start=(0, 0)):
        self._code_lines = code_lines
        self._chunk_start = chunk_start
        self._chunk_str = ""
        self._ptr = chunk_start

    def consume(self, until_point):
        if self._ptr[0] == until_point[0]:
            self._chunk_str += (
                self._code_lines[self._ptr[0]][self._ptr[1] : until_point[1]] + ("\n" if until_point[1] == len(self._code_lines[self._ptr[0]]) else "")
            )
            self._ptr = until_point
            return
        

        self._chunk_str += self._code_lines[self._ptr[0]][self._ptr[1] :] + "\n"

        for i in range(self._ptr[0] + 1, until_point[0]):
            self._chunk_str += self._code_lines[i] + "\n"

        self._chunk_str += self._code_lines[until_point[0]][: until_point[1]]
        self._ptr = until_point

    def add_tag(self, tag):
        self._chunk_str += tag

    def fork(self):
        return Chunk(self._code_lines, self._ptr)
    
    def skip(self, until_point):
        self._ptr = until_point

    def __str__(self):
        return self._chunk_str