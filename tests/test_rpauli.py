import unittest
from collections import Counter
from mimiqlink import MimiqConnection
from quantanium import Quantanium
from mimiqcircuits import *
from symengine import pi, Symbol, Matrix
import io
from symengine import symbols, pi

class TestRPauliConstruction(unittest.TestCase):
    def setUp(self):
        self.processor = Quantanium()
        self.nsamples = 1000
        self.seed = 1
        self.tolerance = 0.05
    
    def get_distribution(self, cstates):
        counts = Counter(cstates)
        total = sum(counts.values())
        return {k: v / total for k, v in counts.items()}
    
    def total_variation_distance(self, dist1, dist2):
        keys = set(dist1) | set(dist2)
        return sum(abs(dist1.get(k, 0) - dist2.get(k, 0)) for k in keys) / 2

    def test_rpauli_decomposition_consistency(self):

        c_orig = Circuit()
        c_orig.push(RPauli(PauliString("XYZIZZY"), pi), 0, 1, 2, 3, 4, 5, 6)

        # Decomposed version of original
        c_decomposed = c_orig.decompose()
        
        # Round-trip: convert to QUA and back
        qua = self.processor.convert_mimiq_to_qua_circuit(c_orig)
        c_restored = self.processor.convert_qua_to_mimiq_circuit(qua)

        # Compare restored with original undecomposed (length & structure)
        self.assertEqual(len(c_orig), len(c_restored), "Restored circuit length mismatch")

        for i in range(len(c_orig)):
            orig_op = c_orig[i].operation
            rest_op = c_restored[i].operation
            self.assertEqual(type(orig_op), type(rest_op), f"Gate type mismatch at index {i}")
            self.assertEqual(c_orig[i].qubits, c_restored[i].qubits, f"Qubit mismatch at index {i}")

        # Compare decompositions
        dec_orig = c_decomposed
        dec_restored = c_restored.decompose()

        self.assertEqual(len(dec_orig), len(dec_restored), "Decomposition length mismatch")

        for i in range(len(dec_orig)):
            o = dec_orig[i]
            r = dec_restored[i]
            self.assertEqual(type(o.operation), type(r.operation), f"Decomposed gate mismatch at index {i}")
            self.assertEqual(o.qubits, r.qubits, f"Decomposed qubits mismatch at index {i}")
            if hasattr(o.operation, "theta"):
                self.assertAlmostEqual(float(o.operation.theta), float(r.operation.theta), places=6,
                                    msg=f"Theta mismatch at index {i}")

        # Execute both and compare output distributions
        result_orig = self.processor.execute(c_orig, nsamples=self.nsamples, seed=self.seed)
        print(c_decomposed)
        result_dec = self.processor.execute(c_decomposed, nsamples=self.nsamples, seed=self.seed)

        dist_orig = self.get_distribution(result_orig.cstates)
        dist_dec = self.get_distribution(result_dec.cstates)
        tvd = self.total_variation_distance(dist_orig, dist_dec)

        self.assertLessEqual(
            tvd, self.tolerance,
            f"TVD too large: {tvd:.4f} between RPauli and its decomposition"
       )

    def test_rpauli_affects_distribution(self):

        theta = pi  # rotation with known non-trivial effect
       
        # Circuit with RPauli
        c = Circuit()
        c.push(GateH(), 0)
        c.push(GateCX(), 0, 1)
        c.push(RPauli(PauliString("XXIZ"), theta), 0, 1, 2, 3)

        # Circuit without RPauli
        c_decomp = c.decompose()

        # Execute both
        result_orig = self.processor.execute(c, nsamples=self.nsamples, seed=self.seed)
        result_decomp = self.processor.execute(c_decomp, nsamples=self.nsamples, seed=self.seed)

        dist_orig = self.get_distribution(result_orig.cstates)
        dist_decomp = self.get_distribution(result_decomp.cstates)
  
        tvd = self.total_variation_distance(dist_orig, dist_decomp)
 
        self.assertLessEqual(
            tvd,
            self.tolerance,  
            f"TVD too large: {tvd:.4f}, decomposition does not match original RPauli gate"
        )

    def test_rpauli_vs_manual(self):
            # Circuit using RPauli("IXYZ", π)
            theta = pi
            c_rpauli = Circuit()
            c_rpauli.push(RPauli(PauliString("IXYZ"), theta), 1, 2, 3, 4)
            c_rpauli.push(Measure(), 1, 1)
            c_rpauli.push(Measure(), 2, 2)
            c_rpauli.push(Measure(), 3, 3)
            c_rpauli.push(Measure(), 4, 4)

            # Manually decomposed equivalent circuit
            c_manual = Circuit()
            c_manual.push(GateH(), 2)
            c_manual.push(GateHYZ(), 3)
            c_manual.push(GateCX(), 2, 4)
            c_manual.push(GateCX(), 3, 4)
            c_manual.push(GateRZ(theta), 4)
            c_manual.push(GateCX(), 3, 4)
            c_manual.push(GateCX(), 2, 4)
            c_manual.push(GateHYZ(), 3)
            c_manual.push(GateH(), 2)
            c_manual.push(Measure(), 1, 1)
            c_manual.push(Measure(), 2, 2)
            c_manual.push(Measure(), 3, 3)
            c_manual.push(Measure(), 4, 4)

            # Execute both circuits
            result_rpauli = self.processor.execute(c_rpauli, nsamples=self.nsamples, seed=self.seed)
            result_manual = self.processor.execute(c_manual, nsamples=self.nsamples, seed=self.seed)

            # Compare output distributions
            dist_rpauli = self.get_distribution(result_rpauli.cstates)
            dist_manual = self.get_distribution(result_manual.cstates)
            tvd = self.total_variation_distance(dist_rpauli, dist_manual)

            print(f"[DEBUG] RPauli dist: {dist_rpauli}")
            print(f"[DEBUG] Manual dist: {dist_manual}")
            print(f"[DEBUG] TVD = {tvd}")

            self.assertLessEqual(
                tvd,
                self.tolerance,
                f"TVD too large: {tvd:.4f}, decomposed circuit does not match original RPauli circuit"
            )
    def test_rpauli_invalid_string(self):
        with self.assertRaises(ValueError):
            RPauli(PauliString("IXYZK"), pi)

    def test_rpauli_evaluate_then_decompose_consistency(self):

        x = symbols("x")
        p1 = PauliString("XYZ")
        p2 = PauliString("X")

        # Original circuit with symbolic and constant RPauli gates
        c = Circuit()
        c.push(RPauli(p1, pi), 0, 1, 2)
        c.push(RPauli(p2, x), 0)

        # Evaluate symbolic parameter
        c_eval = c.evaluate({x: 0.128})

        # Decompose after evaluation
        c_decomp = c_eval.decompose()

        # Execute both
        result_eval = self.processor.execute(c_eval, nsamples=self.nsamples, seed=self.seed)
        result_decomp = self.processor.execute(c_decomp, nsamples=self.nsamples, seed=self.seed)

        # Get distributions
        dist_eval = self.get_distribution(result_eval.cstates)
        dist_decomp = self.get_distribution(result_decomp.cstates)

        # Compute TVD
        tvd = self.total_variation_distance(dist_eval, dist_decomp)
        print(f"[DEBUG] TVD = {tvd}")
        print(f"[DEBUG] dist_eval = {dist_eval}")
        print(f"[DEBUG] dist_decomp = {dist_decomp}")

        self.assertLessEqual(
            tvd,
            self.tolerance,
            f"TVD too large after evaluating and decomposing RPauli: {tvd:.4f}"
        )

if __name__ == "__main__":
    unittest.main()
