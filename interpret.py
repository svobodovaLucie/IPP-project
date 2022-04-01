import argparse
from multiprocessing.sharedctypes import Value
import sys
import os
from xml.etree.ElementTree import ElementTree
import re

# Program is a Singleton
class Program:
  def __init__(self, input_file_pointer):
    self._instr_dict = {}
    self._lf: Frame = None
    self._tf: Frame = None
    self._gf = Frame()
    self._lf_stack = []
    self._call_stack = []
    self._instr_counter = 0 # stores current order
    self._label_dict = {}
    self._input_file_pointer = input_file_pointer
    self._data_stack = []
    
  def get_input_file_pointer(self):
    return self._input_file_pointer

  def add_label(self, name, order):
    if name in self._label_dict:
      sys.stderr.write('Label ' + name + ' already exists.\n')
      exit(52)
    self._label_dict[name] = order

  def get_label_order(self, label_name):
    if not label_name in self._label_dict:
      sys.stderr.write('Label ' + label_name + ' doesn\'t exist.\n')
      exit(52)
    return self._label_dict[label_name]

  def set_instr_counter(self, order):
    self._instr_counter = order

  def get_instr_counter(self):
    return self._instr_counter
  
  def call_stack_push(self, order):
    self._call_stack.append(order)

  def call_stack_pop(self):
    try:
      return self._call_stack.pop()
    except IndexError:
      sys.stderr.write('Call stack is empty.\n')
      exit(56)

  def data_stack_push(self, data):
    self._data_stack.append(data)

  def data_stack_pop(self):
    try:
      return self._data_stack.pop()
    except IndexError:
      sys.stderr.write('Operand stack is empty.\n')
      exit(56)

  def add_instr(self, order, instr):
    self._instr_dict[order] = instr

  def get_instr_dict(self):
    return self._instr_dict

  def sort(self):
    try:
      self._instr_dict = {key:value for key, value in sorted(self._instr_dict.items(), key=lambda item: int(item[0]))}
    except ValueError:
      sys.stderr.write('Invalid input XML.\n')
      exit(32)

  def get_frame(self, frame_name):
    # cut the oznaceni a pak rozhodni
    #print(frame_name)
    if frame_name[0:2] == 'GF':
      return self._gf
    elif frame_name[0:2] == 'LF':
      if self._lf == None:
        sys.stderr.write('Uninitialised local frame.\n')
        exit(55)
      #print("LF dict: ")
      #print(self._lf.get_frame_dict())
      return self._lf
    elif frame_name[0:2] == 'TF':
      if self._tf == None:
        sys.stderr.write('Uninitialised temporary frame.\n')
        print('HEY')
        exit(55)
        print('AHOI')
      return self._tf
    else:
      print('NEJAKA DIVNA CHYBA')
      exit(-1)  # TODO nemelo by nastat ale

  def get_frame_dict(self, frame_name):
    frame = self.get_frame(frame_name)
    return frame.get_frame_dict()

  def set_var(self, name_type):
    name, typ = (name_type)
    #print(name + " TYP: " + typ)
    frame = self.get_frame(name)
    frame.set_var(name, typ)

  def set_var_value(self, name, value_type):
    value, typ = (value_type)
    frame = self.get_frame(name)
    frame.set_var_value(name, value, typ)

  def get_var_value(self, name):
    frame = self.get_frame(name)
    return frame.get_var_value(name[3:])

  def get_var_value_type(self, name):
    frame = self.get_frame(name)
    return frame.get_var_value_type(name[3:])

  def set_tf_frame(self):
    self._tf = Frame()
  
  def push_frame(self):
    # check if the TF is initialised
    if self._tf == None:
      sys.stderr.write('Uninitialised temporary frame.\n')
      print('POOJ')
      exit(55)
    # pass the TF reference to LF
    self._lf = self._tf
    self._tf = None
    # push the LF to the stack
    self._lf_stack.append(self._lf)

  def pop_frame(self):
    # LF -> TF, pokud LF stack empty chyba 55
    # check if the lf_stack is not empty
    if not self._lf_stack:
      sys.stderr.write('LF stack is empty.\n')
      exit(55)
    self._tf = self._lf_stack.pop()
    if self._lf_stack:
      self._lf = self._lf_stack[-1] # top
    else:
      self._lf = None

class Frame:
  def __init__(self):
    self._frame_dict = {}

  def set_var(self, name, typ):
    # slouzi pro DEFVAR - hodnotu jeste nezname
    name = name[3:]
    if name in self._frame_dict:
      sys.stderr.write('Redefinition of variable ' + name + '.\n')
      exit(52)

    # mozna neni treba osetrovat (osetreno v parse.php)
    if typ != 'var':
      sys.stderr.write('Invalid DEFVAR operand type.\n')
      exit(-1)

    self._frame_dict[name] = None

  def set_var_value(self, name, value, valtype):
    # check if the var exists, then insert value
    name = name[3:]
    if not name in self._frame_dict:
      sys.stderr.write('Var ' + name + ' is not defined.\n')
      exit(54)
    
    #TODO podle typu priradit hodnotu
    if valtype == 'var':
      frame = prog.get_frame(value)
      self._frame_dict[name] = (frame.get_var_value(value[3:]), 'var')
      # kktina, potrebuju ziskat hodnotu dane promenne ze slovniku
      
    else:
      self._frame_dict[name] = (value, valtype)

  def get_var_value(self, name):
    # co udela kdyz tam promenna nebude? exception nebo vrati None? osetrit TODO
    if not name in self._frame_dict:
      sys.stderr.write('Var ' + name + ' is not defined.\n')
      exit(54)
    return self._frame_dict[name][0]

  def get_var_value_type(self, name):
    # co udela kdyz tam promenna nebude? exception nebo vrati None? osetrit TODO
    if not name in self._frame_dict:
      sys.stderr.write('Var ' + name + ' is not defined.\n')
      exit(54)
    return self._frame_dict[name]

  def get_frame_dict(self):
    return self._frame_dict

