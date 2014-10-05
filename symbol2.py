#from sympy import simplify, symbols, floor, Mod
#from sympy.functions import Abs
from z3 import *
from functools import wraps
"""
def binaryOperator(method):
    def new_method(self, other):
        if not isinstance(other, Symbol):
            other = Symbol(other)
        retv = method(self, other)
        if retv.isInt():
            return retv
        retv.size = max(self.size, other.size)
        retv.symbol = simplify(retv.symbol)
        return retv
    return new_method
class Symbol(object):
    def __init__(self, name, size = 0):
        if size != 0:
            self.symbol = BitVec(name, size)
        else:
            self.symbol = name
            if self.isInt():
                while 2**self.size <= abs(self.symbol):
                    self.size += 1
    def __str__(self):
        if not self.isInt():
            return simplify(self.symbol).__str__()
        else:
            return str(self.symbol)
    size = property(lambda self:self.symbol.size(), lambda raise Exception("Symbol Cannnot set size"))    
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
        if isinstance(self.symbol == r, bool):
            return self.symbol == r
        return False
    def __neq__(self, other):
        return not self.__eq__(other)
    @binaryOperator
    def __xor__(self, other):
        retv = Symbol(self.symbol ^ other.symbol)
        return retv
    @binaryOperator
    def __rxor__(self, other):
        retv = Symbol(self.symbol ^ other.symbol)
        return retv

    @binaryOperator
    def __or__(self, other):
        retv = Symbol(self.symbol | other.symbol)
        return retv
    @binaryOperator
    def __ror__(self, other):
        retv = Symbol(self.symbol | other.symbol)
        return retv

    @binaryOperator
    def __and__(self, other):
        #if other.isInt() and (1<<self.size) -1 == other.symbol:
        #    return Symbol(self.symbol)
        #if other.isInt() and bin(other.symbol + 1).count("1") == 1:
        #    return Symbol(self.symbol % (other.symbol + 1))
        retv = Symbol(self.symbol & other.symbol)
        return retv
    @binaryOperator
    def __rand__(self, other):
        #if self.isInt() and (1<<other.size) -1 == self.symbol:
        #    return Symbol(other.symbol)
        #if self.isInt() and bin(self.symbol + 1).count("1") == 1:
        #    return Symbol(other.symbol % (self.symbol + 1))
        retv = Symbol(self.symbol & other.symbol)
        return retv

    @binaryOperator
    def __rshift__(self, other):
        retv = Symbol(self.symbol >> other.symbol)
        return retv
    @binaryOperator
    def __rrshift__(self, other):
        retv = Symbol(other.symbol >> self.symbol)
        return retv

    @binaryOperator
    def __lshift__(self, other):
        retv = Symbol(self.symbol << other.symbol)
        return retv
    @binaryOperator
    def __rlshift__(self, other):
        retv = Symbol(other.symbol << self.symbol)
        return retv

    @binaryOperator
    def __add__(self, other):
        retv = Symbol(self.symbol + other.symbol)
        return retv
    @binaryOperator
    def __radd__(self, other):
        retv = Symbol(self.symbol + other.symbol)
        return retv


    @binaryOperator
    def __sub__(self, other):
        retv = Symbol(self.symbol - other.symbol)
        return retv
    @binaryOperator
    def __rsub__(self, other):
        retv = Symbol(other.symbol - self.symbol)
        return retv


    @binaryOperator
    def __mul__(self, other):
        retv = Symbol(self.symbol * other.symbol)
        return retv
    @binaryOperator
    def __rmul__(self, other):
        retv = Symbol(self.symbol * other.symbol)
        return retv

    @binaryOperator
    def __div__(self, other):
        if other.isInt() and (2 << self.size) <= other.symbol:
            return Symbol(0)
        retv = Symbol(self.symbol/ other.symbol)
        #retv = Symbol((self.symbol - self.symbol % other.symbol )/ other.symbol)
        return retv
    @binaryOperator
    def __rdiv__(self, other):
        if self.isInt() and (2 << other.size) <= self.symbol:
            return Symbol(0)
        retv = Symbol(other.symbol/ self.symbol)
        #retv = Symbol((other.symbol - other.symbol % self.symbol )/ self.symbol)
        return retv
    @binaryOperator
    def __truediv__(self, other):
        if other.isInt() and (2 << self.size) <= other.symbol:
            return Symbol(0)
        retv = Symbol(self.symbol/ other.symbol)
        #retv = Symbol((self.symbol - self.symbol % other.symbol )/ other.symbol)
        return retv
    @binaryOperator
    def __rtruediv__(self, other):
        if self.isInt() and (2 << other.size) <= self.symbol:
            return Symbol(0)
        retv = Symbol(other.symbol/ self.symbol)
        #retv = Symbol((other.symbol - other.symbol % self.symbol )/ self.symbol)
        return retv

    @binaryOperator
    def __mod__(self, other):
        retv = Symbol(self.symbol % other.symbol)
        return retv
    @binaryOperator
    def __rmod__(self, other):
        retv = Symbol(self.symbol % other.symbol)
        return retv


    @binaryOperator
    def __pow__(self, other):
        retv = Symbol(self.symbol ** other.symbol)
        return retv
    @binaryOperator
    def __rpow__(self, other):
        retv = Symbol(other.symbol ** self.symbol)
        return retv

def isInt(self):
    return isinstance(self, int) or isinstance(self, long)
"""

def CONCAT(size, *args):
    a = map(lambda x: x if not isInt(x) else BitVec(size, x))
    symbol = reduce(Concat, a)
    return retv

def EXTRACT(s, offset, size):
    """
    if isinstance(s, Symbol):
        retv = s
        if offset != 0:
            retv >>= offset
        #if s.size != offset + size:
        #    retv &= ((1<<size)-1)
        retv.size = size
        return retv
        """
    return (s>>offset)&((1<<size)-1)

def ZEXTEND(s, size):
    """
    if isinstance(s, Symbol):
        retv = s
        retv.size = size
        return retv
        """
    return s
def SEXTEND(s, old_size, size):
    """
    if isinstance(s, Symbol):
        retv = s
        retv.size = size
        return retv
        """
    return s
def UDIV(a, b):
    retv = Symbol(UDiv(a, b))
    """
    retv.size = max(a.size, b.size)"""
    return retv

def UREM(a, b):
    retv = Symbol(URem(a, b))
    """
    retv.size = max(a.size, b.size)"""
    return retv

def chr(c):
    return c &0xff
def ord(c):
    return c

Symbol = BitVec
if __name__ == "__main__":
    a = BitVec("a", 32)
    print simplify((a|0x1)&0x1 == 1)
    print a.size
    pass
