"""
Main execution script for Conic SOCP-OPF Analysis using Pandapower.
"""
import numpy as np
import matplotlib.pyplot as plt
from config import get_test_network, VOLTAGE_MIN, VOLTAGE_MAX
from models.socp_model import SOCPOPFModel

def main():
    print("=== Initializing Pandapower Large System Conic SOCP-OPF ===")
    
    # Load IEEE 33-Bus Test Network
    net = get_test_network()
    print(f"Loaded Network: {net.name} ({len(net.bus)} Buses, {len(net.line)} Lines)")

    # Initialize SOCP OPF Model
    socp_solver = SOCPOPFModel(net, v_min=VOLTAGE_MIN, v_max=VOLTAGE_MAX)
    
    print("\nSolving Convex Second-Order Cone Program...")
    results = socp_solver.solve()

    print(f"\nOptimization Status: {results['status']}")
    print(f"Total Generation Cost: ${results['total_cost']:.2f}")

    print("\nGenerating Bus Voltage Profile Visualization...")
    
    # Plotting voltage profiles across buses
    buses = np.arange(len(results['voltages']))
    voltages = results['voltages']

    plt.figure(figsize=(10, 4))
    plt.plot(buses, voltages, marker='o', color='purple', linestyle='-', label='SOCP Voltage Profile')
    plt.axhline(VOLTAGE_MIN, color='r', linestyle='--', label='Min Voltage Limit')
    plt.axhline(VOLTAGE_MAX, color='g', linestyle='--', label='Max Voltage Limit')
    plt.xlabel('Bus Index')
    plt.ylabel('Voltage Magnitude (p.u.)')
    plt.title('IEEE 33-Bus Conic SOCP-OPF Voltage Profile')
    plt.grid(True, linestyle=':', alpha=0.7)
    plt.legend(loc='lower left')
    plt.tight_layout()

    # Save figure to project directory
    output_filename = "socp_opf_voltage_profile.png"
    plt.savefig(output_filename, dpi=300, bbox_inches='tight')
    print(f"Voltage profile plot successfully saved as '{output_filename}' in your project directory.")

    plt.show()
    print("\nConic programming pipeline finished successfully!")

if __name__ == "__main__":
    main()