class Argument:

  def __init__(self, value, typ):
    if typ == 'string':
      if value == None:
        value = ''
      else:
        value = re.sub(r'\\([0-9]{3})', lambda x: chr(int(x[1])), value)
    self._value = value
    self._typ = typ

  def set_value(self, val):
    self._value = val

  def get_value(self):
    return self._value

  def get_type(self):
    return self._typ

class Instruction:

  def __init__(self, opcode):
    self._opcode = opcode
    self._args = [Argument, Argument, Argument]

  def get_opcode(self):
    return self._opcode

  def execute(self):
    pass
    #print('something default')

  def set_arg(self, arg_num, val, typ):
    self._args[arg_num - 1] = Argument(val, typ)

  def get_arg_value(self, arg_num):
    return self._args[arg_num - 1].get_value()

  def get_arg_value_type(self, arg_num):
    return self._args[arg_num - 1].get_value(), self._args[arg_num - 1].get_type()


class Move(Instruction):

  def __init__(self, arg1v, arg1t, arg2v, arg2t):
    super().__init__("MOVE")
    self.set_arg(1, arg1v, arg1t)
    self.set_arg(2, arg2v, arg2t)

  def execute(self):
    prog.set_var_value(self.get_arg_value(arg_num=1), self.get_arg_value_type(arg_num=2))

    
class Createframe(Instruction):
  def __init__(self):
    super().__init__("CREATEFRAME")

  def execute(self):
    #vytvori novy TF a zahodi obsah puvodniho TF
    prog.set_tf_frame()

class Pushframe(Instruction):
  def __init__(self):
    super().__init__("PUSHFRAME")

  def execute(self):
    #print('Executing pushframe.')
    prog.push_frame()

class Popframe(Instruction):
  def __init__(self):
    super().__init__("POPFRAME")

  def execute(self):
    #print('Executing popframe.')
    prog.pop_frame()

# class for the DEFVAR instruction
class Defvar(Instruction):
  def __init__(self, arg1v, arg1t):
    super().__init__("DEFVAR")
    self.set_arg(1, arg1v, arg1t)

  def execute(self):
    #print('Executing defvar.')
    # inserts new variable with None value in the frame
    prog.set_var(self.get_arg_value_type(arg_num=1))
    
# class for the CALL instruction
class Call(Instruction):
  def __init__(self, arg1v, arg1t):
    super().__init__("CALL")
    self.set_arg(1, arg1v, arg1t)

  def execute(self):
    #print('Executing call.')
    # save the current position
    prog.call_stack_push(prog.get_instr_counter())
    # jump to the label
    prog.set_instr_counter(prog.get_label_order(self.get_arg_value(arg_num=1)))


class Return(Instruction):
  def __init__(self):
    super().__init__("RETURN")

  def execute(self):
    #print('Executing return.')
    pos = prog.call_stack_pop()
    prog.set_instr_counter(pos)

class Pushs(Instruction):
  def __init__(self, arg1v, arg1t):
    super().__init__("PUSHS")
    self.set_arg(1, arg1v, arg1t)

  def execute(self):
    #print('Executing pushs.')
    # save to data stack
    prog.data_stack_push(self.get_arg_value_type(arg_num=1))

class Pops(Instruction):
  def __init__(self, arg1v, arg1t):
    super().__init__("POPS")
    self.set_arg(1, arg1v, arg1t)

  def execute(self):
    #print('Executing pops.')
    # check var
    (name, typ) = self.get_arg_value_type(1)
    prog.set_var_value(name, prog.data_stack_pop())
    

class Arithmetic(Instruction):
  def __init__(self, opcode, arg1v, arg1t, arg2v, arg2t, arg3v, arg3t):
    super().__init__(opcode)
    self.set_arg(1, arg1v, arg1t)
    self.set_arg(2, arg2v, arg2t)
    self.set_arg(3, arg3v, arg3t)

  def get_check_int_operand(self, arg_num):
    # checks if the operand is int and returns it
    (val, typ) = self.get_arg_value_type(arg_num=arg_num)
    if typ == 'var':
      try:
        var_name = val
        (val, typ) = prog.get_var_value_type(val)
      except TypeError:
        # TODO vypsat nil nebo error?
        sys.stderr.write('Variable ' + var_name + ' is not defined.\n')
        exit(54)
    if typ != 'int':
      sys.stderr.write(self.get_opcode() + ': wrong argument type.\n')
      exit(53)
    try:
      val = int(val)
    except ValueError:
      sys.stderr.write(self.get_opcode() + ': wrong argument type.\n')
      exit(32)  # or 53?
    return val

  def check_operand_type_eq(self):
    # return (val1, val2, typ)
    (val1, typ1) = self.get_arg_value_type(arg_num=2)
    (val2, typ2) = self.get_arg_value_type(arg_num=3)
    # TODO pridano - check, jestli to funguje ok
    if typ1 == 'var':
      try:  # muze byt None
        (val1, typ1) = prog.get_var_value_type(val1)
      except:
        sys.stderr.write(self.get_opcode() + ': variable is not defined.\n')
        exit(54)
    if typ2 == 'var':
      try:  # muze byt None
        (val1, typ1) = prog.get_var_value_type(val1)
      except:
        sys.stderr.write(self.get_opcode() + ': variable is not defined.\n')
        exit(54)
    if typ1 == typ2 == 'int':
      try:
        val1 = int(val1)
        val2 = int(val2)
      except ValueError:
        sys.stderr.write(self.get_opcode() + ': wrong operand type.\n')
        exit(53)
    elif  typ1 == typ2 == 'string':
      try:
        val1 = str(val1)
        val2 = str(val2)
      except ValueError:
        sys.stderr.write(self.get_opcode() + ': wrong operand type.\n')
        exit(53) 
    elif typ1 == typ2 == 'nil':
      if val1 != 'nil' and val2 != 'nil':
        sys.stderr.write(self.get_opcode() + ': wrong operand type.\n')
        exit(53)
    elif typ1 == typ2 == 'bool':
      if val1.upper() == 'TRUE':
        val1 = True
      else:
        val1 = False
      if val2.upper() == 'TRUE':
        val2 = True
      else:
        val2 = False
    else:
      sys.stderr.write(self.get_opcode() + ': wrong operand type.\n')
      exit(53)
    return (val1, val2, typ1)


