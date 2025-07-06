# Python Documentation Tool

A Streamlit-based Python documentation tool that automatically extracts function and class metadata from Python code and generates comprehensive documentation with complexity analysis.

## Features

- **AST-based Code Analysis**: Extracts detailed metadata from Python source code
- **Comprehensive Documentation**: Generates formatted documentation with function signatures, parameters, and return types
- **Complexity Metrics**: Calculates cyclomatic complexity, cognitive complexity, and nesting depth
- **Multiple Export Formats**: Supports Markdown, HTML, and JSON output
- **Database Integration**: PostgreSQL storage for documentation history and search
- **Interactive Web Interface**: User-friendly Streamlit interface with file upload and code paste options

## Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd python-documentation-tool
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up PostgreSQL database (optional):
```bash
export DATABASE_URL="postgresql://username:password@host:port/database"
```

## Usage

1. Start the application:
```bash
streamlit run app.py --server.port 5000
```

2. Open your browser and navigate to `http://localhost:5000`

3. Upload a Python file or paste your code in the text area

4. Configure analysis options in the sidebar:
   - Include complexity metrics
   - Include type hints
   - Include docstrings

5. Choose export format (Markdown, HTML, or JSON)

6. View generated documentation and download or save to database

## Project Structure

```
├── app.py                      # Main Streamlit application
├── utils/
│   ├── ast_parser.py          # Python AST parsing and metadata extraction
│   ├── complexity_analyzer.py # Code complexity metrics calculation
│   ├── doc_generator.py       # Documentation formatting and generation
│   ├── export_handler.py      # Multi-format export functionality
│   └── database.py            # PostgreSQL integration and data persistence
├── .streamlit/
│   └── config.toml            # Streamlit configuration
├── requirements.txt           # Python dependencies
└── README.md                  # This file
```

## Architecture

### Core Components

1. **AST Parser** (`utils/ast_parser.py`)
   - Extracts function and class metadata using Python's AST module
   - Identifies parameters, return types, decorators, and docstrings
   - Calculates lines of code and integrates with complexity analyzer

2. **Complexity Analyzer** (`utils/complexity_analyzer.py`)
   - Calculates McCabe cyclomatic complexity
   - Computes cognitive complexity with nesting considerations
   - Measures maximum nesting depth and counts branches/loops

3. **Documentation Generator** (`utils/doc_generator.py`)
   - Creates formatted documentation from parsed metadata
   - Supports configurable output options
   - Generates comprehensive method documentation with purpose descriptions

4. **Export Handler** (`utils/export_handler.py`)
   - Converts documentation to multiple formats
   - Provides styled HTML output with CSS
   - Handles JSON serialization of metadata

5. **Database Manager** (`utils/database.py`)
   - PostgreSQL integration for persistent storage
   - Search functionality by filename and content
   - Analytics and usage statistics

### Features

- **Method Purpose Documentation**: Detailed documentation for each method including purpose, parameters, return types, and complexity metrics
- **Database History**: Save and retrieve previous analyses with search functionality
- **Duplicate Prevention**: Prevents saving duplicate entries when loading from database
- **File Upload Support**: Automatically captures uploaded filenames for better organization
- **Real-time Analysis**: Instant documentation generation as you type or upload

## Configuration

### Streamlit Configuration

The application uses the following Streamlit configuration (`.streamlit/config.toml`):

```toml
[server]
headless = true
address = "0.0.0.0"
port = 5000
```

### Database Configuration

Set the `DATABASE_URL` environment variable to enable database features:

```bash
export DATABASE_URL="postgresql://user:password@host:port/database"
```

## Dependencies

- **streamlit**: Web application framework
- **sqlalchemy**: Database ORM
- **psycopg2-binary**: PostgreSQL adapter

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is open source and available under the MIT License.

## Development

### Local Development

1. Install dependencies: `pip install -r requirements.txt`
2. Run the application: `streamlit run app.py --server.port 5000`
3. Access at `http://localhost:5000`

### Database Setup

For local development with database features:

1. Install PostgreSQL
2. Create a database
3. Set the `DATABASE_URL` environment variable
4. The application will automatically create the required tables

## Changelog

- **July 06, 2025**: Initial release with core documentation features
- **July 06, 2025**: Added PostgreSQL database integration
- **July 06, 2025**: Enhanced method documentation with detailed purpose descriptions
- **July 06, 2025**: Added search functionality and duplicate prevention