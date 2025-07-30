import argparse
from quantanium.Quantanium import Quantanium


from mimiqcircuits import *
from mimiqcircuits import Circuit as MimiqCircuit
from mimiqlink import MimiqConnection as BaseMimiqConnection


def main():
    """
    Main function to demonstrate the usage of the evolve function from Quantanium class with MIMIQ API.

    """
    try:
        # Initialize the processor with local execution
        processor = Quantanium()
        mimiq_circuit = MimiqCircuit()
        mimiq_circuit.push(GateX(), 4)
        mimiq_circuit.push(Measure(), 4, 0)
        processor.evolve(mimiq_circuit)
        sv = processor.get_statevector()
        cv = processor.get_cstate()
        print(cv)

        mimiq_circuit2 = MimiqCircuit()
        mimiq_circuit2.push(GateH(), 0)  
        mimiq_circuit2.push(GateCX(), 0, range(2, 4))
        mimiq_circuit2.push(MeasureZZ(), 0, 1, 1)
        mimiq_circuit2.push(Measure(), 3, 2)

        processor.evolve(mimiq_circuit2)

        sv = processor.get_statevector()
        cv = processor.get_cstate()
        print(sv)
        print(cv)

    except Exception as e:
        # Catch and print any exceptions that occur
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
