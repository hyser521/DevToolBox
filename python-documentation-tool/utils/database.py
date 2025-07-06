import os
import json
from datetime import datetime
from typing import Dict, List, Any, Optional
from sqlalchemy import create_engine, Column, Integer, String, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.dialects.postgresql import JSON

Base = declarative_base()

class DocumentationProject(Base):
    """Database model for documentation projects."""
    __tablename__ = 'documentation_projects'
    
    id = Column(Integer, primary_key=True)
    name = Column(String(255), nullable=False)
    description = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
class CodeAnalysis(Base):
    """Database model for code analysis results."""
    __tablename__ = 'code_analyses'
    
    id = Column(Integer, primary_key=True)
    project_id = Column(Integer, nullable=True)
    filename = Column(String(500))
    source_code = Column(Text, nullable=False)
    parsed_data = Column(JSON, nullable=False)
    documentation = Column(Text, nullable=False)
    export_format = Column(String(20), default='markdown')
    complexity_included = Column(Boolean, default=True)
    type_hints_included = Column(Boolean, default=True)
    docstrings_included = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

class DatabaseManager:
    """Manager for database operations in the documentation tool."""
    
    def __init__(self):
        self.database_url = os.getenv('DATABASE_URL')
        if not self.database_url:
            raise ValueError("DATABASE_URL environment variable not found")
        
        self.engine = create_engine(self.database_url)
        self.SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
        
        # Create tables
        self.init_database()
    
    def init_database(self):
        """Initialize database tables."""
        Base.metadata.create_all(bind=self.engine)
    
    def save_analysis(self, 
                     source_code: str, 
                     parsed_data: Dict[str, Any], 
                     documentation: str,
                     filename: Optional[str] = None,
                     project_id: Optional[int] = None,
                     export_format: str = 'markdown',
                     options: Optional[Dict[str, bool]] = None) -> int:
        """
        Save code analysis results to database.
        
        Args:
            source_code: The original Python source code
            parsed_data: Dictionary containing parsed metadata
            documentation: Generated documentation string
            filename: Optional filename for the code
            project_id: Optional project ID to associate with
            export_format: Format of the documentation (markdown, html, json)
            options: Dictionary of analysis options
            
        Returns:
            ID of the saved analysis record
        """
        session = self.SessionLocal()
        try:
            if options is None:
                options = {'complexity': True, 'type_hints': True, 'docstrings': True}
            
            analysis = CodeAnalysis(
                project_id=project_id,
                filename=filename,
                source_code=source_code,
                parsed_data=parsed_data,
                documentation=documentation,
                export_format=export_format,
                complexity_included=options.get('complexity', True),
                type_hints_included=options.get('type_hints', True),
                docstrings_included=options.get('docstrings', True)
            )
            
            session.add(analysis)
            session.commit()
            return analysis.id
        finally:
            session.close()
    
    def get_analysis(self, analysis_id: int) -> Optional[CodeAnalysis]:
        """Get a code analysis by ID."""
        session = self.SessionLocal()
        try:
            return session.query(CodeAnalysis).filter(CodeAnalysis.id == analysis_id).first()
        finally:
            session.close()
    
    def get_recent_analyses(self, limit: int = 10) -> List[CodeAnalysis]:
        """Get recent code analyses."""
        session = self.SessionLocal()
        try:
            return session.query(CodeAnalysis)\
                         .order_by(CodeAnalysis.created_at.desc())\
                         .limit(limit)\
                         .all()
        finally:
            session.close()
    
    def search_analyses(self, query: str, limit: int = 20) -> List[CodeAnalysis]:
        """
        Search code analyses by filename or source code content.
        
        Args:
            query: Search query string
            limit: Maximum number of results
            
        Returns:
            List of matching analyses
        """
        session = self.SessionLocal()
        try:
            return session.query(CodeAnalysis)\
                         .filter(
                             (CodeAnalysis.filename.ilike(f'%{query}%')) |
                             (CodeAnalysis.source_code.ilike(f'%{query}%'))
                         )\
                         .order_by(CodeAnalysis.created_at.desc())\
                         .limit(limit)\
                         .all()
        finally:
            session.close()
    
    def create_project(self, name: str, description: str = None) -> int:
        """
        Create a new documentation project.
        
        Args:
            name: Project name
            description: Optional project description
            
        Returns:
            ID of the created project
        """
        session = self.SessionLocal()
        try:
            project = DocumentationProject(
                name=name,
                description=description
            )
            session.add(project)
            session.commit()
            return project.id
        finally:
            session.close()
    
    def get_projects(self) -> List[DocumentationProject]:
        """Get all documentation projects."""
        session = self.SessionLocal()
        try:
            return session.query(DocumentationProject)\
                         .order_by(DocumentationProject.created_at.desc())\
                         .all()
        finally:
            session.close()
    
    def get_project_analyses(self, project_id: int) -> List[CodeAnalysis]:
        """Get all analyses for a specific project."""
        session = self.SessionLocal()
        try:
            return session.query(CodeAnalysis)\
                         .filter(CodeAnalysis.project_id == project_id)\
                         .order_by(CodeAnalysis.created_at.desc())\
                         .all()
        finally:
            session.close()
    
    def delete_analysis(self, analysis_id: int) -> bool:
        """Delete a code analysis."""
        session = self.SessionLocal()
        try:
            analysis = session.query(CodeAnalysis).filter(CodeAnalysis.id == analysis_id).first()
            if analysis:
                session.delete(analysis)
                session.commit()
                return True
            return False
        finally:
            session.close()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get database statistics."""
        session = self.SessionLocal()
        try:
            total_analyses = session.query(CodeAnalysis).count()
            total_projects = session.query(DocumentationProject).count()
            
            # Get function and class counts
            recent_analyses = session.query(CodeAnalysis).limit(100).all()
            total_functions = 0
            total_classes = 0
            
            for analysis in recent_analyses:
                parsed_data = analysis.parsed_data
                if isinstance(parsed_data, dict):
                    total_functions += len(parsed_data.get('functions', []))
                    total_classes += len(parsed_data.get('classes', []))
            
            return {
                'total_analyses': total_analyses,
                'total_projects': total_projects,
                'total_functions_documented': total_functions,
                'total_classes_documented': total_classes
            }
        finally:
            session.close()