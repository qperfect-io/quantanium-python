import unittest
from collections import Counter
from quantanium import Quantanium
from mimiqcircuits import (
    Circuit,
    Block,
    GateH,
    GateX,
    GateY,
    GateCX,
    GateCH,
    GateRZZ,
    Measure,
    MeasureZ,
    MeasureY,
    MeasureZZ,
    ExpectationValue,
    PauliString,
    Repeat,
)

class TestRepeatConstruction(unittest.TestCase):
    """
    Unit tests for Repeat and Block-based operations in mimiqcircuits,
    including proto round-trip conversion and functional equivalence.
    """

    def setUp(self):
        self.processor = Quantanium()
        self.nsamples = 1000
        self.seed = 1
        self.tolerance = 0.05

    def _log_success(self, name):
        print(f"[PASSED] {name}")

    def test_proto_conversion_simple_repeat(self):
        """
        Test Proto Conversion for Repeat(GateX)
        """
        circuit = Circuit()
        circuit.push(Repeat(3, GateX()), 0)

        qua_circuit = self.processor.convert_mimiq_to_qua_circuit(circuit)
        restored = self.processor.convert_qua_to_mimiq_circuit(qua_circuit)

        self.assertEqual(len(restored), 1)
        inst = restored[0]
        self.assertIsInstance(inst.operation, Repeat)
        self.assertEqual(inst.operation.repeats, 3)
        self.assertEqual(inst.operation.op.__class__.__name__, "GateX")

        self._log_success("Test Proto Conversion for Repeat(GateX)")

    def test_proto_conversion_repeat_blocks_and_gates(self):
        """
        Test Proto Conversion for Repeat with Gate and Block Instructions
        """
        c = Circuit()
        c.push(Repeat(3, GateX()), 1)
        c.push(Repeat(3, GateX()), 4)
        c.push(Repeat(3, GateCH()), 4, 5)
        c.push(Repeat(3, GateRZZ(3.21)), 3, 4)

        b = Block(3, 2, 1)
        b.push(GateH(), 0)
        b.push(GateCX(), 0, 1)
        b.push(Measure(), 1, 1)
        b.push(ExpectationValue(PauliString("ZZ")), 0, 2, 0)

        c.push(Repeat(3, b), 0, 1, 2, 0, 1, 0)

        qc = self.processor.convert_mimiq_to_qua_circuit(c)
        loaded = self.processor.convert_qua_to_mimiq_circuit(qc)

        self.assertIsInstance(loaded, Circuit)
        self.assertEqual(len(loaded), len(c))

        for i in range(len(c)):
            self.assertIsInstance(loaded[i].operation, Repeat)
            self.assertEqual(loaded[i].operation.repeats, 3)
            inner_op = loaded[i].operation.op
            if isinstance(inner_op, Block):
                self.assertIsInstance(inner_op[0].operation, GateH)

        self._log_success("Test Proto Conversion for Repeat with Gate and Block Instructions")

    def get_distribution(self, cstates):
        counts = Counter(cstates)
        total = sum(counts.values())
        return {k: v / total for k, v in counts.items()}

    def total_variation_distance(self, dist1, dist2):
        keys = set(dist1) | set(dist2)
        return sum(abs(dist1.get(k, 0) - dist2.get(k, 0)) for k in keys) / 2

    def test_execution_repeat_vs_unrolled(self):
        """
        Test Execution Equivalence: Repeat(GateX) vs 3x GateX
        """
        circuit_repeat = Circuit()
        circuit_repeat.push(Repeat(3, GateX()), 0)
        circuit_repeat.push(Measure(), 0, 0)

        circuit_unrolled = Circuit()
        circuit_unrolled.push(GateX(), 0)
        circuit_unrolled.push(GateX(), 0)
        circuit_unrolled.push(GateX(), 0)
        circuit_unrolled.push(Measure(), 0, 0)

        result_repeat = self.processor.execute(circuit_repeat, nsamples=self.nsamples, seed=self.seed)
        result_unrolled = self.processor.execute(circuit_unrolled, nsamples=self.nsamples, seed=self.seed)

        dist_repeat = self.get_distribution(result_repeat.cstates)
        dist_unrolled = self.get_distribution(result_unrolled.cstates)

        tvd = self.total_variation_distance(dist_repeat, dist_unrolled)

        self.assertLessEqual(
            tvd,
            self.tolerance,
            f"TVD too large: {tvd:.4f} (repeat vs unrolled results differ)"
        )

        self._log_success("Test Execution Equivalence: Repeat(GateX) vs 3x GateX")

if __name__ == "__main__":
    unittest.main()

