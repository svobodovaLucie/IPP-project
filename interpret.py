import argparse
#from posixpath import supports_unicode_filenames
import sys
import os
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
    print("Program init\n")
    self._instr_dict = {}

  def add_instr(self, order, instr):
    self._instr_dict[order] = instr

  def get_dict(self):
    return self._instr_dict

  def sort(self):
    self._instr_dict = {key:value for key, value in sorted(self._instr_dict.items(), key=lambda item: int(item[0]))}

class Frame:
  # attributes
  """
  
  """
  def __init__(self):
    print("Frame init\n")

class Variable:
  # attributes
  """
  
  """
  def __init__(self):
    print("Variable init\n")

class Argument:

  def __init__(self):
    # self._typ = typ
    #self._value = value
    print("Argument init")

  def set_value(self, arg1):
    self._value = arg1

  def get_value(self):
    return self._value

class Instruction:
  #_instruction_list = []

  def __init__(self, opcode):
    self._opcode = opcode

  def get_opcode(self):
    return self._opcode

  def execute(self):
    print('something default')

  """"
  def get_list(self):
    return self._instruction_list

  def get_arg(self):
    return self.Arg1

  def set_opcode(self, value):
    self._opcode = value
  """

class Defvar(Instruction):

  def __init__(self, arg1):
    super().__init__("DEFVAR")
    self._arg1 = arg1

  def execute(self):
    print("Jsem defvar s argumentem ")
    print(self._arg1.get_value())

class Move(Instruction):

  def __init__(self, arg1, arg2):
    super().__init__("MOVE")
    self._arg1 = arg1
    self._arg2 = arg2

  def execute(self):
    print("Jsem move s argumentem ")
    print(self._arg1.get_value())
    print(self._arg2.get_value())

class Factory:
  @classmethod
  def resolve(cls, string: str, root):
    if string.upper() == "DEFVAR":
      arg1 = Argument()
      arg1.set_value(root[0].text)
      return Defvar(arg1)
    elif string.upper() == "MOVE":
      arg1 = Argument()
      arg1.set_value(root[0].text)
      arg2 = Argument()
      arg2.set_value(root[1].text)
      return Move(arg1, arg2)
    else:
      sys.stderr.write('Invalid opcode (more like not implemented yet)\n')
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

  #print(input_file.read())
  #print(source_file.read())

  return source_file, input_file

# xml load
def xml_load(source_file):
  print(source_file)
  tree = ElementTree()
  tree.parse(source_file)

  root = tree.getroot()
  print(root.tag)

  prog = Program()

  # add right instruction (order : opcode)
  for child in root:
    if (child.tag != 'instruction'):
      sys.stderr.write('Chybicka se vloudila do vstupniho XML\n')
      exit(32) # mozna 31, idk


    instr = Factory.resolve(child.attrib['opcode'], child)
    if (instr == -1):
      continue
    print(child.attrib['order'], child.attrib['opcode'])

    #prog.add_instr(child.attrib['order'], instr.get_opcode())
    prog.add_instr(child.attrib['order'], instr)


  print(prog.get_dict())

  print("Sort:")

  prog.sort()

  print(prog.get_dict())

  i = 1
  #prochazeni neni do len, ale podle order
  while i < len(prog.get_dict()):
    print("While " + str(i))
    ins = prog.get_dict()[str(i)]
    print(ins)
    ins.execute()
    i += 1

# xml check

# xml2inst

# interpret instr







if __name__ == '__main__':
  
  source_file, input_file = parse_arguments()

  xml_load(source_file)

  sys.stderr.write("Sth\n");


  #exit(blah)

  #source_file.close()
  #input_file.close()