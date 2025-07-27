import os
import json
import pandas as pd
import numpy as np
from pathlib import Path

RESULTS_DIR = "../results"
PROCESSED_DIR = "processed_data"

def process_json_to_parquet():
    """Convert all JSON result files to optimized Parquet format"""
    
    # Create processed data directory
    os.makedirs(PROCESSED_DIR, exist_ok=True)
    
    # Get all result files
    result_files = [f for f in os.listdir(RESULTS_DIR) if f.endswith('_results.json')]
    
    print(f"Found {len(result_files)} result files to process...")
    
    for filename in result_files:
        print(f"\nProcessing {filename}...")
        
        filepath = os.path.join(RESULTS_DIR, filename)
        strategy_key = filename.replace("_results.json", "").replace("_", "-")
        
        # Read JSON file
        print(f"  Reading JSON file...")
        with open(filepath, 'r') as f:
            data = json.load(f)
        
        # Convert to DataFrame
        df = pd.DataFrame(data)
        
        # Calculate basic statistics
        print(f"  Calculating statistics...")
        profits = df['profit'].values
        bets = df.get('bet', 10).values if 'bet' in df.columns else np.full(len(df), 10)
        
        total_profit = profits.sum()
        total_wagered = bets.sum()
        win_rate = np.sum(profits > 0) / len(profits) * 100
        avg_net_per_hand = profits.mean()
        std_deviation = profits.std()
        roi = (total_profit / total_wagered * 100) if total_wagered > 0 else 0
        
        # Create winnings distribution
        winnings_ranges = [
            (-float('inf'), -20, "Big Loss (<-$20)"),
            (-20, 0, "Small Loss (-$20 to $0)"),
            (0, 20, "Small Win ($0 to $20)"),
            (20, float('inf'), "Big Win (>$20)")
        ]
        
        winnings_distribution = []
        for low, high, name in winnings_ranges:
            if high == float('inf'):
                count = np.sum(profits >= low)
            elif low == -float('inf'):
                count = np.sum(profits <= high)
            else:
                count = np.sum((profits > low) & (profits <= high))
            winnings_distribution.append({"name": name, "value": int(count)})
        
        # Create bankroll history (sampled)
        cumulative_profits = np.cumsum(profits)
        sample_size = min(500, len(cumulative_profits))
        indices = np.linspace(0, len(cumulative_profits) - 1, sample_size, dtype=int)
        
        bankroll_history = [
            {"hand": int(i), "bankroll": float(cumulative_profits[i])}
            for i in indices
        ]
        
        # Create summary statistics
        summary_stats = {
            "simulations": len(profits),
            "totalWinnings": float(total_profit),
            "winRate": float(win_rate),
            "avgNetPerHand": float(avg_net_per_hand),
            "stdDeviation": float(std_deviation),
            "roi": float(roi),
            "winningsDistribution": winnings_distribution,
            "bankrollHistory": bankroll_history
        }
        
        # Save processed data
        print(f"  Saving processed data...")
        
        # Save summary stats
        summary_file = os.path.join(PROCESSED_DIR, f"{strategy_key}_summary.json")
        with open(summary_file, 'w') as f:
            json.dump(summary_stats, f, indent=2)
        
        # Save sampled data for charts (much smaller)
        sampled_df = df.iloc[indices]
        parquet_file = os.path.join(PROCESSED_DIR, f"{strategy_key}_sampled.parquet")
        sampled_df.to_parquet(parquet_file, index=False)
        
        print(f"  ✓ Saved {summary_file}")
        print(f"  ✓ Saved {parquet_file}")
    
    print(f"\n✅ All files processed successfully!")
    print(f"Processed data saved in: {PROCESSED_DIR}/")

if __name__ == "__main__":
    process_json_to_parquet() 