import time
from Min_max import choose_best_move

try:
    from Min_max import transposition_table
except ImportError:
    transposition_table = None

try:
    from Min_max import nodes_visited
except ImportError:
    nodes_visited = None

def benchmark(fen_str: str, max_depth: int = 4):
    print(f"Benchmarking FEN:\n{fen_str}\n")

    for depth in range(1, max_depth + 1):
        # Reset counters
        if nodes_visited is not None:
            import Min_max
            #Min_max.nodes_visited = 0

        if transposition_table is not None:
            transposition_table.clear()

        start_time = time.time()

        try:
            best_move = choose_best_move(fen_str, depth)
        except Exception as e:
            print(f"[!] Error at depth {depth}: {e}")
            continue

        end_time = time.time()
        duration = end_time - start_time

        print(f"Depth {depth}:")
        print(f"  Best Move: {best_move}")
        print(f"  Time: {duration:.3f} seconds")

        if nodes_visited is not None:
            print(f"  Zustände: {Min_max.nodes_visited}")

        if transposition_table is not None:
            print(f"  Transposition Table Size: {len(transposition_table)}")

        print()

if __name__ == "__main__":
    test_fen = "7/7/7/b12r11r11/BG1b15/4RG12/7 r"
    #midgame "3RG13/7/3r13/1b12b12/3BG11b11/b16/7 r"
    # endgame "7/7/7/b12r11r11/BG1b15/4RG12/7 r"
    benchmark(test_fen)