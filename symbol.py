#from sympy import simplify, symbols, floor, Mod
#from sympy.functions import Abs
from z3 import *
from functools import wraps
def binaryOperatorWithIMM(method):
    def new_method(self, other):
        if isInt(self) and isInt(other):
            return method(self, other)
        if isInt(self):
            self = Symbol(self, other.size)
        if isInt(other):
            other = Symbol(other, self.size)

        retv = method(self, other)
        #retv.simplify()
        return retv
    return new_method
class Symbol(object):
    def __init__(self, name, size = 0):
        if isInt(name) and size != 0:
            self.symbol = name & ((1<<size) - 1)
            self._size = size
        elif isBitVec(name) and size == 0:
            self.symbol = name
            self._size = name.size()
        elif isBitVec(name) and size != 0:
            self.symbol = Extract(size-1, 0, name)
            self._size = self.symbol.size()
        elif isinstance(name, str) and size != 0:
            self.symbol = BitVec(name, size)
            self._size = size
        else:
            raise Exception("Error")
    def __str__(self):
        if not self.isInt():
            return simplify(self.symbol).__str__()
        else:
            return str(self.symbol)
    size = property(lambda x : x._size)
    def simplify(self):
        self.symbol = simplify(self.symbol)
        return self

    def isInt(self):
        return isinstance(self.symbol, int) or isinstance(self.symbol, long)
    def __eq__(self, other):
        if not isinstance(other, Symbol):
            r = other
        else:
            r = other.symbol
        return str(simplify(self.symbol == r)) == "True"
    def __neq__(self, other):
        return not self.__eq__(other)
    @binaryOperatorWithIMM
    def __xor__(self, other):
        retv = Symbol(self.symbol ^ other.symbol)
        return retv
    @binaryOperatorWithIMM
    def __rxor__(self, other):
        retv = Symbol(self.symbol ^ other.symbol)
        return retv

    @binaryOperatorWithIMM
    def __or__(self, other):
        retv = Symbol(self.symbol | other.symbol)
        return retv
    @binaryOperatorWithIMM
    def __ror__(self, other):
        retv = Symbol(self.symbol | other.symbol)
        return retv

    @binaryOperatorWithIMM
    def __and__(self, other):
        #if other.isInt() and (1<<self.size) -1 == other.symbol:
        #    return Symbol(self.symbol)
        #if other.isInt() and bin(other.symbol + 1).count("1") == 1:
        #    return Symbol(self.symbol % (other.symbol + 1))
        retv = Symbol(self.symbol & other.symbol)
        return retv
    @binaryOperatorWithIMM
    def __rand__(self, other):
        #if self.isInt() and (1<<other.size) -1 == self.symbol:
        #    return Symbol(other.symbol)
        #if self.isInt() and bin(self.symbol + 1).count("1") == 1:
        #    return Symbol(other.symbol % (self.symbol + 1))
        retv = Symbol(self.symbol & other.symbol)
        return retv

    @binaryOperatorWithIMM
    def __rshift__(self, other):
        retv = Symbol(LShR(self.symbol , other.symbol))
        return retv
    @binaryOperatorWithIMM
    def __rrshift__(self, other):
        retv = Symbol(LShR(self.symbol , other.symbol))
        return retv

    @binaryOperatorWithIMM
    def __lshift__(self, other):
        retv = Symbol(self.symbol << other.symbol)
        return retv
    @binaryOperatorWithIMM
    def __rlshift__(self, other):
        retv = Symbol(other.symbol << self.symbol)
        return retv

    @binaryOperatorWithIMM
    def __add__(self, other):
        retv = Symbol(self.symbol + other.symbol)
        return retv
    @binaryOperatorWithIMM
    def __radd__(self, other):
        retv = Symbol(self.symbol + other.symbol)
        return retv


    @binaryOperatorWithIMM
    def __sub__(self, other):
        retv = Symbol(self.symbol - other.symbol)
        return retv
    @binaryOperatorWithIMM
    def __rsub__(self, other):
        retv = Symbol(other.symbol - self.symbol)
        return retv


    @binaryOperatorWithIMM
    def __mul__(self, other):
        retv = Symbol(self.symbol * other.symbol)
        return retv
    @binaryOperatorWithIMM
    def __rmul__(self, other):
        retv = Symbol(self.symbol * other.symbol)
        return retv

    @binaryOperatorWithIMM
    def __div__(self, other):
        if other.isInt() and (2 << self.size) <= other.symbol:
            return Symbol(0)
        retv = Symbol(self.symbol/ other.symbol)
        #retv = Symbol((self.symbol - self.symbol % other.symbol )/ other.symbol)
        return retv
    @binaryOperatorWithIMM
    def __rdiv__(self, other):
        if self.isInt() and (2 << other.size) <= self.symbol:
            return Symbol(0)
        retv = Symbol(other.symbol/ self.symbol)
        #retv = Symbol((other.symbol - other.symbol % self.symbol )/ self.symbol)
        return retv
    @binaryOperatorWithIMM
    def __truediv__(self, other):
        if other.isInt() and (2 << self.size) <= other.symbol:
            return Symbol(0)
        retv = Symbol(self.symbol/ other.symbol)
        #retv = Symbol((self.symbol - self.symbol % other.symbol )/ other.symbol)
        return retv
    @binaryOperatorWithIMM
    def __rtruediv__(self, other):
        if self.isInt() and (2 << other.size) <= self.symbol:
            return Symbol(0)
        retv = Symbol(other.symbol/ self.symbol)
        #retv = Symbol((other.symbol - other.symbol % self.symbol )/ self.symbol)
        return retv

    @binaryOperatorWithIMM
    def __mod__(self, other):
        retv = Symbol(self.symbol % other.symbol)
        return retv
    @binaryOperatorWithIMM
    def __rmod__(self, other):
        retv = Symbol(self.symbol % other.symbol)
        return retv


    @binaryOperatorWithIMM
    def __pow__(self, other):
        retv = Symbol(self.symbol ** other.symbol)
        return retv
    @binaryOperatorWithIMM
    def __rpow__(self, other):
        retv = Symbol(other.symbol ** self.symbol)
        return retv

