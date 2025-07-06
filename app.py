import streamlit as st
import ast
import traceback
from io import StringIO
from utils.ast_parser import PythonASTParser
from utils.doc_generator import DocumentationGenerator
from utils.export_handler import ExportHandler
from utils.database import DatabaseManager

def main():
    st.set_page_config(
        page_title="Python Documentation Tool",
        page_icon="📚",
        layout="wide"
    )
    
    st.title("📚 Python Documentation Tool")
    st.markdown("Automatically extract function metadata and generate comprehensive documentation")
    
    # Initialize database
    try:
        db = DatabaseManager()
        db_available = True
    except Exception as e:
        st.error(f"Database connection failed: {str(e)}")
        db_available = False
        db = None
    
    # Sidebar for options and database features
    with st.sidebar:
        st.header("Options")
        
        # Export format selection
        export_format = st.selectbox(
            "Export Format",
            ["Markdown", "HTML", "JSON"],
            index=0
        )
        
        # Analysis options
        st.subheader("Analysis Options")
        include_complexity = st.checkbox("Include Complexity Metrics", value=True)
        include_type_hints = st.checkbox("Include Type Hints", value=True)
        include_docstrings = st.checkbox("Include Docstrings", value=True)
        
        # Database features
        if db_available:
            st.divider()
            st.subheader("📁 Documentation History")
            
            # Save options
            save_to_db = st.checkbox("Save analysis to database", value=True)
            filename_input = st.text_input("Filename (optional)", placeholder="e.g., my_module.py")
        else:
            save_to_db = False
            filename_input = ""
            
            # Recent analyses
            st.subheader("Recent Analyses")
            if st.button("Refresh History"):
                st.rerun()
            
            try:
                recent_analyses = db.get_recent_analyses(5)
                for analysis in recent_analyses:
                    with st.expander(f"{analysis.filename or 'Untitled'} - {analysis.created_at.strftime('%m/%d %H:%M')}"):
                        st.write(f"**ID:** {analysis.id}")
                        st.write(f"**Format:** {analysis.export_format}")
                        st.write(f"**Functions:** {len(analysis.parsed_data.get('functions', []))}")
                        st.write(f"**Classes:** {len(analysis.parsed_data.get('classes', []))}")
                        if st.button(f"Load Analysis {analysis.id}", key=f"load_{analysis.id}"):
                            st.session_state.loaded_analysis = analysis
                            st.rerun()
            except Exception as e:
                st.error(f"Error loading history: {str(e)}")
            
            # Database statistics
            st.subheader("📊 Statistics")
            try:
                stats = db.get_statistics()
                col1, col2 = st.columns(2)
                with col1:
                    st.metric("Total Analyses", stats['total_analyses'])
                    st.metric("Functions Documented", stats['total_functions_documented'])
                with col2:
                    st.metric("Projects", stats['total_projects'])
                    st.metric("Classes Documented", stats['total_classes_documented'])
            except Exception as e:
                st.error(f"Error loading stats: {str(e)}")
    
    # Main content area
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.header("Input Python Code")
        
        # Input method selection
        input_method = st.radio(
            "Choose input method:",
            ["Upload File", "Paste Code"]
        )
        
        python_code = ""
        
        # Check if we have a loaded analysis from session state
        if 'loaded_analysis' in st.session_state and st.session_state.loaded_analysis:
            analysis = st.session_state.loaded_analysis
            st.info(f"📂 Loaded analysis from database (ID: {analysis.id})")
            python_code = analysis.source_code
            
            # Update options to match the loaded analysis
            if hasattr(analysis, 'complexity_included'):
                include_complexity = analysis.complexity_included
            if hasattr(analysis, 'type_hints_included'):
                include_type_hints = analysis.type_hints_included
            if hasattr(analysis, 'docstrings_included'):
                include_docstrings = analysis.docstrings_included
            if hasattr(analysis, 'export_format'):
                export_format = analysis.export_format.title()
            
            # Clear the loaded analysis
            del st.session_state.loaded_analysis
        
        elif input_method == "Upload File":
            uploaded_file = st.file_uploader(
                "Choose a Python file",
                type=['py'],
                help="Upload a .py file to analyze"
            )
            
            if uploaded_file is not None:
                try:
                    python_code = str(uploaded_file.read(), "utf-8")
                    st.success(f"File '{uploaded_file.name}' uploaded successfully!")
                except Exception as e:
                    st.error(f"Error reading file: {str(e)}")
        
        else:
            python_code = st.text_area(
                "Paste your Python code here:",
                height=400,
                placeholder="def example_function(param1: str, param2: int = 10) -> str:\n    \"\"\"\n    Example function docstring.\n    \n    Args:\n        param1: Description of param1\n        param2: Description of param2\n    \n    Returns:\n        Description of return value\n    \"\"\"\n    return f'{param1}_{param2}'"
            )
        
        if python_code:
            # Display syntax highlighted code
            st.subheader("Code Preview")
            st.code(python_code, language="python")
    
    with col2:
        st.header("Generated Documentation")
        
        if python_code:
            try:
                # Parse the Python code
                parser = PythonASTParser()
                parsed_data = parser.parse_code(python_code)
                
                if not parsed_data['functions'] and not parsed_data['classes']:
                    st.warning("No functions or classes found in the provided code.")
                else:
                    # Generate documentation
                    doc_generator = DocumentationGenerator(
                        include_complexity=include_complexity,
                        include_type_hints=include_type_hints,
                        include_docstrings=include_docstrings
                    )
                    
                    documentation = doc_generator.generate_documentation(parsed_data)
                    
                    # Display documentation
                    if export_format == "Markdown":
                        st.markdown(documentation)
                    elif export_format == "HTML":
                        st.markdown(documentation, unsafe_allow_html=True)
                    else:  # JSON
                        st.json(parsed_data)
                    
                    # Save to database if enabled
                    if db_available and save_to_db:
                        try:
                            analysis_options = {
                                'complexity': include_complexity,
                                'type_hints': include_type_hints,
                                'docstrings': include_docstrings
                            }
                            
                            analysis_id = db.save_analysis(
                                source_code=python_code,
                                parsed_data=parsed_data,
                                documentation=documentation,
                                filename=filename_input if filename_input.strip() else None,
                                export_format=export_format.lower(),
                                options=analysis_options
                            )
                            
                            st.success(f"✅ Analysis saved to database (ID: {analysis_id})")
                        except Exception as e:
                            st.error(f"Failed to save to database: {str(e)}")
                    
                    # Export functionality
                    st.subheader("Export Documentation")
                    
                    export_handler = ExportHandler()
                    
                    if export_format == "Markdown":
                        file_content = documentation
                        file_name = "documentation.md"
                        mime_type = "text/markdown"
                    elif export_format == "HTML":
                        file_content = export_handler.to_html(documentation)
                        file_name = "documentation.html"
                        mime_type = "text/html"
                    else:  # JSON
                        file_content = export_handler.to_json(parsed_data)
                        file_name = "documentation.json"
                        mime_type = "application/json"
                    
                    col_dl1, col_dl2 = st.columns(2)
                    with col_dl1:
                        st.download_button(
                            label=f"Download {export_format}",
                            data=file_content,
                            file_name=file_name,
                            mime=mime_type
                        )
                    
                    # Show database save info
                    if db_available:
                        with col_dl2:
                            if save_to_db:
                                st.info("Auto-saved to database")
                            else:
                                st.info("Database saving disabled")
                    
                    # Display analysis summary
                    st.subheader("Analysis Summary")
                    
                    total_functions = len(parsed_data['functions'])
                    total_classes = len(parsed_data['classes'])
                    total_methods = sum(len(cls['methods']) for cls in parsed_data['classes'])
                    
                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.metric("Functions", total_functions)
                    with col_b:
                        st.metric("Classes", total_classes)
                    with col_c:
                        st.metric("Methods", total_methods)
                        
            except SyntaxError as e:
                st.error(f"Syntax Error in Python code: {str(e)}")
                st.error(f"Line {e.lineno}: {e.text}")
            except Exception as e:
                st.error(f"Error analyzing code: {str(e)}")
                st.error("Traceback:")
                st.code(traceback.format_exc())

if __name__ == "__main__":
    main()