class Add(Arithmetic):
  def __init__(self, arg1v, arg1t, arg2v, arg2t, arg3v, arg3t):
    super().__init__("ADD", arg1v, arg1t, arg2v, arg2t, arg3v, arg3t)

  def execute(self):
    # get and check the operands
    val1 = super().get_check_int_operand(arg_num=2)
    val2 = super().get_check_int_operand(arg_num=3)
    result = val1 + val2
    prog.set_var_value(self.get_arg_value(arg_num=1), (result, 'int'))

class Sub(Arithmetic):
  def __init__(self, arg1v, arg1t, arg2v, arg2t, arg3v, arg3t):
    super().__init__("SUB", arg1v, arg1t, arg2v, arg2t, arg3v, arg3t)

  def execute(self):
    val1 = super().get_check_int_operand(arg_num=2)
    val2 = super().get_check_int_operand(arg_num=3)
    result = val1 - val2
    prog.set_var_value(self.get_arg_value(arg_num=1), (result, 'int'))

class Mul(Arithmetic):
  def __init__(self, arg1v, arg1t, arg2v, arg2t, arg3v, arg3t):
    super().__init__("MUL", arg1v, arg1t, arg2v, arg2t, arg3v, arg3t)

  def execute(self):
    val1 = super().get_check_int_operand(arg_num=2)
    val2 = super().get_check_int_operand(arg_num=3)
    result = val1 * val2
    prog.set_var_value(self.get_arg_value(arg_num=1), (result, 'int'))

class Idiv(Arithmetic):
  def __init__(self, arg1v, arg1t, arg2v, arg2t, arg3v, arg3t):
    super().__init__("IDIV", arg1v, arg1t, arg2v, arg2t, arg3v, arg3t)

  def execute(self):
    val1 = super().get_check_int_operand(arg_num=2)
    val2 = super().get_check_int_operand(arg_num=3)
    try:
      result = val1 // val2
    except ZeroDivisionError:
      sys.stderr.write('Division by zero.\n')
      exit(57)
    prog.set_var_value(self.get_arg_value(arg_num=1), (result, 'int'))

class Lt(Arithmetic):
  def __init__(self, arg1v, arg1t, arg2v, arg2t, arg3v, arg3t):
    super().__init__("LT", arg1v, arg1t, arg2v, arg2t, arg3v, arg3t)

  def execute(self):
    (val1, val2, typ) = super().check_operand_type_eq()
    if typ == 'nil':
      sys.stderr.write(self.get_opcode() + ': wrong operand type.\n')
      exit(53)
    """
    result = 'false'
    if val1 < val2:
      result = 'true'
    """
    result = val1 < val2
    prog.set_var_value(self.get_arg_value(arg_num=1), (result, 'bool'))

class Gt(Arithmetic):
  def __init__(self, arg1v, arg1t, arg2v, arg2t, arg3v, arg3t):
    super().__init__("GT", arg1v, arg1t, arg2v, arg2t, arg3v, arg3t)

  def execute(self):
    (val1, val2, typ) = super().check_operand_type_eq()
    if typ == 'nil':
      sys.stderr.write(self.get_opcode() + ': wrong operand type.\n')
      exit(53)
    result = val1 > val2
    prog.set_var_value(self.get_arg_value(arg_num=1), (result, 'bool'))

class Eq(Arithmetic):
  def __init__(self, arg1v, arg1t, arg2v, arg2t, arg3v, arg3t):
    super().__init__("EQ", arg1v, arg1t, arg2v, arg2t, arg3v, arg3t)

  def execute(self):
    (val1, val2, typ) = super().check_operand_type_eq()
    result = False
    if typ == 'nil' or val1 == val2:
      result = True
    prog.set_var_value(self.get_arg_value(arg_num=1), (result, 'bool'))

class And(Arithmetic):
  def __init__(self, arg1v, arg1t, arg2v, arg2t, arg3v, arg3t):
    super().__init__("AND", arg1v, arg1t, arg2v, arg2t, arg3v, arg3t)

  def execute(self):
    (val1, val2, typ) = super().check_operand_type_eq()
    if typ != 'bool':
      sys.stderr.write(self.get_opcode() + ': wrong operand type.\n')
      exit(53)
    result = val1 and val2
    prog.set_var_value(self.get_arg_value(arg_num=1), (result, 'bool'))

class Or(Arithmetic):
  def __init__(self, arg1v, arg1t, arg2v, arg2t, arg3v, arg3t):
    super().__init__("OR", arg1v, arg1t, arg2v, arg2t, arg3v, arg3t)

  def execute(self):
    (val1, val2, typ) = super().check_operand_type_eq()
    if typ != 'bool':
      sys.stderr.write(self.get_opcode() + ': wrong operand type.\n')
      exit(53)
    result = val1 or val2
    prog.set_var_value(self.get_arg_value(arg_num=1), (result, 'bool'))