def intToBitVec(n, size):
    a = BitVec("QWERTYUIDSFHJKCVBNMRTYUCVRFVTGBUJMUJMDVHDFVBCV", size)
    return simplify(a^a + n)

def isInt(self):
    return isinstance(self, int) or isinstance(self, long)

def isBitVec(o):
    return isinstance(o, BitVecRef)
def _CONCAT(size, args):
    a = map(lambda x: x.symbol & ((1<<size)-1) if not isInt(x) else intToBitVec(x, size), args)
    symbol = reduce(Concat, a)
    retv = Symbol(symbol)
    return retv
def CONCAT(size, *args):
    assert len(args) > 0
    if isinstance(args[0], list) and len(args) == 1:
        return _CONCAT(size, args[0])
    else:
        return _CONCAT(size, args)


def EXTRACT(s, offset, size):
    if isinstance(s, Symbol):
        retv = Symbol(Extract(offset + size - 1, offset, s.symbol) )
        return retv
    if isInt(s):
        return (s>>offset)&((1<<size)-1)
    raise Exception("!@#$")

def ZEXTEND(s, size):
    if isinstance(s, Symbol):
        assert s.size <= size
        if s.size != size:
            return Symbol(Concat(intToBitVec(0, size - s.size), s.symbol))
        return s
    assert False

#TODO
def SEXTEND(s, old_size, size):
    assert old_size <= size
    if isinstance(s, Symbol):
        assert s.size == old_size
        if old_size == size:
            return s
        if not s.isInt():
            signbit = EXTRACT(s, old_size-1, 1)
            signbits = CONCAT(1, [signbit for x in range(size - old_size)])
            if s.size != size:
                return Symbol(Concat(signbits.symbol, s.symbol))
            return s
        else:
            retv = Symbol(s.symbol, size)
            retv.symbol = SEXTEND(retv.symbol, old_size, size)
            return retv
    if isInt(s):
        if s < 0:
            return s
        if s >= ((1 << (old_size-1)) - 1):
            s |= ((1 << (size)) - (1 << old_size))
            return s
        return s
    print type(s)
    print s
    assert False
  

@binaryOperatorWithIMM
def UDIV(a, b):
    retv = Symbol(UDiv(a, b))
    """
    retv.size = max(a.size, b.size)"""
    return retv

@binaryOperatorWithIMM
def UREM(a, b):
    retv = Symbol(URem(a, b))
    """
    retv.size = max(a.size, b.size)"""
    return retv

def chr(c):
    if isinstance(c, Symbol):
        if c.size >= 8:
            return EXTRACT(c, 0, 8) & 0xff
    return c &0xff
def ord(c):
    return c

if __name__ == "__main__":
    a = BitVec("a", 32)
    print type(BitVec)
    print simplify(Concat(a^a, a, a^a, 1))
    print Concat(a^a, a).size()
    print a.size
    pass
