import pygame
import json
import sys
import os
import time
from pathlib import Path
from network import Network

# Initialize pygame
pygame.font.init()

# ==============================================
# PATH CONFIGURATION
# ==============================================
ALPHA_BETA_KI_PATH = r"C:\Users\ylang\Downloads\turm_waechter_ai\turm_waechter_ai"
sys.path.insert(0, ALPHA_BETA_KI_PATH)

# Verify the file exists
KI_FILE = os.path.join(ALPHA_BETA_KI_PATH, "alpha_beta_ki.py")
print(f"Looking for alpha_beta_ki.py at: {KI_FILE}")
print(f"File exists: {os.path.exists(KI_FILE)}")

try:
    from alpha_beta_ki import choose_best_move, format_move_description
    print("Successfully imported alpha_beta_ki!")
except ImportError as e:
    print(f"Import failed: {e}")
    print("Please verify:")
    print(f"1. The file exists at: {KI_FILE}")
    print("2. The filename is EXACTLY 'alpha_beta_ki.py' (case-sensitive)")
    print("3. The file contains 'def choose_best_move()' function")
    sys.exit(1)

class AIClient:
    def __init__(self):
        self.network = None
        self.player = None
        self.max_retries = 3
        self.retry_delay = 2  # seconds
        self.initialize_connection()

    def initialize_connection(self):
        """Handle connection initialization with retries"""
        for attempt in range(self.max_retries):
            try:
                self.network = Network()
                player_assignment = self.network.getP()
                
                if player_assignment is None:
                    raise ValueError("Server returned no player assignment")
                    
                self.player = int(player_assignment)
                print(f"Successfully connected as player {self.player}")
                return
                
            except Exception as e:
                print(f"Connection attempt {attempt + 1} failed: {e}")
                if attempt < self.max_retries - 1:
                    print(f"Retrying in {self.retry_delay} seconds...")
                    time.sleep(self.retry_delay)
                else:
                    print("Max connection attempts reached")
                    raise

    def validate_move(self, move):
        """Ensure move follows the required format"""
        try:
            parts = move.split('-')
            return len(parts) == 3 and parts[2].isdigit()
        except:
            return False

    def run(self):
        """Main game loop with robust error handling"""
        while True:
            try:
                # Get game state with retries
                response = None
                for attempt in range(self.max_retries):
                    response = self.network.send(json.dumps("get"))
                    if response:
                        break
                    print(f"Empty response, retry {attempt + 1}/{self.max_retries}")
                    time.sleep(1)
                
                if not response:
                    print("Server not responding")
                    break
                
                game_state = json.loads(response)
                
                # Check for game end
                if game_state.get("end"):
                    print("Game ended normally")
                    break
                    
                # Only act when it's our turn and both connected
                if (game_state["bothConnected"] and 
                    ((self.player == 0 and game_state["turn"] == "r") or 
                     (self.player == 1 and game_state["turn"] == "b"))):
                    
                    print(f"\nCurrent board: {game_state['board']}")
                    print(f"Time remaining: {game_state['time']}ms")
                    
                    # Get and validate AI move
                    ai_move_1 = choose_best_move(game_state["board"])
                    ai_move = format_move_description(ai_move_1)
                    if not self.validate_move(ai_move):
                        raise ValueError(f"Invalid move format: {ai_move}")
                    
                    print(f"AI sending move: {ai_move}")
                    self.network.send(json.dumps(ai_move))
                
                # Small delay to prevent CPU overload
                time.sleep(0.1)
                
            except json.JSONDecodeError:
                print("Received invalid data from server")
                break
            except ConnectionResetError:
                print("Server connection lost")
                break
            except KeyboardInterrupt:
                print("\nAI shutdown requested")
                break
            except Exception as e:
                print(f"Unexpected error: {e}")
                break

        print("Closing connection...")
        if hasattr(self.network, 'client'):
            self.network.client.close()

if __name__ == "__main__":
    try:
        ai = AIClient()
        ai.run()
    except Exception as e:
        print(f"Fatal error: {e}")
        sys.exit(1)