import argparse
from quantanium.Quantanium import Quantanium


from mimiqcircuits import *
from mimiqcircuits import Circuit as MimiqCircuit


def main():
    """
    Main function to demonstrate the usage of the Hamiltonian with MIMIQ API.

    """

    try:
        c = Circuit()
        c.push(GateX(), range(2))
        h = Hamiltonian()
        h.push(1.0, PauliString("ZZ"), 0, 1)
        c.push_expval(h, 1, 2)
        print(c)

        processor = Quantanium()
        results = processor.execute(c, nsamples=100, seed=1)
  
        
       
    
        print(results)

    except Exception as e:
        # Catch and print any exceptions that occur
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    main()
