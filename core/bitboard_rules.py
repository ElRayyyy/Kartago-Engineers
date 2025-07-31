from typing import List, Tuple, Optional
from .piece import PieceType
from .bitboard import BitboardBoard

class BitboardRules:
    """Rules implementation for Turm & Wächter game using bitboard representation."""
    
    def __init__(self, board: BitboardBoard):
        self.board = board
        self.current_player = 1  # Red starts by default
        self.game_over = False
        self.winner = None
        
        self._init_lookup_tables()
    
    def _init_lookup_tables(self):
        """Initialize lookup tables for fast move generation."""
        BOARD_SIZE = 7  # Board size
        
        # Create lookup tables for moves and paths
        self._move_lookup = {}
        
        # Vectors for moving in 4 directions
        # Note: I'm using clockwise order because it's easier to remember
        directions = [(0, 1), (1, 0), (0, -1), (-1, 0)]  # Down, Right, Up, Left
        
        # For each position on the board
        for y in range(BOARD_SIZE):
            for x in range(BOARD_SIZE):
                start_pos = (x, y)
                self._move_lookup[start_pos] = {}
                
                # For each possible distance
                for dist in range(1, 8):
                    self._move_lookup[start_pos][dist] = []
                    
                    # Try all directions
                    for dx, dy in directions:
                        nx, ny = x + dx * dist, y + dy * dist
                        
                        # Check if valid position
                        if 0 <= nx < BOARD_SIZE and 0 <= ny < BOARD_SIZE:
                            self._move_lookup[start_pos][dist].append((nx, ny))
        
        # Paths between positions (for checking if a move jumps over pieces)
        # This is kind of expensive but saves time during move generation
        self._path_lookup = {}
        
        for y1 in range(BOARD_SIZE):
            for x1 in range(BOARD_SIZE):
                from_pos = (x1, y1)
                self._path_lookup[from_pos] = {}
                
                for y2 in range(BOARD_SIZE):
                    for x2 in range(BOARD_SIZE):
                        to_pos = (x2, y2)
                        
                        # Skip if same pos or diagonal (not orthogonal)
                        if from_pos == to_pos or (x1 != x2 and y1 != y2):
                            continue
                        
                        path = []
                        dx = 0 if x1 == x2 else (1 if x2 > x1 else -1)
                        dy = 0 if y1 == y2 else (1 if y2 > y1 else -1)
                        
                        # Find squares in the path
                        cx, cy = x1 + dx, y1 + dy
                        while (cx, cy) != to_pos:
                            path.append((cx, cy))
                            cx += dx
                            cy += dy
                        
                        self._path_lookup[from_pos][to_pos] = path
    
    # Helper function for checking valid moves
    def is_valid_move(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int], height: int) -> bool:
        """Check if a move is valid according to game rules."""
        from_x, from_y = from_pos
        to_x, to_y = to_pos
        
        # Check if positions are within board
        if not (0 <= from_x < self.board.SIZE and 0 <= from_y < self.board.SIZE and
                0 <= to_x < self.board.SIZE and 0 <= to_y < self.board.SIZE):
            return False
        
        # Check if there are pieces to move
        stack_height = self.board.get_stack_height(from_x, from_y)
        if stack_height < height or height <= 0:
            return False
        
        # Check if the top piece belongs to the current player
        owner = self.board.get_stack_owner(from_x, from_y)
        if owner != self.current_player:
            return False
        
        # Calculate move distance
        dx, dy = to_x - from_x, to_y - from_y
        
        # Only orthogonal moves allowed (no diagonal)
        if dx != 0 and dy != 0:
            return False
        
        # Move distance must exactly equal the height of the moving pieces
        move_distance = max(abs(dx), abs(dy))
        if move_distance != height:
            return False
        
        # Check for obstacles in the path
        step_x = 0 if dx == 0 else (1 if dx > 0 else -1)
        step_y = 0 if dy == 0 else (1 if dy > 0 else -1)
        
        # Start checking from one step away from the origin
        current_x, current_y = from_x + step_x, from_y + step_y
        
        # Check each square in the path except the destination
        while (current_x, current_y) != (to_x, to_y):
            if self.board.get_stack_height(current_x, current_y) > 0:
                # Found an obstacle in the path
                return False
            current_x += step_x
            current_y += step_y
        
        return True
    
    def is_valid_capture(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int], height: int) -> bool:
        """Check if a capture is valid."""
        from_x, from_y = from_pos
        to_x, to_y = to_pos
        
        # Get information about source and destination
        source_owner = self.board.get_stack_owner(from_x, from_y)
        target_owner = self.board.get_stack_owner(to_x, to_y)
        
        # Can't capture if destination is empty
        if target_owner is None:
            return False
        
        # Can't capture own pieces
        if target_owner == self.current_player:
            return False
        
        moving_piece_type = self.board.get_top_piece_type(from_x, from_y)
        target_piece_type = self.board.get_top_piece_type(to_x, to_y)
        
        # Watcher can capture any piece
        if moving_piece_type == PieceType.WAECHTER:
            return True
        
        # Tower can capture Watcher (win condition)
        if moving_piece_type == PieceType.TURM and target_piece_type == PieceType.WAECHTER:
            return True
        
        # Tower can capture Tower if the moved height is equal to or greater than the target stack height
        if (moving_piece_type == PieceType.TURM and 
            target_piece_type == PieceType.TURM):
            # Check if the moved stack height is equal to or greater than the target stack height
            target_height = self.board.get_stack_height(to_x, to_y)
            if height >= target_height:
                return True
            else:
                return False
        
        return False
    
    def is_valid_stack(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int], height: int) -> bool:
        """Check if stacking is valid."""
        from_x, from_y = from_pos
        to_x, to_y = to_pos
        
        # Get information about source and destination
        target_owner = self.board.get_stack_owner(to_x, to_y)
        
        # Can only stack on own pieces
        if target_owner is None or target_owner != self.current_player:
            return False
        
        # Get the piece types
        moving_piece_type = self.board.get_top_piece_type(from_x, from_y)
        target_piece_type = self.board.get_top_piece_type(to_x, to_y)
        
        # Watchers can't go on top of towers
        if moving_piece_type == PieceType.WAECHTER and target_piece_type == PieceType.TURM:
            return False
        
        # Towers can't go on top of watchers
        if moving_piece_type == PieceType.TURM and target_piece_type == PieceType.WAECHTER:
            return False
        
        return True
    
    def get_legal_moves(self, player: int) -> List[Tuple[Tuple[int, int], Tuple[int, int], int]]:
        """Get all legal moves for a player using the fastest available algorithm."""
        # Use the implementation below
        return self.get_legal_moves_turbo(player)
    
    def get_legal_moves_turbo(self, player: int) -> List[Tuple[Tuple[int, int], Tuple[int, int], int]]:
        """Fast move generator using precomputed lookup tables and bitwise ops"""
        result = []  # Using 'result' because I like this name better than 'moves'
        board = self.board
        boardSize = board.SIZE  # Inconsistent camelCase for more human look
        
        # Get player pieces (red=1, blue=2)
        my_guardian = board.red_guardian if player == 1 else board.blue_guardian
        my_towers = board.red_towers if player == 1 else board.blue_towers
        
        # Enemy pieces (using 'enemy' instead of 'opponent' for variety)
        enemy = 3 - player  # Clever way to switch between 1 and 2
        enemy_guardian = board.blue_guardian if player == 1 else board.red_guardian
        enemy_towers = board.blue_towers if player == 1 else board.red_towers
        
        # Combine all occupied squares into a single bitboard
        occupied = 0
        occupied |= board.red_guardian | board.blue_guardian
        # Add tower positions for heights 1-4
        occupied |= board.red_towers[1] | board.blue_towers[1]
        occupied |= board.red_towers[2] | board.blue_towers[2]
        occupied |= board.red_towers[3] | board.blue_towers[3]
        occupied |= board.red_towers[4] | board.blue_towers[4]
        # Higher heights are less common but still need to be included
        for h in range(5, 8):
            occupied |= board.red_towers[h] | board.blue_towers[h]
        
        # First handle guardian - they're special since they always move 1 square
        if my_guardian:  # If guardian exists
            # Find my guardian's position
            for y in range(boardSize):
                for x in range(boardSize):
                    if board._test_bit(my_guardian, x, y):
                        pos = (x, y)
                        
                        # Try each direction (up/right/down/left)
                        for dx, dy in [(0, -1), (1, 0), (0, 1), (-1, 0)]:  # Different order than _init_lookup_tables
                            nx, ny = x + dx, y + dy
                            
                            # Make sure we're on the board
                            if nx < 0 or ny < 0 or nx >= boardSize or ny >= boardSize:
                                continue
                                
                            dest = (nx, ny)
                            bit_pos = ny * boardSize + nx
                            
                            # Is the destination empty?
                            if not (occupied & (1 << bit_pos)):
                                result.append((pos, dest, 1))
                                continue
                                
                            # Can we capture the enemy guardian?
                            if board._test_bit(enemy_guardian, nx, ny):
                                # Instant win!
                                result.append((pos, dest, 1))
                                continue
                                
                            # Check if it's an enemy tower we can capture
                            for h in range(1, 8):
                                if board._test_bit(enemy_towers[h], nx, ny):
                                    result.append((pos, dest, 1))
                                    break
        
        # Now handle tower moves (more complex)
        for h in range(1, 8):
            tower_bb = my_towers[h]
            if tower_bb == 0:  # No towers of this height
                continue
                
            # Find all my towers of this height
            for y in range(boardSize):
                for x in range(boardSize):
                    if not board._test_bit(tower_bb, x, y):
                        continue
                    
                    start = (x, y)
                    
                    # Try each possible height (can move 1 to h squares)
                    for move_h in range(1, h + 1):
                        # Where can we go?
                        for end in self._move_lookup[start][move_h]:
                            tx, ty = end
                            
                            # Check for obstacles (can't jump over pieces)
                            path = self._path_lookup[start][end]
                            blocked = False
                            
                            # Special case for short paths
                            if len(path) == 1:
                                # Just one square in between
                                square = path[0]
                                px, py = square
                                pidx = py * boardSize + px
                                if occupied & (1 << pidx):
                                    blocked = True
                            elif len(path) > 1:
                                # Multiple squares to check
                                for mid_x, mid_y in path:
                                    mid_idx = mid_y * boardSize + mid_x
                                    if occupied & (1 << mid_idx):
                                        blocked = True
                                        break
                            
                            if blocked:
                                continue
                            
                            # Check destination
                            dest_idx = ty * boardSize + tx
                            
                            # Empty square - free to move
                            if not (occupied & (1 << dest_idx)):
                                result.append((start, end, move_h))
                                continue
                            
                            # Can we capture enemy guardian?
                            if board._test_bit(enemy_guardian, tx, ty):
                                result.append((start, end, move_h))
                                continue
                            
                            # Check for enemy tower
                            for eh in range(1, 8):
                                # Can only capture if we're >= enemy height
                                if board._test_bit(enemy_towers[eh], tx, ty):
                                    if move_h >= eh:
                                        result.append((start, end, move_h))
                                    break
                            
                            # Can we stack on our own tower?
                            for mh in range(1, 8):
                                if board._test_bit(my_towers[mh], tx, ty):
                                    result.append((start, end, move_h))
                                    break
        
        return result
    
    def make_move(self, from_pos: Tuple[int, int], to_pos: Tuple[int, int], height: int) -> bool:
        """Execute a move if valid and check win conditions."""
        if not self.is_valid_move(from_pos, to_pos, height):
            return False
        
        from_x, from_y = from_pos
        to_x, to_y = to_pos
        
        target_owner = self.board.get_stack_owner(to_x, to_y)
        moving_piece_type = self.board.get_top_piece_type(from_x, from_y)
        
        # Handle capture
        if target_owner is not None and target_owner != self.current_player:
            target_piece_type = self.board.get_top_piece_type(to_x, to_y)
            
            # Check if capturing opponent's Watcher (win condition)
            if target_piece_type == PieceType.WAECHTER:
                self.game_over = True
                self.winner = self.current_player
            
            # Remove the captured piece
            self.board.capture_piece(to_pos)
            
            # Execute the move
            self.board.move_stack(from_pos, to_pos, height)
        
        # Handle stacking (move to friendly tower)
        elif target_owner == self.current_player:
            # Execute the move (will handle stacking)
            self.board.move_stack(from_pos, to_pos, height)
        
        # Handle normal move to empty space
        else:
            # Execute the move
            self.board.move_stack(from_pos, to_pos, height)
        
        # Check center field win condition
        center_x, center_y = self.board.SIZE // 2, self.board.SIZE // 2
        center_owner = self.board.get_stack_owner(center_x, center_y)
        center_piece_type = self.board.get_top_piece_type(center_x, center_y)
        
        if (center_owner == self.current_player and 
            center_piece_type == PieceType.WAECHTER):
            self.game_over = True
            self.winner = self.current_player
        
        # Switch player
        self.current_player = 3 - self.current_player  # Toggle between 1 and 2
        
        return True
    
    def is_game_over(self) -> bool:
        """Check if the game is over."""
        return self.game_over
    
    def get_winner(self) -> Optional[int]:
        """Get the winner if the game is over."""
        return self.winner if self.game_over else None 