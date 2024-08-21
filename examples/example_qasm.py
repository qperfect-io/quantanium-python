import argparse
from quantaniumpy.Quantanium import Quantanium

def main():
    """
    Main function to process a circuit from QASM file using the Quantanium class of quantaniumpy package.

    This function performs the following steps:
    1. Parses command-line arguments to get the path to the QASM file.
    2. Initializes the Quantanium processor in local mode.
    3. Converts the provided QASM file into a QUA circuit.
    4. Executes the circuit locally with a specified number of samples and a fixed seed.
    5. Prints the results of the execution.

    Args:
        qasm_file (str): The path to the QASM file provided via command-line arguments.

    Raises:
        Exception: If any errors occur during the QASM conversion or circuit execution.
    
    Usage Example:
        To run this script, use the following command in your terminal:
        
        ```bash
        $ poetry run python examples/example_qasm.py path/to/your/qasm/your_circuit.qasm
        ```

        
        This will process the QASM file and print the results of the circuit execution.
    """
    parser = argparse.ArgumentParser(description="Process a QASM file with Quantanium.")
    parser.add_argument('qasm_file', type=str, help='The path to the QASM file')

    args = parser.parse_args()

    try:
        # Initialize the processor with local execution
        processor = Quantanium()
        
        # Convert QASM file to QUA circuit
        qua_circuit = processor.convert_qasm_to_qua_circuit(args.qasm_file)
        
        # Execute the circuit locally with 100 samples and a fixed seed of 1
        results = processor.execute(qua_circuit, nsamples=100, seed=1)
        
        # Print the obtained results
        print(results)
    except Exception as e:
        # Catch and print any exceptions that occur
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()


