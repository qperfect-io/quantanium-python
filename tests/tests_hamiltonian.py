import unittest
from mimiqlink import MimiqConnection
from quantanium import Quantanium
from mimiqcircuits import *
import numpy as np


class TestHamiltonianConstruction(unittest.TestCase):
    def setUp(self):
        self.processor = Quantanium()
        self.nsamples = 1000
        self.seed = 1
        self.tolerance = 0.05

    def _log_success(self, name):
        print(f"[PASSED] {name}")

    def test_simple_hamiltonian(self):
        """
        Test conversion and execution of a Suzuki-Trotterized Hamiltonian circuit.
        """
        # Create a simple Hamiltonian H = Z + 0.5*X on qubit 0
        h = Hamiltonian()
        h.push(1.0, PauliString("Z"), 0)
        h.push(0.5, PauliString("X"), 0)

        # Build the circuit with Suzuki-Trotter expansion
        c_orig = Circuit()
        c_orig.push_suzukitrotter(h, (0,), t=1.0, steps=1, order=2)

        # Convert to Quantanium and back
        try:
            qua_circuit = self.processor.convert_mimiq_to_qua_circuit(c_orig)
            c_restored = self.processor.convert_qua_to_mimiq_circuit(qua_circuit)
        except Exception as e:
            self.fail(f"Quantanium conversion failed: {e}")

        self.assertEqual(len(c_orig), len(c_restored),
                         f"Instruction count mismatch: original={len(c_orig)} vs restored={len(c_restored)}")

        for i, (orig, recon) in enumerate(zip(c_orig, c_restored)):
            self.assertEqual(
                type(orig.operation), type(recon.operation),
                f"Operation type mismatch at index {i}: {type(orig.operation)} vs {type(recon.operation)}"
            )
            self.assertEqual(
                orig.qubits, recon.qubits,
                f"Qubit targets mismatch at index {i}: {orig.qubits} vs {recon.qubits}"
            )

        # Check that it executes without error
        try:
            result = self.processor.execute(qua_circuit, nsamples=self.nsamples, seed=self.seed)
        except Exception as e:
            self.fail(f"Execution raised an unexpected exception: {e}")

        self.assertIsNotNone(result, "Execution returned None unexpectedly")

        self._log_success("Test Suzuki-Trotter Hamiltonian Circuit (conversion + execution)")


if __name__ == "__main__":
    unittest.main()