class Not(Instruction):
  def __init__(self, arg1v, arg1t, arg2v, arg2t):
    super().__init__("NOT")
    self.set_arg(1, arg1v, arg1t)
    self.set_arg(2, arg2v, arg2t)

  def execute(self):
    (val, typ) = self.get_arg_value_type(arg_num=2)
    if typ != 'bool':
      sys.stderr.write(self.get_opcode() + ': wrong operand type.\n')
      exit(53)
    val_bool = False
    if val.upper() == 'TRUE':
      val_bool = True
    result = not val_bool
    prog.set_var_value(self.get_arg_value(arg_num=1), (result, 'bool'))

class Int2char(Instruction):
  def __init__(self, arg1v, arg1t, arg2v, arg2t):
    super().__init__("INT2CHAR")
    self.set_arg(1, arg1v, arg1t)
    self.set_arg(2, arg2v, arg2t)

  def execute(self):
    (val, typ) = self.get_arg_value_type(arg_num=2)
    if typ == 'var':
      try:  # muze byt None
        (val, typ) = prog.get_var_value_type(val)
      except:
        sys.stderr.write(self.get_opcode() + ': variable is not defined.\n')
        exit(54)
    try:
      result = chr(int(val))
    except:
      sys.stderr.write('INT2CHAR: Invalid integer value.\n')
      exit(58)
    prog.set_var_value(self.get_arg_value(arg_num=1), (result, 'string'))

class Stri2int(Instruction):
  def __init__(self, arg1v, arg1t, arg2v, arg2t, arg3v, arg3t):
    super().__init__("STRI2INT")
    self.set_arg(1, arg1v, arg1t)
    self.set_arg(2, arg2v, arg2t)
    self.set_arg(3, arg3v, arg3t)

  def execute(self):
    # TODO osetrit None?
    (val1, typ1) = self.get_arg_value_type(arg_num=2)
    (val2, typ2) = self.get_arg_value_type(arg_num=3)
    if typ1 == 'var':
      try:  # muze byt None
        (val1, typ1) = prog.get_var_value_type(val1)
      except:
        sys.stderr.write(self.get_opcode() + ': variable is not defined.\n')
        exit(54)
    if typ2 == 'var':
      try:  # muze byt None
        (val1, typ1) = prog.get_var_value_type(val1)
      except:
        sys.stderr.write(self.get_opcode() + ': variable is not defined.\n')
        exit(54)
    if typ1 != 'string' and typ2 != 'int':
      sys.stderr.write('STRI2INT: Invalid operand type.\n')
      exit(53)
    try:
      result = ord(val1[int(val2)])
    except:
      sys.stderr.write('STRI2INT: Index out of range.\n')
      exit(58)
    # TypeError exception if invalid chr()?
    prog.set_var_value(self.get_arg_value(arg_num=1), (result, 'int'))


class Read(Instruction):

  def __init__(self, arg1v, arg1t, arg2v, arg2t):
    super().__init__("READ")
    #self.set_args2(arg1v, arg1t, arg2v, arg2t)
    self.set_arg(1, arg1v, arg1t)
    self.set_arg(2, arg2v, arg2t)

  def execute(self):
    # print('\nExecuting read.')
    #input_file = prog.get_input_file()
    if prog.get_input_file_pointer() == None:
    #if input_file == '<stdin>':
      try:
        inp = input()
      except ValueError:
        inp = None
    else:
      #try:
      #  f = open(input_file, "r")
      #except FileNotFoundError:
      #  sys.stderr.write('File ' + input_file + 'not found.\n')
      #  exit(11)
      inp = prog.get_input_file_pointer().readline()
      inp = inp.rstrip('\n')

    try:
      #inp = input_file.readline()
      if self.get_arg_value(arg_num=1) == 'int':    # FIXME why tady bylo 2 misto 1?
        inp = int(inp)
      elif self.get_arg_value(arg_num=1) == 'string':
        inp = str(inp)
      elif self.get_arg_value(arg_num=1) == 'bool':
        if inp.upper() == 'TRUE':
          inp = 'true'
        else:
          inp = 'false'
    except ValueError:
      inp = None
    prog.set_var_value(self.get_arg_value(arg_num=1), (inp, self.get_arg_value(arg_num=2)))

class Write(Instruction):
  def __init__(self, arg1v, arg1t):
    super().__init__("WRITE")
    self.set_arg(1, arg1v, arg1t)

  def execute(self):
    #print('Executing write.')
    # TODO catch exceptions napr. kdyz je promenna (111, 'string') nebo naopak
    (val, typ) = self.get_arg_value_type(arg_num=1)
    if typ == 'var':
      try:
        var_name = val
        #try:
        (val, typ) = prog.get_var_value_type(val)
        #except:
          #sys.stderr.write(self.get_opcode() + ': variable is not defined.\n')
          #exit(56)
      except TypeError:
        # TODO vypsat nil nebo error?
        sys.stderr.write('Variable ' + var_name + ' is not defined.\n')
        exit(54)
    if typ == 'nil':
      print('', end='')
    elif typ == 'bool':
      if val:
        print('true', end='')
      else:
        print('false', end='')
    elif typ == 'int':
      print(val, end='')
    else:
      print(val, end='')
      #print(re.sub(r'\\([0-9]{3})', lambda x: chr(int(x[1])), val), end='')

class Concat(Arithmetic):
  def __init__(self, arg1v, arg1t, arg2v, arg2t, arg3v, arg3t):
    super().__init__("CONCAT", arg1v, arg1t, arg2v, arg2t, arg3v, arg3t)

  def execute(self):
    (val1, val2, typ) = super().check_operand_type_eq()

    if typ != 'string':
      sys.stderr.write('CONCAT: wrong operand type.\n')
      exit(53)
    prog.set_var_value(self.get_arg_value(arg_num=1), (val1 + val2, 'string'))

