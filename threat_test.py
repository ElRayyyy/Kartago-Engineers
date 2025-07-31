#!/usr/bin/env python3
"""
Optimized threat detection for Turm & Wächter, with tests and benchmark.

Usage:
    python threat_test_optimized.py
"""
import time
from core.bitboard import BitboardBoard
from core.fen import FenParser
from core.bitboard_rules import BitboardRules


def threatened_positions(board: BitboardBoard, player: int) -> set:
    """
    Return a set of positions threatened by the opponent in one pass.
    """
    opponent = 3 - player
    rules = BitboardRules(board)
    rules.current_player = opponent
    threatened = set()
    for _, to_pos, _ in rules.get_legal_moves(opponent):
        threatened.add(to_pos)
    return threatened


def is_threatened(board: BitboardBoard, pos: tuple, player: int, threat_set=None) -> bool:
    """
    Check if the piece at `pos` is threatened, using a precomputed threat_set or computing one.
    """
    if threat_set is None:
        threat_set = threatened_positions(board, player)
    return pos in threat_set


def pos_from_alg(alg: str) -> tuple:
    """
    Convert algebraic notation (e.g. 'D7') to zero-based (x, y).
    """
    col = ord(alg[0].upper()) - ord('A')
    row = 7 - int(alg[1])
    return (col, row)


def test_position(fen: str, alg_pos: str, player: int, expected: bool):
    parser = FenParser()
    board, _ = parser.parse_fen(fen)
    threat_set = threatened_positions(board, player)
    pos = pos_from_alg(alg_pos)
    threatened = is_threatened(board, pos, player, threat_set)
    status = "PASS" if threatened == expected else "FAIL"
    print(f"Test {status}: Player {player} at {alg_pos} -> threatened? {threatened} (expected {expected})")


def main():
    # Test cases: (FEN, position, player, expected)
    tests = [
        ("r1r11RG1r1r1/11r11r12/3r13/1b35/3b13/2b11b12/b1b11BG1b1b1 r", "B7", 1, True),
        ("r1r11RG1r1r1/2r1b1r12/3b23/7/3b13/2b11b12/b1b11BG1b1b1 r", "D7", 2, True),
        ("r16/1b6/7/7/7/7/7 r", "A7", 1, False),
    ]
    print("Running optimized threat tests:")
    for fen, alg, player, expected in tests:
        test_position(fen, alg, player, expected)

    # Benchmark
    parser = FenParser()
    fen = "r12RG3/7/6b1/7/2r1b13/7/3BG3 r"
    board, player = parser.parse_fen(fen)
    N = 10000
    start = time.time()
    for _ in range(N):
        threat_set = threatened_positions(board, player)
        # Check a sample position
        _ = is_threatened(board, (3,3), player, threat_set)
    total = time.time() - start
    print(f"\nBenchmark: {N} iterations in {total:.4f}s (avg {total/N*1000:.4f}ms)")

if __name__ == "__main__":
    main()
