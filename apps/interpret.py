# #################### interpret.py #################### #
#        Principles of Programming Languages (IPP)       #
#               Lucie Svobodova, xsvobo1x                #
#               xsvobo1x@stud.fit.vutbr.cz               #
#                        FIT BUT                         #
#                       2021/2022                        #
# ###################################################### #

# This script interprets an input file in XML representation.
# Usage:
#   python3.8 interpret.py [--input=file] [--source=file]
#   - at least one of the arguments must be specified, 
#   the second one is stdin then.
# Print help:
#   python3.8 interpret.py --help

import argparse
import sys
import os
import re
from unittest import result
from xml.etree.ElementTree import ElementTree

# Class Program is a singleton. It represents the input program
# and stores information about the analysis and interpretation.
class Program:

  # Program contructor.
  def __init__(self, input_file_pointer):
    self._instr_dict = {}       # instruction dictionary
    self._lf: Frame = None      # local frame that is current used
    self._tf: Frame = None      # temporary frame that is currently used
    self._gf = Frame()          # global frame
    self._lf_stack = []         # stack of local frames
    self._call_stack = []       # call stack
    self._instr_counter = 0     # instruction counter - stores current order
    self._label_dict = {}       # label dictionary
    self._input_file_pointer = input_file_pointer # pointer to the input file
    
  # Returns pointer to the input file.
  def get_input_file_pointer(self):
    return self._input_file_pointer
  
  # Adds label to the label dictionary.
  def add_label(self, name, order):
    if name in self._label_dict:
      sys.stderr.write('Label ' + name + ' already exists.\n')
      exit(52)
    self._label_dict[name] = order

  # Checks if label is defined.
  def check_if_label_exists(self, label_name):
    if not label_name in self._label_dict:
      sys.stderr.write('Label ' + label_name + ' doesn\'t exist.\n')
      exit(52)

  # Returns order of the label specified by label_name.
  def get_label_order(self, label_name):
    self.check_if_label_exists(label_name)
    return self._label_dict[label_name]

  # Returns current instruction order.
  def get_instr_counter(self):
    return self._instr_counter

  # Sets the instruction counter to the order specified by order.
  def set_instr_counter(self, order):
    self._instr_counter = order

  # Pushes order number to the call stack.
  def call_stack_push(self, order):
    self._call_stack.append(order)

  # Pops order number from the call stack.
  def call_stack_pop(self):
    try:
      return self._call_stack.pop()
    except IndexError:
      sys.stderr.write('Call stack is empty.\n')
      exit(56)      

  # Adds instruction to the instruction dictionary.
  def add_instr(self, order, instr):
    self._instr_dict[order] = instr

  # Returns instruction dictionary.
  def get_instr_dict(self):
    return self._instr_dict

  # Sorts the instruction dictionary by order number.
  def sort(self):
    try:
      self._instr_dict = {key:value for key, value in sorted(self._instr_dict.items(), key=lambda item: int(item[0]))}
    except ValueError:
      sys.stderr.write('Invalid input XML.\n')
      exit(32)      

  # Declares new variable (the type must be 'var').
  # Value and type of the variable is set to None.
  def set_var(self, name):
    try:
      frame = self.get_frame(name)
    except SystemExit as ex:
      sys.stderr.write(ex.args[0])
      exit(ex.args[1])
    # declare new variable in the frame
    try:
      frame.set_var(name)
    except SystemExit as ex:
      sys.stderr.write(ex.args[0])
      exit(ex.args[1])

  # Sets a variable specified by 'name' to (value, type).
  def set_var_value(self, name, value_type):
    value, typ = (value_type)
    try:
      frame = self.get_frame(name)
    except SystemExit as ex:
      sys.stderr.write(ex.args[0])
      exit(ex.args[1])
    try:
      frame.set_var_value(name, value, typ)
    except SystemExit as ex:
      sys.stderr.write(ex.args[0])
      exit(ex.args[1])

  # Returns the value of a variable specified by 'name'.
  def get_var_value(self, name):
    try:
      frame = self.get_frame(name)
    except SystemExit as ex:
      sys.stderr.write(ex.args[0])
      exit(ex.args[1])
    try:
      val = frame.get_var_value(name[3:]) # cut the frame name
    except SystemExit as ex:
      sys.stderr.write(ex.args[0])
      exit(ex.args[1])
    return val

  # Returns the value and type of a variable specified by 'name'.
  def get_var_value_type(self, name):
    try:
      frame = self.get_frame(name)
    except SystemExit as ex:
      sys.stderr.write(ex.args[0])
      exit(ex.args[1])
    try:
      valtype = frame.get_var_value_type(name[3:]) # cut the frame name
    except SystemExit as ex:
      sys.stderr.write(ex.args[0])
      exit(ex.args[1])
    return valtype

  # Returns frame specified by first two characters in frame_name.
  def get_frame(self, frame_name):
    if frame_name[0:2] == 'GF':
      # global frame
      return self._gf
    elif frame_name[0:2] == 'LF':
      # local frame
      if self._lf == None:
        raise SystemExit('Uninitialised local frame.\n', 55)
      return self._lf
    elif frame_name[0:2] == 'TF':
      # temporary frame
      if self._tf == None:
        raise SystemExit('Uninitialised temporary frame.\n', 55)
      return self._tf
    else:
      # invalid variable name - should not happen in the interpret
      raise SystemExit('Invalid variable/frame name.\n', 55)

  # Returns frame dictionary.
  def get_frame_dict(self, frame_name):
    try:
      frame = self.get_frame(frame_name)
    except SystemExit as ex:
      sys.stderr.write(ex.args[0])
      exit(ex.args[1])
    return frame.get_frame_dict()

  # Creates new temporary frame.
  def set_tf_frame(self):
    self._tf = Frame()
  
  # Pushes current temporary frame to the stack of local frames.
  # The temporary frame becomes local and new program temporary
  # frame will be unitialised.
  def push_frame(self):
    # check if the temporary frame is initialised
    if self._tf == None:
      sys.stderr.write('Uninitialised temporary frame.\n')
      exit(55)
    # pass the TF reference to LF
    self._lf = self._tf
    self._tf = None
    # push the LF to the stack
    self._lf_stack.append(self._lf)

  # Pops the local frame from the stack of local frames.
  # Popped frame becomes temporary frame. 
  def pop_frame(self):
    # check if the lf_stack is not empty
    try:
      self._tf = self._lf_stack.pop()
    except IndexError:
      sys.stderr.write('Stack of local frames is empty.\n')
      exit(55)
    # set local frame to frame on the top of the stack
    if self._lf_stack:
      self._lf = self._lf_stack[-1] # top
    else:
      self._lf = None


# Class Frame represents a frame. 
# It stores variables with its types and values in a frame dictionary.
class Frame:

  # Frame constructor.
  def __init__(self):
    self._frame_dict = {}

  # Returns frame dictionary.
  def get_frame_dict(self):
    return self._frame_dict

  # Declares new variable (the type must be 'var').
  # Value and type of the variable is set to None.
  def set_var(self, name):
    # check if the variable is in the frame dictionary
    name = name[3:]
    if name in self._frame_dict:
      raise SystemExit('Redefinition of variable ' + name + '.\n', 52)
    # add the variable and set its value and type to None
    self._frame_dict[name] = None

  # Sets a variable specified by 'name' to (value, type).
  def set_var_value(self, name, value, valtype):
    # check if the var exists in the frame dictionary
    name = name[3:]
    if name not in self._frame_dict:
      raise SystemExit('Var ' + name + ' is not declared.\n', 54)
    # check the value that should be set
    if valtype == 'var':
      try:
        frame = prog.get_frame(value)
      except SystemExit as ex:  # exception from frame.get_var_value
        raise ex
      try:
        self._frame_dict[name] = (frame.get_var_value(value[3:]), valtype)
      except KeyError:    # var is not in the frame dictionary
        raise SystemExit('Var ' + name + ' is not declared.\n', 54)
      except SystemExit as ex:  # exception from frame.get_var_value
        raise ex
    else:
      # set the variable to (value, valtype)
      try:
        self._frame_dict[name] = (value, valtype)
      except:    # var is not in the frame dictionary
        raise SystemExit('Var ' + name + ' is not declared.\n', 54)

  # Returns the value of a variable specified by 'name'.
  def get_var_value(self, name):
    try:
      return self._frame_dict[name][0]
    except TypeError:   # (value, type) is None
      raise SystemExit('Var ' + name + ' is not defined.\n', 56)
    except KeyError:    # var is not in the frame dictionary
      raise SystemExit('Var ' + name + ' is not declared.\n', 54)

  # Returns value and type of a variable specified by 'name'.
  def get_var_value_type(self, name):
    try:
      return self._frame_dict[name]
    except KeyError:
      raise SystemExit('Var ' + name + ' is not declared.\n', 54)


