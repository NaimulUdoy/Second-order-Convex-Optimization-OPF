"""
Configuration parameters for Conic SOCP-OPF using pandapower.
"""
import pandapower.networks as pn

def get_test_network():
    """
    Loads the IEEE 33-bus radial distribution test network from pandapower.
    """
    net = pn.case33bw()
    return net

# Optimization hyperparameters
VOLTAGE_MIN = 0.90  # Minimum allowable voltage magnitude (p.u.)
VOLTAGE_MAX = 1.05  # Maximum allowable voltage magnitude (p.u.)
BASE_MVA = 10.0     # System base MVA