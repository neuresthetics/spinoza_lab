import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Polygon
import json

# Geometric transformation primitives (unchanged — rigid, distance-preserving)
def translate(points: np.ndarray, vector: np.ndarray) -> np.ndarray:
    translation_matrix = np.array([[1, 0, vector[0]],
                                  [0, 1, vector[1]],
                                  [0, 0, 1]])
    homogeneous_points = np.hstack([points, np.ones((len(points), 1))])
    transformed = (translation_matrix @ homogeneous_points.T).T
    return transformed[:, :2]

def rotate(points: np.ndarray, angle_deg: float, center: np.ndarray = np.array([0.0, 0.0])) -> np.ndarray:
    theta = np.radians(angle_deg)
    c, s = np.cos(theta), np.sin(theta)
    rotation_matrix = np.array([[c, -s, 0],
                                [s,  c, 0],
                                [0,  0, 1]])
    translation_to_origin = np.array([[1, 0, -center[0]],
                                      [0, 1, -center[1]],
                                      [0, 0, 1]])
    translation_back = np.array([[1, 0, center[0]],
                                 [0, 1, center[1]],
                                 [0, 0, 1]])
    full_matrix = translation_back @ rotation_matrix @ translation_to_origin
    homogeneous_points = np.hstack([points, np.ones((len(points), 1))])
    transformed = (full_matrix @ homogeneous_points.T).T
    return transformed[:, :2]

def reflect_over_line(points: np.ndarray, line_point: np.ndarray, line_direction: np.ndarray) -> np.ndarray:
    dir_norm = line_direction / np.linalg.norm(line_direction)
    proj_matrix = np.outer(dir_norm, dir_norm)
    perp_matrix = np.eye(2) - proj_matrix
    reflection_matrix = proj_matrix - perp_matrix
    offset = line_point @ (np.eye(2) - reflection_matrix)
    translated = points - offset
    reflected = translated @ reflection_matrix.T
    return reflected + offset

def regular_polygon(n_sides: int, center: np.ndarray = np.array([0.0, 0.0]), radius: float = 1.0) -> np.ndarray:
    if n_sides < 3:
        n_sides = 3
    angles = np.linspace(0, 2 * np.pi, n_sides, endpoint=False)
    x = radius * np.cos(angles) + center[0]
    y = radius * np.sin(angles) + center[1]
    return np.column_stack((x, y))

def best_rigid_alignment(source: np.ndarray, target: np.ndarray, allow_reflection: bool = True) -> np.ndarray:
    mu_s = np.mean(source, axis=0)
    mu_t = np.mean(target, axis=0)
    s_c = source - mu_s
    t_c = target - mu_t
    H = s_c.T @ t_c
    U, _, Vt = np.linalg.svd(H)
    R = Vt.T @ U.T
    if not allow_reflection and np.linalg.det(R) < 0:
        Vt[-1, :] *= -1
        R = Vt.T @ U.T
    aligned = (s_c @ R) + mu_t
    return aligned

def average_min_distance(a: np.ndarray, b: np.ndarray) -> float:
    """Bidirectional average of minimum distances — geometric residual tension proxy."""
    dist_a_to_b = np.min(np.linalg.norm(b - a[:, np.newaxis], axis=2), axis=1).mean()
    dist_b_to_a = np.min(np.linalg.norm(a - b[:, np.newaxis], axis=2), axis=1).mean()
    return (dist_a_to_b + dist_b_to_a) / 2

def plot_multiple_polygons(list_of_points_lists, colors=None, alphas=None, labels=None):
    if colors is None:
        colors = ['blue', 'green', 'red', 'orange', 'purple', 'cyan']
    if alphas is None:
        alphas = [0.6] * len(list_of_points_lists)
    for points, color, alpha in zip(list_of_points_lists, colors, alphas):
        poly = Polygon(np.vstack([points, points[0]]), facecolor=color, edgecolor='black', alpha=alpha, label=labels[i] if labels and i < len(labels) else None)
        plt.gca().add_patch(poly)
    if labels:
        plt.legend()
    plt.axis('equal')
    plt.grid(True)

# === Data-driven loading (now matches uploaded filenames and exact JSON structure) ===
base_radius = 3.0

