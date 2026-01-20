"""
Generate realistic mock data for UniteSocial AI visualization.
Based on current system capabilities and expected performance.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta


def generate_veracity_performance_data():
    """
    Generate veracity analysis performance matrix.
    Shows accuracy across content types and verdict categories.
    """
    content_types = ['Political', 'Social', 'Economic', 'Health', 'Technology']
    verdicts = ['Factually Correct', 'Misleading', 'Untruth', 'Unverifiable']
    
    # Simulate high accuracy (85-96%) across all content types
    # Political and Health often higher accuracy due to verifiable facts
    np.random.seed(42)  # For reproducibility
    
    data = []
    for content in content_types:
        row = []
        for verdict in verdicts:
            # Base accuracy varies by content type
            if content in ['Political', 'Health']:
                base = np.random.uniform(0.88, 0.96)
            elif content in ['Technology', 'Economic']:
                base = np.random.uniform(0.85, 0.93)
            else:  # Social
                base = np.random.uniform(0.82, 0.91)
            
            # Add slight variation by verdict type
            if verdict == 'Factually Correct':
                accuracy = base
            elif verdict == 'Misleading':
                accuracy = base * 0.92  # Slightly lower for partial truth
            elif verdict == 'Untruth':
                accuracy = base * 0.95  # High accuracy for clear falsehoods
            else:  # Unverifiable
                accuracy = base * 0.85  # Lower for unverifiable claims
            
            row.append(accuracy)
        data.append(row)
    
    return pd.DataFrame(data, index=content_types, columns=verdicts)


def generate_multi_search_effectiveness():
    """
    Generate data showing how multiple web searches improve accuracy.
    Demonstrates UniteSocial's technical innovation.
    """
    num_searches = [1, 2, 3, 5, 8]
    
    # Simulate accuracy improvement with more searches
    accuracy = []
    coverage = []
    
    base_accuracy = 0.72
    base_coverage = 0.45
    
    for searches in num_searches:
        # Each additional search improves accuracy significantly
        acc = base_accuracy + (searches - 1) * 0.05
        acc = min(0.96, acc)
        accuracy.append(acc)
        
        # Coverage (facts verified) also improves
        cov = base_coverage + (searches - 1) * 0.09
        cov = min(0.95, cov)
        coverage.append(cov)
    
    return pd.DataFrame({
        'searches': num_searches,
        'accuracy': accuracy,
        'coverage': coverage
    })


def generate_response_times():
    """
    Generate response time analysis by post complexity.
    Shows real-time capability of Try Unite-I Live feature.
    """
    complexity_levels = ['Simple', 'Moderate', 'Complex', 'Very Complex']
    num_claims = [1, 2, 3, 4]
    
    data = {
        'claims': num_claims,
        'avg_response_time': [0.8, 1.4, 2.1, 3.2],
        'p95_response_time': [1.2, 2.1, 3.4, 4.8]
    }
    
    return pd.DataFrame(data)


def generate_search_coverage_timeline():
    """
    Generate timeline showing growth in web search verification.
    Demonstrates improving knowledge base over time.
    """
    # Generate data for last 6 months
    start_date = datetime.now() - timedelta(days=180)
    dates = [start_date + timedelta(days=x) for x in range(0, 180, 10)]
    
    categories = ['Political Books', 'Public Events', 'Policy Claims', 'Historical Facts']
    
    data = {}
    for category in categories:
        # Simulate gradual growth
        base = np.random.uniform(15, 25)
        values = [base + x*0.1 + np.random.normal(0, 2) for x in range(len(dates))]
        data[category] = [max(10, v) for v in values]  # Ensure positive
    
    df = pd.DataFrame(data, index=dates)
    return df


def generate_web_search_distribution():
    """
    Generate data showing distribution of web search results.
    Demonstrates reliance on web search vs training data.
    """
    sources = ['News', 'Wikipedia', 'Government', 'Academic', 'Verified']
    
    # Simulate high reliance on web search (UniteSocial's key feature)
    distribution = [0.35, 0.25, 0.15, 0.15, 0.10]
    
    return pd.DataFrame({
        'source_type': sources,
        'percentage': distribution
    })


def save_all_data():
    """Generate and save all mock data to CSV files."""
    print("Generating mock data for UniteSocial AI visualization...")
    
    veracity_perf = generate_veracity_performance_data()
    veracity_perf.to_csv('analytics/output/veracity_performance.csv')
    print("[OK] Generated: veracity_performance.csv")
    
    multi_search = generate_multi_search_effectiveness()
    multi_search.to_csv('analytics/output/multi_search_effectiveness.csv')
    print("[OK] Generated: multi_search_effectiveness.csv")
    
    response_times = generate_response_times()
    response_times.to_csv('analytics/output/response_times.csv')
    print("[OK] Generated: response_times.csv")
    
    timeline = generate_search_coverage_timeline()
    timeline.to_csv('analytics/output/search_coverage_timeline.csv')
    print("[OK] Generated: search_coverage_timeline.csv")
    
    web_dist = generate_web_search_distribution()
    web_dist.to_csv('analytics/output/web_search_distribution.csv')
    print("[OK] Generated: web_search_distribution.csv")
    
    print("\n[DONE] All mock data generated successfully!")


if __name__ == '__main__':
    save_all_data()


