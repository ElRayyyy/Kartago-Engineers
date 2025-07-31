from typing import List, Tuple, Dict, Optional
from .piece import PieceType
from .bitboard import BitboardBoard

class FenParser:
    """Parser for Turm & Wächter FEN notation.
    
    Examples of FEN strings:
    b36/3b12r3/7/7/1r2RG4/2/BG4/6r1 b
    7/6r3/1RG5/3b43/1r25/7/2BG3r1 r
    """
    
    def __init__(self):
        pass
        
    def parse_fen(self, fen_str: str) -> Tuple[BitboardBoard, int]:
        """Parse a FEN string into a board state and current player.
        
        Args:
            fen_str: FEN string representing the board state and current player
            
        Returns:
            Tuple of (BitboardBoard, current_player)
        """
        # Split FEN string into board and current player
        parts = fen_str.strip().split()
        board_str = parts[0]
        current_player = 1 if parts[1] == 'r' else 2  # r for red (player 1), b for blue (player 2)
        
        # Create empty bitboard
        board = BitboardBoard(setup_initial=False)
        
        # Parse board string
        rows = board_str.split('/')
        for y, row in enumerate(rows):
            if y >= board.SIZE:
                break  # Ensure we don't exceed board height
                
            x = 0
            i = 0
            while i < len(row) and x < board.SIZE:
                # Check for RG (Red Guard)
                if i + 1 < len(row) and row[i:i+2] == "RG":
                    board.red_guardian = board._set_bit(board.red_guardian, x, y)
                    i += 2
                    x += 1
                # Check for BG (Blue Guard)
                elif i + 1 < len(row) and row[i:i+2] == "BG":
                    board.blue_guardian = board._set_bit(board.blue_guardian, x, y)
                    i += 2
                    x += 1
                # Check for tower pieces (r1-r7, b1-b7)
                elif row[i] in ('r', 'b') and i + 1 < len(row) and row[i+1].isdigit():
                    player = 1 if row[i] == 'r' else 2
                    height = int(row[i+1])
                    
                    # Tower height should be between 1 and 7
                    if 1 <= height <= 7:
                        if player == 1:  # Red tower
                            board.red_towers[height] = board._set_bit(board.red_towers[height], x, y)
                        else:  # Blue tower
                            board.blue_towers[height] = board._set_bit(board.blue_towers[height], x, y)
                    
                    i += 2
                    x += 1
                # Check for empty spaces
                elif row[i].isdigit():
                    empty_count = int(row[i])
                    x += empty_count
                    i += 1
                else:
                    # Skip other characters
                    i += 1
                    
        return board, current_player
        
    def describe_move(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int], height: int) -> str:
        """Generate a move description in algebraic notation.
        
        Format: {from_col}{from_row}-{to_col}{to_row}-{height}
        
        Args:
            from_pos: Starting position (x, y)
            to_pos: Ending position (x, y)
            height: Stack height to move
            
        Returns:
            Move in algebraic notation
        """
        # Convert to algebraic notation (A-G for columns, 1-7 for rows)
        from_col = chr(from_pos[0] + ord('A'))
        from_row = 7 - from_pos[1]  # FEN starts from top row
        to_col = chr(to_pos[0] + ord('A'))
        to_row = 7 - to_pos[1]
        
        return f"{from_col}{from_row}-{to_col}{to_row}-{height}"
        
    def get_move_descriptions(self, fen_str: str) -> List[str]:
        """Get descriptions of all legal moves from a FEN string.
        
        Args:
            fen_str: Starting FEN string
            
        Returns:
            List of move descriptions in algebraic notation
        """
        from .bitboard_rules import BitboardRules
        
        # Parse the FEN string
        board, current_player = self.parse_fen(fen_str)
        
        # Setup rules engine
        rules = BitboardRules(board)
        rules.current_player = current_player
        
        # Get all legal moves
        legal_moves = rules.get_legal_moves(current_player)
        
        # Generate move descriptions
        move_descriptions = []
        
        for from_pos, to_pos, height in legal_moves:
            move_descriptions.append(self.describe_move(from_pos, to_pos, height))
            
        return move_descriptions 