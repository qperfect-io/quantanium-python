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
        # Convert qua::Circuit to mimiq::Circuit
        # mimiq_circuit = processor.convert_qua_to_mimiq_circuit(qua_circuit)
        # Convert mimiq::Circuit back to qua::Circuit
        #qua_circuit_converted_back = processor.convert_mimiq_to_qua_circuit(mimiq_circuit)
        # Execute the circuit
        if processor.use_remote:
            # Remote execution
            results = processor.execute(mimiq_circuit, nsamples=100, seed=1)
        else:
            # Local execution
            results = processor.execute(qua_circuit, nsamples=100, seed=1)
            #mimiq_results = processor.convert_qua_results_to_mimiq_results(qua_results)
            print(results)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()

