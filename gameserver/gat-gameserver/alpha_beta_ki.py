#!/usr/bin/env python3
import sys
import time
import json
from copy import deepcopy

from core.fen import FenParser
from core.bitboard_rules import BitboardRules
from evaluate import evaluate, DEFAULT_PARAMS
from win_check import check_win_by_distance_or_capture

# Speed-optimized settings for fast games
MAX_DEPTH = 4  # Very shallow for speed
TIME_BUFFER = 0.05  # Small buffer
NULL_MOVE_REDUCTION = 1  # Reduced

WIN_SCORE = 100000
nodes_visited = 0
ttable = {}
time_start = 0
time_budget = 0

# Global ML-optimized parameters
ML_OPTIMIZED_PARAMS = None

def load_ml_optimized_params():
    """Load ML-optimized parameters from ML_mst4 folder, fallback to defaults"""
    global ML_OPTIMIZED_PARAMS
    
    if ML_OPTIMIZED_PARAMS is not None:
        return ML_OPTIMIZED_PARAMS
    
    try:
        # Look for optimized parameters in ML_mst4 folder
        with open('C:/Users/ylang/Downloads/turm_waechter_ai/turm_waechter_ai/ML_mst4/optimized_params.json', 'r') as f:
            ML_OPTIMIZED_PARAMS = json.load(f)
            print(f"✓ Loaded ML-optimized parameters from ML_mst4/optimized_params.json")
            return ML_OPTIMIZED_PARAMS
    except FileNotFoundError:
        print("⚠ ML_mst4/optimized_params.json not found, using default parameters")
        print("  Run ML_mst4/parameter_optimizer.py to generate ML-optimized parameters")
        ML_OPTIMIZED_PARAMS = DEFAULT_PARAMS.copy()
        return ML_OPTIMIZED_PARAMS
    except json.JSONDecodeError:
        print("⚠ Invalid ML_mst4/optimized_params.json, using default parameters")
        ML_OPTIMIZED_PARAMS = DEFAULT_PARAMS.copy()
        return ML_OPTIMIZED_PARAMS

def get_evaluation_params():
    """Get the best available evaluation parameters (ML-optimized or default)"""
    return load_ml_optimized_params()

def count_pieces(fen_str):
    """Fast piece counting for game phase detection"""
    return fen_str.count('r') + fen_str.count('b') + fen_str.count('RG') + fen_str.count('BG')


def count_my_pieces(fen_str):
    """Count current player's pieces"""
    player = 1 if fen_str.endswith(' r') else 2
    if player == 1:  # Red to move, count red pieces
        return fen_str.count('r') + fen_str.count('RG')
    else:  # Blue to move, count blue pieces
        return fen_str.count('b') + fen_str.count('BG')


def count_enemy_pieces(fen_str):
    """Count enemy pieces based on current player"""
    player = 1 if fen_str.endswith(' r') else 2
    if player == 1:  # Red to move, count blue pieces
        return fen_str.count('b') + fen_str.count('BG')
    else:  # Blue to move, count red pieces
        return fen_str.count('r') + fen_str.count('RG')


def diff_of_pieces(fen_str):
    """Calculate piece difference (my_pieces - enemy_pieces)"""
    my_pieces = count_my_pieces(fen_str)
    enemy_pieces = count_enemy_pieces(fen_str)
    return my_pieces - enemy_pieces


def count_enemy_pieces_in_half(fen_str):
    """Count enemy pieces in our half of the board (critical invasion detection)"""
    player = 1 if fen_str.endswith(' r') else 2
    rows = fen_str.split()[0].split('/')
    
    enemy_count = 0
    
    if player == 1:  # Red player - our half is rows 4-6 (bottom)
        our_half_rows = rows[4:7]  # Last 3 rows
        enemy_pieces = ['b', 'BG']
    else:  # Blue player - our half is rows 0-2 (top)
        our_half_rows = rows[0:3]  # First 3 rows
        enemy_pieces = ['r', 'RG']
    
    for row in our_half_rows:
        for piece in enemy_pieces:
            enemy_count += row.count(piece)
    
    return enemy_count


def detect_game_phase(fen_str):
    """Determine opening/midgame/endgame/critical based on material and danger."""
    piece_diff = diff_of_pieces(fen_str)
    enemy_in_half = count_enemy_pieces_in_half(fen_str)
    my_pieces = count_my_pieces(fen_str)
    enemy_pieces = count_enemy_pieces(fen_str)
    total = my_pieces + enemy_pieces

    if total >= 12:
        base = 'opening'
    elif total >= 7:
        base = 'midgame'
    else:
        base = 'endgame'

    crit = 0
    if piece_diff <= -3:
        crit += 2
    elif piece_diff <= -1:
        crit += 1
    if enemy_in_half >= 3:
        crit += 2
    elif enemy_in_half >= 1:
        crit += 1
    if my_pieces <= 2 or enemy_pieces <= 2:
        crit += 3

    if crit >= 3:
        return 'critical'
    if crit >= 1 and base != 'endgame':
        return base + '_critical'
    return base


