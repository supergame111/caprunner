import unittest

from caprunner.interpreter import JavaCardVM

class TestOpcodes(unittest.TestCase):

    def _teststack(self, opcode, params, init, expected):
        vm = JavaCardVM(None)
        vm.frame.stack = init
        f = getattr(vm, opcode)
        f(*params)
        self.assertEquals(vm.frame.stack, expected)

    def test_swap_x(self):
        self._teststack('swap_x', [0x11], [0,1,2,3,4,5,6,7,8], [0,1,2,3,4,5,6,8,7])
        self._teststack('swap_x', [0x43], [0,1,2,3,4,5,6,7,8], [0,1,5,6,7,8,2,3,4])
        self._teststack('swap_x', [0x13], [0,1,2,3,4,5,6,7,8], [0,1,2,3,4,8,5,6,7])

    def test_dup(self):
        self._teststack('dup', [], [0,1,2], [0,1,2,2])

    def test_dup2(self):
        self._teststack('dup2', [], [2,3,4], [2,3,4,3,4])

    def test_dup_x(self):
        self._teststack('dup_x', [0x12], [0,1,2,3,4,5,6,7,8], [0,1,2,3,4,5,6,8,7,8])
        self._teststack('dup_x', [0x48], [0,1,2,3,4,5,6,7,8], [0,5,6,7,8,1,2,3,4,5,6,7,8])
        self._teststack('dup_x', [0x30], [0,1,2,3,4,5,6,7,8], [0,1,2,3,4,5,6,7,8,6,7,8])

