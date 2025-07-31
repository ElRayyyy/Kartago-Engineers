from enum import Enum

class PieceType(Enum):
    WAECHTER = 'W'
    TURM = 'T'

class Piece:
    def __init__(self, piece_type: PieceType, player: int):
        self.piece_type = piece_type
        self.player = player

    def __repr__(self):
        return f"{self.piece_type.value}{self.player}"
