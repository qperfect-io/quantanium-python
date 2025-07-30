import unittest
from collections import Counter
from quantanium import Quantanium
from mimiqcircuits import *
import numpy as np

class TestRNZIntegration(unittest.TestCase):
    """
    Unit tests for GateRNZ integration: verifying decomposition and proto roundtrip consistency
    using the Quantanium backend.
    """

    def setUp(self):
        self.processor = Quantanium()
        self.nsamples = 1000
        self.seed = 42
        self.tolerance = 0.005

    def get_distribution(self, cstates):
        counts = Counter(cstates)
        total = sum(counts.values())
        return {k: v / total for k, v in counts.items()}

    def total_variation_distance(self, dist1, dist2):
        keys = set(dist1) | set(dist2)
        return sum(abs(dist1.get(k, 0) - dist2.get(k, 0)) for k in keys) / 2

    def test_rnz_execution_equivalence_decomposed_vs_original(self):
        """
        Test Execution Equivalence for GateRNZ using decomposition vs original
        """
        g = GateRNZ(3, np.pi / 4)

        c_orig = Circuit()
        c_orig.push(GateH(), 0)
        c_orig.push(GateH(), 1)
        c_orig.push(GateCCX(), 0, 1, 2)
        c_orig.push(g, 0, 1, 2)
        c_orig.push(GateCCX(), 0, 1, 2)
        c_orig.push(GateH(), 0)
        c_orig.push(GateH(), 1)
        c_orig.push(Measure(), 0, 0)
        c_orig.push(Measure(), 1, 1)
        c_orig.push(Measure(), 2, 2)

        c_decomp = c_orig.decompose()

        result_orig = self.processor.execute(c_orig, nsamples=self.nsamples, seed=self.seed)
        result_decomp = self.processor.execute(c_decomp, nsamples=self.nsamples, seed=self.seed)
        print(result_decomp)
        print(result_orig)
        dist_orig = self.get_distribution(result_orig.cstates)
        dist_decomp = self.get_distribution(result_decomp.cstates)

        tvd = self.total_variation_distance(dist_orig, dist_decomp)
        print(f"TVD between original and decomposed RNZ: {tvd}")

        self.assertLessEqual(
            tvd,
            self.tolerance,
            f"TVD too high for RNZ decomposition: {tvd:.4f}"
        )

        print("[PASSED] Test Execution Equivalence for GateRNZ using decomposition vs original")

    def test_rnz_proto_roundtrip_and_decomposition_consistency(self):
        """
        Test Proto Conversion and Decomposition Roundtrip for GateRNZ
        """
        from math import pi

        g = GateRNZ(3, pi / 2)
        c_orig = Circuit()
        c_orig.push(g, 0, 1, 2)
        c_orig.push(Measure(), 0, 0)
        c_orig.push(Measure(), 1, 1)
        c_orig.push(Measure(), 2, 2)

        c_decomposed = c_orig.decompose()

        qua = self.processor.convert_mimiq_to_qua_circuit(c_orig)
        c_restored = self.processor.convert_qua_to_mimiq_circuit(qua)

        self.assertEqual(len(c_orig), len(c_restored), "Restored circuit length mismatch")

        for i in range(len(c_orig)):
            orig_op = c_orig[i].operation
            rest_op = c_restored[i].operation
            self.assertEqual(type(orig_op), type(rest_op), f"Gate type mismatch at index {i}")
            self.assertEqual(c_orig[i].qubits, c_restored[i].qubits, f"Qubit mismatch at index {i}")

        dec_orig = c_decomposed
        dec_restored = c_restored.decompose()

        self.assertEqual(len(dec_orig), len(dec_restored), "Decomposition length mismatch")

        for i in range(len(dec_orig)):
            o = dec_orig[i]
            r = dec_restored[i]
            self.assertEqual(type(o.operation), type(r.operation), f"Decomposed gate type mismatch at index {i}")
            self.assertEqual(o.qubits, r.qubits, f"Decomposed qubit mismatch at index {i}")

            if hasattr(o.operation, "theta"):
                self.assertAlmostEqual(
                    float(o.operation.theta),
                    float(r.operation.theta),
                    places=6,
                    msg=f"Theta mismatch at index {i}"
                )

        print("[PASSED] Test Proto Conversion and Decomposition Roundtrip for GateRNZ")

if __name__ == "__main__":
    unittest.main()

