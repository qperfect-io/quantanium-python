# Quantanium-python

*Python Wrapper for the MIMIQ Quantanium statevector engine.*

## Prerequisites

Before installing, ensure you have:
- **Python** (version 3.10, 3.11, or 3.12)
- **Git** installed on your system
- **Virtual environment support** (e.g., `venv`)

## Installation

Quantanium is implemented in C++, with a wrapper written in the Python programming language to enhance usability and ensure support with MIMIQ API.
For the released versions of Quantanium, we provide binaries via our Git repository, specifically for the Linux platform, which only require a functional Python environment to install.
You can do this very easily following the instructions from the next subsection.

### Installation Quantanium-python
To install quantanium run the following:
```
pip install quantanium
```

**!Quantanium only supports Linux and MacOS (x86_64 only) for a version of python >= 3.9**


---
### Troubleshooting
- If installation fails, check that you have the correct Python version (`python --version`).
- In some cases you should consider upgrading via the 'pip install --upgrade pip' command.

## Quick Start
In order to start, you can use an example script from folder  `examples`:
Otherise here is a simple example on how to run a circuit:
```python
from quantanium import Quantanium
from mimiqcircuits import *

# Instantiate StateVector simulator
sim = Quantanium()

# build circuit
c = Circuit()
c.push(GateH(), 0)

# execute the circuit
sim.execute(c)

# Parse and create circuit from OpenQASM2
qasm_file_path = "path/to/qasm2"
mimiq_circuit = processor.parse_qasm(qasm_file_path)

# execute circuit
sim.execute(mimiq_circuit)
```