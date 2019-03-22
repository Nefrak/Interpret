import re
import argparse
import sys
from xml.dom.minidom import parse, parseString

#Trida reprezentujici interpretovany program
class Program():
    def __init__(self):
        self.insList = {}
        self.pc = []
        self.pc.append(1)
        self.frames = FrameHolder()
        self.labels = {} #jmeno -> pozice
        self.stack = []
        self.insCounter = 0

    #metoda pro pridani navesti
    def addLabel(self, inst):
        if inst.arg1[1] not in self.labels:
            self.labels[inst.arg1[1]] = inst.order
        else:
            raise SyntaxError("Badly writen code.")

    #metoda proprevadeni esc sekvence
    def escToChar(self, value):
        array = re.findall("\\\\[0-9]{3}", value)
        for y in array:
            i = y[1:]
            i = int(i)
            i = str(chr(i))
            value = value.replace(y,i)
        return value

    def addInst(self, inst):
        if inst.order not in self.insList:
            self.insList[inst.order] = inst
            if inst.opcode == "LABEL":
                self.addLabel(inst)
        else:
            raise SyntaxError("Badly writen code.")

    #metoda kontrolujici typ konstant
    def checkType(self, arg):
        if arg[0] == "int" and isinstance(arg[1], int):
            return True
        elif arg[0] == "bool" and isinstance(arg[1], bool):
            return True
        elif arg[0] == "string" and isinstance(arg[1], str):
            return True
        return False

    #metoda navracejici typ symbolu
    def getSymbType(self, arg):
        try:
            if arg[0] == "int" and isinstance(arg[1], int):
                return "int"
            elif arg[0] == "bool" and isinstance(arg[1], bool):
                return "bool"
            elif arg[0] == "string" and isinstance(arg[1], str):
                return "string"
            elif arg[0] == "var":
                return "var"
            return ""
        except:
            raise TypeError("Wrong operand types.")

    #navraci typ promenne
    def getVarType(self, arg):
        if isinstance(arg[1], int):
            return "int"
        elif isinstance(arg[1], bool):
            return "bool"
        elif isinstance(arg[1], str):
            return "string"
        return ""

    #metoda pro ziskani hodnoty symbolu
    def getSymbVal(self, arg):
        val = ""
        if arg[0] == "int":
            if self.checkType(arg):
                val = arg[1]
            else:
                raise SyntaxError("Badly writen code.")
        elif arg[0] == "bool":
            if self.checkType(arg):
                val = arg[1]
            else:
                raise SyntaxError("Badly writen code.")
        elif arg[0] == "string":
            if self.checkType(arg):
                val = arg[1]
            else:
                raise SyntaxError("Badly writen code.")
        elif arg[0] == "var":
            val = self.frames.getVarVal(arg)
        else:
            raise SyntaxError("Badly writen code.")
        return val

    #metoda pro interpretaci programu
    def do(self):
        while str(self.pc[-1]) in self.insList.keys():
            try:
                self.doInst()
            except SyntaxError as error:
                print(repr(error), file=sys.stderr)
                exit(52)
            except TypeError as error:
                print(repr(error), file=sys.stderr)
                exit(53)
            except NameError as error:
                print(repr(error), file=sys.stderr)
                exit(54)
            except KeyError as error:
                print(repr(error), file=sys.stderr)
                exit(55)
            except ValueError as error:
                print(repr(error), file=sys.stderr)
                exit(56)
            except ZeroDivisionError as error:
                print(repr(error), file=sys.stderr)
                exit(57)
            except AttributeError as error:
                print(repr(error), file=sys.stderr)
                exit(58)

    #metoda pro interpretaci jednotlivych instrukci    
    def doInst(self):
        if self.insList[str(self.pc[-1])].opcode == "MOVE":
            self.move(self.insList[str(self.pc[-1])].arg1, self.insList[str(self.pc[-1])].arg2)
        elif self.insList[str(self.pc[-1])].opcode == "CREATEFRAME":
            self.createframe()
        elif self.insList[str(self.pc[-1])].opcode == "PUSHFRAME":
            self.pushframe()
        elif self.insList[str(self.pc[-1])].opcode == "POPFRAME":
            self.popframe()
        elif self.insList[str(self.pc[-1])].opcode == "DEFVAR":
            self.defvar(self.insList[str(self.pc[-1])].arg1)
        elif self.insList[str(self.pc[-1])].opcode == "CALL":
            self.call(self.insList[str(self.pc[-1])].arg1)
        elif self.insList[str(self.pc[-1])].opcode == "RETURN":
            self.ireturn()
        elif self.insList[str(self.pc[-1])].opcode == "PUSHS":
            self.pushs(self.insList[str(self.pc[-1])].arg1)
        elif self.insList[str(self.pc[-1])].opcode == "POPS":
            self.pops(self.insList[str(self.pc[-1])].arg1)
        elif self.insList[str(self.pc[-1])].opcode == "ADD":
            self.add(self.insList[str(self.pc[-1])].arg1, self.insList[str(self.pc[-1])].arg2, self.insList[str(self.pc[-1])].arg3)
        elif self.insList[str(self.pc[-1])].opcode == "SUB":
            self.sub(self.insList[str(self.pc[-1])].arg1, self.insList[str(self.pc[-1])].arg2, self.insList[str(self.pc[-1])].arg3)
        elif self.insList[str(self.pc[-1])].opcode == "MUL":
            self.mul(self.insList[str(self.pc[-1])].arg1, self.insList[str(self.pc[-1])].arg2, self.insList[str(self.pc[-1])].arg3)
        elif self.insList[str(self.pc[-1])].opcode == "IDIV":
            self.idiv(self.insList[str(self.pc[-1])].arg1, self.insList[str(self.pc[-1])].arg2, self.insList[str(self.pc[-1])].arg3)
        elif self.insList[str(self.pc[-1])].opcode == "LT":
            self.lt(self.insList[str(self.pc[-1])].arg1, self.insList[str(self.pc[-1])].arg2, self.insList[str(self.pc[-1])].arg3)
        elif self.insList[str(self.pc[-1])].opcode == "GT":
            self.gt(self.insList[str(self.pc[-1])].arg1, self.insList[str(self.pc[-1])].arg2, self.insList[str(self.pc[-1])].arg3)
        elif self.insList[str(self.pc[-1])].opcode == "EQ":
            self.eq(self.insList[str(self.pc[-1])].arg1, self.insList[str(self.pc[-1])].arg2, self.insList[str(self.pc[-1])].arg3)
        elif self.insList[str(self.pc[-1])].opcode == "AND":
            self.iand(self.insList[str(self.pc[-1])].arg1, self.insList[str(self.pc[-1])].arg2, self.insList[str(self.pc[-1])].arg3)
        elif self.insList[str(self.pc[-1])].opcode == "OR":
            self.ior(self.insList[str(self.pc[-1])].arg1, self.insList[str(self.pc[-1])].arg2, self.insList[str(self.pc[-1])].arg3)
        elif self.insList[str(self.pc[-1])].opcode == "NOT":
            self.inot(self.insList[str(self.pc[-1])].arg1, self.insList[str(self.pc[-1])].arg2)
        elif self.insList[str(self.pc[-1])].opcode == "INT2CHAR":
            self.int2char(self.insList[str(self.pc[-1])].arg1, self.insList[str(self.pc[-1])].arg2)
        elif self.insList[str(self.pc[-1])].opcode == "STRI2INT":
            self.stri2int(self.insList[str(self.pc[-1])].arg1, self.insList[str(self.pc[-1])].arg2, self.insList[str(self.pc[-1])].arg3)
        elif self.insList[str(self.pc[-1])].opcode == "READ":
            self.read(self.insList[str(self.pc[-1])].arg1, self.insList[str(self.pc[-1])].arg2)
        elif self.insList[str(self.pc[-1])].opcode == "WRITE":
            self.write(self.insList[str(self.pc[-1])].arg1)
        elif self.insList[str(self.pc[-1])].opcode == "CONCAT":
            self.concat(self.insList[str(self.pc[-1])].arg1, self.insList[str(self.pc[-1])].arg2, self.insList[str(self.pc[-1])].arg3)
        elif self.insList[str(self.pc[-1])].opcode == "STRLEN":
            self.strlen(self.insList[str(self.pc[-1])].arg1, self.insList[str(self.pc[-1])].arg2)
        elif self.insList[str(self.pc[-1])].opcode == "GETCHAR":
            self.getchar(self.insList[str(self.pc[-1])].arg1, self.insList[str(self.pc[-1])].arg2, self.insList[str(self.pc[-1])].arg3)
        elif self.insList[str(self.pc[-1])].opcode == "SETCHAR":
            self.setchar(self.insList[str(self.pc[-1])].arg1, self.insList[str(self.pc[-1])].arg2, self.insList[str(self.pc[-1])].arg3)
        elif self.insList[str(self.pc[-1])].opcode == "TYPE":
            self.itype(self.insList[str(self.pc[-1])].arg1, self.insList[str(self.pc[-1])].arg2)
        elif self.insList[str(self.pc[-1])].opcode == "LABEL":
            pass
        elif self.insList[str(self.pc[-1])].opcode == "JUMP":
            self.jump(self.insList[str(self.pc[-1])].arg1)
        elif self.insList[str(self.pc[-1])].opcode == "JUMPIFEQ":
            self.jumpifeq(self.insList[str(self.pc[-1])].arg1, self.insList[str(self.pc[-1])].arg2, self.insList[str(self.pc[-1])].arg3)
        elif self.insList[str(self.pc[-1])].opcode == "JUMPIFNEQ":
            self.jumpifneq(self.insList[str(self.pc[-1])].arg1, self.insList[str(self.pc[-1])].arg2, self.insList[str(self.pc[-1])].arg3)
        elif self.insList[str(self.pc[-1])].opcode == "DPRINT":
            self.dprint(self.insList[str(self.pc[-1])].arg1)
        elif self.insList[str(self.pc[-1])].opcode == "BREAK":
            self.ibreak(str(self.pc[-1]))
        else:
            raise SyntaxError("Badly writen code.")
        self.pc[-1] += 1
        self.insCounter += 1
    
    def move(self, arg1, arg2):
        nType = None
        if type(self.getSymbVal(arg2)) is str:
            nType = "string"
        if type(self.getSymbVal(arg2)) is int:
            nType = "int"
        if type(self.getSymbVal(arg2)) is bool:
            nType = "bool"
        if (self.getSymbType(arg1) == "var"):
            self.frames.changeVar(arg1, nType, self.getSymbVal(arg2))
        else:
            raise TypeError("Wrong operand types.")
    
    def createframe(self):
        self.frames.createFrame()

    def pushframe(self):
        self.frames.pushFrame()
    
    def popframe(self):
        self.frames.popFrame()

    def defvar(self, arg):
        myVar = Variable(arg[1], None)
        self.frames.addVar(myVar, myVar.frame)
    
    def call(self, arg):
        if arg[1] in self.labels.keys():
            self.pc.append(int(self.labels.get(arg[1])))
        else:
            raise ValueError("Missing value.")

    def ireturn(self):
        if len(self.pc) > 1:
            self.pc.pop()
        else:
            raise ValueError("Missing value.")

    def pushs(self, arg):
        print(arg)
        if self.getSymbType(arg) == "var":
            arg[1] = self.getSymbVal(arg) 
            arg[0] = self.getVarType(arg)
            self.stack.append(arg)
        else:
            self.stack.append(arg)
    
    def pops(self, arg):
        if len(self.stack) > 0:
            val = self.stack.pop()
            self.frames.changeVar(arg, val[0], val[1])
        else:
            raise ValueError("Missing value.")

    def add(self, arg1, arg2, arg3):
        val1 = self.getSymbVal(arg2)
        val2 = self.getSymbVal(arg3)
        if (self.getSymbType(arg1) == "var"
            and isinstance(val1, int)
            and isinstance(val2, int)):
            val = val1 + val2
            self.frames.changeVar(arg1, "int", val)
        else:
            raise TypeError("Wrong operand types.")

    def sub(self, arg1, arg2, arg3):
        val1 = self.getSymbVal(arg2)
        val2 = self.getSymbVal(arg3)
        if (self.getSymbType(arg1) == "var"
            and isinstance(val1, int)
            and isinstance(val2, int)):
            val = val1 - val2
            self.frames.changeVar(arg1, "int", val)
        else:
            raise TypeError("Wrong operand types.")

    def mul(self, arg1, arg2, arg3):
        val1 = self.getSymbVal(arg2)
        val2 = self.getSymbVal(arg3)
        if (self.getSymbType(arg1) == "var"
            and isinstance(val1, int)
            and isinstance(val2, int)):
            val = val1 * val2
            self.frames.changeVar(arg1, "int", val)
        else:
            raise TypeError("Wrong operand types.")

    def idiv(self, arg1, arg2, arg3):
        val1 = self.getSymbVal(arg2)
        val2 = self.getSymbVal(arg3)
        if (self.getSymbType(arg1) == "var"
            and isinstance(val1, int)
            and isinstance(val2, int)):
            if val2 == 0:
                raise ZeroDivisionError("Badly writen code.")
            val = val1 // val2
            self.frames.changeVar(arg1, "int", val)
        else:
            raise TypeError("Wrong operand types.")

    def lt(self, arg1, arg2, arg3): 
        type1 = None
        type2 = None
        if self.getSymbType(arg2) == "var":
            type1 = type(self.frames.getVarVal(arg2))
        else:
            type1 =  type(self.getSymbVal(arg2))
        if self.getSymbType(arg3) == "var":
            type2 = type(self.frames.getVarVal(arg3))
        else:
            type2 = type(self.getSymbVal(arg3))
        if self.getSymbType(arg1) == "var" and type1 == type2:
            val1 = self.getSymbVal(arg2)
            val2 = self.getSymbVal(arg3)
            self.frames.changeVar(arg1, "bool", val1 < val2)
        else:
            raise TypeError("Wrong operand types.")

    def gt(self, arg1, arg2, arg3):
        type1 = None
        type2 = None
        if self.getSymbType(arg2) == "var":
            type1 = type(self.frames.getVarVal(arg2))
        else:
            type1 = type(self.getSymbVal(arg2))
        if self.getSymbType(arg3) == "var":
            type2 = type(self.frames.getVarVal(arg3))
        else:
            type2 = type(self.getSymbVal(arg3))
        if self.getSymbType(arg1) == "var" and type1 == type2:
            val1 = self.getSymbVal(arg2)
            val2 = self.getSymbVal(arg3)
            self.frames.changeVar(arg1, "bool", val1 > val2)
        else:
            raise TypeError("Wrong operand types.")

    def eq(self, arg1, arg2, arg3):
        type1 = None
        type2 = None
        if self.getSymbType(arg2) == "var":
            type1 = type(self.frames.getVarVal(arg2))
        else:
            type1 =  type(self.getSymbVal(arg2))
        if self.getSymbType(arg3) == "var":
            type2 = type(self.frames.getVarVal(arg3))
        else:
            type2 = type(self.getSymbVal(arg3))
        if self.getSymbType(arg1) == "var" and type1 == type2:
            val1 = self.getSymbVal(arg2)
            val2 = self.getSymbVal(arg3)
            self.frames.changeVar(arg1, "bool", val1 == val2)
        else:
            raise TypeError("Wrong operand types.")

    def iand(self, arg1, arg2, arg3):
        vType = None
        if (((self.getSymbType(arg2) == "var" and isinstance(self.getSymbVal(arg2), bool)) 
            or self.getSymbType(arg2) == "bool") 
            and ((self.getSymbType(arg3) == "var" and isinstance(self.getSymbVal(arg3), bool)) 
            or self.getSymbType(arg3) == "bool")):
            vType = "bool"
        if self.getSymbType(arg1) == "var" and vType == "bool":
            val1 = bool(self.getSymbVal(arg2))
            val2 = bool(self.getSymbVal(arg3))
            self.frames.changeVar(arg1, vType, val1 and val2)
        else:
            raise TypeError("Wrong operand types.")

    def ior(self, arg1, arg2, arg3):
        vType = None
        if (((self.getSymbType(arg2) == "var" and isinstance(self.getSymbVal(arg2), bool)) 
            or self.getSymbType(arg2) == "bool") 
            and ((self.getSymbType(arg3) == "var" and isinstance(self.getSymbVal(arg3), bool)) 
            or self.getSymbType(arg3) == "bool")):
            vType = vType = "bool"
        if self.getSymbType(arg1) == "var" and vType == "bool":
            val1 = self.getSymbVal(arg2)
            val2 = self.getSymbVal(arg3)
            self.frames.changeVar(arg1, vType, val1 or val2)
        else:
            raise TypeError("Wrong operand types.")

    def inot(self, arg1, arg2):
        vType = None
        if ((self.getSymbType(arg2) == "var" and isinstance(self.getSymbVal(arg2), bool)) 
            or self.getSymbType(arg2) == "bool"):
            vType = "bool"
        if self.getSymbType(arg1) == "var" and vType == "bool":
            self.frames.changeVar(arg1, vType, not self.getSymbVal(arg2))
        else:
            raise TypeError("Wrong operand types.")

    def int2char(self, arg1, arg2):
        if (isinstance(self.getSymbVal(arg2), int) 
        and len(self.getSymbVal(arg2)) == 1
        and self.getSymbType(arg1) == "var"):
            self.frames.changeVar(arg1, "string", self.getSymbVal(arg2))
        else:
            raise TypeError("Wrong operand types.")

    def stri2int(self, arg1, arg2, arg3):
        if (isinstance(self.getSymbVal(arg2), str) 
        and len(self.getSymbVal(arg2)) >= self.getSymbVal(arg3)
        and self.getSymbType(arg1) == "var"):
            self.frames.changeVar(arg1, "string", ord(self.getSymbVal(arg2)[self.getSymbVal(arg3)]))
        else:
            raise TypeError("Wrong operand types.")

    def read(self, arg1, arg2):
        if arg2[1] == "string" or arg2[1] == "int" or arg2[1] == "bool":
            typ = arg2[1]
            val = input()
            if typ == "string":
                val = self.escToChar(val)
                val = str(val)
            elif typ == "int":
                try:
                    val = int(val)
                except ValueError:
                    raise TypeError("Wrong operand types.")
            elif typ == "bool":
                val.lower()
                val[0].upper()
                if val == "True" or val == "False":
                    val = bool(val)
                else:
                    raise TypeError("Wrong operand types.")
            else:
                raise TypeError("Wrong operand types.")
            self.frames.changeVar(arg1, typ, val)
        else:
            raise ValueError("Missing value.")

    def write(self, arg):
        toPrint = self.getSymbVal(arg)
        if self.getSymbType(arg) == "int" or self.getSymbType(arg) == "bool" or self.getSymbType(arg) == "string":
            if isinstance(arg[1], bool):
                arg[1] = str(arg[1]).lower()
            print(arg[1])
        elif self.getSymbType(arg) == "var":
            if isinstance(toPrint, bool):
                toPrint = str(toPrint).lower()
            print(toPrint)
        else:
            raise TypeError("Wrong operand types.")

    def concat(self, arg1, arg2, arg3):
        if (isinstance(self.getSymbVal(arg2), str)
        and isinstance(self.getSymbVal(arg3), str)
        and self.getSymbType(arg1) == "var"):
            val1 = self.getSymbVal(arg2)
            val2 = self.getSymbVal(arg3)
            val = val1 + val2
            self.frames.changeVar(arg1, "string", val)
        else:
            raise TypeError("Wrong operand types.")

    def strlen(self, arg1, arg2):
        if (isinstance(self.getSymbVal(arg2), str)
        and self.getSymbType(arg1) == "var"):
            val = len(self.getSymbVal(arg2))
            self.frames.changeVar(arg1, "int", val)
        else:
            raise AttributeError("Incorect working with string.")

    def getchar(self, arg1, arg2, arg3):
        if (isinstance(self.getSymbVal(arg2), str)
        and isinstance(self.getSymbVal(arg3), int)
        and len(self.getSymbVal(arg2)) >= self.getSymbVal(arg3)
        and self.getSymbType(arg1) == "var"):
            val = self.getSymbVal(arg2)[self.getSymbVal(arg3)]
            self.frames.changeVar(arg1, "string", val)
        else:
            raise AttributeError("Incorect working with string.")

    def setchar(self, arg1, arg2, arg3):
        if (isinstance(self.getSymbVal(arg2), int)
        and isinstance(self.getSymbVal(arg3), str)
        and len(self.getSymbVal(arg1)) >= int(self.getSymbVal(arg2))
        and len(self.getSymbVal(arg3)) == 1
        and self.getSymbType(arg1) == "var"):
            val = self.getSymbVal(arg1)
            val = list(val)
            val[int(self.getSymbVal(arg2))] = self.getSymbVal(arg3)
            val = ''.join(val)
            self.frames.changeVar(arg1, "string", val)
        else:
            raise AttributeError("Incorect working with string.")

    def itype(self, arg1, arg2):
        if self.getSymbType(arg1) == "var":
            if isinstance(self.getSymbVal(arg2), int):
                self.frames.changeVar(arg1, "string", "int")
            elif isinstance(self.getSymbVal(arg2), bool):
                self.frames.changeVar(arg1, "string", "bool")
            elif isinstance(self.getSymbVal(arg2), str):
                self.frames.changeVar(arg1, "string", "string")
            else:
                raise TypeError("Wrong operand types.")
        else:
            raise TypeError("Wrong operand types.")

    def jump(self, arg):
        if arg[1] in self.labels.keys():
            self.pc[-1] = int(self.labels.get(arg[1]))
        else:
            raise ValueError("Missing value.")

    def jumpifeq(self, arg1, arg2, arg3):
        if self.getSymbVal(arg2) == self.getSymbVal(arg3):
            if arg1[1] in self.labels.keys():
                self.pc[-1] = int(self.labels.get(arg1[1]))
            else:
                raise ValueError("Missing value.")

    def jumpifneq(self, arg1, arg2, arg3):
        if self.getSymbVal(arg2) != self.getSymbVal(arg3):
            if arg1[1] in self.labels.keys():
                self.pc[-1] = int(self.labels.get(arg1[1]))
            else:
                raise ValueError("Missing value.")

    def dprint(self, arg):
        sys.stderr.write(self.getSymbVal(arg))

    def ibreak(self, number):
        sys.stderr.write(self.insList[number].order)
        self.frames.printFrames()
        sys.stderr.write(self.insCounter)

