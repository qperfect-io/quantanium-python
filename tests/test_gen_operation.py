import unittest
import numpy as np
from quantanium import Quantanium
from mimiqlink import MimiqConnection
from mimiqcircuits import *

class TestGeneralizedArithmeticOperations(unittest.TestCase):
    def setUp(self):
        self.processor = Quantanium()
        self.seed = 42
        self.nsamples = 123

    def _log_success(self, name):
        print(f"[PASSED] {name}")

    def test_add_and_multiply_roundtrip_proto_conversion(self):
        """
        Test Quantanium proto round-trip for Add and Multiply instructions.
        """
        c_orig = Circuit()

        c_orig.push(Add(3, c=5.0), 0, 1, 2)
        c_orig.push(Multiply(3, c=3.0), 0, 1, 2)

        qua = self.processor.convert_mimiq_to_qua_circuit(c_orig)
        c_restored = self.processor.convert_qua_to_mimiq_circuit(qua)

        self.assertEqual(len(c_orig), len(c_restored),
                         f"Instruction count mismatch: original={len(c_orig)}, restored={len(c_restored)}")

        for i, (orig, recon) in enumerate(zip(c_orig, c_restored)):
            self.assertEqual(type(orig.operation), type(recon.operation),
                             f"Operation type mismatch at index {i}: {type(orig.operation)} vs {type(recon.operation)}")
            if hasattr(orig.operation, 'c'):
                self.assertAlmostEqual(
                    float(orig.operation.c), float(recon.operation.c),
                    msg=f"Parameter mismatch at index {i}: {orig.operation.c} vs {recon.operation.c}"
                )

        self._log_success("Test Proto Conversion for Add and Multiply")

    def test_add_zstate(self):
        """
        Test Add modifies z-registers correctly.
        """
        c = Circuit()
        c.push(GateH(), 0)
        c.push(Add(3, c=5.0), 0, 1, 2)

        result = self.processor.execute(c, seed=self.seed)
        zstates = result.zstates

        self.assertGreaterEqual(len(zstates), 1)
        z0, z1, z2 = zstates[0][0], zstates[0][1], zstates[0][2]

        self.assertAlmostEqual(z0.real, 5.0, places=5, msg=f"z0 mismatch: got {z0}, expected 5.0")
        self.assertAlmostEqual(z1.real, 0.0, places=5, msg=f"z1 mismatch: got {z1}, expected 0.0")
        self.assertAlmostEqual(z2.real, 0.0, places=5, msg=f"z2 mismatch: got {z2}, expected 0.0")

        self._log_success("Test Add z-state modification")

    def test_add_and_multiply_zstate(self):
        """
        Test chained Add and Multiply with z-registers set to zero.
        """
        c = Circuit()
        c.push(GateH(), 0)
        c.push(Add(3, c=5.0), 0, 1, 2)
        # c.push(Barrier(1), 1)
        c.push(Multiply(3, c=3.0), 0, 1, 2)

        result = self.processor.execute(c, seed=self.seed)
        zstates = result.zstates
        self.assertGreaterEqual(len(zstates), 1)

        z0, z1, z2 = zstates[0][0], zstates[0][1], zstates[0][2]

        self.assertAlmostEqual(z0.real, 0.0, places=5, msg=f"z0 mismatch: got {z0}, expected 0.0")
        self.assertAlmostEqual(z1.real, 0.0, places=5, msg=f"z1 mismatch: got {z1}, expected 0.0")
        self.assertAlmostEqual(z2.real, 0.0, places=5, msg=f"z2 mismatch: got {z2}, expected 0.0")

        self._log_success("Test Add and Multiply with zeroed z-registers")

    def test_add_and_multiply_zstate_nonzero(self):
        """
        Test correct z-register values after Add and Multiply with nonzero initial values.
        """
        c = Circuit()
        c.push(GateH(), 0)
        c.push(Add(1, c=1.0), 1)
        c.push(Add(1, c=2.0), 2)
        c.push(Add(3, c=5.0), 0, 1, 2)
        c.push(Multiply(3, c=3.0), 0, 1, 2)

        result = self.processor.execute(c, seed=self.seed)
        zstates = result.zstates
        self.assertGreaterEqual(len(zstates), 1)

        z0, z1, z2 = zstates[0][0], zstates[0][1], zstates[0][2]

        self.assertAlmostEqual(z0.real, 48.0, places=5, msg=f"z0 mismatch: got {z0}, expected 48.0")
        self.assertAlmostEqual(z1.real, 1.0, places=5, msg=f"z1 mismatch: got {z1}, expected 1.0")
        self.assertAlmostEqual(z2.real, 2.0, places=5, msg=f"z2 mismatch: got {z2}, expected 2.0")

        self._log_success("Test Add and Multiply with non-zero z-registers")


if __name__ == "__main__":
    unittest.main()

