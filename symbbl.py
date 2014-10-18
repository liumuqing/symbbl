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
    plaininst = """
   4:	48 89 7d e8          	mov    %rdi,-0x18(%rbp)
   8:	48 89 75 e0          	mov    %rsi,-0x20(%rbp)
   c:	89 55 dc             	mov    %edx,-0x24(%rbp)
   f:	c7 45 f4 00 00 00 00 	movl   $0x0,-0xc(%rbp)
  16:	eb 16                	jmp    2e <_Z8RC4_initPcS_i+0x2e>
  18:	8b 45 f4             	mov    -0xc(%rbp),%eax
  1b:	48 63 d0             	movslq %eax,%rdx
  1e:	48 8b 45 e8          	mov    -0x18(%rbp),%rax
  22:	48 01 c2             	add    %rax,%rdx
  25:	8b 45 f4             	mov    -0xc(%rbp),%eax
  28:	88 02                	mov    %al,(%rdx)
  2a:	83 45 f4 01          	addl   $0x1,-0xc(%rbp)
  2e:	81 7d f4 ff 00 00 00 	cmpl   $0xff,-0xc(%rbp)
  35:	7e e1                	jle    18 <_Z8RC4_initPcS_i+0x18>
  37:	c7 45 f8 00 00 00 00 	movl   $0x0,-0x8(%rbp)
  3e:	c7 45 fc 00 00 00 00 	movl   $0x0,-0x4(%rbp)
  45:	e9 92 00 00 00       	jmpq   dc <_Z8RC4_initPcS_i+0xdc>
  4a:	8b 45 fc             	mov    -0x4(%rbp),%eax
  4d:	48 63 d0             	movslq %eax,%rdx
  50:	48 8b 45 e8          	mov    -0x18(%rbp),%rax
  54:	48 01 d0             	add    %rdx,%rax
  57:	0f b6 00             	movzbl (%rax),%eax
  5a:	0f be d0             	movsbl %al,%edx
  5d:	8b 45 f8             	mov    -0x8(%rbp),%eax
  60:	8d 0c 02             	lea    (%rdx,%rax,1),%ecx
  63:	8b 45 fc             	mov    -0x4(%rbp),%eax
  66:	99                   	cltd   
  67:	f7 7d dc             	idivl  -0x24(%rbp)
  6a:	89 d0                	mov    %edx,%eax
  6c:	48 63 d0             	movslq %eax,%rdx
  6f:	48 8b 45 e0          	mov    -0x20(%rbp),%rax
  73:	48 01 d0             	add    %rdx,%rax
  76:	0f b6 00             	movzbl (%rax),%eax
  79:	0f be c0             	movsbl %al,%eax
  7c:	8d 14 01             	lea    (%rcx,%rax,1),%edx
  7f:	89 d0                	mov    %edx,%eax
  81:	c1 f8 1f             	sar    $0x1f,%eax
  84:	c1 e8 18             	shr    $0x18,%eax
  87:	01 c2                	add    %eax,%edx
  89:	0f b6 d2             	movzbl %dl,%edx
  8c:	29 c2                	sub    %eax,%edx
  8e:	89 d0                	mov    %edx,%eax
  90:	89 45 f8             	mov    %eax,-0x8(%rbp)
  93:	8b 45 fc             	mov    -0x4(%rbp),%eax
  96:	48 63 d0             	movslq %eax,%rdx
  99:	48 8b 45 e8          	mov    -0x18(%rbp),%rax
  9d:	48 01 d0             	add    %rdx,%rax
  a0:	0f b6 00             	movzbl (%rax),%eax
  a3:	88 45 f3             	mov    %al,-0xd(%rbp)
  a6:	8b 45 fc             	mov    -0x4(%rbp),%eax
  a9:	48 63 d0             	movslq %eax,%rdx
  ac:	48 8b 45 e8          	mov    -0x18(%rbp),%rax
  b0:	48 01 c2             	add    %rax,%rdx
  b3:	8b 45 f8             	mov    -0x8(%rbp),%eax
  b6:	48 63 c8             	movslq %eax,%rcx
  b9:	48 8b 45 e8          	mov    -0x18(%rbp),%rax
  bd:	48 01 c8             	add    %rcx,%rax
  c0:	0f b6 00             	movzbl (%rax),%eax
  c3:	88 02                	mov    %al,(%rdx)
  c5:	8b 45 f8             	mov    -0x8(%rbp),%eax
  c8:	48 63 d0             	movslq %eax,%rdx
  cb:	48 8b 45 e8          	mov    -0x18(%rbp),%rax
  cf:	48 01 c2             	add    %rax,%rdx
  d2:	0f b6 45 f3          	movzbl -0xd(%rbp),%eax
  d6:	88 02                	mov    %al,(%rdx)
  d8:	83 45 fc 01          	addl   $0x1,-0x4(%rbp)
  dc:	81 7d fc ff 00 00 00 	cmpl   $0xff,-0x4(%rbp)
  e3:	0f 8e 61 ff ff ff    	jle    4a <_Z8RC4_initPcS_i+0x4a>
"""
    inst = ""
    for line in plaininst.split("\n"):
        if len(line) < 10:
            continue
        inst += line.strip("\n")[6:28].replace("\t", "").replace(" ", "").decode("hex")

    predefine = {("RBP-8", 4): "C", ("RBP-12", 4):"B", ("RBP-16", 4):"A"}

    res = symbbl(inst, "amd64", predefine)
    print prettyPrint(res)

