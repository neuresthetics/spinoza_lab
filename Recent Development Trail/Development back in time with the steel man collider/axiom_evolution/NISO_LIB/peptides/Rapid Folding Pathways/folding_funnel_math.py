# folding_funnel_math.py
# Models protein folding landscapes: funneled energy surfaces for rapid pathways
# Implements diffusion on 1D reaction coordinate (Q: 0 unfolded → 1 native)
# Contrasts downhill (barrierless, fast) vs. two-state (with barrier, cooperative)
# Uses Langevin dynamics for stochastic trajectories; computes mean first-passage time (MFPT)
# Lineage: Neuresthetic Ethics Eternal – Protein Folding Hardening
# Evaluation: 2025-12-20 (inspired by 2025 pathway ensembles; minimal frustration principle)
# Contrast: Integrates amyloid transients from peptide_math.py for duality (trap vs. harmony)

import numpy as np
import matplotlib.pyplot as plt
from scipy.integrate import odeint  # For amyloid contrast

# Step 1: Folding Funnel Potentials (1D Reaction Coordinate Q ∈ [0,1])
def potential(Q, regime='downhill', barrier_height=0.0, barrier_pos=0.5, barrier_width=0.1, slope=5.0):
    """
    Energy landscape V(Q):
    - Base: funneled slope toward native (Q=1)
    - Downhill: no barrier
    - Two-state: add Gaussian barrier for cooperativity
    """
    V = -slope * Q  # Funnel slope to native minimum
    if regime == 'two_state':
        V += barrier_height * np.exp(-((Q - barrier_pos)**2) / (2 * barrier_width**2))
    return V

# Derivative for force in Langevin
def dV_dQ(Q, regime='downhill', **params):
    slope = params.get('slope', 5.0)
    dV = -slope  # Constant force from slope
    if regime == 'two_state':
        barrier_height = params.get('barrier_height', 3.0)
        barrier_pos = params.get('barrier_pos', 0.5)
        barrier_width = params.get('barrier_width', 0.1)
        gauss = np.exp(-((Q - barrier_pos)**2) / (2 * barrier_width**2))
        dV += barrier_height * gauss * (-2 * (Q - barrier_pos) / (2 * barrier_width**2))
    return dV

# Step 2: Langevin Dynamics Simulation (Stochastic Trajectories)
def simulate_trajectory(Q0=0.0, dt=0.01, gamma=1.0, D=1.0, t_max=1000, regime='downhill', absorb_at=1.0, **pot_params):
    """
    Simulate single path: dQ = -gamma * dV/dQ dt + sqrt(2 D dt) dW (Brownian)
    Returns time to absorb at native (Q >= absorb_at) or t_max if not
    """
    Q = Q0
    t = 0.0
    while t < t_max and Q < absorb_at:
        force = -gamma * dV_dQ(Q, regime, **pot_params)
        noise = np.sqrt(2 * D * dt) * np.random.randn()
        Q += force * dt + noise
        Q = np.clip(Q, 0.0, 1.0)  # Bound to [0,1]
        t += dt
    return t if Q >= absorb_at else np.inf  # Infinite if not folded

# Compute MFPT over N trajectories
def compute_mfpt(N=100, regime='downhill', **params):
    times = [simulate_trajectory(regime=regime, **params) for _ in range(N)]
    finite_times = [tt for tt in times if np.isfinite(tt)]
    return np.mean(finite_times) if finite_times else np.inf

# Step 3: Amyloid Contrast (from peptide_math.py ODEs, simplified)
def amyloid_model(y, t, params):
    rho, P = y
    v_s, lam, memes, mu, kappa0, alpha, P_target, amplitude = params
    kappa = kappa0 * np.tanh(alpha * np.abs(P_target - P))
    tau_o = amplitude * np.exp(-((t - 5)**2) / 2)  # Transient peak
    drho_dt = v_s * (1 - kappa) * (1 - rho) * tau_o - lam * rho + memes * mu * rho * (1 - rho)
    dP_dt = P * (1 - rho) * kappa * lam - v_s * rho * P * tau_o
    return [drho_dt, dP_dt]

def simulate_amyloid(regime='toxic'):
    if regime == 'toxic':
        params = (0.8, 0.3, 0.2, 0.1, 0.4, 0.5, 1.5, 1.0)
    elif regime == 'benign':
        params = (0.3, 0.6, 0.1, 0.05, 0.9, 0.2, 2.0, 0.5)
    y0 = [0.1, 1.0]
    t_span = np.linspace(0, 10, 100)
    sol = odeint(amyloid_model, y0, t_span, args=(params,))
    # "Time" to high ρ (trap): first t where ρ > 0.8
    trap_idx = np.where(sol[:, 0] > 0.8)[0]
    trap_time = t_span[trap_idx[0]] if trap_idx.size > 0 else np.inf
    return trap_time, sol

