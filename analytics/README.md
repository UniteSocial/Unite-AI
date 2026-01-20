# UniteSocial AI Analytics Visualization

Generate interactive heatmaps showcasing UniteSocial's AI fact-checking capabilities for presentations.

## Features

Creates 5 compelling visualizations:

1. **Veracity Performance Matrix** - Accuracy across content types (Political, Social, Economic, Health, Tech)
2. **Multi-Search Effectiveness** - How multiple web searches improve accuracy (1-8 searches)
3. **Response Time Analysis** - Real-time analysis speed by complexity
4. **Search Coverage Timeline** - Growing web search coverage over 6 months
5. **Web Search Distribution** - Sources verified (News, Wikipedia, Government, etc.)

## Installation

Install Python dependencies:

```bash
# Option 1: Install globally (if you have access)
pip install pandas plotly numpy kaleido

# Option 2: Install for user only
python3 -m pip install --user pandas plotly numpy kaleido

# Option 3: Create virtual environment
python3 -m venv analytics_venv
source analytics_venv/bin/activate  # or analytics_venv\Scripts\activate on Windows
pip install pandas plotly numpy kaleido
```

## Usage

### Quick Start

```bash
cd analytics
python3 run_all.py
```

This will:
1. Generate realistic mock data
2. Create all heatmaps
3. Output HTML and PNG files to `output/` directory

### Individual Scripts

Generate data only:
```bash
python3 generate_mock_data.py
```

Generate visualizations only:
```bash
python3 generate_heatmaps.py
```

### Output Files

All files are created in `analytics/output/`:

- `veracity_performance.html/png` - Main performance matrix
- `multi_search_effectiveness.html/png` - Search effectiveness
- `response_times.html/png` - Speed analysis  
- `search_coverage_timeline.html/png` - Coverage over time
- `web_search_distribution.html/png` - Source distribution
- `full_dashboard.html/png` - Combined dashboard (if using dashboard.py)

## What It Visualizes

### Core Messages

1. **Accuracy**: 85-96% accuracy across all content types
2. **Innovation**: Multiple web searches (up to 8 per claim)
3. **Real-time**: Fast response times (0.8s - 3.2s)
4. **Transparency**: Web search-based, not training data
5. **Growth**: Improving coverage over time

### Presentation Tips

- Open HTML files for **interactive viewing** (zoom, hover, etc.)
- Use PNG files for **slides and documents**
- The Veracity Performance Matrix is the most impactful - use it first
- Multi-Search Effectiveness demonstrates technical innovation

## Customization

Edit `generate_mock_data.py` to adjust:
- Accuracy ranges
- Response times
- Search effectiveness curves

Edit `generate_heatmaps.py` to customize:
- Color schemes
- Titles and labels
- Layout sizes

## Technical Details

Based on [Plotly Heatmaps](https://plotly.com/python/heatmaps/):
- Interactive HTML for live demos
- Static PNG for slides
- Professional color schemes (RdYlGn, Viridis)
- Hover tooltips with detailed metrics
- Publication-ready quality

## Requirements

- Python 3.8+
- pandas >= 2.0
- plotly >= 5.18
- numpy >= 1.24
- kaleido >= 0.2.1 (for PNG export)


