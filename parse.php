<?php
/* ****************** parse.php ****************** *
 *    Principles of Programming Languages (IPP)    *
 *           Lucie Svobodova, xsvobo1x             *
 *          xsvobo1x@stud.fit.vutbr.cz             *
 *                   FIT BUT                       *
 *                  2021/2022                      *
 * *********************************************** */
/**
 * This script parses the input file in IPPcode22 language
 * and prints its XML representation to stdout.
 */

// print warnings to stderr
ini_set('display_errors', 'stderr');

/**
 * Function prints help to stdout.
 */
function print_help() {
  echo "  This script parses input file in IPPcode22 programming language 
  and prints its XML representation to stdout after the lexical and syntactic analysis.

  Usage:
  - run the programme:
    php8.1 parse.php <input_file
  - print help
    php8.1 parse.php --help
  - run the programme with statistics (described below)
    php8.1 parse.php <input_file [options]

  Run with statistics:
  - various statistics can be saved into files
  - use option '--stats=file' where 'file' is a file to that the stats will be written
  - then use the statistics specifiers:
    --loc - number of lines
    --comments - number of comments
    --labels - number of labels
    --jumps - number of jumps and returns
    --fwjumps - number of forward jumps
    --backjumps - number of backward jumps
    --badjumps - number of jumps to invalid labels
  - usage example (loc and jumps will be written to file1 and comments and labels to file2):
    php8.1 parse.php <input_file --stats=file1 --loc --jumps --stats=file2 --comments --labels
  ";
}

/**
 * Function parses command line arguments and stores them 
 * in the "$cli_args" array.
 * In the case of invalid arguments the programme exits.
 * 
 * @param $argv command line arguments
 */
function parse_cmdline($argv) {
  $args = count($argv);
  switch ($args) {
    case 1:   // no options
      return;
    case 2:   // --help or stats
      if ($argv[1] == "--help") {
        print_help();
        exit(0);
      }
    default:  // other
      break;
  }
  // check if the first option is --stats=file -> if not, the cmd line arguments are invalid
  if (preg_match("/^--stats=/", $argv[1]) != 1) {
    exit(10);
  }
  // check the arguments and store them in $cli_args array
  global $cli_args;
  $counter_for_cli = -1;
  for ($i=1; $i < count($argv); $i++) {
    // --stats=file
    if (preg_match("/^--stats=/", $argv[$i]) == 1) {
      $cli_args[++$counter_for_cli] = preg_split("/--stats=/", $argv[$i], 0, PREG_SPLIT_NO_EMPTY);
      // check if the filename is unique
      for ($j = 0; $j < count($cli_args) - 1; $j++) {
        if ($cli_args[$counter_for_cli][0] == $cli_args[$j][0])
          exit(12);
      }
      continue;
    }
    // another options
    if ($argv[$i] == "--loc" || $argv[$i] == "--comments" || $argv[$i] == "--labels" || $argv[$i] == "--jumps" 
        || $argv[$i] == "--fwjumps" || $argv[$i] == "--backjumps" || $argv[$i] == "--badjumps") {
      array_push($cli_args[$counter_for_cli], $argv[$i]);
    } else
      exit(10);
  }
}

/**
 * Function saves stats to files specified in command line arguments.
 * 
 * @param $cli_args array that contains the command line arguments
 * @param $stats array that contains statistics about the analyzed file
 */
function save_stats($cli_args, $stats) {
  $stats_group_num = 0;
  while ($stats_group_num < count($cli_args)) {
    // try to open the file
      try {
        $stats_file = fopen($cli_args[$stats_group_num][0],'w');
        if (!$stats_file) {
          throw new Exception('File open failed.');
        }  
      } catch (Exception $ex) {
        exit(11);
      }

    // write to the file
    for ($i = 1; $i < count($cli_args[$stats_group_num]); $i++) {
      switch ($cli_args[$stats_group_num][$i]) {
        case '--loc':
          fwrite($stats_file, $stats['loc']."\n");
          break;
        case '--comments':
          fwrite($stats_file, $stats['comments']."\n");
          break;
        case '--labels':
          fwrite($stats_file, count($stats['labels_defined'])."\n");
          break;
        case '--jumps':
          fwrite($stats_file, $stats['jumps']."\n");
          break;
        case '--fwjumps':
          fwrite($stats_file, $stats['fwjumps']."\n");
          break;
        case '--backjumps':
          fwrite($stats_file, $stats['backjumps']."\n");
          break;
        case '--badjumps':
          $badjumps_cnt = 0;
          foreach ($stats['labels_undefined'] as $jump) {
            $badjumps_cnt += $jump;
          }
          fwrite($stats_file, $badjumps_cnt);
          break;
      }
    }
    fclose($stats_file);
    $stats_group_num++;
  }
}

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
  global $stats;
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
      $stats['comments']++;
    else if (preg_match("/^.IPPcode22#/", $line[0]) == 1) // comment after header
      break;
    else                          // syntax error - no header
      exit(21);
  }
}

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
  $argn_el = $xml->createElement("arg".$n, htmlspecialchars($line[$n], ENT_XML1));
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
  if (preg_match("/^(GF|LF|TF)@[a-zA-Z_\-$&%*!?][a-zA-Z0-9_\-$&%*!?]*$/", $var) == 1)
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
  if (preg_match("/^([^ \\\\]|\\\\\d{3})*$/", $string) == 1)
    return $string;
  return NULL;

}

