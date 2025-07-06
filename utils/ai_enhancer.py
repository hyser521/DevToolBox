"""
AI-Enhanced Documentation Generator for intelligent code analysis and documentation.
"""

import json
import os
from typing import Dict, Any, List, Optional
from openai import OpenAI

class AIDocumentationEnhancer:
    """AI-powered documentation enhancement using OpenAI's GPT models."""
    
    def __init__(self):
        """Initialize the AI enhancer with OpenAI API."""
        self.client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
        # the newest OpenAI model is "gpt-4o" which was released May 13, 2024.
        # do not change this unless explicitly requested by the user
        self.model = "gpt-4o"
    
    def generate_intelligent_docstring(self, function_info: Dict[str, Any]) -> str:
        """
        Generate intelligent docstring for a function using AI.
        
        Args:
            function_info: Dictionary containing function metadata
            
        Returns:
            AI-generated docstring
        """
        try:
            # Prepare function context
            name = function_info.get('name', 'unknown')
            params = function_info.get('parameters', [])
            return_type = function_info.get('return_annotation', 'None')
            complexity = function_info.get('complexity', {})
            
            # Build parameter info
            param_info = []
            for param in params:
                if param['name'] not in ['self', 'cls']:
                    param_str = f"{param['name']}: {param.get('annotation', 'Any')}"
                    if param.get('default') is not None:
                        param_str += f" = {param['default']}"
                    param_info.append(param_str)
            
            prompt = f"""
            Generate a comprehensive docstring for this Python function:
            
            Function: {name}
            Parameters: {', '.join(param_info) if param_info else 'None'}
            Returns: {return_type}
            Complexity: {complexity.get('cyclomatic_complexity', 'N/A')}
            
            Please provide:
            1. A clear, concise description of what the function does
            2. Detailed parameter descriptions
            3. Return value explanation
            4. Any important notes about usage or behavior
            5. Example usage if applicable
            
            Format as a proper Python docstring with Args, Returns, and Example sections.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are an expert Python documentation writer. Generate clear, helpful docstrings."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=500,
                temperature=0.3
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"Error generating AI docstring: {str(e)}"
    
    def analyze_code_quality(self, parsed_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze code quality and provide AI-powered suggestions.
        
        Args:
            parsed_data: Dictionary containing parsed code metadata
            
        Returns:
            Dictionary with quality analysis and suggestions
        """
        try:
            # Prepare code summary
            functions = parsed_data.get('functions', [])
            classes = parsed_data.get('classes', [])
            
            # Calculate overall complexity
            total_complexity = 0
            complex_functions = []
            
            for func in functions:
                complexity = func.get('complexity', {}).get('cyclomatic_complexity', 0)
                total_complexity += complexity
                if complexity > 10:
                    complex_functions.append(func['name'])
            
            for cls in classes:
                for method in cls.get('methods', []):
                    complexity = method.get('complexity', {}).get('cyclomatic_complexity', 0)
                    total_complexity += complexity
                    if complexity > 10:
                        complex_functions.append(f"{cls['name']}.{method['name']}")
            
            prompt = f"""
            Analyze this Python code structure and provide quality insights:
            
            Code Structure:
            - Functions: {len(functions)}
            - Classes: {len(classes)}
            - Total Methods: {sum(len(cls.get('methods', [])) for cls in classes)}
            - Average Complexity: {total_complexity / max(len(functions) + sum(len(cls.get('methods', [])) for cls in classes), 1):.2f}
            - Complex Functions: {', '.join(complex_functions) if complex_functions else 'None'}
            
            Please provide:
            1. Overall code quality assessment (Good/Fair/Needs Improvement)
            2. Top 3 specific recommendations for improvement
            3. Maintainability score (1-10)
            4. Any architectural patterns detected
            
            Respond in JSON format with keys: quality_score, recommendations, maintainability_score, patterns_detected
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a senior code architect. Analyze code quality and provide actionable recommendations."},
                    {"role": "user", "content": prompt}
                ],
                response_format={"type": "json_object"},
                max_tokens=400,
                temperature=0.2
            )
            
            return json.loads(response.choices[0].message.content)
            
        except Exception as e:
            return {
                "quality_score": "Error",
                "recommendations": [f"Error analyzing code: {str(e)}"],
                "maintainability_score": 0,
                "patterns_detected": []
            }
    
    def generate_contextual_explanation(self, function_info: Dict[str, Any], context: str = "") -> str:
        """
        Generate contextual explanation for complex functions.
        
        Args:
            function_info: Dictionary containing function metadata
            context: Additional context about the codebase
            
        Returns:
            Human-readable explanation
        """
        try:
            name = function_info.get('name', 'unknown')
            complexity = function_info.get('complexity', {})
            cyclomatic = complexity.get('cyclomatic_complexity', 0)
            cognitive = complexity.get('cognitive_complexity', 0)
            
            if cyclomatic <= 3:
                return f"The function '{name}' has simple logic and is easy to understand."
            
            prompt = f"""
            Explain this Python function in simple terms for a non-technical audience:
            
            Function: {name}
            Cyclomatic Complexity: {cyclomatic}
            Cognitive Complexity: {cognitive}
            Context: {context}
            
            Please provide:
            1. What the function does in everyday language
            2. Why it might be complex (if applicable)
            3. How it fits into the larger system
            4. Any potential concerns or benefits
            
            Keep the explanation conversational and accessible.
            """
            
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a technical translator who explains complex code in simple, everyday language."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=300,
                temperature=0.4
            )
            
            return response.choices[0].message.content.strip()
            
        except Exception as e:
            return f"Error generating explanation: {str(e)}"
    
    def suggest_improvements(self, function_info: Dict[str, Any]) -> List[str]:
        """
        Suggest specific improvements for a function.
        
        Args:
            function_info: Dictionary containing function metadata
            
        Returns:
            List of improvement suggestions
        """
        try:
            name = function_info.get('name', 'unknown')
            params = function_info.get('parameters', [])
            complexity = function_info.get('complexity', {})
            lines_of_code = function_info.get('lines_of_code', 0)
            
            # Quick analysis for simple cases
            suggestions = []
            
            if complexity.get('cyclomatic_complexity', 0) > 10:
                suggestions.append("Consider breaking down this function into smaller, more focused functions")
            
            if lines_of_code > 50:
                suggestions.append("This function is quite long - consider splitting it for better readability")
            
            if len(params) > 5:
                suggestions.append("This function has many parameters - consider using a configuration object")
            
            # If complexity is high, get AI suggestions
            if complexity.get('cyclomatic_complexity', 0) > 5:
                prompt = f"""
                Suggest 2-3 specific improvements for this Python function:
                
                Function: {name}
                Parameters: {len(params)}
                Cyclomatic Complexity: {complexity.get('cyclomatic_complexity', 0)}
                Lines of Code: {lines_of_code}
                
                Focus on:
                1. Code structure improvements
                2. Performance optimizations
                3. Maintainability enhancements
                
                Provide specific, actionable suggestions.
                """
                
                response = self.client.chat.completions.create(
                    model=self.model,
                    messages=[
                        {"role": "system", "content": "You are a senior developer providing code improvement suggestions."},
                        {"role": "user", "content": prompt}
                    ],
                    max_tokens=200,
                    temperature=0.3
                )
                
                ai_suggestions = response.choices[0].message.content.strip().split('\n')
                suggestions.extend([s.strip('- ').strip() for s in ai_suggestions if s.strip()])
            
            return suggestions[:5]  # Limit to 5 suggestions
            
        except Exception as e:
            return [f"Error generating suggestions: {str(e)}"]