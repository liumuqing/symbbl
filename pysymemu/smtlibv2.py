import z3
import os

class Symbol(object):
    def __init__(self, name, size = 0):
        raise Exception("Symbol is a virtual class")

    def __str__(self):
        self.simplify()
        return str(self.symbol)

    size = property(lambda x : x.symbol.size())

    def simplify(self):
        self.symbol = z3.simplify(self.symbol, elim_sign_ext = False)
        self._simplified = True
        return self

def binaryBoolOperatorWithIMM(method):
    def new_method(self, other):
        if isinstance(self, bool) and isinstance(other, bool):
            raise Exception("Error!")
        elif isinstance(self, bool) and isinstance(other, Bool):
            self = Bool(self)
        elif isinstance(self, Bool) and isinstance(other, bool):
            other = Bool(other)
        retv = method(self, other)
        return retv
    return new_method
class Bool(Symbol):
    def __init__(self, name):
        self._simplified = False
        if isinstance(name, Bool):
            self.symbol = name.symbol
        elif isinstance(name, bool):
            self.symbol = z3.BoolVal(name)
        elif isinstance(name, str):
            self.symbol = z3.Bool(name)
        elif isinstance(name, z3.BoolRef):
            self.symbol = name
        else:
            raise Exception("Error")
    def simplify(self):
        super(Bool, self).simplify()
        if proved(Bool(self)):
            self.symbol = z3.BoolVal(True)
        elif proved(Bool(self.symbol == False)):
            self.symbol = z3.BoolVal(False)
        self._simplified = True
        return self
    
    @binaryBoolOperatorWithIMM
    def __and__(self, other):
        return Bool(z3.And(self.symbol, other.symbol))
    @binaryBoolOperatorWithIMM
    def __rand__(self, other):
        return Bool(z3.And(other.symbol, self.symbol))

    @binaryBoolOperatorWithIMM
    def __or__(self, other):
        return Bool(z3.Or(self.symbol, other.symbol))
    @binaryBoolOperatorWithIMM
    def __ror__(self, other):
        return Bool(z3.Or(other.symbol, self.symbol))


    @binaryBoolOperatorWithIMM
    def __xor__(self, other):
        return Bool(z3.Xor(self.symbol, other.symbol))
    @binaryBoolOperatorWithIMM
    def __rxor__(self, other):
        return Bool(z3.Xor(self.symbol, other.symbol))

def binaryBitVecOperatorWithIMM(method):
    def new_method(self, other):
        if isInt(self) and isInt(other):
            raise Exception("Error!")
        elif isInt(self) and not isInt(other):
            self = BitVec(self, other.size)
        elif isInt(other) and not isInt(self):
            other = BitVec(other, self.size)
        retv = method(self, other)
        return retv
    return new_method