/**
 * Function checks if the number is valid.
 * 
 * @param $num the number to be checked
 * @return  true if the number is valid,
 *          false if it is invalid
 */
function check_int($num) {
  if ((preg_match("/^[-|+]?\d\d*$/", $num) != 1) and 
      (preg_match("/^0[xX][0-9a-fA-F]+$/", $num) != 1) and 
      (preg_match("/^0[1-7][0-7]*$/", $num) != 1)) {
    return false;
  }
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
    return false;
  return true;
}

/**
 * Function checks if the nil type contains nil value.
 * 
 * @return  true if valid, 
 *          false if invalid
 */
function check_nil($string) {
  if ($string != 'nil')
    return false;
  return true;
}

/** 
 * Function checks if the name of a label is valid and counts the statistics.
 * 
 * @param $label the name to be checked
 * @return  NULL if invalid,
 *          $label if valid
 */
function check_label($label, $instr) {
  if (!preg_match("/^[a-zA-Z_\-$&%*!?][a-zA-Z0-9_\-$&%*!?]*$/", $label) == 1)
    return false;

  global $stats;
  if ($instr == 'LABEL') {
    if (!in_array($label, $stats['labels_defined'])) {
      if (array_key_exists($label, $stats['labels_undefined'])) {
        // remove from the labels_undefined array
        $stats['fwjumps'] += $stats['labels_undefined'][$label];
        unset($stats['labels_undefined'][$label]);
      }
      // add to the labels_defined array
      array_push($stats['labels_defined'], $label);
    }

  } else { // eg JUMP, JUMPIFEQ...
    $stats['jumps']++;
    // is the label defined yet -> backjump
    if (in_array($label, $stats['labels_defined'])) {
      $stats['backjumps']++;
      return true;
    }
    if (array_key_exists($label, $stats['labels_undefined'])) {
      $stats['labels_undefined'][$label] += 1;
    } else {
      // label is not defined yet -> add to labels_undefined array
      $stats['labels_undefined'] += array($label=>1);
    }
  }
  return true;
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

  if (($type == 'string')) {
    $string = check_string($word);
    if (is_null($string))
      return NULL;
    if ($string == "")
      return array('string', "");
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

/* Array used for storing information about statistics. */
$stats = array("instr"=> 0, "loc"=> 0, "comments"=> 0, "jumps"=> 0, "fwjumps"=> 0,
                "backjumps"=> 0, "labels_defined"=> [], "labels_undefined"=> []);

/* Array used for storing the parsed command line options. */
$cli_args = [];

/* The XML object. */
$xml = new DomDocument('1.0', 'UTF-8');
$xml->formatOutput = true;

// create a program element
$program_el = $xml->createElement("program");
$program_el->setAttribute("language", "IPPcode22");
$xml->appendChild($program_el);

// parse the command line arguments
parse_cmdline($argv);

// check if the ".IPPcode22" header is present
header_check();

// the main loop that checks the syntax of the input
while ($line_str = fgets(STDIN)) {
  // remove '\n'
  $line_str = trim($line_str, "\n");

  // remove comments
  if (str_contains("$line_str", '#')) {
    $stats['comments']++;
    $line_str = explode('#', $line_str);
    $line_str = $line_str[0];

    // line starting with a comment
    if (empty($line_str[0]))
      continue;
  }
  // line starting with a comment
  if (empty($line_str[0]))
    continue;
  
  $stats['loc']++;
  // split the line by white characters
  $line = preg_split('/\s+/',$line_str);
  // remove empty elements
  $line = array_values(array_filter($line, "is_var_empty"));

  $line[0] = strtoupper($line[0]);

  // create an instruction element
  $instruction_el = $xml->createElement("instruction");
  $instruction_el->setAttribute("order", ++$stats['instr']);
  $instruction_el->setAttribute("opcode", $line[0]);
  $program_el->appendChild($instruction_el);
  
  switch($line[0]) {
    // INSTRUCTION
    case 'RETURN':
      $stats['jumps']++;
    case 'CREATEFRAME';
    case 'PUSHFRAME';
    case 'POPFRAME';
    case 'BREAK':
      // check the number of operands
      if (count($line) != 1) {
        echo "INSTRUCTION - BAD - $stats[0]\n";
        exit(23);
      }
      break;

    // INSTRUCTION <var>
    case 'DEFVAR';
    case 'POPS':
      // check the number of operands and check them
      if ((count($line) != 2) or 
          (!check_var($line[1]))) {
        echo "INSTRUCTION <var> - BAD - $stats[0]\n";
        exit(23);
      }
      // create arg1 element
      arg_el($line, $instruction_el, '1', 'var');
      break;

    // INSTRUCTION <label>
    case 'LABEL':
    case 'CALL';
    case 'JUMP':
      // check the number of operands and check them
      if ((count($line) != 2) or 
          (!check_label($line[1], $line[0]))) {
        echo "INSTRUCTION <label> - BAD - $stats[0]\n";
        exit(23);
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
          echo "INSTRUCTION <symb> - BAD - $stats[0]\n";
        exit(23);
      }
      // create arg1 element
      $line[1] = $type_text[1];
      arg_el($line, $instruction_el,'1', $type_text[0]);
      break;

    // INSTRUCTION <var> <symb>
    case 'MOVE';
    case 'INT2CHAR';
    case 'STRLEN';
    case 'NOT';
    case 'TYPE':
      $type_text = check_symb($line[2]);
      if ((count($line) != 3) or 
          !check_var($line[1]) or
          empty($type_text)) {
        echo "INSTRUCTION <var> <symb> - BAD - $stats[0]\n";
        exit(23);
      }
      // create arg1 and arg2 elements
      arg_el($line, $instruction_el, '1', 'var');
      $line[2] = $type_text[1];
      arg_el($line, $instruction_el, '2', $type_text[0]);
      break;

    // INSTRUCTION <var> <type>
    case 'READ':
      if ((count($line) != 3) or 
          !check_var($line[1]) or
          !check_type($line[2])) {
        echo "INSTRUCTION <var> <type> - BAD - $stats[0]\n";
        exit(23);
      }
      // create arg1 and arg2 elements
      arg_el($line, $instruction_el, '1', 'var');
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
        echo "INSTRUCTION <var> <symb1> <symb2> - BAD - $stats[0]\n";
        exit(23);
      }
      // create arg1, arg2 and arg3 elements
      arg_el($line, $instruction_el, '1', 'var');
      $line[2] = $type_text1[1];
      arg_el($line, $instruction_el, '2', $type_text1[0]);
      $line[3] = $type_text2[1];
      arg_el($line, $instruction_el, '3', $type_text2[0]);
      break;

      // INSTRUCTION <label> <symb1> <symb2>
    case 'JUMPIFEQ';
    case 'JUMPIFNEQ':
      $type_text1 = check_symb($line[2]);
      $type_text2 = check_symb($line[3]);
      if ((count($line) != 4) or 
          !check_label($line[1], $line[0]) or
          empty($type_text1) or
          empty($type_text2)) {
        echo "INSTRUCTION <label> <symb1> <symb2> - BAD - $stats[0]\n";
        exit(23);
      }
      // create arg1, arg2 and arg3 elements
      arg_el($line, $instruction_el, '1', 'label');
      $line[2] = $type_text1[1];
      arg_el($line, $instruction_el, '2', $type_text1[0]);
      $line[3] = $type_text2[1];
      arg_el($line, $instruction_el, '3', $type_text2[0]);
      break;

    // wrong instruction
    default:
      echo("Problem on line starting with instruction: ".$line[0]."\n");
      exit(22);
  }
  // check comments (for stats)
  foreach ($line as $v) {
    if (str_contains("$v", '#')) {
      $stats['comments']++;
      break;
    }
  }
}

// save statistics
if (count($argv) != 1)
  save_stats($cli_args, $stats);

// print XML to stdout
echo($xml->saveXML());
?>