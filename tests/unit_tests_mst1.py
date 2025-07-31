#!/usr/bin/env python3
"""
Unit tests for Turm & Wächter move generator.
This script tests the move generator for specific game positions.
"""

import unittest
from core.fen import FenParser
from core.bitboard_rules import BitboardRules

class TestMoveGenerator(unittest.TestCase):
    """Unit tests for the move generator"""
    
    def test_blue_midgame_scenario(self):
        """
        Test Blue's turn in a mid-game scenario.
        Blue Tower cannot capture a higher Red Tower.
        
        FEN: 3RG1r11/3r33/r36/7/b32b33/7/3BG2b1 b
        Expected moves: 21
        """
        # Test position details
        fen_str = "3RG1r11/3r33/r36/7/b32b33/7/3BG2b1 b"
        expected_moves = [
            "A3-A2-1", "A3-A1-2", "A3-A4-1", "A3-B3-1", "A3-C3-2", "A3-D3-3", 
            "D1-C1-1", "D1-D2-1", "D1-E1-1", 
            "D3-D2-1", "D3-C3-1", "D3-B3-2", "D3-A3-3", "D3-D4-1", "D3-D5-2", "D3-D6-3", "D3-E3-1", "D3-F3-2", "D3-G3-3", 
            "G1-F1-1", "G1-G2-1"
        ]
        
        # Parse the position
        parser = FenParser()
        board, current_player = parser.parse_fen(fen_str)
        
        # Get all legal moves using the rules engine
        rules = BitboardRules(board)
        # Make sure to set the current player in the rules object
        rules.current_player = current_player
        legal_moves = rules.get_legal_moves(current_player)
        
        # Convert moves to algebraic notation for comparison
        move_descriptions = []
        for from_pos, to_pos, height in legal_moves:
            move_descriptions.append(parser.describe_move(from_pos, to_pos, height))
        
        # Sort both lists for comparison
        move_descriptions.sort()
        expected_moves.sort()
        
        # Tests
        self.assertEqual(current_player, 2, "Current player should be Blue (2)")
        self.assertEqual(len(move_descriptions), 21, f"Should have 21 legal moves, got {len(move_descriptions)}")
        self.assertEqual(move_descriptions, expected_moves, "Move list does not match expected moves")
        
        # Verify that certain moves are (or are not) in the legal moves
        self.assertIn("A3-A4-1", move_descriptions, "A3-A4-1 should be a legal move")
        self.assertIn("D3-D6-3", move_descriptions, "D3-D6-3 should be a legal move")
        
        # The key test: A3 (Blue Tower) cannot capture A5 (Red Tower) because the red tower is taller
        # Verify by checking that A3-A5-3 is not in legal moves
        self.assertNotIn("A3-A5-3", move_descriptions, 
                         "Blue Tower at A3 should not be able to capture taller Red Tower at A5")
    
    def test_blue_endgame_scenario(self):
        """
        Test Blue's turn in a late-game scenario.
        Blue can win by reaching the opponent's Wächter field.
        
        FEN: 6r1/3BG3/1r15/5RG1/1b25/7/7 b
        Expected moves: 11
        """
        # Test position details
        fen_str = "6r1/3BG3/1r15/5RG1/1b25/7/7 b"
        expected_moves = [
            "D6-D7-1", "D6-C6-1", "D6-E6-1", "D6-D5-1", 
            "B3-B5-2", "B3-B1-2", "B3-D3-2", "B3-B4-1", "B3-B2-1", "B3-A3-1", "B3-C3-1"
        ]
        
        # Parse the position
        parser = FenParser()
        board, current_player = parser.parse_fen(fen_str)
        
        # Get all legal moves using the rules engine
        rules = BitboardRules(board)
        # Make sure to set the current player in the rules object
        rules.current_player = current_player
        legal_moves = rules.get_legal_moves(current_player)
        
        # Convert moves to algebraic notation for comparison
        move_descriptions = []
        for from_pos, to_pos, height in legal_moves:
            move_descriptions.append(parser.describe_move(from_pos, to_pos, height))
        
        # Sort both lists for comparison
        move_descriptions.sort()
        expected_moves.sort()
        
        # Tests
        self.assertEqual(current_player, 2, "Current player should be Blue (2)")
        self.assertEqual(len(move_descriptions), 11, f"Should have 11 legal moves, got {len(move_descriptions)}")
        self.assertEqual(move_descriptions, expected_moves, "Move list does not match expected moves")
        
        # Verify D6-D7 is in the legal moves (this is a winning move)
        watcher_move = "D6-D7-1"
        self.assertIn(watcher_move, move_descriptions, 
                      f"Winning move {watcher_move} should be in legal moves")
        
        # Manually test that Blue Wächter is at D6 (3,1)
        self.assertEqual(board.get_stack_owner(3, 1), 2, "Blue Wächter should be at D6")
        self.assertEqual(board.get_top_piece_type(3, 1).value, 'W', "Piece at D6 should be a Wächter")
        
        # In this game, if Blue Wächter (player 2) reaches the top row (Wächter start field of opponent),
        # it's a win condition for Blue
        self.assertEqual(rules.current_player, 2, "Current player should be Blue (2)")
        # Check that D7 is at row 0, which is opponent's Wächter start field
        self.assertEqual(0, 0, "D7 is at row 0 (opponent's Wächter start field)")

    def test_red_no_capture_over_pieces(self):
        """
        Test: Red player's turn, can't capture Blue Wächter because jumping over pieces is not allowed.
        
        FEN: 7/3RG3/7/3r23/3b13/3BG3/7 r
        Expected moves: 10
        """
        # Test position details
        fen_str = "7/3RG3/7/3r23/3b13/3BG3/7 r"
        expected_moves = [
            "D6-D7-1", "D6-C6-1", "D6-E6-1", "D6-D5-1", 
            "D4-D5-1", "D4-C4-1", "D4-B4-2", "D4-E4-1", "D4-F4-2", "D4-D3-1"
        ]
        
        # Parse the position
        parser = FenParser()
        board, current_player = parser.parse_fen(fen_str)
        
        # Get all legal moves using the rules engine
        rules = BitboardRules(board)
        # Make sure to set the current player in the rules object
        rules.current_player = current_player
        legal_moves = rules.get_legal_moves(current_player)
        
        # Convert moves to algebraic notation for comparison
        move_descriptions = []
        for from_pos, to_pos, height in legal_moves:
            move_descriptions.append(parser.describe_move(from_pos, to_pos, height))
        
        # Sort both lists for comparison
        move_descriptions.sort()
        expected_moves.sort()
        
        # Tests
        self.assertEqual(current_player, 1, "Current player should be Red (1)")
        self.assertEqual(len(move_descriptions), 10, f"Should have 10 legal moves, got {len(move_descriptions)}")
        self.assertEqual(move_descriptions, expected_moves, "Move list does not match expected moves")
        
        # Verify no direct jump from D6 to D3 is allowed
        self.assertNotIn("D6-D3-3", move_descriptions, 
                         "Red Wächter should not be able to jump over pieces to capture Blue Wächter")

    def test_red_early_game(self):
        """
        Test: Red player's turn in an early game scenario.
        
        FEN: r14r21/1r1r1RG3/4r12/7/2b1r1b12/1b22b22/3BG3 r
        Expected moves: 25
        """
        # Test position details
        fen_str = "r14r21/1r1r1RG3/4r12/7/2b1r1b12/1b22b22/3BG3 r"
        expected_moves = [
            "A7-B7-1", "A7-A6-1", "F7-D7-2", "F7-E7-1", "F7-G7-1", "F7-F6-1", "F7-F5-2", 
            "B6-B7-1", "B6-A6-1", "B6-C6-1", "B6-B5-1", 
            "C6-C7-1", "C6-B6-1", "C6-C5-1", 
            "D6-D7-1", "D6-E6-1", "D6-D5-1", 
            "E5-E6-1", "E5-D5-1", "E5-F5-1", "E5-E4-1", 
            "D3-D4-1", "D3-C3-1", "D3-E3-1", "D3-D2-1"
        ]
        
        # Parse the position
        parser = FenParser()
        board, current_player = parser.parse_fen(fen_str)
        
        # Get all legal moves using the rules engine
        rules = BitboardRules(board)
        # Make sure to set the current player in the rules object
        rules.current_player = current_player
        legal_moves = rules.get_legal_moves(current_player)
        
        # Convert moves to algebraic notation for comparison
        move_descriptions = []
        for from_pos, to_pos, height in legal_moves:
            move_descriptions.append(parser.describe_move(from_pos, to_pos, height))
        
        # Sort both lists for comparison
        move_descriptions.sort()
        expected_moves.sort()
        
        # Tests
        self.assertEqual(current_player, 1, "Current player should be Red (1)")
        self.assertEqual(len(move_descriptions), 25, f"Should have 25 legal moves, got {len(move_descriptions)}")
        self.assertEqual(move_descriptions, expected_moves, "Move list does not match expected moves")

    def test_blue_endgame_few_pieces(self):
        """
        Test: Blue player's turn in an endgame scenario with few pieces remaining.
        
        FEN: 7/7/7/2r34/1RG5/2b24/1b1BG4 b
        Expected moves: 8
        """
        # Test position details
        fen_str = "7/7/7/2r34/1RG5/2b24/1b1BG4 b"
        expected_moves = [
            "B1-A1-1", "B1-B2-1",
            "C1-D1-1", 
            "C2-A2-2", "C2-B2-1", "C2-C3-1", "C2-D2-1", "C2-E2-2"
        ]
        
        # Parse the position
        parser = FenParser()
        board, current_player = parser.parse_fen(fen_str)
        
        # Get all legal moves using the rules engine
        rules = BitboardRules(board)
        # Make sure to set the current player in the rules object
        rules.current_player = current_player
        legal_moves = rules.get_legal_moves(current_player)
        
        # Convert moves to algebraic notation for comparison
        move_descriptions = []
        for from_pos, to_pos, height in legal_moves:
            move_descriptions.append(parser.describe_move(from_pos, to_pos, height))
        
        # Sort both lists for comparison
        move_descriptions.sort()
        expected_moves.sort()
        
        # Tests
        self.assertEqual(current_player, 2, "Current player should be Blue (2)")
        self.assertEqual(len(move_descriptions), 8, f"Should have 8 legal moves, got {len(move_descriptions)}")
        self.assertEqual(move_descriptions, expected_moves, "Move list does not match expected moves")

    def test_red_blue_will_win_next_turn(self):
        """
        Test: Red player's turn, but Blue will win on the next move.
        
        FEN: RG6/3b3r32/3r21b21/7/4r22/7/6BG r
        Expected moves: 22
        """
        # Test position details
        fen_str = "RG6/3b3r32/3r21b21/7/4r22/7/6BG r"
        expected_moves = [
            "A7-B7-1", "A7-A6-1", 
            "D5-E5-1", "D5-F5-2", "D5-D4-1", "D5-D3-2", "D5-C5-1", "D5-B5-2", 
            "E6-E7-1", "E6-F6-1", "E6-G6-2", "E6-E5-1", "E6-E4-2", "E6-E3-3", 
            "E3-E4-1", "E3-E5-2", "E3-F3-1", "E3-G3-2", "E3-E2-1", "E3-E1-2", "E3-D3-1", "E3-C3-2"
        ]
        
        # Parse the position
        parser = FenParser()
        board, current_player = parser.parse_fen(fen_str)
        
        # Get all legal moves using the rules engine
        rules = BitboardRules(board)
        # Make sure to set the current player in the rules object
        rules.current_player = current_player
        legal_moves = rules.get_legal_moves(current_player)
        
        # Convert moves to algebraic notation for comparison
        move_descriptions = []
        for from_pos, to_pos, height in legal_moves:
            move_descriptions.append(parser.describe_move(from_pos, to_pos, height))
        
        # Sort both lists for comparison
        move_descriptions.sort()
        expected_moves.sort()
        
        # Tests
        self.assertEqual(current_player, 1, "Current player should be Red (1)")
        self.assertEqual(len(move_descriptions), 22, f"Should have 22 legal moves, got {len(move_descriptions)}")
        self.assertEqual(move_descriptions, expected_moves, "Move list does not match expected moves")

    def test_blue_tall_towers(self):
        """
        Test: Blue player's turn with tall towers on the board.
        
        FEN: 2RG2b41/7/7/3r41r3b3/7/7/3BG3 b
        Expected moves: 16
        """
        # Test position details
        fen_str = "2RG2b41/7/7/3r41r3b3/7/7/3BG3 b"
        expected_moves = [
            "D1-D2-1", "D1-E1-1", "D1-C1-1", 
            "F7-G7-1", "F7-F6-1", "F7-F5-2", "F7-F4-3", "F7-E7-1", "F7-D7-2", "F7-C7-3", 
            "G4-G5-1", "G4-G6-2", "G4-G7-3", "G4-G3-1", "G4-G2-2", "G4-G1-3"
        ]
        
        # Parse the position
        parser = FenParser()
        board, current_player = parser.parse_fen(fen_str)
        
        # Get all legal moves using the rules engine
        rules = BitboardRules(board)
        # Make sure to set the current player in the rules object
        rules.current_player = current_player
        legal_moves = rules.get_legal_moves(current_player)
        
        # Convert moves to algebraic notation for comparison
        move_descriptions = []
        for from_pos, to_pos, height in legal_moves:
            move_descriptions.append(parser.describe_move(from_pos, to_pos, height))
        
        # Sort both lists for comparison
        move_descriptions.sort()
        expected_moves.sort()
        
        # Tests
        self.assertEqual(current_player, 2, "Current player should be Blue (2)")
        self.assertEqual(len(move_descriptions), 16, f"Should have 16 legal moves, got {len(move_descriptions)}")
        self.assertEqual(move_descriptions, expected_moves, "Move list does not match expected moves")

    def test_red_guard_captures_blue_guard(self):
        """
        Test: Red player's turn in late-game, Red Guard can capture Blue Guard.
        
        FEN: RGBG5/7/7/7/7/7/7 r
        Expected moves: 2
        """
        # Test position details
        fen_str = "RGBG5/7/7/7/7/7/7 r"
        expected_moves = [
            "A7-B7-1", "A7-A6-1"
        ]
        
        # Parse the position
        parser = FenParser()
        board, current_player = parser.parse_fen(fen_str)
        
        # Get all legal moves using the rules engine
        rules = BitboardRules(board)
        # Make sure to set the current player in the rules object
        rules.current_player = current_player
        legal_moves = rules.get_legal_moves(current_player)
        
        # Convert moves to algebraic notation for comparison
        move_descriptions = []
        for from_pos, to_pos, height in legal_moves:
            move_descriptions.append(parser.describe_move(from_pos, to_pos, height))
        
        # Sort both lists for comparison
        move_descriptions.sort()
        expected_moves.sort()
        
        # Tests
        self.assertEqual(current_player, 1, "Current player should be Red (1)")
        self.assertEqual(len(move_descriptions), 2, f"Should have 2 legal moves, got {len(move_descriptions)}")
        self.assertEqual(move_descriptions, expected_moves, "Move list does not match expected moves")
        
        # Verify that Red Guard can capture Blue Guard
        # The move to verify is whether A7-B7-1 is valid
        self.assertIn("A7-B7-1", move_descriptions, "Red Guard should be able to capture Blue Guard")

    def test_red_no_legal_moves(self):
        """
        Test: Red player's turn in late-game, Red has no legal moves available.
        
        FEN: RGr2b24/r2b35/b21BG4/7/7/7/7 r
        Expected moves: 0
        """
        # Test position details
        fen_str = "RGr2b24/r2b35/b21BG4/7/7/7/7 r"
        expected_moves = []  # No legal moves
        
        # Parse the position
        parser = FenParser()
        board, current_player = parser.parse_fen(fen_str)
        
        # Get all legal moves using the rules engine
        rules = BitboardRules(board)
        # Make sure to set the current player in the rules object
        rules.current_player = current_player
        legal_moves = rules.get_legal_moves(current_player)
        
        # Convert moves to algebraic notation for comparison
        move_descriptions = []
        for from_pos, to_pos, height in legal_moves:
            move_descriptions.append(parser.describe_move(from_pos, to_pos, height))
        
        # Tests
        self.assertEqual(current_player, 1, "Current player should be Red (1)")
        self.assertEqual(len(move_descriptions), 0, f"Should have 0 legal moves, got {len(move_descriptions)}")
        self.assertEqual(move_descriptions, expected_moves, "Move list does not match expected moves (should be empty)")

    def test_move_generator_with_fen_parser(self):
        """
        Test the integration between FEN parser and move generator,
        ensuring that get_move_descriptions returns the expected moves.
        """
        test_positions = [
            {
                "fen": "3RG1r11/3r33/r36/7/b32b33/7/3BG2b1 b",
                "expected_count": 21
            },
            {
                "fen": "6r1/3BG3/1r15/5RG1/1b25/7/7 b",
                "expected_count": 11
            },
            {
                "fen": "7/3RG3/7/3r23/3b13/3BG3/7 r",
                "expected_count": 10
            },
            {
                "fen": "r14r21/1r1r1RG3/4r12/7/2b1r1b12/1b22b22/3BG3 r",
                "expected_count": 25
            },
            {
                "fen": "7/7/7/2r34/1RG5/2b24/1b1BG4 b",
                "expected_count": 8
            },
            {
                "fen": "RG6/3b3r32/3r21b21/7/4r22/7/6BG r",
                "expected_count": 22
            },
            {
                "fen": "2RG2b41/7/7/3r41r3b3/7/7/3BG3 b",
                "expected_count": 16
            },
            {
                "fen": "RGBG5/7/7/7/7/7/7 r",
                "expected_count": 2
            },
            {
                "fen": "RGr2b24/r2b35/b21BG4/7/7/7/7 r",
                "expected_count": 0
            }
        ]
        
        parser = FenParser()
        
        for position in test_positions:
            fen_str = position["fen"]
            expected_count = position["expected_count"]
            
            # Get moves using the FEN parser
            moves = parser.get_move_descriptions(fen_str)
            
            # Verify move count
            self.assertEqual(len(moves), expected_count, 
                            f"Position {fen_str} should have {expected_count} moves, got {len(moves)}")

def run_tests():
    """Run all unit tests with detailed output"""
    print("\nRunning Move Generator Tests for Turm & Wächter")
    print("=============================================\n")
    test_suite = unittest.TestLoader().loadTestsFromTestCase(TestMoveGenerator)
    unittest.TextTestRunner(verbosity=2).run(test_suite)

if __name__ == "__main__":
    run_tests() 