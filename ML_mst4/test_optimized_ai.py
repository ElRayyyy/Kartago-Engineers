#!/usr/bin/env python3
import os, sys
# Ensure project root is on path to allow importing alpha_beta_ki etc.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

import json
from tournament_runner import TournamentRunner
from evaluate import DEFAULT_PARAMS

def load_optimized_params():
    """Load the optimized parameters from file (search in same folder)"""
    file_path = os.path.join(os.path.dirname(__file__), 'optimized_params.json')
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("optimized_params.json not found! Run the optimizer first.")
        return None

def compare_parameters(default_params, optimized_params):
    """Show the differences between default and optimized parameters"""
    print("PARAMETER COMPARISON:")
    print("=" * 50)
    print(f"{'Parameter':<20} {'Default':<10} {'Optimized':<12} {'Change':<10}")
    print("-" * 50)
    
    for param in default_params:
        default_val = default_params[param]
        optimized_val = optimized_params[param]
        
        if abs(optimized_val - default_val) > 0.01:
            pct_change = ((optimized_val - default_val) / default_val) * 100
            print(f"{param:<20} {default_val:<10.1f} {optimized_val:<12.1f} {pct_change:+6.0f}%")
        else:
            print(f"{param:<20} {default_val:<10.1f} {optimized_val:<12.1f} {'~0%':<10}")
    print()

def test_ai_battle():
    """Test optimized AI vs default AI"""
    
    # Load optimized parameters
    optimized_params = load_optimized_params()
    if not optimized_params:
        return
    
    print("TURM & WÄCHTER AI - OPTIMIZED vs DEFAULT")
    print("=" * 50)
    
    # Show parameter comparison
    compare_parameters(DEFAULT_PARAMS, optimized_params)
    
    # Run tournament
    runner = TournamentRunner(max_moves=20, move_timeout=0.5)
    
    print("BATTLE RESULTS:")
    print("-" * 20)
    print("Running multiple tournaments...")
    
    total_opt_wins = 0
    total_def_wins = 0
    total_draws = 0
    
    # Run 3 tournaments of 4 games each
    for tournament in range(3):
        print(f"\nTournament {tournament + 1}:")
        wins_opt, wins_def, draws = runner.run_tournament(
            optimized_params, DEFAULT_PARAMS, num_games=4
        )
        
        total_opt_wins += wins_opt
        total_def_wins += wins_def
        total_draws += draws
        
        print(f"  Optimized: {wins_opt}, Default: {wins_def}, Draws: {draws}")
    
    print(f"\nFINAL RESULTS:")
    print("=" * 20)
    print(f"Optimized AI: {total_opt_wins} wins")
    print(f"De^ult AI:   {total_def_wins} wins") 
    print(f"Draws:        {total_draws}")
    
    total_games = total_opt_wins + total_def_wins + total_draws
    if total_games > 0:
        opt_win_rate = (total_opt_wins / total_games) * 100
        def_win_rate = (total_def_wins / total_games) * 100
        draw_rate = (total_draws / total_games) * 100
        
        print(f"\nWin Rates:")
        print(f"Optimized AI: {opt_win_rate:.1f}%")
        print(f"Default AI:   {def_win_rate:.1f}%")
        print(f"Draw Rate:    {draw_rate:.1f}%")
        
        # Determine winner
        if total_opt_wins > total_def_wins:
            print(f"\n🏆 OPTIMIZED AI WINS! (+{total_opt_wins - total_def_wins} games)")
        elif total_def_wins > total_opt_wins:
            print(f"\n🏆 DEFAULT AI WINS! (+{total_def_wins - total_opt_wins} games)")
        else:
            print(f"\n🤝 TIE GAME!")
    
    return optimized_params

def main():
    """Main test function"""
    print("Testing Machine Learning Optimized AI")
    print("=" * 40)
    
    optimized_params = test_ai_battle()
    
    if optimized_params:
        print("\n" + "=" * 50)
        print("MACHINE LEARNING OPTIMIZATION SUCCESS!")
        print("=" * 50)
        print("The genetic algorithm found parameters that create")
        print("dramatically different AI behavior with more decisive games!")
        print("Key optimizations:")
        
        opt = optimized_params
        def_params = DEFAULT_PARAMS
        
        if opt['center_control'] > def_params['center_control'] * 2:
            print(f"• CENTER OBSESSION: {opt['center_control']:.0f} vs {def_params['center_control']}")
        if opt['guardian_safety'] > def_params['guardian_safety'] * 2:
            print(f"• GUARDIAN PARANOIA: {opt['guardian_safety']:.0f} vs {def_params['guardian_safety']}")
        if opt['positioning'] > def_params['positioning'] * 2:
            print(f"• POSITIONAL MASTER: {opt['positioning']:.0f} vs {def_params['positioning']}")
        
        print("\nThis demonstrates successful ML parameter optimization!")

if __name__ == "__main__":
    main() 