import streamlit as st
import ast
import traceback
import os
from io import StringIO
from utils.ast_parser import PythonASTParser
from utils.doc_generator import DocumentationGenerator
from utils.export_handler import ExportHandler
from utils.database import DatabaseManager
from utils.ai_enhancer import AIDocumentationEnhancer
from utils.pattern_analyzer import CodePatternAnalyzer
from utils.github_integration import GitHubIntegration

def main():
    st.set_page_config(
        page_title="AI-Powered Python Documentation Tool",
        page_icon="🤖",
        layout="wide"
    )
    
    st.title("🤖 AI-Powered Python Documentation Tool")
    st.markdown("Intelligent code analysis with AI enhancement, pattern recognition, and GitHub integration")
    
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
        
        # Search functionality (available even if database is not available, but will show error)
        if db_available:
            st.divider()
            st.subheader("🔍 Search Analyses")
            search_query = st.text_input("Search by filename or content:", placeholder="e.g., calculator.py")
            
            if search_query.strip():
                try:
                    search_results = db.search_analyses(search_query, limit=10)
                    st.write(f"Found {len(search_results)} results:")
                    
                    for analysis in search_results:
                        with st.expander(f"🔍 {analysis.filename or 'Untitled'} - {analysis.created_at.strftime('%m/%d %H:%M')}"):
                            st.write(f"**ID:** {analysis.id}")
                            st.write(f"**Filename:** {analysis.filename or 'No filename'}")
                            st.write(f"**Format:** {analysis.export_format}")
                            st.write(f"**Functions:** {len(analysis.parsed_data.get('functions', []))}")
                            st.write(f"**Classes:** {len(analysis.parsed_data.get('classes', []))}")
                            
                            # Show a preview of the source code
                            code_preview = analysis.source_code[:200] + "..." if len(analysis.source_code) > 200 else analysis.source_code
                            st.code(code_preview, language="python")
                            
                            if st.button(f"Load Analysis {analysis.id}", key=f"search_load_{analysis.id}"):
                                st.session_state.loaded_analysis = analysis
                                st.rerun()
                except Exception as e:
                    st.error(f"Search error: {str(e)}")
            
            # Recent analyses
            st.subheader("📋 Recent Analyses")
            col_refresh, col_clear = st.columns(2)
            with col_refresh:
                if st.button("Refresh"):
                    st.rerun()
            with col_clear:
                if st.button("Clear Search"):
                    st.rerun()
            
            try:
                recent_analyses = db.get_recent_analyses(5)
                for analysis in recent_analyses:
                    with st.expander(f"📄 {analysis.filename or 'Untitled'} - {analysis.created_at.strftime('%m/%d %H:%M')}"):
                        st.write(f"**ID:** {analysis.id}")
                        st.write(f"**Filename:** {analysis.filename or 'No filename'}")
                        st.write(f"**Format:** {analysis.export_format}")
                        st.write(f"**Functions:** {len(analysis.parsed_data.get('functions', []))}")
                        st.write(f"**Classes:** {len(analysis.parsed_data.get('classes', []))}")
                        if st.button(f"Load Analysis {analysis.id}", key=f"recent_load_{analysis.id}"):
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
            ["Upload File", "Paste Code", "GitHub Repository"]
        )
        
        python_code = ""
        uploaded_filename = None
        is_loaded_from_db = False
        loaded_analysis_id = None
        
        # Check if we have a loaded analysis from session state
        if 'loaded_analysis' in st.session_state and st.session_state.loaded_analysis:
            analysis = st.session_state.loaded_analysis
            st.info(f"📂 Loaded analysis from database (ID: {analysis.id})")
            python_code = analysis.source_code
            uploaded_filename = analysis.filename
            is_loaded_from_db = True
            loaded_analysis_id = analysis.id
            
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
                    uploaded_filename = uploaded_file.name
                    st.success(f"File '{uploaded_file.name}' uploaded successfully!")
                except Exception as e:
                    st.error(f"Error reading file: {str(e)}")
        
        elif input_method == "Paste Code":
            python_code = st.text_area(
                "Paste your Python code here:",
                height=400,
                placeholder="def example_function(param1: str, param2: int = 10) -> str:\n    \"\"\"\n    Example function docstring.\n    \n    Args:\n        param1: Description of param1\n        param2: Description of param2\n    \n    Returns:\n        Description of return value\n    \"\"\"\n    return f'{param1}_{param2}'"
            )
        
        else:  # GitHub Repository
            st.subheader("📡 GitHub Repository Analysis")
            github_url = st.text_input(
                "GitHub Repository URL:",
                placeholder="https://github.com/owner/repository",
                help="Enter a public GitHub repository URL to analyze and document all Python files"
            )
            
            if github_url:
                # Extract repo name from URL
                try:
                    repo_name = github_url.replace("https://github.com/", "").replace("http://github.com/", "")
                    if repo_name.endswith('.git'):
                        repo_name = repo_name[:-4]
                    
                    st.info(f"Repository: {repo_name}")
                    
                    analyze_col, cancel_col = st.columns([3, 1])
                    
                    with analyze_col:
                        analyze_button = st.button("🔍 Analyze Repository", type="primary", key="analyze_repo")
                    
                    with cancel_col:
                        if 'github_operation_active' in st.session_state and st.session_state.github_operation_active:
                            if st.button("🛑 Cancel", type="secondary", key="cancel_repo"):
                                if 'github_integration' in st.session_state:
                                    st.session_state.github_integration.cancel_operation()
                                st.session_state.github_operation_active = False
                                st.warning("Operation cancelled")
                                st.rerun()
                    
                    if analyze_button:
                        # Initialize progress tracking
                        progress_placeholder = st.empty()
                        status_placeholder = st.empty()
                        
                        try:
                            # Initialize GitHub integration
                            github_integration = GitHubIntegration()
                            st.session_state.github_integration = github_integration
                            st.session_state.github_operation_active = True
                            
                            def progress_callback(message):
                                progress_placeholder.info(f"📡 {message}")
                            
                            # Connect to repository
                            if github_integration.connect_repository(repo_name):
                                status_placeholder.success(f"Successfully connected to {repo_name}")
                                
                                # Generate repository analysis report with progress and cancellation
                                repo_report = github_integration.generate_repository_report(
                                    progress_callback=progress_callback,
                                    max_files=15  # Limit to reduce API calls
                                )
                                
                                # Clear progress indicators
                                progress_placeholder.empty()
                                st.session_state.github_operation_active = False
                                
                                # Check if operation was cancelled
                                if repo_report.get('cancelled'):
                                    status_placeholder.warning(repo_report.get('message', 'Operation was cancelled'))
                                elif repo_report.get('error'):
                                    status_placeholder.error(f"Error: {repo_report['error']}")
                                else:
                                    # Store repository analysis in session state
                                    st.session_state.repo_analysis = repo_report
                                    st.session_state.repo_name = repo_name
                                    
                                    # Display repository summary
                                    st.subheader("📊 Repository Summary")
                                    col1, col2, col3, col4 = st.columns(4)
                                    
                                    with col1:
                                        st.metric("Python Files", len(repo_report.get('python_files', [])))
                                    with col2:
                                        st.metric("Total Functions", repo_report.get('total_functions', 0))
                                    with col3:
                                        st.metric("Total Classes", repo_report.get('total_classes', 0))
                                    with col4:
                                        api_calls = repo_report.get('api_calls_made', 0)
                                        st.metric("API Calls", api_calls, help="Number of GitHub API calls made (optimized to reduce rate limiting)")
                                    
                                    # Show file selection
                                    python_files = repo_report.get('python_files', [])
                                    if python_files:
                                        st.subheader("📁 Select Files to Document")
                                        selected_files = st.multiselect(
                                            "Choose Python files:",
                                            python_files,
                                            default=python_files[:5] if len(python_files) <= 5 else python_files[:3],
                                            help="Select files to include in documentation"
                                        )
                                        
                                        if selected_files and st.button("📖 Generate Documentation"):
                                            # Process selected files
                                            combined_code = ""
                                            combined_filename = f"{repo_name.replace('/', '_')}_analysis"
                                            
                                            for file_path in selected_files:
                                                file_content = repo_report['file_contents'].get(file_path, '')
                                                combined_code += f"# File: {file_path}\n{file_content}\n\n"
                                            
                                            python_code = combined_code
                                            uploaded_filename = combined_filename
                                            
                                            st.success(f"✓ Generated documentation for {len(selected_files)} files from {repo_name}")
                                            st.info("📥 Scroll down to see the generated documentation and download options")
                                    else:
                                        st.warning("No Python files found in this repository")
                            else:
                                status_placeholder.error("Failed to connect to repository. Please check the URL and try again.")
                                
                        except Exception as e:
                            st.session_state.github_operation_active = False
                            progress_placeholder.empty()
                            status_placeholder.error(f"Error analyzing repository: {str(e)}")
                            st.info("💡 Tip: Make sure the repository is public and the URL is correct")
                                
                except Exception as e:
                    st.error(f"Invalid GitHub URL: {str(e)}")
                    st.info("Please enter a valid GitHub repository URL (e.g., https://github.com/owner/repo)")
        
        if python_code:
            # Display syntax highlighted code
            st.subheader("Code Preview")
            st.code(python_code, language="python")
    
    with col2:
        st.header("Generated Documentation")
        
        if python_code:
            # Show source indicator for GitHub repositories
            if input_method == "GitHub Repository" and uploaded_filename:
                st.info(f"📁 Documentation for: {uploaded_filename}")
                st.caption("Download options will appear below after generation")
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
                    
                    # Save to database if enabled and not loaded from database
                    if db_available and save_to_db and not is_loaded_from_db:
                        try:
                            analysis_options = {
                                'complexity': include_complexity,
                                'type_hints': include_type_hints,
                                'docstrings': include_docstrings
                            }
                            
                            # Use uploaded filename if available, otherwise use manual input
                            save_filename = uploaded_filename or (filename_input if filename_input.strip() else None)
                            
                            analysis_id = db.save_analysis(
                                source_code=python_code,
                                parsed_data=parsed_data,
                                documentation=documentation,
                                filename=save_filename,
                                export_format=export_format.lower(),
                                options=analysis_options
                            )
                            
                            st.success(f"✅ Analysis saved to database (ID: {analysis_id})")
                        except Exception as e:
                            st.error(f"Failed to save to database: {str(e)}")
                    elif is_loaded_from_db:
                        st.info(f"📂 Viewing existing analysis (ID: {loaded_analysis_id}) - not saving duplicate")
                    
                    # Export functionality
                    st.subheader("Export Documentation")
                    
                    export_handler = ExportHandler()
                    
                    # Create appropriate filename based on source
                    base_filename = uploaded_filename or "documentation"
                    if base_filename.endswith('.py'):
                        base_filename = base_filename[:-3]  # Remove .py extension
                    
                    if export_format == "Markdown":
                        file_content = documentation
                        file_name = f"{base_filename}.md"
                        mime_type = "text/markdown"
                    elif export_format == "HTML":
                        file_content = export_handler.to_html(documentation)
                        file_name = f"{base_filename}.html"
                        mime_type = "text/html"
                    else:  # JSON
                        file_content = export_handler.to_json(parsed_data)
                        file_name = f"{base_filename}.json"
                        mime_type = "application/json"
                    
                    col_dl1, col_dl2 = st.columns(2)
                    with col_dl1:
                        download_label = f"📥 Download {export_format}"
                        if input_method == "GitHub Repository":
                            download_label = f"📥 Download Repository Docs ({export_format})"
                        
                        st.download_button(
                            label=download_label,
                            data=file_content,
                            file_name=file_name,
                            mime=mime_type,
                            type="primary"
                        )
                    
                    # Show database save info
                    if db_available:
                        with col_dl2:
                            if is_loaded_from_db:
                                st.info("Loaded from database")
                            elif save_to_db:
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
    
    # Agentic Features Section
    if python_code:
        st.markdown("---")
        st.header("🤖 AI-Powered Enhancements")
        
        # Create columns for agentic features
        ai_col1, ai_col2 = st.columns(2)
        
        with ai_col1:
            st.subheader("🧠 AI Analysis")
            
            try:
                # Check if OpenAI API key is available
                if os.environ.get("OPENAI_API_KEY"):
                    if st.button("🚀 Generate AI Insights", type="primary"):
                        with st.spinner("AI is analyzing your code..."):
                            ai_enhancer = AIDocumentationEnhancer()
                            
                            # Generate AI quality analysis
                            quality_analysis = ai_enhancer.analyze_code_quality(parsed_data)
                            
                            st.subheader("📊 Code Quality Assessment")
                            st.json(quality_analysis)
                            
                            # Generate AI suggestions for complex functions
                            st.subheader("💡 AI Improvement Suggestions")
                            for func in parsed_data['functions']:
                                if func.get('complexity', {}).get('cyclomatic_complexity', 0) > 5:
                                    with st.expander(f"Suggestions for {func['name']}"):
                                        suggestions = ai_enhancer.suggest_improvements(func)
                                        for suggestion in suggestions:
                                            st.write(f"• {suggestion}")
                            
                            for cls in parsed_data['classes']:
                                for method in cls['methods']:
                                    if method.get('complexity', {}).get('cyclomatic_complexity', 0) > 5:
                                        with st.expander(f"Suggestions for {cls['name']}.{method['name']}"):
                                            suggestions = ai_enhancer.suggest_improvements(method)
                                            for suggestion in suggestions:
                                                st.write(f"• {suggestion}")
                else:
                    st.info("🔑 OpenAI API key needed for AI features. Add it in Replit Secrets.")
                    
            except Exception as e:
                st.error(f"AI Analysis error: {str(e)}")
        
        with ai_col2:
            st.subheader("🔍 Pattern Analysis")
            
            if st.button("🎯 Analyze Code Patterns", type="secondary"):
                with st.spinner("Analyzing code patterns..."):
                    try:
                        pattern_analyzer = CodePatternAnalyzer()
                        pattern_analysis = pattern_analyzer.analyze_patterns(parsed_data)
                        
                        # Display design patterns
                        if pattern_analysis['design_patterns']:
                            st.subheader("🏗️ Design Patterns Detected")
                            for pattern, classes in pattern_analysis['design_patterns'].items():
                                st.write(f"**{pattern.title()}**: {', '.join(classes)}")
                        
                        # Display code smells
                        if pattern_analysis['code_smells']:
                            st.subheader("⚠️ Code Smells Detected")
                            for smell, items in pattern_analysis['code_smells'].items():
                                if items:
                                    st.write(f"**{smell.replace('_', ' ').title()}**: {', '.join(items)}")
                        
                        # Display recommendations
                        if pattern_analysis['recommendations']:
                            st.subheader("📋 Recommendations")
                            for rec in pattern_analysis['recommendations']:
                                st.write(f"• {rec}")
                        
                        # Display architecture insights
                        arch = pattern_analysis['architectural_insights']
                        st.subheader("🏛️ Architecture Analysis")
                        st.write(f"**Separation of Concerns**: {arch['separation_of_concerns']}")
                        st.write(f"**Cohesion Level**: {arch['cohesion_level']}")
                        st.write(f"**Abstraction Level**: {arch['abstraction_level']}")
                        
                    except Exception as e:
                        st.error(f"Pattern Analysis error: {str(e)}")
        
        # GitHub Integration Section
        st.markdown("---")
        st.header("🔗 GitHub Integration")
        
        github_col1, github_col2 = st.columns(2)
        
        with github_col1:
            st.subheader("📁 Repository Connection")
            repo_name = st.text_input("Repository (owner/repo):", placeholder="username/repository-name")
            github_token = st.text_input("GitHub Token (optional):", type="password", 
                                       help="Required for private repos and advanced features")
            
            if st.button("🔌 Connect to Repository"):
                if repo_name:
                    try:
                        github_integration = GitHubIntegration(github_token)
                        if github_integration.connect_repository(repo_name):
                            st.success(f"✅ Connected to {repo_name}")
                            st.session_state['github_repo'] = repo_name
                            st.session_state['github_integration'] = github_integration
                        else:
                            st.error("❌ Failed to connect. Check repository name and token.")
                    except Exception as e:
                        st.error(f"Connection error: {str(e)}")
                else:
                    st.warning("Please enter a repository name")
        
        with github_col2:
            st.subheader("📊 Repository Analysis")
            
            if 'github_integration' in st.session_state:
                if st.button("📈 Generate Repository Report"):
                    with st.spinner("Analyzing repository..."):
                        try:
                            report = st.session_state['github_integration'].generate_repository_report()
                            
                            if 'error' not in report:
                                st.subheader("📋 Repository Statistics")
                                stats = report['repository_stats']
                                col1, col2, col3 = st.columns(3)
                                with col1:
                                    st.metric("Stars", stats['stars'])
                                with col2:
                                    st.metric("Forks", stats['forks'])
                                with col3:
                                    st.metric("Open Issues", stats['open_issues'])
                                
                                st.subheader("💻 Recent Activity")
                                for activity in report['commit_analysis']['recent_activity'][:5]:
                                    st.write(f"**{activity['author']}**: {activity['message']}")
                            else:
                                st.error(report['error'])
                        except Exception as e:
                            st.error(f"Repository analysis error: {str(e)}")
            else:
                st.info("Connect to a repository first to enable analysis features")
        
        # PR Analysis Section
        if 'github_integration' in st.session_state:
            st.markdown("---")
            st.subheader("🔄 Pull Request Analysis")
            
            pr_number = st.number_input("PR Number:", min_value=1, step=1)
            
            if st.button("🔍 Analyze Pull Request") and pr_number:
                with st.spinner("Analyzing pull request..."):
                    try:
                        pr_analysis = st.session_state['github_integration'].analyze_pull_request(int(pr_number))
                        
                        if 'error' not in pr_analysis:
                            st.write(f"**Title**: {pr_analysis['title']}")
                            st.write(f"**Author**: {pr_analysis['author']}")
                            
                            if pr_analysis['documentation_needed']:
                                st.warning("📝 Documentation needed for: " + ", ".join(pr_analysis['documentation_needed']))
                            
                            if pr_analysis['complexity_alerts']:
                                st.error("⚠️ High complexity detected in: " + ", ".join(pr_analysis['complexity_alerts']))
                            
                            if pr_analysis['suggestions']:
                                st.subheader("💡 Suggestions")
                                for suggestion in pr_analysis['suggestions']:
                                    st.write(f"• {suggestion}")
                            
                            # Automated workflow option
                            if st.button("🤖 Run Automated Workflow"):
                                workflow_result = st.session_state['github_integration'].automated_documentation_workflow(int(pr_number))
                                if 'error' not in workflow_result:
                                    st.success("✅ Automated workflow completed")
                                    for action in workflow_result['actions_taken']:
                                        st.write(f"• {action}")
                                else:
                                    st.error(workflow_result['error'])
                        else:
                            st.error(pr_analysis['error'])
                    except Exception as e:
                        st.error(f"PR analysis error: {str(e)}")

if __name__ == "__main__":
    main()
