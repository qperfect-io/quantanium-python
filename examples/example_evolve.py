import argparse
from quantanium.Quantanium import Quantanium


from mimiqcircuits import *
from mimiqcircuits import Circuit as MimiqCircuit
from mimiqlink import MimiqConnection as BaseMimiqConnection

def add_or_increment(d, element):
    if element in d:
        d[element] += 1
    else:
        d[element] = 1


def main():
    """
    Main function to demonstrate the usage of the evolve function from Quantanium class with MIMIQ API.
    """
    
    try:
        print("First example: Expected result 50% - 011 50% - 000")
        histogram = {}
        # Expected result 50% - 011 50% - 000
        processor = Quantanium()
        for i in range(1000): 
            processor.zerostate()
            mimiq_circuit = MimiqCircuit()
            mimiq_circuit.push(GateX(), 4)
            mimiq_circuit.push(Measure(), 4, 2)
            processor.evolve(mimiq_circuit)

            mimiq_circuit2 = MimiqCircuit()
            mimiq_circuit2.push(GateH(), 0)  
            mimiq_circuit2.push(GateCX(), 0, range(2, 3))
            mimiq_circuit2.push(MeasureZZ(), 0, 1, 1)
            mimiq_circuit2.push(Measure(), 0, 2)
            processor.evolve(mimiq_circuit2)

            sv = processor.get_statevector()
            cv = processor.get_cstate()   
            add_or_increment(histogram, str(cv[0])) 
        print("\n=== Histogram ===")
        for state, count in sorted(histogram.items()):
            print(f"{state}: {count}")

        print("\nSecond example: Expected result 50% - 100 50% - 111")
        histogram = {}
        # Expected result 50% - 100 50% - 111
        processor = Quantanium()
        for i in range(1000):
            processor.zerostate()
            mimiq_circuit = MimiqCircuit()
            mimiq_circuit.push(GateX(), 4)
            mimiq_circuit.push(Measure(), 4, 0)
            processor.evolve(mimiq_circuit)
     
    
            mimiq_circuit2 = MimiqCircuit()
            mimiq_circuit2.push(GateH(), 0)  
            mimiq_circuit2.push(GateCX(), 0, range(2, 4))
            mimiq_circuit2.push(MeasureZZ(), 0, 1, 1)
            mimiq_circuit2.push(Measure(), 3, 2)
 
            processor.evolve(mimiq_circuit2)

            sv = processor.get_statevector()
            cv = processor.get_cstate()
           
            add_or_increment(histogram, str(cv[0])) 
        print("\n=== Histogram ===")
        for state, count in sorted(histogram.items()):
            print(f"{state}: {count}")
            

    except Exception as e:
        # Catch and print any exceptions that occur
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
