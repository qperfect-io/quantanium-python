import unittest
from quantanium import Quantanium
from mimiqcircuits import *


class TestSimpleOperationRoundtrip(unittest.TestCase):
    def setUp(self):
        self.processor = Quantanium()
        self.seed = 123
        self.nsamples = 5

    def _log_success(self, name):
        print(f"[PASSED] {name}")

    def assert_roundtrip_equal(self, c_orig):
        qua = self.processor.convert_mimiq_to_qua_circuit(c_orig)
        c_restored = self.processor.convert_qua_to_mimiq_circuit(qua)
        self.assertEqual(len(c_orig), len(c_restored), "Instruction count mismatch")

        for i, (orig, recon) in enumerate(zip(c_orig, c_restored)):
            self.assertEqual(
                orig.operation.__class__, recon.operation.__class__,
                f"Operation type mismatch at index {i}"
            )
            if hasattr(orig.operation, 'c'):
                self.assertAlmostEqual(
                    float(orig.operation.c), float(recon.operation.c),
                    msg=f"Parameter mismatch at index {i}"
                )

    def assert_roundtrip_equal_decomp(self, c_orig):
        qua = self.processor.convert_mimiq_to_qua_circuit(c_orig)
        c_restored = self.processor.convert_qua_to_mimiq_circuit(qua)
        c_orig = c_orig.decompose()

        self.assertEqual(len(c_orig), len(c_restored), "Instruction count mismatch")

        for i, (orig, recon) in enumerate(zip(c_orig, c_restored)):
            self.assertEqual(
                orig.operation.__class__, recon.operation.__class__,
                f"Operation type mismatch at index {i}"
            )
            if hasattr(orig.operation, 'c'):
                self.assertAlmostEqual(
                    float(orig.operation.c), float(recon.operation.c),
                    msg=f"Parameter mismatch at index {i}"
                )

    def test_proto_pow(self):
        c = Circuit()
        c.push(Pow(2), 1)
        self.assert_roundtrip_equal(c)
        self._log_success("Test Proto Conversion for Pow")

    def test_proto_not(self):
        c = Circuit()
        c.push(Not(), 1)
        self.assert_roundtrip_equal(c)
        self._log_success("Test Proto Conversion for Not")

    def test_proto_measurex(self):
        c = Circuit()
        c.push(MeasureX(), 1, 1)
        self.assert_roundtrip_equal_decomp(c)
        self._log_success("Test Proto Conversion for MeasureX")

    def test_proto_measurey(self):
        c = Circuit()
        c.push(MeasureY(), 1, 1)
        self.assert_roundtrip_equal_decomp(c)
        self._log_success("Test Proto Conversion for MeasureY")

    def test_proto_measurez(self):
        c = Circuit()
        c.push(MeasureZ(), 1, 1)
        self.assert_roundtrip_equal(c)
        self._log_success("Test Proto Conversion for MeasureZ")

    def test_proto_measure_default(self):
        c = Circuit()
        c.push(Measure(), 1, 1)
        self.assert_roundtrip_equal(c)
        self._log_success("Test Proto Conversion for Measure (default Z)")

    def test_proto_measurexx(self):
        c = Circuit()
        c.push(MeasureXX(), 1, 2, 1)
        self.assert_roundtrip_equal_decomp(c)
        self._log_success("Test Proto Conversion for MeasureXX")

    def test_proto_measureyy(self):
        c = Circuit()
        c.push(MeasureYY(), 1, 2, 1)
        self.assert_roundtrip_equal_decomp(c)
        self._log_success("Test Proto Conversion for MeasureYY")

    def test_proto_measurezz(self):
        c = Circuit()
        c.push(MeasureZZ(), 1, 2, 1)
        self.assert_roundtrip_equal_decomp(c)
        self._log_success("Test Proto Conversion for MeasureZZ")

    def test_proto_measureresetx(self):
        c = Circuit()
        c.push(MeasureResetX(), 1, 1)
        self.assert_roundtrip_equal_decomp(c)
        self._log_success("Test Proto Conversion for MeasureResetX")

    def test_proto_measureresety(self):
        c = Circuit()
        c.push(MeasureResetY(), 1, 1)
        self.assert_roundtrip_equal_decomp(c)
        self._log_success("Test Proto Conversion for MeasureResetY")

    def test_proto_measureresetz(self):
        c = Circuit()
        c.push(MeasureResetZ(), 1, 1)
        self.assert_roundtrip_equal(c)
        self._log_success("Test Proto Conversion for MeasureResetZ")

    def test_proto_measurereset_default(self):
        c_orig = Circuit()
        c_orig.push(GateX(), 1)
        c_orig.push(MeasureReset(), 1, 1)
        c_orig.push(Measure(), 1, 1)

        c_restored = c_orig.decompose()
        result_orig = self.processor.execute(c_orig, nsamples=self.nsamples, seed=self.seed)
        result_restored = self.processor.execute(c_restored, nsamples=self.nsamples, seed=self.seed)

        c_orig_state = result_orig.cstates
        c_rest_state = result_restored.cstates
        self.assertEqual(len(c_orig_state), len(c_rest_state), "Mismatch in number of classical registers")

        for i in range(len(c_orig_state)):
            self.assertEqual(c_orig_state[i], c_rest_state[i], f"Mismatch in cstates[{i}]")

        if result_orig.zstates and result_restored.zstates:
            z_orig_state = result_orig.zstates[0]
            z_rest_state = result_restored.zstates[0]
            self.assertEqual(len(z_orig_state), len(z_rest_state), "Mismatch in number of z-registers")
            for i in range(len(z_orig_state)):
                self.assertAlmostEqual(
                    z_orig_state[i].real,
                    z_rest_state[i].real,
                    places=5,
                    msg=f"Mismatch in zstates[{i}]: {z_orig_state[i]} vs {z_rest_state[i]}"
                )
        self._log_success("Test Execution Equivalence for Decomposed MeasureReset")

    def test_execution_pow_zstate(self):
        c = Circuit()
        c.push(GateH(), 0)
        c.push(Add(3, c=2.0), 0, 1, 2)
        c.push(Pow(2.0), 0)

        result = self.processor.execute(c, nsamples=self.nsamples, seed=self.seed)
        zstates = result.zstates
        self.assertGreaterEqual(len(zstates), 1, "Expected at least 1 z-registers")

        z0 = zstates[0][0]
        z1 = zstates[0][1]
        z2 = zstates[0][2]

        self.assertAlmostEqual(z0.real, 4.0, places=5, msg=f"z0 mismatch: got {z0}, expected 4.0")
        self.assertAlmostEqual(z1.real, 0.0, places=5, msg=f"z1 mismatch: got {z1}, expected 0.0")
        self.assertAlmostEqual(z2.real, 0.0, places=5, msg=f"z2 mismatch: got {z2}, expected 0.0")
        self._log_success("Test Execution for Pow on Z-State")

    def test_execution_not_creg(self):
        c = Circuit()
        c.push(GateX(), 0)
        c.push(GateX(), 0)
        c.push(Measure(), 0, 0)
        c.push(Not(), 0)
        result = self.processor.execute(c, nsamples=self.nsamples, seed=self.seed)
        creg = result.cstates

        self.assertGreaterEqual(len(creg), 1, "Expected at least 1 classical bit")
        self.assertEqual(creg[0][0], True, f"c[0] mismatch: got {creg[0][0]}, expected True")
        self._log_success("Test Execution for Classical Not Gate")


if __name__ == "__main__":
    unittest.main()
