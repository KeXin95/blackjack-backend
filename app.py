from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
import numpy as np
from scipy import stats
import pandas as pd

app = Flask(__name__)
CORS(app)

# Configure for Railway deployment
port = int(os.environ.get('PORT', 5001))

# Use absolute paths for Railway deployment
RESULTS_DIR = os.path.join(os.path.dirname(__file__), ".")  # Same directory as app.py
PROCESSED_DIR = os.path.join(os.path.dirname(__file__), "processed_data")

@app.route('/')
def home():
    """Simple health check endpoint"""
    return jsonify({
        "status": "ok",
        "message": "Blackjack API is running",
        "port": port,
        "results_dir": RESULTS_DIR,
        "processed_dir": PROCESSED_DIR
    })

def load_and_process_results(filename):
    """Load pre-processed results for fast API response"""
    strategy_key = filename.replace("_results.json", "").replace("_", "-")
    summary_file = os.path.join(PROCESSED_DIR, f"{strategy_key}_summary.json")
    
    if not os.path.exists(summary_file):
        print(f"Warning: Pre-processed data not found for {filename}")
        print("Run 'python preprocess_data.py' to create optimized data files")
        return None
    
    # Load pre-processed summary data
    with open(summary_file, 'r') as f:
        return json.load(f)

def get_all_processed_strategies():
    """Get all available strategies from processed data files"""
    strategies = {}
    
    if not os.path.exists(PROCESSED_DIR):
        print(f"ERROR: PROCESSED_DIR does not exist: {PROCESSED_DIR}")
        return strategies
    
    # Get all summary files
    summary_files = [f for f in os.listdir(PROCESSED_DIR) if f.endswith('_summary.json')]
    
    for filename in summary_files:
        strategy_key = filename.replace("_summary.json", "")
        summary_file = os.path.join(PROCESSED_DIR, filename)
        
        try:
            with open(summary_file, 'r') as f:
                data = json.load(f)
            
            # Get strategy info based on the key
            info = get_strategy_info_from_key(strategy_key)
            
            strategies[strategy_key] = {
                **data,
                "name": info["name"],
                "description": info["description"]
            }
        except Exception as e:
            print(f"Error loading {filename}: {e}")
            continue
    
    return strategies

def get_strategy_info_from_key(strategy_key):
    """Get strategy name and description based on strategy key"""
    strategy_map = {
        "basic": {
            "name": "Basic Strategy",
            "description": "Follows the mathematically optimal decisions for hitting, standing, and doubling."
        },
        "card-counter": {
            "name": "Card Counter",
            "description": "Adjusts strategy and bets based on the count of high vs. low cards."
        },
        "dealer-weakness": {
            "name": "Dealer Weakness",
            "description": "Stands if dealer shows 2-6 and player has 12+, otherwise hits to 17."
        },
        "mimic-dealer": {
            "name": "Mimic Dealer",
            "description": "Player hits until 17, just like the dealer."
        },
        "martingale": {
            "name": "Martingale + Basic",
            "description": "Uses Basic Strategy for decisions and doubles the bet after every loss."
        }
    }
    
    # Handle fixed threshold strategies
    if strategy_key.startswith("fixed-threshold-"):
        threshold = strategy_key.split("-")[2]
        return {
            "name": f"Fixed Threshold ({threshold})",
            "description": f"Player always hits until their hand value is {threshold} or more."
        }
    
    return strategy_map.get(strategy_key, {
        "name": strategy_key.replace("-", " ").title(),
        "description": "Strategy simulation results."
    })

def get_strategy_info(filename):
    """Get strategy name and description based on filename"""
    strategy_map = {
        "basic_results.json": {
            "name": "Basic Strategy",
            "description": "Follows the mathematically optimal decisions for hitting, standing, and doubling."
        },
        "card_counter_results.json": {
            "name": "Card Counter",
            "description": "Adjusts strategy and bets based on the count of high vs. low cards."
        },
        "dealer_weakness_results.json": {
            "name": "Dealer Weakness",
            "description": "Stands if dealer shows 2-6 and player has 12+, otherwise hits to 17."
        },
        "mimic_dealer_results.json": {
            "name": "Mimic Dealer",
            "description": "Player hits until 17, just like the dealer."
        },
        "martingale_results.json": {
            "name": "Martingale + Basic",
            "description": "Uses Basic Strategy for decisions and doubles the bet after every loss."
        }
    }
    
    # Handle fixed threshold strategies
    if filename.startswith("fixed_threshold_") and filename.endswith("_results.json"):
        threshold = filename.split("_")[2]
        return {
            "name": f"Fixed Threshold ({threshold})",
            "description": f"Player always hits until their hand value is {threshold} or more."
        }
    
    return strategy_map.get(filename, {
        "name": filename.replace("_results.json", "").replace("_", " ").title(),
        "description": "Strategy simulation results."
    })