# Class Stack is a singleton. It represents the operand (data) stack.
class Stack():

  # Stack constructor.
  def __init__(self):
    self._operand_stack = []

  # Pushes an operand on the stack.
  def operand_stack_push(self, data):
    # TODO co treba retezec s escape sekvencemi
    # TODO co var? Nechat jako var nebo tam dat jeji hodnotu?
    (value, typ) = data
    if typ == 'var':
      # TODO opravit - check if var exists 
      prog.get_var_value(value)
    if typ == 'string':
      # check empty string
      if value == None:
        value = ''
      # convert escape sequences
      else:
        value = re.sub(r'\\([0-9]{3})', lambda x: chr(int(x[1])), value)
    if typ == 'bool':
      try:
        if value.upper() == 'TRUE':
          value = True
        else:
          value = False
      except AttributeError:
        pass
    self._operand_stack.append((value, typ))

  # Pops an operand from the stack.
  def operand_stack_pop(self):
    try:
      return self._operand_stack.pop()
    except IndexError:
      sys.stderr.write('Operand stack is empty.\n')
      exit(56)

  # Returns an operand stack.
  def get_operand_stack(self):
    return self._operand_stack

  # Pops and operand and check if it is an integer type.
  def pop_and_check_int(self):
    try:
      (op, op_type) = self.operand_stack_pop()
    except SystemExit as ex:
      sys.stderr.write(ex.args[0])
      exit(ex.args[1])
    if op_type == 'var':
      try:
        (op, op_type) = prog.get_var_value_type(op)
      except: # var value is None
        sys.stderr.write('Variable is not defined.\n')
        exit(54)
    if op_type != 'int':
      sys.stderr.write('Invalid operand type on the operand stack.\n')
      exit(53)
    try:
      op = int(op)
    except ValueError:
      sys.stderr.write('Invalid operand type on the operand stack.\n')
      exit(53)
    return op

  # Pops two operands from the stack and checks if their types are equal.
  def pop_2_check_types_eq(self):
    (val2, typ2) = self.operand_stack_pop()
    (val1, typ1) = self.operand_stack_pop()
    # if the operand is a variable -> get its value
    if typ1 == 'var':
      try:  
        (val1, typ1) = prog.get_var_value_type(val1)
      except TypeError:  # NoneType -> variable is not defined
        sys.stderr.write(self.get_opcode() + ': variable is not defined.\n')
        exit(56)
      except SystemExit as ex:  # variable is not declared
        sys.stderr.write(ex.args[0])
        exit(ex.args[1])
    if typ2 == 'var':
      try:
        (val1, typ1) = prog.get_var_value_type(val1)
      except TypeError: # NoneType -> variable is not defined (exit 56)
        sys.stderr.write('Variable is not defined.\n')
        exit(56)
      except SystemExit as ex:  # variable is not declared (exit 54)
        sys.stderr.write(ex.args[0])
        exit(ex.args[1])
    # check types equality
    if typ1 == typ2 == 'int':
      try:
        val1 = int(val1)
        val2 = int(val2)
      except ValueError:
        sys.stderr.write('Wrong operand type on the operand stack.\n')
        exit(53)
    elif  typ1 == typ2 == 'string':
      try:
        val1 = str(val1)
        val2 = str(val2)
      except ValueError:
        sys.stderr.write('Wrong operand type on the operand stack.\n')
        exit(53) 
    elif typ1 == 'nil' or typ2 == 'nil':
      pass
    elif typ1 == typ2 == 'bool':
      pass
    else:
      sys.stderr.write('Wrong operand type on the operand stack.\n')
      exit(53)
    return (val1, val2, typ1, typ2)


# Class Argument represents an argument of the opcode.
# It has its value and type.
class Argument:

  # Argument contructor.
  def __init__(self, value, typ):
    if typ == 'string':
      # check empty string
      if value == None:
        value = ''
      # convert escape sequences
      else:
        value = re.sub(r'\\([0-9]{3})', lambda x: chr(int(x[1])), value)
    if typ == 'bool':
      if value.upper() == 'TRUE':
        value = True
      else:
        value = False
    self._value = value
    self._typ = typ

  # Sets the value. 
  def set_value(self, val):
    self._value = val

  # Returns the value.
  def get_value(self):
    return self._value

  # Returns the type.
  def get_type(self):
    return self._typ

# Class Instruction represents the opcode. 
# It has its name and an array of arguments.
class Instruction:
  # Instruction constructor.
  def __init__(self, opcode):
    self._opcode = opcode
    self._args = [Argument, Argument, Argument]

  # Returns the name of the instruction (opcode).
  def get_opcode(self):
    return self._opcode

  # Sets the name and type to the argument specified by arg_num.
  def set_arg(self, arg_num, val, typ):
    self._args[arg_num - 1] = Argument(val, typ)

  # Returns value of the argument.
  def get_arg_value(self, arg_num):
    return self._args[arg_num - 1].get_value()

  # Returns type of the argument.
  def get_arg_type(self, arg_num):
    return self._args[arg_num - 1].get_type()

  # Returns value and type of the argument as a tuple (value, type).
  # If the argument is of type var, it returns its real value and type.
  def get_arg_value_type(self, arg_num):
    (value, typ) = self._args[arg_num - 1].get_value(), self._args[arg_num - 1].get_type()
    if typ == 'var':
      try:
        (value, typ) = prog.get_var_value_type(value)
      except TypeError:   # variable is not defined (exit 56)
        sys.stderr.write('Variable ' + value + ' is not defined.\n')
        exit(56)
    return (value, typ)


# Class Arithmetic is inherited from Instruction class.
# It is used for arithmetic instructions - ADD, MUL etc
# All arithmetic instructions have three operands.
class Arithmetic(Instruction):

  # Arithmetic instruction constructor.
  def __init__(self, opcode, arg1v, arg1t, arg2v, arg2t, arg3v, arg3t):
    super().__init__(opcode)
    self.set_arg(1, arg1v, arg1t)
    self.set_arg(2, arg2v, arg2t)
    self.set_arg(3, arg3v, arg3t)

  # Checks if the operand is integer and returns it.
  def get_check_int_operand(self, arg_num):
    (val, typ) = self.get_arg_value_type(arg_num=arg_num)
    # check integer type
    if typ != 'int':
      sys.stderr.write(self.get_opcode() + ': wrong argument type.\n')
      exit(53)
    # cast the value to integer
    try:
      val = int(val)
    except ValueError: # invalid input XML
      sys.stderr.write(self.get_opcode() + ': wrong argument type.\n')
      exit(32)  # TODO or 53?
    return val

  # Checks if two operands have equal type and returns them.
  def check_operand_type_eq(self):
    # get operands types and values
    (val1, typ1) = self.get_arg_value_type(arg_num=2)
    (val2, typ2) = self.get_arg_value_type(arg_num=3)
    # check types equality
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
    elif typ1 == typ2 == 'bool':
      pass
    elif typ1 == 'nil' or typ2 == 'nil':
      if typ1 == 'nil' and val1 != 'nil':
        sys.stderr.write(self.get_opcode() + ': wrong operand type.\n')
        exit(53)
      if typ2 == 'nil' and val2 != 'nil':
        sys.stderr.write(self.get_opcode() + ': wrong operand type.\n')
        exit(53)
    else:
      sys.stderr.write(self.get_opcode() + ': wrong operand type.\n')
      exit(53)
    return (val1, val2, typ1, typ2)

