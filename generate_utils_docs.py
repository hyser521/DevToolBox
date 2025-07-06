#!/usr/bin/env python3
"""
Script to generate comprehensive documentation for the utils package.
"""

import os
from utils.ast_parser import PythonASTParser
from utils.doc_generator import DocumentationGenerator
from utils.ai_enhancer import AIDocumentationEnhancer
from utils.pattern_analyzer import CodePatternAnalyzer

def generate_module_documentation():
    """Generate comprehensive documentation for all utils modules."""
    
    # Initialize components
    parser = PythonASTParser()
    doc_gen = DocumentationGenerator()
    
    # Module information
    modules_info = {
        'ast_parser.py': {
            'title': 'AST Parser',
            'purpose': 'Core Python code parsing and metadata extraction using Abstract Syntax Tree (AST) analysis',
            'features': [
                'Extracts function and class metadata',
                'Analyzes import statements and dependencies', 
                'Calculates complexity metrics',
                'Identifies top-level vs nested functions',
                'Parses type annotations and decorators'
            ]
        },
        'complexity_analyzer.py': {
            'title': 'Complexity Analyzer',
            'purpose': 'Advanced code complexity metrics calculation and analysis',
            'features': [
                'McCabe Cyclomatic Complexity calculation',
                'Cognitive Complexity assessment',
                'Nesting depth analysis',
                'Branch and loop counting',
                'Decision point identification'
            ]
        },
        'doc_generator.py': {
            'title': 'Documentation Generator',
            'purpose': 'Intelligent documentation formatting and generation with human-readable summaries',
            'features': [
                'Template-based documentation creation',
                'Human-readable function summaries',
                'Pattern recognition for function purposes',
                'Configurable output options',
                'Multi-format documentation support'
            ]
        },
        'export_handler.py': {
            'title': 'Export Handler',
            'purpose': 'Multi-format documentation export and conversion utilities',
            'features': [
                'Markdown to HTML conversion',
                'JSON data serialization',
                'CSS-styled HTML output',
                'Clean, professional formatting',
                'Cross-platform compatibility'
            ]
        },
        'database.py': {
            'title': 'Database Manager',
            'purpose': 'PostgreSQL integration for persistent storage of documentation and analysis results',
            'features': [
                'SQLAlchemy ORM models',
                'Analysis result persistence',
                'Search and retrieval functionality',
                'Project organization support',
                'Statistics and analytics tracking'
            ]
        },
        'ai_enhancer.py': {
            'title': 'AI Documentation Enhancer',
            'purpose': 'OpenAI GPT-4o powered intelligent code analysis and documentation enhancement',
            'features': [
                'AI-generated docstrings',
                'Code quality assessment',
                'Intelligent improvement suggestions',
                'Contextual code explanations',
                'Advanced pattern recognition'
            ]
        },
        'pattern_analyzer.py': {
            'title': 'Code Pattern Analyzer',
            'purpose': 'Advanced pattern recognition for design patterns, code smells, and architectural analysis',
            'features': [
                'Design pattern detection',
                'Code smell identification',
                'Architecture quality assessment',
                'Naming convention analysis',
                'Complexity distribution analysis'
            ]
        },
        'github_integration.py': {
            'title': 'GitHub Integration',
            'purpose': 'Automated GitHub repository monitoring and workflow integration',
            'features': [
                'Pull request analysis',
                'Repository monitoring',
                'Automated issue creation',
                'Webhook support',
                'Continuous documentation workflows'
            ]
        }
    }
    
    # Start building comprehensive documentation
    doc_content = []
    doc_content.append("# Utils Package Documentation")
    doc_content.append("*Generated automatically by AI-Powered Python Documentation Tool*")
    doc_content.append("")
    doc_content.append("## Overview")
    doc_content.append("")
    doc_content.append("The `utils` package contains the core functionality modules for the AI-Powered Python Documentation Tool. This package implements intelligent code analysis, documentation generation, pattern recognition, and GitHub integration capabilities.")
    doc_content.append("")
    doc_content.append("## Package Architecture")
    doc_content.append("")
    doc_content.append("The utils package follows a modular architecture with eight specialized components:")
    doc_content.append("")
    doc_content.append("- **Core Analysis**: `ast_parser.py`, `complexity_analyzer.py`")
    doc_content.append("- **Documentation Engine**: `doc_generator.py`, `export_handler.py`")
    doc_content.append("- **Data Persistence**: `database.py`")
    doc_content.append("- **AI Enhancement**: `ai_enhancer.py`, `pattern_analyzer.py`")
    doc_content.append("- **External Integration**: `github_integration.py`")
    doc_content.append("")
    
    # Process each module
    for module_file, info in modules_info.items():
        module_path = f"utils/{module_file}"
        
        if os.path.exists(module_path):
            print(f"Processing {module_file}...")
            
            # Read source code
            with open(module_path, 'r', encoding='utf-8') as f:
                source_code = f.read()
            
            # Parse the code
            parsed_data = parser.parse_code(source_code)
            
            # Add module documentation
            doc_content.append(f"## {info['title']} (`{module_file}`)")
            doc_content.append("")
            doc_content.append(f"**Purpose**: {info['purpose']}")
            doc_content.append("")
            
            # Add statistics
            total_functions = len(parsed_data['functions'])
            total_classes = len(parsed_data['classes'])
            total_methods = sum(len(cls['methods']) for cls in parsed_data['classes'])
            
            doc_content.append("**Statistics**:")
            doc_content.append(f"- Functions: {total_functions}")
            doc_content.append(f"- Classes: {total_classes}")
            doc_content.append(f"- Methods: {total_methods}")
            doc_content.append("")
            
            # Add key features
            doc_content.append("**Key Features**:")
            for feature in info['features']:
                doc_content.append(f"- {feature}")
            doc_content.append("")
            
            # Document classes
            if parsed_data['classes']:
                for cls in parsed_data['classes']:
                    doc_content.append(f"### Class: `{cls['name']}`")
                    doc_content.append("")
                    
                    if cls.get('docstring'):
                        doc_content.append(f"**Description**: {cls['docstring']}")
                        doc_content.append("")
                    
                    if cls.get('base_classes'):
                        doc_content.append(f"**Inherits from**: {', '.join(cls['base_classes'])}")
                        doc_content.append("")
                    
                    if cls['methods']:
                        doc_content.append(f"**Methods** ({len(cls['methods'])} total):")
                        doc_content.append("")
                        
                        # Group methods by type
                        public_methods = [m for m in cls['methods'] if not m['name'].startswith('_')]
                        private_methods = [m for m in cls['methods'] if m['name'].startswith('_') and not m['name'].startswith('__')]
                        special_methods = [m for m in cls['methods'] if m['name'].startswith('__')]
                        
                        if special_methods:
                            doc_content.append("**Special Methods**:")
                            for method in special_methods:
                                summary = doc_gen._generate_function_summary(method)
                                params = len([p for p in method.get('parameters', []) if p['name'] not in ['self', 'cls']])
                                doc_content.append(f"- `{method['name']}({params} params)`: {summary}")
                            doc_content.append("")
                        
                        if public_methods:
                            doc_content.append("**Public Methods**:")
                            for method in public_methods:
                                summary = doc_gen._generate_function_summary(method)
                                params = len([p for p in method.get('parameters', []) if p['name'] not in ['self', 'cls']])
                                complexity = method.get('complexity', {}).get('cyclomatic_complexity', 0)
                                complexity_indicator = ""
                                if complexity > 7:
                                    complexity_indicator = " ⚠️ Complex"
                                elif complexity > 3:
                                    complexity_indicator = " 🔸 Moderate"
                                doc_content.append(f"- `{method['name']}({params} params)`: {summary}{complexity_indicator}")
                            doc_content.append("")
                        
                        if private_methods:
                            doc_content.append("**Private Methods**:")
                            for method in private_methods:
                                summary = doc_gen._generate_function_summary(method)
                                params = len([p for p in method.get('parameters', []) if p['name'] not in ['self', 'cls']])
                                doc_content.append(f"- `{method['name']}({params} params)`: {summary}")
                            doc_content.append("")
            
            # Document standalone functions
            if parsed_data['functions']:
                doc_content.append("### Standalone Functions")
                doc_content.append("")
                for func in parsed_data['functions']:
                    summary = doc_gen._generate_function_summary(func)
                    params = len(func.get('parameters', []))
                    doc_content.append(f"- `{func['name']}({params} params)`: {summary}")
                doc_content.append("")
            
            doc_content.append("---")
            doc_content.append("")
    
    # Add usage examples and best practices
    doc_content.append("## Usage Examples")
    doc_content.append("")
    doc_content.append("### Basic Code Analysis")
    doc_content.append("```python")
    doc_content.append("from utils.ast_parser import PythonASTParser")
    doc_content.append("from utils.doc_generator import DocumentationGenerator")
    doc_content.append("")
    doc_content.append("# Parse Python code")
    doc_content.append("parser = PythonASTParser()")
    doc_content.append("parsed_data = parser.parse_code(source_code)")
    doc_content.append("")
    doc_content.append("# Generate documentation")
    doc_content.append("doc_gen = DocumentationGenerator()")
    doc_content.append("documentation = doc_gen.generate_documentation(parsed_data)")
    doc_content.append("```")
    doc_content.append("")
    
    doc_content.append("### AI-Enhanced Analysis")
    doc_content.append("```python")
    doc_content.append("from utils.ai_enhancer import AIDocumentationEnhancer")
    doc_content.append("from utils.pattern_analyzer import CodePatternAnalyzer")
    doc_content.append("")
    doc_content.append("# AI-powered analysis")
    doc_content.append("ai_enhancer = AIDocumentationEnhancer()")
    doc_content.append("quality_analysis = ai_enhancer.analyze_code_quality(parsed_data)")
    doc_content.append("")
    doc_content.append("# Pattern analysis")
    doc_content.append("pattern_analyzer = CodePatternAnalyzer()")
    doc_content.append("patterns = pattern_analyzer.analyze_patterns(parsed_data)")
    doc_content.append("```")
    doc_content.append("")
    
    doc_content.append("### GitHub Integration")
    doc_content.append("```python")
    doc_content.append("from utils.github_integration import GitHubIntegration")
    doc_content.append("")
    doc_content.append("# Connect to repository")
    doc_content.append("github = GitHubIntegration(github_token)")
    doc_content.append("github.connect_repository('owner/repo')")
    doc_content.append("")
    doc_content.append("# Analyze pull request")
    doc_content.append("pr_analysis = github.analyze_pull_request(123)")
    doc_content.append("```")
    doc_content.append("")
    
    # Write the complete documentation
    with open('UTILS_DOCUMENTATION.md', 'w', encoding='utf-8') as f:
        f.write('\n'.join(doc_content))
    
    print("✅ Comprehensive utils documentation generated!")
    print(f"📄 Documentation saved to UTILS_DOCUMENTATION.md")
    print(f"📊 Total lines: {len(doc_content)}")

if __name__ == "__main__":
    generate_module_documentation()