from quantaniumpy.Quantanium import Quantanium
from mimiqcircuits import *

processor = Quantanium()


n = 10
c = Circuit()
c.push(GateH(), range(n))
c.push(GateCZ(), range(n-1), range(1,n))
c.push(GateCZ(), 0, n-1)

#c.push(Measure(), range(1,5),range(1,5))
c.push(Amplitude(BitString.fromint(n, 0)), 0)
c.push(Amplitude(BitString.fromint(n, 2**int(n/2))),1)
c.push(Amplitude(BitString.fromint(n ,n)), 2)
c.push(Amplitude(BitString.fromint(n, 2**n - 1)), 3)
r = processor.execute(c, nsamples=1000, bitstrings = [BitString.fromint(10, 2**10-1), BitString.fromint(10, 10), BitString.fromint(10,0)])
print(r)

print(r.amplitudes)
