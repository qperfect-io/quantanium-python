

import unittest
from collections import Counter
from quantanium import Quantanium
from mimiqcircuits import Circuit, Block, GateH, GateX, GateCX, Measure


class TestBlockEquivalence(unittest.TestCase):
    def setUp(self):
        self.processor = Quantanium()
        self.nsamples = 1000
        self.seed = 1
        self.tolerance = 0.05  # Threshold for total variation distance

    def _log_success(self, name):
        print(f"[PASSED] {name}")

    def build_block_circuit(self):
        # Create a circuit using a Block
        block = Block(3, 1, 0)
        block.push(GateH(), 1)
        block.push(GateCX(), 1, 2)
        block.push(Measure(), 2, 0)

        circuit = Circuit()
        circuit.push(block, 3, 4, 5, 0)
        return circuit

    def build_flat_circuit(self):
        # Create an equivalent circuit without using Block
        circuit = Circuit()
        circuit.push(GateH(), 4)
        circuit.push(GateCX(), 4, 5)
        circuit.push(Measure(), 5, 0)
        return circuit

    def get_distribution(self, cstates):
        counts = Counter(cstates)
        total = sum(counts.values())
        return {k: v / total for k, v in counts.items()}

    def total_variation_distance(self, dist1, dist2):
        # Calculate total variation distance between two distributions
        keys = set(dist1) | set(dist2)
        return sum(abs(dist1.get(k, 0) - dist2.get(k, 0)) for k in keys) / 2

    def test_block_vs_flat_distribution(self):
        # Compare Block-based and flat circuit output distributions
        result_block = self.processor.execute(self.build_block_circuit(), nsamples=self.nsamples, seed=self.seed)
        result_flat = self.processor.execute(self.build_flat_circuit(), nsamples=self.nsamples, seed=self.seed)

        dist_block = self.get_distribution(result_block.cstates)
        dist_flat = self.get_distribution(result_flat.cstates)
        tvd = self.total_variation_distance(dist_block, dist_flat)

        self.assertLessEqual(
            tvd,
            self.tolerance,
            f"TVD too large: {tvd:.4f} (Block vs Flat circuit)"
        )
        self._log_success("Test Block vs Flat Distribution")

    def test_simple_block_roundtrip_proto_conversion(self):
        # Create a simple Block and push it into a circuit
        block = Block(3, 1, 0)
        block.push(GateH(), 1)
        block.push(GateCX(), 1, 2)
        block.push(Measure(), 2, 0)

        circuit = Circuit()
        circuit.push(block, 0, 1, 2, 0)

        # Ensure the circuit executes without error
        _ = self.processor.execute(circuit, nsamples=self.nsamples, seed=self.seed)

        # Convert to QUA and back
        qua = self.processor.convert_mimiq_to_qua_circuit(circuit)
        restored = self.processor.convert_qua_to_mimiq_circuit(qua)

        # Check structure and instruction contents
        self.assertEqual(len(restored), 1)
        inst = restored[0]
        self.assertIsInstance(inst.operation, Block)
        self.assertEqual(inst.qubits, (0, 1, 2))
        self.assertEqual(inst.bits, (0,))
        self.assertEqual(len(inst.operation), 3)
        sub = inst.operation
        self.assertIsInstance(sub[0].operation, GateH)
        self.assertIsInstance(sub[2].operation, Measure)

        self._log_success("Test Block Roundtrip and Structure")

    def test_nested_block_roundtrip_proto_conversion(self):
        # Create a nested Block structure
        inner = Block(1, 0, 0)
        inner.push(GateCX(), 0)

        outer = Block(2, 0, 0)
        outer.push(GateH(), 1)
        outer.push(inner, 0)

        circuit = Circuit()
        circuit.push(outer, 1, 2)

        # Convert to Quantanium and back
        qua = self.processor.convert_mimiq_to_qua_circuit(circuit)
        restored = self.processor.convert_qua_to_mimiq_circuit(qua)

        # Validate structure
        self.assertEqual(len(restored), 1)
        inst = restored[0]
        self.assertIsInstance(inst.operation, Block)

        restored_outer = inst.operation
        self.assertIsInstance(restored_outer[0].operation, GateH)
        self.assertIsInstance(restored_outer[1].operation, Block)
        inner_restored = restored_outer[1]
        self.assertIsInstance(inner_restored.decompose()[0].operation, GateX)

        self._log_success("Test Nested Block Conversion")


if __name__ == "__main__":
    unittest.main()
