symbbl
========
* An intel 64 symbolic basic block analysis model. 
* ``cpu.py`` is from https://github.com/feliam/pysymemu

Dependencies:
-------------
* z3, an smt solver. http://z3.codeplex.com/ 
* distorm3, a disassembler. https://code.google.com/p/distorm/

Example
------------
```python
from symbbl import symbbl, prettyPrint
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
    inst += line.strip("\n")[7:30].replace("\t", "").replace(" ", "").decode("hex")

predefine = {("RBP-8", 4): "C", ("RBP-12", 4):"B", ("RBP-16", 4):"A"}

res = symbbl(inst, "amd64", predefine)
print prettyPrint(res)
```

part of what you will get:
```
RAX:
Concat(0x0,
       Extract(0x3f, 0x30, SignExt(0x20, A)*SignExt(0x20, B)),
       Extract(0xf,
               0x0,
               bvsmod_i(Concat(Extract(0x2f,
                                       0x20,
                                       SignExt(0x20, A)*
                                       SignExt(0x20, B)),
                               Extract(0xf,
                                       0x0,
                                       SignExt(0x20, A))*
                               Extract(0xf,
                                       0x0,
                                       SignExt(0x20, B))),
                        C)))

RCX:
RCX

0x4@[0xfffffffffffffffcL + RBP]:			Concat(Extract(0x3f, 0x30, SignExt(0x20, A)*SignExt(0x20, B)),
       Extract(0xf,
               0x0,
               bvsmod_i(Concat(Extract(0x2f,
                                       0x20,
                                       SignExt(0x20, A)*
                                       SignExt(0x20, B)),
                               Extract(0xf,
                                       0x0,
                                       SignExt(0x20, A))*
                               Extract(0xf,
                                       0x0,
                                       SignExt(0x20, B))),
                        C)))

0x4@[0xfffffffffffffff8L + RBP]:			C

0x8@[RSP]:			0x8@[RSP]

0x4@[0xfffffffffffffff0L + RBP]:			A

0x4@[0xfffffffffffffff4L + RBP]:			B
```
	

