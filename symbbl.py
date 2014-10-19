from cpu import Cpu
from memory import InstMemory, DataMemory
from pysymemu.smtlibv2 import BitVec, CONCAT, issymbolic, isconcrete, getallvalues
import copy
def _doPreDefineMem(addr, lenOfByte, symbolName, datamem, cpu):
    assert lenOfByte in [1, 2, 4, 8]
    lenOfBit = lenOfByte * 8
    _addr = addr
    for regname in sorted(cpu.listRegisters(), key=lambda x:-len(x)):
        l = len(regname)
        i = 0
        while i < len(_addr)-l:
            if (i == 0 or _addr[i-1] not in "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_.") and _addr[i:i+l].upper() == regname:
                _addr = _addr[:i] + "cpu."+regname+_addr[i+l:] 
            i += 1
    _addr = eval(_addr)
    datamem.store(_addr, BitVec(symbolName, lenOfBit), lenOfBit)

def symbbl(inst, arch="i386", preDefineMem={}, startPC=0):
    assert arch in ["i386", "amd64"]

    instmem = InstMemory()
    for addr in xrange(len(inst)):
        instmem.putchar(addr, inst[addr])

    datamem = DataMemory()

    PC0 = startPC
    cpu = Cpu(instmem, datamem, arch)
    cpu.PC = startPC

    for k in preDefineMem.keys():
        _doPreDefineMem(k[0], k[1], preDefineMem[k], datamem, cpu)

    #RUN
    while PC0 <=cpu.PC < len(inst)+PC0:
        if issymbolic(cpu.PC):
            pcs = getallvalues(cpu.PC)
            if len(pcs) == 1:
                cpu.PC = pcs[0]
            else:
                print "Stop Execution because symbolic PC"
                print pcs
                print cpu.PC
                raw_input()
                break
        print cpu.getInstruction(cpu.PC)
        cpu.execute()

    return cpu
def prettyPrint(cpu):
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


    retv = ""
    for k in cpu.listRegisters():
        if issymbolic(cpu.getRegister(k)) and cpu.getRegister(k).size == cpu.AddressSize:
            retv += "%s:\n%s\n\n" % (p(k), p(cpu.getRegister(k)))

    for k in cpu.mem.data.keys():
        retv += "%s@[%s]:\t\t\t%s\n\n" % (p(k[1]), p(k[0]), p(cpu.mem.data[k]))

    return retv


if __name__ == "__main__":

    plaininst = """
       4:	8b 45 f0             	mov    -0x10(%rbp),%eax
       7:	0f af 45 f4          	imul   -0xc(%rbp),%eax
       b:	99                   	cltd   
       c:	f7 7d f8             	idivl  -0x8(%rbp)
       f:	89 55 fc             	mov    %edx,-0x4(%rbp)
      12:	8b 45 fc             	mov    -0x4(%rbp),%eax
      15:	5d                   	pop    %rbp
    """
    inst = ""
    for line in plaininst.split("\n"):
        if len(line) < 10:
            continue
        line = line.strip("\n")
        inst += line[line.find(":")+1:line.find(":") + 23].replace("\t", "").replace(" ", "").decode("hex")

    predefine = {("RBP-8", 4): "C", ("RBP-12", 4):"B", ("RBP-16", 4):"A"}

    res = symbbl(inst, "amd64", predefine)
    print prettyPrint(res)