# Step 4: Run Simulations and Visualize
# Parameters
downhill_params = {'slope': 5.0}
two_state_params = {'regime': 'two_state', 'barrier_height': 3.0, 'barrier_pos': 0.5, 'barrier_width': 0.1, 'slope': 5.0}

# Compute MFPTs
mfpt_downhill = compute_mfpt(N=100, dt=0.001, t_max=100, regime='downhill', **downhill_params)
mfpt_two_state = compute_mfpt(N=100, dt=0.001, t_max=100, **two_state_params)

print(f"MFPT Downhill: {mfpt_downhill:.2f} time units")
print(f"MFPT Two-State: {mfpt_two_state:.2f} time units")

# Amyloid contrast
toxic_trap_time, toxic_sol = simulate_amyloid('toxic')
benign_trap_time, benign_sol = simulate_amyloid('benign')
print(f"Amyloid Toxic Trap Time: {toxic_trap_time:.2f}" if np.isfinite(toxic_trap_time) else "Amyloid Toxic: No Trap")
print(f"Amyloid Benign Trap Time: {benign_trap_time:.2f}" if np.isfinite(benign_trap_time) else "Amyloid Benign: No Trap")

# Visualization
Q_vals = np.linspace(0, 1, 100)
V_downhill = potential(Q_vals, regime='downhill', **downhill_params)
V_two_state = potential(Q_vals, **two_state_params)

plt.figure(figsize=(12, 6))

# Potentials
plt.subplot(1, 2, 1)
plt.plot(Q_vals, V_downhill, label='Downhill (Barrierless)', color='blue')
plt.plot(Q_vals, V_two_state, label='Two-State (Barrier)', color='green')
plt.xlabel('Q (Folding Coordinate)')
plt.ylabel('V (Potential Energy)')
plt.title('Folding Funnel Landscapes')
plt.legend()
plt.grid(True)

# Example Trajectories (one each)
t_downhill = simulate_trajectory(regime='downhill', dt=0.001, t_max=100, **downhill_params)
t_two_state = simulate_trajectory(**two_state_params, dt=0.001, t_max=100)

# For plotting, re-simulate with history
def simulate_with_history(**sim_params):
    Q = sim_params.pop('Q0', 0.0)
    dt = sim_params.pop('dt', 0.001)
    t_max = sim_params.pop('t_max', 100)
    absorb_at = sim_params.pop('absorb_at', 1.0)
    gamma = sim_params.pop('gamma', 1.0)
    D = sim_params.pop('D', 1.0)
    regime = sim_params.pop('regime', 'downhill')
    
    Q_hist = [Q]
    t_hist = [0.0]
    t = 0.0
    while t < t_max and Q < absorb_at:
        force = -gamma * dV_dQ(Q, regime, **sim_params)
        noise = np.sqrt(2 * D * dt) * np.random.randn()
        Q += force * dt + noise
        Q = np.clip(Q, 0.0, 1.0)
        t += dt
        Q_hist.append(Q)
        t_hist.append(t)
    return np.array(t_hist), np.array(Q_hist)

t_down, Q_down = simulate_with_history(regime='downhill', **downhill_params)
t_two, Q_two = simulate_with_history(**two_state_params)

plt.subplot(1, 2, 2)
plt.plot(t_down, Q_down, label='Downhill Trajectory', color='blue')
plt.plot(t_two, Q_two, label='Two-State Trajectory', color='green')
plt.xlabel('Time')
plt.ylabel('Q')
plt.title('Sample Folding Pathways')
plt.legend()
plt.grid(True)

plt.tight_layout()
plt.show()

# Amyloid Contrast Plot (ρ trajectories)
t_span = np.linspace(0, 10, 100)
plt.figure(figsize=(6, 4))
plt.plot(t_span, toxic_sol[:, 0], label='Amyloid Toxic ρ (Trap)', color='red')
plt.plot(t_span, benign_sol[:, 0], label='Amyloid Benign ρ (Harmony)', color='darkgreen')
plt.xlabel('Time')
plt.ylabel('ρ (Rigidity)')
plt.title('Contrast: Amyloid Transients vs. Folding Speed')
plt.legend()
plt.grid(True)
plt.show()

# Interpretation: Downhill folding shows ultrafast MFPT with no barriers; two-state adds delay via cooperativity. Amyloid toxic regime contrasts with slow rigidity trap due to transients.