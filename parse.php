<?php
/* ****************** parse.php ****************** *
 *   Principy programovacích jazyků a OOP (IPP)    *
 *           Lucie Svobodová, xsvobo1x             *
 *                FIT VUT v Brně                   *
 *                  2021/2022                      *
 * *********************************************** */

// print warnings to stderr
ini_set('display_errors', 'stderr');

/**
 * Function prints help to stdout.
 */
function print_help() {
  echo "Help\n";
  echo "And sth else\n";
}

/**
 * Function parses command line arguments and stores them in
 * the "$cli_args" array.
 * In the case of invalid arguments the programme exits.
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
    default:
      break;
  }
  // TODO check jestli neni zadan vicekrat stejny soubor (pozor, check i "file" a file)
  // --help
  /*
  if ($argv[1] == "--help") {
    if (count($argv) != 2)
      exit(10);
    print_help();
    exit(0);
  }
  */

  // Wrong arguments
  // TODO maybe dont check for files
  if (preg_match("/^--stats=\"?[^<>:;,?\"*|\/]+\"?$/", $argv[1]) != 1) {
    exit(10);
  }

  /*
    $cli_args array:
    [0] => Array  (
                    [0] => file1.txt
                    [1] => loc
                    [2] => jumps
                  )
    [1] => Array  (
                    [0] => file2.txt
                    [1] => badjumps
                  )
  */
  global $cli_args;
  $counter_for_cli = -1;
  for ($i=1; $i < count($argv); $i++) {
    // --stats=file
    if (preg_match("/^--stats=\"?[^<>:;,?\"*|\/]+\"?$/", $argv[$i]) == 1) {
      $cli_args[++$counter_for_cli] = preg_split("/--stats=/", $argv[$i], 0, PREG_SPLIT_NO_EMPTY);
      continue;
    }
    // other options
    if ($argv[$i] == "--loc" || $argv[$i] == "--comments" || $argv[$i] == "--labels" || $argv[$i] == "--jumps" 
        || $argv[$i] == "--fwjumps" || $argv[$i] == "--backjumps" || $argv[$i] == "--badjumps") {
      array_push($cli_args[$counter_for_cli], $argv[$i]);
    } else
      exit(10);
  }
  // TODO remove debug
  //print_r($cli_args);
}

/**
 * TODO
 */
function save_stats($cli_args, $stats) {
  //echo "saving stats\n";
  $stats_group_num = 0;
  //var_dump($cli_args);
  while ($stats_group_num < count($cli_args)) {
    // open file
    $stats_file = fopen($cli_args[$stats_group_num][0],'w');
    if ($stats_file == false)
      exit(11);

    // inside
    for ($i = 1; $i < count($cli_args[$stats_group_num]); $i++) {
      //print_r($cli_args[$stats_group_num][$i]);
      //echo "\n";
      switch ($cli_args[$stats_group_num][$i]) {
        // write_stats();
        case '--loc':
          fwrite($stats_file, $stats['loc']."\n");
          break;
        case '--comments':
          fwrite($stats_file, $stats['comments']."\n");
          break;
        case '--labels':
          fwrite($stats_file, count($stats['labels_defined'])."\n");
          //echo "LABELS: ".count($stats['labels_defined'])."\n";
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
          foreach ($jump as $stats['labels_undefined']) {
            $badjumps_cnt += $jump;
          }
          fwrite($stats_file, $badjumps_cnt);
          //echo "BADJUMPS: ".$badjumps_cnt."\n";
          break;
      }
    }
    
    // close file
    fclose($stats_file);
    //echo "ONE DONE\n";
    $stats_group_num++;
  }

  /*
echo "LOCS: ".$stats['loc']."\n";
echo "COMMENTS: ". $stats['comments']."\n";
$labels_cnt = count($stats['labels_defined']);
//echo "LABELS: ".$stats['labels']."\n";
// z pole undefined zjistime nasledujici:
// to, co v nem zbylo, je pocet badjumps
print_r($stats['labels_undefined']);
print_r($stats['labels_defined']);
echo "JUMPS: ".$stats['jumps']."\n";
echo "FWJUMPS: ".$stats['fwjumps']."\n";
echo "BACKJUMPS: ".$stats['backjumps']."\n";
//echo "BADJUMPS: ".$stats['badjumps']."\n";
*/
}

// global variables (stats, xml)
// TODO dat do struktury
$stats = array("instr"=> 0, "loc"=> 0, "comments"=> 0, "jumps"=> 0, "fwjumps"=> 0,
                "backjumps"=> 0, "labels_defined"=> [], "labels_undefined"=> []);

$cli_args = [];
//$instr_cnt = 0;//
//$comments_cnt = 0;//
//$labels_cnt = 0;//
//$labels_defined = [];//
//$labels_undefined = [];//
//$loc_cnt = 0;//
//$jumps_cnt = 0;//
//$fwjumps_cnt = 0;
//$backjumps_cnt = 0;
//$badjumps_cnt = 0;

// the xml object
$xml = new DomDocument('1.0', 'UTF-8');
$xml->formatOutput = true;

/** TODO
 * Function parses command line arguments.
 * 
 * @return  true if succesful,
 *          false if not
 */