class Strlen(Instruction):
  def __init__(self, arg1v, arg1t, arg2v, arg2t):
    super().__init__("STRLEN")
    self.set_arg(1, arg1v, arg1t)
    self.set_arg(2, arg2v, arg2t)

  def execute(self):
    (val, typ) = self.get_arg_value_type(arg_num=2)
    if typ == 'var':
      try:
        (val, typ) = prog.get_var_value_type(val)
      except:
        sys.stderr.write(self.get_opcode() + ': variable is not defined.\n')
        exit(54)
    if typ != 'string':
      sys.stderr.write('STRLEN: wrong operand type.\n')
      exit(53)
    try:
      result = len(val)
    except:
      sys.stderr.write('STRLEN: wrong operand type.\n')
      exit(53)
    prog.set_var_value(self.get_arg_value(arg_num=1), (result, 'int'))

class Getchar(Arithmetic):
  def __init__(self, arg1v, arg1t, arg2v, arg2t, arg3v, arg3t):
    super().__init__("GETCHAR", arg1v, arg1t, arg2v, arg2t, arg3v, arg3t)

  def execute(self):
    # TODO osetrit None?
    (val1, typ1) = self.get_arg_value_type(arg_num=2)
    (val2, typ2) = self.get_arg_value_type(arg_num=3)
    if typ1 == 'var':
      try:  # muze byt None
        (val1, typ1) = prog.get_var_value_type(val1)
      except:
        sys.stderr.write(self.get_opcode() + ': variable is not defined.\n')
        exit(54)
    if typ2 == 'var':
      try:  # muze byt None
        (val2, typ2) = prog.get_var_value_type(val2)
      except:
        sys.stderr.write(self.get_opcode() + ': variable is not defined.\n')
        exit(54)
    if typ1 != 'string' and typ2 != 'int':
      sys.stderr.write('GETCHAR: Invalid operand type.\n')
      exit(58)
    try:
      result = val1[int(val2)]
    except:
      sys.stderr.write('GETCHAR: Index out of range.\n')
      exit(58)
    # TypeError exception if invalid chr()?
    prog.set_var_value(self.get_arg_value(arg_num=1), (result, 'string'))

class Setchar(Arithmetic):
  def __init__(self, arg1v, arg1t, arg2v, arg2t, arg3v, arg3t):
    super().__init__("SETCHAR", arg1v, arg1t, arg2v, arg2t, arg3v, arg3t)

  def execute(self):
    # get the value of variable
    (var, typ) = self.get_arg_value_type(arg_num=1)
    (symb1_val, symb1_typ) = self.get_arg_value_type(arg_num=2)
    (symb2_val, symb2_typ) = self.get_arg_value_type(arg_num=3)
    if symb1_typ == 'var':
      try:
        (symb1_val, symb1_typ) = prog.get_var_value_type(symb1_val)
      except TypeError:
        sys.stderr.write('SETCHAR: variable is not defined.\n')
        exit(54)
    if symb2_typ == 'var':
      try:
        (symb2_val, symb2_typ) = prog.get_var_value_type(symb2_val)
      except TypeError:
        sys.stderr.write('SETCHAR: variable is not defined.\n')
        exit(54)
    if typ != 'var' and symb1_typ != 'int' and symb2_typ != 'string':
      sys.stderr.write('SETCHAR: wrong operand type.\n')
      exit(53)
    try:
      (var_val, var_typ) = prog.get_var_value_type(var)
    except TypeError:
      sys.stderr.write('SETCHAR: variable is not defined.\n')
      exit(54)
    if var_typ != 'string':
      sys.stderr.write('SETCHAR: wrong operand type.\n')
      exit(53)
    try:
      index = int(symb1_val)
      result = var_val[:index] + symb2_val[0] + var_val[(index+1):]
    except TypeError:
      sys.stderr.write('SETCHAR: index out of range.\n')
      exit(53)
    except ValueError:
      sys.stderr.write('SETCHAR: wrong operand type.\n')
      exit(53)
    prog.set_var_value(var, (result, 'string'))

class Type(Instruction):
  def __init__(self, arg1v, arg1t, arg2v, arg2t):
    super().__init__("TYPE")
    self.set_arg(1, arg1v, arg1t)
    self.set_arg(2, arg2v, arg2t)

  def execute(self):
    (symb_val, symb_typ) = self.get_arg_value_type(arg_num=2)
    if symb_typ == 'var':
      try:
        (var_val, var_typ) = prog.get_var_value_type(symb_val)
        symb_typ = var_typ
      except:
        # None - neinicializovana
        symb_typ = ''
    prog.set_var_value(self.get_arg_value(arg_num=1), (symb_typ, 'string'))
    
class Label(Instruction):
  def __init__(self, arg1v, arg1t, order):
    super().__init__("LABEL")
    self.set_arg(1, arg1v, arg1t)
    prog.add_label(arg1v, order)

  def execute(self):
    #print('Executing label (label does nothing).')
    pass
  
class Jump(Instruction):
  def __init__(self, arg1v, arg1t):
    super().__init__("JUMP")
    self.set_arg(1, arg1v, arg1t)

  def execute(self):
    # zmena rizeni toku programu
    #print('Executing jump.')
    prog.set_instr_counter(prog.get_label_order(self.get_arg_value(arg_num=1)))