class BitVec(Symbol):
    def __init__(self, name, size = 0):
        self._simplified = False
        if isInt(name) and size != 0:
            self.symbol = z3.BitVecVal(name, size)
        elif isBitVec(name) and size == 0:
            self.symbol = name
            self.simplify()
        elif isBitVec(name) and size != 0:
            self.symbol = z3.Extract(size-1, 0, name)
            self.simplify()
        elif isinstance(name, str) and size != 0:
            self.symbol = z3.BitVec(name, size)
        else:
            raise Exception("Error")

    @binaryBitVecOperatorWithIMM
    def __xor__(self, other):
        retv = BitVec(self.symbol ^ other.symbol)
        return retv
    @binaryBitVecOperatorWithIMM
    def __rxor__(self, other):
        retv = BitVec(self.symbol ^ other.symbol)
        return retv

    @binaryBitVecOperatorWithIMM
    def __or__(self, other):
        retv = BitVec(self.symbol | other.symbol)
        return retv
    @binaryBitVecOperatorWithIMM
    def __ror__(self, other):
        retv = BitVec(self.symbol | other.symbol)
        return retv

    @binaryBitVecOperatorWithIMM
    def __and__(self, other):
        #if other.isInt() and (1<<self.size) -1 == other.symbol:
        #    return Symbol(self.symbol)
        #if other.isInt() and bin(other.symbol + 1).count("1") == 1:
        #    return Symbol(self.symbol % (other.symbol + 1))
        retv = BitVec(self.symbol & other.symbol)
        return retv
    @binaryBitVecOperatorWithIMM
    def __rand__(self, other):
        #if self.isInt() and (1<<other.size) -1 == self.symbol:
        #    return Symbol(other.symbol)
        #if self.isInt() and bin(self.symbol + 1).count("1") == 1:
        #    return Symbol(other.symbol % (self.symbol + 1))
        retv = BitVec(self.symbol & other.symbol)
        return retv

    @binaryBitVecOperatorWithIMM
    def __rshift__(self, other):
        retv = BitVec(z3.LShR(self.symbol , other.symbol))
        return retv
    @binaryBitVecOperatorWithIMM
    def __rrshift__(self, other):
        retv = BitVec(z3.LShR(self.symbol , other.symbol))
        return retv

    @binaryBitVecOperatorWithIMM
    def __lshift__(self, other):
        retv = BitVec(self.symbol << other.symbol)
        return retv
    @binaryBitVecOperatorWithIMM
    def __rlshift__(self, other):
        retv = BitVec(other.symbol << self.symbol)
        return retv

    @binaryBitVecOperatorWithIMM
    def __add__(self, other):
        retv = BitVec(self.symbol + other.symbol)
        return retv
    @binaryBitVecOperatorWithIMM
    def __radd__(self, other):
        retv = BitVec(self.symbol + other.symbol)
        return retv


    @binaryBitVecOperatorWithIMM
    def __sub__(self, other):
        retv = BitVec(self.symbol - other.symbol)
        return retv
    @binaryBitVecOperatorWithIMM
    def __rsub__(self, other):
        retv = BitVec(other.symbol - self.symbol)
        return retv


    @binaryBitVecOperatorWithIMM
    def __mul__(self, other):
        retv = BitVec(self.symbol * other.symbol)
        return retv
    @binaryBitVecOperatorWithIMM
    def __rmul__(self, other):
        retv = BitVec(self.symbol * other.symbol)
        return retv

    @binaryBitVecOperatorWithIMM
    def __div__(self, other):
        retv = BitVec(self.symbol/ other.symbol)
        #retv = Symbol((self.symbol - self.symbol % other.symbol )/ other.symbol)
        return retv
    @binaryBitVecOperatorWithIMM
    def __rdiv__(self, other):
        retv = BitVec(other.symbol/ self.symbol)
        #retv = Symbol((other.symbol - other.symbol % self.symbol )/ self.symbol)
        return retv
    @binaryBitVecOperatorWithIMM
    def __truediv__(self, other):
        retv = BitVec(self.symbol/ other.symbol)
        #retv = Symbol((self.symbol - self.symbol % other.symbol )/ other.symbol)
        return retv
    @binaryBitVecOperatorWithIMM
    def __rtruediv__(self, other):
        retv = BitVec(other.symbol/ self.symbol)
        #retv = Symbol((other.symbol - other.symbol % self.symbol )/ self.symbol)
        return retv

    @binaryBitVecOperatorWithIMM
    def __mod__(self, other):
        retv = BitVec(self.symbol % other.symbol)
        return retv
    @binaryBitVecOperatorWithIMM
    def __rmod__(self, other):
        retv = BitVec(self.symbol % other.symbol)
        return retv


    @binaryBitVecOperatorWithIMM
    def __pow__(self, other):
        retv = BitVec(self.symbol ** other.symbol)
        return retv
    @binaryBitVecOperatorWithIMM
    def __rpow__(self, other):
        retv = BitVec(other.symbol ** self.symbol)
        return retv

    @binaryBitVecOperatorWithIMM
    def __lt__(self, other):
        return Bool(self.symbol < other.symbol)

    @binaryBitVecOperatorWithIMM
    def __le__(self, other):
        return Bool(self.symbol <= other.symbol)

    @binaryBitVecOperatorWithIMM
    def __gt__(self, other):
        return Bool(self.symbol > other.symbol)

    @binaryBitVecOperatorWithIMM
    def __ge__(self, other):
        return Bool(self.symbol >= other.symbol)

    @binaryBitVecOperatorWithIMM
    def __eq__(self, other):
        return Bool(self.symbol == other.symbol)

    @binaryBitVecOperatorWithIMM
    def __ne__(self, other):
        return Bool(self.symbol != other.symbol)
    
    @binaryBitVecOperatorWithIMM
    def ult(self, other):
        return Bool(z3.ULT(self.symbol, other.symbol))

    @binaryBitVecOperatorWithIMM
    def ule(self, other):
        return Bool(z3.ULE(self.symbol, other.symbol))

    @binaryBitVecOperatorWithIMM
    def ugt(self, other):
        return Bool(z3.UGT(self.symbol, other.symbol))

    @binaryBitVecOperatorWithIMM
    def uge(self, other):
        return Bool(z3.UGE(self.symbol, other.symbol))

