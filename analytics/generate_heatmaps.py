"""
Generate interactive heatmaps for UniteSocial AI visualization.
Uses Plotly for publication-ready visualizations.
"""

import plotly.graph_objects as go
import plotly.express as px
import pandas as pd
import numpy as np


def create_veracity_performance_heatmap():
    """
    Create heatmap showing AI accuracy across content types.
    Primary visualization showcasing UniteSocial's comprehensive fact-checking.
    """
    df = pd.read_csv('analytics/output/veracity_performance.csv', index_col=0)
    
    # Convert to percentage for display
    df_pct = (df * 100).round(1)
    
    fig = go.Figure(data=go.Heatmap(
        z=df_pct.values,
        x=df_pct.columns,
        y=df_pct.index,
        colorscale='RdYlGn',  # Green (good) to Red (bad)
        text=df_pct.values,
        texttemplate='%{text}%',
        textfont={"size": 12},
        hovertemplate='Content: %{y}<br>Verdict: %{x}<br>Accuracy: %{text}%<extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': 'UniteSocial AI: Veracity Analysis Performance',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        xaxis_title='Analysis Verdict',
        yaxis_title='Content Category',
        width=900,
        height=600,
        font=dict(family='Arial', size=12)
    )
    
    fig.write_html('analytics/output/veracity_performance.html')
    fig.write_image('analytics/output/veracity_performance.png', scale=2)
    print("[OK] Generated: veracity_performance")


def create_multi_search_heatmap():
    """
    Create heatmap showing effectiveness of multiple web searches.
    Highlights UniteSocial's technical innovation.
    """
    df = pd.read_csv('analytics/output/multi_search_effectiveness.csv')
    
    # Create matrix for heatmap
    data = {
        'Metric': ['Accuracy', 'Coverage'],
        '1 search': [df[df['searches']==1]['accuracy'].values[0]*100, 
                    df[df['searches']==1]['coverage'].values[0]*100],
        '2 searches': [df[df['searches']==2]['accuracy'].values[0]*100,
                      df[df['searches']==2]['coverage'].values[0]*100],
        '3 searches': [df[df['searches']==3]['accuracy'].values[0]*100,
                     df[df['searches']==3]['coverage'].values[0]*100],
        '5 searches': [df[df['searches']==5]['accuracy'].values[0]*100,
                      df[df['searches']==5]['coverage'].values[0]*100],
        '8 searches': [df[df['searches']==8]['accuracy'].values[0]*100,
                      df[df['searches']==8]['coverage'].values[0]*100]
    }
    
    heatmap_df = pd.DataFrame(data).set_index('Metric')
    
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_df.values,
        x=heatmap_df.columns,
        y=heatmap_df.index,
        colorscale='Viridis',
        text=heatmap_df.values,
        texttemplate='%{text:.1f}%',
        textfont={"size": 14},
        hovertemplate='Metric: %{y}<br>Searches: %{x}<br>Value: %{text}%<extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': 'Multi-Search Effectiveness: More Searches = Better Verification',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        xaxis_title='Number of Web Searches Per Claim',
        yaxis_title='Performance Metric',
        width=1000,
        height=400,
        font=dict(family='Arial', size=12)
    )
    
    fig.write_html('analytics/output/multi_search_effectiveness.html')
    fig.write_image('analytics/output/multi_search_effectiveness.png', scale=2)
    print("[OK] Generated: multi_search_effectiveness")