function parse_cmd() {
  printf("TODO\n");
  return true;
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
      //$comments_cnt++;
      $stats['comments']++;
    else if (preg_match("/^.IPPcode22#/", $line[0]) == 1) // comment after header
      break;
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
  // TODO hexa numbers with + or -?
  // TODO check regexes, }maybe use intval too - but it matches eg 40i etc.
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
 * Function checks if the name of a label is valid.
 * 
 * @param $label the name to be checked
 * @return  NULL if invalid,
 *          $label if valid
 */
function check_label($label, $instr) {
  if (!preg_match("/^[a-zA-Z_\-$&%*!?][a-zA-Z0-9_\-$&%*!?]*$/", $label) == 1)
    return false;
  global $stats;
  /*
  global $labels_defined;
  global $labels_undefined;
  global $fwjumps_cnt;
  global $jumps_cnt;
  */

  if ($instr == 'LABEL') {
    //$labels_cnt++;  // TODO remove from main switch
    //if (!in_array($label, $labels_defined)) {
    if (!in_array($label, $stats['labels_defined'])) {
      // if v array undefined - prepise se do defined a pocet, co byl v undefined u daneho klice se da do fwdjumps
      //print_r($labels_undefined);
      //if (array_key_exists($label, $labels_undefined)) {
      if (array_key_exists($label, $stats['labels_undefined'])) {
        //$fwjumps_cnt += $labels_undefined[$label];
        $stats['fwjumps'] += $stats['labels_undefined'][$label];
        // delete from undefined array
        //unset($labels_undefined[$label]);
        unset($stats['labels_undefined'][$label]);
      }
      //array_push($labels_defined, $label);
      array_push($stats['labels_defined'], $label);
    } // else redefinice - neresime?

  } else { // eg JUMP, JUMPIFEQ...
    //$jumps_cnt++;
    $stats['jumps']++;
    
    // is the label defined yet? -> if yes then backjump
    
    //if (in_array($label, $labels_defined)) {
    if (in_array($label, $stats['labels_defined'])) {
      //$backjumps_cnt++;
      $stats['backjumps']++;
      // vyresit neco, abychom vedeli, co u return atd.

      return true;
    
    } // else

    // not defined yet - forward or bad jump
    if (array_key_exists($label, $stats['labels_undefined'])) {
      //$labels_undefined[$label] += 1;
      $stats['labels_undefined'][$label] += 1;
    } else {
      // label not defined yet
      //$labels_undefined += array($label=>1);
      $stats['labels_undefined'] += array($label=>1);
    }
  }
  // TODO remove
  //echo "LABELS DEFINED\n";
  //print_r($stats['labels_defined']);
  //echo "LABELS UNDEFINED\n";
  //print_r($stats['labels_undefined']);
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

  if (($type == 'string')) {//} and (($string = check_string($word)) != NULL)) {
    $string = check_string($word);
    if (is_null($string))
      return NULL;
    if ($string == "") // - maybe return sth like string_empty and then check in the main function and don't print the string
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

// parse the command line arguments
parse_cmdline($argv);
//echo "PARSE OK\n";

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
    //$comments_cnt++;
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
  
  //$loc_cnt++;
  $stats['loc']++;
  // split the line by white characters
  $line = preg_split('/\s+/',$line_str);
  // remove empty elements
  $line = array_values(array_filter($line, "is_var_empty"));

  // create an instruction element
  $instruction_el = $xml->createElement("instruction");
  //$instruction_el->setAttribute("order", ++$instr_cnt);
  $instruction_el->setAttribute("order", ++$stats['instr']);
  $instruction_el->setAttribute("opcode", strtoupper($line[0]));
  $program_el->appendChild($instruction_el);
  
  switch(strtoupper($line[0])) {
    // INSTRUCTION
    case 'RETURN':
      //$jumps_cnt++;
      $stats['jumps']++;
    case 'CREATEFRAME';
    case 'PUSHFRAME';
    case 'POPFRAME';
    case 'BREAK': // TODO is BREAK a jump?
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
      /*
      if (!in_array($line[1], $labels_array)) {
        array_push($labels_defined, $line[1]);  // syntax is checked later
      }
      */
    case 'CALL';
    case 'JUMP':
      //if ($line[0] != 'LABEL')
        //$jumps_cnt++;
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
        echo "INSTRUCTION <var> <type> - BAD - $stats[0]\n";
        exit(23);
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
      //$jumps_cnt++;
      $type_text1 = check_symb($line[2]);
      $type_text2 = check_symb($line[3]);
      if ((count($line) != 4) or 
          !check_label($line[1], $line[0]) or
          empty($type_text1) or
          empty($type_text2)) {
        echo "INSTRUCTION <label> <symb1> <symb2> - BAD - $stats[0]\n";
        exit(23);
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
      echo("Problem on line starting with: [".$line[0]."]\n");
      exit(22);
  }
  
  // check comments (for stats)
  foreach ($line as $v) {
    if (str_contains("$v", '#')) {
      //$comments_cnt++;
      $stats['comments']++;
      break;
    }
  }
}

echo($xml->saveXML());

if (count($argv) != 1)
  save_stats($cli_args, $stats);
//echo "stats saved\n";
?>