import json
from typing import Dict, Any, List
from datetime import datetime

class DocumentationGenerator:
    """Generator for creating formatted documentation from parsed code metadata."""
    
    def __init__(self, include_complexity: bool = True, include_type_hints: bool = True, include_docstrings: bool = True):
        self.include_complexity = include_complexity
        self.include_type_hints = include_type_hints
        self.include_docstrings = include_docstrings
    
    def generate_documentation(self, parsed_data: Dict[str, Any]) -> str:
        """
        Generate comprehensive documentation from parsed metadata.
        
        Args:
            parsed_data: Dictionary containing parsed code metadata
            
        Returns:
            Formatted documentation string
        """
        doc_parts = []
        
        # Header
        doc_parts.append("# Python Code Documentation")
        doc_parts.append(f"*Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
        doc_parts.append("")
        
        # Module docstring
        if parsed_data.get('module_docstring'):
            doc_parts.append("## Module Description")
            doc_parts.append(parsed_data['module_docstring'])
            doc_parts.append("")
        
        # Summary
        doc_parts.append("## Summary")
        doc_parts.append(self._generate_summary(parsed_data))
        doc_parts.append("")
        
        # Imports
        if parsed_data.get('imports'):
            doc_parts.append("## Imports")
            doc_parts.append(self._format_imports(parsed_data['imports']))
            doc_parts.append("")
        
        # Functions
        if parsed_data.get('functions'):
            doc_parts.append("## Functions")
            for func in parsed_data['functions']:
                doc_parts.append(self._format_function(func))
                doc_parts.append("")
        
        # Classes
        if parsed_data.get('classes'):
            doc_parts.append("## Classes")
            for cls in parsed_data['classes']:
                doc_parts.append(self._format_class(cls))
                doc_parts.append("")
        
        return "\n".join(doc_parts)
    
    def _generate_summary(self, parsed_data: Dict[str, Any]) -> str:
        """Generate a summary of the parsed code."""
        summary_parts = []
        
        # Count statistics
        num_functions = len(parsed_data.get('functions', []))
        num_classes = len(parsed_data.get('classes', []))
        num_methods = sum(len(cls.get('methods', [])) for cls in parsed_data.get('classes', []))
        num_imports = len(parsed_data.get('imports', []))
        
        summary_parts.append(f"- **Functions:** {num_functions}")
        summary_parts.append(f"- **Classes:** {num_classes}")
        summary_parts.append(f"- **Methods:** {num_methods}")
        summary_parts.append(f"- **Imports:** {num_imports}")
        
        return "\n".join(summary_parts)
    
    def _format_imports(self, imports: List[Dict[str, Any]]) -> str:
        """Format import statements."""
        import_lines = []
        
        for imp in imports:
            if imp['type'] == 'import':
                line = f"- `import {imp['module']}`"
                if imp.get('alias'):
                    line += f" as {imp['alias']}"
            else:  # from_import
                line = f"- `from {imp['module']} import {imp['name']}`"
                if imp.get('alias'):
                    line += f" as {imp['alias']}"
            
            import_lines.append(line)
        
        return "\n".join(import_lines)
    
    def _format_function(self, func: Dict[str, Any]) -> str:
        """Format function documentation."""
        doc_parts = []
        
        # Function signature
        signature = self._build_signature(func)
        doc_parts.append(f"### `{signature}`")
        
        # Location info
        doc_parts.append(f"*Line {func['line_number']}*")
        
        # Docstring
        if self.include_docstrings and func.get('docstring'):
            doc_parts.append("")
            doc_parts.append("**Description:**")
            doc_parts.append(func['docstring'])
        
        # Parameters
        if func.get('parameters'):
            doc_parts.append("")
            doc_parts.append("**Parameters:**")
            for param in func['parameters']:
                param_doc = f"- `{param['name']}`"
                if self.include_type_hints and param.get('annotation'):
                    param_doc += f": {param['annotation']}"
                if param.get('default') is not None:
                    param_doc += f" = {param['default']}"
                doc_parts.append(param_doc)
        
        # Return type
        if self.include_type_hints and func.get('return_annotation'):
            doc_parts.append("")
            doc_parts.append(f"**Returns:** `{func['return_annotation']}`")
        
        # Decorators
        if func.get('decorators'):
            doc_parts.append("")
            doc_parts.append("**Decorators:** " + ", ".join(f"`@{dec}`" for dec in func['decorators']))
        
        # Complexity metrics
        if self.include_complexity and func.get('complexity'):
            doc_parts.append("")
            doc_parts.append("**Complexity Metrics:**")
            complexity = func['complexity']
            doc_parts.append(f"- Cyclomatic Complexity: {complexity.get('cyclomatic_complexity', 'N/A')}")
            doc_parts.append(f"- Cognitive Complexity: {complexity.get('cognitive_complexity', 'N/A')}")
            doc_parts.append(f"- Max Nesting Depth: {complexity.get('nesting_depth', 'N/A')}")
            doc_parts.append(f"- Lines of Code: {func.get('lines_of_code', 'N/A')}")
        
        # Additional info
        if func.get('is_async'):
            doc_parts.append("")
            doc_parts.append("*This is an async function*")
        
        return "\n".join(doc_parts)
    
    def _format_class(self, cls: Dict[str, Any]) -> str:
        """Format class documentation."""
        doc_parts = []
        
        # Class header
        class_signature = f"class {cls['name']}"
        if cls.get('bases'):
            class_signature += f"({', '.join(cls['bases'])})"
        
        doc_parts.append(f"### `{class_signature}`")
        doc_parts.append(f"*Line {cls['line_number']}*")
        
        # Docstring
        if self.include_docstrings and cls.get('docstring'):
            doc_parts.append("")
            doc_parts.append("**Description:**")
            doc_parts.append(cls['docstring'])
        
        # Decorators
        if cls.get('decorators'):
            doc_parts.append("")
            doc_parts.append("**Decorators:** " + ", ".join(f"`@{dec}`" for dec in cls['decorators']))
        
        # Attributes
        if cls.get('attributes'):
            doc_parts.append("")
            doc_parts.append("**Attributes:**")
            for attr in cls['attributes']:
                attr_doc = f"- `{attr['name']}`"
                if self.include_type_hints and attr.get('annotation'):
                    attr_doc += f": {attr['annotation']}"
                doc_parts.append(attr_doc)
        
        # Methods
        if cls.get('methods'):
            doc_parts.append("")
            doc_parts.append("**Methods:**")
            for method in cls['methods']:
                method_signature = self._build_signature(method)
                doc_parts.append(f"- `{method_signature}`")
                if self.include_docstrings and method.get('docstring'):
                    # Add first line of method docstring
                    first_line = method['docstring'].split('\n')[0].strip()
                    if first_line:
                        doc_parts.append(f"  - {first_line}")
        
        # Class metrics
        if self.include_complexity:
            doc_parts.append("")
            doc_parts.append("**Class Metrics:**")
            doc_parts.append(f"- Number of Methods: {len(cls.get('methods', []))}")
            doc_parts.append(f"- Number of Attributes: {len(cls.get('attributes', []))}")
            doc_parts.append(f"- Lines of Code: {cls.get('lines_of_code', 'N/A')}")
        
        return "\n".join(doc_parts)
    
    def _build_signature(self, func: Dict[str, Any]) -> str:
        """Build function signature string."""
        name = func['name']
        params = []
        
        for param in func.get('parameters', []):
            param_str = param['name']
            if self.include_type_hints and param.get('annotation'):
                param_str += f": {param['annotation']}"
            if param.get('default') is not None:
                param_str += f" = {param['default']}"
            params.append(param_str)
        
        signature = f"{name}({', '.join(params)})"
        
        if self.include_type_hints and func.get('return_annotation'):
            signature += f" -> {func['return_annotation']}"
        
        return signature
