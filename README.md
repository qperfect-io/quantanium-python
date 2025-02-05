# QuantaniumPY

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

### Installation Quantaniumpy from Binary
Installation Steps: 

1. Clone the Quantaniumpy Repository
Clone the repository from the `feat-mcb012` branch:
```sh
 git clone -b feat-mcb012 git@github.com:qperfect-io/quantaniumpy.git
```

2. Create a Python Virtual Environment
```sh
 python -m venv quant
```

3. Activate the Virtual Environment
On **Linux**:
```sh
 source quant/bin/activate
```
4. Navigate to the Quantaniumpy Directory
```sh
 cd quantaniumpy
```

5. Create a Distribution Folder
```sh
 mkdir dist
```

6. Download the Artifact
- Go to the **Actions** page of Quantaniumpy's GitHub repository.
- Select the latest successful action.
- Download the artifact **cibw-wheels-ubuntu-latest**.
- Example link (replace with the latest action ID):  
   [Download Artifact](https://github.com/qperfect-io/quantaniumpy/actions/runs/12802623816)

7. Unzip the Artifact
```sh
 unzip cibw-wheels-ubuntu-latest.zip
```
This will extract multiple `.whl` files corresponding to different Python versions (10, 11 and 12).

8. Select the Correct Wheel File
Identify and copy the appropriate `.whl` file for your Python version. Example for **Python 3.10**:
```sh
 cp quantaniumpy-0.1.0-cp310-cp310-man~17_x86_64.manylinux2014_x86_64.whl path/to/quantaniumpy/dist/
```

9. Install the Python Package
Navigate to the `quantnaiumpy` folder and install the package using `pip`:
```sh
pip install dist/quantaniumpy-0.1.0-cp310-cp310-manylinux_2_17_x86_64.manylinux2014_x86_64.whl 

```

10. Verify the Installation
Run an example script to confirm everything is working:
```sh
 python examples/example_qasm.py
```

Quantaniumpy is now installed and ready for use.
More examples in folder 'quantaniumpy/examples'.
This package support MimiqCircuit python api.

---
### Troubleshooting
- If installation fails, check that you have the correct Python version (`python --version`).
- Ensure all dependencies are installed.
- In some cases you should consider upgrading via the 'pip install --upgrade pip' command.


### Installation from Source

You can also build and install Quantaniumpy from source. Note, in this way, a g++ or clang++ compiler is necessary: make sure that the compiler installed.

In order to install quantaniumpy from source, please follow the next set of instructions:

1. Clone this repository with

```sh
$ git git@git.unistra.fr:code-quantum/quantanium.git
$ cd quantanium
```

2. Initialize all the dependencies of the project by typing the following instruction in the command line of your `shell` terminal:

```sh
$ git submodule init && git submodule update
```

3. Setup the build directory and build C++ code with python wrapper support by the following instructions in the command line of your `shell` terminal:

```sh
$ mkdir release-python

$ cd release-python

$ cmake -DCMAKE_BUILD_TYPE=Release -DBUILD_SHARED_LIBS=On -DQUANTANIUM_WITH_PYTHON=On ../

$ cmake --build . -j 4
```

4. Since C++ source code is built, you have to prepare your library environement. 
   In order to do this, please, navigate to root folder of the project `quantanium` and make the following set of commands: 
```sh
$ cd ..
$ mkdir python/quantaniumpy/lib
$ cp release-python/lib/quantaniumpy.cpython-310-x86_64-linux-gnu.so python/quantaniumpy/lib
$ export PYTHONPATH=$PYTHONPATH:../../release-python/lib

```
- You may need to export path to `spdlog` library:
```sh
export LD_LIBRARY_PATH=../../release-python/libs/spdlog
```

5. Building the Python Package with Poetry

- Navigate to the directory of the python project (supposing you are still in the root folder of the project `quantanium`):

```sh
cd python/
```

- Set up Python virtual development environment

Virtual environments are used for development to isolate the development environment from system-wide packages.
This way helps to avoid inadvertently becoming dependent on a particular system configuration and makes it easy to maintain multiple environments: e.g. for older versions of Quantanium.
Start by creating a new virtual environment with `venv`:

```sh
python -m venv ~/.venvs/quapy 
```
Activate the environment by invoking the activation command:
```sh
source ~/.venvs/quapy/bin/activate
```

- Ensure you have Poetry installed. If you don't have it installed, you can install it using the following command:

```sh
python -m pip install poetry
```

- Build the package using Poetry:
```sh
poetry build
```

6. Install the package, use pip to install the wheel file generated by Poetry:

```sh
pip install dist/quantaniumpy-0.1.0-py3-none-any.whl
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

