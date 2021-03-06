import types
from distorm3 import Decompose, Decode16Bits, Decode32Bits, Decode64Bits, Mnemonics, Registers

import pysymemu
from pysymemu import cpu
from pysymemu.smtlibv2 import BitVec, proved, EXTRACT, CONCAT, SEXTEND, UDIV, UREM


class Register256(cpu.Register256):
    def __init__(self):
        raise Exception("Overloaded Register __init__ has two args (self, name)")
    def __init__(self, name):
        super(Register256, self).__init__()
        self._YMM = BitVec(name, 256)
class Register64(cpu.Register64):
    def __init__(self):
        raise Exception("Overloaded Register __init__ has two args (self, name)")
    def __init__(self, name):
        super(Register64, self).__init__()
        self._RX = BitVec(name, 64)

class Cpu(cpu.Cpu):
    def __init__(self, instmem, memory, machine='i386'):
        super(Cpu, self).__init__(memory, machine)
        self.instmem = instmem

        for reg in ['RAX', 'RCX', 'RDX', 'RBX', 'RSP', 'RBP', 'RSI', 'RDI', 'R8',
                    'R9', 'R10', 'R11', 'R12', 'R13', 'R14', 'R15',  'RIP']:
            setattr(self, '_%s'%reg, Register64(reg))

        for reg in ['_YMM0', '_YMM1', '_YMM2', '_YMM3', '_YMM4', '_YMM5',
                    '_YMM6', '_YMM7', '_YMM8', '_YMM9', '_YMM10', '_YMM11',
                    '_YMM12', '_YMM13', '_YMM14', '_YMM15']:
            setattr(self, reg, Register256(reg))

        #for reg in ['ES', 'CS', 'SS', 'DS', 'FS', 'GS' ]:
        #    setattr(self, '%s'%reg, 0)

        #for reg in ['CF','PF','AF','ZF','SF','DF','OF','IF']:
        #    setattr(self, reg, Bool(reg))
     
    def store(self, where, expr, size):
        '''
        Writes a little endian value in memory.
        
        @param where: the address in memory where to store the value.
        @param expr: the value to store in memory.
        @param size: the amount of bytes to write. 
        '''
        assert size in [8, 16, 32, 64, 128, 256] 
        self.mem.store(where, expr, size)

    def load(self, where, size):
        '''
        Reads a little endian value of C{size} bits from memory at address C{where}.
        
        @rtype: int or L{BitVec}
        @param where: the address to read from.
        @param size: the number of bits to read.
        @return: the value read.
        '''
        #return CONCAT(8, *[ord(self.mem.getchar(where+i/8)) for i in reversed(xrange(0,size,8))])
        return self.mem.load(where, size)

    def getInstruction(cpu,pc):
        text = []
        try:
            for i in xrange(0,16):
                text.append(cpu.instmem.fetchchar(pc+i))
        except Exception, e:
            pass
        text = "".join(text)
        try:
            instruction = Decompose(pc, text, cpu.dmode)[0]
        except:
            raise pysymemu.cpu.DecodeException(pc,text,'')

        if not instruction.valid:
            raise pysymemu.cpu.DecodeException(pc,text,'')

        if instruction.mnemonic == 'POPF':
            instruction.operandSize = [16,32,64][(((instruction.rawFlags) >> 8) & 3)]
            instruction.addrSize = [16,32,64][(((instruction.rawFlags) >> 10) & 3)]
            if instruction.operandSize == 32:
                instruction.mnemonic = 'POPFD'
            elif instruction.operandSize == 64:
                instruction.mnemonic = 'POPFQ'
        if instruction.mnemonic == 'PUSHF':
            instruction.operandSize = [16,32,64][(((instruction.rawFlags) >> 8) & 3)]
            instruction.addrSize = [16,32,64][(((instruction.rawFlags) >> 10) & 3)]
            if instruction.operandSize == 32:
                instruction.mnemonic = 'PUSHFD'
            elif instruction.operandSize == 64:
                instruction.mnemonic = 'PUSHFQ'
            #print instruction, instruction.size, instruction.operands,, dir(instruction)
        if instruction.mnemonic.startswith('CMPS') or instruction.mnemonic.startswith('SCAS'):
            if 'FLAG_REP' in instruction.flags:
                instruction.flags[instruction.flags.index('FLAG_REP')]='FLAG_REPZ'

        #Fix/aument opperands so it can access cpu/memory
        for op in instruction.operands:
            op.read=types.MethodType(cpu.readOperand, op)
            op.write=types.MethodType(cpu.writeOperand, op)
            op.address=types.MethodType(cpu.getOperandAddress, op)

        return instruction

    @cpu.instruction
    def IDIV(cpu, src):
        reg_name_h = { 8: 'AH', 16: 'DX', 32:'EDX', 64:'RDX'}[src.size]
        reg_name_l = { 8: 'AL', 16: 'AX', 32:'EAX', 64:'RAX'}[src.size]
        reg_h = cpu.getRegister(reg_name_h)
        reg_l = cpu.getRegister(reg_name_l)

        if proved(reg_h == EXTRACT(SEXTEND(reg_l, src.size, src.size * 2), src.size, src.size)):
            dividend = reg_l
            divisor = src.read()
        else:
            dividend = CONCAT(src.size, reg_h, reg_l)
            divisor = SEXTEND(src.read(), src.size, src.size * 2)

        if isinstance(divisor, (int,long)) and divisor == 0:
            raise DivideError()

        quotient = dividend / divisor
        if isinstance(quotient, (int,long)) and quotient > (1<<src.size)-1:
            raise DivideError()
        reminder = dividend % divisor

        cpu.setRegister(reg_name_l, EXTRACT(quotient, 0, src.size))
        cpu.setRegister(reg_name_h, EXTRACT(reminder, 0, src.size))
        #Flags Affected
        #The CF, OF, SF, ZF, AF, and PF flags are undefined.

    @cpu.instruction
    def DIV(cpu, src):
        reg_name_h = { 8: 'AH', 16: 'DX', 32:'EDX', 64:'RDX'}[src.size]
        reg_name_l = { 8: 'AL', 16: 'AX', 32:'EAX', 64:'RAX'}[src.size]
        reg_h = cpu.getRegister(reg_name_h)
        reg_l = cpu.getRegister(reg_name_l)

        if proved(reg_h == 0):
            dividend = reg_l
            divisor = src.read()
        else:
            dividend = CONCAT(src.size, reg_h, reg_l)
            divisor = ZEXTEND(src.read(), src.size * 2)

        if isinstance(divisor, (int,long)) and divisor == 0:
            raise DivideError()

        quotient = UDIV(dividend, divisor)
        if isinstance(quotient, (int,long)) and quotient > (1<<src.size)-1:
            raise DivideError()
        reminder = UREM(dividend, divisor)

        cpu.setRegister(reg_name_l, EXTRACT(quotient, 0, src.size))
        cpu.setRegister(reg_name_h, EXTRACT(reminder, 0, src.size))
        #Flags Affected
        #The CF, OF, SF, ZF, AF, and PF flags are undefined.

