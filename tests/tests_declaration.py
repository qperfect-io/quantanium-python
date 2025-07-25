import unittest
from collections import Counter
from mimiqcircuits import (
    Circuit,
    Block,
    GateX,
    GateH,
    GateY,
    GateRX,
    GateCX,
    Measure,
    Repeat,
    ExpectationValue,
    PauliString,
    gatedecl,
)
from symengine import symbols
from quantanium import Quantanium


class TestGateDeclarationEquivalence(unittest.TestCase):
    def setUp(self):
        self.processor = Quantanium()
        self.nsamples = 1000
        self.seed = 42
        self.tolerance = 0.05

    def _log_success(self, name):
        print(f"[PASSED] {name}")

    def get_distribution(self, cstates):
        counts = Counter(cstates)
        total = sum(counts.values())
        return {k: v / total for k, v in counts.items()}

    def total_variation_distance(self, dist1, dist2):
        keys = set(dist1) | set(dist2)
        return sum(abs(dist1.get(k, 0) - dist2.get(k, 0)) for k in keys) / 2

    def test_gatedecl_vs_manual_circuit(self):
        x = symbols("x")

        @gatedecl("custom_ansatz")
        def custom_ansatz(x):
            c = Circuit()
            c.push(GateH(), 0)
            c.push(GateRX(x), 1)
            c.push(GateCX(), 1, 0)
            c.push(GateY(), 1)
            return c

        c_decl = Circuit()
        c_decl.push(GateX(), 0)
        c_decl.push(custom_ansatz(0.7), 0, 1)
        c_decl.push(Measure(), 0, 0)
        c_decl.push(Measure(), 1, 1)

        c_manual = Circuit()
        c_manual.push(GateX(), 0)
        c_manual.push(GateH(), 0)
        c_manual.push(GateRX(0.7), 1)
        c_manual.push(GateCX(), 1, 0)
        c_manual.push(GateY(), 1)
        c_manual.push(Measure(), 0, 0)
        c_manual.push(Measure(), 1, 1)

        result_decl = self.processor.execute(c_decl, nsamples=self.nsamples, seed=self.seed)
        result_manual = self.processor.execute(c_manual, nsamples=self.nsamples, seed=self.seed)

        dist_decl = self.get_distribution(result_decl.cstates)
        dist_manual = self.get_distribution(result_manual.cstates)
        tvd = self.total_variation_distance(dist_decl, dist_manual)

        self.assertLessEqual(tvd, self.tolerance, f"TVD too large: {tvd:.4f} (declared vs manual circuit mismatch)")
        self._log_success("Test GateDecl vs Manual Circuit Equivalence")

    def test_gatedecl_vs_manual_equivalence_simple(self):
        x = symbols("x")

        @gatedecl("ansatz")
        def ansatz(x):
            c = Circuit()
            c.push(GateX(), 0)
            c.push(GateRX(x), 1)
            return c

        c_declared = Circuit()
        c_declared.push(ansatz(1), 0, 1)
        c_declared.push(Measure(), 0, 0)
        c_declared.push(Measure(), 1, 1)

        c_unrolled = Circuit()
        c_unrolled.push(GateX(), 0)
        c_unrolled.push(GateRX(1), 1)
        c_unrolled.push(Measure(), 0, 0)
        c_unrolled.push(Measure(), 1, 1)

        result_decl = self.processor.execute(c_declared, nsamples=self.nsamples, seed=self.seed)
        result_unrolled = self.processor.execute(c_unrolled, nsamples=self.nsamples, seed=self.seed)

        dist_decl = self.get_distribution(result_decl.cstates)
        dist_unrolled = self.get_distribution(result_unrolled.cstates)
        tvd = self.total_variation_distance(dist_decl, dist_unrolled)

        self.assertLessEqual(tvd, self.tolerance, f"TVD too large: {tvd:.4f} (gatedecl vs unrolled mismatch)")
        self._log_success("Test GateDecl vs Manual Equivalence Simple")

    def test_declared_gate_roundtrip_proto_conversion(self):
        x = symbols("x")

        @gatedecl("ansatz")
        def ansatz(x):
            c = Circuit()
            c.push(GateX(), 0)
            c.push(GateRX(x), 1)
            c.push(GateCX(), 1, 0)
            return c

        c = Circuit()
        c.push(ansatz(0.42), 0, 1)
        c.push(Measure(), 0, 0)
        c.push(Measure(), 1, 1)

        qua = self.processor.convert_mimiq_to_qua_circuit(c)
        restored = self.processor.convert_qua_to_mimiq_circuit(qua)

        self.assertEqual(len(c), len(restored), "Instruction count mismatch after round-trip")

        for i in range(len(c)):
            orig = c[i]
            recon = restored[i]

            self.assertEqual(orig.operation.__class__, recon.operation.__class__, f"Gate type mismatch at {i}")
            self.assertEqual(orig.qubits, recon.qubits, f"Qubit mismatch at {i}")
            self.assertEqual(orig.bits, recon.bits, f"Bit mismatch at {i}")
            if hasattr(orig.operation, "theta"):
                self.assertAlmostEqual(
                    float(orig.operation.theta),
                    float(recon.operation.theta),
                    places=6,
                    msg=f"Theta mismatch at {i}"
                )

        self._log_success("Test Declared Gate Structure Preserved After Conversion")

    def test_block_gate_equivalence(self):
        block = Block(2, 0, 0)
        block.push(GateX(), 0)
        block.push(GateY(), 1)

        repeated_block = Repeat(3, block)

        c_block = Circuit()
        c_block.push(repeated_block, 0, 1)
        c_block.push(Measure(), 0, 0)
        c_block.push(Measure(), 1, 1)

        c_manual = Circuit()
        for _ in range(3):
            c_manual.push(GateX(), 0)
            c_manual.push(GateY(), 1)
        c_manual.push(Measure(), 0, 0)
        c_manual.push(Measure(), 1, 1)

        result_block = self.processor.execute(c_block, nsamples=self.nsamples, seed=self.seed)
        result_manual = self.processor.execute(c_manual, nsamples=self.nsamples, seed=self.seed)

        dist_block = self.get_distribution(result_block.cstates)
        dist_manual = self.get_distribution(result_manual.cstates)
        tvd = self.total_variation_distance(dist_block, dist_manual)

        self.assertLessEqual(tvd, self.tolerance, f"TVD too large in block test: {tvd:.4f}")
        self._log_success("Test Block Gate vs Manual Circuit Equivalence")

    def test_multiple_gatedecls_vs_manual(self):
        x, y = symbols("x y")

        @gatedecl("first_decl")
        def first_decl(x):
            c = Circuit()
            c.push(GateRX(x), 0)
            c.push(GateH(), 0)
            return c

        @gatedecl("second_decl")
        def second_decl(y):
            c = Circuit()
            c.push(GateY(), 0)
            c.push(GateRX(y), 0)
            return c

        c_decl = Circuit()
        c_decl.push(first_decl(0.5), 0)
        c_decl.push(second_decl(0.8), 1)
        c_decl.push(Measure(), 0, 0)
        c_decl.push(Measure(), 1, 1)

        c_manual = Circuit()
        c_manual.push(GateRX(0.5), 0)
        c_manual.push(GateH(), 0)
        c_manual.push(GateY(), 1)
        c_manual.push(GateRX(0.8), 1)
        c_manual.push(Measure(), 0, 0)
        c_manual.push(Measure(), 1, 1)

        result_decl = self.processor.execute(c_decl, nsamples=self.nsamples, seed=self.seed)
        result_manual = self.processor.execute(c_manual, nsamples=self.nsamples, seed=self.seed)

        dist_decl = self.get_distribution(result_decl.cstates)
        dist_manual = self.get_distribution(result_manual.cstates)
        tvd = self.total_variation_distance(dist_decl, dist_manual)

        self.assertLessEqual(tvd, self.tolerance, f"TVD too large: {tvd:.4f} (multiple declared vs manual mismatch)")
        self._log_success("Test Multiple GateDecls vs Manual Circuit Equivalence")


if __name__ == "__main__":
    unittest.main()
