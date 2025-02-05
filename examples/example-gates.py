
import numpy as np
from quantaniumpy.Quantanium import Quantanium
from mimiqcircuits import *
processor = Quantanium()

circuit = Circuit()
 
# Add various gates
circuit.push(GateH(), 0)
circuit.push(GateX(), 1)
circuit.push(GateY(), 2)
circuit.push(GateZ(), 3)
circuit.push(GateCX(), 0, 1)
circuit.push(GateCZ(), 2, 3)
circuit.push(GateSWAP(), 0, 2)
circuit.push(GateRX(np.pi / 4), 1)
circuit.push(GateRY(np.pi / 4), 2)
circuit.push(GateRZ(np.pi / 4), 3)
circuit.push(GateU(0.5, 0.3, 0.1), 0)

# Add parametric gates
circuit.push(Control(1, GateX()), 0, 1)
circuit.push(Power(GateR(np.pi / 4, np.pi / 8), 0.5), 2)
circuit.push(Inverse(GateR(np.pi / 4, np.pi / 8)), 3)

# Add a custom unitary gate
custom_matrix = np.array([[0, 1], [1, 0]], dtype=np.complex128)
circuit.push(GateCustom(custom_matrix), 0)

# Pauli String
circuit.push(PauliString("XYZI"), 0, 1, 2, 3)

r = processor.execute(circuit, nsamples=100)
print(r)


