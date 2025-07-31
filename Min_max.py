#!/usr/bin/env python3
import sys
import time
from copy import deepcopy
from core.fen import FenParser
from core.bitboard_rules import BitboardRules
from evaluate import evaluate
from win_check import check_win_by_distance_or_capture

MAX_DEPTH = 4
nodes_visited = 0
WIN_SCORE = 1_000_000

def order_moves(rules, moves):
    def priority(move):
        from_pos, to_pos, height = move
        temp = deepcopy(rules)
        temp.make_move(from_pos, to_pos, height)
        if check_win_by_distance_or_capture(temp.board, rules.current_player):
            return 3
        piece_type = rules.board.get_top_piece_type(*from_pos)
        if piece_type.name == 'WAECHTER':
            return 2
        owner_dest = rules.board.get_stack_owner(*to_pos)
        if owner_dest is not None and owner_dest != rules.current_player:
            return 1
        return 0
    return sorted(moves, key=priority, reverse=True)

def minmax(rules, depth, player):
    global nodes_visited
    nodes_visited += 1  # count this node

    # Win/loss cutoff
    if check_win_by_distance_or_capture(rules.board, player):
        return WIN_SCORE
    if check_win_by_distance_or_capture(rules.board, 3 - player):
        return -WIN_SCORE

    moves = rules.get_legal_moves(player)
    if depth == 0 or not moves:
        return evaluate(rules.board.to_fen(player))

    best = float('-inf')
    for move in order_moves(rules, moves):
        next_rules = deepcopy(rules)
        next_rules.make_move(*move)
        next_rules.current_player = 3 - player
        val = -minmax(next_rules, depth - 1, 3 - player)
        if val > best:
            best = val
        #alpha = max(alpha, val)
        if best >= WIN_SCORE:
            break
    return best

def choose_best_move(fen_str, depth):
    global nodes_visited
    #nodes_visited += 1
    #nodes_visited = 0  # reset count

    parser = FenParser()
    board, player = parser.parse_fen(fen_str)
    rules = BitboardRules(board)
    rules.current_player = player

    moves = rules.get_legal_moves(player)
    moves = order_moves(rules, moves)

    # Immediate-win check
    for move in moves:
        nodes_visited += 1  # counting this trial
        temp_rules = deepcopy(rules)
        temp_rules.make_move(*move)
        if check_win_by_distance_or_capture(temp_rules.board, player):
            return FenParser().describe_move(*move)

    best_move = None
    best_score = float('-inf')
    for move in moves:
        nodes_visited += 1  # count this root move trial
        next_rules = deepcopy(rules)
        next_rules.make_move(*move)
        next_rules.current_player = 3 - player
        score = -minmax(next_rules, depth - 1, 3 - player)
        if score > best_score:
            best_score = score
            best_move = move
        if best_score >= WIN_SCORE:
            break

    return FenParser().describe_move(*best_move)

def main():
    if len(sys.argv) < 2:
        print("Usage: python alpha_beta_ki.py \"FEN_STRING\"")
        sys.exit(1)
    fen_str = sys.argv[1]
    start = time.time()
    move = choose_best_move(fen_str, MAX_DEPTH)
    duration = time.time() - start
    print(move)
    print(f"Time taken: {duration:.2f} seconds")
    print(f"Nodes visited: {nodes_visited}")

if __name__ == '__main__':
    main()
