#
# Copyright © 2023-2024, QPerfect. All rights reserved.
# Unauthorized copying of this file, via any medium is strictly prohibited.
# Proprietary and confidential.
#
import os
import time
import tempfile
import platform

if platform.system() == "Windows":
    package_dir = os.path.dirname(__file__)  
    dll_dir = os.path.abspath(
        os.path.join(package_dir, os.pardir, "quantanium.libs")
    )
    if not os.path.isdir(dll_dir):
        raise FileNotFoundError(f"quantanium.libs not found at {dll_dir!r}")
    os.add_dll_directory(dll_dir)
from ._core import (
    Circuit,
    ProtoParser,
    ProtoResult,
    StateVectorF64,
    BitVector,
    execute_double,
    evolve,
    evolve_next,
    load_open_qasm,
)
from ._core import QCSResults as QuantaniumQCSResults
from ._core import BitVector as QuantaniumBitVector
from mimiqcircuits.lazy import LazyExpr, LazyArg
from mimiqcircuits import Circuit as MimiqCircuit, QCSResults
import mimiqcircuits as mc

QUANTANIUM_SUPPORTED_OPERATIONS = {
    mc.GateID,
    mc.GateH,
    mc.GateX,
    mc.GateY,
    mc.GateZ,
    mc.GateT,
    mc.GateTDG,
    mc.GateS,
    mc.GateSDG,
    mc.GateP,
    mc.GateRX,
    mc.GateRY,
    mc.GateRZ,
    mc.GateU1,
    mc.GateU2,
    mc.GateU3,
    mc.GateU,
    mc.GateSX,
    mc.GateCSX,
    mc.GateSWAP,
    mc.GateXXplusYY,
    mc.GateCX,
    mc.GateCY,
    mc.GateCZ,
    mc.GateCP,
    mc.GateCS,
    mc.GateCH,
    mc.GateCU,
    mc.GateCRX,
    mc.GateCRY,
    mc.GateCRZ,
    mc.GateRNZ,
    mc.Barrier,
    mc.Block,
    mc.Repeat,
    mc.Measure,
    mc.Reset,
    mc.IfStatement,
    mc.PauliString,
    mc.RPauli,
    mc.Amplitude,
    mc.PauliNoise,
    mc.PauliX,
    mc.PauliY,
    mc.PauliZ,
    mc.ProjectiveNoiseX,
    mc.ProjectiveNoiseY,
    mc.ProjectiveNoiseZ,
    mc.PhaseAmplitudeDamping,
    mc.AmplitudeDamping,
    mc.GeneralizedAmplitudeDamping,
    mc.MixedUnitary,
    mc.Depolarizing,
    mc.ThermalNoise,
    mc.Kraus,
    mc.GateCustom,
    mc.GateDecl,
    mc.GateCall,
    mc.HamiltonianTerm,
    mc.Hamiltonian,
    mc.Detector,
    mc.ObservableInclude,
    mc.Add,
    mc.Multiply,
    mc.Pow,
    mc.Not,
    mc.Tick,
    mc.ShiftCoordinates,
    mc.QubitCoordinates,
    mc.MeasureReset,
    mc.GateHXY,
    mc.GateHYZ

}