n_autopsy = 4
n_joiner = 4
n_collider = 7  # 7 tree branches in current collider

try:
    with open('1_idea_autopsy.json', 'r') as f:
        autopsy_data = json.load(f)['idea_autopsy']
        n_autopsy = len(autopsy_data['meta_axioms'])
    print(f"Loaded Autopsy procedure: {n_autopsy} meta-axioms")
except Exception as e:
    print(f"Could not load 1_idea_autopsy.json (using default {n_autopsy}): {e}")

try:
    with open('2_idea_joiner.json', 'r') as f:
        joiner_data = json.load(f)['idea_joiner']
        n_joiner = len(joiner_data['axiomatic_joining_function']['meta_axioms'])
    print(f"Loaded Joiner procedure: {n_joiner} meta-axioms")
except Exception as e:
    print(f"Could not load 2_idea_joiner.json (using default {n_joiner}): {e}")

try:
    with open('3_alignment_framework_collider.json', 'r') as f:
        collider_data = json.load(f)['alignment_framework_collider']
        n_collider = len(collider_data['system_structure']['tree_branches'])
    print(f"Loaded Collider procedure: {n_collider} judge branches")
except Exception as e:
    print(f"Could not load 3_alignment_framework_collider.json (using default {n_collider}): {e}")

# Geometric manifolds
autopsy_points = regular_polygon(n_autopsy, center=np.array([0.0, 0.0]), radius=base_radius)
collider_points = regular_polygon(n_collider, center=np.array([0.0, 0.0]), radius=base_radius)

# Phase 2: Autopsy proliferation — now driven by joiner dimensionality (4 branches at 90° steps)
proliferated = [autopsy_points]
for i in range(1, n_joiner + 1):
    angle = i * (360.0 / (n_joiner + 1))  # symmetric branching
    branch = rotate(autopsy_points, angle)
    proliferated.append(branch)

# Phase 3: Collider confrontation (adversarial reflection over diagonal)
line_point = np.array([0.0, 0.0])
line_dir = np.array([1.0, 1.0])
confronted_collider = reflect_over_line(collider_points, line_point, line_dir)

# Phase 4: Joiner synthesis — best rigid alignment of confronted collider onto core autopsy manifold
aligned_collider = best_rigid_alignment(confronted_collider, autopsy_points, allow_reflection=True)

# Quantitative geometric feedback (usable by collider for invariance scoring)
misalignment = average_min_distance(aligned_collider, autopsy_points)
geometric_convergence = np.exp(-misalignment / base_radius)  # 1.0 = perfect overlay, →0 with large residuals
print(f"\nGeometric misalignment (avg min distance): {misalignment:.4f}")
print(f"Analog convergence score (higher = more invariant): {geometric_convergence:.4f}")
if geometric_convergence < 0.995:
    print("→ Geometric veto triggered: residuals suggest dissolution or ledger entry.")

# Visualization
plt.figure(figsize=(16, 4))

plt.subplot(1, 4, 1)
plot_multiple_polygons([autopsy_points, collider_points], colors=['lightblue', 'lightcoral'], alphas=[0.8, 0.8])
plt.title("Phase 1: Separate Manifolds\n(Autopsy & Collider)")

plt.subplot(1, 4, 2)
plot_multiple_polygons(proliferated, colors=['lightblue']*(len(proliferated)), alphas=[0.8] + [0.3]*(len(proliferated)-1))
plt.title("Phase 2: Autopsy Proliferation\n(Joiner-driven branches)")

plt.subplot(1, 4, 3)
plot_multiple_polygons(proliferated + [confronted_collider], colors=['lightblue']*(len(proliferated)) + ['red'], alphas=[0.3]*(len(proliferated)) + [0.8])
plt.title("Phase 3: Collider Confrontation\n(Reflected adversarial)")

plt.subplot(1, 4, 4)
plot_multiple_polygons(proliferated + [aligned_collider], colors=['lightblue']*(len(proliferated)) + ['purple'], alphas=[0.3]*(len(proliferated)) + [0.9])
plt.title(f"Phase 4: Joiner Synthesis\n(Convergence: {geometric_convergence:.3f})")

plt.tight_layout()
plt.show()

print("\nSample aligned collider points:")
print(np.round(aligned_collider[:5], decimals=4))