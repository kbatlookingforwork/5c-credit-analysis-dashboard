import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import numpy as np
from typing import Dict, List

class CreditVisualizations:
    """
    Visualization components for credit analysis dashboard
    Creates interactive charts for 5C credit analysis
    """
    
    def __init__(self, data: pd.DataFrame):
        self.data = data
        self.color_palette = {
            'primary': '#1f77b4',
            'secondary': '#ff7f0e', 
            'success': '#2ca02c',
            'warning': '#d62728',
            'info': '#9467bd',
            'light': '#17becf'
        }
    
    def plot_score_distribution(self, scores: pd.Series) -> go.Figure:
        """Plot credit score distribution histogram"""
        fig = go.Figure()
        
        fig.add_trace(go.Histogram(
            x=scores,
            nbinsx=20,
            name='Credit Scores',
            marker_color=self.color_palette['primary'],
            opacity=0.7,
            hovertemplate='Score Range: %{x}<br>Count: %{y}<extra></extra>'
        ))
        
        # Add mean line
        mean_score = scores.mean()
        fig.add_vline(
            x=mean_score, 
            line_dash="dash", 
            line_color="red",
            annotation_text=f"Mean: {mean_score:.3f}"
        )
        
        fig.update_layout(
            title="Credit Score Distribution",
            xaxis_title="Credit Score",
            yaxis_title="Number of Applications",
            showlegend=False,
            height=400
        )
        
        return fig
    
    def plot_5c_radar(self, scores: pd.DataFrame) -> go.Figure:
        """Plot 5C components as radar chart"""
        # Calculate average scores for each component
        components = ['character_score', 'capacity_score', 'capital_score', 
                     'collateral_score', 'conditions_score']
        
        avg_scores = [scores[comp].mean() for comp in components]
        component_names = ['Character', 'Capacity', 'Capital', 'Collateral', 'Conditions']
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=avg_scores + [avg_scores[0]],  # Close the radar
            theta=component_names + [component_names[0]],
            fill='toself',
            name='Average Scores',
            line_color=self.color_palette['primary'],
            fillcolor=self.color_palette['primary'],
            opacity=0.3,
            hovertemplate='%{theta}: %{r:.3f}<extra></extra>'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )
            ),
            title="5C Components - Portfolio Average",
            height=400
        )
        
        return fig
    
    def plot_risk_segments(self, scores: pd.DataFrame, threshold: float) -> go.Figure:
        """Plot risk segmentation pie chart"""
        total_score = scores['total_score']
        
        high_risk = (total_score < threshold).sum()
        medium_risk = ((total_score >= threshold) & (total_score < threshold + 0.2)).sum()
        low_risk = (total_score >= threshold + 0.2).sum()
        
        labels = ['High Risk', 'Medium Risk', 'Low Risk']
        values = [high_risk, medium_risk, low_risk]
        colors = ['#d62728', '#ff7f0e', '#2ca02c']
        
        fig = go.Figure(data=[go.Pie(
            labels=labels,
            values=values,
            marker_colors=colors,
            hole=0.3,
            hovertemplate='%{label}: %{value} applications<br>%{percent}<extra></extra>'
        )])
        
        fig.update_layout(
            title="Risk Segmentation",
            height=400,
            annotations=[dict(text=f'Total<br>{sum(values)}', x=0.5, y=0.5, font_size=16, showarrow=False)]
        )
        
        return fig
    
    def plot_5c_correlation(self, scores: pd.DataFrame) -> go.Figure:
        """Plot correlation matrix of 5C components"""
        components = ['character_score', 'capacity_score', 'capital_score', 
                     'collateral_score', 'conditions_score']
        
        correlation_matrix = scores[components].corr()
        
        fig = go.Figure(data=go.Heatmap(
            z=correlation_matrix.values,
            x=['Character', 'Capacity', 'Capital', 'Collateral', 'Conditions'],
            y=['Character', 'Capacity', 'Capital', 'Collateral', 'Conditions'],
            colorscale='RdBu',
            zmid=0,
            text=correlation_matrix.round(3).values,
            texttemplate="%{text}",
            textfont={"size": 12},
            hovertemplate='%{y} vs %{x}<br>Correlation: %{z:.3f}<extra></extra>'
        ))
        
        fig.update_layout(
            title="5C Components Correlation Matrix",
            height=400,
            xaxis_title="Components",
            yaxis_title="Components"
        )
        
        return fig
    
    def plot_component_distribution(self, scores: pd.DataFrame, component: str) -> go.Figure:
        """Plot distribution of individual 5C component"""
        component_name = component.replace('_score', '').title()
        
        fig = go.Figure()
        
        fig.add_trace(go.Histogram(
            x=scores[component],
            nbinsx=15,
            name=component_name,
            marker_color=self.color_palette['secondary'],
            opacity=0.7,
            hovertemplate=f'{component_name} Score: %{{x}}<br>Count: %{{y}}<extra></extra>'
        ))
        
        # Add statistics
        mean_val = scores[component].mean()
        median_val = scores[component].median()
        
        fig.add_vline(x=mean_val, line_dash="dash", line_color="red", 
                      annotation_text=f"Mean: {mean_val:.3f}")
        fig.add_vline(x=median_val, line_dash="dot", line_color="green", 
                      annotation_text=f"Median: {median_val:.3f}")
        
        fig.update_layout(
            title=f"{component_name} Score Distribution",
            xaxis_title=f"{component_name} Score",
            yaxis_title="Frequency",
            showlegend=False,
            height=300
        )
        
        return fig
    
    def plot_5c_performance_comparison(self, scores: pd.DataFrame) -> go.Figure:
        """Box plot comparison of 5C components"""
        components = ['character_score', 'capacity_score', 'capital_score', 
                     'collateral_score', 'conditions_score']
        component_names = ['Character', 'Capacity', 'Capital', 'Collateral', 'Conditions']
        
        fig = go.Figure()
        
        for i, (comp, name) in enumerate(zip(components, component_names)):
            fig.add_trace(go.Box(
                y=scores[comp],
                name=name,
                marker_color=px.colors.qualitative.Set1[i],
                hovertemplate=f'{name}<br>Score: %{{y}}<extra></extra>'
            ))
        
        fig.update_layout(
            title="5C Components Performance Comparison",
            yaxis_title="Score",
            xaxis_title="Components",
            height=400
        )
        
        return fig
    
    def plot_individual_5c_bar(self, scores: Dict[str, float]) -> go.Figure:
        """Bar chart for individual borrower 5C scores"""
        components = ['character_score', 'capacity_score', 'capital_score', 
                     'collateral_score', 'conditions_score']
        component_names = ['Character', 'Capacity', 'Capital', 'Collateral', 'Conditions']
        
        values = [scores[comp] for comp in components]
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
        
        fig = go.Figure(data=[
            go.Bar(
                x=component_names,
                y=values,
                marker_color=colors,
                text=[f'{v:.3f}' for v in values],
                textposition='auto',
                hovertemplate='%{x}: %{y:.3f}<extra></extra>'
            )
        ])
        
        fig.update_layout(
            title="Individual 5C Scores",
            yaxis_title="Score",
            yaxis=dict(range=[0, 1]),
            height=400,
            showlegend=False
        )
        
        return fig
    
    def plot_individual_5c_radar(self, scores: Dict[str, float]) -> go.Figure:
        """Radar chart for individual borrower 5C scores"""
        components = ['character_score', 'capacity_score', 'capital_score', 
                     'collateral_score', 'conditions_score']
        component_names = ['Character', 'Capacity', 'Capital', 'Collateral', 'Conditions']
        
        values = [scores[comp] for comp in components]
        
        fig = go.Figure()
        
        fig.add_trace(go.Scatterpolar(
            r=values + [values[0]],
            theta=component_names + [component_names[0]],
            fill='toself',
            name='Borrower Scores',
            line_color=self.color_palette['success'],
            fillcolor=self.color_palette['success'],
            opacity=0.3,
            hovertemplate='%{theta}: %{r:.3f}<extra></extra>'
        ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )
            ),
            title="Individual 5C Profile",
            height=400,
            showlegend=False
        )
        
        return fig
    
    def plot_risk_heatmap(self, scores: pd.DataFrame, threshold: float) -> go.Figure:
        """Risk concentration heatmap"""
        # Create score bins
        score_bins = np.arange(0, 1.1, 0.1)
        score_labels = [f'{i:.1f}-{i+0.1:.1f}' for i in score_bins[:-1]]
        
        # Bin the scores
        scores['score_bin'] = pd.cut(scores['total_score'], bins=score_bins, labels=score_labels, include_lowest=True)
        
        # Count applications in each bin
        bin_counts = scores['score_bin'].value_counts().sort_index()
        
        # Create risk categories
        risk_colors = []
        for i, label in enumerate(score_labels):
            bin_start = float(label.split('-')[0])
            if bin_start < threshold:
                risk_colors.append('High Risk')
            elif bin_start < threshold + 0.2:
                risk_colors.append('Medium Risk')
            else:
                risk_colors.append('Low Risk')
        
        # Create heatmap data
        heatmap_data = bin_counts.values.reshape(1, -1)
        
        fig = go.Figure(data=go.Heatmap(
            z=heatmap_data,
            x=score_labels,
            y=['Applications'],
            colorscale='Reds',
            text=[[f'{count}<br>{risk}' for count, risk in zip(bin_counts.values, risk_colors)]],
            texttemplate="%{text}",
            textfont={"size": 10},
            hovertemplate='Score Range: %{x}<br>Count: %{z}<extra></extra>'
        ))
        
        fig.update_layout(
            title="Risk Concentration Heatmap",
            xaxis_title="Credit Score Range",
            height=200
        )
        
        return fig
    
    def plot_risk_factors(self, high_risk_data: pd.DataFrame) -> go.Figure:
        """Analyze primary risk factors for high-risk applications"""
        components = ['character_score', 'capacity_score', 'capital_score', 
                     'collateral_score', 'conditions_score']
        component_names = ['Character', 'Capacity', 'Capital', 'Collateral', 'Conditions']
        
        # Calculate average scores for high-risk applications
        avg_scores = [high_risk_data[comp].mean() for comp in components]
        
        # Sort by lowest scores (biggest risk factors)
        sorted_data = sorted(zip(component_names, avg_scores), key=lambda x: x[1])
        sorted_names, sorted_scores = zip(*sorted_data)
        
        # Color bars based on score (red for low scores)
        colors = ['#d62728' if score < 0.3 else '#ff7f0e' if score < 0.5 else '#2ca02c' 
                 for score in sorted_scores]
        
        fig = go.Figure(data=[
            go.Bar(
                x=list(sorted_scores),
                y=list(sorted_names),
                orientation='h',
                marker_color=colors,
                text=[f'{score:.3f}' for score in sorted_scores],
                textposition='auto',
                hovertemplate='%{y}: %{x:.3f}<extra></extra>'
            )
        ])
        
        fig.update_layout(
            title="Primary Risk Factors (High-Risk Applications)",
            xaxis_title="Average Score",
            yaxis_title="5C Components",
            height=400,
            showlegend=False
        )
        
        return fig

    def plot_borrower_type_comparison(self, scores: pd.DataFrame, data: pd.DataFrame) -> go.Figure:
        """Compare 5C performance between consumer and SME borrowers"""
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Consumer Credit Profile', 'SME Credit Profile'),
            specs=[[{'type': 'polar'}, {'type': 'polar'}]]
        )
        
        components = ['character_score', 'capacity_score', 'capital_score', 
                     'collateral_score', 'conditions_score']
        component_names = ['Character', 'Capacity', 'Capital', 'Collateral', 'Conditions']
        
        # Separate data by borrower type
        if 'borrower_type' in data.columns:
            consumer_mask = data['borrower_type'] == 'consumer'
            sme_mask = data['borrower_type'] == 'sme'
            
            consumer_scores = [scores[consumer_mask][comp].mean() for comp in components]
            sme_scores = [scores[sme_mask][comp].mean() for comp in components]
            
            # Consumer radar
            fig.add_trace(go.Scatterpolar(
                r=consumer_scores + [consumer_scores[0]],
                theta=component_names + [component_names[0]],
                fill='toself',
                name='Consumer Average',
                line_color='#1f77b4',
                fillcolor='rgba(31, 119, 180, 0.3)'
            ), row=1, col=1)
            
            # SME radar
            fig.add_trace(go.Scatterpolar(
                r=sme_scores + [sme_scores[0]],
                theta=component_names + [component_names[0]],
                fill='toself',
                name='SME Average',
                line_color='#ff7f0e',
                fillcolor='rgba(255, 127, 14, 0.3)'
            ), row=1, col=2)
        
        fig.update_layout(
            title="Credit Profile Comparison: Consumers vs SMEs",
            polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
            polar2=dict(radialaxis=dict(visible=True, range=[0, 1])),
            height=500,
            showlegend=False
        )
        
        return fig

    def plot_credit_score_vs_5c(self, scores: pd.DataFrame, data: pd.DataFrame) -> go.Figure:
        """Analyze relationship between raw credit scores and 5C components"""
        if 'credit_score_raw' not in data.columns:
            return go.Figure().add_annotation(text="Credit score data not available", 
                                            xref="paper", yref="paper", x=0.5, y=0.5)
        
        fig = make_subplots(
            rows=2, cols=3,
            subplot_titles=['Character vs Credit Score', 'Capacity vs Credit Score', 
                           'Capital vs Credit Score', 'Collateral vs Credit Score', 
                           'Conditions vs Credit Score', '5C Total vs Credit Score']
        )
        
        components = ['character_score', 'capacity_score', 'capital_score', 
                     'collateral_score', 'conditions_score', 'total_score']
        component_names = ['Character', 'Capacity', 'Capital', 'Collateral', 'Conditions', 'Total 5C']
        
        positions = [(1,1), (1,2), (1,3), (2,1), (2,2), (2,3)]
        
        for i, (comp, name, pos) in enumerate(zip(components, component_names, positions)):
            fig.add_trace(go.Scatter(
                x=data['credit_score_raw'],
                y=scores[comp],
                mode='markers',
                name=name,
                marker=dict(
                    size=6,
                    color=scores[comp],
                    colorscale='Viridis',
                    opacity=0.7
                ),
                hovertemplate=f'Credit Score: %{{x}}<br>{name}: %{{y:.3f}}<extra></extra>'
            ), row=pos[0], col=pos[1])
        
        fig.update_layout(
            title="Credit Score vs 5C Component Analysis",
            height=600,
            showlegend=False
        )
        
        return fig

    def plot_industry_risk_analysis(self, scores: pd.DataFrame, data: pd.DataFrame) -> go.Figure:
        """Analyze risk patterns by industry"""
        if 'industry' not in data.columns:
            return go.Figure().add_annotation(text="Industry data not available", 
                                            xref="paper", yref="paper", x=0.5, y=0.5)
        
        # Group by industry and calculate average scores
        industry_stats = []
        for industry in data['industry'].unique():
            if pd.notna(industry):
                mask = data['industry'] == industry
                industry_data = {
                    'industry': industry,
                    'count': mask.sum(),
                    'avg_total_score': scores[mask]['total_score'].mean(),
                    'avg_character': scores[mask]['character_score'].mean(),
                    'avg_capacity': scores[mask]['capacity_score'].mean(),
                    'avg_capital': scores[mask]['capital_score'].mean(),
                    'avg_collateral': scores[mask]['collateral_score'].mean(),
                    'avg_conditions': scores[mask]['conditions_score'].mean()
                }
                industry_stats.append(industry_data)
        
        industry_df = pd.DataFrame(industry_stats)
        
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Industry Risk Overview', 'Industry 5C Breakdown'),
            specs=[[{'type': 'bar'}, {'type': 'bar'}]]
        )
        
        # Industry risk overview
        fig.add_trace(go.Bar(
            x=industry_df['industry'],
            y=industry_df['avg_total_score'],
            name='Average Total Score',
            marker_color=['#2ca02c' if score >= 0.7 else '#ff7f0e' if score >= 0.5 else '#d62728' 
                         for score in industry_df['avg_total_score']],
            text=[f'{score:.2f}' for score in industry_df['avg_total_score']],
            textposition='auto',
            hovertemplate='Industry: %{x}<br>Average Score: %{y:.3f}<br>Count: %{customdata}<extra></extra>',
            customdata=industry_df['count']
        ), row=1, col=1)
        
        # 5C breakdown by industry
        components = ['avg_character', 'avg_capacity', 'avg_capital', 'avg_collateral', 'avg_conditions']
        component_names = ['Character', 'Capacity', 'Capital', 'Collateral', 'Conditions']
        colors = ['#1f77b4', '#ff7f0e', '#2ca02c', '#d62728', '#9467bd']
        
        for comp, name, color in zip(components, component_names, colors):
            fig.add_trace(go.Bar(
                x=industry_df['industry'],
                y=industry_df[comp],
                name=name,
                marker_color=color,
                hovertemplate=f'{name}: %{{y:.3f}}<extra></extra>'
            ), row=1, col=2)
        
        fig.update_layout(
            title="Industry Risk Analysis",
            height=500,
            showlegend=True
        )
        
        return fig

    def plot_payment_behavior_analysis(self, scores: pd.DataFrame, data: pd.DataFrame) -> go.Figure:
        """Analyze the relationship between payment delays and credit performance"""
        if 'payment_delays' not in data.columns:
            return go.Figure().add_annotation(text="Payment delay data not available", 
                                            xref="paper", yref="paper", x=0.5, y=0.5)
        
        # Create payment delay categories
        data_copy = data.copy()
        data_copy['payment_category'] = pd.cut(
            data_copy['payment_delays'], 
            bins=[-0.1, 0, 2, 5, float('inf')], 
            labels=['No Delays', '1-2 Delays', '3-5 Delays', '6+ Delays']
        )
        
        fig = make_subplots(
            rows=1, cols=2,
            subplot_titles=('Payment Behavior Impact on Total Score', 'Payment Delays Distribution'),
            specs=[[{'type': 'box'}, {'type': 'bar'}]]
        )
        
        # Box plot of scores by payment category
        for category in data_copy['payment_category'].cat.categories:
            mask = data_copy['payment_category'] == category
            fig.add_trace(go.Box(
                y=scores[mask]['total_score'],
                name=category,
                boxpoints='outliers',
                hovertemplate=f'{category}<br>Score: %{{y:.3f}}<extra></extra>'
            ), row=1, col=1)
        
        # Distribution of payment delays
        delay_counts = data_copy['payment_category'].value_counts()
        fig.add_trace(go.Bar(
            x=delay_counts.index,
            y=delay_counts.values,
            name='Count',
            marker_color=['#2ca02c', '#17becf', '#ff7f0e', '#d62728'],
            text=delay_counts.values,
            textposition='auto',
            hovertemplate='Category: %{x}<br>Count: %{y}<extra></extra>'
        ), row=1, col=2)
        
        fig.update_layout(
            title="Payment Behavior Analysis",
            height=500,
            showlegend=False
        )
        
        return fig
