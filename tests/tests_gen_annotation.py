
import unittest
from mimiqlink import MimiqConnection
from quantanium import Quantanium
from mimiqcircuits import *
import numpy as np


class TestGeneralizedAnnotations(unittest.TestCase):
    def setUp(self):
        self.processor = Quantanium()

    def _log_success(self, name):
        print(f"[PASSED] {name}")

    def test_detector_and_observable_annotations(self):
        """
        Test round-trip proto conversion for Detector and ObservableInclude annotations.
        """
        # Build a circuit
        c = Circuit()
        c.push(GateH(), 0)
        c.push(GateCX(), 0, 1)

        # Add annotations
        detector = Detector(1, [0.5, 1.0])
        observable = ObservableInclude(2, [1.0, 2.0])

        c.push(detector, 2)
        c.push(observable, 2, 3)

        # Convert to QUA and back
        qua = self.processor.convert_mimiq_to_qua_circuit(c)
        c_restored = self.processor.convert_qua_to_mimiq_circuit(qua)

        # Validate circuit length
        self.assertEqual(len(c), len(c_restored), "Mismatch in circuit instruction count after round-trip")

        # Validate restored Detector
        detector_restored = c_restored[-2].operation
        self.assertIsInstance(detector_restored, Detector, "Second-last operation should be Detector")

        self.assertEqual(detector_restored._num_bits, 1, "Restored Detector should target 1 classical bit")

        np.testing.assert_allclose(detector_restored.notes, [0.5, 1.0], err_msg="Detector notes mismatch")

        # Validate restored ObservableInclude
        restored_op = c_restored[-1].operation
        self.assertIsInstance(restored_op, ObservableInclude, "Last operation should be ObservableInclude")

        self.assertEqual(restored_op._num_bits, 2, "Restored ObservableInclude should target 2 classical bits")

        np.testing.assert_allclose(restored_op.notes, [1.0, 2.0], err_msg="ObservableInclude notes mismatch")

        self._log_success("Test Proto Conversion for Detector and ObservableInclude")

if __name__ == '__main__':
    unittest.main()