class Quantanium:
    def __init__(self):
        """
        Initialize the MIMIQ Quantanium engine.
        """
        self._statevector = None
        self._cplx = None
        self._cstate = None


    @staticmethod
    def unwrap(op):
        """
        Recursively unwraps a quantum operation to obtain its base (inner) gate.

        This function handles common wrappers like:
        - Power (e.g., S = Power(Z, 1/2))
        - Control (e.g., Control(H))
        - Inverse (e.g., Inverse(T))

        Returns:
            The innermost unwrapped gate/operation (e.g., GateZ).
        """
        seen = set()

        while True:
            if id(op) in seen:
                # Prevent infinite loops in recursive wrappers
                break
            seen.add(id(op))

            # Generic .get_operation() method
            if hasattr(op, "get_operation"):
                inner = op.get_operation()
                if inner is not op:
                    op = inner
                    continue

            # Power wrapper
            if isinstance(op, mc.Power) and hasattr(op, "op"):
                op = op.op
                continue

            # Inverse wrapper
            if isinstance(op, mc.Inverse) and hasattr(op, "op"):
                op = op.op
                continue

            # Control wrapper
            if isinstance(op, mc.Control) and hasattr(op, "op"):
                op = op.op
                continue
            break
        return op


    def issupported(self, op: mc.Operation) -> bool:
        if type(op) in QUANTANIUM_SUPPORTED_OPERATIONS:
            return True

        if isinstance(op, mc.IfStatement):
            return self.issupported(op.get_operation())
 
        op_name = self.unwrap(op)
        if type(op_name) in QUANTANIUM_SUPPORTED_OPERATIONS:
            return True


        if isinstance(op, mc.BondDim):
            raise ValueError(
                "Bond dimension is not supported by the statevector simulator."
            )

        if isinstance(op, mc.SchmidtRank):
            raise ValueError(
                "The Schmidt rank is not supported by the statevector simulator."
            )

        if isinstance(op, mc.VonNeumannEntropy):
            raise ValueError(
                "The von Neumann entropy is not supported by the statevector simulator."
            )

        if isinstance(op, mc.ExpectationValue):
            if op.num_qubits <= 2:
                return True
            elif isinstance(op.get_operation(), mc.PauliString):
                return True
            else:
                raise ValueError(
                    "Expectation value of non Pauli strings more than 2 qubits is not supported."
                )

        if isinstance(op, mc.GateCustom):
            if op.num_qubits() <= 2:
                return True
            else:
                raise ValueError(
                    "Custom gates with more than 2 qubits are not supported by the local executor."
                )

        if isinstance(op, mc.PolynomialOracle):
            raise ValueError("PolynomialOracle is not supported by the local executor.")

        return False

    def _checkdecompose(self, c: MimiqCircuit, inst: mc.Instruction) -> bool:
        op = inst.get_operation()
        if self.issupported(op):
            c.push(inst)
        elif (
            isinstance(inst.get_operation(), mc.Gate)
            and not isinstance(op, mc.GateCall)
            and inst.num_qubits() <= 2
        ):
            c.push(mc.GateCustom(inst.get_operation().matrix()), *inst.get_qubits())
        else:
            decomposed = inst.decompose()
            for inst2 in decomposed:
                self._checkdecompose(c, inst2)
        return c

    def _decompose_mimiq(self, c: MimiqCircuit):
        cnew = MimiqCircuit()
        for inst in c:
            self._checkdecompose(cnew, inst)
        return cnew

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
        tmp_name = None
        try:
            # Create temp file, but don't delete it on close
            with tempfile.NamedTemporaryFile(suffix=".pb", delete=False) as tmp:
                # Write out the proto data
                self._decompose_mimiq(mimiq_circuit).saveproto(tmp)
                tmp.flush()
                tmp_name = tmp.name   # capture path

            # Now that tmp is closed (and unlocked), we can reopen it
            qua_circuit = ProtoParser().load_proto(tmp_name)
        except Exception as e:
            # Propagate with your custom message
            raise Exception(f"Error converting mimiq::Circuit to Circuit: {e}")

        finally:
            # Clean up the file if it exists
            if tmp_name and os.path.exists(tmp_name):
                try:
                    os.remove(tmp_name)
                except OSError:
                    pass

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
        tmp_name = None
        try:
            # Create a temp file but don’t delete on close, so we can reopen it
            with tempfile.NamedTemporaryFile(suffix=".pb", delete=False) as tmp:
                pp = ProtoParser()
                # Save the proto to the path
                pp.save_proto(tmp.name, qua_circuit)
                tmp_name = tmp.name

            # Now the file is closed and unlocked, we can load it
            mimiq_circuit = MimiqCircuit()
            mimiq_circuit = mimiq_circuit.loadproto(tmp_name)

        except Exception as e:
            raise Exception(f"Error converting Circuit to mimiq::Circuit: {e}")

        finally:
            # Clean up the temporary file
            if tmp_name and os.path.exists(tmp_name):
                try:
                    os.remove(tmp_name)
                except OSError:
                    pass

        return mimiq_circuit

    
    def parse_qasm(self, qasm_file: str) -> MimiqCircuit:
        """
        Parses a QASM file and converts it into a MimiqCircuit.

        Args:
            qasm_file (str): Path to the QASM file.

        Returns:
            MimiqCircuit: The converted MimiqCircuit.
        """
        # Step 1: Convert QASM to QUA circuit
        qua_circuit = self.convert_qasm_to_qua_circuit(qasm_file)

        # Step 2: Convert QUA circuit to MimiqCircuit
        mimiq_circuit = self.convert_qua_to_mimiq_circuit(qua_circuit)
        return mimiq_circuit

    def convert_qua_results_to_mimiq_results(
        self, qua_results: QuantaniumQCSResults
    ) -> QCSResults:
        """
        Convert a QCSResults to a QCSResults.

        Args:
            qua_results (QCSResults): The QCSResults to convert.

        Returns:
            QCSResult: The converted QCSResult (Mimiq).

        Raises:
            Exception: If there is an error in the conversion process.
        """
        tmp_name = None
        try:
            with tempfile.NamedTemporaryFile(suffix='.pb', delete=False) as tmp:
                pp = ProtoResult()
                pp.save_proto(tmp.name, qua_results)
                tmp_name = tmp.name


            mimiq_results = QCSResults()
            mimiq_results = mimiq_results.loadproto(tmp_name)
        except Exception as e:
            raise Exception(f"Error converting QuantaniumQCSResults to Mimiq QCSResults: {e}")
        finally:

            if tmp_name and os.path.exists(tmp_name):
                try:
                    os.remove(tmp_name)
                except OSError:
                    pass

        return mimiq_results


    def execute(
        self,
        circuit,
        label="pyapi_v1.0",
        algorithm="auto",
        nsamples=1000,
        bitstrings=None,
        timelimit=300,
        bonddim=None,
        entdim=None,
        seed=None,
        qasmincludes=None,
    ):
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
        if isinstance(circuit, MimiqCircuit):
            qua_circuit = self.convert_mimiq_to_qua_circuit(circuit)
        elif isinstance(circuit, Circuit):
            qua_circuit = circuit
        elif isinstance(circuit, str):
            qua_circuit = self.convert_qasm_to_qua_circuit(circuit)
        else:
            raise TypeError("circuit must be either a Circuit or mimiq::Circuit")
        try:
            if seed is None:
                seed = int(time.time())

            if bitstrings is None:
                bs = []
            else:
                bs = [QuantaniumBitVector(bitstring.to01()) for bitstring in bitstrings]

            qua_result, sv = execute_double(qua_circuit, nsamples, seed, bs)
            self._cplx = sv
            result = self.convert_qua_results_to_mimiq_results(qua_result)

        except Exception as e:
            raise Exception(f"Error executing the Circuit: {e}")

        return result



    def evolve(
            self,
            circuit,
            stop_before_measure=False,
            seed=None,
        ):
            """
            Evolve the given circuit, with or without a provided statevector.

            Args:
                circuit: MimiqCircuit, QuaCircuit or str.
                stop_before_measure (bool): Whether to stop before measurement.
                seed (int): Random seed (default = time.time()).

            """
            if isinstance(circuit, MimiqCircuit):
                qua_circuit = self.convert_mimiq_to_qua_circuit(circuit)
            elif isinstance(circuit, QuaCircuit):
                qua_circuit = circuit
            elif isinstance(circuit, str):
                qua_circuit = self.convert_qasm_to_qua_circuit(circuit)
            else:
                raise TypeError("circuit must be MimiqCircuit, Circuit, or str")

            if seed is None:
                seed = time.time_ns()

            try:
                if self._statevector is not None:
                    # Call evolve_next that modifies the given statevector in place
                    self._statevector, sv_cplx = evolve_next(self._statevector, qua_circuit, seed, stop_before_measure)
                    self._cplx = sv_cplx
                     
                else:
                    # Call evolve that returns a new statevector
                    self._statevector, sv_cplx = evolve(qua_circuit, seed, stop_before_measure)
                    self._cplx = sv_cplx
                  
            except Exception as e:
                raise RuntimeError(f"Error evolving the circuit: {e}")

            return 

    def zerostate(self):
        """
        Initializes the internal statevector to the zero state |00...0⟩.

        Raises:
            RuntimeError: If the internal statevector is not initialized.
        """
        if self._statevector is not None:    
            self._statevector.zerostate()

    def get_statevector(self):
        """
        Returns the statevector from the last execution.

        Returns:
            list: A list of complex numbers representing the statevector.
        """
        if not hasattr(self, "_statevector"):
            raise RuntimeError("Statevector is not available. Run 'execute' first.")
        return self._cplx #self._statevector

    def get_cstate(self):
        """
        Returns the classical state from the last evolve.

        Returns:
            list: A list of classical states.
        """
        if not hasattr(self, "_statevector"):
            raise RuntimeError("Statevector is not available. Run 'execute' first.")
        return self._statevector.get_cstates() 
    
    def get_results(self, *args, **kwargs):
        raise RuntimeError("get_results is only available for remote execution.")