def isInt(self):
    return isinstance(self, int) or isinstance(self, long)

def isBitVec(o):
    return isinstance(o, z3.BitVecRef)
def _CONCAT(size, args):
    a = map(lambda x: x.symbol & ((1<<size)-1) if not isInt(x) else z3.BitVecVal(x, size), args)
    symbol = reduce(z3.Concat, a)
    retv = BitVec(symbol)
    return retv.simplify()

def CONCAT(size, *args):
    assert len(args) > 0
    if isinstance(args[0], list) and len(args) == 1:
        return _CONCAT(size, args[0]).simplify()
    else:
        return _CONCAT(size, args).simplify()


def EXTRACT(s, offset, size):
    if isinstance(s, Symbol):
        retv = BitVec(z3.Extract(offset + size - 1, offset, s.symbol) )
        return retv.simplify()
    if isInt(s):
        return (s>>offset)&((1<<size)-1)
    raise Exception("!@#$")

def ZEXTEND(s, size):
    if isinstance(s, Symbol):
        assert s.size <= size
        if s.size != size:
            return BitVec(z3.Concat(z3.BitVecVal(0, size - s.size), s.symbol))
        return s.simplify()
    if isInt(s):
        return s
    assert False

#TODO
def SEXTEND(s, old_size, size):
    assert old_size <= size
    if isinstance(s, Symbol):
        assert s.size == old_size
        if old_size != size:
            retv =  BitVec(z3.SignExt(size - old_size, s.symbol))
            assert retv.size == size
            return retv.simplify()
        return s
    if isInt(s):
        if s < 0:
            return s
        if s & (1 << (old_size-1)):
            s |= ((1 << (size)) - (1 << old_size))
            return s
        return s
    assert False
  

@binaryBitVecOperatorWithIMM
def _UDIV(a, b):
    retv = BitVec(UDiv(a, b))
    return retv.simplify()
def UDIV(a, b):
    if isInt(a) and isInt(b):
        return a / b
    else:
        return _UDIV(a, b)

@binaryBitVecOperatorWithIMM
def _UREM(a, b):
    retv = BitVec(URem(a, b))
    return retv.simplify()
def UREM(a, b):
    if isInt(a) and isInt(b):
        return a % b
    else:
        return _UREM(a, b)

def OR(a, b):
    return a | b
def AND(a, b):
    return a & b

def ITEBV(size, cond, true, false):
    if type(cond) in (int, long, bool):
        return true if cond else false
    assert isinstance(cond, Bool)
    if isinstance(true, Bool):
        true = true.symbol
    if isInt(true):
        true = BitVec(true, size).symbol
    if isinstance(false, Bool):
        false = false.symbol
    if isInt(false):
        false = BitVec(false, size).symbol

    return BitVec(z3.If(cond.symbol, true&((1<<size)-1), false&((1<<size)-1)), size)

