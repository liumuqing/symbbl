from symbol import BitVec, EXTRACT, proved

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
        #data.simplify()
        for k in self.data.keys():
            if proved(addr == k):
                self.data.pop(k)
        key = addr
        self.data[key] = EXTRACT(data, 0, 8)
    def getchar(self, addr):
        addr.simplify()
        for k in self.data.keys():
            if proved(addr == k):
                return self.data[k]
        retv = BitVec(str("[%s]" % addr), 8) # "[%s] % addr" may be a unicode, ...., cast it to str
        self.data[addr] = retv
        return retv


