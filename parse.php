<?php
/** HEADER */
/** HEADER */
/** HEADER */
/** HEADER */
/** HEADER */
/** HEADER */

// print warnings to stderr
ini_set('display_errors', 'stderr');

// global variables (stats, xml)
$instr_cnt = 0;
$comments_cnt = 0;
//$labels_cnt = 0;
$labels_array = [];
$loc_cnt = 0;
$jumps_cnt = 0;
$fwjumps_cnt = 0;
$backjumps_cnt = 0;
$badjumps_cnt = 0;

// the xml object
$xml = new DomDocument('1.0', 'UTF-8');
$xml->formatOutput = true;

/**
 * Callback function that checks if the variable is empty.
 * 
 * @return  true if the variable is not empty (NULL, FALSE, ""),
 *          false if the variable is empty.
 */
function is_var_empty($var){
  return ($var !== NULL && $var !== FALSE && $var !== "");
}

/**
 * Function checks if there is a header in the stdin stream.
 */
function header_check() {
  global $comments_cnt;
  while ($line_str = fgets(STDIN)) {
    // split the line
    $line = preg_split('/\s+/', trim($line_str, '\n'));
    // remove empty elements
    $line = array_values(array_filter($line, "is_var_empty"));
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

// adds the nth argument
/**
 * Function inserts new arg element into $xml.
 * 
 * @param $line line containing the text element
 * @param $instruction_el the parent of the new element
 * @param $n the order of the new element (arg1, arg2, arg3)
 * @param $type attribute type of the new element
 * 
 */
function arg_el($line, $instruction_el, $n, $type) {
  global $xml;
  $argn_el = $xml->createElement("arg".$n, $line[$n]);
  $argn_el->setAttribute("type", $type);
  $instruction_el->appendChild($argn_el);
}

/**
 * Function checks the validity of a variable.
 * 
 * @param $var the variable to be checked
 * @return  true if the variable is valid,
 *          false if it is invalid
 */
function check_var($var) {
  if (preg_match("/(GF|LF|TF)@[a-zA-Z_\-$&%*!?][a-zA-Z0-9_\-$&%*!?]*/", $var) == 1)
    return true;
  return false;
}

/**
 * Function checks the validity of a string.
 * 
 * @param $string the string to be checked
 * @return  NULL if the string is invalid, 
 *          $string if it is valid
 */
function check_string($string) {
  // check string and convert characters problematic in XML - automatic
  if ($string == "")
    return "a";
  return $string;

}

/**
 * Function checks if the number is valid.
 * 
 * @param $num the number to be checked
 * @return  true if the number is valid,
 *          false if it is invalid
 */
function check_int($num) {
  // check int validity
  /*
  echo "INT: $num\n";
  if ((intval($num, 0) == 0)) {//) or preg_match("/[0][0]* /", $num) != 1) {
    $check = preg_match("/00* /", $num);
    echo "INT - bad or 0: $num, check = $check\n";
      return false;
  }
  */
  return true;
}

/**
 * Function checks if the bool type contains values true or false.
 * 
 * @param $string the string to be checked
 * @return  true if valid,
 *          false if invalid
 */
function check_bool($string) {
  if ($string != 'true' and $string != 'false')
    return NULL;
  return $string;
}

/**
 * Function checks if the nil type contains nil value.
 * 
 * @return  true if valid, 
 *          false if invalid
 */
function check_nil($string) {
  if ($string != 'nil')
    return NULL;
  return 'nil';
}

/** 
 * Function checks if the name of a label is valid.
 * 
 * @param $label the name to be checked
 * @return  NULL if invalid,
 *          $label if valid
 */
function check_label($label) {
  if (preg_match("/[a-zA-Z_\-$&%*!?][a-zA-Z0-9_\-$&%*!?]*/", $label) == 1)
    return true;
  return false;
}

/**
 * Function checks the validity of a type (int, string, bool).
 * 
 * @param $type the string to be checked
 * @return  true if valid,
 *          false if invalid
 */
function check_type($type) {
  if ($type != 'int' and $type != 'string' and $type != 'bool')
    return false;
  return true;
}

/** 
 * Function checks the validity of a symbol and returns it if valid.
 * 
 * @param $word_orig the string to be checked
 * @return  NULL if invalid,
 *          array of (type, symbol) if valid
 */
function check_symb($word_orig) {
  // word must contain '@'
  if (substr_count($word_orig, '@') < 1)
    return NULL;
  $word = explode('@', $word_orig);
  // the part before '@' can't be empty
  if (empty($word[0]))
    return NULL;
  $type = $word[0];

  // remove the type part and implode the rest
  unset($word[0]);
  $word = implode('@', array_values($word));

  if (($type == 'string') and (($string = check_string($word)) != NULL)) {
    return array('string', $string);
  } else if (($type == 'int') and check_int($word)) {
    return array('int', $word);
  } else if (($type == 'bool') and check_bool($word)) {
    return array('bool', $word);
  } else if (($type == 'nil') and check_nil($word)) {
    return array('nil', 'nil');
  } else if (check_var($word_orig)) {
    return array('var', $word_orig);
  }
  // invalid type
  return NULL;
}

/**
 * The main body.
 */
// create program element
$program_el = $xml->createElement("program");
$program_el->setAttribute("language", "IPPcode22");
$xml->appendChild($program_el);

// check the header
header_check();

// the main loop that checks the syntax of the input
while ($line_str = fgets(STDIN)) {
  // remove the '\n'
  $line_str = trim($line_str, "\n");

  // remove comments
  if (str_contains("$line_str", '#')) {
    $comments_cnt++;
    $line_str = explode('#', $line_str);
    $line_str = $line_str[0];

    // line starting with a comment
    if (empty($line_str[0]))
      continue;
  }
  // line starting with a comment
  if (empty($line_str[0]))
    continue;
  
  $loc_cnt++;
  // split the line by white characters
  $line = preg_split('/\s+/',$line_str);
  // remove empty elements
  $line = array_values(array_filter($line, "is_var_empty"));

  // create an instruction element
  $instruction_el = $xml->createElement("instruction");
  $instruction_el->setAttribute("order", ++$instr_cnt);
  $instruction_el->setAttribute("opcode", strtoupper($line[0]));
  $program_el->appendChild($instruction_el);
  
  switch(strtoupper($line[0])) {
    // INSTRUCTION
    case 'RETURN':
      $jumps_cnt++;
    case 'CREATEFRAME';
    case 'PUSHFRAME';
    case 'POPFRAME';
    case 'BREAK': // TODO is BREAK a jump?
      // check the number of operands
      if (count($line) != 1) {
        echo "INSTRUCTION - BAD\n";
        exit(22);
      }
      break;

    // INSTRUCTION <var>
    case 'DEFVAR';
    case 'POPS':
      // check the number of operands and check them
      if ((count($line) != 2) or 
          (!check_var($line[1]))) {
        echo "INSTRUCTION <var> - BAD - $instr_cnt\n";
        exit(22);
      }
      // create arg1 element
      arg_el($line, $instruction_el, '1', 'var');
      break;

    // INSTRUCTION <label>
    case 'LABEL':
      //$labels_cnt++;
      if (!in_array($line[1], $labels_array)) {
        array_push($labels_array, $line[1]);  // syntax is checked later
      }
    case 'CALL';
    case 'JUMP':
      if ($line[0] != 'LABEL')
        $jumps_cnt++;
      // check the number of operands and check them
      if ((count($line) != 2) or 
          (!check_label($line[1]))) {
        echo "INSTRUCTION <label> - BAD - $instr_cnt\n";
        exit(22);
      }
      // create arg1 element
      arg_el($line, $instruction_el, '1', 'label');
      break;

    // INSTRUCTION <symb>
    case 'PUSHS';
    case 'WRITE';
    case 'EXIT';
    case 'DPRINT':
      // check the number of operands and check them
      $type_text = check_symb($line[1]);
      if ((count($line) != 2) or 
          empty($type_text)) {
          echo "INSTRUCTION <symb> - BAD - $instr_cnt\n";
        exit(22);
      }
      $line[1] = $type_text[1];
      arg_el($line, $instruction_el,'1', $type_text[0]);
      break;

    // INSTRUCTION <var> <symb>
    case 'MOVE';
    case 'INT2CHAR';
    case 'STRLEN';
    case 'TYPE':
      $type_text = check_symb($line[2]);
      if ((count($line) != 3) or 
          !check_var($line[1]) or
          empty($type_text)) {
        echo "INSTRUCTION <var> <symb> - BAD - $instr_cnt\n";
        exit(22);
      }
      // create arg1 element
      arg_el($line, $instruction_el, '1', 'var');
      // create arg2 element
      $line[2] = $type_text[1];
      arg_el($line, $instruction_el, '2', $type_text[0]);
      break;

    // INSTRUCTION <var> <type>
    case 'READ':
      if ((count($line) != 3) or 
          !check_var($line[1]) or
          !check_type($line[2])) {
        echo "INSTRUCTION <var> <type> - BAD - $instr_cnt\n";
        exit(22);
      }
      // create arg1 element
      arg_el($line, $instruction_el, '1', 'var');
      // create arg2 element
      arg_el($line, $instruction_el, '2', 'type');
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
      $type_text1 = check_symb($line[2]);
      $type_text2 = check_symb($line[3]);
      if ((count($line) != 4) or 
          !check_var($line[1]) or
          empty($type_text1) or
          empty($type_text2)) {
        echo "INSTRUCTION <var> <symb1> <symb2> - BAD - $instr_cnt\n";
        exit(22);
      }
      // create arg1 element
      arg_el($line, $instruction_el, '1', 'var');
      // create arg2 element
      $line[2] = $type_text1[1];
      arg_el($line, $instruction_el, '2', $type_text1[0]);
      // create arg3 element
      $line[3] = $type_text2[1];
      arg_el($line, $instruction_el, '3', $type_text2[0]);
      break;

      // INSTRUCTION <label> <symb1> <symb2>
    case 'JUMPIFEQ';
    case 'JUMPIFNEQ':
      $jumps_cnt++;
      $type_text1 = check_symb($line[2]);
      $type_text2 = check_symb($line[3]);
      if ((count($line) != 4) or 
          !check_label($line[1]) or
          empty($type_text1) or
          empty($type_text2)) {
        echo "INSTRUCTION <label> <symb1> <symb2> - BAD - $instr_cnt\n";
        exit(22);
      }
      // create arg1 element
      arg_el($line, $instruction_el, '1', 'label');
      // create arg2 element
      $line[2] = $type_text1[1];
      arg_el($line, $instruction_el, '2', $type_text1[0]);
      // create arg3 element
      $line[3] = $type_text2[1];
      arg_el($line, $instruction_el, '3', $type_text2[0]);
      break;

    // other
    default:
      //echo("Problem on line starting with: [".$line[0]."]\n");
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
echo "LOCS: $labels_cnt\n";
echo "COMMENTS: $comments_cnt\n";
//echo "LABELS: $labels_cnt\n";
print_r($labels_array);
echo "JUMPS: $jumps_cnt\n";
echo "FWJUMPS: $fwjumps_cnt\n";
echo "BACKJUMPS: $backjumps_cnt\n";
echo "BADJUMPS: $badjumps_cnt\n";

?>