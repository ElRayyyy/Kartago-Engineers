from typing import List, Tuple, Optional
from .piece import PieceType

class BitboardBoard:
    """
    Board representation using bitboards for Turm & Wächter game.
    
    The 7x7 board requires 49 bits to represent each position.
    We use separate bitboards for:
    - Red Towers
    - Blue Towers
    - Red Guardian (Wächter)
    - Blue Guardian (Wächter)
    
    For towers, we maintain up to 7 separate bitboards for each height,
    allowing efficient stack representation.
    """
    SIZE = 7
    
    def __init__(self, setup_initial=True):
        # Board size is 7x7 = 49 positions
        self.red_guardian = 0   # Red Guardian (Wächter) positions
        self.blue_guardian = 0  # Blue Guardian (Wächter) positions
        
        # Tower bitboards for each player and height
        # Index 0 is unused, heights start from 1
        self.red_towers = [0] * 8   # Red Tower positions by height
        self.blue_towers = [0] * 8  # Blue Tower positions by height
        
        if setup_initial:
            self.setup_starting_position()

    @staticmethod
    def count_bits(bitboard: int) -> int:

        return bin(bitboard).count('1')

    def _pos_to_bitpos(self, x: int, y: int) -> int:
        """Convert x,y coordinates to bit position (0-48)"""
        if not (0 <= x < self.SIZE and 0 <= y < self.SIZE):
            raise ValueError(f"Position ({x},{y}) is outside the board")
        return y * self.SIZE + x
    
    def _bitpos_to_pos(self, bitpos: int) -> Tuple[int, int]:
        """Convert bit position (0-48) to x,y coordinates"""
        if not (0 <= bitpos < self.SIZE * self.SIZE):
            raise ValueError(f"Bit position {bitpos} is invalid")
        return bitpos % self.SIZE, bitpos // self.SIZE
    
    def _set_bit(self, bitboard: int, x: int, y: int) -> int:
        """Set the bit at position (x,y) in the given bitboard"""
        bitpos = self._pos_to_bitpos(x, y)
        return bitboard | (1 << bitpos)
    
    def _clear_bit(self, bitboard: int, x: int, y: int) -> int:
        """Clear the bit at position (x,y) in the given bitboard"""
        bitpos = self._pos_to_bitpos(x, y)
        return bitboard & ~(1 << bitpos)
    
    def _test_bit(self, bitboard: int, x: int, y: int) -> bool:
        """Test if the bit at position (x,y) is set in the given bitboard"""
        bitpos = self._pos_to_bitpos(x, y)
        return (bitboard & (1 << bitpos)) != 0
    
    def setup_starting_position(self):
        """Set up the initial game position"""
        # Reset all bitboards
        self.red_guardian = 0
        self.blue_guardian = 0
        self.red_towers = [0] * 8
        self.blue_towers = [0] * 8
        
        # Place Red Guardian (Wächter) at D7
        self.red_guardian = self._set_bit(self.red_guardian, 3, 0)
        
        # Place Blue Guardian (Wächter) at D1
        self.blue_guardian = self._set_bit(self.blue_guardian, 3, 6)
        
        # Place Red Towers with height 1
        red_tower_positions = [(0, 0), (1, 0), (2, 1), (3, 2), (4, 1), (5, 0), (6, 0)]  # A7, B7, C6, D5, E6, F7, G7
        for x, y in red_tower_positions:
            self.red_towers[1] = self._set_bit(self.red_towers[1], x, y)
        
        # Place Blue Towers with height 1
        blue_tower_positions = [(0, 6), (1, 6), (2, 5), (3, 4), (4, 5), (5, 6), (6, 6)]  # A1, B1, C2, D3, E2, F1, G1
        for x, y in blue_tower_positions:
            self.blue_towers[1] = self._set_bit(self.blue_towers[1], x, y)
    
    def get_stack_height(self, x: int, y: int) -> int:
        """Get the height of the stack at position (x,y)"""
        # Check for guardians first
        if self._test_bit(self.red_guardian, x, y) or self._test_bit(self.blue_guardian, x, y):
            return 1
        
        # Check tower stacks - find the highest non-zero bit
        for h in range(7, 0, -1):
            if self._test_bit(self.red_towers[h], x, y) or self._test_bit(self.blue_towers[h], x, y):
                return h
        
        return 0  # Empty square
    
    def get_stack_owner(self, x: int, y: int) -> Optional[int]:
        """Get the player who owns the stack at (x,y) or None if empty"""
        # Check if Red player's pieces are at this position
        if self._test_bit(self.red_guardian, x, y):
            return 1
        
        for h in range(1, 8):
            if self._test_bit(self.red_towers[h], x, y):
                return 1
        
        # Check if Blue player's pieces are at this position
        if self._test_bit(self.blue_guardian, x, y):
            return 2
        
        for h in range(1, 8):
            if self._test_bit(self.blue_towers[h], x, y):
                return 2
        
        return None  # Empty square
    
    def get_top_piece_type(self, x: int, y: int) -> Optional[PieceType]:
        """Get the type of the top piece at position (x,y) or None if empty"""
        # Check for guardians first
        if self._test_bit(self.red_guardian, x, y) or self._test_bit(self.blue_guardian, x, y):
            return PieceType.WAECHTER
        
        # Check tower stacks - find the highest non-zero bit
        for h in range(7, 0, -1):
            if self._test_bit(self.red_towers[h], x, y) or self._test_bit(self.blue_towers[h], x, y):
                return PieceType.TURM
        
        return None  # Empty square
    
    def move_stack(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int], height: int) -> None:
        """Move a stack of pieces from one position to another"""
        from_x, from_y = from_pos
        to_x, to_y = to_pos
        
        # Get information about the source stack
        owner = self.get_stack_owner(from_x, from_y)
        piece_type = self.get_top_piece_type(from_x, from_y)
        stack_height = self.get_stack_height(from_x, from_y)
        
        if owner is None or piece_type is None or stack_height < height:
            raise ValueError("Invalid move: source stack cannot be moved")
        
        # Handle guardian moves
        if piece_type == PieceType.WAECHTER:
            if owner == 1:  # Red guardian
                # Clear old position
                self.red_guardian = self._clear_bit(self.red_guardian, from_x, from_y)
                # Set new position
                self.red_guardian = self._set_bit(self.red_guardian, to_x, to_y)
            else:  # Blue guardian
                # Clear old position
                self.blue_guardian = self._clear_bit(self.blue_guardian, from_x, from_y)
                # Set new position
                self.blue_guardian = self._set_bit(self.blue_guardian, to_x, to_y)
            return
        
        # Handle tower moves
        # We need to update the tower bitboards for the source and destination
        if owner == 1:  # Red towers
            # Clear the source position in the original height bitboard
            self.red_towers[stack_height] = self._clear_bit(self.red_towers[stack_height], from_x, from_y)
            
            # If not moving all pieces, update the source with remaining pieces
            if height < stack_height:
                self.red_towers[stack_height - height] = self._set_bit(self.red_towers[stack_height - height], from_x, from_y)
            
            # Calculate new height at destination
            dest_height = self.get_stack_height(to_x, to_y)
            new_height = height
            
            # If destination already has pieces of the same player, add heights
            if dest_height > 0 and self.get_stack_owner(to_x, to_y) == 1:
                new_height += dest_height
                # Clear the destination's old height
                self.red_towers[dest_height] = self._clear_bit(self.red_towers[dest_height], to_x, to_y)
            
            # Set the new height at destination
            self.red_towers[new_height] = self._set_bit(self.red_towers[new_height], to_x, to_y)
        else:  # Blue towers
            # Clear the source position in the original height bitboard
            self.blue_towers[stack_height] = self._clear_bit(self.blue_towers[stack_height], from_x, from_y)
            
            # If not moving all pieces, update the source with remaining pieces
            if height < stack_height:
                self.blue_towers[stack_height - height] = self._set_bit(self.blue_towers[stack_height - height], from_x, from_y)
            
            # Calculate new height at destination
            dest_height = self.get_stack_height(to_x, to_y)
            new_height = height
            
            # If destination already has pieces of the same player, add heights
            if dest_height > 0 and self.get_stack_owner(to_x, to_y) == 2:
                new_height += dest_height
                # Clear the destination's old height
                self.blue_towers[dest_height] = self._clear_bit(self.blue_towers[dest_height], to_x, to_y)
            
            # Set the new height at destination
            self.blue_towers[new_height] = self._set_bit(self.blue_towers[new_height], to_x, to_y)
    
    def capture_piece(self, pos: Tuple[int, int]) -> None:
        """Remove a piece at the given position (for captures)"""
        x, y = pos
        owner = self.get_stack_owner(x, y)
        piece_type = self.get_top_piece_type(x, y)
        
        if owner is None:
            return  # Nothing to capture
        
        if piece_type == PieceType.WAECHTER:
            if owner == 1:  # Red guardian
                self.red_guardian = self._clear_bit(self.red_guardian, x, y)
            else:  # Blue guardian
                self.blue_guardian = self._clear_bit(self.blue_guardian, x, y)
        else:  # Tower
            height = self.get_stack_height(x, y)
            if owner == 1:  # Red tower
                self.red_towers[height] = self._clear_bit(self.red_towers[height], x, y)
            else:  # Blue tower
                self.blue_towers[height] = self._clear_bit(self.blue_towers[height], x, y)
    
    def print_board(self) -> None:
        """Print a text representation of the board"""
        print("  A B C D E F G")
        for y in range(self.SIZE):
            row = f"{7-y} "
            for x in range(self.SIZE):
                owner = self.get_stack_owner(x, y)
                piece_type = self.get_top_piece_type(x, y)
                height = self.get_stack_height(x, y)
                
                if owner is None:
                    row += ". "
                elif piece_type == PieceType.WAECHTER:
                    row += ("R" if owner == 1 else "B") + "G "
                else:  # Tower
                    row += ("r" if owner == 1 else "b") + str(height) + " "
            print(row)
    
    def to_fen(self, current_player: int) -> str:
        """Convert the bitboard to FEN notation"""
        rows = []
        
        for y in range(self.SIZE):
            row = ""
            empty_count = 0
            
            for x in range(self.SIZE):
                owner = self.get_stack_owner(x, y)
                piece_type = self.get_top_piece_type(x, y)
                height = self.get_stack_height(x, y)
                
                if owner is None:
                    # Empty square
                    empty_count += 1
                else:
                    # If there were empty squares before this piece, add them to the row
                    if empty_count > 0:
                        row += str(empty_count)
                        empty_count = 0
                    
                    # Handle Guardians (Wächter)
                    if piece_type == PieceType.WAECHTER:
                        if owner == 1:
                            row += "RG"  # Red Guardian
                        else:
                            row += "BG"  # Blue Guardian
                    # Handle Towers (Turm)
                    else:
                        if owner == 1:
                            row += f"r{height}"  # Red Tower
                        else:
                            row += f"b{height}"  # Blue Tower
            
            # If there are empty squares at the end of the row, add them
            if empty_count > 0:
                row += str(empty_count)
            
            rows.append(row)
        
        # Join rows with '/' and add current player
        board_str = '/'.join(rows)
        player_str = 'r' if current_player == 1 else 'b'
        
        return f"{board_str} {player_str}"
    
    @classmethod
    def from_fen(cls, fen_str: str) -> Tuple['BitboardBoard', int]:
        """Create a BitboardBoard from a FEN string and return it with the current player"""
        from core.fen import FenParser
        parser = FenParser()
        board, current_player = parser.parse_fen(fen_str)
        
        # Convert the regular board to a bitboard
        bitboard = cls(setup_initial=False)
        
        for y in range(bitboard.SIZE):
            for x in range(bitboard.SIZE):
                stack = board.get_stack(x, y)
                if not stack:
                    continue
                
                top_piece = stack[-1]
                height = len(stack)
                
                if top_piece.piece_type == PieceType.WAECHTER:
                    if top_piece.player == 1:  # Red guardian
                        bitboard.red_guardian = bitboard._set_bit(bitboard.red_guardian, x, y)
                    else:  # Blue guardian
                        bitboard.blue_guardian = bitboard._set_bit(bitboard.blue_guardian, x, y)
                else:  # Tower
                    if top_piece.player == 1:  # Red tower
                        bitboard.red_towers[height] = bitboard._set_bit(bitboard.red_towers[height], x, y)
                    else:  # Blue tower
                        bitboard.blue_towers[height] = bitboard._set_bit(bitboard.blue_towers[height], x, y)
        
        return bitboard, current_player 