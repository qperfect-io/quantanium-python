import unittest
from quantanium import *
from mimiqcircuits import *
import mimiqcircuits
import inspect
from random import random


class TestQleo(unittest.TestCase):

    def setUp(self):
        self.c = Circuit()
        self.sim = Qleo()

    def test_one_qubit_gates(self):

        gates = mimiqcircuits.GATES.list()
        for oper in gates:
            if issubclass(oper, mimiqcircuits.Operation):
                nb_params = len(inspect.signature(oper).parameters)
                if nb_params == 0 and oper().num_qubits == 1 and oper().num_bits == 0 and oper().num_zvars == 0:
                    self.c.push(oper(), 0)

        c_inv = inverse(self.c)
        self.c.append(c_inv)

        res = self.sim.execute(self.c)
        self.assertEqual(len(res.histogram().keys()), 1)
        self.assertEqual(res.cstates[0].tolist(), [0])

    def test_non_parametric_gates(self):
        """This test will apply all single qubit gates and multi qubits gates excluding the parametric gates to one circuit, append its inverse and attempt at getting back the original 0 state
        """
        # TODO: check CSWAP et GateSC?

        max_qubits = 0
        # get the list of all gates available in imiqcircuits
        gates = mimiqcircuits.GATES.list()

        # The next loop is going to iterate over all the possible gates and add to the circuit all the non prametric gates
        for oper in gates:
            # Check type of operation
            if issubclass(oper, mimiqcircuits.Operation):
                # Check the number of expected args to filter parametric gates
                nb_params = len(inspect.signature(oper).parameters)
                if nb_params == 0 and oper().num_bits == 0 and oper().num_zvars == 0 and "CSWAP" not in oper.__name__ and "GateCS" not in oper.__name__:
                    max_qubits = max(max_qubits, oper().num_qubits)
                    # push gate to circuit with the expected number of args
                    self.c.push(oper(), *range(0, oper().num_qubits))

        c_inv = inverse(self.c)
        self.c.append(c_inv)

        res = self.sim.execute(self.c)
        self.assertEqual(len(res.histogram().keys()), 1)
        self.assertEqual(res.cstates[0].tolist(), [
                         0 for _ in range(max_qubits)])

    def test_rotation_gates(self):
        """This test will apply all rotation gates
        """

        # TODO: add controlled rotation gates
        max_qubits = 0

        # get the list of all gates available in imiqcircuits
        gates = mimiqcircuits.GATES.list()[1:]
        # The next loop is going to iterate over all the possible gates and add to the circuit all the rotation gates
        for oper in gates:
            # Check type of operation
            if issubclass(oper, mimiqcircuits.Operation) and "R" in oper.__name__ and "CR" not in oper.__name__:
                # Check the number of expected args to filter parametric gates
                nb_params = len(inspect.signature(oper).parameters)
                args = [random() for _ in range(nb_params)]
                op = oper(*args)
                if nb_params != 0 and op.num_bits == 0 and op.num_zvars == 0:
                    max_qubits = max(max_qubits, op.num_qubits)
                    # push gate to circuit with the expected number of args
                    self.c.push(op, *range(0, op.num_qubits))

        c_inv = inverse(self.c)
        self.c.append(c_inv)

        res = self.sim.execute(self.c)
        self.assertEqual(len(res.histogram().keys()), 1)
        self.assertEqual(res.cstates[0].tolist(), [
                         0 for _ in range(max_qubits)])


if __name__ == '__main__':
    unittest.main()
