import argparse
#from posixpath import supports_unicode_filenames
import sys
import os
from traceback import print_tb
from xml.etree.ElementTree import ElementTree

class Program:
  # attributes:
  """
  gf: Frame
  lf: Frame
  tf: Frame
  lf_list: []
  instr_dict: {}
  """
  def __init__(self):
    self._instr_dict = {}
    self._lf: Frame = None
    self._tf: Frame = None
    self._gf = Frame()
    self._lf_stack = []
    self._call_stack = []
    self._instr_counter = 0 # ma v sobe order, ne index pole!!!
    self._label_dict = {}
    
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

  def add_instr(self, order, instr):
    self._instr_dict[order] = instr

  def get_instr_dict(self):
    return self._instr_dict

  def sort(self):
    self._instr_dict = {key:value for key, value in sorted(self._instr_dict.items(), key=lambda item: int(item[0]))}

  def get_frame(self, frame_name):
    # cut the oznaceni a pak rozhodni
    if frame_name[0:2] == 'GF':
      return self._gf
    elif frame_name[0:2] == 'LF':
      if self._lf == None:
        sys.stderr.write('Uninitialised local frame.\n')
        exit(55)
      print("LF dict: ")
      print(self._lf.get_frame_dict())
      return self._lf
    elif frame_name[0:2] == 'TF':
      if self._tf == None:
        sys.stderr.write('Uninitialised temporary frame.\n')
        exit(55)
      print("TF dict: ")
      print(self._tf.get_frame_dict())
      return self._tf
    else:
      exit(-1)  # TODO nemelo by nastat ale

  def get_frame_dict(self, frame_name):
    # TODO remove - just for debug
    if frame_name[0:2] == 'TF' and self._tf == None:
      return {}
    if frame_name[0:2] == 'LF' and self._lf == None:
      return {}
    # TODO don't remove
    return self.get_frame(frame_name).get_frame_dict()

  def set_var(self, name_type):
    name, typ = (name_type)
    print(name + "TYP: " + typ)
    self.get_frame(name).set_var(name, typ)

  def set_var_value(self, name, value_type):
    value, typ = (value_type)
    self.get_frame(name).set_var_value(name, value, typ)

  def set_tf_frame(self):
    self._tf = Frame()
  
  def push_frame(self):
    # check if the TF is initialised
    if self._tf == None:
      sys.stderr.write('Uninitialised temporary frame.\n')
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
    #print("Frame init\n")
    self._frame_dict = {}

  def set_var(self, name, typ):
    # slouzi pro DEFVAR - hodnotu jeste nezname
    # osetrit, zda tam jeste 'name' neni
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
      self._frame_dict[name] = prog.get_frame(value).get_var_value(value[3:])
      #self._frame_dict[name] = self.get_var_value(value[3:]) #self._frame_dict[value[3:]]
      # kktina, potrebuju ziskat hodnotu dane promenne ze slovniku
      
    else:
      self._frame_dict[name] = value

  def get_var_value(self, name):
    # co udela kdyz tam promenna nebude? exception nebo vrati None? osetrit TODO
    if not name in self._frame_dict:
      sys.stderr.write('Var ' + name + ' is not defined.\n')
      exit(54)

    return self._frame_dict[name]

  def get_frame_dict(self):
    return self._frame_dict

class Argument:

  def __init__(self, value, typ):
    # self._typ = typ
    self._value = value
    self._typ = typ
    #print("Argument init")

  def set_value(self, arg1):
    self._value = arg1

  def get_value(self):
    return self._value

  def get_type(self):
    return self._typ

class Instruction:

  def __init__(self, opcode):
    self._opcode = opcode
    self._arg1: Argument
    self._arg2: Argument
    self._arg3: Argument

  def get_opcode(self):
    return self._opcode

  def execute(self):
    print('something default')

  def set_arg1(self, value, typ):
    self._arg1 = Argument(value, typ)
    #self._arg1.set_value(arg1)
    #self._arg1 = arg1

  def set_arg2(self, value, typ):
    #self._arg2 = arg2
    self._arg2 = Argument(value, typ)
    #self._arg2.set_value(arg2)
    

  def set_arg3(self, value, typ):
    #self._arg3 = arg3
    self._arg3 = Argument(value, typ)
    #self._arg3.set_value(arg3)

  def set_args2(self, value1, typ1, value2, typ2):
    self._arg1 = Argument(value1, typ1)
    self._arg2 = Argument(value2, typ2)

  def set_args3(self, value1, typ1, value2, typ2, value3, typ3):
    self._arg1 = Argument(value1, typ1)
    self._arg2 = Argument(value2, typ2)
    self._arg3 = Argument(value3, typ3)

  def get_arg1_value(self):
    return self._arg1.get_value()

  def get_arg1_value_type(self):
    return self._arg1.get_value(), self._arg1.get_type()

  def get_arg2_value(self):
    return self._arg2.get_value()

  def get_arg2_value_type(self):
    return self._arg2.get_value(), self._arg2.get_type()

  def get_arg3_value(self):
    return self._arg3.get_value()

  def get_arg1_type(self):
    return self._arg1.get_type()

  def get_arg2_type(self):
    return self._arg2.get_type()

  def get_arg3_type(self):
    return self._arg3.get_type()