class Jumpifeq(Instruction):
  def __init__(self, arg1v, arg1t, arg2v, arg2t, arg3v, arg3t):
    super().__init__("JUMPIFEQ")
    self.set_arg(1, arg1v, arg1t)
    self.set_arg(2, arg2v, arg2t)
    self.set_arg(3, arg3v, arg3t)

  def execute(self):
    # zmena rizeni toku programu
    (symb1_val, symb1_typ) = self.get_arg_value_type(arg_num=2)
    (symb2_val, symb2_typ) = self.get_arg_value_type(arg_num=3)
    if symb1_typ == 'var':
      try:  # muze byt None
        (symb1_val, symb1_typ) = prog.get_var_value_type(symb1_val)
      except:
        sys.stderr.write(self.get_opcode() + ': variable is not defined.\n')
        exit(54)
    if symb2_typ == 'var':
      try:  # muze byt None
        (symb2_val, symb2_typ) = prog.get_var_value_type(symb2_val)
      except:
        sys.stderr.write(self.get_opcode() + ': variable is not defined.\n')
        exit(54)
    if symb1_typ == symb2_typ:
      if symb1_typ == 'int':
        try:
          symb1_val = int(symb1_val)
          symb2_val = int(symb2_val)
        except TypeError:
          sys.stderr.write('Invalid int type in JUMPIFEQ.\n')
          exit(32)
      if symb1_val == symb2_val:
        prog.set_instr_counter(prog.get_label_order(self.get_arg_value(arg_num=1)))
    elif symb1_typ == 'nil' or symb2_typ == 'nil':
      #print('Not sure co s tim nilem')
      pass
    else:
      sys.stderr.write('JUMPIFEQ: wrong operand type.\n')
      exit(53)

class Jumpifneq(Instruction):
  def __init__(self, arg1v, arg1t, arg2v, arg2t, arg3v, arg3t):
    super().__init__("JUMPIFNEQ")
    self.set_arg(1, arg1v, arg1t)
    self.set_arg(2, arg2v, arg2t)
    self.set_arg(3, arg3v, arg3t)

  def execute(self):
    # zmena rizeni toku programu
    #print('Executing jump.')
    (symb1_val, symb1_typ) = self.get_arg_value_type(arg_num=2)
    (symb2_val, symb2_typ) = self.get_arg_value_type(arg_num=3)
    if symb1_typ == 'var':
      try:  # muze byt None
        (symb1_val, symb1_typ) = prog.get_var_value_type(symb1_val)
      except:
        sys.stderr.write(self.get_opcode() + ': variable is not defined.\n')
        exit(54)
    if symb2_typ == 'var':
      try:  # muze byt None
        (symb2_val, symb2_typ) = prog.get_var_value_type(symb2_val)
      except:
        sys.stderr.write(self.get_opcode() + ': variable is not defined.\n')
        exit(54)
    if symb1_typ == symb2_typ:
      if symb1_typ == 'int':
        try:
          symb1_val = int(symb1_val)
          symb2_val = int(symb2_val)
        except TypeError:
          sys.stderr.write('Invalid int type in JUMPIFEQ.\n')
          exit(32)
      if symb1_val != symb2_val:
        prog.set_instr_counter(prog.get_label_order(self.get_arg_value(arg_num=1)))
    elif symb1_typ == 'nil' or symb2_typ == 'nil':
      #print('Not sure co s tim nilem')
      pass
    else:
      sys.stderr.write('JUMPIFNEQ: wrong operand type.\n')
      exit(53)

class Exit(Instruction):
  def __init__(self, arg1v, arg1t):
      super().__init__("EXIT")
      self.set_arg(1, arg1v, arg1t)

  def execute(self):
    (val, typ) = self.get_arg_value_type(arg_num=1)
    try:
      exit_code = int(val)
    except ValueError:
      sys.stderr.write('Invalid EXIT number.\n')
      exit(57)
    if typ != 'int' or exit_code < 0 or exit_code > 49:
      sys.stderr.write('Invalid EXIT number.\n')
      exit(57)
    else:
      # TODO osetrit uzavreni souboru atd. -> pak return asi
      # je to vubec v Pythonu treba osetrovat?
      exit(exit_code)

class Dprint(Instruction):
  def __init__(self, arg1v, arg1t):
      super().__init__("DPRINT")
      self.set_arg(1, arg1v, arg1t)

  def execute(self):
    (val, typ) = self.get_arg_value_type(arg_num=1)
    sys.stderr.write(val + ' of type ' + typ + '\n')

class Break(Instruction):
  def __init__(self):
      super().__init__("BREAK")

  def execute(self):
    sys.stderr.write('Instruction: BREAK\nInstruction order: ' + prog.get_instr_counter() + '\n')
    sys.stderr.write('GF:\n')
    sys.stderr.write(prog.get_frame_dict('GF'))
    sys.stderr.write('\n')

