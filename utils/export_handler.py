import json
from typing import Dict, Any
import html

class ExportHandler:
    """Handler for exporting documentation to different formats."""
    
    def to_html(self, markdown_content: str) -> str:
        """
        Convert markdown documentation to HTML format.
        
        Args:
            markdown_content: Markdown formatted documentation
            
        Returns:
            HTML formatted documentation
        """
        html_content = self._markdown_to_html(markdown_content)
        
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Python Documentation</title>
    <style>
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
            line-height: 1.6;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            color: #333;
        }}
        
        h1, h2, h3 {{
            color: #2c3e50;
            border-bottom: 1px solid #eee;
            padding-bottom: 10px;
        }}
        
        code {{
            background-color: #f8f9fa;
            padding: 2px 4px;
            border-radius: 3px;
            font-family: 'Courier New', Consolas, monospace;
            color: #e83e8c;
        }}
        
        pre {{
            background-color: #f8f9fa;
            padding: 15px;
            border-radius: 5px;
            overflow-x: auto;
            border-left: 4px solid #007bff;
        }}
        
        ul {{
            margin: 10px 0;
        }}
        
        li {{
            margin: 5px 0;
        }}
        
        .function-signature {{
            background-color: #e9ecef;
            padding: 10px;
            border-radius: 5px;
            margin: 10px 0;
            font-family: 'Courier New', Consolas, monospace;
        }}
        
        .complexity-metrics {{
            background-color: #fff3cd;
            padding: 10px;
            border-radius: 5px;
            border-left: 4px solid #ffc107;
            margin: 10px 0;
        }}
        
        .docstring {{
            background-color: #d1ecf1;
            padding: 10px;
            border-radius: 5px;
            border-left: 4px solid #17a2b8;
            margin: 10px 0;
            font-style: italic;
        }}
    </style>
</head>
<body>
{html_content}
</body>
</html>"""
    
    def to_json(self, parsed_data: Dict[str, Any]) -> str:
        """
        Convert parsed data to JSON format.
        
        Args:
            parsed_data: Dictionary containing parsed metadata
            
        Returns:
            JSON formatted string
        """
        return json.dumps(parsed_data, indent=2, ensure_ascii=False)
    
    def _markdown_to_html(self, markdown: str) -> str:
        """
        Simple markdown to HTML converter.
        
        Args:
            markdown: Markdown content
            
        Returns:
            HTML content
        """
        lines = markdown.split('\n')
        html_lines = []
        in_code_block = False
        
        for line in lines:
            # Handle code blocks
            if line.strip().startswith('```'):
                if in_code_block:
                    html_lines.append('</pre>')
                    in_code_block = False
                else:
                    html_lines.append('<pre><code>')
                    in_code_block = True
                continue
            
            if in_code_block:
                html_lines.append(html.escape(line))
                continue
            
            # Handle headers
            if line.startswith('### '):
                html_lines.append(f'<h3>{html.escape(line[4:])}</h3>')
            elif line.startswith('## '):
                html_lines.append(f'<h2>{html.escape(line[3:])}</h2>')
            elif line.startswith('# '):
                html_lines.append(f'<h1>{html.escape(line[2:])}</h1>')
            
            # Handle lists
            elif line.strip().startswith('- '):
                if not html_lines or not html_lines[-1].startswith('<li>'):
                    html_lines.append('<ul>')
                content = line.strip()[2:]
                content = self._process_inline_markdown(content)
                html_lines.append(f'<li>{content}</li>')
            
            # Handle bold and italic
            elif line.strip().startswith('**') and line.strip().endswith('**'):
                content = line.strip()[2:-2]
                html_lines.append(f'<p><strong>{html.escape(content)}</strong></p>')
            
            # Handle italic
            elif line.strip().startswith('*') and line.strip().endswith('*') and not line.strip().startswith('**'):
                content = line.strip()[1:-1]
                html_lines.append(f'<p><em>{html.escape(content)}</em></p>')
            
            # Handle empty lines
            elif line.strip() == '':
                if html_lines and html_lines[-1].startswith('<li>'):
                    html_lines.append('</ul>')
                html_lines.append('')
            
            # Regular paragraphs
            else:
                if html_lines and html_lines[-1].startswith('<li>'):
                    html_lines.append('</ul>')
                content = self._process_inline_markdown(line)
                if content.strip():
                    html_lines.append(f'<p>{content}</p>')
        
        # Close any open lists
        if html_lines and html_lines[-1].startswith('<li>'):
            html_lines.append('</ul>')
        
        return '\n'.join(html_lines)
    
    def _process_inline_markdown(self, text: str) -> str:
        """Process inline markdown elements like code, bold, italic."""
        # Handle inline code
        while '`' in text:
            start = text.find('`')
            if start == -1:
                break
            end = text.find('`', start + 1)
            if end == -1:
                break
            
            code_content = text[start + 1:end]
            text = text[:start] + f'<code>{html.escape(code_content)}</code>' + text[end + 1:]
        
        # Handle bold
        while '**' in text:
            start = text.find('**')
            if start == -1:
                break
            end = text.find('**', start + 2)
            if end == -1:
                break
            
            bold_content = text[start + 2:end]
            text = text[:start] + f'<strong>{html.escape(bold_content)}</strong>' + text[end + 2:]
        
        # Escape remaining HTML
        text = html.escape(text)
        
        return text
