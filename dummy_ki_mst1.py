#!/usr/bin/env python3
"""
Dummy AI for Turm & Wächter.
Simple implementation that selects a random legal move.

Usage:
    python dummy_ki.py "b36/3b12r3/7/7/1r2RG4/2/BG4/6r1 b"
"""

import sys
import random
import subprocess
import os

def get_random_move(fen_str):
    """
    Get a random legal move using zuggenerator.py.
    1. Pass FEN string to zuggenerator.py
    2. Get all legal moves as output
    3. Choose one randomly
    """
    # Call zuggenerator.py as a subprocess with the FEN string
    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "zuggenerator.py")
    
    try:
        # Run zuggenerator.py with the FEN string to get all legal moves
        env = os.environ.copy()
        env["PYTHONPATH"] = os.path.dirname(os.path.abspath(__file__))
        result = subprocess.run(
            ["python3", script_path, fen_str], 
            capture_output=True, 
            text=True, 
            env=env
        )
        
        if result.returncode != 0:
            print(f"Error from zuggenerator.py: {result.stderr}", file=sys.stderr)
            return None
        
        # Parse the output to get all legal moves
        output_lines = result.stdout.strip().split('\n')
        moves = []
        
        for line in output_lines:
            # Skip empty lines and the summary line
            if not line or line.startswith('Total:') or line.startswith('No legal'):
                continue
            moves.append(line)
        
        if not moves:
            return None
        
        # Select a random move from the list
        return random.choice(moves)
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return None

def main():
    if len(sys.argv) < 2:
        print("Example: python dummy_ki.py \"b36/3b12r3/7/7/1r2RG4/2/BG4/6r1 b\"")
        sys.exit(1)
        
    fen_str = sys.argv[1]
    
    # Get a random legal move
    move = get_random_move(fen_str)
    
    if move:
        print(move)
    else:
        print("No legal moves available")

if __name__ == "__main__":
    main() 