class Move(Instruction):

  def __init__(self, arg1v, arg1t, arg2v, arg2t):
    super().__init__("MOVE")
    #self.set_arg1(Argument(arg1))
    #self.set_arg2(Argument(arg2))
    self.set_args2(arg1v, arg1t, arg2v, arg2t)
    #self.set_arg2(arg2v, arg2t)

  def execute(self):
    print('Executing move.')
    prog.set_var_value(self.get_arg1_value(), self.get_arg2_value_type())
    print(prog.get_frame_dict('GF'))
    print(prog.get_frame_dict('LF'))

    
class Createframe(Instruction):
  def __init__(self):
    super().__init__("CREATEFRAME")

  def execute(self):
    #vytvori novy TF a zahodi obsah puvodniho TF
    print('Executing createframe.')
    prog.set_tf_frame()
    print("GF dict:")
    print(prog.get_frame_dict('GF'))
    print("LF dict:")
    print(prog.get_frame_dict('LF'))
    print("TF dict:")
    print(prog.get_frame_dict('TF'))

class Pushframe(Instruction):
  def __init__(self):
    super().__init__("PUSHFRAME")

  def execute(self):
    print('Executing pushframe.')
    prog.push_frame()

class Popframe(Instruction):
  def __init__(self):
    super().__init__("POPFRAME")

  def execute(self):
    print('Executing popframe.')
    prog.pop_frame()

# class for the DEFVAR instruction
class Defvar(Instruction):
  def __init__(self, arg1v, arg1t):
    super().__init__("DEFVAR")
    self.set_arg1(arg1v, arg1t)

  def execute(self):
    print('Executing defvar.')
    # inserts new variable with None value in the frame
    prog.set_var(self.get_arg1_value_type())
    
# class for the CALL instruction
class Call(Instruction):
  def __init__(self, arg1v, arg1t):
    super().__init__("CALL")
    self.set_arg1(arg1v, arg1t)

  def execute(self):
    print('Executing call.')
    # save the current position
    prog.call_stack_push(prog.get_instr_counter())
    # jump to the label
    prog.set_instr_counter(prog.get_label_order(self._arg1.get_value()))


class Return(Instruction):
  def __init__(self):
    super().__init__("RETURN")

  def execute(self):
    print('Executing return.')
    pos = prog.call_stack_pop()
    prog.set_instr_counter(pos)

class Pushs(Instruction):
  def __init__(self):
    super().__init__("PUSHS")

  def execute(self):
    print('Executing pushs.')

class Pops(Instruction):
  def __init__(self):
    super().__init__("POPS")

  def execute(self):
    print('Executing pops.')

# TODO arithmetic instructions

class Read(Instruction):

  def __init__(self, arg1v, arg1t, arg2v, arg2t):
    super().__init__("READ")
    self.set_args2(arg1v, arg1t, arg2v, arg2t)

  def execute(self):
    print('Executing read.')
    if input_file == '<stdin>':
      try:
        inp = input()
      except ValueError:
        inp = None
    else:
      try:
        f = open(input_file, "r")
      except FileNotFoundError:
        sys.stderr.write('File ' + input_file + 'not found.\n')
        exit(11)
      inp = f.readline()

    try:
      #inp = input_file.readline()
      if self.get_arg2_value() == 'int':
        inp = int(inp)
      elif self.get_arg1_value() == 'string':
        inp = str(inp)
      elif self.get_arg1_value() == 'bool':
        if inp.upper() == 'TRUE':
          inp = 'true'
        else:
          inp = 'false'
    except ValueError:
      inp = None

class Write(Instruction):
  def __init__(self, arg1v, arg1t):
    super().__init__("WRITE")
    self.set_arg1(arg1v, arg1t)

  def execute(self):
    print('Executing write.')
    if self.get_arg1_type() == 'nil':
      print('', end='')
    elif self.get_arg1_type() == 'bool':
      if self.get_arg1_value().upper() == 'TRUE':
        print('true', end='')
      else:
        print('false', end='')
    else:
      print(self.get_arg1_value(), end='')
    # TODO remove
    print('')