#Trida reprezentujici promennou
class Variable():
    def __init__(self, ident, val):
        split = ident.split('@')
        self.frame = split[0]
        if len(split) == 2:
            self.ident = split[1]
        else:
            self.ident = ""
        self.val = val
        self.type = None

    #porovnani promennych
    def __eq__(self, other):
        return self.ident == other.ident

    #zmena hodnoty promenne
    def changeVal(self, vType, val):
        self.type = vType
        if self.type == "int":
            self.val = int(val)
        elif self.type == "string":
            self.val = str(val)
        elif self.type == "bool":
            self.val = bool(val)
        else:
            raise SyntaxError("Badly writen code.")

    #ziskani hodnoty promenne
    def getVal(self):
        if self.val != None:
            return self.val
        else:
            raise ValueError("Missing value.")

#Trida udrzujici hodnoty instrukce
class Instruction():
    def __init__(self, order, opcode, arg1, arg2, arg3):
        self.order = order
        self.opcode = opcode
        self.arg1 = arg1
        self.arg2 = arg2
        self.arg3 = arg3

#Trida obsahujuci ramce a jejich promenne
class FrameHolder():
    def __init__(self):
        self.gf = []
        self.lfStack = []
        self.tf = []
        self.tfDefined = False

    #pridani promenne
    def addVar(self, obj, frame):
        if frame == "GF" and (obj not in self.gf):
            self.gf.append(obj)
        elif frame == "LF" and (obj not in self.lfStack[-1]):
            self.lfStack[-1].append(obj)
        elif frame == "TF" and (obj not in self.tf) and self.tfDefined:
            self.tf.append(obj)
        else:
            raise KeyError("Frame error.")

    #zmena hodnoty promenne
    def changeVar(self, arg, vType, val):
        myVar = Variable(arg[1], None)
        if myVar.frame == "GF" and (myVar in self.gf):
            position = self.gf.index(myVar)
            self.gf[position].changeVal(vType, val)
        elif myVar.frame == "LF" and (myVar in self.lfStack[-1]):
            position = self.lfStack[-1].index(myVar)
            self.lfStack[-1][position].changeVal(vType, val)
        elif myVar.frame == "TF" and (myVar in self.tf) and self.tfDefined:
            position = self.tf.index(myVar)
            self.tf[position].changeVal(vType, val)
        else:
            raise NameError("Variable not found.")

    #ziskani hodnoty promenne
    def getVarVal(self, arg):
        myVar = Variable(arg[1], None)
        val = ""
        if myVar.frame == "GF" and (myVar in self.gf):
            position = self.gf.index(myVar)
            val = self.gf[position].getVal()
        elif myVar.frame == "LF" and (myVar in self.lfStack[-1]):
            position = self.lfStack[-1].index(myVar)
            val = self.lfStack[-1][position].getVal()
        elif myVar.frame == "TF" and (myVar in self.tf) and self.tfDefined:
            position = self.tf.index(myVar)
            val = self.tf[position].getVal()
        else:
            raise NameError("Variable not found.")
        return val

    #vytvoreni ramce
    def createFrame(self):
        self.tfDefined = True
        self.tf.clear()

    #push tf ramce do lf
    def pushFrame(self):
        if self.tfDefined:
            self.lfStack.append(self.tf.copy())
            self.tf.clear()
            self.tfDefined = False
        else:
            raise SyntaxError("Badly writen code.")

    #pop tf ramce z lf
    def popFrame(self):
        if len(self.lfStack) > 0:
            self.tf = self.lfStack.pop()
            self.tfDefined = True
        else:
            raise KeyError("Frame error.")

    #metoda pro vypsani framu
    def printFrames(self):
        sys.stderr.write(self.gf)
        sys.stderr.write(self.lfStack)
        sys.stderr.write(self.tf)
        

