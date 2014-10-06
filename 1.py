from cpu import Cpu
from memory import InstMemory, DataMemory
from symbol import BitVec, CONCAT

instmem = InstMemory()
datamem = DataMemory()
cpu = Cpu(instmem, datamem, "amd64")
cpu.PC = 0x0
#(A+B) * (A+2*B)
plaininst = """
  4004ed:	55                   	push   %rbp
  4004ee:	48 89 e5             	mov    %rsp,%rbp
  4004f1:	8b 45 f8             	mov    -0x8(%rbp),%eax
  4004f4:	8b 55 f4             	mov    -0xc(%rbp),%edx
  4004f7:	01 d0                	add    %edx,%eax
  4004f9:	89 45 fc             	mov    %eax,-0x4(%rbp)
  4004fc:	8b 45 fc             	mov    -0x4(%rbp),%eax
  4004ff:	8b 55 f8             	mov    -0x8(%rbp),%edx
  400502:	01 d0                	add    %edx,%eax
  400504:	89 45 f4             	mov    %eax,-0xc(%rbp)
  400507:	8b 45 f4             	mov    -0xc(%rbp),%eax
  40050a:	0f af 45 fc          	imul   -0x4(%rbp),%eax
  40050e:	89 45 f4             	mov    %eax,-0xc(%rbp)
  400511:	8b 45 f4             	mov    -0xc(%rbp),%eax
  400514:	5d                   	pop    %rbp"""
inst = ""
for line in plaininst.split("\n"):
    if len(line) < 9: continue
    h = line[9:31]
    inst =inst + h.replace(" ", "").replace("\t", "").decode("hex")

for addr in xrange(len(inst)):
    instmem.putchar(addr, inst[addr])

def giveName(addr, name, lenOfBit):
    s = BitVec(name, lenOfBit)
    lenOfByte = lenOfBit / 8
    for i in range(lenOfByte):
        datamem.putchar(addr + i, s >> (8*i))

def printAddr(addr, lenOfBit):
    lenOfByte = lenOfBit / 8
    a = []
    for i in range(lenOfByte):
       a.append(datamem.getchar(addr+i))
    print "%s@[%s] = %s" % (lenOfByte, p(addr),  p(CONCAT(8, a[::-1]).simplify()))
    
RSP0 = cpu.RSP
giveName(cpu.RSP-16, "B", 32)
giveName(cpu.RSP-20, "A", 32)

def p(s):
    if isinstance(s, BitVec):
        s.simplify()
    s = str(s)
    retv = ""
    temp = ""
    flag = True
    for c in s:
        if c in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ":
            flag = False
        elif c not in "0123456789":
            flag = True
        if c in "0123456789" and flag:
            temp += c
        elif temp == "":
            retv += c
        else:
            retv += hex(int(temp))
            retv += c
            temp = ""
    if temp != "":
        retv += hex(int(temp))
        temp = ""
    return retv


while cpu.PC < len(inst):
    cpu.execute()
    """
    for reg in cpu.listRegisters():
        print eval("p('%s') + '\t\t' + p(cpu.%s)" % (reg, reg))
    for k in sorted(cpu.mem.data.keys(), key=lambda s: str(s)):
        print p(k), "-----",p(cpu.mem.data[k])
    """
printAddr(RSP0 -4, 32)
printAddr(RSP0 -8, 32)
printAddr(RSP0 -12, 32)
printAddr(RSP0 -16, 32)
printAddr(RSP0 -20, 32)
printAddr(RSP0 -24, 32)