def allocate_time(fen_str):
    """Map game phase to time budget - more time for critical situations"""
    phase = detect_game_phase(fen_str)
    mapping = {
        'opening': 0.2,
        'midgame': 0.3,
        'opening_critical': 0.4,
        'midgame_critical':0.5,
        'critical': 0.5,
        'endgame': 0.2,
        'endgame_critical': 0.2,
    }
    return mapping.get(phase, 0.2)


def order_moves_fast(rules, moves):
    """MUCH faster move ordering without expensive deepcopy operations"""
    if not moves:
        return moves
    
    # Simple heuristic ordering without game state evaluation
    ordered_moves = []
    
    # Priority 1: Guardian moves (likely important)
    guardian_moves = []
    # Priority 2: Captures (moves to occupied squares)
    capture_moves = []
    # Priority 3: Other moves
    other_moves = []
    
    for mv in moves:
        frm, to, h = mv
        
        # Check if this is a guardian move (piece type at source)
        piece_type = rules.board.get_top_piece_type(*frm)
        if piece_type and piece_type.name == 'WAECHTER':
            guardian_moves.append(mv)
            continue
        
        # Check if target square is occupied (potential capture)
        target_owner = rules.board.get_stack_owner(*to)
        if target_owner and target_owner != rules.current_player:
            capture_moves.append(mv)
            continue
        
        other_moves.append(mv)
    
    # Return in priority order
    return guardian_moves + capture_moves + other_moves


def negamax(rules, depth, alpha, beta, player, stop_time, eval_params=None):
    """Negamax with α-β, simplified for speed"""
    global nodes_visited, ttable
    
    # Quick time cutoff
    if time.time() >= stop_time - TIME_BUFFER:
        raise TimeoutError
    
    nodes_visited += 1

    # Simple transposition lookup (reduced key for speed)
    fen = rules.board.to_fen(player)
    key = (hash(fen) % 10000, depth)  # Simpler hash for speed
    if key in ttable:
        return ttable[key]

    # Terminal checks
    if check_win_by_distance_or_capture(rules.board, player):
        ttable[key] = WIN_SCORE
        return WIN_SCORE
    if check_win_by_distance_or_capture(rules.board, 3 - player):
        ttable[key] = -WIN_SCORE
        return -WIN_SCORE

    moves = rules.get_legal_moves(player)
    if depth == 0 or not moves:
        # Use ML-optimized parameters if none provided
        if eval_params is None:
            eval_params = get_evaluation_params()
        val = evaluate(fen, eval_params)
        ttable[key] = val
        return val

    # Simplified null-move pruning (only at higher depths)
    if depth > 2:
        null_rules = deepcopy(rules)
        null_rules.current_player = 3 - player
        val = -negamax(
            null_rules,
            depth - 1 - NULL_MOVE_REDUCTION,
            -beta,
            -alpha,
            player,
            stop_time,
            eval_params
        )
        if val >= beta:
            ttable[key] = beta
            return beta

    # Main search with fast move ordering
    best = -float('inf')
    for mv in order_moves_fast(rules, moves):
        child = deepcopy(rules)
        child.make_move(*mv)
        child.current_player = 3 - player
        score = -negamax(child, depth - 1, -beta, -alpha, 3 - player, stop_time, eval_params)
        best = max(best, score)
        alpha = max(alpha, best)
        if best >= WIN_SCORE or alpha >= beta:
            break

    ttable[key] = best
    return best


def iterative_deepening(rules, budget, eval_params=None):
    """Run negamax from depth=1…MAX_DEPTH until time runs out"""
    global nodes_visited, ttable, time_start, time_budget
    nodes_visited = 0
    ttable.clear()
    time_start = time.time()
    time_budget = budget
    stop_time = time_start + budget

    # Use ML-optimized parameters if none provided
    if eval_params is None:
        eval_params = get_evaluation_params()

    root_moves = order_moves_fast(rules, rules.get_legal_moves(rules.current_player))
    best_mv = None

    for depth in range(1, MAX_DEPTH + 1):
        try:
            alpha, beta = -float('inf'), float('inf')
            local_best = -float('inf')
            for mv in root_moves:
                if time.time() >= stop_time - TIME_BUFFER:
                    raise TimeoutError
                child = deepcopy(rules)
                child.make_move(*mv)
                child.current_player = 3 - rules.current_player
                score = -negamax(child, depth - 1, -beta, -alpha, 3 - rules.current_player, stop_time, eval_params)
                if score > local_best:
                    local_best, best_mv = score, mv
                alpha = max(alpha, score)
                if local_best >= WIN_SCORE:
                    return best_mv
        except TimeoutError:
            break

    return best_mv


