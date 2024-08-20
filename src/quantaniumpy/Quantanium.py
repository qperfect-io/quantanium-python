import os
import ctypes
import time
import shutil
import json
import tempfile
import numpy as np
from quantaniumpy_core import *
from mimiqcircuits import Circuit as MimiqCircuit, QCSResults
from time import sleep
from mimiqlink import MimiqConnection as BaseMimiqConnection


class Quantanium:
    def __init__(self, use_remote=False, connection_url=None, email=None, password=None):
        """
        Initialize the Quantanium.

        Args:
            use_remote (bool): Flag to indicate if remote execution is used.
            connection_url (str): URL for the Mimiq server.
            email (str): Email for Mimiq server authentication.
            password (str): Password for Mimiq server authentication.
        """
        
        self.use_remote = use_remote
        self.connection = None
        if self.use_remote:
            self.connection = MimiqConnection(url=connection_url)
            self.connection.connectUser(email, password)

    def convert_qasm_to_qua_circuit(self, qasm_file: str) -> Circuit:
        """
        Convert a QASM file to a Circuit.

        Args:
            qasm_file (str): The path to the QASM file.

        Returns:
            Circuit: The converted Circuit.

        Raises:
            FileNotFoundError: If the QASM file does not exist.
            Exception: If there is an error loading the QASM file.
        """
        

        if not os.path.exists(qasm_file):
            raise FileNotFoundError(f"The file {qasm_file} does not exist.")
        try:
            qua_circuit = load_open_qasm(qasm_file)
        except Exception as e:
            raise Exception(f"Error loading QASM file: {e}")
        return qua_circuit


    def convert_mimiq_to_qua_circuit(self, mimiq_circuit: MimiqCircuit) -> Circuit:
        """
        Convert a mimiq::Circuit to a Circuit.

        Args:
            mimiq_circuit (MimiqCircuit): The mimiq::Circuit to convert.

        Returns:
            Circuit: The converted Circuit.

        Raises:
            Exception: If there is an error in the conversion process.
        """
        proto_file = "tmp.pb"
        try:
            mimiq_circuit.saveproto(proto_file)
            qua_circuit = ProtoParser().load_proto(proto_file)
        except Exception as e:
            raise Exception(f"Error converting mimiq::Circuit to Circuit: {e}")
       # finally:
       #     if os.path.exists(proto_file):
       #         os.remove(proto_file)
        return qua_circuit


    def convert_qua_to_mimiq_circuit(self, qua_circuit: Circuit) -> MimiqCircuit:
        """
        Convert a Circuit to a mimiq::Circuit.

        Args:
            qua_circuit (Circuit): The Circuit to convert.

        Returns:
            MimiqCircuit: The converted mimiq::Circuit.

        Raises:
            Exception: If there is an error in the conversion process.
        """
        proto_file = "tmp.pb"
        try:
            pp = ProtoParser()
            pp.save_proto(proto_file, qua_circuit)
            mimiq_circuit = MimiqCircuit()
            mimiq_circuit = mimiq_circuit.loadproto(proto_file)
        except Exception as e:
            raise Exception(f"Error converting Circuit to mimiq::Circuit: {e}")
        finally:
            if os.path.exists(proto_file):
                os.remove(proto_file)
        return mimiq_circuit


    def convert_qua_results_to_mimiq_results(self, qua_results: QCSResults) -> QCSResults:
        """
        Convert a QCSResults to a QCSResults.

        Args:
            qua_results (QCSResults): The QCSResults to convert.

        Returns:
            QCSResult: The converted QCSResult (Mimiq).

        Raises:
            Exception: If there is an error in the conversion process.
        """
        proto_file = "tmp_results.pb"
        try:
            pp = ProtoResult()
            pp.save_proto(proto_file, qua_results)
            mimiq_results = QCSResults()
            mimiq_results = mimiq_results.loadproto(proto_file)
        except Exception as e:
            raise Exception(f"Error converting QCSResults to QCSResult: {e}")
        finally:
            if os.path.exists(proto_file):
                os.remove(proto_file)
        
        return mimiq_results


    def execute(self, circuit, label="pyapi_v1.0", algorithm="auto", nsamples=1000, bitstrings=None, 
                timelimit=300, bonddim=None, entdim=None, seed=None, qasmincludes=None):
        """
        Execute the given circuit, either locally or via the Mimiq server.

        Args:
            circuit (Circuit): The circuit to be executed.
            label (str): The label for the execution.
            algorithm (str): The algorithm to be used for execution.
            nsamples (int): The number of samples to generate.
            bitstrings (list): List of bitstrings for conditional execution.
            timelimit (int): The time limit for execution in seconds.
            bonddim (int): The bond dimension for the MPS algorithm.
            entdim (int): The entangling dimension for the MPS algorithm.
            seed (int): The seed for generating random numbers.
            qasmincludes (list): List of OPENQASM files to include in the execution.

        Returns:
            QCSResults or QCSResult: The result of the execution.
        """
        if self.use_remote and isinstance(circuit, MimiqCircuit):
            execution_id = self.connection.execute(circuit, label, algorithm, nsamples, bitstrings, timelimit, bonddim, entdim, seed, qasmincludes)
            return self.connection.get_results(execution_id)
        else:
            if isinstance(circuit, MimiqCircuit):
                qua_circuit = self.convert_mimiq_to_qua_circuit(circuit)
            elif isinstance(circuit, Circuit):
                qua_circuit = circuit
            else:
                raise TypeError("circuit must be either a Circuit or mimiq::Circuit")
            try:
                if seed is None:
                    seed = int(time.time())
                qua_result = execute_double(qua_circuit, nsamples, seed)
                result = self.convert_qua_results_to_mimiq_results(qua_result)

            except Exception as e:
                raise Exception(f"Error executing the Circuit: {e}")
            return result


    def get_results(self, execution, interval=10):
        """
        Retrieve the results of a completed execution.

        Args:
            execution (str): The execution identifier.
            interval (int): The interval (in seconds) for checking job status.

        Returns:
            QCSResults: An instance of the QCSResults class.
        """
        if self.use_remote:
            return self.connection.get_results(execution, interval)
        else:
            raise RuntimeError("get_results is only available for remote execution.")


# Example usage:
if __name__ == "__main__":
    try:
        # Initialize the processor with local execution
        processor = Quantanium()

        # Convert QASM file to Circuit
        qua_circuit = processor.convert_qasm_to_qua_circuit("pea_3_pi_8.qasm")

        # Convert Circuit to mimiq::Circuit
        mimiq_circuit = processor.convert_qua_to_mimiq_circuit(qua_circuit)

        # Convert mimiq::Circuit back to Circuit
        #qua_circuit_converted_back = processor.convert_mimiq_to_qua_circuit(mimiq_circuit)

        # Execute the circuit
        if processor.use_remote:
            # Remote execution
            results = processor.execute(mimiq_circuit, nsamples=100, seed=1)
        else:
            # Local execution
            results = processor.execute(qua_circuit, nsamples=100)# seed=1)
            #results.print_result() # printout Qua QCSResult
            #mimiq_results = processor.convert_qua_results_to_mimiq_results(qua_results)
            print(results)        # printout Mimiq QCSResults
    except Exception as e:
        print(f"An error occurred: {e}")