# Class Move represents MOVE instruction.
class Move(Instruction):

  # Move constructor.
  def __init__(self, arg1v, arg1t, arg2v, arg2t):
    super().__init__("MOVE")
    self.set_arg(1, arg1v, arg1t)
    self.set_arg(2, arg2v, arg2t)

  # Moves the value in arg_num=2 to arg_num=1.
  def execute(self):
    # TODO opravit
    if self.get_arg_type(arg_num=1) != 'var':
      sys.stderr.write('MOVE: Invalid operand\n')
      exit(53)
    prog.set_var_value(self.get_arg_value(arg_num=1), self.get_arg_value_type(arg_num=2))

# Class Createframe represents CREATEFRAME instruction.
class Createframe(Instruction):
  
  # Createframe constructor.
  def __init__(self):
    super().__init__("CREATEFRAME")

  # Creates an empty temporary frame.
  def execute(self):
    prog.set_tf_frame()

# Class Pushframe represents PUSHFRAME instruction.
class Pushframe(Instruction):

  # Pushframe constructor.
  def __init__(self):
    super().__init__("PUSHFRAME")

  # Pushes temporary frame on the stack of local frames.
  def execute(self):
    prog.push_frame()

# Class Popframe represents POPFRAME instruction.
class Popframe(Instruction):

  # Popframe constructor.
  def __init__(self):
    super().__init__("POPFRAME")

  # Pops frame from the stack of local frames.
  # Popped frame becomes temporary frame.
  def execute(self):
    prog.pop_frame()

# Class Defvar represents DEFVAR instruction.
class Defvar(Instruction):

  # Defvar constructor.
  def __init__(self, arg1v, arg1t):
    super().__init__("DEFVAR")
    self.set_arg(1, arg1v, arg1t)

  # Declares a new variable with None value.
  def execute(self):
    # TODO zkusit exceptions - jestli se to fakt ukonci nebo ne
    # TODO opravit
    (var_name, typ) = self.get_arg_value(arg_num=1), self.get_arg_type(arg_num=1)
    if typ != 'var':
      sys.stderr.write('DEFVAR: Invalid operand.\n')
      exit(53)
    prog.set_var(var_name)
    
# Class Call represents CALL instruction.
class Call(Instruction):

  # Call constructor.
  def __init__(self, arg1v, arg1t):
    super().__init__("CALL")
    self.set_arg(1, arg1v, arg1t)

  # Sets instruction counter to new position (specified by label).
  def execute(self):
    # push the current position to the call stack
    prog.call_stack_push(prog.get_instr_counter())
    # jump to the label
    prog.set_instr_counter(prog.get_label_order(self.get_arg_value(arg_num=1)))

# Class Return represents RETURN instruction.
class Return(Instruction):

  # Return constructor.
  def __init__(self):
    super().__init__("RETURN")

  # Sets instruction counter to the previous position (popped from the call stack).
  def execute(self):
    pos = prog.call_stack_pop()
    prog.set_instr_counter(pos)

# Class Pushs represents PUSHS instruction.
class Pushs(Instruction):

  # Pushs constructor.
  def __init__(self, arg1v, arg1t):
    super().__init__("PUSHS")
    self.set_arg(1, arg1v, arg1t)

  # Pushes an operand to the operand stack.
  def execute(self):
    stack.operand_stack_push(self.get_arg_value_type(arg_num=1))

# Class Pops represents POPS instruction.
class Pops(Instruction):

  # Pops constructor.
  def __init__(self, arg1v, arg1t):
    super().__init__("POPS")
    self.set_arg(1, arg1v, arg1t)

  # Pops an operand from the operand stack and stores it in a variable.
  def execute(self):
    name = self.get_arg_value(arg_num=1)
    prog.set_var_value(name, stack.operand_stack_pop())
    
# Class Clears represents CLEARS instruction.
class Clears(Instruction):

  # Clears constructor.
  def __init__(self):
      super().__init__("CLEARS")

  # Clears the operand stack.
  def execute(self):
    stack.get_operand_stack().clear()

# Class Adds represents ADDS instruction.
class Adds(Instruction):

  # Adds constructor.
  def __init__(self):
      super().__init__("ADDS")

  # TODO check co exceptions - jestli se ukonci program nebo je mam odchytit tady
  # Pops two operands from the operand stack, adds them
  # and pushes them back to the stack.
  def execute(self):
    op2 = stack.pop_and_check_int()
    op1 = stack.pop_and_check_int()
    result = op1 + op2
    stack.operand_stack_push((result, 'int'))

# Class Subs represents SUBS instruction.
class Subs(Instruction):

  # Subs constructor.
  def __init__(self):
      super().__init__("SUBS")

  # Pops two operands from the operand stack, subtracts them
  # and pushes them back to the stack.
  def execute(self):
    op2 = stack.pop_and_check_int()
    op1 = stack.pop_and_check_int()
    result = op1 - op2
    stack.operand_stack_push((result, 'int'))

# Class Muls represents MULS instruction.
class Muls(Instruction):

  # Muls constructor.
  def __init__(self):
      super().__init__("MULS")

  # Pops two operands from the operand stack, multiplies them
  # and pushes them back to the stack.
  def execute(self):
    op2 = stack.pop_and_check_int()
    op1 = stack.pop_and_check_int()
    result = op1 * op2
    stack.operand_stack_push((result, 'int'))

# Class Idivs represents IDIVS instruction.
class Idivs(Instruction):

  # Idivs constructor.
  def __init__(self):
      super().__init__("IDIVS")

  # Pops two operands from the operand stack, executes integer division
  # and pushes them back to the stack.
  def execute(self):
    op2 = stack.pop_and_check_int()
    op1 = stack.pop_and_check_int()
    try:
      result = op1 // op2
    except ZeroDivisionError:
      sys.stderr.write('IDIVS: Division by zero.\n')
      exit(57)
    stack.operand_stack_push((result, 'int'))

# Class Lts represents LTS instruction.
class Lts(Instruction):

  # Lts constructor.
  def __init__(self):
      super().__init__("LTS")

  # Pops two operands from the operand stack, checks if the first operand is lower
  # than the second one and pushes the boolean result back to the stack.
  def execute(self):
    (val1, val2, typ1, typ2) = stack.pop_2_check_types_eq()
    # nil is not supported in GTS operation
    if typ1 == 'nil' or typ2 == 'nil':
      sys.stderr.write(self.get_opcode() + ': wrong operand type on the operand stack.\n')
      exit(53)
    result = val1 < val2
    stack.operand_stack_push((result, 'bool'))

# Class Gts represents GTS instruction.
class Gts(Instruction):

  # Gts constructor.
  def __init__(self):
      super().__init__("LTS")

  # Pops two operands from the operand stack, checks if the first operand is greater
  # than the second one and pushes the boolean result back to the stack.
  def execute(self):
    (val1, val2, typ1, typ2) = stack.pop_2_check_types_eq()
    # nil is not supported in GTS operation
    if typ1 == 'nil' or typ2 == 'nil':
      sys.stderr.write(self.get_opcode() + ': wrong operand type on the operand stack.\n')
      exit(53)
    result = val1 > val2
    stack.operand_stack_push((result, 'bool'))

