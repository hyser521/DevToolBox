"""
Automated GitHub Integration for continuous documentation and analysis.
"""

import os
import json
import time
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime
from github import Github
from github.Repository import Repository
from github.PullRequest import PullRequest
from github.Issue import Issue
import threading

class GitHubIntegration:
    """Automated GitHub integration for documentation and analysis."""
    
    def __init__(self, github_token: Optional[str] = None):
        """Initialize GitHub integration."""
        self.token = github_token or os.environ.get("GITHUB_TOKEN")
        # Create client - works without token for public repos
        self.client = Github(self.token) if self.token else Github()
        self.repo = None
        self._cancel_flag = False
        self._operation_thread = None
        self._api_call_count = 0
        self._last_api_call = 0
        self._rate_limit_delay = 1.0  # seconds between API calls
    
    def cancel_operation(self):
        """Cancel any ongoing GitHub API operation."""
        self._cancel_flag = True
        if self._operation_thread and self._operation_thread.is_alive():
            # Thread will check cancel flag and stop naturally
            pass
    
    def reset_cancel_flag(self):
        """Reset the cancellation flag for new operations."""
        self._cancel_flag = False
    
    def _throttle_api_call(self):
        """Add delay between API calls to avoid rate limiting."""
        current_time = time.time()
        if self._last_api_call > 0:
            time_since_last_call = current_time - self._last_api_call
            if time_since_last_call < self._rate_limit_delay:
                time.sleep(self._rate_limit_delay - time_since_last_call)
        
        self._last_api_call = time.time()
        self._api_call_count += 1
    
    def _check_cancellation(self) -> bool:
        """Check if operation should be cancelled."""
        return self._cancel_flag
        
    def connect_repository(self, repo_name: str) -> bool:
        """
        Connect to a GitHub repository.
        
        Args:
            repo_name: Repository name in format 'owner/repo'
            
        Returns:
            True if connection successful, False otherwise
        """
        try:
            if not self.client:
                raise Exception("GitHub client not initialized")
            
            self._throttle_api_call()
            self.repo = self.client.get_repo(repo_name)
            return True
            
        except Exception as e:
            error_msg = str(e).lower()
            if "rate limit" in error_msg or "403" in error_msg:
                raise Exception("GitHub API rate limit exceeded. Please wait a few minutes or provide a GitHub token for higher limits.")
            elif "not found" in error_msg or "404" in error_msg:
                raise Exception(f"Repository '{repo_name}' not found. Please check the repository name.")
            elif "forbidden" in error_msg:
                raise Exception("Access forbidden. The repository may be private or require authentication.")
            else:
                raise Exception(f"Error connecting to repository: {str(e)}")
            return False
    
    def analyze_pull_request(self, pr_number: int) -> Dict[str, Any]:
        """
        Analyze a pull request for documentation needs.
        
        Args:
            pr_number: Pull request number
            
        Returns:
            Analysis results with documentation suggestions
        """
        try:
            if not self.repo:
                return {"error": "No repository connected"}
            
            pr = self.repo.get_pull(pr_number)
            files = pr.get_files()
            
            analysis = {
                "pr_number": pr_number,
                "title": pr.title,
                "author": pr.user.login,
                "files_analyzed": [],
                "documentation_needed": [],
                "complexity_alerts": [],
                "suggestions": []
            }
            
            # Analyze each Python file in the PR
            for file in files:
                if file.filename.endswith('.py'):
                    file_analysis = self._analyze_file_changes(file)
                    analysis["files_analyzed"].append(file_analysis)
                    
                    # Check if documentation is needed
                    if file_analysis.get("new_functions", 0) > 0:
                        analysis["documentation_needed"].append(file.filename)
                    
                    # Check for complexity alerts
                    if file_analysis.get("high_complexity", False):
                        analysis["complexity_alerts"].append(file.filename)
            
            # Generate suggestions
            analysis["suggestions"] = self._generate_pr_suggestions(analysis)
            
            return analysis
            
        except Exception as e:
            return {"error": f"Error analyzing PR: {str(e)}"}
    
    def _analyze_file_changes(self, file) -> Dict[str, Any]:
        """Analyze changes in a single file."""
        try:
            # Get file content
            content = file.patch or ""
            
            # Count new functions/methods
            new_functions = content.count("def ")
            new_classes = content.count("class ")
            
            # Simple complexity check (count of conditions)
            complexity_indicators = (
                content.count("if ") + 
                content.count("for ") + 
                content.count("while ") + 
                content.count("except ")
            )
            
            return {
                "filename": file.filename,
                "additions": file.additions,
                "deletions": file.deletions,
                "changes": file.changes,
                "new_functions": new_functions,
                "new_classes": new_classes,
                "complexity_score": complexity_indicators,
                "high_complexity": complexity_indicators > 10
            }
            
        except Exception as e:
            return {"filename": file.filename, "error": str(e)}
    
    def _generate_pr_suggestions(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate suggestions based on PR analysis."""
        suggestions = []
        
        if analysis.get("documentation_needed"):
            suggestions.append("📝 Consider adding documentation for new functions and classes")
        
        if analysis.get("complexity_alerts"):
            suggestions.append("⚠️ High complexity detected - consider refactoring for maintainability")
        
        total_files = len(analysis.get("files_analyzed", []))
        if total_files > 5:
            suggestions.append("📊 Large PR - consider breaking into smaller, focused changes")
        
        return suggestions
    
    def create_documentation_issue(self, title: str, body: str, labels: List[str] = None) -> Optional[int]:
        """
        Create a GitHub issue for documentation needs.
        
        Args:
            title: Issue title
            body: Issue description
            labels: List of labels to add
            
        Returns:
            Issue number if successful, None otherwise
        """
        try:
            if not self.repo:
                return None
            
            labels = labels or ["documentation", "automated"]
            issue = self.repo.create_issue(
                title=title,
                body=body,
                labels=labels
            )
            
            return issue.number
            
        except Exception as e:
            print(f"Error creating issue: {e}")
            return None
    
    def add_pr_comment(self, pr_number: int, comment: str) -> bool:
        """
        Add a comment to a pull request.
        
        Args:
            pr_number: Pull request number
            comment: Comment text
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.repo:
                return False
            
            pr = self.repo.get_pull(pr_number)
            pr.create_issue_comment(comment)
            
            return True
            
        except Exception as e:
            print(f"Error adding PR comment: {e}")
            return False
    
    def monitor_repository(self, check_interval: int = 300) -> Dict[str, Any]:
        """
        Monitor repository for new changes and documentation needs.
        
        Args:
            check_interval: Check interval in seconds
            
        Returns:
            Monitoring results
        """
        try:
            if not self.repo:
                return {"error": "No repository connected"}
            
            # Get recent pull requests
            prs = self.repo.get_pulls(state='open', sort='updated', direction='desc')
            
            monitoring_results = {
                "timestamp": datetime.now().isoformat(),
                "open_prs": [],
                "documentation_alerts": [],
                "complexity_alerts": []
            }
            
            # Analyze recent PRs
            for pr in prs[:10]:  # Check last 10 PRs
                pr_analysis = self.analyze_pull_request(pr.number)
                
                monitoring_results["open_prs"].append({
                    "number": pr.number,
                    "title": pr.title,
                    "author": pr.user.login,
                    "updated": pr.updated_at.isoformat()
                })
                
                if pr_analysis.get("documentation_needed"):
                    monitoring_results["documentation_alerts"].append(pr.number)
                
                if pr_analysis.get("complexity_alerts"):
                    monitoring_results["complexity_alerts"].append(pr.number)
            
            return monitoring_results
            
        except Exception as e:
            return {"error": f"Error monitoring repository: {str(e)}"}
    
    def generate_repository_report(self, progress_callback: Optional[Callable] = None, max_files: int = 20) -> Dict[str, Any]:
        """
        Generate a comprehensive repository analysis report with cancellation support.
        
        Args:
            progress_callback: Optional callback function to report progress
            max_files: Maximum number of Python files to analyze
            
        Returns:
            Repository analysis report
        """
        try:
            # Reset cancellation flag for new operation
            self.reset_cancel_flag()
            
            if not self.repo:
                return {"error": "No repository connected"}
            
            if progress_callback:
                progress_callback("Getting repository information...")
            
            # Get repository statistics with throttling
            self._throttle_api_call()
            if self._check_cancellation():
                return {"cancelled": True, "message": "Operation cancelled by user"}
                
            stats = {
                "repository": self.repo.full_name,
                "language": self.repo.language,
                "stars": self.repo.stargazers_count,
                "forks": self.repo.forks_count,
                "open_issues": self.repo.open_issues_count,
                "last_updated": self.repo.updated_at.isoformat()
            }
            
            # Find Python files with limited scope
            python_files = []
            file_contents = {}
            total_functions = 0
            total_classes = 0
            
            try:
                if progress_callback:
                    progress_callback("Scanning for Python files...")
                
                # Get repository contents with throttling
                self._throttle_api_call()
                if self._check_cancellation():
                    return {"cancelled": True, "message": "Operation cancelled by user"}
                    
                contents = self.repo.get_contents("")
                python_files_data = self._get_python_files_recursive(contents, max_files, progress_callback)
                
                if self._check_cancellation():
                    return {"cancelled": True, "message": "Operation cancelled by user"}
                
                if progress_callback:
                    progress_callback(f"Analyzing {len(python_files_data)} Python files...")
                
                # Extract Python files and analyze them
                from .ast_parser import PythonASTParser
                parser = PythonASTParser()
                
                files_processed = 0
                for file_path, file_content in python_files_data.items():
                    if self._check_cancellation():
                        return {"cancelled": True, "message": "Operation cancelled by user"}
                        
                    if file_path.endswith('.py'):
                        python_files.append(file_path)
                        file_contents[file_path] = file_content
                        
                        # Parse Python file for statistics
                        try:
                            parsed_data = parser.parse_code(file_content)
                            total_functions += len(parsed_data.get('functions', []))
                            total_classes += len(parsed_data.get('classes', []))
                        except Exception:
                            # Skip files that can't be parsed
                            pass
                    
                    files_processed += 1
                    if progress_callback and files_processed % 5 == 0:
                        progress_callback(f"Processed {files_processed}/{len(python_files_data)} files...")
                            
            except Exception as e:
                return {"error": f"Error accessing repository contents: {str(e)}"}
            
            # Skip commit analysis to reduce API calls and improve performance
            commit_analysis = {
                "skipped": True,
                "reason": "Optimized for faster loading and reduced API calls"
            }
            
            if progress_callback:
                progress_callback("Analysis complete!")
            
            return {
                "repository_stats": stats,
                "python_files": python_files,
                "file_contents": file_contents,
                "total_functions": total_functions,
                "total_classes": total_classes,
                "commit_analysis": commit_analysis,
                "api_calls_made": self._api_call_count,
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"error": f"Error generating repository report: {str(e)}"}
    
    def _get_python_files_recursive(self, contents, max_files=50, progress_callback: Optional[Callable] = None) -> Dict[str, str]:
        """
        Recursively get Python files from repository contents with cancellation support.
        
        Args:
            contents: Repository contents from GitHub API
            max_files: Maximum number of files to process
            progress_callback: Optional callback for progress updates
            
        Returns:
            Dictionary mapping file paths to file contents
        """
        python_files = {}
        files_processed = 0
        
        try:
            for content_file in contents:
                if self._check_cancellation():
                    break
                    
                if files_processed >= max_files:
                    break
                    
                if content_file.type == "dir":
                    # Skip common directories that rarely contain useful Python files
                    skip_dirs = {'.git', '__pycache__', '.pytest_cache', 'node_modules', 
                               '.venv', 'venv', 'env', '.env', 'dist', 'build'}
                    if content_file.name in skip_dirs:
                        continue
                        
                    # Recursively process directories
                    try:
                        if progress_callback:
                            progress_callback(f"Scanning directory: {content_file.path}")
                            
                        self._throttle_api_call()
                        if self._check_cancellation():
                            break
                            
                        sub_contents = self.repo.get_contents(content_file.path)
                        sub_files = self._get_python_files_recursive(
                            sub_contents, 
                            max_files - files_processed,
                            progress_callback
                        )
                        python_files.update(sub_files)
                        files_processed += len(sub_files)
                    except Exception:
                        # Skip directories that can't be accessed
                        continue
                        
                elif content_file.name.endswith('.py'):
                    try:
                        if progress_callback:
                            progress_callback(f"Loading: {content_file.path}")
                            
                        # Get file content with throttling
                        self._throttle_api_call()
                        if self._check_cancellation():
                            break
                            
                        file_content = content_file.decoded_content.decode('utf-8')
                        python_files[content_file.path] = file_content
                        files_processed += 1
                    except Exception:
                        # Skip files that can't be decoded
                        continue
                        
        except Exception:
            # Return what we have so far if there's an error
            pass
            
        return python_files
    
    def setup_webhook(self, webhook_url: str, events: List[str] = None) -> bool:
        """
        Set up a webhook for automated monitoring.
        
        Args:
            webhook_url: URL to receive webhook notifications
            events: List of events to monitor
            
        Returns:
            True if successful, False otherwise
        """
        try:
            if not self.repo:
                return False
            
            events = events or ["pull_request", "push", "issues"]
            
            webhook_config = {
                "url": webhook_url,
                "content_type": "json",
                "secret": os.environ.get("WEBHOOK_SECRET", "")
            }
            
            self.repo.create_hook(
                name="web",
                config=webhook_config,
                events=events,
                active=True
            )
            
            return True
            
        except Exception as e:
            print(f"Error setting up webhook: {e}")
            return False
    
    def automated_documentation_workflow(self, pr_number: int) -> Dict[str, Any]:
        """
        Run automated documentation workflow for a PR.
        
        Args:
            pr_number: Pull request number
            
        Returns:
            Workflow results
        """
        try:
            # Analyze the PR
            analysis = self.analyze_pull_request(pr_number)
            
            workflow_results = {
                "pr_number": pr_number,
                "analysis_completed": True,
                "actions_taken": [],
                "recommendations": []
            }
            
            # Auto-comment if documentation is needed
            if analysis.get("documentation_needed"):
                comment = self._generate_documentation_comment(analysis)
                if self.add_pr_comment(pr_number, comment):
                    workflow_results["actions_taken"].append("Added documentation reminder comment")
            
            # Create issue for high complexity
            if analysis.get("complexity_alerts"):
                issue_title = f"High complexity detected in PR #{pr_number}"
                issue_body = self._generate_complexity_issue_body(analysis)
                issue_number = self.create_documentation_issue(
                    issue_title, 
                    issue_body, 
                    ["complexity", "refactoring"]
                )
                if issue_number:
                    workflow_results["actions_taken"].append(f"Created issue #{issue_number} for complexity")
            
            # Generate recommendations
            workflow_results["recommendations"] = analysis.get("suggestions", [])
            
            return workflow_results
            
        except Exception as e:
            return {"error": f"Error in automated workflow: {str(e)}"}
    
    def _generate_documentation_comment(self, analysis: Dict[str, Any]) -> str:
        """Generate documentation reminder comment."""
        comment = "## 📝 Documentation Reminder\n\n"
        comment += "This PR introduces new code that may need documentation:\n\n"
        
        for file in analysis.get("documentation_needed", []):
            comment += f"- `{file}`\n"
        
        comment += "\n**Please consider:**\n"
        comment += "- Adding docstrings to new functions and classes\n"
        comment += "- Updating README if public API changes\n"
        comment += "- Adding inline comments for complex logic\n\n"
        comment += "*This comment was generated automatically by the documentation tool.*"
        
        return comment
    
    def _generate_complexity_issue_body(self, analysis: Dict[str, Any]) -> str:
        """Generate issue body for complexity alerts."""
        body = "## ⚠️ High Complexity Alert\n\n"
        body += f"High complexity detected in PR #{analysis['pr_number']}:\n\n"
        
        for file in analysis.get("complexity_alerts", []):
            body += f"- `{file}`\n"
        
        body += "\n**Recommendations:**\n"
        body += "- Consider breaking down complex functions\n"
        body += "- Add unit tests for complex logic\n"
        body += "- Review for potential refactoring opportunities\n\n"
        body += "*This issue was created automatically by the documentation tool.*"
        
        return body