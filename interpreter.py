import python.lang

import bytecode, utils

class JavaCardStack(list):
    """
    This is the operand stack
    it contains words (short)
    """
    def push_int(self, integer):
        self.push(integer & 0xffff)
        self.push((integer & 0xffff0000) >> 16)

    def pop_int(self):
        return self.pop() | (self.pop() << 16)
    
    # We are a stack after all ...
    push = list.append

class JavaCardLocals(dict):
    """
    The method parameters are the first local variables.
    0 being "self" in the majority of the cases
    Theorically, the number and type of the params is known ...
    The mapping is: index -> value
    """
    def __init__(self, *params):
        for i in xrange(len(params)):
            self[i] = params[i]

    def aget(self, index):
        """ Get an address """
        return self.get(index, None)

    def sget(self, index):
        """ Get a short """
        return self.get(index, 0)

class JavaCardFrame(object):
    """
    A frame has its own local variables, stack, bytecodes
    A frame has its own Exception handlers
    A frame should also have its own context for security purposes.
    We will forget that for the moment
    """
    def __init__(self, params, bytecodes):
        self.bytecodes = bytecodes
        self.stack = JavaCardStack()
        self.locals = JavaCardLocals(*params)
        # Current instruction pointer
        self.ip = 0

    def push(self, val):
        self.stack.push(val)

    def pop(self):
        return self.stack.pop()

    def aget(self, index):
        return self.locals.aget(index)

    def sget(self, index):
        return self.locals.sget(index)

class ExecutionDone(Exception):
    pass

class DummyFrame(object):
    """ 
    The bottom of the frame stack. 
    Only used to get the return value.
    """
    ip = -1
    #stack = []
    def __init__(self):
        self.returnVal = None
    def push(self, val):
        self.returnVal = val
    def getValue(self):
        return self.returnVal

class JavaCardFrames(list):
    """
    This is the frame stack
    """
    def __init__(self):
        self.push(DummyFrame())

    def push(self, frame):
        self.current = frame
        self.append(frame)

    def pop(self):
        """ When we pop a frame, we don't care about the old one """
        list.pop(self)
        self.current = self[-1]

class JavaCardVM(object):
    def __init__(self, resolver):
        self.resolver = resolver
        # Stack of frames
        self.frames = JavaCardFrames()

    @property
    def frame(self):
        """ current frame """
        return self.frames.current

    def step(self):
        code = self.frame.bytecodes[self.frame.ip:]
        print bytecode.opname[code[0]]
        # get the function
        f = getattr(self, bytecode.opname[code[0]])
        # get the params
        len, params = bytecode.getParams(code)
        # execute the function
        inc = f(*params)
        # if we are done
        if isinstance(self.frame, DummyFrame):
            raise ExecutionDone
        # increment IP
        if inc is None:
            # regular function without branching
            inc = len
        self.frame.ip += inc

    def _invokejava(self, method):
        self.frames.append(JavaCardFrame(method))
        self.frame = self.frames[-1]

    def aload_0(self):
        self.aload(0)
    def aload_1(self):
        self.aload(1)
    def aload_2(self):
        self.aload(2)
    def aload_3(self):
        self.aload(3)
    def aload(self, index):
        self.frame.push(self.frame.aget(index))

    def sload_0(self):
        self.sload(0)
    def sload_1(self):
        self.sload(1)
    def sload_2(self):
        self.sload(2)
    def sload_3(self):
        self.sload(3)
    def sload(self, index):
        self.frame.push(self.frame.sget(index))

    def sconst_m1(self):
        self._sconst(-1)
    def sconst_0(self):
        self._sconst(0)
    def sconst_1(self):
        self._sconst(1)
    def sconst_2(self):
        self._sconst(2)
    def sconst_3(self):
        self._sconst(3)
    def sconst_4(self):
        self._sconst(4)
    def sconst_5(self):
        self._sconst(5)
    def _sconst(self, value):
        """ Not to be externaly called """
        self.frame.push(value)

    def srem(self):
        val2 = self.frame.pop()
        val1 = self.frame.pop()
        if val2 == 0:
            raise python.lang.ArithmeticException()
        self.frame.push(val1 - (val1 / val2) * val2)

    def sadd(self):
        val2 = self.frame.pop()
        val1 = self.frame.pop()
        self.frame.push(val1 + val2)

    def bspush(self, byte):
        self.frame.push(byte)

    def s2b(self):
        val = self.frame.pop()
        self.frame.push(val & 0xff)

    def sreturn(self):
        val = self.frame.pop()
        self.frames.pop()
        self.frame.push(val)

    def smul(self):
        val2 = self.frame.pop()
        val1 = self.frame.pop()
        self.frame.push((val1 * val2) & 0xffff)
        
    def ifne(self, branch):
        val = self.frame.pop()
        if val != 0:
            return utils.signed1(branch)

    def if_scmpge(self, branch):
        val2 = self.frame.pop()
        val1 = self.frame.pop()
        if val1 >= val2:
            return utils.signed1(branch)

    def goto(self, branch):
        return utils.signed1(branch)

    def sstore_0(self):
        self.sstore(0)
    def sstore_1(self):
        self.sstore(1)
    def sstore_2(self):
        self.sstore(2)
    def sstore_3(self):
        self.sstore(3)
    def sstore(self, index):
        val = self.frame.pop()
        self.frame.locals[index] = val