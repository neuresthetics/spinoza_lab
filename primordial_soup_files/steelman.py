import numpy as np
import matplotlib.pyplot as plt
from dataclasses import dataclass
from typing import List, Tuple, Optional

# =============================================================================
# STEELMAN.PY - The Recursive Steel Man Collider Engine
# Version: 4.0 (Unified Dynamics)
# Based on: motion_law_math_v2.json, logic_topology_math.json
# =============================================================================

@dataclass
class Basin:
    """
    Represents an 'Argument' or 'Worldview' as a geometric basin of attraction.
    Defined in logic_topology_math.json.
    """
    name: str
    center: np.ndarray  # Coordinates [x, y] on the belief manifold
    depth: float        # How stable/convincing the argument is (lowers Free Energy)
    width: float        # How broad the basin is (catchment area)
    
    def free_energy_contribution(self, pos: np.ndarray) -> float:
        """Calculates the local Free Energy (F) well for this argument."""
        dist_sq = np.sum((pos - self.center)**2)
        # F = -depth * exp(-dist^2 / width)
        return -self.depth * np.exp(-dist_sq / self.width)

class BeliefManifold:
    """
    The Riemannian manifold M where beliefs exist.
    Implements the landscape defined in logic_topology_math.json.
    """
    def __init__(self, dimension: int = 2):
        self.dim = dimension
        self.basins: List[Basin] = []
        
    def add_argument(self, name: str, center: List[float], stability: float, scope: float):
        """Adds a basin (Argument) to the landscape."""
        self.basins.append(Basin(name, np.array(center), stability, scope))
        
    def free_energy(self, pos: np.ndarray) -> float:
        """
        Calculates total Free Energy F(xi) at a given state.
        F = Sum(Basins) + Background_Ridge
        """
        # Background tension (the "Ridge" forcing decisions)
        # Centers tension at 0.5, 0.5
        f_background = 0.5 * np.sum((pos - 0.5)**2)
        
        f_basins = sum(b.free_energy_contribution(pos) for b in self.basins)
        return f_background + f_basins
    
    def gradient(self, pos: np.ndarray, epsilon: float = 1e-5) -> np.ndarray:
        """Computes -nabla F (The Conatus Drive)."""
        grad = np.zeros_like(pos)
        for i in range(len(pos)):
            # Finite difference
            pos_plus = pos.copy()
            pos_plus[i] += epsilon
            pos_minus = pos.copy()
            pos_minus[i] -= epsilon
            
            df = self.free_energy(pos_plus) - self.free_energy(pos_minus)
            grad[i] = df / (2 * epsilon)
        return grad

class Agent:
    """
    The active inference agent traversing the manifold.
    Dynamics governed by motion_law_math_v2.json.
    """
    def __init__(self, start_pos: List[float], rigidity: float = 0.5):
        self.pos = np.array(start_pos)
        self.rigidity = rigidity # rho
        self.path = [self.pos.copy()]
        self.rigidity_history = [self.rigidity]
        self.coherence_history = []
        
    def update(self, manifold: BeliefManifold, dt: float = 0.05, 
               lambda_eff: float = 0.5, kappa: float = 0.2):
        """
        Evolves state xi according to the Motion Law:
        dxi/dt = -nabla F (Conatus) + Entropy (Noise) + Momentum
        """
        # 1. Calculate Rational Drive (-nabla F)
        grad_F = manifold.gradient(self.pos)
        conatus_drive = -grad_F
        
        # 2. Entropy Export / NAND Kick (Stochasticity)
        # Higher rigidity requires more entropy to break dogma
        noise_scale = 0.05 * (1 + self.rigidity) 
        entropy_flux = np.random.randn(len(self.pos)) * noise_scale
        
        # 3. Update Position (Euler integration)
        # Rigidity acts as friction/resistance to update
        d_xi = (conatus_drive + entropy_flux) * (1.0 - self.rigidity * 0.5)
        
        self.pos += d_xi * dt
        self.pos = np.clip(self.pos, 0.0, 1.0) # Bound to manifold [0,1]
        
        # 4. Update Dynamics (Dissolution of Dogma)
        # If moving fast (learning), rigidity drops. If stuck, rigidity climbs.
        velocity = np.linalg.norm(d_xi)
        d_rho = -lambda_eff * velocity + 0.01 * (1 - velocity)
        self.rigidity = np.clip(self.rigidity + d_rho, 0.0, 1.0)
        
        # Record stats
        self.path.append(self.pos.copy())
        self.rigidity_history.append(self.rigidity)
        self.coherence_history.append(-manifold.free_energy(self.pos))