class Factory:

  def check_args(opcode: str, root):
    # check if there are only arg1, arg2 and arg3 tags
        
    zero_arg = ['CREATEFRAME', 'PUSHFRAME', 'POPFRAME', 'RETURN', 'BREAK']
    one_arg = ['DEFVAR', 'CALL', 'PUSHS', 'POPS', 'WRITE', 'LABEL', 'JUMP', 'EXIT', 'DPRINT']
    two_args = ['MOVE', 'NOT', 'INT2CHAR', 'READ', 'STRLEN', 'TYPE']
    three_args = ['ADD', 'SUB', 'MUL', 'IDIV', 'LT', 'GT', 'EQ', 'AND', 'OR', 'STRI2INT',\
                  'CONCAT', 'GETCHAR', 'SETCHAR', 'JUMPIFEQ', 'JUMPIFNEQ']
    
    # check the number of args in opcode
    for child in root:
      if opcode in zero_arg:
        sys.stderr.write('Invalid arguments in instruction ' + opcode + '.\n')
        exit(32)
      elif opcode in one_arg:
        if child.tag != 'arg1':
          sys.stderr.write('Invalid arguments in instruction ' + opcode + '.\n')
          exit(32)
      elif opcode in two_args:
        if child.tag != 'arg1' and child.tag != 'arg2':
          sys.stderr.write('Invalid arguments in instruction ' + opcode + '.\n')
          exit(32)
      elif opcode in three_args:
        if child.tag != 'arg1' and child.tag != 'arg2' and child.tag != 'arg3':
          sys.stderr.write('Invalid arguments in instruction ' + opcode + '.\n')
          exit(32)
      else:
        sys.stderr.write('Invalid opcode ' + opcode + '.\n')
        exit(32)
    
    

  @classmethod
  def resolve(cls, opcode: str, root):
    opcode = opcode.upper()

    # check if there is not any invalid tag
    cls.check_args(opcode, root)

    try:
      if opcode == 'MOVE':
        return Move(root.find('arg1').text, root.find('arg1').attrib['type'],\
                    root.find('arg2').text, root.find('arg2').attrib['type'])
      elif opcode == 'CREATEFRAME':
        return Createframe()
      elif opcode == 'PUSHFRAME':
        return Pushframe()
      elif opcode == 'POPFRAME':
        return Popframe()
      elif opcode == 'DEFVAR':
        return Defvar(root.find('arg1').text, root.find('arg1').attrib['type'])
      elif opcode == 'CALL':
        return Call(root.find('arg1').text, root.find('arg1').attrib['type'])
      elif opcode == 'RETURN':
        return Return()
      elif opcode == 'PUSHS':
        return Pushs(root.find('arg1').text, root.find('arg1').attrib['type'])
      elif opcode == 'POPS':
        return Pops(root.find('arg1').text, root.find('arg1').attrib['type'])
      elif opcode == 'ADD':
        return Add(root.find('arg1').text, root.find('arg1').attrib['type'],\
                    root.find('arg2').text, root.find('arg2').attrib['type'],\
                    root.find('arg3').text, root.find('arg3').attrib['type'])
      elif opcode == 'SUB':
        return Sub(root.find('arg1').text, root.find('arg1').attrib['type'],\
                    root.find('arg2').text, root.find('arg2').attrib['type'],\
                    root.find('arg3').text, root.find('arg3').attrib['type'])
      elif opcode == 'MUL':
        return Mul(root.find('arg1').text, root.find('arg1').attrib['type'],\
                    root.find('arg2').text, root.find('arg2').attrib['type'],\
                    root.find('arg3').text, root.find('arg3').attrib['type'])
      elif opcode == 'IDIV':
        return Idiv(root.find('arg1').text, root.find('arg1').attrib['type'],\
                    root.find('arg2').text, root.find('arg2').attrib['type'],\
                    root.find('arg3').text, root.find('arg3').attrib['type'])
      elif opcode == 'LT':
        return Lt(root.find('arg1').text, root.find('arg1').attrib['type'],\
                    root.find('arg2').text, root.find('arg2').attrib['type'],\
                    root.find('arg3').text, root.find('arg3').attrib['type'])
      elif opcode == 'GT':
        return Gt(root.find('arg1').text, root.find('arg1').attrib['type'],\
                    root.find('arg2').text, root.find('arg2').attrib['type'],\
                    root.find('arg3').text, root.find('arg3').attrib['type'])
      elif opcode == 'EQ':
        return Eq(root.find('arg1').text, root.find('arg1').attrib['type'],\
                    root.find('arg2').text, root.find('arg2').attrib['type'],\
                    root.find('arg3').text, root.find('arg3').attrib['type'])
      elif opcode == 'AND':
        return And(root.find('arg1').text, root.find('arg1').attrib['type'], 
                    root.find('arg2').text, root.find('arg2').attrib['type'],\
                    root.find('arg3').text, root.find('arg3').attrib['type'])
      elif opcode == 'OR':
        return Or(root.find('arg1').text, root.find('arg1').attrib['type'],\
                    root.find('arg2').text, root.find('arg2').attrib['type'],\
                    root.find('arg3').text, root.find('arg3').attrib['type'])
      elif opcode == 'NOT':
        return Not(root.find('arg1').text, root.find('arg1').attrib['type'],\
                    root.find('arg2').text, root.find('arg2').attrib['type'])
      elif opcode == 'INT2CHAR':
        return Int2char(root.find('arg1').text, root.find('arg1').attrib['type'],\
                    root.find('arg2').text, root.find('arg2').attrib['type'])
      elif opcode == 'STRI2INT':
        return Stri2int(root.find('arg1').text, root.find('arg1').attrib['type'],\
                    root.find('arg2').text, root.find('arg2').attrib['type'],\
                    root.find('arg3').text, root.find('arg3').attrib['type'])
      elif opcode == 'READ':
        return Read(root.find('arg1').text, root.find('arg1').attrib['type'],\
                    root.find('arg2').text, root.find('arg2').attrib['type'])
      elif opcode == 'WRITE':
        return Write(root.find('arg1').text, root.find('arg1').attrib['type'])
      elif opcode == 'CONCAT':
        return Concat(root.find('arg1').text, root.find('arg1').attrib['type'],\
                    root.find('arg2').text, root.find('arg2').attrib['type'],\
                    root.find('arg3').text, root.find('arg3').attrib['type'])
      elif opcode == 'STRLEN':
        return Strlen(root.find('arg1').text, root.find('arg1').attrib['type'],\
                    root.find('arg2').text, root.find('arg2').attrib['type'])
      elif opcode == 'GETCHAR':
        return Getchar(root.find('arg1').text, root.find('arg1').attrib['type'],\
                    root.find('arg2').text, root.find('arg2').attrib['type'],\
                    root.find('arg3').text, root.find('arg3').attrib['type'])
      elif opcode == 'SETCHAR':
        return Setchar(root.find('arg1').text, root.find('arg1').attrib['type'],\
                    root.find('arg2').text, root.find('arg2').attrib['type'],\
                    root.find('arg3').text, root.find('arg3').attrib['type'])
      elif opcode == 'TYPE':
        return Type(root.find('arg1').text, root.find('arg1').attrib['type'],\
                    root.find('arg2').text, root.find('arg2').attrib['type'])
      elif opcode == 'EXIT':
        return Exit(root.find('arg1').text, root.find('arg1').attrib['type'])

      elif opcode == 'LABEL':
        return Label(root.find('arg1').text, root.find('arg1').attrib['type'],\
                    root.attrib['order'])
      elif opcode == 'JUMP':
        return Jump(root.find('arg1').text, root.find('arg1').attrib['type'])
      elif opcode == 'JUMPIFEQ':
        return Jumpifeq(root.find('arg1').text, root.find('arg1').attrib['type'],\
                    root.find('arg2').text, root.find('arg2').attrib['type'],\
                    root.find('arg3').text, root.find('arg3').attrib['type'])
      elif opcode == 'JUMPIFNEQ':
        return Jumpifneq(root.find('arg1').text, root.find('arg1').attrib['type'],\
                    root.find('arg2').text, root.find('arg2').attrib['type'],\
                    root.find('arg3').text, root.find('arg3').attrib['type'])
      elif opcode == 'DPRINT':
        return Dprint(root.find('arg1').text, root.find('arg1').attrib['type'])
      elif opcode == 'BREAK':
        return Break()
      else:
        sys.stderr.write('Invalid opcode ' + opcode + '.\n')
        exit(32)
    except AttributeError:
      sys.stderr.write('Invalid input XML.\n')
      exit(32)

