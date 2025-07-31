#!/usr/bin/env python3
"""
Win-check utilities for Turm & Wächter replacing is_game_over/get_winner:
  - A player wins if their guardian reaches the opponent's start (distance=0)
  - Or if the opponent's guardian no longer exists on the board.
"""
from core.bitboard import BitboardBoard
from distance_test import distance_to_opponent_start


def opponent_guardian_exists(board: BitboardBoard, opponent: int) -> bool:
    """
    Check if the opponent's guardian bitboard is non-zero.
    """
    if opponent == 1:
        return board.red_guardian != 0
    else:
        return board.blue_guardian != 0


def check_win_by_distance_or_capture(board: BitboardBoard, player: int) -> bool:
    """
    Return True if 'player' has won by either:
      1) Guardian distance to opponent start == 0, or
      2) Opponent guardian no longer on board.
    """
    # 1) Distance-to-opponent-start == 0
    dist = distance_to_opponent_start(board, player)
    if dist == 0:
        return True

    # 2) Opponent guardian disappeared
    opponent = 3 - player
    if not opponent_guardian_exists(board, opponent):
        return True

    return False


# Example tests
if __name__ == "__main__":
    from core.fen import FenParser
    parser = FenParser()

    # 1) Terminal by arrival
    fen1 = "7/7/7/3RG3/7/7/7 r"  # Red guardian on D4 (3,3) -> dist to D1=3, not a win yet
    # Move to D1 (3,6) would be distance 0
    board1, player1 = parser.parse_fen(fen1)
    print("Win?", check_win_by_distance_or_capture(board1, player1))  # False

    # 2) Capture opponent guardian
    fen2 = "7/7/7/3RG3/3BG3/7/7 r"  # Red can capture Blue guardian at D4
    board2, player2 = parser.parse_fen(fen2)
    # Simulate capture manually
    rules = __import__("core.bitboard_rules", fromlist=["BitboardRules"]).BitboardRules(board2)
    rules.current_player = player2
    rules.make_move((3,2),(3,3),1)
    print("Win?", check_win_by_distance_or_capture(rules.board, player2))  # True