def choose_best_move(fen_str, eval_params=None):
    """Choose the best move using ML-optimized parameters by default"""
    parser = FenParser()
    board, player = parser.parse_fen(fen_str)
    rules = BitboardRules(board)
    rules.current_player = player

    # Use ML-optimized parameters if none provided
    if eval_params is None:
        eval_params = get_evaluation_params()

    budget = allocate_time(fen_str)

    # Quick win check
    moves = order_moves_fast(rules, rules.get_legal_moves(player))
    for mv in moves[:3]:  # Only check first 3 moves for speed
        tmp = deepcopy(rules)
        tmp.make_move(*mv)
        if check_win_by_distance_or_capture(tmp.board, player):
            return mv

    best_move = iterative_deepening(rules, budget, eval_params)
    return best_move


def show_parameter_info(fen_str=None):
    """Show information about the parameters being used and game situation"""
    params = get_evaluation_params()
    
    if params == DEFAULT_PARAMS:
        print("")
    else:
        #print("Using ML-OPTIMIZED parameters:")
        #print("Key optimizations vs defaults:")
        
        significant_changes = []
        for param, value in params.items():
            default_val = DEFAULT_PARAMS[param]
            if abs(value - default_val) > 0.01:
                pct_change = ((value - default_val) / default_val) * 100
                if abs(pct_change) > 50:  # Only show major changes
                    significant_changes.append((abs(pct_change), param, value, default_val, pct_change))
        
        # Show top 3 biggest changes
        significant_changes.sort(reverse=True)
        for _, param, value, default_val, pct_change in significant_changes[:3]:
            print(f"  • {param}: {value:.1f} (was {default_val}, {pct_change:+.0f}%)")
    
    # Show game phase analysis if FEN provided
    if fen_str:
        phase = detect_game_phase(fen_str)
        time_budget = allocate_time(fen_str)
        
        # Critical situation indicators
        '''
        if 'critical' in phase:
            if phase == 'critical':
                print(f"🚨 CRITICAL situation detected! (time: {time_budget}s)")
            else:
                print(f"⚠️  {phase.upper()} situation (time: {time_budget}s)")
        else:
            print(f"📊 Game phase: {phase} (time: {time_budget}s)")'''
        
        # Show danger analysis
        piece_diff = diff_of_pieces(fen_str)
        enemy_in_half = count_enemy_pieces_in_half(fen_str)
        my_pieces = count_my_pieces(fen_str)
        '''
        if piece_diff <= -3:
            print(f"⚔️  Material disadvantage: {piece_diff}")
        if enemy_in_half >= 3:
            print(f"🛡️  Enemy invasion: {enemy_in_half} pieces in our half")
        if my_pieces <= 2:
            print(f"💀 Low material: only {my_pieces} pieces remaining")'''


def format_move_description(best_move):
    """Format move in a user-friendly way"""
    if len(best_move) == 3:
        from_pos, to_pos, height = best_move
        
        # Convert coordinates to chess-like notation (A1-G7)
        def coord_to_notation(x, y):
            return f"{chr(ord('A') + x)}{7 - y}"
        
        from_notation = coord_to_notation(*from_pos)
        to_notation = coord_to_notation(*to_pos)
        
        return f"{from_notation}-{to_notation}-{height}"
    else:
        return str(best_move)

def main():
    if len(sys.argv) < 2:
        print("Usage: python alpha_beta_ki.py \"FEN_STRING\"")
        sys.exit(1)
    fen_str = sys.argv[1]

    # Show parameter and situation information
    show_parameter_info(fen_str)
    print()

    start_time = time.time()
    best_move = choose_best_move(fen_str)  # Now automatically uses ML params
    end_time = time.time()

    if best_move:
        move_str = format_move_description(best_move)
        print(f"🤖 ML-Optimized AI move: {move_str}")
    else:
        print("No legal moves available or no move found.")

    duration = end_time - start_time
    print(f"⏱️ Analysis: {duration:.2f}s, {nodes_visited} nodes evaluated")


if __name__ == '__main__':
    main()
