#!/usr/bin/env python3
import os, sys
# Ensure project root is on sys.path so we can import alpha_beta_ki, core, etc.
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
import time
from alpha_beta_ki import choose_best_move
from core.fen import FenParser
from evaluate import DEFAULT_PARAMS

class TournamentRunner:
    def __init__(self, max_moves: int = 20, move_timeout: float = 0.5):
        """Simple tournament runner.

        Args:
            max_moves: per-game ply cap before declaring a draw.
            move_timeout: hard wall-clock seconds for a single move before we fall back to a random move.
        """
        self.parser = FenParser()
        self.max_moves = max_moves
        self.move_timeout = move_timeout
    
    def play_game(self, params1, params2, starting_fen=None):
        """
        Play a ultra-fast game between two AI with different parameters.
        Returns: 1 if params1 wins, 2 if params2 wins, 0 if draw
        """
        # Use simpler starting positions that lead to quicker games
        if starting_fen is None:
            starting_positions = [
                # Standard position
                "r1r11RG1r1r1/2r11r12/3r13/7/3b13/2b11b12/b1b11BG1b1b1 r",
                # More aggressive positions that should end faster
                "r1r11RG1r1r1/2r21r12/7/3r23b3/7/2b11b12/b1b11BG1b1b1 r",
                "r1r12RG1r12/7/2r13/7/3b13/7/b1b12BG1b1b1 b",
            ]
            # Use hash to deterministically pick position but vary between param sets
            pos_index = (hash(str(params1) + str(params2)) % len(starting_positions))
            current_fen = starting_positions[pos_index]
        else:
            current_fen = starting_fen
        
        move_count = 0
        
        while move_count < self.max_moves:
            board, current_player = self.parser.parse_fen(current_fen)
            
            # Quick win check
            from win_check import check_win_by_distance_or_capture
            if check_win_by_distance_or_capture(board, 1):
                return 1
            if check_win_by_distance_or_capture(board, 2):
                return 2
            
            # Choose parameters based on current player
            eval_params = params1 if current_player == 1 else params2
            
            # Get move with strict timeout
            try:
                start_time = time.time()
                best_move = choose_best_move(current_fen, eval_params)
                move_time = time.time() - start_time
                
                # Enforce strict timeout
                if move_time > self.move_timeout or not best_move:
                    # Use fallback random move
                    from core.bitboard_rules import BitboardRules
                    rules = BitboardRules(board)
                    rules.current_player = current_player
                    legal_moves = rules.get_legal_moves(current_player)
                    if legal_moves:
                        import random
                        best_move = random.choice(legal_moves[:min(5, len(legal_moves))])  # Only consider first 5 moves
                    else:
                        # No legal moves - game over
                        return 3 - current_player
                
                # Make the move
                from core.bitboard_rules import BitboardRules
                rules = BitboardRules(board)
                rules.current_player = current_player
                rules.make_move(*best_move)
                
                # Update FEN for next iteration
                current_fen = rules.board.to_fen(3 - current_player)
                move_count += 1
                
            except Exception as e:
                # Any error - other player wins
                return 3 - current_player
        
        # Game exceeded move limit - draw
        return 0
    
    def run_tournament(self, params1, params2, num_games=2):
        """
        Run ultra-fast tournament between two parameter sets.
        Returns: (wins_for_params1, wins_for_params2, draws)
        """
        wins1 = 0
        wins2 = 0
        draws = 0
        
        print(f" {num_games}g", end="", flush=True)
        
        for game_num in range(num_games):
            # Alternate who plays first
            if game_num % 2 == 0:
                result = self.play_game(params1, params2)
            else:
                # Swap and invert result
                result = self.play_game(params2, params1)
                if result == 1:
                    result = 2
                elif result == 2:
                    result = 1
            
            if result == 1:
                wins1 += 1
            elif result == 2:
                wins2 += 1
            else:
                draws += 1
            
            # Simple progress
            print(".", end="", flush=True)
        
        print(f" {wins1}-{wins2}-{draws}")
        return wins1, wins2, draws
    
    def evaluate_params(self, params, baseline, num_games=2):
        """
        Evaluate parameter set against baseline.
        Returns score representing how much better params is than baseline.
        """
        wins1, wins2, draws = self.run_tournament(params, baseline, num_games)
        
        total_games = wins1 + wins2 + draws
        if total_games == 0:
            return 0.0
        
        # Score based on win rate with big bonus for decisive games
        win_rate = wins1 / total_games
        decisiveness_bonus = (1.0 - draws / total_games) * 0.3  # Big bonus for no draws
        
        return win_rate + decisiveness_bonus


def main():
    """Test the ultra-fast tournament runner"""
    runner = TournamentRunner(max_moves=20, move_timeout=0.5)
    
    print("Testing ultra-fast tournament runner...")
    
    # Create very different parameter sets for testing
    params1 = DEFAULT_PARAMS.copy()
    params2 = DEFAULT_PARAMS.copy()
    
    # Make params2 much more aggressive
    params2['guardian_advance'] = params2['guardian_advance'] * 1.8
    params2['aggression'] = params2['aggression'] * 2.0
    params2['tower_height'] = params2['tower_height'] * 0.5
    params2['positioning'] = params2['positioning'] * 1.5
    
    print(f"Params1: Conservative")
    print(f"Params2: Aggressive")
    
    wins1, wins2, draws = runner.run_tournament(params1, params2, num_games=4)
    print(f"Results: Conservative {wins1}, Aggressive {wins2}, Draws {draws}")
    
    score = runner.evaluate_params(params1, params2, num_games=4)
    print(f"Score: {score:.2f}")
    
    # Quick test of parameter optimizer
    print("\nTesting optimizer...")
    try:
        from ML_mst4.parameter_optimizer import ParameterOptimizer
        optimizer = ParameterOptimizer(population_size=3)
        print("Optimizer loaded successfully!")
        
        # Test a single evaluation
        test_params = DEFAULT_PARAMS.copy()
        test_params['aggression'] *= 1.5
        score = optimizer.evaluate_individual(test_params)
        print(f"Test evaluation score: {score:.2f}")
        
    except Exception as e:
        print(f"Optimizer test failed: {e}")


if __name__ == "__main__":
    main() 