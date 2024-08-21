import argparse
from quantaniumpy.Quantanium import Quantanium


def main():
    parser = argparse.ArgumentParser(description="Process a QASM file with Quantanium.")
    parser.add_argument('qasm_file', type=str, help='The path to the QASM file')

    args = parser.parse_args()

    try:
        # Initialize the processor with local execution
        processor = Quantanium()
        # Convert QASM file to qua::Circuit
        qua_circuit = processor.convert_qasm_to_qua_circuit(args.qasm_file)
        # Execute the circuit
        results = processor.execute(qua_circuit, nsamples=100, seed=1)
        # print the obteined results
        print(results)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()

