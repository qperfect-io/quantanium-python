from quantanium.Quantanium import Quantanium
from mimiqcircuits import *
from symengine import *
import numpy as np


def main():
    # Initialize the processor with local execution
    processor = Quantanium()

    g = GateCustom(np.matrix([[0.0, 1.0], [1.0, 0.0]]))
    circ = Circuit()
    circ.push(g, 4)
    results = processor.execute(circ, nsamples=100, seed=1)
    sv = processor.get_statevector()
    # Print the results of the execution
    print(results)
    print(sv)


if __name__ == "__main__":
    main()
