import pandas as pd
import re
import numpy as np
from scipy.integrate import odeint
from scipy.optimize import fsolve
import networkx as nx

class NodesHandler:
    """
    Enhanced stateful handler for nodes.csv and optional edges_part1.csv in multidimensional DNA analysis.
    Upgraded for edges integration (PPI networks), AD interactome extraction, degree-scaled ODE params,
    and 2025 CASP8/polyGR hardening. Advances predictive prototyping by fusing graph metrics with dynamics
    for * factors (e.g., hub degree as mu boosters) and DNA markers (e.g., connectivity-scaled v_s).
    
    Attributes:
        nodes_df (pd.DataFrame): Cached nodes.csv.
        edges_df (pd.DataFrame | None): Cached edges_part1.csv (optional).
        G (nx.Graph | None): Undirected PPI graph (built on demand).
    
    Lineage: Neuresthetic Ethics Eternal – DNA Ontology Hardening
    Evaluation: 2025-12-21 (Edges-integrated for network invariance)
    """
    
    def __init__(self, nodes_path: str, edges_path: str | None = None):
        """
        Initializes with nodes.csv; optionally loads edges_part1.csv for graph analysis.
        
        Args:
            nodes_path (str): Path to nodes.csv.
            edges_path (str | None): Path to edges_part1.csv (optional for PPI networks).
        
        Raises:
            FileNotFoundError: If files not found.
            ValueError: If structures invalid.
        """
        try:
            self.nodes_df = pd.read_csv(nodes_path, dtype=str)
            expected_node_cols = ['node_index', 'node_id', 'node_type', 'node_name', 'node_source']
            if not all(col in self.nodes_df.columns for col in expected_node_cols):
                raise ValueError("Invalid nodes.csv structure.")
            
            self.edges_df = None
            self.G = None
            if edges_path:
                self.edges_df = pd.read_csv(edges_path, dtype=str)
                expected_edge_cols = ['source', 'target', 'interaction_type']  # Adjust as per actual
                if not all(col in self.edges_df.columns for col in expected_edge_cols):
                    raise ValueError("Invalid edges_part1.csv structure.")
                self._build_graph()
        except FileNotFoundError as e:
            raise FileNotFoundError(f"File not found: {e.filename}")
        except Exception as e:
            raise ValueError(f"Initialization failed: {str(e)}")
    
    def _build_graph(self) -> None:
        """Builds undirected PPI graph from edges_df."""
        self.G = nx.Graph()
        for _, row in self.edges_df.iterrows():
            self.G.add_edge(row['source'], row['target'], type=row.get('interaction_type', 'PPI'))
        # Add node attributes from nodes_df
        node_attrs = self.nodes_df.set_index('node_id').to_dict('index')
        nx.set_node_attributes(self.G, node_attrs)
    
    def summary_stats(self) -> Dict[str, Any]:
        """Computes basic stats on nodes/edges."""
        stats = {
            'num_nodes': len(self.nodes_df),
            'node_types': self.nodes_df['node_type'].value_counts().to_dict()
        }
        if self.G:
            stats.update({
                'num_edges': self.G.number_of_edges(),
                'average_degree': np.mean([d for n, d in self.G.degree()])
            })
        return stats
    
    def get_ad_interactome(self) -> pd.DataFrame:
        """Extracts AD-related subnetwork (e.g., APP/APOE interactions)."""
        if not self.G:
            raise ValueError("Edges not loaded; cannot extract interactome.")
        ad_genes = ['APP', 'APOE', 'PSEN1']  # Extend as needed
        subgraph = self.G.subgraph([n for n in self.G if n in ad_genes or 'AD' in self.G.nodes[n].get('node_source', '')])
        return nx.to_pandas_edgelist(subgraph)
    
    def get_polygenic_cluster(self, seed_genes: List[str]) -> pd.DataFrame:
        """Clusters around polygenic seeds (e.g., MYC/APP/APOE)."""
        if not self.G:
            raise ValueError("Edges not loaded; cannot cluster.")
        cluster_nodes = set(seed_genes)
        for gene in seed_genes:
            if gene in self.G:
                cluster_nodes.update(self.G.neighbors(gene))
        return self.nodes_df[self.nodes_df['node_id'].isin(cluster_nodes)]
    
    def estimate_ode_params(self, cluster_df: pd.DataFrame) -> Dict[str, float]:
        """Estimates ODE params scaled by graph metrics."""
        if self.G:
            subgraph = self.G.subgraph(cluster_df['node_id'])
            degrees = dict(subgraph.degree())
            avg_degree = np.mean(list(degrees.values())) if degrees else 1.0
            hub_boost = np.log1p(avg_degree)  # Scales mu/v_s
        else:
            hub_boost = 1.0
        
        return {
            'kappa': 0.9,  # Default high reciprocity
            'lam': 0.4,    # Dissolution rate
            'v_s': 0.3 * hub_boost,  # Scaled violence/speciation
            'mu': 0.1 * hub_boost    # Mutation/drift booster
        }
    
    def simulate_dna_dynamics(self, cluster_df: pd.DataFrame, t_span: np.ndarray, y0: List[float] = [0.1, 1.0, 0.8]) -> np.ndarray:
        """Simulates multidimensional DNA ODEs with cluster-scaled params."""
        params = self.estimate_ode_params(cluster_df)
        
        def dna_dynamics(y, t, kappa, lam, v_s, mu):
            rho, P, epi = y
            drho = v_s * (1 - kappa) * (1 - rho) * epi - lam * rho + mu * rho * (1 - rho)
            dP = P * (1 - rho) * kappa * lam - v_s * rho * P * epi
            depi = lam * (1 - epi) - mu * epi * rho
            return [drho, dP, depi]
        
        sol = odeint(dna_dynamics, y0, t_span, args=(params['kappa'], params['lam'], params['v_s'], params['mu']))
        print(f"Simulated for {len(cluster_df)} nodes; final ρ: {sol[-1, 0]:.3f}.")
        return sol
    
    def find_fixed_point(self, cluster_df: pd.DataFrame) -> tuple:
        """Solves fixed point with cluster params."""
        params = self.estimate_ode_params(cluster_df)
        
        def eqs(vars, kappa, lam, v_s, mu):
            rho, epi = vars
            return [
                v_s * (1 - kappa) * (1 - rho) * epi - lam * rho + mu * rho * (1 - rho),
                lam * (1 - epi) - mu * epi * rho
            ]
        
        fixed_point = fsolve(eqs, [0.1, 0.8], args=(params['kappa'], params['lam'], params['v_s'], params['mu']))
        print(f"Fixed point for {len(cluster_df)} nodes: ρ≈{fixed_point[0]:.3f}, epi≈{fixed_point[1]:.3f}.")
        return tuple(fixed_point)

# Example REPL (uncomment):
# handler = NodesHandler('nodes.csv', 'edges_part1.csv')
# handler.summary_stats()
# ad_interactome = handler.get_ad_interactome()
# print(ad_interactome.head())
# cluster = handler.get_polygenic_cluster(['MYC', 'APP', 'APOE'])
# params = handler.estimate_ode_params(cluster)
# t_span = np.linspace(0, 50, 500)
# sol = handler.simulate_dna_dynamics(cluster, t_span)
# fixed = handler.find_fixed_point(cluster)