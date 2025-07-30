import unittest
from quantanium import Quantanium
from mimiqcircuits import (
    Circuit,
    GateX,
    Tick,
    QubitCoordinates,
    ShiftCoordinates,
    Detector,
    ObservableInclude,
)

class TestAnnotationConversion(unittest.TestCase):
    """
    Unit tests for conversion and execution of annotation operations
    using the Quantanium processor.
    """

    def setUp(self):
        """Initialize the processor and circuit for both tests."""
        self.processor = Quantanium()
        self.nsamples = 1000
        self.seed = 1

        # Store circuit for reuse in both tests
        self.c_orig = Circuit()
        self.c_orig.push(GateX(), 0)  # Add standard gate

        annotation_ops = [
            (Tick(), None),
            (QubitCoordinates([0.2, 0.3]), 0),
            (ShiftCoordinates(0.5, 0.5, 0.0), None),
            (Detector(1, [0.1, 0.9]), 0),
            (ObservableInclude(1, [1]), 0),
        ]

        for op, target in annotation_ops:
            if target is not None:
                self.c_orig.push(op, target)
            else:
                self.c_orig.push(op)

    def _log_success(self, name):
        print(f"[PASSED] {name}")

    def test_annotation_proto_conversion_roundtrip(self):
        """
        Test Proto Conversion for annotation operations:
        Tick, QubitCoordinates, ShiftCoordinates, Detector, ObservableInclude
        """
        try:
            qua = self.processor.convert_mimiq_to_qua_circuit(self.c_orig)
            c_restored = self.processor.convert_qua_to_mimiq_circuit(qua)
        except Exception as e:
            self.fail(f"Conversion failed: {e}")

        self.assertEqual(
            len(self.c_orig), len(c_restored),
            f"Instruction count mismatch: {len(self.c_orig)} vs {len(c_restored)}"
        )

        for i, (orig, recon) in enumerate(zip(self.c_orig, c_restored)):
            self.assertEqual(
                type(orig.operation), type(recon.operation),
                f"Operation type mismatch at index {i}: {type(orig.operation)} vs {type(recon.operation)}"
            )
            if hasattr(orig.operation, "get_notes") and callable(orig.operation.get_notes):
                self.assertEqual(
                    recon.operation.get_notes(), orig.operation.get_notes(),
                    f"Note mismatch at index {i}: {recon.operation.get_notes()} vs {orig.operation.get_notes()}"
                )

        self._log_success("Test Proto Conversion for Annotation Operations")

    def test_annotation_execution(self):
        """
        Test Execution of annotation operations:
        Tick, QubitCoordinates, ShiftCoordinates, Detector, ObservableInclude
        """
        try:
            result = self.processor.execute(
                self.c_orig,
                nsamples=self.nsamples,
                seed=self.seed
            )
        except Exception as e:
            self.fail(f"Execution raised an unexpected exception: {e}")

        self._log_success("Test Execution for Annotation Operations")

if __name__ == "__main__":
    unittest.main()
