import argparse
from posixpath import supports_unicode_filenames
import sys
import os
from xml.etree.ElementTree import ElementTree


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
  print(root[0].tag)
  print(root[1].tag)
  print(root[1][0].tag)
  print(root[1][1].tag)
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