def parse_arguments():
  ap = argparse.ArgumentParser(conflict_handler="resolve")
  ap.add_argument("--help", "-h", action='store_true')
  ap.add_argument("--source", nargs=1, action='append')
  ap.add_argument("--input", nargs=1, action='append')

  args = vars(ap.parse_args())  # dict with attributes
  
  if args['help']:
    if len(args) != 3 or args['input'] != None or args['source'] != None:
      sys.stderr.write('Invalid arguments.\n')
      exit(10)
    else:
      print('This script interprets an input file in XML representation.\n'\
            'Usage:\n'\
            '   python3.8 interpret.py [--input=file] [--source=file]\n'\
            '- at least one of the arguments must be specified, the second one\n'\
            '  can be taken from stdin.\n'
            '\n'\
            'Print help:\n'\
            'python3.8 interpret.py --help')
      exit(0)

  if args['source'] is None:
    if args['input'] is None:
      print("BADASS")
      exit(10)

    if len(args['input']) != 1:
      print("BADIDASS")
      exit(10)

    source_file = None
    input_file = args['input'][0][0]
    
  elif args['input'] is None:
    if args['source'] is None:
      print("BAD")
      exit(10)

    if len(args['source']) != 1:
      print("BADER")
      exit(10)

    input_file = None
    source_file = args['source'][0][0]
    
  elif len(args['source']) != 1 or len(args['input']) != 1:
    print("BAD1")
    exit(10)

  elif args['input'][0][0] == args['source'][0][0]:
    print("BAD2")
    exit(10)
  
  else:
    if os.path.exists(args['input'][0][0]):
      input_file = args['input'][0][0]
    else:
      exit(11)
    
    if os.path.exists(args['source'][0][0]):
      source_file = args['source'][0][0]
    else:
      exit(11)

  # source, input, if any of them is None -> means stdin
  return (source_file, input_file)




# xml load
def xml_load(source_file):

  tree = ElementTree()
  
  try:
    if source_file == None:  
      tree.parse(sys.stdin)
    else:
      tree.parse(source_file)
  except:
    sys.stderr.write('Invalid input XML.\n')
    exit(31)

  root = tree.getroot()

  # add right instruction (order : opcode)
  for child in root:
    if (child.tag != 'instruction'):
      sys.stderr.write('Invalid input XML.\n')
      exit(32)
    try:
      instr = Factory.resolve(child.attrib['opcode'], child)
      if (child.attrib['order'] in prog.get_instr_dict()) or (int(child.attrib['order']) < 0):
        sys.stderr.write('Invalid input XML file.\n')
        exit(32)
    except (KeyError, ValueError):
          exit(32)
    prog.add_instr(child.attrib['order'], instr)

  prog.sort()

  # DRUHA SECOND CAST PROGRAMU
  order_list = list(prog.get_instr_dict().keys())
  index = 0

  while index < len(order_list):
    #print(order_list[index])
    # set instruction counter to the order on current index
    prog.set_instr_counter(order_list[index])

    # execute the instruction
    ins = prog.get_instr_dict()[order_list[index]]
    ins.execute()

    # detect if the program flow changed -> change the index
    if prog.get_instr_counter() != order_list[index]:
      index = order_list.index(prog.get_instr_counter())
    
    # increment the program counter
    index += 1

# xml check

# xml2inst

# interpret instr







if __name__ == '__main__':

  (source_file, input_file) = parse_arguments() # returns (source_file, input_file)
  #parse_arguments()

  if input_file != None:
    try:
      input_file_pointer = open(input_file, "r")
    except FileNotFoundError:
      sys.stderr.write('File ' + input_file + 'not found.\n')
      exit(11)
  else:
    input_file_pointer = None
  
  prog = Program(input_file_pointer)

  xml_load(source_file)

  sys.stderr.write("Program successfully processed.\n")
  #print("\n\nProgram successfully processed.")


  #exit(blah)

  #source_file.close()
  #input_file.close()