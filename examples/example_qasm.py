import argparse
from quantanium.Quantanium import Quantanium


def main():
    # Initialize the processor with local execution
    processor = Quantanium()

    qasm_file_path = "examples/test.qasm"
    mimiq_circuit = processor.parse_qasm(qasm_file_path)

    # Print the constructed Mimiq circuit
    print(mimiq_circuit)

    # Execute the circuit locally with 100 samples and a fixed seed of 1
    results = processor.execute(mimiq_circuit, nsamples=100, seed=1)

    # Print the results of the execution
    print(results)


if __name__ == "__main__":
    main()
