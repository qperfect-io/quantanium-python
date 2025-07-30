import unittest
from quantanium import Quantanium
from mimiqcircuits import *


class TestIfStatementIntegration(unittest.TestCase):
    def setUp(self):
        self.processor = Quantanium()
        self.nsamples = 10
        self.seed = 1

    def test_ifstatement_roundtrip_qua_conversion(self):
        # Construct original circuit with an IfStatement
        c_orig = Circuit()
        bit_condition = BitString(2)  # 2-bit classical condition
        gate = GateX()
        if_stmt = IfStatement(gate, bit_condition)

        # Push IfStatement onto the circuit
        c_orig.push(if_stmt, 0, 1, 2)

        # Convert to QUA circuit and back to Mimiq
        qua = self.processor.convert_mimiq_to_qua_circuit(c_orig)
        c_restored = self.processor.convert_qua_to_mimiq_circuit(qua)

        # Check that instruction counts match
        self.assertEqual(
            len(c_orig),
            len(c_restored),
            f"Instruction count mismatch: {len(c_orig)} vs {len(c_restored)}"
        )

        # Extract the original and restored instructions
        instr_orig = c_orig[0]
        instr_restored = c_restored[0]

        # Verify the restored operation is an IfStatement
        self.assertIsInstance(
            instr_restored.operation, IfStatement,
            f"Expected IfStatement, got {type(instr_restored.operation)}"
        )

        # Check that the wrapped operation types match (e.g., GateX)
        self.assertEqual(
            type(instr_orig.operation._op),
            type(instr_restored.operation._op),
            "Wrapped operation mismatch inside IfStatement"
        )

        # Check that the bitstring conditions match
        self.assertEqual(
            instr_orig.operation._bitstring,
            instr_restored.operation._bitstring,
            "BitString condition mismatch in IfStatement"
        )

        # Check qubit targets match
        self.assertEqual(
            instr_orig.qubits,
            instr_restored.qubits,
            f"Qubit mismatch: {instr_orig.qubits} vs {instr_restored.qubits}"
        )

if __name__ == "__main__":
    unittest.main()