# Class Eqs represents EQS instruction.
class Eqs(Instruction):

  # Eqs constructor.
  def __init__(self):
      super().__init__("LTS")

  # Pops two operands from the operand stack, checks if they are equal
  # and pushes the boolean result back to the stack.
  def execute(self):
    (val1, val2, typ1, typ2) = stack.pop_2_check_types_eq()
    result = False
    if (typ1 == 'nil' and typ2 == 'nil') or val1 == val2:
      result = True
    stack.operand_stack_push((result, 'bool'))

# Class Ands represents ANDS instruction.
class Ands(Instruction):

  # Ands constructor.
  def __init__(self):
    super().__init__("ANDS")

  # Pops two operands from the operand stack, executes and operation
  # and pushes the boolean result back to the stack.
  def execute(self):
    (val1, val2, typ1, typ2) =  stack.pop_2_check_types_eq()
    if typ1 != 'bool' or typ2 != 'bool':
      sys.stderr.write('ANDS: wrong operand type on the operand stack.\n')
      exit(53)
    result = val1 and val2
    stack.operand_stack_push((result, 'bool'))

# Class Ors represents ORS instruction.
class Ors(Instruction):

  # Ors constructor.
  def __init__(self):
    super().__init__("ORS")

  # Pops two operands from the operand stack, executes or operation
  # and pushes the boolean result back to the stack.
  def execute(self):
    (val1, val2, typ1, typ2) =  stack.pop_2_check_types_eq()
    if typ1 != 'bool' or typ2 != 'bool':
      sys.stderr.write('ORS: wrong operand type on the operand stack.\n')
      exit(53)
    result = val1 or val2
    stack.operand_stack_push((result, 'bool'))

# Class Nots represents NOTS instruction.
class Nots(Instruction):

  # Nots constructor.
  def __init__(self):
    super().__init__("NOTS")

  # Pops an operand from the operand stack, executes not operation
  # and pushes the boolean result back to the stack.
  def execute(self):
    (val, typ) = stack.operand_stack_pop()
    if typ != 'bool':
      sys.stderr.write('NOTS: wrong operand type on the operand stack.\n')
      exit(53)
    # TODO check jestli to nevyhazuje vyjimku - pokud
    # je mam uz na stacku ulozene spravne, melo by toto byt nepotrebne
    # TODO check jestli je ukladam na stack spravne a mozna pridat 'pretypovani'
    # uz do ukladani argumentu v Instruction/Argument class
    # TODO opravit
    #val_bool = False
    #if val.upper() == 'TRUE':
    #  val_bool = True
    #result = not val_bool
    result = not val
    stack.operand_stack_push((result, 'bool'))

# Class Int2chars represents INT2CHARS instruction.
class Int2chars(Instruction):

  # Int2chars constructor.
  def __init__(self):
    super().__init__("INT2CHARS")

  # Pops an operand from the stack, checks if it is an integer, 
  # gets its character value and pushes the value back on the stack.
  # TODO check jestli vubec na operand stack davam variables nebo rovnou jejich hodnoty
  def execute(self):
    (val, typ) = stack.operand_stack_pop()
    if typ == 'var':
      try:
        (val, typ) = prog.get_var_value_type(val)
      except TypeError: # NoneType -> variable is not defined (exit 56)
        sys.stderr.write('Variable is not defined.\n')
        exit(56)
    # check integer type
    if typ != 'int':
      sys.stderr.write('INT2CHARS: Invalid integer value.\n')
      exit(58)
    try:  # get the character value
      result = chr(int(val))
    except: # not a valid value
      sys.stderr.write('INT2CHARS: Invalid value.\n')
      exit(58)
    stack.operand_stack_push((result, 'string'))

# Class Stri2ints represents STRI2INTS instruction.
class Stri2ints(Instruction):

  # Stri2ints constructor.
  def __init__(self):
    super().__init__("STRI2INTS")

  # Pops two operands from the operand stack. Check if the symb2 is integer
  # and symb1 string. Gets the character on index specified by symb2, 
  # converts it to its ordinal value and pushes the result back to the stack.
  def execute(self):
    # TODO check jestli mam spravne poradi
    val2 = stack.pop_and_check_int()  # check if the operand is integer
    (val1, typ1) = stack.operand_stack_pop()
    if typ1 == 'var':
      try:
        (val1, typ1) = prog.get_var_value_type(val1)
      except TypeError: # NoneType -> variable is not defined (exit 56)
        sys.stderr.write('Variable is not defined.\n')
        exit(56)
    if typ1 != 'string':
      sys.stderr.write('STRI2INTS: Invalid operand type.\n')
      exit(53)
    if val2 < 0 or val2 >= len(val1):
      sys.stderr.write('STRI2INTS: Index out of range.\n')
      exit(58)
    try:
      result = ord(val1[val2])
    except:
      sys.stderr.write('STRI2INTS: Index out of range.\n')
      exit(58)
    stack.operand_stack_push((result, 'int'))

# Class Jumpifeqs represents JUMPIFEQS instruction.
class Jumpifeqs(Instruction):

  # Jumpifeqs constructor.
  def __init__(self, arg1v, arg1t):
    super().__init__("JUMPIFEQS")
    self.set_arg(1, arg1v, arg1t)

  # Pops two operands from the operand stack, checks if they are equal
  # and if they are, jumps to the label specified by arg1.
  def execute(self):
    # check if the label is defined -> if not exit(52)
    prog.check_if_label_exists(self.get_arg_value(arg_num=1))
    # check operands
    (symb2_val, symb2_typ) = stack.operand_stack_pop()
    (symb1_val, symb1_typ) = stack.operand_stack_pop()
    # if the symbol is a variable, get its value and type
    if symb1_typ == 'var':
      try:
        (symb1_val, symb1_typ) = prog.get_var_value_type(symb1_val)
      except TypeError: # NoneType -> variable is not defined (exit 56)
        sys.stderr.write('Variable is not defined.\n')
        exit(56)
    if symb2_typ == 'var':
      try:
        (symb2_val, symb2_typ) = prog.get_var_value_type(symb2_val)
      except TypeError: # NoneType -> variable is not defined (exit 56)
        sys.stderr.write('Variable is not defined.\n')
        exit(56)
    # check if the symbols are equal
    if symb1_typ == symb2_typ:
      if symb1_typ == 'int':
        try:
          symb1_val = int(symb1_val)
          symb2_val = int(symb2_val)
        except TypeError:
          sys.stderr.write('JUMPIFEQS: wrong operand type.\n')
          exit(32)
      if symb1_val == symb2_val:
        prog.set_instr_counter(prog.get_label_order(self.get_arg_value(arg_num=1)))
    elif symb1_typ == 'nil' or symb2_typ == 'nil':
      if symb1_typ == symb2_typ:
        prog.set_instr_counter(prog.get_label_order(self.get_arg_value(arg_num=1)))
    else:
      sys.stderr.write('JUMPIFEQS: wrong operand type.\n')
      exit(53)

