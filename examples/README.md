# Examples of `quantaniumpy` package  usage 

## `example_circuit.py` : basic functionality with MIMIQ API integration.

This example presents `main` function to demonstrate the usage of the Quantanium class from quantaniumpy package with MIMIQ API.
This function initializes the Quantanium processor in local mode, constructs a simple MimiqCircuit and then executes the circuit. 
The results of the execution are printed in the terminal.


**Steps:**
1. Initializes a `Quantanium` processor with local execution.
2. Creates a Mimiq circuit with Hadamard (H) and CNOT (CX) gates.
3. Executes the circuit locally with specified sampling and seed.
4. Prints the results of the execution.

Exception raises if any errors occur during the execution of the circuit or conversion processes.

Usage Example:
To run this script, use the following command in your terminal:

```bash
$ poetry run python examples/example_circuit.py 
```

This will initialize a Quantanium processor, create a simple quantum circuit with a Hadamard gate on 
qubit 0 and a CNOT gate on control qubit 0 and target qubits 2,3,4 and then execute this circuit.
The results will be printed to the console.


## `example_qasm.py` : basic example how to run circuit from the file in OpenQASm 2.0 format anf get results with MIMIQ API

This example process a circuit from QASM file using the Quantanium class of quantaniumpy package.

**Steps:**
1. Parses command-line arguments to get the path to the QASM file.
2. Initializes the Quantanium processor in local mode.
3. Converts the provided QASM file into a QUA (Quantanium) circuit.
4. Executes the circuit locally with a specified number of samples and a fixed seed.
5. Prints the results of the execution.

Args:
    qasm_file (str): The path to the QASM file provided via command-line arguments.

Exception raises if any errors occur during the QASM conversion or circuit execution.
    
Usage Example:
To run this script, use the following command in your terminal:
        
```bash
$ poetry run python examples/example_qasm.py path/to/your/qasm/your_circuit.qasm
```
This will process the QASM file and print the results of the circuit execution.