def ULT(a, b):
    return {  (int, int): lambda : a < b if a>=0 and b>=0 else None,
              (long, int): lambda : a < b if a>=0 and b>=0 else None,
              (int, long): lambda : a < b if a>=0 and b>=0 else None,
              (long,long): lambda : a < b if a>=0 and b>=0 else None,
              (BitVec, int): lambda : a.ult(b),
              (BitVec, long): lambda : a.ult(b),
              (int, BitVec): lambda : b.uge(a) == False,
              (long, BitVec): lambda : b.uge(a) == False,
              (BitVec,BitVec): lambda : a.ult(b),
            }[(type(a),type(b))]()

def ULE(a, b):
    return {  (int, int): lambda : a <= b if a>=0 and b>=0 else None,
              (long, int): lambda : a <= b if a>=0 and b>=0 else None,
              (int, long): lambda : a <= b if a>=0 and b>=0 else None,
              (long,long): lambda : a <= b if a>=0 and b>=0 else None,
              (BitVec, int): lambda : a.ule(b),
              (BitVec, long): lambda : a.ule(b),
              (int, BitVec): lambda : b.ugt(a) == False,
              (long, BitVec): lambda : b.ugt(a) == False,
              (BitVec,BitVec): lambda : a.ule(b),
            }[(type(a),type(b))]()

def UGT(a, b):
    return {  (int, int): lambda : a > b if a>=0 and b>=0 else None,
              (long, int): lambda : a > b if a>=0 and b>=0 else None,
              (int, long): lambda : a > b if a>=0 and b>=0 else None,
              (long,long): lambda : a > b if a>=0 and b>=0 else None,
              (BitVec, int): lambda : a.ugt(b),
              (int, BitVec): lambda : b.ule(a) == False,
              (BitVec, long): lambda : a.ugt(b),
              (long, BitVec): lambda : b.ule(a) == False,
              (BitVec, BitVec): lambda : a.ugt(b),
            }[(type(a),type(b))]()

def UGE(a, b):
    return {  (int, int): lambda : a >= b if a>=0 and b>=0 else None,
              (long, int): lambda : a >= b if a>=0 and b>=0 else None,
              (int, long): lambda : a >= b if a>=0 and b>=0 else None,
              (long,long): lambda : a >= b if a>=0 and b>=0 else None,
              (BitVec, int): lambda : a.uge(b),
              (BitVec, long): lambda : a.uge(b),
              (int, BitVec): lambda : b.ult(a) == False,
              (long, BitVec): lambda : b.ult(a) == False,
              (BitVec,BitVec): lambda : a.uge(b),
            }[(type(a),type(b))]()

def chr(c):
    if isinstance(c, Symbol):
        if c.size >= 8:
            return EXTRACT(c, 0, 8)
    return c &0xff
def ord(c):
    return c

def proved(arg):
    if isinstance(arg, bool):
        return arg
    assert isinstance(arg, Bool)
    s = z3.Solver()
    s.add(z3.Not(arg.symbol))
    r = s.check()
    if r == z3.unsat:
        return True
    return False

def issymbolic(s):
    return isinstance(s, Symbol)
def isconcrete(s):
    return not issymbolic(s)

class Array(object):
    pass

def getallvalues(x):
    retv = []
    #TODO: use a different name
    s = z3.BitVec("PC", x.size)
    solver = z3.Solver()
    solver.add(s == x.symbol)
    while solver.check() == z3.sat:
        m = solver.model()
        v = m[s]
        retv.append(int(str(v)))
        solver.add(s != v)
    return retv

if __name__ == "__main__":
    a = z3.BitVec("a", 32)
    print type(z3.BitVec)
    print z3.simplify(z3.Concat(a^a, a, a^a, 1))
    print z3.Concat(a^a, a).size()
    print a.size
    pass
