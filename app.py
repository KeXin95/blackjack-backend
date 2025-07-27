from flask import Flask, jsonify, request
from flask_cors import CORS
import json
import os
import numpy as np
from scipy import stats
import pandas as pd

app = Flask(__name__)
CORS(app)

RESULTS_DIR = "../results"
PROCESSED_DIR = "processed_data"

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
    strategies = {}
    
    # Get all result files
    result_files = [f for f in os.listdir(RESULTS_DIR) if f.endswith('_results.json')]
    
    for filename in result_files:
        strategy_key = filename.replace("_results.json", "").replace("_", "-")
        
        # Load and process the data
        data = load_and_process_results(filename)
        if data is None:
            continue
            
        # Get strategy info
        info = get_strategy_info(filename)
        
        # Combine data and info
        strategies[strategy_key] = {
            **data,
            "name": info["name"],
            "description": info["description"]
        }
    
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
    print("HELLO")
    strategies = {}
    
    result_files = [f for f in os.listdir(RESULTS_DIR) if f.endswith('_results.json')]
    
    for filename in result_files:
        print(filename)
        strategy_key = filename.replace("_results.json", "").replace("_", "-")
        data = load_and_process_results(filename)
        
        if data is None:
            continue
            
        info = get_strategy_info(filename)
        strategies[strategy_key] = {
            **data,
            "name": info["name"],
            "description": info["description"]
        }
    
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
    print(comparison_data)
    return jsonify({
        "strategies": strategies,
        "comparisonData": comparison_data
    })

@app.route('/api/quick-comparison', methods=['GET'])
def get_quick_comparison():
    """Get just the basic comparison data for faster initial load"""
    comparison_data = []
    
    result_files = [f for f in os.listdir(RESULTS_DIR) if f.endswith('_results.json')]
    
    for filename in result_files:
        strategy_key = filename.replace("_results.json", "").replace("_", "-")
        info = get_strategy_info(filename)
        
        # Load minimal data for quick comparison
        data = load_and_process_results(filename)
        if data is None:
            continue
            
        comparison_data.append({
            "key": strategy_key,
            "name": info["name"],
            "description": info["description"],
            "avgNetPerHand": data["avgNetPerHand"],
            "roi": data["roi"],
            "stdDeviation": data["stdDeviation"],
            "winRate": data["winRate"],
            "totalWinnings": data["totalWinnings"]
        })
    
    return jsonify({
        "comparisonData": comparison_data
    })

if __name__ == '__main__':
    app.run(debug=True, port=5001) 
