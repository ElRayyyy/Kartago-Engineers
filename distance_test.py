#!/usr/bin/env python3
"""
Script combining `distance_to_opponent_start` and its tests in one file.

Usage:
    python distance_to_opponent_start_test.py
"""

from core.bitboard import BitboardBoard
from core.fen import FenParser


def distance_to_opponent_start(board: BitboardBoard, player: int) -> int:
    """
    Calculate the Manhattan distance from the player's Guardian
    to the opponent's initial starting square.

    Opponent initial positions (zero-based coords):
      - If player=1 (Red), opponent=Blue starts at D1 -> (3, 6)
      - If player=2 (Blue), opponent=Red starts at D7 -> (3, 0)

    Returns:
        int: Manhattan distance between current Guardian position and opponent's initial position.
    """
    # Determine which bitboard and target based on player
    if player == 1:
        bitboard = board.red_guardian
        target_x, target_y = 3, 6
    else:
        bitboard = board.blue_guardian
        target_x, target_y = 3, 0

    # Find current Guardian position bit index
    for bitpos in range(board.SIZE * board.SIZE):
        if bitboard & (1 << bitpos):
            x = bitpos % board.SIZE
            y = bitpos // board.SIZE
            # Return Manhattan distance immediately
            return abs(x - target_x) + abs(y - target_y)

    # If no guardian found, return a large distance
    return board.SIZE * 2  # worst-case distance


def test_distance_to_opponent(fen: str, player: int, expected: int):
    parser = FenParser()
    board, _ = parser.parse_fen(fen)
    dist = distance_to_opponent_start(board, player)
    status = "PASS" if dist == expected else "FAIL"
    print(f"Test {status}: player {player}, expected {expected}, got {dist} (FEN: {fen})")


def main():
    # Test cases: (FEN, player, expected distance)
    tests = [
        # Initial positions -> distance = 6
        (
            "r1r11RG1r1r1/2r11r12/3r13/7/3b13/2b11b12/b1b11BG1b1b1 r",
            1, 6
        ),  # Red at D7 to Blue start D1
        (
            "r1r11RG1r1r1/2r11r12/3r13/7/3b13/2b11b12/b1b11BG1b1b1 b",
            2, 6
        ),  # Blue at D1 to Red start D7
        # Red moves to D4 -> distance from (3,3) to (3,6) = 3
        (
            "7/7/7/3RG3/7/7/7 r",
            1, 3
        ),
        # Blue moves to D4 -> distance from (3,3) to (3,0) = 3
        (
            "7/3RG3/7/31BG2/7/7/7 b",
            2, 3
        ),
    ]

    for fen, player, expected in tests:
        test_distance_to_opponent(fen, player, expected)


if __name__ == "__main__":
    main()
