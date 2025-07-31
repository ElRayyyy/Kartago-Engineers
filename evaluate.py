from core.fen import FenParser
from core.bitboard import BitboardBoard
from win_check import check_win_by_distance_or_capture

# Pre‐parse parser once
_parser = FenParser()

# Simplified parameters - only 10 most important for speed
DEFAULT_PARAMS = {
    'material_weight': 80,        # Basic piece count
    'guardian_advance': 40,       # Guardian advancement to center/enemy
    'guardian_safety': 200,       # Guardian protection 
    'center_control': 25,         # Control of center squares
    'tower_height': 20,           # Tall tower bonus
    'aggression': 50,             # Attack vs defense preference
    'mobility': 10,               # Move options
    'positioning': 10,            # Board position quality
    'tempo': 20,                  # Initiative/momentum
    'win_bonus': 10000,           # Win detection
}

def evaluate(fen_str: str, params: dict = None) -> int:
    """
    Fast simplified evaluation from Red's perspective.
    Only 10 parameters for speed and better optimization.
    """
    if params is None:
        params = DEFAULT_PARAMS
    
    # Parse FEN
    board, player = _parser.parse_fen(fen_str)
    size = board.SIZE
    
    # Quick win/loss detection
    if check_win_by_distance_or_capture(board, player):
        return params['win_bonus']
    if check_win_by_distance_or_capture(board, 3 - player):
        return -params['win_bonus']
    
    # Determine perspectives
    if player == 1:  # Red
        my_guard_bb = board.red_guardian
        enemy_guard_bb = board.blue_guardian  
        my_towers = board.red_towers
        enemy_towers = board.blue_towers
        my_target = (3, 6)  # D1 for Red
    else:  # Blue
        my_guard_bb = board.blue_guardian
        enemy_guard_bb = board.red_guardian
        my_towers = board.blue_towers  
        enemy_towers = board.red_towers
        my_target = (3, 0)  # D7 for Blue
    
    score = 0
    
    # === MATERIAL & HEIGHT (fast) ===
    my_pieces = 0
    enemy_pieces = 0
    my_height_total = 0
    enemy_height_total = 0
    
    for h in range(1, 8):
        my_count = my_towers[h].bit_count()
        enemy_count = enemy_towers[h].bit_count()
        my_pieces += my_count
        enemy_pieces += enemy_count
        my_height_total += h * my_count if h >= 3 else 0  # Only count tall towers
        enemy_height_total += h * enemy_count if h >= 3 else 0
    
    # Add guardians
    my_pieces += my_guard_bb.bit_count()
    enemy_pieces += enemy_guard_bb.bit_count()
    
    score += params['material_weight'] * (my_pieces - enemy_pieces)
    score += params['tower_height'] * (my_height_total - enemy_height_total)
    
    # === GUARDIAN STRATEGY ===
    if my_guard_bb:
        my_guard_pos = my_guard_bb.bit_length() - 1
        gx, gy = my_guard_pos % size, my_guard_pos // size
        
        # Distance to target (closer is better)
        dist_to_target = abs(gx - my_target[0]) + abs(gy - my_target[1])
        score -= params['guardian_advance'] * dist_to_target
        
        # Center bonus (D4 area)
        center_dist = abs(gx - 3) + abs(gy - 3)
        score += params['center_control'] * max(0, 3 - center_dist)
        
        # Safety (edge penalty)
        edge_dist = min(gx, size-1-gx, gy, size-1-gy)
        if edge_dist == 0:
            score -= params['guardian_safety'] // 2
    
    # === POSITIONAL CONTROL (fast) ===
    center_squares = [(2,3), (3,3), (4,3), (2,4), (3,4), (4,4)]  # Reduced set
    my_center = 0
    enemy_center = 0
    
    for x, y in center_squares:
        owner = board.get_stack_owner(x, y)
        if owner == player:
            my_center += 1
        elif owner == (3 - player):
            enemy_center += 1
    
    score += params['center_control'] * (my_center - enemy_center)
    
    # === MOBILITY (estimate) ===
    mobility_score = 0
    for h in range(1, 4):  # Only check heights 1-3 for speed
        mobility_score += my_towers[h].bit_count() * h
    
    score += params['mobility'] * mobility_score
    
    # === AGGRESSION (simplified) ===
    if enemy_guard_bb:
        enemy_guard_pos = enemy_guard_bb.bit_length() - 1
        ex, ey = enemy_guard_pos % size, enemy_guard_pos // size
        
        # Count pieces that could threaten enemy guardian
        threats = 0
        for h in range(1, 4):  # Only check lower heights for speed
            my_bb = my_towers[h]
            for pos in range(min(20, size * size)):  # Limit search for speed
                if my_bb & (1 << pos):
                    x, y = pos % size, pos // size
                    if abs(x - ex) + abs(y - ey) <= h + 1:  # Close to enemy guardian
                        threats += 1
        
        score += params['aggression'] * threats
    
    # === POSITIONING (board advancement) ===
    my_advanced = 0
    enemy_advanced = 0
    middle = size // 2
    
    for h in range(1, 3):  # Only check heights 1-2 for speed
        my_bb = my_towers[h]
        enemy_bb = enemy_towers[h]
        
        # Count pieces in enemy half
        for pos in range(size * middle):  # Only check first half of board
            if player == 1 and (my_bb & (1 << pos)):  # Red in upper half
                my_advanced += 1
            elif player == 2 and (enemy_bb & (1 << pos)):  # Blue in lower half
                enemy_advanced += 1
    
    score += params['positioning'] * (my_advanced - enemy_advanced)
    
    # === TEMPO (simple piece activity) ===
    tempo_score = my_pieces * 2 - enemy_pieces  # Simple activity measure
    score += params['tempo'] * tempo_score
    
    # Return from current player's perspective
    return score if player == 1 else -score


def quick_benchmark():
    """Quick test of the evaluation function"""
    test_positions = [
        "r1r11RG1r1r1/2r11r12/3r13/7/3b13/2b11b12/b1b11BG1b1b1 r",  # Opening
        "3RG1r11/3r33/r36/7/b32b33/7/3BG2b1 b",  # Midgame
    ]
    
    for i, fen in enumerate(test_positions):
        score = evaluate(fen)
        print(f"Position {i+1}: {score}")


if __name__ == "__main__":
    quick_benchmark()