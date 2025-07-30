
import unittest
from collections import Counter
from quantanium import Quantanium
from mimiqcircuits import Circuit, GateX, GateY, GateZ, PauliString


class TestPauliStringIntegration(unittest.TestCase):
    def setUp(self):
        self.processor = Quantanium()
        self.nsamples = 1000
        self.seed = 42
        self.tolerance = 0.05

    def _log_success(self, name):
        print(f"[PASSED] {name}")

    def get_distribution_from_cstates(self, cstates):
        counts = Counter(cstates)
        total = sum(counts.values())
        return {k: v / total for k, v in counts.items()}

    def total_variation_distance(self, dist1, dist2):
        keys = set(dist1) | set(dist2)
        return sum(abs(dist1.get(k, 0) - dist2.get(k, 0)) for k in keys) / 2

    def build_manual_pauli_circuit(self, paulis, qubits):
        c = Circuit()
        for p, q in zip(paulis, qubits):
            if p == 'X':
                c.push(GateX(), q)
            elif p == 'Y':
                c.push(GateY(), q)
            elif p == 'Z':
                c.push(GateZ(), q)
        return c

    def build_paulistring_circuit(self, pauli_str):
        c = Circuit()
        c.push(pauli_str, 0, 1, 2)
        return c

    def test_paulistring_circuit_roundtrip_proto_conversion(self):
        # Construct the original circuit
        pauli_str = PauliString("XYZ")
        circuit_orig = self.build_paulistring_circuit(pauli_str)

        qua_circuit = self.processor.convert_mimiq_to_qua_circuit(circuit_orig)
        circuit_restored = self.processor.convert_qua_to_mimiq_circuit(qua_circuit)

        # Compare number of instructions
        self.assertEqual(
            len(circuit_orig),
            len(circuit_restored),
            f"Instruction count mismatch: original={len(circuit_orig)} vs restored={len(circuit_restored)}"
        )

        # Compare gate-by-gate
        for i in range(len(circuit_orig)):
            orig = circuit_orig[i]
            recon = circuit_restored[i]

            self.assertEqual(
                orig.operation.__class__,
                recon.operation.__class__,
                f"Gate type mismatch at index {i}: {orig.operation.__class__} vs {recon.operation.__class__}"
            )

            self.assertEqual(
                orig.qubits,
                recon.qubits,
                f"Qubit mismatch at index {i}: {orig.qubits} vs {recon.qubits}"
            )

            if hasattr(orig.operation, "theta"):
                self.assertAlmostEqual(
                    float(orig.operation.theta),
                    float(recon.operation.theta),
                    places=6,
                    msg=f"Theta mismatch at index {i}: {orig.operation.theta} vs {recon.operation.theta}"
                )

            if hasattr(orig.operation, "pauli_string"):
                self.assertEqual(
                    orig.operation.pauli_string,
                    recon.operation.pauli_string,
                    f"Pauli string mismatch at index {i}: {orig.operation.pauli_string} vs {recon.operation.pauli_string}"
                )

        self._log_success("Test PauliString Roundtrip Quantanium Conversion")

    def test_paulistring_vs_manual_gates(self):
        pauli_labels = ['X', 'Y', 'Z']
        qubits = [0, 1, 2]

        # Manual gate application
        circuit_manual = self.build_manual_pauli_circuit(pauli_labels, qubits)
        result_manual = self.processor.execute(circuit_manual, nsamples=self.nsamples, seed=self.seed)
        dist_manual = self.get_distribution_from_cstates(result_manual.cstates)

        # PauliString usage
        pauli_str = PauliString("XYZ")
        circuit_paulistring = self.build_paulistring_circuit(pauli_str)

        result_pauli = self.processor.execute(circuit_paulistring, nsamples=self.nsamples, seed=self.seed)
        dist_pauli = self.get_distribution_from_cstates(result_pauli.cstates)

        # Compare
        tvd = self.total_variation_distance(dist_manual, dist_pauli)
        self.assertLessEqual(tvd, self.tolerance, f"PauliString circuit differs too much: TVD = {tvd:.4f}")

        self._log_success("Test PauliString vs Manual Gates")

if __name__ == "__main__":
    unittest.main()
