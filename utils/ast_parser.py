import ast
import inspect
from typing import Dict, List, Any, Optional
from .complexity_analyzer import ComplexityAnalyzer

class PythonASTParser:
    """Parser for extracting metadata from Python code using AST."""
    
    def __init__(self):
        self.complexity_analyzer = ComplexityAnalyzer()
    
    def parse_code(self, code: str) -> Dict[str, Any]:
        """
        Parse Python code and extract function and class metadata.
        
        Args:
            code: Python source code as string
            
        Returns:
            Dictionary containing parsed metadata
        """
        try:
            tree = ast.parse(code)
            
            result = {
                'functions': [],
                'classes': [],
                'imports': [],
                'module_docstring': self._get_module_docstring(tree)
            }
            
            for node in ast.walk(tree):
                if isinstance(node, ast.Import):
                    result['imports'].extend(self._parse_import(node))
                elif isinstance(node, ast.ImportFrom):
                    result['imports'].extend(self._parse_import_from(node))
                elif isinstance(node, ast.FunctionDef):
                    # Only parse top-level functions (not methods)
                    if self._is_top_level_function(tree, node):
                        result['functions'].append(self._parse_function(node, code))
                elif isinstance(node, ast.ClassDef):
                    result['classes'].append(self._parse_class(node, code))
            
            return result
            
        except Exception as e:
            raise Exception(f"Failed to parse code: {str(e)}")
    
    def _get_module_docstring(self, tree: ast.AST) -> Optional[str]:
        """Extract module-level docstring."""
        if (tree.body and 
            isinstance(tree.body[0], ast.Expr) and 
            isinstance(tree.body[0].value, ast.Str)):
            return tree.body[0].value.s
        elif (tree.body and 
              isinstance(tree.body[0], ast.Expr) and 
              isinstance(tree.body[0].value, ast.Constant) and
              isinstance(tree.body[0].value.value, str)):
            return tree.body[0].value.value
        return None
    
    def _is_top_level_function(self, tree: ast.AST, func_node: ast.FunctionDef) -> bool:
        """Check if function is at module level (not inside a class)."""
        for node in ast.walk(tree):
            if isinstance(node, ast.ClassDef):
                for class_node in ast.walk(node):
                    if class_node is func_node:
                        return False
        return True
    
    def _parse_function(self, node: ast.FunctionDef, source_code: str) -> Dict[str, Any]:
        """Parse function node and extract metadata."""
        function_data = {
            'name': node.name,
            'line_number': node.lineno,
            'docstring': ast.get_docstring(node),
            'parameters': self._parse_parameters(node.args),
            'return_annotation': self._parse_annotation(node.returns),
            'decorators': [self._parse_decorator(dec) for dec in node.decorator_list],
            'is_async': isinstance(node, ast.AsyncFunctionDef),
            'complexity': self.complexity_analyzer.calculate_complexity(node),
            'lines_of_code': self._count_lines(node)
        }
        
        return function_data
    
    def _parse_class(self, node: ast.ClassDef, source_code: str) -> Dict[str, Any]:
        """Parse class node and extract metadata."""
        class_data = {
            'name': node.name,
            'line_number': node.lineno,
            'docstring': ast.get_docstring(node),
            'bases': [self._parse_base_class(base) for base in node.bases],
            'decorators': [self._parse_decorator(dec) for dec in node.decorator_list],
            'methods': [],
            'attributes': [],
            'lines_of_code': self._count_lines(node)
        }
        
        # Parse methods and attributes
        for item in node.body:
            if isinstance(item, (ast.FunctionDef, ast.AsyncFunctionDef)):
                class_data['methods'].append(self._parse_function(item, source_code))
            elif isinstance(item, ast.Assign):
                class_data['attributes'].extend(self._parse_class_attributes(item))
        
        return class_data
    
    def _parse_parameters(self, args: ast.arguments) -> List[Dict[str, Any]]:
        """Parse function parameters."""
        parameters = []
        
        # Regular arguments
        for i, arg in enumerate(args.args):
            param_data = {
                'name': arg.arg,
                'annotation': self._parse_annotation(arg.annotation),
                'default': None,
                'kind': 'positional'
            }
            
            # Check for default values
            defaults_offset = len(args.args) - len(args.defaults)
            if i >= defaults_offset:
                default_index = i - defaults_offset
                param_data['default'] = self._parse_default_value(args.defaults[default_index])
            
            parameters.append(param_data)
        
        # *args parameter
        if args.vararg:
            parameters.append({
                'name': f"*{args.vararg.arg}",
                'annotation': self._parse_annotation(args.vararg.annotation),
                'default': None,
                'kind': 'var_positional'
            })
        
        # Keyword-only arguments
        for i, arg in enumerate(args.kwonlyargs):
            param_data = {
                'name': arg.arg,
                'annotation': self._parse_annotation(arg.annotation),
                'default': None,
                'kind': 'keyword_only'
            }
            
            if i < len(args.kw_defaults) and args.kw_defaults[i] is not None:
                param_data['default'] = self._parse_default_value(args.kw_defaults[i])
            
            parameters.append(param_data)
        
        # **kwargs parameter
        if args.kwarg:
            parameters.append({
                'name': f"**{args.kwarg.arg}",
                'annotation': self._parse_annotation(args.kwarg.annotation),
                'default': None,
                'kind': 'var_keyword'
            })
        
        return parameters
    
    def _parse_annotation(self, annotation) -> Optional[str]:
        """Parse type annotation."""
        if annotation is None:
            return None
        
        try:
            return ast.unparse(annotation)
        except:
            # Fallback for older Python versions
            if isinstance(annotation, ast.Name):
                return annotation.id
            elif isinstance(annotation, ast.Constant):
                return str(annotation.value)
            elif isinstance(annotation, ast.Attribute):
                return f"{self._parse_annotation(annotation.value)}.{annotation.attr}"
            else:
                return str(type(annotation).__name__)
    
    def _parse_default_value(self, default) -> str:
        """Parse default parameter value."""
        try:
            return ast.unparse(default)
        except:
            # Fallback for older Python versions
            if isinstance(default, ast.Constant):
                return repr(default.value)
            elif isinstance(default, ast.Name):
                return default.id
            else:
                return "..."
    
    def _parse_decorator(self, decorator) -> str:
        """Parse decorator."""
        try:
            return ast.unparse(decorator)
        except:
            if isinstance(decorator, ast.Name):
                return decorator.id
            else:
                return str(type(decorator).__name__)
    
    def _parse_base_class(self, base) -> str:
        """Parse base class."""
        try:
            return ast.unparse(base)
        except:
            if isinstance(base, ast.Name):
                return base.id
            else:
                return str(type(base).__name__)
    
    def _parse_class_attributes(self, node: ast.Assign) -> List[Dict[str, Any]]:
        """Parse class attributes from assignment nodes."""
        attributes = []
        
        for target in node.targets:
            if isinstance(target, ast.Name):
                attributes.append({
                    'name': target.id,
                    'line_number': node.lineno,
                    'annotation': self._parse_annotation(getattr(node, 'annotation', None))
                })
        
        return attributes
    
    def _parse_import(self, node: ast.Import) -> List[Dict[str, str]]:
        """Parse import statement."""
        imports = []
        for alias in node.names:
            imports.append({
                'type': 'import',
                'module': alias.name,
                'alias': alias.asname,
                'line_number': node.lineno
            })
        return imports
    
    def _parse_import_from(self, node: ast.ImportFrom) -> List[Dict[str, str]]:
        """Parse from...import statement."""
        imports = []
        for alias in node.names:
            imports.append({
                'type': 'from_import',
                'module': node.module,
                'name': alias.name,
                'alias': alias.asname,
                'line_number': node.lineno
            })
        return imports
    
    def _count_lines(self, node: ast.AST) -> int:
        """Count lines of code for a node."""
        if hasattr(node, 'end_lineno') and node.end_lineno:
            return node.end_lineno - node.lineno + 1
        else:
            # Fallback: estimate based on body length
            return len(getattr(node, 'body', [])) + 1
