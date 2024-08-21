import argparse
from quantaniumpy.Quantanium import Quantanium
from mimiqcircuits import *
from mimiqcircuits import Circuit as MimiqCircuit
from mimiqlink import MimiqConnection as BaseMimiqConnection


def main():

    try:
        # Initialize the processor with local execution
        processor = Quantanium()
        mimiq_circuit = MimiqCircuit()
        mimiq_circuit.push(GateH(),0)
        mimiq_circuit.push(GateCX(), 0, range(2,4))
        print(mimiq_circuit)
        qua_circuit = processor.convert_mimiq_to_qua_circuit(mimiq_circuit)
        results = processor.execute(mimiq_circuit, nsamples=100, seed=1)
        print(results)
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()

