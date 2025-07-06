# Python Documentation Tool

## Overview

This is a Streamlit-based Python documentation tool that automatically extracts function and class metadata from Python code and generates comprehensive documentation. The application uses Abstract Syntax Tree (AST) parsing to analyze Python source code and provides various export formats including Markdown, HTML, and JSON.

## System Architecture

The application follows a modular architecture with clear separation of concerns:

- **Frontend**: Streamlit web interface for user interaction
- **Core Parser**: AST-based Python code analysis engine
- **Documentation Engine**: Template-based documentation generation
- **Export System**: Multi-format output handler
- **Analysis Modules**: Complexity metrics and code quality assessment
- **Database Layer**: PostgreSQL integration for storing documentation history and analytics

## Key Components

### 1. Main Application (`app.py`)
- **Purpose**: Streamlit frontend interface
- **Responsibilities**: User interaction, file upload, configuration options
- **Features**: 
  - File upload and code paste input methods
  - Export format selection (Markdown, HTML, JSON)
  - Analysis options configuration
  - Two-column layout for input/output

### 2. AST Parser (`utils/ast_parser.py`)
- **Purpose**: Python code parsing and metadata extraction
- **Technology**: Python AST (Abstract Syntax Tree)
- **Capabilities**:
  - Function and class detection
  - Import statement analysis
  - Module docstring extraction
  - Top-level vs nested function differentiation
- **Integration**: Uses ComplexityAnalyzer for code quality metrics

### 3. Complexity Analyzer (`utils/complexity_analyzer.py`)
- **Purpose**: Code complexity metrics calculation
- **Metrics Provided**:
  - McCabe Cyclomatic Complexity
  - Cognitive Complexity
  - Nesting Depth Analysis
  - Branch and Loop Counting
- **Algorithm**: AST traversal with decision point counting

### 4. Documentation Generator (`utils/doc_generator.py`)
- **Purpose**: Formatted documentation creation
- **Features**:
  - Configurable output options
  - Timestamp generation
  - Module summary creation
  - Function and class documentation formatting
- **Flexibility**: Supports optional complexity metrics, type hints, and docstrings

### 5. Export Handler (`utils/export_handler.py`)
- **Purpose**: Multi-format documentation export
- **Supported Formats**: HTML, Markdown, JSON
- **HTML Features**: Styled output with CSS, responsive design
- **Design**: Clean, professional documentation appearance

### 6. Database Manager (`utils/database.py`)
- **Purpose**: PostgreSQL integration for data persistence
- **Models**: DocumentationProject and CodeAnalysis tables
- **Features**: Save/retrieve analyses, search functionality, statistics
- **Schema**: SQLAlchemy ORM with JSON storage for parsed metadata

## Data Flow

1. **Input Stage**: User provides Python code via file upload or direct paste
2. **Parsing Stage**: AST parser extracts structural metadata and imports
3. **Analysis Stage**: Complexity analyzer calculates code quality metrics
4. **Generation Stage**: Documentation generator creates formatted output
5. **Export Stage**: Export handler converts to selected format (Markdown/HTML/JSON)

## External Dependencies

### Core Dependencies
- **Streamlit**: Web application framework for the user interface
- **Python AST**: Built-in library for code parsing and analysis

### Utility Dependencies
- **datetime**: Timestamp generation for documentation headers
- **json**: JSON export functionality
- **html**: HTML escaping and formatting
- **io.StringIO**: In-memory string operations
- **traceback**: Error handling and debugging

## Deployment Strategy

The application is designed for Replit deployment with:
- **Runtime**: Python 3.x environment
- **Interface**: Streamlit web server
- **Architecture**: Single-node application with modular utilities
- **Scalability**: Suitable for individual/team documentation tasks

## Changelog

Changelog:
- July 06, 2025. Initial setup
- July 06, 2025. Added PostgreSQL database integration for storing documentation history and analytics
- July 06, 2025. Enhanced method documentation with detailed purpose descriptions and complexity metrics
- July 06, 2025. Fixed isinstance syntax errors in complexity analyzer
- July 06, 2025. Added human-readable summaries for all methods and functions with intelligent pattern recognition
- July 06, 2025. Implemented three major agentic features:
  * AI-Enhanced Documentation Generator (OpenAI GPT-4o integration)
  * Smart Code Pattern Recognition (design patterns, code smells, architecture analysis)
  * Automated GitHub Integration (PR analysis, repository monitoring, automated workflows)

## User Preferences

Preferred communication style: Simple, everyday language.