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

### Installation Quantanium-python from Binary
Installation Steps: 

create a new python environment:
```
python -m venv .quantanium_venv
```

activate your environment:
```
source .quantanium_venv/bin/acitvate
```

Download the latest release here: https://github.com/qperfect-io/quantanium-python/releases/latest

Extract the content of the zip file using 

To install the wheel make sure to select the correct file for your system.
- the number after cp[NUM] in the name of the whl file must match your python version
- If you are using macos take the file with macos included in the name, otherwise take the file with manylinux. (not built for windows yet)

For example to install the wheels on ubuntu for python 3.12 run:
```
pip install  quantaniumpy-0.1.0-cp312-cp312-manylinux_2_17_x86_64.manylinux2014_x86_64.whl
```

---
### Troubleshooting
- If installation fails, check that you have the correct Python version (`python --version`).
- Ensure all dependencies are installed.
- In some cases you should consider upgrading via the 'pip install --upgrade pip' command.


### Installation from Source

You can also build and install quantanium-python from source. Note, in this way, a g++ or clang++ compiler is necessary: make sure that the compiler installed.

In order to install quantanium-python from source, please follow the next set of instructions:

1. Clone this repository with

```sh
$ git clone git@github.com:qperfect-io/quantanium-python-private.git
$ cd quantanium-python-private
```

2. Initialize all the dependencies of the project by typing the following instructions in the command line of your `shell` terminal:

```sh
$ git submodule init && git submodule update
```

```sh
$ cd libs/quantanium
```

```sh
$ git submodule init && git submodule update
```

```sh
$ cd ../../
```


3. Setup the build directory and build C++ code with python wrapper support by the following instructions in the command line of your `shell` terminal:

```sh
$ mkdir release-python

$ cd release-python

$ cmake ../

$ make 
```


4. install the Python Package 

Start by creating virtual environment (if not done yet)

```sh
python -m venv .venv 
```
Activate the environment by invoking the activation command:
```sh
source .venvs/bin/activate
```
Install quantanium-python locally:

```sh
pip install -e .
```

## Accessible Functions

All accessible functions are defined within the Quantanium class inside Quantanium.py. These include:
- convert_qasm_to_qua_circuit(qasm_file): Converts a QASM file to a qua::Circuit.
- convert_qua_to_mimiq_circuit(qua_circuit): Converts a qua::Circuit to a mimiq::Circuit.
- convert_mimiq_to_qua_circuit(mimiq_circuit): Converts a mimiq::Circuit back to a qua::Circuit.
- convert_qua_results_to_mimiq_results(qua_results): Converts qua::Results to mimiq::Results.
- execute(circuit, label="pyapi_v1.0", algorithm="auto", nsamples=1000, bitstrings=None, timelimit=300, bonddim=None, entdim=None, seed=None, qasmincludes=None): Executes the given circuit.

## Quick Start
In order to start, you can use an example script from folder  `examples`, e.g.:

```sh
$ python examples/example_qasm.py
```

