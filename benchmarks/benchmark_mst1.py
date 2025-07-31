#!/usr/bin/env python3
"""
Benchmark tests for Turm & Wächter.
Tests the speed of the move generator on different positions:
- Initial position (start of game)
- Midgame position (some pieces captured)
- Endgame position (few pieces left)

Runs 10k iterations to get reliable performance numbers.
"""

import time
import sys
import os
from typing import List, Tuple

# Add parent directory to sys.path to allow imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from core.bitboard import BitboardBoard
from core.bitboard_rules import BitboardRules
from core.fen import FenParser

# Test positions (copied from the README)
INIT_POS = "r1r11RG1r1r1/2r11r12/3r13/7/3b13/2b11b12/b1b11BG1b1b1 r"  # Initial
MID_POS = "3RG1r11/3r333/r36/7/b32b33/7/3BG2b1 b"  # Midgame with some captures
END_POS = "RGBG5/7/7/7/7/7/7 r"  # Endgame (just guardians left)

# For detailed timing info
DEBUG = False

# Number of iterations - more = more accurate but slower
ITERATIONS = 10000

def time_it(func):
    """Simple timing decorator - useful for detailed profiling"""
    def wrapper(*args, **kwargs):
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        if DEBUG:
            print(f"{func.__name__} took {(end - start)*1000:.2f}ms")
        return result
    return wrapper

def benchmark_position(fen: str, name: str, iters: int = ITERATIONS):
    """
    Run benchmark on a specific position
    """
    print(f"\nBenchmarking {name} position")
    print(f"Position: {fen}")
    
    # Setup the board and rules
    parser = FenParser()
    board, player = parser.parse_fen(fen)
    rules = BitboardRules(board)
    rules.current_player = player
    
    # Count legal moves first (for verification)
    # This is outside the timing loop
    moves = rules.get_legal_moves(player)
    print(f"Legal moves: {len(moves)}")
    
    # Main benchmark
    print(f"Running {iters} iterations...")
    
    # Timing code
    start = time.time()
    
    # This is the hotspot where we spend all our time
    for i in range(iters):
        rules.get_legal_moves(player)
        
        # Progress indicator for slow runs
        if DEBUG and i % 1000 == 0 and i > 0:
            sys.stdout.write(".")
            sys.stdout.flush()
            
    end = time.time()
    
    # Calculate stats
    elapsed = end - start
    ms_per_iter = elapsed * 1000 / iters
    
    print(f"Total time: {elapsed:.2f} seconds")
    print(f"Average time: {ms_per_iter:.4f} ms per generation")
    
    return elapsed, ms_per_iter, len(moves)

def run_benchmark_tests():
    """Run benchmarks on all positions"""
    print("\n========== Turm & Wächter Benchmark ==========")
    print("Testing move generator performance")
    
    results = []
    
    # Test initial position (start of game)
    init_time, init_avg, init_moves = benchmark_position(
        INIT_POS, "Initial", ITERATIONS
    )
    results.append(("Initial", init_time, init_avg, init_moves))
    
    # Test midgame position
    mid_time, mid_avg, mid_moves = benchmark_position(
        MID_POS, "Midgame", ITERATIONS
    )
    results.append(("Midgame", mid_time, mid_avg, mid_moves))
    
    # Test endgame position (few pieces)
    end_time, end_avg, end_moves = benchmark_position(
        END_POS, "Endgame", ITERATIONS
    )
    results.append(("Endgame", end_time, end_avg, end_moves))
    
    # Print a nice summary table
    print("\n=== Results Summary ===")
    print(f"Position   | Moves | Total Time (s)  | Avg (ms/move)")
    print(f"-----------|-------|-----------------|------------------")
    
    for pos, total, avg, moves in results:
        print(f"{pos:<10} | {moves:<5} | {total:<15.2f} | {avg:<15.4f}")
    
    print("\nDone! Benchmarks completed successfully.")
    
    if DEBUG:
        print("\nNotes:")
        print("- Run with DEBUG=True for more timing info")
        print("- Increase ITERATIONS for more accurate results")

if __name__ == "__main__":
    run_benchmark_tests() 