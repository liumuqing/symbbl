from pysymemu.smtlibv2 import BitVec, EXTRACT, proved, CONCAT
#from z3 import Array, Update
import z3

class MemoryException(Exception):
    '''
    Memory exceptions
    '''
    def __init__(self, cause, address=0):
        '''
        Builds a memory exception.
        @param cause: exception message.
        @param address: memory address where the exception occurred.
        '''
        super(MemoryException, self, ).__init__("%s <0x%08x>"%(cause, address))

class InstMemory(object):
    def __init__(self):
        self.data = {}
    def putchar(self, addr, data):
        self.data[addr] = data
    def fetchchar(self, addr):
        retv = self.data.get(addr)
        if retv == None:
            raise MemoryException("Can not asscess InstMem", addr)
        return retv

class ByteArray(object):
    def __init__(self, name, addressSize):
        assert addressSize in [32, 64]
        self._data = z3.Array(name, z3.BitVecSort(addressSize), z3.BitVecSort(8))
        self._addressSize = addressSize
    def get(self, addr):
        return self._data[addr]
    def put(self, addr, value):
        if isinstance(addr, int) or isinstance(addr, long):
            self._data = z3.Update(self._data, z3.BitVecVal(self._addressSize, addr), value)
        else:
            self._data = z3.Update(self._data, addr, value)




class DataMemory(object):
    def __init__(self, addrSize):
        self.data = ByteArray("Mem", addrSize)
        self.read_records = set()
        self.write_records = set()

    def putchar(self, addr, data):
        addr.simplify()
        _addr = addr.symbol
        if isinstance(data, BitVec):
            data.simplify()
            _data = data.symbol
        else:
            _data = data
        self.data.put(_addr, _data)

    def getchar(self, addr):
        addr.simplify()
        return BitVec(self.data.get(addr.symbol)) & 0xff

    def load(self, addr, sizeOfBit):
        sizeOfByte = sizeOfBit / 8
        retv = CONCAT(8, *[self.getchar(addr+i) for i in reversed(range(0, sizeOfByte))])
        return retv

    def store(self, addr, data, sizeOfBit):
        self.write_records.add((addr, sizeOfBit))
        sizeOfByte = sizeOfBit/8
        for k in range(sizeOfByte):
            self.putchar(addr+k,  EXTRACT(data, k*8, 8))






