#!/usr/bin/env python3
"""Run all analytics generation scripts."""
import subprocess
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def main():
    print("=" * 60)
    print("UniteSocial AI Analytics Visualization Generator")
    print("=" * 60)
    print("\nThis script generates heatmaps showcasing our AI capabilities.")
    print("\nRequirements: pandas, plotly, numpy, kaleido")
    print("Install with: pip install pandas plotly numpy kaleido")
    print("\n" + "=" * 60)
    
    response = input("\nReady to generate? [y/n]: ")
    if response.lower() != 'y':
        print("Cancelled.")
        return
    
    print("\nGenerating visualizations...\n")
    
    try:
        # Change to analytics directory
        os.chdir(os.path.dirname(__file__))
        
        # Import and run
        print("Loading modules...")
        import generate_mock_data as gm
        import generate_heatmaps as gh
        
        print("\nGenerating data...")
        gm.save_all_data()
        
        print("\nCreating visualizations...")
        gh.generate_all_heatmaps()
        
        print("\n" + "=" * 60)
        print("[DONE] All visualizations generated!")
        print("=" * 60)
        print("\nFiles created in analytics/output/:")
        print("  • veracity_performance.html")
        print("  • multi_search_effectiveness.html")
        print("  • response_times.html")
        print("  • search_coverage_timeline.html")
        print("  • web_search_distribution.html")
        print("\nOpen these HTML files in your browser for interactive viewing.")
        print("\n" + "=" * 60)
        
    except ImportError as e:
        print(f"\n[ERROR] Missing dependencies: {e}")
        print("\nInstall with: pip install pandas plotly numpy kaleido")
        print("Or run: python3 -m pip install --user pandas plotly numpy kaleido")
        sys.exit(1)
    except Exception as e:
        print(f"\n[ERROR] {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == '__main__':
    main()


