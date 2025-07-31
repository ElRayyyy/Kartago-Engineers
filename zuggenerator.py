#!/usr/bin/env python3
"""
Simplified move generator for Turm & Wächter.

Usage:
    python zuggenerator.py "b36/3b12r3/7/7/1r2RG4/2/BG4/6r1 b"
"""

import sys
import os

# Add parent directory to sys.path to allow imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from core.fen import FenParser

def main():
    if len(sys.argv) < 2:
        print("Example: python zuggenerator.py \"b36/3b12r3/7/7/1r2RG4/2/BG4/6r1 b\"")
        sys.exit(1)
        
    fen_str = sys.argv[1]
    parser = FenParser()
    
    try:
        # Get moves in algebraic notation
        moves = parser.get_move_descriptions(fen_str)
        moves.sort()  # Sort alphabetically for readability
        
        if moves:
            # Output all legal moves, one per line
            for move in moves:
                print(move)
            print(f"\nTotal: {len(moves)} legal moves")
        else:
            print("No legal moves available")
                
    except Exception as e:
        print(f"Error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main() 