class Label(Instruction):
  def __init__(self, arg1v, arg1t, order):
    super().__init__("LABEL")
    self.set_arg1(arg1v, arg1t)
    prog.add_label(arg1v, order)

  def execute(self):
    print('Executing label (label does nothing).')
    pass
  
class Jump(Instruction):
  def __init__(self, arg1v, arg1t):
    super().__init__("JUMP")
    self.set_arg1(arg1v, arg1t)

  def execute(self):
    # zmena rizeni toku programu
    print('Executing jump.')
    prog.set_instr_counter(prog.get_label_order(self._arg1.get_value()))

class Factory:
  @classmethod
  def resolve(cls, opcode: str, root):
    opcode = opcode.upper()
    if opcode == 'MOVE':
      return Move(root[0].text, root[0].attrib['type'], root[1].text, root[1].attrib['type'])
    elif opcode == 'CREATEFRAME':
      return Createframe()
    elif opcode == 'PUSHFRAME':
      return Pushframe()
    elif opcode == 'POPFRAME':
      return Popframe()
    elif opcode == 'DEFVAR':
      return Defvar(root[0].text, root[0].attrib['type'])
    elif opcode == 'CALL':
      return Call(root[0].text, root[0].attrib['type'])
    elif opcode == 'RETURN':
      return Return()
    elif opcode == 'PUSHS':
      return Pushs(root[0].text, root[0].attrib['type'])
    elif opcode == 'POPS':
      return Pops(root[0].text, root[0].attrib['type'])
    if opcode == 'READ':
      return Read(root[0].text, root[0].attrib['type'], root[1].text, root[1].attrib['type'])
    elif opcode == 'WRITE':
      return Write(root[0].text, root[0].attrib['type'])

    elif opcode == 'LABEL':
      return Label(root[0].text, root[0].attrib['type'], root.attrib['order'])
    elif opcode == 'JUMP':
      return Jump(root[0].text, root[0].attrib['type'])
    else:
      sys.stderr.write('Invalid opcode (more like not implemented yet).\n')
      #exit(52)
      return -1


# argparse
def parse_arguments():
  ap = argparse.ArgumentParser()
  #ap.add_argument("--help", help="Idk help")
  ap.add_argument("--source", nargs=1, help="Idk src", action='append')
  ap.add_argument("--input", nargs=1, help="Idk inp", action='append')

  args = vars(ap.parse_args())  # dict with attributes
  print(args)
  print(args['source'])
  print(args['input'])

  if args['source'] is None:
    if args['input'] is None:
      exit(10)

    if len(args['input']) != 1:
      exit(10)

    # everything ok - s = def and file open
    source_file = sys.stdin
    input_file = open(args['input'][0][0], "r")
    
  elif args['input'] is None:
    if args['source'] is None:
      exit(10)

    if len(args['source']) != 1:
      exit(10)

    # everything ok - s = def and file open
    input_file = sys.stdin
    source_file = open(args['source'][0][0], "r")
    
  elif len(args['source']) != 1 or len(args['input']) != 1:
    exit(10)

  elif args['input'][0][0] == args['source'][0][0]:
    exit(10)
  
  else:
    if os.path.exists(args['input'][0][0]):
      #input_file = open(args['input'][0][0], "r")
      input_file = args['input'][0][0]
    else:
      # Print message if the file does not exist
      print("File " + args['input'][0][0] + " does not exist.")
      exit(11)
    
    if os.path.exists(args['source'][0][0]):
      #source_file = open(args['source'][0][0], "r")
      source_file = args['source'][0][0]
    else:
      # Print message if the file does not exist
      print("File " + args['source'][0][0] + " does not exist.")
      exit(11)

  return source_file, input_file

# xml load
def xml_load(source_file):
  tree = ElementTree()
  tree.parse(source_file)

  root = tree.getroot()

  # add right instruction (order : opcode)
  for child in root:
    if (child.tag != 'instruction'):
      sys.stderr.write('Chybicka se vloudila do vstupniho XML\n')
      exit(32) # mozna 31, idk

    instr = Factory.resolve(child.attrib['opcode'], child)
    if (instr == -1):
      continue

    prog.add_instr(child.attrib['order'], instr)

  prog.sort()

  # DRUHA SECOND CAST PROGRAMU
  order_list = list(prog.get_instr_dict().keys())
  index = 0

  while index < len(order_list):
    print(order_list[index])
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

  source_file, input_file = parse_arguments()

  prog = Program()

  xml_load(source_file)

  sys.stderr.write("Program successfully processed.\n");


  #exit(blah)

  #source_file.close()
  #input_file.close()