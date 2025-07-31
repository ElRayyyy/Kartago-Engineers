#!/usr/bin/env python3
"""
Test script for piece-counting functions in Turm & Wächter.

Usage:
    python piece_counts_test.py
"""
from core.fen import FenParser
from core.bitboard import BitboardBoard

# Monkey-patch BitboardBoard to add count_bits if missing
if not hasattr(BitboardBoard, 'count_bits'):
    BitboardBoard.count_bits = lambda self, bb: bin(bb).count('1')


def count_pieces(fen_str: str) -> int:
    """
    Count stacks (Guardians + towers) belonging to the current player.
    """
    parser = FenParser()
    board, current_player = parser.parse_fen(fen_str)
    count = 0
    # Count towers of each height for current player
    for h in range(1, 8):
        bitboard = board.red_towers[h] if current_player == 1 else board.blue_towers[h]
        count += board.count_bits(bitboard)
    # Add guardian
    guardian_bb = board.red_guardian if current_player == 1 else board.blue_guardian
    count += board.count_bits(guardian_bb)
    return count


def count_enemy_pieces(fen_str: str) -> int:
    """
    Count stacks (Guardians + towers) belonging to the opponent of the current player.
    """
    parser = FenParser()
    board, current_player = parser.parse_fen(fen_str)
    enemy = 2 if current_player == 1 else 1
    count = 0
    for h in range(1, 8):
        bitboard = board.red_towers[h] if enemy == 1 else board.blue_towers[h]
        count += board.count_bits(bitboard)
    guardian_bb = board.red_guardian if enemy == 1 else board.blue_guardian
    count += board.count_bits(guardian_bb)
    return count


def diff_of_pieces(fen_str: str) -> int:
    """
    Difference between current player's and opponent's stack counts.
    """
    return count_pieces(fen_str) - count_enemy_pieces(fen_str)


def count_enemy_pieces_in_half(fen_str: str) -> int:
    """
    Count opponent stacks located in the current player's half of the board.
    """
    parser = FenParser()
    board, current_player = parser.parse_fen(fen_str)
    enemy = 2 if current_player == 1 else 1
    # Define half-rows
    if current_player == 1:
        rows = range(0, 3)    # Red's half: rows 0,1,2
    else:
        rows = range(4, 7)    # Blue's half: rows 4,5,6
    count = 0
    for y in rows:
        for x in range(board.SIZE):
            if board.get_stack_owner(x, y) == enemy:
                count += 1
    return count


def test_case(fen: str, expected_my: int, expected_enemy: int, expected_diff: int, expected_enemy_half: int):
    my = count_pieces(fen)
    enemy = count_enemy_pieces(fen)
    diff = diff_of_pieces(fen)
    eh = count_enemy_pieces_in_half(fen)
    status = lambda got, exp: 'PASS' if got == exp else 'FAIL'
    print(f"FEN: {fen}")
    print(f"  count_pieces: got {my}, expected {expected_my} -> {status(my, expected_my)}")
    print(f"  count_enemy_pieces: got {enemy}, expected {expected_enemy} -> {status(enemy, expected_enemy)}")
    print(f"  diff_of_pieces: got {diff}, expected {expected_diff} -> {status(diff, expected_diff)}")
    print(f"  count_enemy_pieces_in_half: got {eh}, expected {expected_enemy_half} -> {status(eh, expected_enemy_half)}\n")


def main():
    # Test positions
    tests = [
        # Initial position, Red to move
        (
            "r1r11RG1r1r1/2r11r12/3r13/7/3b13/2b11b12/b1b11BG1b1b1 r",
            8, 8, 0, 0
        ),
        # Initial position, Blue to move
        (
            "r1r11RG1r1r1/2r11r12/3r13/7/3b13/2b11b12/b1b11BG1b1b1 b",
            8, 8, 0, 0
        ),
        # Only guardians on board, Red to move
        ("7/7/7/3RG3/7/7/7 r", 1, 0, 1, 0),
        # Red has one tower + guardian, Blue one guardian only, Red to move
        ("7/2r34/7/7/7/7/7 r", 2, 1, 1, 0),
        # Blue has two towers + guardian, Red to move
        ("7/7/7/7/7/2b14/3BG3 r", 0, 3, -3, 2),
    ]
    for fen, my_e, en_e, diff_e, eh_e in tests:
        test_case(fen, my_e, en_e, diff_e, eh_e)


if __name__ == "__main__":
    main()