# Class Jumpifneqs represents JUMPIFNEQS instruction.
class Jumpifneqs(Instruction):

  # Jumpifneqs constructor.
  def __init__(self, arg1v, arg1t):
    super().__init__("JUMPIFNEQS")
    self.set_arg(1, arg1v, arg1t)

  # Pops two operands from the operand stack, checks if they are equal
  # and if they are not equal, jumps to the label specified by arg1.
  def execute(self):
    # check if the label is defined -> if not exit(52)
    prog.check_if_label_exists(self.get_arg_value(arg_num=1))
    # check operands
    (symb2_val, symb2_typ) = stack.operand_stack_pop()
    (symb1_val, symb1_typ) = stack.operand_stack_pop()
    # if the symbol is a variable, get its value and type
    if symb1_typ == 'var':
      try:
        (symb1_val, symb1_typ) = prog.get_var_value_type(symb1_val)
      except TypeError: # NoneType -> variable is not defined (exit 56)
        sys.stderr.write('Variable is not defined.\n')
        exit(56)
    if symb2_typ == 'var':
      try:
        (symb2_val, symb2_typ) = prog.get_var_value_type(symb2_val)
      except TypeError: # NoneType -> variable is not defined (exit 56)
        sys.stderr.write('Variable is not defined.\n')
        exit(56)
    # check if the operands are equal
    if symb1_typ == symb2_typ:
      if symb1_typ == 'int':
        try:
          symb1_val = int(symb1_val)
          symb2_val = int(symb2_val)
        except TypeError:
          sys.stderr.write('JUMPIFNEQS: wrong operand type.\n')
          exit(32)
      if symb1_val != symb2_val:
        prog.set_instr_counter(prog.get_label_order(self.get_arg_value(arg_num=1)))
    elif symb1_typ == 'nil' or symb2_typ == 'nil':
      if symb1_typ != symb2_typ:
        prog.set_instr_counter(prog.get_label_order(self.get_arg_value(arg_num=1)))
    else:
      sys.stderr.write('JUMPIFNEQS: wrong operand type.\n')
      exit(53)

# Class Add represents ADD instruction.
class Add(Arithmetic):

  # Add constructor.
  def __init__(self, arg1v, arg1t, arg2v, arg2t, arg3v, arg3t):
    super().__init__("ADD", arg1v, arg1t, arg2v, arg2t, arg3v, arg3t)

  # Adds two integer values and stores the result in variable specified by arg1.
  def execute(self):
    # get and check the operands
    val1 = super().get_check_int_operand(arg_num=2)
    val2 = super().get_check_int_operand(arg_num=3)
    result = val1 + val2
    prog.set_var_value(self.get_arg_value(arg_num=1), (result, 'int'))

# Class Sub represents SUB instruction.
class Sub(Arithmetic):

  # Sub constructor.
  def __init__(self, arg1v, arg1t, arg2v, arg2t, arg3v, arg3t):
    super().__init__("SUB", arg1v, arg1t, arg2v, arg2t, arg3v, arg3t)

  # Substracts two integer values and stores the result in variable specified by arg1.
  def execute(self):
    val1 = super().get_check_int_operand(arg_num=2)
    val2 = super().get_check_int_operand(arg_num=3)
    result = val1 - val2
    prog.set_var_value(self.get_arg_value(arg_num=1), (result, 'int'))

# Class Mul representas MUL instruction.
class Mul(Arithmetic):

  # Mul constructor.
  def __init__(self, arg1v, arg1t, arg2v, arg2t, arg3v, arg3t):
    super().__init__("MUL", arg1v, arg1t, arg2v, arg2t, arg3v, arg3t)

  # Multiplies two integer values and stores the result in variable specified by arg1.
  def execute(self):
    val1 = super().get_check_int_operand(arg_num=2)
    val2 = super().get_check_int_operand(arg_num=3)
    result = val1 * val2
    prog.set_var_value(self.get_arg_value(arg_num=1), (result, 'int'))

# Class Idiv represents IDIV istruction.
class Idiv(Arithmetic):

  # Idiv constructor.
  def __init__(self, arg1v, arg1t, arg2v, arg2t, arg3v, arg3t):
    super().__init__("IDIV", arg1v, arg1t, arg2v, arg2t, arg3v, arg3t)

  # Divides two integer values and stores the result in variable specified by arg1.
  def execute(self):
    val1 = super().get_check_int_operand(arg_num=2)
    val2 = super().get_check_int_operand(arg_num=3)
    try:
      result = val1 // val2
    except ZeroDivisionError:
      sys.stderr.write('Division by zero.\n')
      exit(57)
    prog.set_var_value(self.get_arg_value(arg_num=1), (result, 'int'))

# Class Lt represents LT istruction.
class Lt(Arithmetic):

  # Lt constructor.
  def __init__(self, arg1v, arg1t, arg2v, arg2t, arg3v, arg3t):
    super().__init__("LT", arg1v, arg1t, arg2v, arg2t, arg3v, arg3t)

  # Checks if arg2 value is lower than arg2 value and stores the boolean
  # result in variable specified by arg1.
  def execute(self):
    (val1, val2, typ1, typ2) = super().check_operand_type_eq()
    # nil is not supported in LT operation
    if typ1 == 'nil' or typ2 == 'nil':
      sys.stderr.write('LT: wrong operand type.\n')
      exit(53)
    result = val1 < val2
    prog.set_var_value(self.get_arg_value(arg_num=1), (result, 'bool'))

# Class Gt represents GT instruction.
class Gt(Arithmetic):

  # Gt constructor.
  def __init__(self, arg1v, arg1t, arg2v, arg2t, arg3v, arg3t):
    super().__init__("GT", arg1v, arg1t, arg2v, arg2t, arg3v, arg3t)

  # Checks if arg2 value is greater than arg2 value and stores the boolean
  # result in variable specified by arg1.
  def execute(self):
    (val1, val2, typ1, typ2) = super().check_operand_type_eq()
    # nil is not supported in GT operation
    if typ1 == 'nil' or typ2 == 'nil':
      sys.stderr.write('GT: wrong operand type.\n')
      exit(53)
    result = val1 > val2
    prog.set_var_value(self.get_arg_value(arg_num=1), (result, 'bool'))

# Class Eq represents EQ instruction.
class Eq(Arithmetic):

  # Eq constructor.
  def __init__(self, arg1v, arg1t, arg2v, arg2t, arg3v, arg3t):
    super().__init__("EQ", arg1v, arg1t, arg2v, arg2t, arg3v, arg3t)

  # Checks if arg2 value equals arg2 value and stores the boolean
  # result in variable specified by arg1.
  def execute(self):
    (val1, val2, typ1, typ2) = super().check_operand_type_eq()
    result = False
    if (typ1 == 'nil' and typ2 == 'nil') or val1 == val2:
      result = True
    prog.set_var_value(self.get_arg_value(arg_num=1), (result, 'bool'))

# Class And represents AND instruction.
class And(Arithmetic):

  # And constructor.
  def __init__(self, arg1v, arg1t, arg2v, arg2t, arg3v, arg3t):
    super().__init__("AND", arg1v, arg1t, arg2v, arg2t, arg3v, arg3t)

  # Checks if the operands are booleans and executes and operation.
  # Boolean result is stored in a variable specified by arg1.
  def execute(self):
    (val1, val2, typ1, typ2) = super().check_operand_type_eq()
    if typ1 != 'bool' or typ2 != 'bool':
      sys.stderr.write('AND: wrong operand type.\n')
      exit(53)
    result = val1 and val2
    prog.set_var_value(self.get_arg_value(arg_num=1), (result, 'bool'))

# Class Or represents OR instruction.
class Or(Arithmetic):

  # Or constructor.
  def __init__(self, arg1v, arg1t, arg2v, arg2t, arg3v, arg3t):
    super().__init__("OR", arg1v, arg1t, arg2v, arg2t, arg3v, arg3t)

  # Checks if the operands are booleans and executes or operation.
  # Boolean result is stored in a variable specified by arg1.
  def execute(self):
    (val1, val2, typ1, typ2) = super().check_operand_type_eq()
    if typ1 != 'bool' or typ2 != 'bool':
      sys.stderr.write('OR: wrong operand type.\n')
      exit(53)
    result = val1 or val2
    prog.set_var_value(self.get_arg_value(arg_num=1), (result, 'bool'))

# Class Not represents NOT instruction.
class Not(Instruction):

  # Not constructor.
  def __init__(self, arg1v, arg1t, arg2v, arg2t):
    super().__init__("NOT")
    self.set_arg(1, arg1v, arg1t)
    self.set_arg(2, arg2v, arg2t)

  # Checks if the operand is boolean and executes not operation.
  # Boolean result is stored in a variable specified by arg1.
  def execute(self):
    (val, typ) = self.get_arg_value_type(arg_num=2)
    if typ != 'bool':
      sys.stderr.write('NOT: wrong operand type.\n')
      exit(53)
    result = not val
    prog.set_var_value(self.get_arg_value(arg_num=1), (result, 'bool'))

