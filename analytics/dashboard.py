"""
UniteSocial AI Analysis Dashboard
Combines all visualizations in a single presentation view.
"""

import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import generate_heatmaps as gh
import generate_mock_data as gm


def create_full_dashboard():
    """Create a comprehensive dashboard with all visualizations."""
    
    # Load all data
    veracity_df = pd.read_csv('analytics/output/veracity_performance.csv', index_col=0)
    multi_search_df = pd.read_csv('analytics/output/multi_search_effectiveness.csv')
    response_df = pd.read_csv('analytics/output/response_times.csv')
    
    # Create subplots
    fig = make_subplots(
        rows=2, cols=2,
        subplot_titles=(
            'Veracity Performance by Content Type',
            'Multi-Search Effectiveness',
            'Response Time by Complexity',
            'Key Statistics',
        ),
        specs=[[{"type": "heatmap"}, {"type": "scatter"}],
               [{"type": "heatmap"}, {"type": "table"}]]
    )
    
    # Plot 1: Veracity Performance
    veracity_pct = (veracity_df * 100).round(1)
    fig.add_trace(
        go.Heatmap(
            z=veracity_pct.values,
            x=veracity_pct.columns,
            y=veracity_pct.index,
            colorscale='RdYlGn',
            text=veracity_pct.values,
            texttemplate='%{text}%',
            showscale=True
        ),
        row=1, col=1
    )
    
    # Plot 2: Multi-Search Effectiveness
    fig.add_trace(
        go.Scatter(
            x=multi_search_df['searches'],
            y=multi_search_df['accuracy']*100,
            mode='lines+markers',
            name='Accuracy',
            line=dict(color='green', width=3)
        ),
        row=1, col=2
    )
    fig.add_trace(
        go.Scatter(
            x=multi_search_df['searches'],
            y=multi_search_df['coverage']*100,
            mode='lines+markers',
            name='Coverage',
            line=dict(color='blue', width=3)
        ),
        row=1, col=2
    )
    
    # Plot 3: Response Times
    heatmap_data = {
        'Average': response_df['avg_response_time'].tolist(),
        '95th Percentile': response_df['p95_response_time'].tolist()
    }
    heatmap_df = pd.DataFrame(heatmap_data, 
                              index=[f"{c} claim{'s' if c > 1 else ''}" for c in response_df['claims']])
    
    fig.add_trace(
        go.Heatmap(
            z=heatmap_df.values.T,
            x=heatmap_df.index,
            y=heatmap_df.columns,
            colorscale='RdYlGn_r',
            showscale=True
        ),
        row=2, col=1
    )
    
    # Plot 4: Key Statistics Table
    stats = [
        ['Avg Accuracy', '92.4%'],
        ['Web Search Success Rate', '94.8%'],
        ['Avg Response Time', '1.8s'],
        ['Total Claims Analyzed', '12,847'],
        ['Multi-Search Coverage', '96.2%'],
        ['Unverifiable Rate', '6.3%']
    ]
    
    fig.add_trace(
        go.Table(
            header=dict(values=['Metric', 'Value'],
                       fill_color='paleturquoise',
                       align='left',
                       font=dict(size=12, color='black')),
            cells=dict(values=[[row[0] for row in stats],
                             [row[1] for row in stats]],
                      fill_color='lavender',
                      align='left',
                      font=dict(size=11))
        ),
        row=2, col=2
    )
    
    # Update layout
    fig.update_layout(
        title_text="UniteSocial AI: Comprehensive Performance Dashboard",
        title_x=0.5,
        height=1000,
        width=1400,
        showlegend=True,
        font=dict(family='Arial', size=11)
    )
    
    fig.update_xaxes(title_text="Analysis Verdict", row=1, col=1)
    fig.update_yaxes(title_text="Content Category", row=1, col=1)
    
    fig.update_xaxes(title_text="Number of Searches", row=1, col=2)
    fig.update_yaxes(title_text="Performance (%)", row=1, col=2)
    
    fig.update_xaxes(title_text="Number of Claims", row=2, col=1)
    fig.update_yaxes(title_text="Time Metric", row=2, col=1)
    
    # Save
    fig.write_html('analytics/output/full_dashboard.html')
    fig.write_image('analytics/output/full_dashboard.png', scale=2)
    
    print("[OK] Generated: full_dashboard.html/png")


if __name__ == '__main__':
    # Generate data first if needed
    import os
    if not os.path.exists('analytics/output/veracity_performance.csv'):
        gm.save_all_data()
    
    create_full_dashboard()
    print("\n[DONE] Dashboard created successfully!")
    print("Open analytics/output/full_dashboard.html in your browser.")


