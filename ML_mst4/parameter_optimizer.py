#!/usr/bin/env python3
import os, sys
# Ensure project root is on sys.path so that evaluate, alpha_beta_ki are importable
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)
"""
Parameter optimization using genetic algorithm.
Evolves better evaluation parameters for the Turm & Wächter AI.
"""

import json
import random
import time
import sys
from ML_mst4.tournament_runner import TournamentRunner
from evaluate import DEFAULT_PARAMS

class ParameterOptimizer:
    def __init__(self, population_size=10, mutation_rate=0.4):
        self.population_size = population_size
        self.mutation_rate = mutation_rate
        self.tournament_runner = TournamentRunner(max_moves=20, move_timeout=0.5)
        self.generation = 0
        self.best_ever_score = -float('inf')
        self.best_ever_params = None
        
        # Define EXTREME parameter ranges to create very different behaviors
        # Much wider ranges to force dramatic playstyle differences
        self.param_ranges = {
            'material_weight': (5, 80),        # 5x to 80 - huge material focus vs ignore
            'guardian_advance': (10, 200),     # 10 to 200 - super conservative vs kamikaze
            'guardian_safety': (20, 300),      # 20 to 300 - reckless vs paranoid
            'center_control': (5, 100),        # 5 to 100 - ignore center vs obsessed
            'tower_height': (1, 60),           # 1 to 60 - flat vs super tall preference
            'aggression': (5, 120),            # 5 to 120 - passive vs hyper-aggressive
            'mobility': (1, 50),               # 1 to 50 - ignore options vs maximize moves
            'positioning': (5, 80),            # 5 to 80 - ignore position vs positional master
            'tempo': (1, 60),                  # 1 to 60 - slow vs tempo obsessed
            'win_bonus': (8000, 12000),        # Keep win bonus stable
        }
    
    def create_random_individual(self):
        """Create a random parameter set with extreme ranges"""
        individual = {}
        for param, (min_val, max_val) in self.param_ranges.items():
            if param == 'win_bonus':
                individual[param] = random.randint(int(min_val), int(max_val))
            else:
                # Use full range for maximum diversity
                individual[param] = random.uniform(min_val, max_val)
        return individual
    
    def create_extreme_individual(self):
        """Create an individual with extreme values for testing"""
        individual = {}
        for param, (min_val, max_val) in self.param_ranges.items():
            if param == 'win_bonus':
                individual[param] = random.randint(int(min_val), int(max_val))
            else:
                # Pick extreme values (very high or very low)
                if random.random() < 0.5:
                    individual[param] = min_val + (max_val - min_val) * 0.1  # Very low
                else:
                    individual[param] = min_val + (max_val - min_val) * 0.9  # Very high
        return individual
    
    def mutate_individual(self, individual):
        """Mutate with massive changes for extreme diversity"""
        mutated = individual.copy()
        
        for param in mutated:
            if random.random() < self.mutation_rate:
                min_val, max_val = self.param_ranges[param]
                
                if param == 'win_bonus':
                    mutated[param] = random.randint(int(min_val), int(max_val))
                else:
                    # Huge mutations - 60% of range for maximum change
                    range_size = max_val - min_val
                    mutation_size = range_size * 0.6
                    
                    new_value = individual[param] + random.uniform(-mutation_size, mutation_size)
                    new_value = max(min_val, min(max_val, new_value))
                    mutated[param] = new_value
        
        return mutated
    
    def crossover(self, parent1, parent2):
        """Create child by combining parents with extreme variations"""
        child = {}
        for param in parent1:
            if random.random() < 0.5:
                child[param] = parent1[param]
            else:
                child[param] = parent2[param]
            
            # High chance of extreme randomization during crossover
            if random.random() < 0.2:  # 20% chance of complete randomization
                min_val, max_val = self.param_ranges[param]
                if param == 'win_bonus':
                    child[param] = random.randint(int(min_val), int(max_val))
                else:
                    child[param] = random.uniform(min_val, max_val)
        
        return child
    
    def evaluate_individual(self, individual):
        """Evaluate individual against baseline"""
        baseline = DEFAULT_PARAMS.copy()
        
        # Use minimal games for speed
        num_games = 4
        
        print(f"    Eval", end="", flush=True)
        
        try:
            wins1, wins2, draws = self.tournament_runner.run_tournament(
                individual, baseline, num_games=num_games
            )
            
            total_games = wins1 + wins2 + draws
            if total_games == 0:
                return 0.0
            
            win_rate = wins1 / total_games
            # Huge bonus for decisive games (avoiding draws)
            decisiveness_bonus = (1.0 - draws / total_games) * 0.5  # 50% bonus for no draws
            
            score = win_rate + decisiveness_bonus
            print(f":{score:.2f}", end="")
            
            return score
            
        except Exception as e:
            print(f":ERR", end="")
            return 0.0
    
    def tournament_selection(self, population, scores, tournament_size=2):
        """Simple tournament selection"""
        tournament_indices = random.sample(range(len(population)), tournament_size)
        tournament_scores = [scores[i] for i in tournament_indices]
        winner_idx = tournament_indices[tournament_scores.index(max(tournament_scores))]
        return population[winner_idx]
    
    def run_optimization(self, max_generations=10, output_file="optimized_params.json"):
        """Run the genetic algorithm optimization"""
        
        print("Turm & Wächter AI Parameter Optimization (EXTREME MODE)")
        print("=" * 60)
        print(f"Population: {self.population_size}, Generations: {max_generations}")
        print(f"Games per eval: 4, Mutation: {self.mutation_rate}")
        print(f"Parameters: {len(self.param_ranges)} with EXTREME ranges")
        print("=" * 60)
        print()
        
        # Initialize population with mix of random and extreme individuals
        print("Initializing population...")
        population = []
        
        # Add some extreme individuals for maximum diversity
        for i in range(self.population_size // 2):
            population.append(self.create_extreme_individual())
        
        # Add some random individuals
        for i in range(self.population_size - len(population)):
            population.append(self.create_random_individual())
        
        for generation in range(max_generations):
            self.generation = generation + 1
            start_time = time.time()
            
            print(f"\n--- Generation {self.generation}/{max_generations} ---")
            
            # Evaluate population
            scores = []
            for i, individual in enumerate(population):
                print(f"Ind{i+1}/{self.population_size}: ", end="")
                score = self.evaluate_individual(individual)
                scores.append(score)
                
                # Track best ever
                if score > self.best_ever_score:
                    self.best_ever_score = score
                    self.best_ever_params = individual.copy()
                
                print(" |", end="")
            
            print()  # New line after all individuals
            
            # Generation statistics
            best_score = max(scores)
            avg_score = sum(scores) / len(scores)
            
            gen_time = time.time() - start_time
            
            print(f"Gen {self.generation}: Best {best_score:.2f}, Avg {avg_score:.2f}, Overall {self.best_ever_score:.2f} ({gen_time:.1f}s)")
            
            # Early termination if excellent solution
            if best_score > 0.9:
                print(f"Excellent solution found!")
                break
            
            # Create next generation (except for last generation)
            if generation < max_generations - 1:
                print("Creating next generation...")
                new_population = []
                
                # Keep best individual (elitism)
                best_idx = scores.index(best_score)
                new_population.append(population[best_idx])
                
                # Generate rest with extreme variations
                while len(new_population) < self.population_size:
                    parent1 = self.tournament_selection(population, scores)
                    parent2 = self.tournament_selection(population, scores)
                    
                    child = self.crossover(parent1, parent2)
                    child = self.mutate_individual(child)
                    
                    new_population.append(child)
                
                population = new_population
        
        # Save best result inside script directory when path is relative
        if self.best_ever_params:
            if not os.path.isabs(output_file):
                output_file_path = os.path.join(os.path.dirname(__file__), output_file)
            else:
                output_file_path = output_file
            with open(output_file_path, 'w') as f:
                json.dump(self.best_ever_params, f, indent=2)

        # Inform about exact save location
        saved_path = output_file_path if self.best_ever_params else output_file
        
        print("\n" + "=" * 60)
        print("OPTIMIZATION COMPLETE!")
        print(f"Best score: {self.best_ever_score:.2f}")
        print(f"Saved to: {saved_path}")
        print("=" * 60)
        
        # Show parameter changes from default
        if self.best_ever_params:
            print("Most extreme parameter changes:")
            changes = []
            for param, value in self.best_ever_params.items():
                default_val = DEFAULT_PARAMS[param]
                if abs(value - default_val) > 0.01:
                    pct_change = ((value - default_val) / default_val) * 100
                    changes.append((abs(pct_change), param, value, default_val, pct_change))
            
            # Show top 5 biggest changes
            changes.sort(reverse=True)
            for _, param, value, default_val, pct_change in changes[:5]:
                print(f"  {param}: {value:.1f} (was {default_val}, {pct_change:+.0f}%)")
        
        return self.best_ever_params, self.best_ever_score


def main():
    if len(sys.argv) > 1 and sys.argv[1] == "test":
        # Quick test mode
        print("Testing optimization (extreme mini run)...")
        optimizer = ParameterOptimizer(population_size=3)
        best_params, best_score = optimizer.run_optimization(
            max_generations=2, 
            output_file="test_params.json"
        )
    else:
        # Full optimization
        print("Starting EXTREME parameter optimization...")
        
        optimizer = ParameterOptimizer(
            population_size=6,       # Small population for speed
            mutation_rate=0.4        # Very high mutation for exploration
        )
        
        best_params, best_score = optimizer.run_optimization(
            max_generations=3,       # Few generations
            output_file="optimized_params.json"
        )
    
    print("Optimization completed!")
    return best_params, best_score


if __name__ == "__main__":
    main() 