# Class represents INT2CHAR instruction.
class Int2char(Instruction):

  # Int2char constructor.
  def __init__(self, arg1v, arg1t, arg2v, arg2t):
    super().__init__("INT2CHAR")
    self.set_arg(1, arg1v, arg1t)
    self.set_arg(2, arg2v, arg2t)

  # Checks if the arg2 is an integer, gets its character value
  # and stores the string result in a variable specified by arg1.
  def execute(self):
    (val, typ) = self.get_arg_value_type(arg_num=2)
    if typ != 'int':
      sys.stderr.write('INT2CHAR: Wrong operand type.\n')
      exit(53)
    try:
      val = int(val)
    except:
      sys.stderr.write('INT2CHAR: Wrong operand type.\n')
      exit(53)
    try:
      result = chr(val)
    except: # not a valid value
      sys.stderr.write('INT2CHAR: Invalid integer value.\n')
      exit(58)
    prog.set_var_value(self.get_arg_value(arg_num=1), (result, 'string'))

# Class Stri2int represents STRI2INT instruction.
class Stri2int(Instruction):
  
  # Stri2int constructor.
  def __init__(self, arg1v, arg1t, arg2v, arg2t, arg3v, arg3t):
    super().__init__("STRI2INT")
    self.set_arg(1, arg1v, arg1t)
    self.set_arg(2, arg2v, arg2t)
    self.set_arg(3, arg3v, arg3t)

  # Checks if arg2 is an integer and arg1 string. Gets the character on index
  # specified by arg2, converts it to its ordinal value and stores the integer
  # result in a variable specified by arg1.
  def execute(self):
    (val1, typ1) = self.get_arg_value_type(arg_num=2)
    (val2, typ2) = self.get_arg_value_type(arg_num=3)
    # check the types
    if typ1 != 'string' or typ2 != 'int':
      sys.stderr.write('STRI2INT: Invalid operand type.\n')
      exit(53)
    try:
      val2 = int(val2)
    except:
      sys.stderr.write('STRI2INT: Invalid operand type.\n')
      exit(53)
    if val2 < 0 or val2 >= len(val1):
      sys.stderr.write('STRI2INT: Index out of range.\n')
      exit(58)
    try:
      result = ord(val1[val2])
    except:   # invalid value, index out of range
      sys.stderr.write('STRI2INT: Index out of range.\n')
      exit(58)
    prog.set_var_value(self.get_arg_value(arg_num=1), (result, 'int'))

# Class Read represents READ instruction.
class Read(Instruction):

  # Read constructor.
  def __init__(self, arg1v, arg1t, arg2v, arg2t):
    super().__init__("READ")
    self.set_arg(1, arg1v, arg1t)
    self.set_arg(2, arg2v, arg2t)

  # Reads a value from the input file/stdin, converts the escape characters
  # and stores it to a variable specified by arg1.
  def execute(self):
    inp_type = self.get_arg_value(arg_num=2)
    # read from stdin
    if prog.get_input_file_pointer() == None:
      try:
        inp = input()
      except ValueError:
        inp = None
    else:
      # read from input file
      inp_line = prog.get_input_file_pointer().readline()
      inp = inp_line.rstrip('\n')
      if len(inp) == 0:
        if inp_type == 'string':
          if len(inp_line) != 0:
            inp = ''
          else:
            inp = None
        else:
          inp = None
    # check the input value type and converts it
    
    try:
      if inp == None:
        inp = 'nil'
        inp_type = 'nil'
      elif inp_type == 'int':
        inp = int(inp)
      elif inp_type == 'string':
          inp = str(inp)
      elif inp_type == 'bool':
        if inp.upper() == 'TRUE':
          inp = True
        else:
          inp = False
    except ValueError:  # invalid input
      inp = 'nil'
      inp_type = 'nil'
    prog.set_var_value(self.get_arg_value(arg_num=1), (inp, inp_type))

# Class Write represents WRITE instruction.
class Write(Instruction):

  # Write constructor.
  def __init__(self, arg1v, arg1t):
    super().__init__("WRITE")
    self.set_arg(1, arg1v, arg1t)

  # Prints the value specified by arg1 to the stdout.
  def execute(self):
    (val, typ) = self.get_arg_value_type(arg_num=1)
    # convert the value and print it
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

# Class Concat represents CONCAT instruction.
class Concat(Arithmetic):

  # Concat constructor.
  def __init__(self, arg1v, arg1t, arg2v, arg2t, arg3v, arg3t):
    super().__init__("CONCAT", arg1v, arg1t, arg2v, arg2t, arg3v, arg3t)

  # Concatenates two strings and stores it to the variable specified by arg1.
  def execute(self):
    (val1, val2, typ1, typ2) = super().check_operand_type_eq()
    if typ1 != 'string' or typ2 != 'string':
      sys.stderr.write('CONCAT: wrong operand type.\n')
      exit(53)
    try:
      val1 = str(val1)
      val2 = str(val2)
    except:
      sys.stderr.write('CONCAT: wrong operand type.\n')
      exit(53)
    prog.set_var_value(self.get_arg_value(arg_num=1), (val1 + val2, 'string'))

# Class Strlen represents STRLEN instruction.
class Strlen(Instruction):

  # Strlen constructor.
  def __init__(self, arg1v, arg1t, arg2v, arg2t):
    super().__init__("STRLEN")
    self.set_arg(1, arg1v, arg1t)
    self.set_arg(2, arg2v, arg2t)

  # Stores the length of arg2 string into the variable specified by arg1.
  def execute(self):
    (val, typ) = self.get_arg_value_type(arg_num=2)
    if typ != 'string':
      sys.stderr.write('STRLEN: wrong operand type.\n')
      exit(53)
    try:
      val = str(val)
      result = len(val)
    except:   # invalid type
      sys.stderr.write('STRLEN: wrong operand type.\n')
      exit(53)
    prog.set_var_value(self.get_arg_value(arg_num=1), (result, 'int'))

# Class Getchar represents GETCHAR instruction.
class Getchar(Arithmetic):

  # Getchar constructor.
  def __init__(self, arg1v, arg1t, arg2v, arg2t, arg3v, arg3t):
    super().__init__("GETCHAR", arg1v, arg1t, arg2v, arg2t, arg3v, arg3t)

  # Gets one character from string arg2 on index arg3 and stores the character
  # to a variable specified by arg1.
  def execute(self):
    (val1, typ1) = self.get_arg_value_type(arg_num=2)
    (val2, typ2) = self.get_arg_value_type(arg_num=3)
    # check the types
    if typ1 != 'string' or typ2 != 'int':
      sys.stderr.write('GETCHAR: Invalid operand type.\n')
      exit(53)
    try:
      val2 = int(val2)
    except:   # invalid type
      sys.stderr.write('GETCHAR: Invalid operand type.\n')
      exit(53)
    if val2 < 0 or val2 >= len(val1):
      sys.stderr.write('GETCHAR: Index out of range.\n')
      exit(58)
    try:
      result = val1[val2]
    except IndexError:   # index out of range
      sys.stderr.write('GETCHAR: Index out of range.\n')
      exit(58)
    prog.set_var_value(self.get_arg_value(arg_num=1), (result, 'string'))

