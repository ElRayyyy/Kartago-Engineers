#!/usr/bin/env python3
import time
import alpha_beta_ki
from alpha_beta_ki import choose_best_move, TIME_BUFFER

def benchmark(fen_str: str, max_depth: int = None):
    """
    Iterativ erhöhte Suchtiefe mit while-Loop.
    Stoppt automatisch, wenn das Zeitbudget ausgelaufen ist
    oder (optional) max_depth erreicht wurde.
    """
    print(f"\nBenchmarking FEN:\n{fen_str}\n")
    start = time.time()
    depth = 1
    while True:
        # Abbruch, falls eine obere Tiefe definiert und erreicht wurde
        if max_depth is not None and depth > max_depth:
            print(f"→ Max-Depth {max_depth} erreicht. Benchmark beendet.")
            break

        # Reset der globalen Variablen
        alpha_beta_ki.ttable.clear()
        alpha_beta_ki.nodes_visited = 1
        alpha_beta_ki.MAX_DEPTH = depth

        print(f"--- Tiefe {depth} ---")

        # nur fen_str übergeben, Tiefe steuert das globale MAX_DEPTH
        best_move, allocated = choose_best_move(fen_str)
        elapsed = time.time() - start

        print(f"Best Move:               {best_move}")
        print(f"Time Taken:              {elapsed:.3f} s (Budget: {allocated:.2f}s)")
        print(f"Nodes Visited:           {alpha_beta_ki.nodes_visited}")
        print(f"Transposition Table Size:{len(alpha_beta_ki.ttable)}\n")

        # Stoppe, wenn das Zeitbudget (minus Puffer) erreicht ist
        if elapsed >= allocated - TIME_BUFFER:
            print(f"→ Zeitbudget von {allocated:.2f}s bei Tiefe {depth} erreicht. Abbruch.")
            break

        depth += 1

if __name__ == "__main__":
    tests = [
        ("Midgame Test", "3RG13/7/3r13/1b12b12/3BG11b11/b16/7 b"),
        ("Endgame Test", "7/7/7/b12r11r11/BG1b15/4RG12/7 b"),
        ("opening","r1r11RG1r1r1/2r11r12/3r13/3b13/7/2b11b12/b1b11BG1b1b1 r"),
        ("midgame_critical","7/r21r24/1BG5/4b22/3b13/3b23/RG6 r"),
        ("midgame,","3RG1r21/4r32/7/r22b13/7/3b23/1b21BGb12 b"),
        ("open_critical","r1r1RG11r1r1/b1b1r1b1r1b1b1/3r13/3b13/7/2b1111/111BG12 r"),
        ("critical", "2RG4/5r11/1b15/b16/7/7/3BG3 r")
    ]

    for label, fen in tests:
        print(f"=== {label} ===")
        benchmark(fen, max_depth=6)
