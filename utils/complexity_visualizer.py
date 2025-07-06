"""
Interactive Code Complexity Visualization with Playful Progress Indicators.
"""

import plotly.graph_objects as go
import plotly.express as px
from plotly.subplots import make_subplots
import streamlit as st
import pandas as pd
import numpy as np
from typing import Dict, Any, List, Optional
import time
import random

class ComplexityVisualizer:
    """Interactive visualization engine for code complexity metrics with engaging animations."""
    
    def __init__(self):
        """Initialize the complexity visualizer."""
        self.color_schemes = {
            'complexity': ['#2E8B57', '#FFD700', '#FF6347', '#DC143C'],  # Green to Red
            'functions': ['#4CAF50', '#8BC34A', '#CDDC39', '#FFEB3B'],   # Nature greens
            'playful': ['#FF6B6B', '#4ECDC4', '#45B7D1', '#96CEB4', '#FECA57']  # Playful colors
        }
        self.emoji_indicators = {
            'low': '😌 Simple & Clean',
            'medium': '🤔 Getting Complex',
            'high': '😰 Needs Attention',
            'very_high': '🚨 Critical Complexity'
        }
    
    def create_playful_progress_bar(self, value: float, max_value: float, 
                                  label: str, emoji: str = "🎯") -> None:
        """
        Create an animated progress bar with playful indicators.
        
        Args:
            value: Current value
            max_value: Maximum value for the scale
            label: Label for the progress bar
            emoji: Emoji to display with the progress
        """
        progress_container = st.container()
        
        with progress_container:
            col1, col2, col3 = st.columns([1, 3, 1])
            
            with col1:
                st.write(f"{emoji} **{label}**")
            
            with col2:
                # Calculate percentage
                percentage = min(value / max_value, 1.0) if max_value > 0 else 0
                
                # Animated progress bar with color coding
                if percentage <= 0.3:
                    color = "#4CAF50"  # Green
                    mood = "😊"
                elif percentage <= 0.6:
                    color = "#FFC107"  # Yellow
                    mood = "😐"
                elif percentage <= 0.8:
                    color = "#FF9800"  # Orange
                    mood = "😬"
                else:
                    color = "#F44336"  # Red
                    mood = "😱"
                
                # Create progress bar HTML with animation
                progress_html = f"""
                <div style="background-color: #f0f0f0; border-radius: 10px; padding: 3px; margin: 5px 0;">
                    <div style="
                        background: linear-gradient(90deg, {color} 0%, {color} {percentage*100}%, transparent {percentage*100}%);
                        height: 20px;
                        border-radius: 7px;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        color: white;
                        font-weight: bold;
                        transition: all 0.5s ease-in-out;
                        animation: pulse 2s infinite;
                    ">
                        {value:.1f} / {max_value}
                    </div>
                </div>
                <style>
                @keyframes pulse {{
                    0% {{ opacity: 0.8; }}
                    50% {{ opacity: 1; }}
                    100% {{ opacity: 0.8; }}
                }}
                </style>
                """
                st.markdown(progress_html, unsafe_allow_html=True)
            
            with col3:
                st.write(f"{mood} {percentage*100:.1f}%")
    
    def create_complexity_radar_chart(self, function_data: Dict[str, Any]) -> go.Figure:
        """
        Create an interactive radar chart for function complexity metrics.
        
        Args:
            function_data: Dictionary containing function complexity data
            
        Returns:
            Plotly radar chart figure
        """
        # Extract complexity metrics
        complexity_metrics = function_data.get('complexity', {})
        
        categories = [
            'Cyclomatic Complexity',
            'Cognitive Complexity', 
            'Nesting Depth',
            'Parameters Count',
            'Lines of Code'
        ]
        
        values = [
            complexity_metrics.get('cyclomatic_complexity', 0),
            complexity_metrics.get('cognitive_complexity', 0),
            complexity_metrics.get('max_nesting_depth', 0),
            len(function_data.get('parameters', [])),
            function_data.get('lines_of_code', 0)
        ]
        
        # Normalize values to 0-10 scale for better visualization
        normalized_values = []
        max_values = [15, 20, 5, 10, 50]  # Reasonable max values for each metric
        
        for val, max_val in zip(values, max_values):
            normalized_values.append(min(val / max_val * 10, 10))
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=normalized_values,
            theta=categories,
            fill='toself',
            fillcolor='rgba(255, 107, 107, 0.3)',
            line=dict(color='rgba(255, 107, 107, 0.8)', width=3),
            name=function_data.get('name', 'Function'),
            marker=dict(size=8, color='#FF6B6B')
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 10],
                    tickvals=[2, 4, 6, 8, 10],
                    ticktext=['Low', 'Fair', 'Medium', 'High', 'Critical'],
                    gridcolor='rgba(0,0,0,0.1)'
                ),
                angularaxis=dict(
                    tickfont=dict(size=12, color='#2E86AB'),
                    gridcolor='rgba(0,0,0,0.1)'
                ),
                bgcolor='rgba(0,0,0,0)'
            ),
            showlegend=True,
            title=dict(
                text=f"🎯 Complexity Profile: {function_data.get('name', 'Function')}",
                font=dict(size=16, color='#2E86AB'),
                x=0.5
            ),
            font=dict(family="Arial, sans-serif"),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)'
        )
        
        return fig
    
    def create_complexity_heatmap(self, parsed_data: Dict[str, Any]) -> go.Figure:
        """
        Create an interactive heatmap showing complexity across functions.
        
        Args:
            parsed_data: Parsed code data with functions and classes
            
        Returns:
            Plotly heatmap figure
        """
        functions = parsed_data.get('functions', [])
        
        if not functions:
            # Return empty figure if no functions
            fig = go.Figure()
            fig.add_annotation(
                text="🤷‍♂️ No functions found to visualize",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16, color='gray')
            )
            return fig
        
        # Prepare data for heatmap
        function_names = [f.get('name', f'Function_{i}') for i, f in enumerate(functions)]
        metrics = ['Cyclomatic', 'Cognitive', 'Nesting', 'Parameters', 'Lines']
        
        # Create matrix of complexity values
        complexity_matrix = []
        for func in functions:
            complexity = func.get('complexity', {})
            row = [
                complexity.get('cyclomatic_complexity', 0),
                complexity.get('cognitive_complexity', 0),
                complexity.get('max_nesting_depth', 0),
                len(func.get('parameters', [])),
                func.get('lines_of_code', 0)
            ]
            complexity_matrix.append(row)
        
        # Convert to numpy array for easier manipulation
        complexity_array = np.array(complexity_matrix)
        
        # Normalize each column independently
        normalized_matrix = []
        for i in range(len(metrics)):
            column = complexity_array[:, i]
            if column.max() > 0:
                normalized_column = (column / column.max()) * 100
            else:
                normalized_column = column
            normalized_matrix.append(normalized_column)
        
        normalized_matrix = np.array(normalized_matrix).T
        
        # Create heatmap
        fig = go.Figure(data=go.Heatmap(
            z=normalized_matrix,
            x=metrics,
            y=function_names,
            colorscale=[
                [0, '#4CAF50'],    # Green for low complexity
                [0.3, '#FFEB3B'],  # Yellow for medium
                [0.6, '#FF9800'],  # Orange for high
                [1, '#F44336']     # Red for very high
            ],
            text=complexity_matrix,
            texttemplate="%{text}",
            textfont={"size": 10},
            hoverongaps=False,
            hovertemplate='<b>%{y}</b><br>%{x}: %{text}<br>Normalized: %{z:.1f}%<extra></extra>'
        ))
        
        fig.update_layout(
            title=dict(
                text="🔥 Complexity Heatmap - Hotspots Revealed!",
                font=dict(size=16, color='#2E86AB'),
                x=0.5
            ),
            xaxis_title="📊 Complexity Metrics",
            yaxis_title="🔧 Functions",
            font=dict(family="Arial, sans-serif"),
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            height=max(400, len(function_names) * 30)
        )
        
        return fig
    
    def create_complexity_distribution(self, parsed_data: Dict[str, Any]) -> go.Figure:
        """
        Create distribution charts for complexity metrics.
        
        Args:
            parsed_data: Parsed code data
            
        Returns:
            Plotly figure with distribution plots
        """
        functions = parsed_data.get('functions', [])
        
        if not functions:
            fig = go.Figure()
            fig.add_annotation(
                text="📊 No functions available for distribution analysis",
                xref="paper", yref="paper",
                x=0.5, y=0.5, showarrow=False,
                font=dict(size=16, color='gray')
            )
            return fig
        
        # Extract complexity values
        cyclomatic_values = []
        cognitive_values = []
        
        for func in functions:
            complexity = func.get('complexity', {})
            cyclomatic_values.append(complexity.get('cyclomatic_complexity', 0))
            cognitive_values.append(complexity.get('cognitive_complexity', 0))
        
        # Create subplots
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('🎯 Cyclomatic Complexity', '🧠 Cognitive Complexity'),
            specs=[[{"type": "histogram"}, {"type": "histogram"}]]
        )
        
        # Add histograms
        fig.add_trace(
            go.Histogram(
                x=cyclomatic_values,
                nbinsx=10,
                marker=dict(
                    color='#4ECDC4',
                    line=dict(color='#2E86AB', width=1)
                ),
                name='Cyclomatic',
                opacity=0.7
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Histogram(
                x=cognitive_values,
                nbinsx=10,
                marker=dict(
                    color='#FF6B6B',
                    line=dict(color='#C0392B', width=1)
                ),
                name='Cognitive',
                opacity=0.7
            ),
            row=1, col=2
        )
        
        fig.update_layout(
            title=dict(
                text="📈 Complexity Distribution Analysis",
                font=dict(size=16, color='#2E86AB'),
                x=0.5
            ),
            showlegend=False,
            paper_bgcolor='rgba(0,0,0,0)',
            plot_bgcolor='rgba(0,0,0,0)',
            font=dict(family="Arial, sans-serif")
        )
        
        return fig
    
    def create_animated_loading_indicator(self, message: str = "Analyzing code complexity...") -> None:
        """
        Display an animated loading indicator with random fun messages.
        
        Args:
            message: Loading message to display
        """
        loading_messages = [
            "🔍 Hunting down complex code...",
            "🧮 Counting decision points...",
            "🎯 Measuring code quality...",
            "🔬 Analyzing code patterns...",
            "📊 Generating awesome visualizations...",
            "🎨 Adding some visual magic...",
            "⚡ Processing at light speed...",
            "🚀 Launching complexity analysis..."
        ]
        
        # Use provided message or random one
        display_message = message if message != "Analyzing code complexity..." else random.choice(loading_messages)
        
        # Create animated progress indicator
        progress_bar = st.progress(0)
        status_text = st.empty()
        
        for i in range(100):
            # Update progress
            progress_bar.progress(i + 1)
            
            # Add some random pauses for realistic effect
            if i % 20 == 0:
                status_text.text(f"{display_message} {i+1}%")
                time.sleep(0.05)
            elif i % 10 == 0:
                time.sleep(0.02)
            else:
                time.sleep(0.01)
        
        # Clean up
        progress_bar.empty()
        status_text.empty()
    
    def get_complexity_category(self, value: int, metric_type: str) -> str:
        """
        Categorize complexity values into human-readable categories.
        
        Args:
            value: Complexity value
            metric_type: Type of complexity metric
            
        Returns:
            Category string with emoji
        """
        if metric_type == 'cyclomatic':
            if value <= 5:
                return self.emoji_indicators['low']
            elif value <= 10:
                return self.emoji_indicators['medium']
            elif value <= 15:
                return self.emoji_indicators['high']
            else:
                return self.emoji_indicators['very_high']
        elif metric_type == 'cognitive':
            if value <= 7:
                return self.emoji_indicators['low']
            elif value <= 15:
                return self.emoji_indicators['medium']
            elif value <= 25:
                return self.emoji_indicators['high']
            else:
                return self.emoji_indicators['very_high']
        elif metric_type == 'nesting':
            if value <= 2:
                return self.emoji_indicators['low']
            elif value <= 3:
                return self.emoji_indicators['medium']
            elif value <= 5:
                return self.emoji_indicators['high']
            else:
                return self.emoji_indicators['very_high']
        else:
            return "📊 Unknown"
    
    def display_complexity_insights(self, parsed_data: Dict[str, Any]) -> None:
        """
        Display insights and recommendations based on complexity analysis.
        
        Args:
            parsed_data: Parsed code data
        """
        functions = parsed_data.get('functions', [])
        
        if not functions:
            st.info("🤷‍♂️ No functions found to analyze")
            return
        
        # Calculate overall statistics
        total_functions = len(functions)
        complex_functions = 0
        total_cyclomatic = 0
        total_cognitive = 0
        max_complexity_func = None
        max_complexity_value = 0
        
        for func in functions:
            complexity = func.get('complexity', {})
            cyclomatic = complexity.get('cyclomatic_complexity', 0)
            cognitive = complexity.get('cognitive_complexity', 0)
            
            total_cyclomatic += cyclomatic
            total_cognitive += cognitive
            
            if cyclomatic > 10 or cognitive > 15:
                complex_functions += 1
            
            total_complexity = cyclomatic + cognitive
            if total_complexity > max_complexity_value:
                max_complexity_value = total_complexity
                max_complexity_func = func
        
        # Display insights
        st.subheader("🎯 Complexity Insights & Recommendations")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            st.metric(
                "🔧 Total Functions", 
                total_functions,
                help="Total number of functions analyzed"
            )
        
        with col2:
            complexity_ratio = (complex_functions / total_functions * 100) if total_functions > 0 else 0
            st.metric(
                "⚠️ Complex Functions", 
                f"{complex_functions} ({complexity_ratio:.1f}%)",
                delta=f"-{100-complexity_ratio:.1f}% to ideal" if complexity_ratio > 20 else "Good ratio!",
                delta_color="inverse" if complexity_ratio > 20 else "normal"
            )
        
        with col3:
            avg_complexity = (total_cyclomatic + total_cognitive) / total_functions if total_functions > 0 else 0
            st.metric(
                "📊 Average Complexity", 
                f"{avg_complexity:.1f}",
                help="Combined average of cyclomatic and cognitive complexity"
            )
        
        # Recommendations
        if complexity_ratio > 30:
            st.warning(
                "🚨 **High Complexity Alert!** Over 30% of your functions are complex. "
                "Consider refactoring to improve maintainability."
            )
        elif complexity_ratio > 15:
            st.info(
                "🤔 **Moderate Complexity** detected. Some functions could benefit from simplification."
            )
        else:
            st.success(
                "🎉 **Great job!** Your code complexity is well-managed and maintainable."
            )
        
        # Highlight most complex function
        if max_complexity_func:
            with st.expander("🔍 Most Complex Function Details"):
                func_name = max_complexity_func.get('name', 'Unknown')
                func_complexity = max_complexity_func.get('complexity', {})
                
                st.write(f"**Function:** `{func_name}`")
                st.write(f"**Cyclomatic Complexity:** {func_complexity.get('cyclomatic_complexity', 0)}")
                st.write(f"**Cognitive Complexity:** {func_complexity.get('cognitive_complexity', 0)}")
                st.write(f"**Nesting Depth:** {func_complexity.get('max_nesting_depth', 0)}")
                st.write(f"**Lines of Code:** {max_complexity_func.get('lines_of_code', 0)}")
                
                if func_complexity.get('cyclomatic_complexity', 0) > 15:
                    st.error("💡 **Suggestion:** Break this function into smaller, focused functions")
                elif func_complexity.get('cognitive_complexity', 0) > 25:
                    st.warning("💡 **Suggestion:** Reduce nested conditions and loops")
                else:
                    st.info("💡 **Suggestion:** Monitor this function during future changes")