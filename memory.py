from pysymemu.smtlibv2 import BitVec, EXTRACT, proved, CONCAT

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
    @staticmethod
    def provedAddrSizeInList(addr, size, l):
        if len(l) == 0:
            return []
        if len(l) == 1:
            k = l[0]
            if size != 0 and proved((addr==k[0]) & (size == k[1])):
                return l
            elif size == 0 and proved(addr==k[0]):
                return l
            else:
                return []
        retv = []

        left = l[:len(l)/2]
        right = l[len(l)/2:]
        for ll in [left, right]:
            exp = False
            for k in ll:
                if size == 0:
                    exp = exp | (addr == k[0])
                else:
                    exp = exp | ((addr == k[0]) & (size == k[1]))
            if proved(exp):
                a = DataMemory.provedAddrSizeInList(addr, size, ll)
                retv.extend(a)
        return retv

    def putchar(self, addr, data):
        addr.simplify()
        if isinstance(data, BitVec):
            data.simplify()
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
        #assert proved(addr%sizeOfByte == 0) #This line is Wrong, e.g RBP-8 will not be proved
        for k in self.provedAddrSizeInList(addr, sizeOfByte, self.data.keys()):
            return self.data[k]
        """
        for k in self.data.keys():
            if proved(addr/k[1]*k[1]  == k[0]) or proved(k[0]/sizeOfByte*sizeOfByte == addr):
                retv = CONCAT(8, *[self.getchar(addr+i) for i in reversed(range(0, sizeOfByte))])
                return retv
        """
        retv = BitVec((str("%d@[%s]" % (sizeOfByte, addr))), sizeOfBit)
        self.data[(addr, sizeOfByte)] = retv
        return retv
    def store(self, addr, data, sizeOfBit):
        addr.simplify()
        if isinstance(data, BitVec):
            data.simplify()
        sizeOfByte = sizeOfBit / 8
        for k in self.provedAddrSizeInList(addr, sizeOfByte, self.data.keys()):
            self.data.pop(k)
            self.data[(addr, sizeOfByte)] = EXTRACT(data, 0, sizeOfBit)
            return 
        """
        for k in self.data.keys():
            if proved(addr/k[1]*k[1]  == k[0]) and proved(k[0] == k[0] % sizeOfByte):
                old_data = self.data[k]
                self.data.pop(k)
            if proved(addr  == k[0]/sizeOfByte*sizeOfByte):
                pass
            elif proved(k[0] == addr / k[1] * k[1]):
                #FIXME: this line is wrong
                pass
        """
        self.data[(addr, sizeOfByte)] = EXTRACT(data, 0, sizeOfBit)






