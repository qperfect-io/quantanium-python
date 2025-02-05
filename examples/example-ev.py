from quantaniumpy.Quantanium import Quantanium
from mimiqcircuits import *
processor = Quantanium()
c = Circuit()
c.push(GateX(), range(1,5))
c.push(ExpectationValue(GateU3(3.14,1,1)), range(1,3), range(1,3))
c.push(Measure(), range(1,5), range(1,5))
r = processor.execute(c, nsamples=100, seed=1)
print(r)

c = Circuit()
c.push(GateX(), range(1,5))
c.push(ExpectationValue(control(1, GateU(3.14/2,1,1))), range(0,3), range(1,4), range(0,3))
c.push(Measure(), range(1,5), range(1,5))
r = processor.execute(c, nsamples=100, seed=1)
print(r)

c = Circuit()
c.push(GateX(), range(1,5))
c.push(ExpectationValue(PauliString("XYZI")), 0, 1, 2, 3, range(1,4))
c.push(Measure(), range(1,5), range(1,5))
r = processor.execute(c, nsamples=100)
print(r)

c = Circuit()
c.push(GateX(), range(1,5))
c.push(ExpectationValue(Projector1()), 0, 4)
c.push(Measure(), range(1,5), range(1,5))
r = processor.execute(c, nsamples=100, seed=1)
print(r)

c = Circuit()
c.push(GateX(), range(1,5))
c.push(ExpectationValue(Projector11()), 0, 4, 0)
c.push(Measure(), range(1,5), range(1,5))
r = processor.execute(c, nsamples=100, seed=1)
print(r)

