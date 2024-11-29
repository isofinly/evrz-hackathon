import typing as tp
from pathlib import Path


def strip_function_bodies(py_lines: list[str]) -> str:
    """
    Returns a string with Python code without function bodies
    """
    key_constructions = ['def', 'class', 'import', 'from']
    result = []
    open_parentheses = 0
    current_declaration = []
    for line in py_lines:
        
        if any(construction in line for construction in key_constructions):
            current_declaration = [line.rstrip()]
            open_parentheses = line.count('(') - line.count(')')
            
            if open_parentheses == 0:
                result.extend(current_declaration)
                current_declaration = []
            continue
        
        if open_parentheses > 0:
            current_declaration.append(line.rstrip())
            open_parentheses += line.count('(') - line.count(')')
            
            if open_parentheses == 0:
                result.extend(current_declaration)
                current_declaration = []
                
    return '\n'.join(result)


def get_py_declarations(py_lines: list[str]) -> tp.Iterator[str]:
    """
    Returns an iterator of Python declarations (functions and complete classes with their methods)
    """
    if len(py_lines) == 0:
        return

    current_declaration = []
    indent_level = None
    in_class = False
    class_indent = None
    
    for line in py_lines:
        stripped_line = line.rstrip()
            
        current_indent = len(line) - len(line.lstrip())
        
        if 'class ' in line:
            if current_declaration and not in_class:
                yield '\n'.join(current_declaration)
            current_declaration = [stripped_line]
            indent_level = current_indent
            in_class = True
            class_indent = current_indent
            continue
            
        if 'def ' in line:
            if not in_class:
                if current_declaration:
                    yield '\n'.join(current_declaration)
                current_declaration = [stripped_line]
                indent_level = current_indent
            else:
                current_declaration.append(stripped_line)
            continue
            
        if indent_level is not None and current_indent > indent_level:
            current_declaration.append(stripped_line)
            
        elif in_class and current_indent <= class_indent:
            yield '\n'.join(current_declaration)
            current_declaration = []
            in_class = False
            indent_level = None
            class_indent = None
            
        elif not in_class and indent_level is not None and current_indent <= indent_level:
            yield '\n'.join(current_declaration)
            current_declaration = []
            indent_level = None
    
    if current_declaration:
        yield '\n'.join(current_declaration)