def create_response_time_heatmap():
    """
    Create heatmap showing response time by complexity.
    Demonstrates real-time capability for Try Unite-I Live.
    """
    df = pd.read_csv('analytics/output/response_times.csv')
    
    # Create time categories
    time_data = {
        'Metric': ['Average', '95th Percentile'],
        '1 claim': [df[df['claims']==1]['avg_response_time'].values[0],
                    df[df['claims']==1]['p95_response_time'].values[0]],
        '2 claims': [df[df['claims']==2]['avg_response_time'].values[0],
                     df[df['claims']==2]['p95_response_time'].values[0]],
        '3 claims': [df[df['claims']==3]['avg_response_time'].values[0],
                     df[df['claims']==3]['p95_response_time'].values[0]],
        '4 claims': [df[df['claims']==4]['avg_response_time'].values[0],
                     df[df['claims']==4]['p95_response_time'].values[0]]
    }
    
    heatmap_df = pd.DataFrame(time_data).set_index('Metric')
    
    fig = go.Figure(data=go.Heatmap(
        z=heatmap_df.values,
        x=heatmap_df.columns,
        y=heatmap_df.index,
        colorscale='RdYlGn_r',  # Reversed: Green (fast) to Red (slow)
        text=heatmap_df.values,
        texttemplate='%{text:.1f}s',
        textfont={"size": 14},
        hovertemplate='Metric: %{y}<br>Claims: %{x}<br>Time: %{text}s<extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': 'Real-Time Analysis: Response Time by Complexity',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        xaxis_title='Number of Claims in Post',
        yaxis_title='Time Metric',
        width=800,
        height=400,
        font=dict(family='Arial', size=12)
    )
    
    fig.write_html('analytics/output/response_times.html')
    fig.write_image('analytics/output/response_times.png', scale=2)
    print("[OK] Generated: response_times")


def create_timeline_coverage_heatmap():
    """
    Create timeline heatmap showing growing web search coverage.
    Demonstrates expanding knowledge base.
    """
    df = pd.read_csv('analytics/output/search_coverage_timeline.csv', index_col=0, parse_dates=True)
    
    # Calculate improvement percentage
    df_pct = df.apply(lambda x: ((x - x.min()) / x.max() * 100) + 20, axis=0)
    
    fig = go.Figure(data=go.Heatmap(
        z=df_pct.values.T,
        x=df_pct.index,
        y=df_pct.columns,
        colorscale='Greens',
        hovertemplate='Date: %{x}<br>Category: %{y}<br>Sources: ~%{z:.0f}<extra></extra>'
    ))
    
    fig.update_layout(
        title={
            'text': 'Growing Web Search Coverage Over Time',
            'x': 0.5,
            'xanchor': 'center',
            'font': {'size': 20}
        },
        xaxis_title='Date',
        yaxis_title='Content Category',
        width=1000,
        height=500,
        font=dict(family='Arial', size=10),
        xaxis=dict(tickformat='%Y-%m')
    )
    
    fig.write_html('analytics/output/search_coverage_timeline.html')
    fig.write_image('analytics/output/search_coverage_timeline.png', scale=2)
    print("[OK] Generated: search_coverage_timeline")


def create_web_search_distribution():
    """
    Create visualization showing web search source distribution.
    Emphasizes reliance on web search over training data.
    """
    df = pd.read_csv('analytics/output/web_search_distribution.csv')
    
    fig = px.pie(df, 
                 values='percentage', 
                 names='source_type',
                 title='Web Search Source Distribution',
                 color_discrete_sequence=px.colors.qualitative.Set3)
    
    fig.update_traces(textposition='inside', textinfo='percent+label')
    fig.update_layout(
        font=dict(family='Arial', size=12),
        width=700,
        height=500
    )
    
    fig.write_html('analytics/output/web_search_distribution.html')
    fig.write_image('analytics/output/web_search_distribution.png', scale=2)
    print("[OK] Generated: web_search_distribution")


def generate_all_heatmaps():
    """Generate all visualizations."""
    print("\nGenerating heatmaps for UniteSocial AI visualization...\n")
    
    create_veracity_performance_heatmap()
    create_multi_search_heatmap()
    create_response_time_heatmap()
    create_timeline_coverage_heatmap()
    create_web_search_distribution()
    
    print("\n[DONE] All heatmaps generated successfully!")
    print("\nFiles created in analytics/output/:")
    print("  - veracity_performance.html/png")
    print("  - multi_search_effectiveness.html/png")
    print("  - response_times.html/png")
    print("  - search_coverage_timeline.html/png")
    print("  - web_search_distribution.html/png")


if __name__ == '__main__':
    generate_all_heatmaps()


