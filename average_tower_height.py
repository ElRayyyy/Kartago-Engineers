#!/usr/bin/env python3
"""
Test script for `average_tower_height` function in Turm & Wächter.

Usage:
    python average_tower_height_test.py
"""
from core.fen import FenParser


def average_tower_height(fen_str: str) -> float:
    """
    Calculate the average height of the current player's towers.
    Returns 0.0 if the player has no towers.
    """
    parser = FenParser()
    board, current_player = parser.parse_fen(fen_str)
    total_height = 0
    total_stacks = 0
    # Heights 1 through 7
    for h in range(1, 8):
        # Select the correct bitboard for the current player
        bitboard = board.red_towers[h] if current_player == 1 else board.blue_towers[h]
        # Count bits (number of stacks at height h)
        count = bin(bitboard).count('1')
        total_height += h * count
        total_stacks += count
    return total_height / total_stacks if total_stacks > 0 else 0.0


def test_case(fen: str, expected: float):
    avg = average_tower_height(fen)
    status = 'PASS' if abs(avg - expected) < 1e-6 else 'FAIL'
    print(f"FEN: {fen}\n  average_tower_height: got {avg:.2f}, expected {expected:.2f} -> {status}\n")


def main():
    # Test cases: (FEN, expected average)
    tests = [
        # Initial position: 7 towers of height 1 -> avg = 1
        ("r1r11RG1r1r1/2r11r12/3r13/7/3b13/2b11b12/b1b11BG1b1b1 r", 1.0),
        # No towers at all -> avg = 0
        ("7/7/7/3RG3/7/7/7 r", 0.0),
        # Two red towers: heights 2 and 4 -> avg = 3.0
        ("r2r45/7/7/7/7/7/7 r", 3.0),
        # Mixed blue towers: one height3, two height1 -> avg = (3 + 1 + 1)/3 = 1.67
        ("7/7/7/7/7/7/b31BG1b1b12 b", (3 + 1 + 1) / 3),
    ]
    for fen, expected in tests:
        test_case(fen, expected)


if __name__ == "__main__":
    main()