#Trida zpracovavajici parametry
class ArgParser():
    def __init__(self):
        parser = argparse.ArgumentParser(epilog="")
        parser.add_argument('--source')
        try:
            self.args = parser.parse_args()
        except SystemExit:
            print("Spatne zadane argumenty.")
            exit(10)

    def getSource(self, file):
        file = self.args.source
        return file

#Trida zpracovavajici soubor s XML
class XMLreader():
    def __init__(self, file):
        self.file = file

    #metoda pro prevedeni esc sekvence na znak
    def escToChar(self, value):
        array = re.findall("\\\\[0-9]{3}", value)
        for y in array:
            i = y[1:]
            i = int(i)
            i = str(chr(i))
            value = value.replace(y,i)
        return value

    
    #metoda pro cteni souboru
    def readFile(self):
        try:
            xml = parse(self.file)
        except:
            exit(31) 
        program = xml.getElementsByTagName("program")
        #spatny pocet programu
        if len(program) != 1:
            exit(31)
        lang = program[0].getAttribute("language")
        if lang != "IPPcode18":
            exit(31)
        instruction = program[0].getElementsByTagName("instruction")
        ippProg = self.getProg(instruction)
        return ippProg

    #zpracovani instrukci v souboru a nahrani do pole
    def getProg(self, instruction):
        ippProg = Program()
        for inst in instruction:
            arg1Type = ""
            arg2Type = ""
            arg3Type = ""
            arg1Val = ""
            arg2Val = ""
            arg3Val = ""
            order = inst.getAttribute("order")
            opcode = inst.getAttribute("opcode")
            argCheck = inst.getElementsByTagName("arg1")
            if len(argCheck) == 1:
                arg1Type = argCheck[0].getAttribute("type")
                if hasattr(argCheck[0].firstChild, 'data'):
                    if arg1Type == "int":
                        try:
                            arg1Val = int(argCheck[0].firstChild.data)
                        except ValueError:
                            exit(32)
                    elif arg1Type == "bool":
                        arg1Val = str(argCheck[0].firstChild.data)
                        if len(arg1Val) > 0:
                            arg1Val.lower()
                        else:
                            exit(32)
                        if arg1Val == "true":
                            arg1Val = True
                        elif arg1Val == "false":
                            arg1Val = False
                        else:
                            exit(32)
                    elif arg1Type == "string":
                        arg1Val = str(argCheck[0].firstChild.data)
                        arg1Val = self.escToChar(arg1Val)
                    elif arg1Type == "var" or arg1Type == "label" or arg1Type == "type":
                        arg1Val = str(argCheck[0].firstChild.data)
                    else:
                        exit(32)
            argCheck = inst.getElementsByTagName("arg2")
            if len(argCheck) == 1:
                arg2Type = argCheck[0].getAttribute("type")
                if hasattr(argCheck[0].firstChild, 'data'):
                    if arg2Type == "int":
                        try:
                            arg2Val = int(argCheck[0].firstChild.data)
                        except ValueError:
                            exit(32)
                    elif arg2Type == "bool":
                        arg2Val = str(argCheck[0].firstChild.data)
                        if len(arg2Val) > 0:
                            arg2Val.lower()
                        else:
                            exit(32)
                        if arg2Val == "true":
                            arg2Val = True
                        elif arg2Val == "false":
                            arg2Val = False
                        else:
                            exit(32)
                    elif arg2Type == "string":
                        arg2Val = str(argCheck[0].firstChild.data)
                        arg2Val = self.escToChar(arg2Val)
                    elif arg2Type == "var" or arg2Type == "label" or arg2Type == "type":
                        arg2Val = str(argCheck[0].firstChild.data)
                    else:
                        exit(32)
            argCheck = inst.getElementsByTagName("arg3")
            if len(argCheck) == 1:
                arg3Type = argCheck[0].getAttribute("type")
                if hasattr(argCheck[0].firstChild, 'data'): 
                    if arg3Type == "int":
                        try:
                            arg3Val = int(argCheck[0].firstChild.data)
                        except ValueError:
                            exit(32)
                    elif arg3Type == "bool":
                        arg3Val = str(argCheck[0].firstChild.data)
                        if len(arg3Val) > 0:
                            arg3Val.lower()
                        else:
                            exit(32)
                        if arg3Val == "true":
                            arg3Val = True
                        elif arg3Val == "false":
                            arg3Val = False
                        else:
                            exit(32)
                    elif arg3Type == "string":
                        arg3Val = str(argCheck[0].firstChild.data)
                        arg3Val = self.escToChar(arg3Val)
                    elif arg3Type == "var" or arg3Type == "label" or arg3Type == "type":
                        arg3Val = str(argCheck[0].firstChild.data)
                    else:
                        exit(32)
            arg1 = [arg1Type, arg1Val]
            arg2 = [arg2Type, arg2Val]
            arg3 = [arg3Type, arg3Val]
            instruction = Instruction(order, opcode, arg1, arg2, arg3)
            ippProg.addInst(instruction)
        return ippProg

#main
def main():
    sFile = ""
    parser = ArgParser()
    sFile = parser.getSource(sFile)
    if sFile != "" or sFile != None:
        reader = XMLreader(sFile)
    else:
        exit(10)
    program = reader.readFile()
    program.do()
    exit(0)

main(); 