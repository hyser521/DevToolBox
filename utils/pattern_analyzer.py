"""
Smart Code Pattern Recognition for advanced code analysis.
"""

import ast
import re
from typing import Dict, Any, List, Set, Optional
from collections import defaultdict, Counter

class CodePatternAnalyzer:
    """Advanced pattern recognition for code analysis."""
    
    def __init__(self):
        """Initialize the pattern analyzer."""
        self.design_patterns = {
            'singleton': ['__new__', '_instance', 'instance'],
            'factory': ['create', 'make', 'build', 'get_instance'],
            'observer': ['notify', 'subscribe', 'unsubscribe', 'observers'],
            'decorator': ['wrapper', 'wrap', 'decorate'],
            'strategy': ['execute', 'algorithm', 'strategy'],
            'command': ['execute', 'undo', 'command'],
            'builder': ['build', 'create', 'construct', 'builder']
        }
        
        self.code_smells = {
            'god_class': lambda cls: len(cls.get('methods', [])) > 20,
            'long_method': lambda func: func.get('lines_of_code', 0) > 30,
            'too_many_parameters': lambda func: len(func.get('parameters', [])) > 6,
            'complex_method': lambda func: func.get('complexity', {}).get('cyclomatic_complexity', 0) > 10,
            'deep_nesting': lambda func: func.get('complexity', {}).get('max_nesting_depth', 0) > 4
        }
    
    def analyze_patterns(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze code patterns and architectural decisions.
        
        Args:
            parsed_data: Dictionary containing parsed code metadata
            
        Returns:
            Dictionary with pattern analysis results
        """
        analysis = {
            'design_patterns': self._detect_design_patterns(parsed_data),
            'code_smells': self._detect_code_smells(parsed_data),
            'architectural_insights': self._analyze_architecture(parsed_data),
            'naming_conventions': self._analyze_naming_conventions(parsed_data),
            'complexity_distribution': self._analyze_complexity_distribution(parsed_data),
            'recommendations': []
        }
        
        # Generate recommendations based on patterns
        analysis['recommendations'] = self._generate_pattern_recommendations(analysis)
        
        return analysis
    
    def _detect_design_patterns(self, parsed_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Detect common design patterns in the code."""
        detected = defaultdict(list)
        
        # Analyze classes for design patterns
        for cls in parsed_data.get('classes', []):
            class_name = cls['name']
            method_names = [m['name'] for m in cls.get('methods', [])]
            
            # Check each design pattern
            for pattern, keywords in self.design_patterns.items():
                matches = 0
                for keyword in keywords:
                    if any(keyword in method.lower() for method in method_names):
                        matches += 1
                    if keyword in class_name.lower():
                        matches += 1
                
                if matches >= 2:  # Need at least 2 matches to suggest pattern
                    detected[pattern].append(class_name)
        
        return dict(detected)
    
    def _detect_code_smells(self, parsed_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Detect code smells and anti-patterns."""
        smells = defaultdict(list)
        
        # Check functions
        for func in parsed_data.get('functions', []):
            for smell_name, smell_check in self.code_smells.items():
                if smell_check(func):
                    smells[smell_name].append(func['name'])
        
        # Check class methods
        for cls in parsed_data.get('classes', []):
            # Check for god class
            if self.code_smells['god_class'](cls):
                smells['god_class'].append(cls['name'])
            
            # Check methods
            for method in cls.get('methods', []):
                for smell_name, smell_check in self.code_smells.items():
                    if smell_name != 'god_class' and smell_check(method):
                        smells[smell_name].append(f"{cls['name']}.{method['name']}")
        
        return dict(smells)
    
    def _analyze_architecture(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze architectural patterns and structure."""
        architecture = {
            'separation_of_concerns': self._check_separation_of_concerns(parsed_data),
            'cohesion_level': self._calculate_cohesion(parsed_data),
            'coupling_indicators': self._analyze_coupling(parsed_data),
            'abstraction_level': self._analyze_abstraction(parsed_data)
        }
        
        return architecture
    
    def _check_separation_of_concerns(self, parsed_data: Dict[str, Any]) -> str:
        """Check if code follows separation of concerns principle."""
        classes = parsed_data.get('classes', [])
        
        if not classes:
            return "No classes found - limited analysis"
        
        # Check for mixed responsibilities
        mixed_responsibilities = 0
        for cls in classes:
            method_names = [m['name'] for m in cls.get('methods', [])]
            
            # Check for database + UI methods in same class
            has_db_methods = any('save' in name or 'load' in name or 'database' in name.lower() 
                               for name in method_names)
            has_ui_methods = any('display' in name or 'show' in name or 'render' in name.lower() 
                              for name in method_names)
            
            if has_db_methods and has_ui_methods:
                mixed_responsibilities += 1
        
        if mixed_responsibilities == 0:
            return "Good - Clear separation of concerns"
        elif mixed_responsibilities <= len(classes) * 0.3:
            return "Fair - Some mixed responsibilities detected"
        else:
            return "Poor - Multiple classes with mixed responsibilities"
    
    def _calculate_cohesion(self, parsed_data: Dict[str, Any]) -> str:
        """Calculate cohesion level of classes."""
        classes = parsed_data.get('classes', [])
        
        if not classes:
            return "No classes to analyze"
        
        high_cohesion = 0
        for cls in classes:
            methods = cls.get('methods', [])
            if not methods:
                continue
                
            # Simple heuristic: classes with focused naming patterns have higher cohesion
            method_names = [m['name'] for m in methods]
            
            # Check for consistent naming patterns
            prefixes = [name.split('_')[0] for name in method_names if '_' in name]
            if prefixes:
                most_common_prefix = Counter(prefixes).most_common(1)[0]
                if most_common_prefix[1] >= len(methods) * 0.7:
                    high_cohesion += 1
        
        cohesion_ratio = high_cohesion / len(classes)
        
        if cohesion_ratio >= 0.7:
            return "High - Classes are well-focused"
        elif cohesion_ratio >= 0.4:
            return "Medium - Mixed cohesion levels"
        else:
            return "Low - Classes may have too many responsibilities"
    
    def _analyze_coupling(self, parsed_data: Dict[str, Any]) -> List[str]:
        """Analyze coupling indicators."""
        indicators = []
        
        # Check for excessive parameter passing
        functions = parsed_data.get('functions', [])
        classes = parsed_data.get('classes', [])
        
        high_param_count = 0
        total_functions = len(functions)
        
        for func in functions:
            if len(func.get('parameters', [])) > 5:
                high_param_count += 1
        
        for cls in classes:
            for method in cls.get('methods', []):
                total_functions += 1
                if len(method.get('parameters', [])) > 5:
                    high_param_count += 1
        
        if total_functions > 0 and high_param_count / total_functions > 0.3:
            indicators.append("High parameter coupling detected")
        
        # Check for complex inheritance
        deep_inheritance = 0
        for cls in classes:
            if len(cls.get('base_classes', [])) > 2:
                deep_inheritance += 1
        
        if deep_inheritance > 0:
            indicators.append("Complex inheritance hierarchy detected")
        
        return indicators
    
    def _analyze_abstraction(self, parsed_data: Dict[str, Any]) -> str:
        """Analyze the level of abstraction in the code."""
        classes = parsed_data.get('classes', [])
        functions = parsed_data.get('functions', [])
        
        if not classes and not functions:
            return "No code to analyze"
        
        # Count abstract methods and interfaces
        abstract_indicators = 0
        total_methods = 0
        
        for cls in classes:
            methods = cls.get('methods', [])
            total_methods += len(methods)
            
            for method in methods:
                # Check for abstract method indicators
                if (method['name'].startswith('_') and not method['name'].startswith('__') or
                    'abstract' in method['name'].lower() or
                    'interface' in method['name'].lower()):
                    abstract_indicators += 1
        
        total_methods += len(functions)
        
        if total_methods == 0:
            return "No methods to analyze"
        
        abstraction_ratio = abstract_indicators / total_methods
        
        if abstraction_ratio >= 0.3:
            return "High - Good use of abstraction"
        elif abstraction_ratio >= 0.1:
            return "Medium - Some abstraction present"
        else:
            return "Low - Mostly concrete implementations"
    
    def _analyze_naming_conventions(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze naming conventions and consistency."""
        conventions = {
            'snake_case_functions': 0,
            'camelCase_functions': 0,
            'PascalCase_classes': 0,
            'snake_case_classes': 0,
            'consistent_naming': True,
            'descriptive_names': 0
        }
        
        # Analyze function naming
        functions = parsed_data.get('functions', [])
        for func in functions:
            name = func['name']
            if '_' in name and name.islower():
                conventions['snake_case_functions'] += 1
            elif any(c.isupper() for c in name) and not name.startswith('_'):
                conventions['camelCase_functions'] += 1
            
            # Check for descriptive names (length > 3, contains verb)
            if len(name) > 3 and any(verb in name.lower() for verb in 
                                   ['get', 'set', 'create', 'update', 'delete', 'process', 'calculate']):
                conventions['descriptive_names'] += 1
        
        # Analyze class naming
        classes = parsed_data.get('classes', [])
        for cls in classes:
            name = cls['name']
            if name[0].isupper() and '_' not in name:
                conventions['PascalCase_classes'] += 1
            elif '_' in name:
                conventions['snake_case_classes'] += 1
        
        # Check for method naming consistency
        for cls in classes:
            for method in cls.get('methods', []):
                name = method['name']
                if '_' in name and name.islower():
                    conventions['snake_case_functions'] += 1
                elif any(c.isupper() for c in name) and not name.startswith('_'):
                    conventions['camelCase_functions'] += 1
                
                if len(name) > 3 and any(verb in name.lower() for verb in 
                                       ['get', 'set', 'create', 'update', 'delete', 'process', 'calculate']):
                    conventions['descriptive_names'] += 1
        
        return conventions
    
    def _analyze_complexity_distribution(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze the distribution of complexity across the codebase."""
        complexities = []
        
        # Collect complexity metrics
        for func in parsed_data.get('functions', []):
            complexity = func.get('complexity', {}).get('cyclomatic_complexity', 0)
            complexities.append(complexity)
        
        for cls in parsed_data.get('classes', []):
            for method in cls.get('methods', []):
                complexity = method.get('complexity', {}).get('cyclomatic_complexity', 0)
                complexities.append(complexity)
        
        if not complexities:
            return {'average': 0, 'max': 0, 'distribution': 'No data'}
        
        avg_complexity = sum(complexities) / len(complexities)
        max_complexity = max(complexities)
        
        # Categorize complexity distribution
        simple = sum(1 for c in complexities if c <= 3)
        moderate = sum(1 for c in complexities if 4 <= c <= 7)
        complex = sum(1 for c in complexities if c > 7)
        
        distribution = f"{simple} simple, {moderate} moderate, {complex} complex"
        
        return {
            'average': round(avg_complexity, 2),
            'max': max_complexity,
            'distribution': distribution,
            'total_functions': len(complexities)
        }
    
    def _generate_pattern_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on pattern analysis."""
        recommendations = []
        
        # Design pattern recommendations
        patterns = analysis.get('design_patterns', {})
        if not patterns:
            recommendations.append("Consider implementing design patterns for better code organization")
        
        # Code smell recommendations
        smells = analysis.get('code_smells', {})
        if 'god_class' in smells:
            recommendations.append("Break down large classes into smaller, focused classes")
        if 'long_method' in smells:
            recommendations.append("Refactor long methods into smaller, reusable functions")
        if 'too_many_parameters' in smells:
            recommendations.append("Use parameter objects or configuration classes for methods with many parameters")
        
        # Architecture recommendations
        architecture = analysis.get('architectural_insights', {})
        if architecture.get('separation_of_concerns') == 'Poor':
            recommendations.append("Improve separation of concerns by separating business logic from UI and data access")
        if architecture.get('cohesion_level') == 'Low':
            recommendations.append("Increase class cohesion by ensuring each class has a single, well-defined responsibility")
        
        # Complexity recommendations
        complexity = analysis.get('complexity_distribution', {})
        if complexity.get('average', 0) > 5:
            recommendations.append("Reduce overall complexity by simplifying complex methods")
        
        return recommendations[:5]  # Limit to top 5 recommendations