class SteelManCollider:
    """
    The orchestration engine for colliding arguments.
    """
    def __init__(self):
        self.manifold = BeliefManifold(dimension=2)
        
    def setup_debate(self, thesis_pos, thesis_strength, 
                     antithesis_pos, antithesis_strength, 
                     synthesis_pos, synthesis_strength):
        """Initializes the landscape with Thesis, Antithesis, and Synthesis basins."""
        self.manifold.add_argument("Thesis", thesis_pos, thesis_strength, 0.1)
        self.manifold.add_argument("Antithesis", antithesis_pos, antithesis_strength, 0.1)
        # The Synthesis is the hidden attractor (The Steel Man)
        self.manifold.add_argument("Synthesis (Steel Man)", synthesis_pos, synthesis_strength, 0.15)
        
    def run_collision(self, start_pos, steps=1000):
        """Runs the simulation."""
        agent = Agent(start_pos, rigidity=0.8) # Start with high dogma
        
        print(f"--- Starting Collision ---")
        print(f"Initial State: {agent.pos}, Rigidity: {agent.rigidity}")
        
        for t in range(steps):
            agent.update(self.manifold)
            
            # Check for convergence (low movement, low rigidity)
            if t > 100 and agent.rigidity < 0.2 and np.linalg.norm(agent.pos - agent.path[-2]) < 0.001:
                print(f"Converged at step {t} to {agent.pos}")
                break
                
        return agent

    def visualize(self, agent, title="Steel Man Collision"):
        """Generates the topological plot."""
        x = np.linspace(0, 1, 100)
        y = np.linspace(0, 1, 100)
        X, Y = np.meshgrid(x, y)
        
        # Compute F landscape
        Z = np.zeros_like(X)
        for i in range(100):
            for j in range(100):
                Z[i,j] = self.manifold.free_energy(np.array([X[i,j], Y[i,j]]))
                
        plt.figure(figsize=(10, 8))
        
        # Plot Landscape
        cp = plt.contourf(X, Y, Z, levels=30, cmap='viridis_r', alpha=0.8)
        plt.colorbar(cp, label='Free Energy (Surprise)')
        
        # Plot Basins
        for b in self.manifold.basins:
            plt.text(b.center[0], b.center[1], b.name, 
                     color='white', ha='center', fontweight='bold', 
                     bbox=dict(facecolor='black', alpha=0.5))
            
        # Plot Path
        path = np.array(agent.path)
        plt.plot(path[:,0], path[:,1], 'w-', lw=2, label='Trajectory')
        plt.plot(path[0,0], path[0,1], 'ro', label='Start (Dogma)')
        plt.plot(path[-1,0], path[-1,1], 'g*', markersize=15, label='Convergence')
        
        plt.title(title)
        plt.xlabel("Belief Dimension 1")
        plt.ylabel("Belief Dimension 2")
        plt.legend()
        plt.grid(True, alpha=0.3)
        plt.show()

# =============================================================================
# EXAMPLE USAGE: The Free Will Debate
# =============================================================================

if __name__ == "__main__":
    collider = SteelManCollider()
    
    # 1. Setup the Logic Topology
    # X-Axis: Determinism (0=Random, 1=Strict Law)
    # Y-Axis: Agency (0=Passive, 1=Active)
    
    # Thesis: "Determinism" (High Law, Low Agency)
    collider.setup_debate(
        thesis_pos=[0.9, 0.1], thesis_strength=1.0,
        
        # Antithesis: "Libertarianism" (Low Law, High Agency)
        antithesis_pos=[0.1, 0.9], antithesis_strength=1.0,
        
        # Synthesis: "Compatibilism" (High Law, Moderate/High Agency)
        # This is the "Steel Man" - a deeper basin
        synthesis_pos=[0.8, 0.7], synthesis_strength=1.5
    )
    
    # 2. Run the Collision
    # Start the agent deep in the "Determinism" basin with high rigidity
    agent_result = collider.run_collision(start_pos=[0.9, 0.1])
    
    # 3. View Results
    collider.visualize(agent_result, title="Collision: Free Will vs. Determinism")