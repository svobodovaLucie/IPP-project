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
    self._lf = Frame()
    self._tf = Frame()
    self._gf = Frame()
    self._gf.set_frame()  # initialise frame
    self._lf_list = []

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
      if not self._lf.is_initialised():
        sys.stderr.write('Uninitialised local frame.\n')
        exit(55)
      return self._lf
    elif frame_name[0:2] == 'TF':
      if not self._tf.is_initialised():
        sys.stderr.write('Uninitialised temporary frame.\n')
        exit(55)
      return self._tf
    else:
      exit(-1)  # TODO nemelo by nastat ale

  def get_frame_dict(self, frame_name):
    return self.get_frame(frame_name).get_frame_dict()

  def set_var(self, name_type):
    name, typ = (name_type)
    print(name + "TYP: " + typ)
    self.get_frame(name).set_var(name, typ)

  def set_var_value(self, name, value_type):
    value, typ = (value_type)
    self.get_frame(name).set_var_value(name, value, typ)

  

class Frame:
  # attributes
  """
  
  """
  def __init__(self):
    print("Frame init\n")
    self._frame_dict = {}
    self._initialised = False

  def set_frame(self):
    self._initialised = True

  def set_var(self, name, typ):
    if self._initialised == False:
      sys.stderr.write('Frame does not exist.\n')
      exit(55)
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
      self._frame_dict[name] = self.get_var_value(value[3:]) #self._frame_dict[value[3:]]
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

  def is_initialised(self):
    return self._initialised

class Argument:

  def __init__(self, value, typ):
    # self._typ = typ
    self._value = value
    self._typ = typ
    print("Argument init")

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
    print("Jsem move s argumentem ")
    print(self.get_arg1_value())
    print(self.get_arg2_value())
    #prog.get_frame('GF').set_var_value(self._arg1.get_value(), self._arg2.get_value())
    #TODO check: 
    prog.set_var_value(self.get_arg1_value(), self.get_arg2_value_type())
    print(prog.get_frame_dict('GF'))

# class for the DEFVAR instruction
class Defvar(Instruction):
  def __init__(self, arg1v, arg1t):
    super().__init__("DEFVAR")
    self.set_arg1(arg1v, arg1t)

  def execute(self):
    # inserts new variable with None value in the frame
    """if self.get_arg1_type() != 'var':
      sys.stderr.write('Invalid DEFVAR operand type.\n')
      exit(-1)"""
    prog.set_var(self.get_arg1_value_type())
    print("Prog GF:")
    print(prog.get_frame_dict('GF'))
    

class Factory:
  @classmethod
  def resolve(cls, string: str, root):
    if string.upper() == "DEFVAR":
      #arg1 = Argument(root[0].text)
      #print('LEN OF ROOT: ' + str(len(root)))
      #arg1.set_value(root[0].text)
      #return Defvar(arg1) # TODO here arg1 by byl proste text a argument() by se vytvoril az v konstruktoru Defvar
      return Defvar(root[0].text, root[0].attrib['type'])
    elif string.upper() == "MOVE":
      #arg1 = Argument(root[0].text)
      #arg1.set_value(root[0].text)
      #arg2 = Argument(root[1].text)
      #arg2.set_value(root[1].text)
      return Move(root[0].text, root[0].attrib['type'], root[1].text, root[1].attrib['type'])
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

  #prog = Program()

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


  print(prog.get_instr_dict())

  print("Sort:")

  prog.sort()

  print(prog.get_instr_dict())

  #i = 1
  #prochazeni neni do len, ale podle order
  # TODO sekvence nemusi byt souvisla
  # TODO vyresit skoky
  for i in prog.get_instr_dict():
  #while i < len(prog.get_instr_dict()):
    print("While " + str(i))
    ins = prog.get_instr_dict()[str(i)]
    print('Bef')
    ins.execute()
    print(ins)

    #i += 1

# xml check

# xml2inst

# interpret instr







if __name__ == '__main__':

  source_file, input_file = parse_arguments()

  prog = Program()

  xml_load(source_file)

  sys.stderr.write("Sth\n");


  #exit(blah)

  #source_file.close()
  #input_file.close()