# Class Setchar represents SETCHAR instruction. 
class Setchar(Arithmetic):

  # Setchar constructor.
  def __init__(self, arg1v, arg1t, arg2v, arg2t, arg3v, arg3t):
    super().__init__("SETCHAR", arg1v, arg1t, arg2v, arg2t, arg3v, arg3t)

  # Modifies a character in arg1 variable on index arg2 to the character 
  # specified by arg3.
  def execute(self):
    # check if the first operand is a variable
    if self.get_arg_type(arg_num=1) != 'var':
      sys.stderr.write('SETCHAR: Wrong operand type.\n')
      exit(53)
    # get values of the operands
    var = self.get_arg_value(arg_num=1)
    (symb1_val, symb1_typ) = self.get_arg_value_type(arg_num=2)
    (symb2_val, symb2_typ) = self.get_arg_value_type(arg_num=3)
    # check the types
    if symb1_typ != 'int' or symb2_typ != 'string':
      sys.stderr.write('SETCHAR: Wrong operand type.\n')
      exit(53)
    # get value of the variable var
    try:
      (var_val, var_typ) = prog.get_var_value_type(var)
    except TypeError: # NoneType -> variable is not defined (exit 56)
      sys.stderr.write('Variable is not defined.\n')
      exit(56)
    if var_typ != 'string':
      sys.stderr.write('SETCHAR: Wrong operand type.\n')
      exit(53)
    try:
      index = int(symb1_val)
      var_val = str(var_val)
    except:
      sys.stderr.write('SETCHAR: Wrong operand type.\n')
      exit(53)
    if index < 0 or index >= len(var_val):
      sys.stderr.write('SETCHAR: Index out of range.\n')
      exit(58)
    try:
      result = var_val[:index] + symb2_val[0] + var_val[(index+1):]
    except IndexError:
      sys.stderr.write('SETCHAR: Index out of range.\n')
      exit(58)
    except:
      sys.stderr.write('SETCHAR: Wrong operand type.\n')
      exit(53)
    prog.set_var_value(var, (result, 'string'))

# Class Type represents TYPE instruction.
class Type(Instruction):

  # Type constructor.
  def __init__(self, arg1v, arg1t, arg2v, arg2t):
    super().__init__("TYPE")
    self.set_arg(1, arg1v, arg1t)
    self.set_arg(2, arg2v, arg2t)

  # TODO opravit type
  # Gets the type of arg2 and stores it as a string to a variable specified by arg
  def execute(self):
    typ = self.get_arg_type(arg_num=2)
    if typ == 'var':
      try:
        (var_name, typ) = prog.get_var_value_type(self.get_arg_value(arg_num=2))
      except TypeError: # NoneType -> variable is not defined -> string = ''
        typ = '' 
    prog.set_var_value(self.get_arg_value(arg_num=1), (typ, 'string'))

# Class Label represents LABEL instruction.
class Label(Instruction):

  # Label constructor.
  def __init__(self, arg1v, arg1t, order):
    super().__init__("LABEL")
    self.set_arg(1, arg1v, arg1t)
    prog.add_label(arg1v, order)

  # Label does nothing when executing.
  def execute(self):
    pass
  
# Class Jump represents JUMP instruction.
class Jump(Instruction):

  # Jump constructor.
  def __init__(self, arg1v, arg1t):
    super().__init__("JUMP")
    self.set_arg(1, arg1v, arg1t)

  # Sets the instruction counter to the label specified by arg1.
  def execute(self):
    prog.set_instr_counter(prog.get_label_order(self.get_arg_value(arg_num=1)))

# Class Jumpifeq represents JUMPIFEQ instruction.
class Jumpifeq(Instruction):

  # Jumpifeq constructor.
  def __init__(self, arg1v, arg1t, arg2v, arg2t, arg3v, arg3t):
    super().__init__("JUMPIFEQ")
    self.set_arg(1, arg1v, arg1t)
    self.set_arg(2, arg2v, arg2t)
    self.set_arg(3, arg3v, arg3t)

  # Checks if arg2 and arg3 are equal and if they are, jumps 
  # to the label specified by arg1.
  def execute(self):
    # check if the label is defined -> if not exit(52)
    prog.check_if_label_exists(self.get_arg_value(arg_num=1))
    # check operands
    (symb1_val, symb1_typ) = self.get_arg_value_type(arg_num=2)
    (symb2_val, symb2_typ) = self.get_arg_value_type(arg_num=3)
    # check the types and values
    if symb1_typ == symb2_typ:
      if symb1_typ == 'int':
        try:
          symb1_val = int(symb1_val)
          symb2_val = int(symb2_val)
        except TypeError:
          sys.stderr.write('Invalid int type in JUMPIFEQ.\n')
          exit(53)
      if symb1_val == symb2_val:
        prog.set_instr_counter(prog.get_label_order(self.get_arg_value(arg_num=1)))
    elif symb1_typ == 'nil' or symb2_typ == 'nil':
      if symb1_typ == symb2_typ:
        prog.set_instr_counter(prog.get_label_order(self.get_arg_value(arg_num=1)))
    else:
      sys.stderr.write('JUMPIFEQ: wrong operand type.\n')
      exit(53)

# Class Jumpifneq represents JUMPIFNEQ instruction.
class Jumpifneq(Instruction):

  # Jumpifneq constructor.
  def __init__(self, arg1v, arg1t, arg2v, arg2t, arg3v, arg3t):
    super().__init__("JUMPIFNEQ")
    self.set_arg(1, arg1v, arg1t)
    self.set_arg(2, arg2v, arg2t)
    self.set_arg(3, arg3v, arg3t)

  # Checks if arg2 and arg3 are equal and if they are not, jumps 
  # to the label specified by arg1.
  def execute(self):
    # check if the label is defined -> if not exit(52)
    prog.check_if_label_exists(self.get_arg_value(arg_num=1))
    # check operands
    (symb1_val, symb1_typ) = self.get_arg_value_type(arg_num=2)
    (symb2_val, symb2_typ) = self.get_arg_value_type(arg_num=3)
    if symb1_typ == symb2_typ:
      if symb1_typ == 'int':
        try:
          symb1_val = int(symb1_val)
          symb2_val = int(symb2_val)
        except TypeError:
          sys.stderr.write('Invalid int type in JUMPIFEQ.\n')
          exit(53)
      if symb1_val != symb2_val:
        prog.set_instr_counter(prog.get_label_order(self.get_arg_value(arg_num=1)))
    elif symb1_typ == 'nil' or symb2_typ == 'nil':
      if symb1_typ != symb2_typ:
        prog.set_instr_counter(prog.get_label_order(self.get_arg_value(arg_num=1)))
    else:
      sys.stderr.write('JUMPIFNEQ: wrong operand type.\n')
      exit(53)

# Class Exit represents EXIT instruction.
class Exit(Instruction):

  # Exit constructor.
  def __init__(self, arg1v, arg1t):
      super().__init__("EXIT")
      self.set_arg(1, arg1v, arg1t)

  # Exits the program with a specified exit number.
  def execute(self):
    (val, typ) = self.get_arg_value_type(arg_num=1)
    try:
      exit_code = int(val)
    except ValueError:
      sys.stderr.write('Invalid EXIT number.\n')
      exit(53)
    if typ != 'int':
      sys.stderr.write('Invalid EXIT number.\n')
      exit(53)
    # integer number must be 0 - 49 -> else exit(57)
    if exit_code < 0 or exit_code > 49:
      sys.stderr.write('Invalid EXIT number.\n')
      exit(57)
    else:
      exit(exit_code)

# Class Dprint represents DPRINT instruction.
class Dprint(Instruction):

  # Dprint constructor.
  def __init__(self, arg1v, arg1t):
      super().__init__("DPRINT")
      self.set_arg(1, arg1v, arg1t)

  # Prints arg1 to the stderr.
  def execute(self):
    (val, typ) = self.get_arg_value_type(arg_num=1)
    sys.stderr.write(val + ' of type ' + typ + '\n')

