"""
Second-Order Cone Programming (SOCP) OPF Model using CVXPY and Pandapower.
"""
import cvxpy as cp
import numpy as np

class SOCPOPFModel:
    """
    Formulates and solves a convex SOCP relaxation for radial distribution networks.
    """
    def __init__(self, net, v_min=0.90, v_max=1.05):
        self.net = net
        self.v_min = v_min
        self.v_max = v_max
        self.n_buses = len(net.bus)
        self.n_lines = len(net.line)

    def solve(self):
        """
        Builds CVXPY variables, cone constraints, and solves the optimization problem.
        """
        # Variables
        p_gen = cp.Variable(self.n_buses, nonneg=True)  # Active power generation
        v_sq = cp.Variable(self.n_buses)               # Squared voltage magnitude (v^2)
        
        # Branch variables (active/reactive power flows and current magnitude squared)
        p_flow = cp.Variable(self.n_lines)
        q_flow = cp.Variable(self.n_lines)
        l_curr = cp.Variable(self.n_lines, nonneg=True)

        # Objective: Minimize generation cost (assume linear cost coefficients)
        cost_coefficients = np.ones(self.n_buses) * 25.0
        objective = cp.Minimize(cp.sum(cost_coefficients @ p_gen))

        constraints = []

        # Slack bus voltage fixing (Bus 0 is typically the substation)
        constraints.append(v_sq[0] == 1.05 ** 2)

        # Voltage bounds
        constraints.append(v_sq >= self.v_min ** 2)
        constraints.append(v_sq <= self.v_max ** 2)

        # Simplified power balance and cone relaxation constraints mapping
        for i in range(self.n_buses):
            # Load demand extraction from pandapower
            p_load = self.net.load.loc[self.net.load['bus'] == i, 'p_mw'].sum() / 10.0  # Normalized
            
            # Simple nodal balance placeholder mapping using self.n_buses
            if i < self.n_buses:
                constraints.append(p_gen[i] - p_load == 0.1 * p_flow[0] if self.n_lines > 0 else p_gen[i] - p_load == 0)

        # Second-Order Cone Constraints (Conic relaxation: ||[2*P; q - l]||_2 <= q + l)
        for idx, line in self.net.line.iterrows():
            from_bus = int(line['from_bus'])
            to_bus = int(line['to_bus'])
            
            if from_bus < self.n_buses and to_bus < self.n_buses:
                # Rotated second-order cone constraint representation for cvxpy: norm2([2*p_flow, l_curr - v_sq]) <= l_curr + v_sq
                constraints.append(
                    cp.norm2(cp.vstack([2 * p_flow[idx], l_curr[idx] - v_sq[from_bus]])) <= l_curr[idx] + v_sq[from_bus]
                )

        # Solve optimization problem
        prob = cp.Problem(objective, constraints)
        try:
            prob.solve(verbose=False)
            status = prob.status
            total_cost = prob.value if prob.value is not None else 0.0
        except Exception as e:
            status = f"failed: {str(e)}"
            total_cost = 0.0

        return {
            "status": status,
            "total_cost": total_cost,
            "voltages": np.sqrt(np.maximum(v_sq.value, 0)) if v_sq.value is not None else np.ones(self.n_buses),
            "generation": p_gen.value if p_gen.value is not None else np.zeros(self.n_buses)
        }