@app.route('/api/strategies', methods=['GET'])
def get_all_strategies():
    """Get all available strategies with their processed data"""
    strategies = get_all_processed_strategies()
    return jsonify(strategies)

@app.route('/api/strategy/<strategy_key>', methods=['GET'])
def get_strategy(strategy_key):
    """Get data for a specific strategy"""
    filename = f"{strategy_key.replace('-', '_')}_results.json"
    data = load_and_process_results(filename)
    
    if data is None:
        return jsonify({"error": "Strategy not found"}), 404
    
    info = get_strategy_info(filename)
    return jsonify({
        **data,
        "name": info["name"],
        "description": info["description"]
    })

@app.route('/api/comparison', methods=['GET'])
def get_comparison_data():
    """Get comparison data for all strategies"""
    try:
        print(f"PROCESSED_DIR: {PROCESSED_DIR}")
        
        # Check if processed data directory exists
        if not os.path.exists(PROCESSED_DIR):
            print(f"ERROR: PROCESSED_DIR does not exist: {PROCESSED_DIR}")
            return jsonify({"error": "Processed data directory not found"}), 500
        
        # Get all strategies from processed data
        strategies = get_all_processed_strategies()
        print(f"Found {len(strategies)} strategies from processed data")
        
        # Create comparison data - filter to only include fixed threshold 16
        comparison_data = []
        for strategy_key, strategy in strategies.items():
            # Only include fixed threshold 16, skip other fixed thresholds
            if strategy_key.startswith("fixed-threshold-") and strategy_key != "fixed-threshold-16":
                continue
                
            comparison_data.append({
                "name": strategy["name"],
                "Avg Net Winnings": strategy["avgNetPerHand"],
                "ROI (%)": strategy["roi"],
                "Volatility (Std Dev)": strategy["stdDeviation"],
            })
        
        print(f"Returning {len(strategies)} strategies and {len(comparison_data)} comparison items")
        return jsonify({
            "strategies": strategies,
            "comparisonData": comparison_data
        })
        
    except Exception as e:
        print(f"ERROR in get_comparison_data: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

@app.route('/api/quick-comparison', methods=['GET'])
def get_quick_comparison():
    """Get just the basic comparison data for faster initial load"""
    try:
        print(f"PROCESSED_DIR: {PROCESSED_DIR}")
        
        # Check if processed data directory exists
        if not os.path.exists(PROCESSED_DIR):
            print(f"ERROR: PROCESSED_DIR does not exist: {PROCESSED_DIR}")
            return jsonify({"error": "Processed data directory not found"}), 500
        
        # Get all strategies from processed data
        strategies = get_all_processed_strategies()
        print(f"Found {len(strategies)} strategies from processed data")
        
        # Create quick comparison data - filter to only include fixed threshold 16
        comparison_data = []
        for strategy_key, strategy in strategies.items():
            # Only include fixed threshold 16, skip other fixed thresholds
            if strategy_key.startswith("fixed-threshold-") and strategy_key != "fixed-threshold-16":
                continue
                
            comparison_data.append({
                "key": strategy_key,
                "name": strategy["name"],
                "description": strategy["description"],
                "avgNetPerHand": strategy["avgNetPerHand"],
                "roi": strategy["roi"],
                "stdDeviation": strategy["stdDeviation"],
                "winRate": strategy["winRate"],
                "totalWinnings": strategy["totalWinnings"]
            })
        
        print(f"Returning {len(comparison_data)} quick comparison items")
        return jsonify({
            "comparisonData": comparison_data
        })
        
    except Exception as e:
        print(f"ERROR in get_quick_comparison: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5001))
    app.run(host='0.0.0.0', port=port, debug=False) 