# Class Break represents BREAK instruction.
class Break(Instruction):

  # Break constructor.
  def __init__(self):
      super().__init__("BREAK")

  # Prints instruction order and the variables in global frame to the stderr.
  def execute(self):
    sys.stderr.write('Instruction: BREAK\nInstruction order: ' + prog.get_instr_counter() + '\n')
    sys.stderr.write('GF:\n')
    sys.stderr.write(prog.get_frame_dict('GF'))
    sys.stderr.write('\n')


# --------------------------------------------------------------------------------
# Factory class for creating instances of the instructions.
class Factory:

  # Checks if there are any invalid args inside the instruction.
  def check_args(opcode: str, root):
    # number of arguments in the opcode
    zero_arg = ['CREATEFRAME', 'PUSHFRAME', 'POPFRAME', 'RETURN', 'BREAK', 'CLEARS', 'ADDS',\
                'SUBS', 'MULS', 'IDIVS', 'LTS', 'GTS', 'EQS', 'ANDS', 'ORS', 'NOTS',\
                'INT2CHARS', 'STRI2INTS']
    one_arg = ['DEFVAR', 'CALL', 'PUSHS', 'POPS', 'WRITE', 'LABEL', 'JUMP', 'EXIT', 'DPRINT',\
              'JUMPIFEQS', 'JUMPIFNEQS']
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

    # check arg types
    operands = ['var', 'label', 'type', 'int', 'string', 'bool', 'nil']
    if opcode not in zero_arg:
      # check if the arg is var, label, type, int, string, bool, nil
      try:
        if root.find('arg1').attrib['type']:
          if root.find('arg1').attrib['type'] not in operands:
            sys.stderr.write('Invalid operand type in arg1.\n')
            exit(32)
        elif root.find('arg2').attrib['type']:
          if root.find('arg2').attrib['type'] not in operands:
            sys.stderr.write('Invalid operand type in arg2.\n')
            exit(32)
        elif root.find('arg3').attrib['type']:
          if root.find('arg3').attrib['type'] not in operands:
            sys.stderr.write('Invalid operand type in arg3.\n')
            exit(32)
      except AttributeError:
        sys.stderr.write('Invalid input XML.\n')
        exit(32)

  # Resolves the intruction specified by 'opcode' and call its constructor.
  @classmethod
  def resolve(cls, opcode: str, root):
    opcode = opcode.upper()
    # check if all args are valid
    cls.check_args(opcode, root)
    #resolve the instruction
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
      elif opcode == 'CLEARS':
        return Clears()
      elif opcode == 'ADDS':
        return Adds()
      elif opcode == 'SUBS':
        return Subs()
      elif opcode == 'MULS':
        return Muls()
      elif opcode == 'IDIVS':
        return Idivs()
      elif opcode == 'LTS':
        return Lts()
      elif opcode == 'GTS':
        return Gts()
      elif opcode == 'EQS':
        return Eqs()
      elif opcode == 'ANDS':
        return Ands()
      elif opcode == 'ORS':
        return Ors()
      elif opcode == 'NOTS':
        return Nots()
      elif opcode == 'INT2CHARS':
        return Int2chars()
      elif opcode == 'STRI2INTS':
        return Stri2ints()
      elif opcode == 'JUMPIFEQS':
        return Jumpifeqs(root.find('arg1').text, root.find('arg1').attrib['type'])
      elif opcode == 'JUMPIFNEQS':
        return Jumpifneqs(root.find('arg1').text, root.find('arg1').attrib['type'])
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


# --------------------------------------------------------------------------------
# Function prints help to the stdout.
def print_help():
  print('This script interprets an input file in XML representation.\n'\
            'Usage:\n'\
            '   python3.8 interpret.py [--input=file] [--source=file]\n'\
            '- at least one of the arguments must be specified, the second one\n'\
            '  is stdin then.\n'
            '\n'\
            'Print help:\n'\
            'python3.8 interpret.py --help')


# Function parses command line arguments.
# Returns a tuple (source_file, input_file).Stdin is represented as None in th tuple.
def parse_arguments():
  ap = argparse.ArgumentParser(conflict_handler="resolve")
  ap.add_argument("--help", "-h", action='store_true')
  ap.add_argument("--source", nargs=1, action='append')
  ap.add_argument("--input", nargs=1, action='append')
  # create a dictionary with options
  args = vars(ap.parse_args())  

  # check if --help option is present
  if args['help']:
    if len(args) != 3 or args['input'] != None or args['source'] != None:
      print_help()
      sys.stderr.write('Invalid arguments.\n')
      exit(10)
    else:
      print_help()
      exit(0)

  # check if the combination of arguments is valid
  if args['source'] is None:
    if args['input'] is None:
      exit(10)
    if len(args['input']) != 1:
      exit(10)
    source_file = None  # stdin
    # check if the input file exists
    if os.path.exists(args['input'][0][0]):
      input_file = args['input'][0][0]
    else:
      exit(11)
  elif args['input'] is None:
    if args['source'] is None:
      exit(10)
    if len(args['source']) != 1:
      exit(10)
    input_file = None # stdin
    # check if the source file exists
    if os.path.exists(args['source'][0][0]):
      source_file = args['source'][0][0]
    else:
      exit(11)
  elif len(args['source']) != 1 or len(args['input']) != 1:
    exit(10)
  elif args['input'][0][0] == args['source'][0][0]:
    exit(10)
  else:
    # check if the files exist
    if os.path.exists(args['input'][0][0]):
      input_file = args['input'][0][0]
    else:
      exit(11)
    if os.path.exists(args['source'][0][0]):
      source_file = args['source'][0][0]
    else:
      exit(11)

  # return (source, input), stdin is represented as None
  return (source_file, input_file)


# Function loads the input XML file into a tree. I resolves the instructions, stores them
# to the program instructions dictionary. Afterwards they are sorted by order number.
def xml_load(source_file):
  # parse the XML file to the tree
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

  # resolve the instructions
  for child in root:
    if (child.tag != 'instruction'):
      sys.stderr.write('Invalid input XML.\n')
      exit(32)
    try:
      instr = Factory.resolve(child.attrib['opcode'], child)
      # check XML structure
      if (child.attrib['order'] in prog.get_instr_dict()) or (int(child.attrib['order']) < 0):
        sys.stderr.write('Invalid input XML file.\n')
        exit(32)
    except (KeyError, ValueError):  # invalid XML structure
      exit(32)
    # add the instruction to the program instruction dictionary
    prog.add_instr(child.attrib['order'], instr)

  # sort the instruction dictionary by order number
  prog.sort()


# Function parses the XML file, creates Instruction objects in a Factory
# stores them to the Program instruction dictionary and executes them afterwards. 
def interpret(source_file):
  # load XML file to the Program instruction dictionary
  xml_load(source_file)

  # interpret the instructions
  order_list = list(prog.get_instr_dict().keys())   # sorted instructions list
  pos = 0                                           # current position in the list

  while pos < len(order_list):
    # set instruction counter to the order on current index
    prog.set_instr_counter(order_list[pos])

    # execute the instruction
    ins = prog.get_instr_dict()[order_list[pos]]
    ins.execute()

    # detect if the program flow changed -> change the index
    if prog.get_instr_counter() != order_list[pos]:
      pos = order_list.index(prog.get_instr_counter())
    
    # increment the program counter
    pos += 1


# Main function.
if __name__ == '__main__':

  # parse command line arguments - get the source and input file
  (source_file, input_file) = parse_arguments()

  # open the input file
  if input_file != None:
    try:
      input_file_pointer = open(input_file, "r")
    except FileNotFoundError:
      sys.stderr.write('File ' + input_file + 'not found.\n')
      exit(11)
  else:
    input_file_pointer = None
  
  # create an instance of Program ans Stack (operand stack)
  prog = Program(input_file_pointer)
  stack = Stack()

  # interpret the instructions
  interpret(source_file)

  # close the input file and exit
  if input_file != None:
    input_file_pointer.close()
  exit(0)
