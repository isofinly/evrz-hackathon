from pathlib import Path
import typing as tp

def strip_function_bodies(ts_lines: list[str]) -> str:
    """
    Returns a string with TypeScript code without function bodies
    """
    key_constructions = ['function', '=>', 'async ', '):', 'class', 'interface', 'type', 'enum', 'component', 'constructor']
    result = []
    brace_count = 0
    
    for line in ts_lines:
        stripped = line.strip()
        
        if stripped.startswith('import ') or stripped.startswith('from '):
            result.append(line)
            continue
        
        brace_count += line.count('{') - line.count('}')
        
        if any(construction in line for construction in key_constructions):
            result.append(line.replace('{', '').replace('}', '').rstrip())
            
    return '\n'.join(result)


def get_ts_declarations(ts_lines: list[str]) -> tp.Iterator[str]:
    """
    Returns an iterator of TypeScript declarations
    (functions, classes, components, etc.)
    """
    current_declaration = []
    for line in ts_lines:
        stripped = line.strip()
        if not stripped or stripped.startswith(('import ', 'from ')):
            continue
        current_declaration.append(line.rstrip())
        if line.rstrip() == '}':
            yield '\n'.join(current_declaration)
            current_declaration = []
