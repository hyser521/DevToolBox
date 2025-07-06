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
        
        # Human-readable summary
        summary = self._generate_function_summary(func)
        if summary:
            doc_parts.append("")
            doc_parts.append("**Summary:**")
            doc_parts.append(summary)
        
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
                doc_parts.append("")
                doc_parts.append(self._format_method_detailed(method))
        
        # Class metrics
        if self.include_complexity:
            doc_parts.append("")
            doc_parts.append("**Class Metrics:**")
            doc_parts.append(f"- Number of Methods: {len(cls.get('methods', []))}")
            doc_parts.append(f"- Number of Attributes: {len(cls.get('attributes', []))}")
            doc_parts.append(f"- Lines of Code: {cls.get('lines_of_code', 'N/A')}")
        
        return "\n".join(doc_parts)
    
    def _generate_function_summary(self, func: Dict[str, Any]) -> str:
        """Generate a human-readable summary for a function or method."""
        name = func['name']
        params = func.get('parameters', [])
        return_type = func.get('return_annotation')
        complexity = func.get('complexity', {})
        
        # Start building the summary
        summary_parts = []
        
        # Basic function description
        if name.startswith('__') and name.endswith('__'):
            if name == '__init__':
                summary_parts.append("Creates a new instance of the class")
            elif name == '__str__':
                summary_parts.append("Returns a string representation of the object")
            elif name == '__repr__':
                summary_parts.append("Returns a detailed string representation for debugging")
            elif name == '__len__':
                summary_parts.append("Returns the length or size of the object")
            elif name == '__call__':
                summary_parts.append("Makes the object callable like a function")
            else:
                summary_parts.append(f"Special method {name}")
        elif name.startswith('_'):
            summary_parts.append("Private helper method")
        else:
            # Analyze function name for common patterns
            name_lower = name.lower()
            if name_lower.startswith(('get', 'fetch', 'retrieve', 'find')):
                summary_parts.append("Retrieves or fetches data")
            elif name_lower.startswith(('set', 'update', 'modify', 'change')):
                summary_parts.append("Updates or modifies data")
            elif name_lower.startswith(('create', 'make', 'build', 'generate')):
                summary_parts.append("Creates or generates new data")
            elif name_lower.startswith(('delete', 'remove', 'clear')):
                summary_parts.append("Removes or deletes data")
            elif name_lower.startswith(('save', 'store', 'write')):
                summary_parts.append("Saves or stores data")
            elif name_lower.startswith(('load', 'read', 'open')):
                summary_parts.append("Loads or reads data")
            elif name_lower.startswith(('check', 'verify', 'validate')):
                summary_parts.append("Validates or checks conditions")
            elif name_lower.startswith(('calculate', 'compute', 'process')):
                summary_parts.append("Performs calculations or processing")
            elif name_lower.startswith(('format', 'convert', 'transform')):
                summary_parts.append("Formats or transforms data")
            elif name_lower.startswith(('is_', 'has_', 'can_')):
                summary_parts.append("Returns a boolean result based on conditions")
            else:
                summary_parts.append("Performs a specific operation")
        
        # Add parameter information
        non_self_params = [p for p in params if p['name'] not in ['self', 'cls']]
        if non_self_params:
            param_count = len(non_self_params)
            required_params = [p for p in non_self_params if p.get('default') is None and not p['name'].startswith('*')]
            optional_params = [p for p in non_self_params if p.get('default') is not None]
            
            if param_count == 1:
                summary_parts.append("with 1 parameter")
            elif param_count > 1:
                summary_parts.append(f"with {param_count} parameters")
            
            if required_params and optional_params:
                summary_parts.append(f"({len(required_params)} required, {len(optional_params)} optional)")
            elif optional_params:
                summary_parts.append(f"(all {len(optional_params)} optional)")
        else:
            summary_parts.append("with no parameters")
        
        # Add return type information
        if return_type and return_type.lower() != 'none':
            if return_type.lower() in ['str', 'string']:
                summary_parts.append("and returns text")
            elif return_type.lower() in ['int', 'integer', 'float', 'number']:
                summary_parts.append("and returns a number")
            elif return_type.lower() in ['bool', 'boolean']:
                summary_parts.append("and returns True or False")
            elif return_type.lower() in ['list', 'tuple', 'set']:
                summary_parts.append("and returns a collection")
            elif return_type.lower() in ['dict', 'dictionary']:
                summary_parts.append("and returns a dictionary")
            else:
                summary_parts.append(f"and returns {return_type}")
        elif return_type and return_type.lower() == 'none':
            summary_parts.append("without returning a value")
        
        # Add complexity insight
        cyclomatic = complexity.get('cyclomatic_complexity', 0)
        if cyclomatic > 10:
            summary_parts.append("(complex logic)")
        elif cyclomatic > 5:
            summary_parts.append("(moderate complexity)")
        elif cyclomatic > 1:
            summary_parts.append("(simple logic)")
        
        # Join the parts into a readable sentence
        if len(summary_parts) > 1:
            summary = summary_parts[0] + " " + " ".join(summary_parts[1:])
        else:
            summary = summary_parts[0] if summary_parts else "Function performs an operation"
        
        # Capitalize first letter and ensure it ends with a period
        summary = summary[0].upper() + summary[1:] if summary else ""
        if summary and not summary.endswith('.'):
            summary += '.'
        
        return summary
    
    def _format_method_detailed(self, method: Dict[str, Any]) -> str:
        """Format detailed method documentation within a class."""
        doc_parts = []
        
        # Method signature
        signature = self._build_signature(method)
        doc_parts.append(f"#### `{signature}`")
        
        # Location info
        doc_parts.append(f"*Line {method['line_number']}*")
        
        # Human-readable summary
        summary = self._generate_function_summary(method)
        if summary:
            doc_parts.append("")
            doc_parts.append("**Summary:**")
            doc_parts.append(summary)
        
        # Method purpose from docstring
        if self.include_docstrings and method.get('docstring'):
            doc_parts.append("")
            doc_parts.append("**Purpose:**")
            
            # Extract the main purpose (first paragraph of docstring)
            docstring_lines = method['docstring'].strip().split('\n')
            purpose_lines = []
            for line in docstring_lines:
                line = line.strip()
                if not line:  # Empty line indicates end of purpose section
                    break
                purpose_lines.append(line)
            
            if purpose_lines:
                doc_parts.append(' '.join(purpose_lines))
            
            # Add full docstring if it contains Args/Returns sections
            if any(keyword in method['docstring'].lower() for keyword in ['args:', 'arguments:', 'returns:', 'return:']):
                doc_parts.append("")
                doc_parts.append("**Full Documentation:**")
                doc_parts.append("```")
                doc_parts.append(method['docstring'])
                doc_parts.append("```")
        
        # Parameters
        if method.get('parameters'):
            doc_parts.append("")
            doc_parts.append("**Parameters:**")
            for param in method['parameters']:
                param_doc = f"- `{param['name']}`"
                if self.include_type_hints and param.get('annotation'):
                    param_doc += f": {param['annotation']}"
                if param.get('default') is not None:
                    param_doc += f" = {param['default']}"
                doc_parts.append(param_doc)
        
        # Return type
        if self.include_type_hints and method.get('return_annotation'):
            doc_parts.append("")
            doc_parts.append(f"**Returns:** `{method['return_annotation']}`")
        
        # Decorators
        if method.get('decorators'):
            doc_parts.append("")
            doc_parts.append("**Decorators:** " + ", ".join(f"`@{dec}`" for dec in method['decorators']))
        
        # Complexity metrics for methods
        if self.include_complexity and method.get('complexity'):
            doc_parts.append("")
            doc_parts.append("**Complexity Metrics:**")
            complexity = method['complexity']
            doc_parts.append(f"- Cyclomatic Complexity: {complexity.get('cyclomatic_complexity', 'N/A')}")
            doc_parts.append(f"- Cognitive Complexity: {complexity.get('cognitive_complexity', 'N/A')}")
            doc_parts.append(f"- Max Nesting Depth: {complexity.get('nesting_depth', 'N/A')}")
            doc_parts.append(f"- Lines of Code: {method.get('lines_of_code', 'N/A')}")
        
        # Method type info
        if method.get('is_async'):
            doc_parts.append("")
            doc_parts.append("*This is an async method*")
        
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
