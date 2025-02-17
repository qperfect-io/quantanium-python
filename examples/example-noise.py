from quantanium.Quantanium import Quantanium
from mimiqcircuits import *
from symengine import *

processor = Quantanium()

c = Circuit()
c.push(GateX(), range(0, 6))
c.push(AmplitudeDamping(0.9), 0)
c.push(Measure(), range(0, 6), range(0, 6))
r = processor.execute(c, nsamples=100)
print(r)

c = Circuit()
c.push(GateX(), range(0, 6))
c.push(GeneralizedAmplitudeDamping(0.5, 1), 2)
c.push(Measure(), range(0, 6), range(0, 6))
r = processor.execute(c, nsamples=100)
print(r)

c = Circuit()
c.push(GateX(), range(0, 6))
c.push(Kraus([Matrix([[1, 0], [0, sqrt(0.9)]]),
       Matrix([[0, sqrt(0.1)], [0, 0]])]), 4)
c.push(Measure(), range(0, 6), range(0, 6))
r = processor.execute(c, nsamples=100)
print(r)

print("ProjectiveNoise\n")
c = Circuit()
c.push(GateX(), range(0, 6))
c.push(ProjectiveNoise("Z"), 1)
c.push(Measure(), range(0, 6), range(0, 6))
r = processor.execute(c, nsamples=100)
print(r)

print("ProjectiveNoiseX\n")
c = Circuit()
c.push(GateX(), range(0, 6))
c.push(ProjectiveNoiseX(), 1)
c.push(Measure(), range(0, 6), range(0, 6))
r = processor.execute(c, nsamples=100)
print(r)

print("PauliX\n")
c = Circuit()
c.push(GateX(), range(0, 6))
c.push(PauliX(0.1), [1, 2, 3, 4, 5])
c.push(Measure(), range(0, 6), range(0, 6))
r = processor.execute(c, nsamples=100)
print(r)
# print("MIMIQ")
# job = conn.execute(c, nsamples=100)
# r = conn.get_result(job)
# print(r)


print("PauliY\n")
c = Circuit()
c.push(GateX(), range(0, 6))
c.push(PauliY(0.1), [1, 2, 3, 4, 5])
c.push(Measure(), range(0, 6), range(0, 6))
r = processor.execute(c, nsamples=100)
print(r)
# print("MIMIQ")
# job = conn.execute(c, nsamples=100)
# r = conn.get_result(job)
# print(r)


print("PauliZ\n")
c = Circuit()
c.push(GateX(), range(0, 6))
c.push(PauliZ(0.1), [1, 2, 3, 4, 5])
c.push(Measure(), range(0, 6), range(0, 6))
r = processor.execute(c, nsamples=100)
print(r)


print("PauliNoise\n")
c = Circuit()
c.push(GateX(), range(0, 6))
c.push(PauliNoise([0.8, 0.1, 0.1], ["II", "XX", "YX"]), 3, 1)
# c.push(PauliNoise([0.8, 0.1, 0.1], ["I", "X", "Y"]), 1)
c.push(Measure(), range(0, 6), range(0, 6))
r = processor.execute(c, nsamples=100)
print(r)

print("Mix Unitary\n")
c = Circuit()
c.push(GateX(), range(0, 6))
# c.push(MixedUnitary([0.7, 0.3], [Matrix(GateID().matrix()), Matrix(GateRX(0.2).matrix())]), 1)
c.push(MixedUnitary([0.9, 0.1], [
       Matrix([[1, 0], [0, 1]]), Matrix([[0, 1], [1, 0]])]), 0)
c.push(Measure(), range(0, 6), range(0, 6))
r = processor.execute(c, nsamples=100)
print(r)


print("Depolarizing1\n")
c = Circuit()
c.push(GateX(), range(0, 6))
c.push(Depolarizing1(0.5), [1, 2, 3, 4, 5])
c.push(Measure(), range(0, 6), range(0, 6))
r = processor.execute(c, nsamples=100)
print(r)


# print("Depolarizing2\n")
# c = Circuit()
# c.push(GateX(), range(0,6))
# c.push(Depolarizing2(0.1), 1, [2, 3, 4, 5])
# c.push(Measure(), range(0,6), range(0,6))
# r = processor.execute(c, nsamples=100)
# print(r)
