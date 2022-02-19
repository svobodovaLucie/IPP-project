<?php
ini_set('display_errors', 'stderr');

// parse the file
$instr_cnt = 0;
$comments_cnt = 0;

// create the xml object
$xml = new DomDocument('1.0', 'UTF-8');
$xml->formatOutput = true;


// Defining a callback function
function remove_whitechars($var){
  return ($var !== NULL && $var !== FALSE && $var !== "");
}

// Check the header
function header_check() {
  global $comments_cnt;
  while ($line_str = fgets(STDIN)) {
    // split the line
    $line = preg_split('/\s+/', trim($line_str, '\n'));
    // remove empty elements
    $line = array_values(array_filter($line, "remove_whitechars"));
    if (count($line) == 0)        // empty line
      continue;
    if ($line[0] == '.IPPcode22') // the header
      break;
    else if ($line[0][0] == '#')  // line with a comment
      $comments_cnt++;
    else                          // syntax error - no header
      exit(21);
  }
}

// checks type and returns it
function check_type($type) {
  return "some_type -> ".$type;
}

// adds the nth argument
function arg_el($line, $instruction_el, $n, $type) {
  global $xml;
  // create arg1 element
  $arg1_el = $xml->createElement("arg".$n, $line[$n]);
  $arg1_el->setAttribute("type", check_type($type));
  $instruction_el->appendChild($arg1_el);
}

// create program element
$program_el = $xml->createElement("program");
$program_el->setAttribute("language", "IPPcode22");
$xml->appendChild($program_el);

/*
// create instruction element
$instruction_el = $xml->createElement("instruction");
$instruction_el->setAttribute("order", "TODO:ciiiiiislo");
$instruction_el->setAttribute("opcode", "TODO:opcoode");
$program_el->appendChild($instruction_el);

// create arg1 element
$arg1_el = $xml->createElement("arg1", "TODO: some text");
$arg1_el->setAttribute("type", "TODO:tyyyyype");
$instruction_el->appendChild($arg1_el);

// create arg1 element
$arg2_el = $xml->createElement("arg2");
$instruction_el->appendChild($arg2_el);

// create arg1 element
$arg3_el = $xml->createElement("arg3");
$instruction_el->appendChild($arg3_el);

//echo($xml->saveXML());
*/



// check the header
header_check();

while ($line_str = fgets(STDIN)) {
  // split the line
  $line = preg_split('/\s+/', trim($line_str, '\n'));
  // remove empty elements
  $line = array_values(array_filter($line, "remove_whitechars"));

  // check line starting with comment
  if ($line[0][0] == '#') {
    $comments_cnt++;
    continue;
  }

  // create an instruction element
  $instruction_el = $xml->createElement("instruction");
  $instruction_el->setAttribute("order", ++$instr_cnt);
  $instruction_el->setAttribute("opcode", strtoupper($line[0]));
  $program_el->appendChild($instruction_el);
  
  switch(strtoupper($line[0])) {
    // INSTRUCTION
    case 'CREATEFRAME';
    case 'PUSHFRAME';
    case 'POPFRAME';
    case 'RETURN';
    case 'BREAK':
      break;

    // INSTRUCTION <var>
    case 'DEFVAR';
    case 'POPS':
      // create arg1 element
      arg_el($line, $instruction_el,"1", "var");
      break;

    // INSTRUCTION <label>
    case 'CALL';
    case 'LABEL';
    case 'JUMP':
      // create arg1 element
      arg_el($line, $instruction_el,"1", "label");
      break;

    // INSTRUCTION <symb>
    case 'PUSHS';
    case 'WRITE';
    case 'EXIT';
    case 'DPRINT':
      // create arg1 element
      arg_el($line, $instruction_el,"1", "symb");
      break;

    // INSTRUCTION <var> <symb>
    case 'MOVE';
    case 'INT2CHAR';
    case 'STRLEN';
    case 'TYPE':
      // create arg1 element
      arg_el($line, $instruction_el,"1", "var");
      // create arg2 element
      arg_el($line, $instruction_el,"2", "symb");
      break;
    // INSTRUCTION <var> <type>
    case 'READ':
      // create arg1 element
      arg_el($line, $instruction_el,"1", "var");
      // create arg2 element
      arg_el($line, $instruction_el,"2", "type");
      break;

      // INSTRUCTION <var> <symb1> <symb2>
    case 'ADD';
    case 'SUB';
    case 'MUL';
    case 'IDIV';
    case 'LT';
    case 'GT';
    case 'EQ';
    case 'AND';
    case 'OR';
    case 'NOT';
    case 'STRI2INT';
    case 'CONCAT';
    case 'GETCHAR';
    case 'SETCHAR':
      // create arg1 element
      arg_el($line, $instruction_el,"1", "var");
      // create arg2 element
      arg_el($line, $instruction_el,"2", "symb1");
      // create arg3 element
      arg_el($line, $instruction_el,"3", "symb2");
      break;      
    // INSTRUCTION <label> <symb1> <symb2>
    case 'JUMPIFEQ';
    case 'JUMPIFNEQ':
      // create arg1 element
      arg_el($line, $instruction_el,"1", "label");
      // create arg2 element
      arg_el($line, $instruction_el, "2", "symb1");
      // create arg3 element
      arg_el($line, $instruction_el, "3", "symb2");
      break;

    // other
    default:
      echo("Problem on line starting with: [".$line[0]."]\n");
      exit(22);
  }
  
  // check comments (for stats)
  foreach ($line as $v) {
    if (str_contains("$v", '#')) {
      $comments_cnt++;
      break;
    }
  }


}

echo($xml->saveXML());
echo("Number of comments: ".$comments_cnt."\n");
?>