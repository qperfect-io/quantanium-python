import argparse
from quantaniumpy.Quantanium import Quantanium
from mimiqcircuits import *
from mimiqcircuits import Circuit as MimiqCircuit
from mimiqlink import MimiqConnection as BaseMimiqConnection

def main():
    """
    Main function to demonstrate the usage of the Quantanium class with MIMIQ API.

    This function initializes the Quantanium processor in local mode, constructs a simple MimiqCircuit and then executes the circuit. The results of the execution
    are printed.

    Steps:
    1. Initializes a `Quantanium` processor with local execution.
    2. Creates a Mimiq circuit with Hadamard (H) and CNOT (CX) gates.
    3. Executes the circuit locally with specified sampling and seed.
    4. Prints the results of the execution.

    Raises:
        Exception: If any errors occur during the execution of the circuit or conversion processes.
    
    Usage Example:
        To run this script, use the following command in your terminal:

        ```bash
        poetry run python examples/example_circuit.py 
        ```

    This will initialize a Quantanium processor, create a simple quantum circuit with a Hadamard gate on 
    qubit 0 and a CNOT gate on control qubit 0 and target qubits 2,3,4 and then execute this circuit.
    The results will be printed to the console.
    
    """
    try:
        # Initialize the processor with local execution
        processor = Quantanium()
        
        # Create a Mimiq circuit and add gates
        mimiq_circuit = MimiqCircuit()
        mimiq_circuit.push(GateH(), 0)  # Apply Hadamard gate to qubit 0
        mimiq_circuit.push(GateCX(), 0, range(2, 4))  # Apply CNOT gate 
        
        # Print the constructed Mimiq circuit
        print(mimiq_circuit)
        
        # Execute the circuit locally with 100 samples and a fixed seed of 1
        results = processor.execute(mimiq_circuit, nsamples=100, seed=1)
        
        # Print the results of the execution
        print(results)
    except Exception as e:
        # Catch and print any exceptions that occur
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()


