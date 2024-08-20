# Example of Quantaniumpy usage (`example.py`)

## Script Description

The script performs the following steps:

- Initializes the Quantanium.
- Converts the provided QASM file to a qua::Circuit.
- Converts the qua::Circuit to a mimiq::Circuit.
- Optionally converts the mimiq::Circuit back to a qua::Circuit.
- Executes the circuit:
    - If remote execution is enabled, it runs the mimiq::Circuit remotely.
    - If remote execution is disabled, it runs the qua::Circuit locally and converts the results to mimiq::Results.

### Running Example

```sh
$ python example.py path/to/your/qasm_file.qasm
```

## Error Handling

If an error occurs during the process, the script will print an error message with details.

