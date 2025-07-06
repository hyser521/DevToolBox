import ast
from typing import Dict, Any

class ComplexityAnalyzer:
    """Analyzer for calculating code complexity metrics."""
    
    def calculate_complexity(self, node: ast.AST) -> Dict[str, Any]:
        """
        Calculate various complexity metrics for a function or method.
        
        Args:
            node: AST node to analyze
            
        Returns:
            Dictionary containing complexity metrics
        """
        return {
            'cyclomatic_complexity': self._cyclomatic_complexity(node),
            'cognitive_complexity': self._cognitive_complexity(node),
            'nesting_depth': self._max_nesting_depth(node),
            'num_branches': self._count_branches(node),
            'num_loops': self._count_loops(node)
        }
    
    def _cyclomatic_complexity(self, node: ast.AST) -> int:
        """
        Calculate McCabe cyclomatic complexity.
        
        Cyclomatic complexity = E - N + 2P
        For a single function: complexity = number of decision points + 1
        """
        complexity = 1  # Base complexity
        
        for child in ast.walk(node):
            # Decision points that increase complexity
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                complexity += 1
            elif isinstance(child, ast.ExceptHandler):
                complexity += 1
            elif isinstance(child, (ast.With, ast.AsyncWith)):
                complexity += 1
            elif isinstance(child, ast.Assert):
                complexity += 1
            elif isinstance(child, ast.BoolOp):
                # Each additional condition in and/or
                complexity += len(child.values) - 1
            elif isinstance(child, ast.ListComp):
                complexity += 1
            elif isinstance(child, ast.DictComp):
                complexity += 1
            elif isinstance(child, ast.SetComp):
                complexity += 1
            elif isinstance(child, ast.GeneratorExp):
                complexity += 1
        
        return complexity
    
    def _cognitive_complexity(self, node: ast.AST) -> int:
        """
        Calculate cognitive complexity (similar to cyclomatic but considers nesting).
        """
        return self._cognitive_complexity_recursive(node, 0)
    
    def _cognitive_complexity_recursive(self, node: ast.AST, nesting_level: int) -> int:
        """Recursively calculate cognitive complexity considering nesting."""
        complexity = 0
        
        for child in ast.iter_child_nodes(node):
            increment = 0
            new_nesting = nesting_level
            
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor)):
                increment = 1 + nesting_level
                new_nesting = nesting_level + 1
            elif isinstance(child, ast.ExceptHandler):
                increment = 1 + nesting_level
                new_nesting = nesting_level + 1
            elif isinstance(child, (ast.With, ast.AsyncWith)):
                increment = 1 + nesting_level
                new_nesting = nesting_level + 1
            elif isinstance(child, ast.BoolOp):
                increment = len(child.values) - 1
            elif isinstance(child, (ast.ListComp, ast.DictComp, ast.SetComp, ast.GeneratorExp)):
                increment = 1
            elif isinstance(child, ast.Lambda):
                increment = 1
            
            complexity += increment
            complexity += self._cognitive_complexity_recursive(child, new_nesting)
        
        return complexity
    
    def _max_nesting_depth(self, node: ast.AST) -> int:
        """Calculate maximum nesting depth."""
        return self._nesting_depth_recursive(node, 0)
    
    def _nesting_depth_recursive(self, node: ast.AST, current_depth: int) -> int:
        """Recursively calculate nesting depth."""
        max_depth = current_depth
        
        for child in ast.iter_child_nodes(node):
            new_depth = current_depth
            
            if isinstance(child, (ast.If, ast.While, ast.For, ast.AsyncFor, 
                                ast.With, ast.AsyncWith, ast.Try, ast.FunctionDef, 
                                ast.AsyncFunctionDef, ast.ClassDef)):
                new_depth = current_depth + 1
            
            child_max_depth = self._nesting_depth_recursive(child, new_depth)
            max_depth = max(max_depth, child_max_depth)
        
        return max_depth
    
    def _count_branches(self, node: ast.AST) -> int:
        """Count the number of branching statements."""
        count = 0
        
        for child in ast.walk(node):
            if isinstance(child, (ast.If, ast.For, ast.While, ast.AsyncFor, 
                                ast.Try, ast.With, ast.AsyncWith)):
                count += 1
            elif isinstance(child, ast.ExceptHandler):
                count += 1
        
        return count
    
    def _count_loops(self, node: ast.AST) -> int:
        """Count the number of loop statements."""
        count = 0
        
        for child in ast.walk(node):
            if isinstance(child, (ast.For, ast.While, ast.AsyncFor)):
                count += 1
            elif isinstance(child, (ast.ListComp, ast.DictComp, ast.SetComp, ast.GeneratorExp)):
                count += 1
        
        return count
