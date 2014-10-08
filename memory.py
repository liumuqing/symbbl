from symbol import BitVec, EXTRACT, proved, CONCAT

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

class DataMemory(object):
    def __init__(self):
        self.data = {}
    def putchar(self, addr, data):
        addr.simplify()
        for k in self.data.keys():
            if proved(addr == k[0]):
                self.data.pop(k)
        key = (addr, 1)
        self.data[key] = EXTRACT(data, 0, 8)
    def getchar(self, addr):
        addr.simplify()
        for k in self.data.keys():
            if proved(addr%k[1] == k[0]):
                return EXTRACT((addr - k[0]) * 8, 8, self.data[k])
        retv = BitVec(str("1@[%s]" % addr), 8) # "[%s] % addr" may be a unicode, ...., cast it to str
        self.data[(addr, 1)] = retv
        return retv
    def load(self, addr, sizeOfBit):
        sizeOfByte = sizeOfBit / 8
        assert proved(addr%sizeOfByte == 0)
        for k in self.data.keys():
            if proved(addr == k[0]) and proved(sizeOfByte == k[1]):
                return self.data[k]
            if proved(addr%k[1]  == k[0]) or proved(k[0]%sizeOfByte == addr):
                retv = CONCAT(8, *[self.getchar(addr+i) for i in reversed(range(0, sizeOfByte))])
                return retv
        retv = BitVec((str("%d@[%s]" % (sizeOfByte, addr))), sizeOfBit)
        self.data[(addr, sizeOfByte)] = retv
        return retv
    @staticmethod
    def _addrInRange(addr, start, length):
        if proved(addr < start):
            return -1
        if proved(addr >= start) and proved(addr < start + length):
            return 0
        if proved(addr >= start + length):
            return 1
        assert False
    def store(self, addr, data, sizeOfBit):
        sizeOfByte = sizeOfBit / 8
        #FIXME:something is wrong 
        for k in self.data.keys():
            if proved(addr == k[0]) and proved(sizeOfByte == k[1]):
                self.data.pop(k)
                self.data[(addr, sizeOfByte)] = EXTRACT(data, 0, sizeOfBit)
                return 
            if proved(addr%k[1]  == k[0]) and proved(k[0] == k[0] % sizeOfByte):
                old_data = self.data[k]
                self.data.pop(k)
            if proved(addr%k[1]  == k[0]):
                self.store(k[0], EXTRACT(0, (addr-k[0])*8, old_data), (addr-k[0])*8)
            if proved(k[0] == k[0] % sizeOfByte):
                self.store(addr+sizeOfByte, EXTRACT((k[1]-addr-sizeOfByter-k[0])*8 , (addr+sizeOfByte-k[0])*8, old_data), (addr+sizeOfByte-k[0]))
        self.data[(addr, sizeOfByte)] = EXTRACT(data, 0, sizeOfBit)






