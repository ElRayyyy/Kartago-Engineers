#!/usr/bin/env python3
"""
Apply optimized parameters to the AI.
This script loads optimized parameters and can update the default parameters in evaluate.py
"""

import sys
import os
import json
import shutil
from typing import Dict

# Add parent directory to sys.path for imports
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from evaluate import DEFAULT_PARAMS
from alpha_beta_ki import choose_best_move

def load_optimized_params(filename: str = "optimized_params.json") -> Dict:
    """Load optimized parameters from file (search in same folder by default)"""
    if not os.path.isabs(filename):
        filename = os.path.join(os.path.dirname(__file__), filename)
    try:
        with open(filename, 'r') as f:
            params = json.load(f)
        return params
    except FileNotFoundError:
        print(f"Error: {filename} not found. Run parameter_optimizer.py first.")
        return None
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON in {filename}")
        return None

def update_evaluate_py(params: Dict, backup: bool = True):
    """Update the DEFAULT_PARAMS in evaluate.py with optimized parameters"""
    evaluate_file = "evaluate.py"
    
    if backup:
        shutil.copy(evaluate_file, f"{evaluate_file}.backup")
        print(f"Backup created: {evaluate_file}.backup")
    
    # Read the current file
    with open(evaluate_file, 'r') as f:
        content = f.read()
    
    # Create the new DEFAULT_PARAMS string
    new_params_str = "DEFAULT_PARAMS = {\n"
    for key, value in params.items():
        new_params_str += f"    '{key}': {value},\n"
    new_params_str += "}"
    
    # Replace the DEFAULT_PARAMS definition
    import re
    pattern = r'DEFAULT_PARAMS\s*=\s*{[^}]*}'
    new_content = re.sub(pattern, new_params_str, content, flags=re.DOTALL)
    
    # Write back to file
    with open(evaluate_file, 'w') as f:
        f.write(new_content)
    
    print(f"Updated {evaluate_file} with optimized parameters")

def test_optimized_ai(params: Dict, test_fen: str = None):
    """Test the AI with optimized parameters"""
    if test_fen is None:
        test_fen = "r1r11RG1r1r1/2r11r12/3r13/7/3b13/2b11b12/b1b11BG1b1b1 r"
    
    print(f"Testing AI with optimized parameters on position: {test_fen}")
    
    # Test with default parameters
    print("\nDefault parameters:")
    default_move = choose_best_move(test_fen, DEFAULT_PARAMS)
    if default_move:
        from core.fen import FenParser
        print(f"  Move: {FenParser.describe_move(*default_move)}")
    else:
        print("  No move found")
    
    # Test with optimized parameters
    print("\nOptimized parameters:")
    optimized_move = choose_best_move(test_fen, params)
    if optimized_move:
        from core.fen import FenParser
        print(f"  Move: {FenParser.describe_move(*optimized_move)}")
    else:
        print("  No move found")

def compare_params(optimized: Dict, default: Dict = None):
    """Compare optimized parameters with default parameters"""
    if default is None:
        default = DEFAULT_PARAMS
    
    print("Parameter comparison:")
    print(f"{'Parameter':<20} {'Default':<12} {'Optimized':<12} {'Change':<10}")
    print("-" * 60)
    
    for param in default:
        def_val = default[param]
        opt_val = optimized.get(param, def_val)
        change = ((opt_val - def_val) / def_val) * 100 if def_val != 0 else 0
        
        print(f"{param:<20} {def_val:<12.2f} {opt_val:<12.2f} {change:+6.1f}%")

def main():
    """Main function to apply optimized parameters"""
    print("Turm & Wächter AI - Apply Optimized Parameters")
    print("=" * 50)
    
    # Load optimized parameters
    params = load_optimized_params()
    if params is None:
        return
    
    print("Loaded optimized parameters:")
    for key, value in params.items():
        print(f"  {key}: {value:.2f}")
    
    # Compare with defaults
    print("\n" + "=" * 50)
    compare_params(params)
    
    # Test the AI
    print("\n" + "=" * 50)
    test_optimized_ai(params)
    
    # Ask user if they want to permanently apply the changes
    print("\n" + "=" * 50)
    response = input("Do you want to permanently update evaluate.py with these parameters? (y/n): ")
    
    if response.lower() == 'y':
        update_evaluate_py(params)
        print("Parameters applied successfully!")
        print("The AI will now use the optimized parameters by default.")
    else:
        print("Parameters not applied. You can always run this script again.")
    
    print("\nTo use optimized parameters without permanently changing the code:")
    print("  from apply_optimized_params import load_optimized_params")
    print("  params = load_optimized_params()")
    print("  move = choose_best_move(fen_string, params)")

if __name__ == "__main__":
    main() 