#!/usr/bin/env python3
"""
AI Game Demo for Turm & Wächter.
This script demonstrates AI playing a game against itself (Random vs Random).
"""

import sys
import os
import subprocess
from typing import List, Tuple, Optional


def call_dummy_ki(fen_str: str) -> Optional[str]:
    """
    Call alpha_beta_ki.py with a FEN string to get a move.
    Returns only the first line of output (move in algebraic notation).
    """
    dummy_ki_path = os.path.abspath(os.path.join(
        os.path.dirname(__file__), '..', 'alpha_beta_ki.py'
    ))
    try:
        env = os.environ.copy()
        env["PYTHONPATH"] = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        result = subprocess.run(
            [sys.executable, dummy_ki_path, fen_str],
            capture_output=True,
            text=True,
            env=env
        )
        if result.returncode != 0:
            print(f"Error from AI script: {result.stderr}", file=sys.stderr)
            return None
        lines = result.stdout.strip().splitlines()
        return lines[0] if lines else None
    except Exception as e:
        print(f"Error calling AI script: {e}", file=sys.stderr)
        return None


def visualize_board(fen_str: str) -> None:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from core.fen import FenParser

    parser = FenParser()
    board, current_player = parser.parse_fen(fen_str)

    print("\n   A    B    C    D    E    F    G  \n")
    for y in range(board.SIZE):
        row = f"{7-y}  "
        for x in range(board.SIZE):
            owner = board.get_stack_owner(x, y)
            if owner is None:
                row += ".    "
            else:
                piece_type = board.get_top_piece_type(x, y)
                stack_height = board.get_stack_height(x, y)
                char = ('R' if owner == 1 else 'B') if piece_type.value == 'W' else ('r' if owner == 1 else 'b')
                row += f"{char}{stack_height if stack_height>1 else ''}   "
        print(row + f" {7-y}\n")
    print("   A    B    C    D    E    F    G  \n")
    print(f"Current player: {'Red' if current_player==1 else 'Blue'}\n")


def get_next_fen(current_fen: str, move: str) -> Optional[str]:
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from core.fen import FenParser
    from core.bitboard_rules import BitboardRules

    parser = FenParser()
    board, current_player = parser.parse_fen(current_fen)
    rules = BitboardRules(board)
    rules.current_player = current_player

    # Only split first line
    parts = move.strip().splitlines()[0].split('-')
    if len(parts) != 3:
        print(f"Invalid move format: {move}", file=sys.stderr)
        return None
    from_str, to_str, height_str = parts
    fx = ord(from_str[0]) - ord('A')
    fy = 7 - int(from_str[1])
    tx = ord(to_str[0]) - ord('A')
    ty = 7 - int(to_str[1])
    try:
        height = int(height_str)
    except ValueError:
        print(f"Invalid height in move: {height_str}", file=sys.stderr)
        return None

    rules.make_move((fx, fy), (tx, ty), height)
    return board.to_fen(rules.current_player)


def play_ai_game(max_moves=50):
    initial_fen = "r1r11RG1r1r1/2r11r12/3r13/7/3b13/2b11b12/b1b11BG1b1b1 r"
    current_fen = initial_fen
    print("Starting AI vs AI game")
    visualize_board(current_fen)

    for move_num in range(1, max_moves+1):
        current_player = 'Red' if current_fen.split()[-1]=='r' else 'Blue'
        move = call_dummy_ki(current_fen)
        if not move:
            print(f"{current_player} has no moves.")
            break
        print(f"Move {move_num}: {current_player} plays {move}\n")
        next_fen = get_next_fen(current_fen, move)
        if not next_fen:
            break
        current_fen = next_fen
        visualize_board(current_fen)

    print("Game finished or reached move limit.")


def main():
    play_ai_game(max_moves=15)

if __name__ == '__main__':
    main()
