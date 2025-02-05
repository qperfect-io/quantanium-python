
import numpy as np
from quantaniumpy.Quantanium import Quantanium
from mimiqcircuits import *


processor = Quantanium()

circuit = Circuit()
circuit.push(GateX(), range(1,5))
 
circuit.push(MeasureX(), 0,0)
circuit.push(MeasureY(), 1,1)
circuit.push(MeasureZ(), 2,1)
circuit.push(MeasureResetX(), 3,1)
circuit.push(MeasureResetY(), 0,1)
circuit.push(MeasureResetZ(), 1,1)
circuit.push(Reset(), 2)
r = processor.execute(circuit, nsamples=100)
print(r)


