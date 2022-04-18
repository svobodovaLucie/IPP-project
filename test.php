<?php
/* ***************** test.php ******************** *
 *    Principles of Programming Languages (IPP)    *
 *           Lucie Svobodova, xsvobo1x             *
 *          xsvobo1x@stud.fit.vutbr.cz             *
 *                   FIT BUT                       *
 *                  2021/2022                      *
 * *********************************************** */
/**
 * Test script for testing IPP project - parser (parse.php) and interpret (interpret.py).
 */

/* print warnings to stderr */
ini_set('display_errors', 'stderr');

/**
 * Function prints help to stdout.
 */
function print_help() {
  echo "
Test script for testing IPP project - parser (parse.php) and interpret (interpret.py).
Usage:
php8.1 test.php [--help] [--directory=path] [--recursive] [--parse-script=file]
                [--int-script=file] [--parse-only] [--int-only] [--jexampath=path] [--noclean]
Options:
--help            - prints help
--directory=path  - directory with test inputs
                  - default: \".\"
--recursive       - use test inputs from --directory=path and all its subdirectories
--parse-script    - path to the parse script
                  - default: \"./parse.php\"
--int-script      - path to the interpret script
                  - default: \"./interpret.py\"
--parse-only      - only parse script will be tested
--int-only        - only interpret script will be tested
--jexampath       - path to the directory containing jexamxml.jar file and directory options
                  - default: \"/pub/courses/ipp/jexamxml/\"
--noclean         - temporary files (.out_parse_tmp and .out_int_tmp) won't be removed
";
}

/**
 * Global variables.
 */
$html = new DomDocument();  // output HTML file
$options = array();         // stores the cli arguments
$failed = 0;                // the number of failed tests

/**
 * Function checks if there is a --directory option.
 * If not, the default value "." is set.
 */
function check_directory() {
  global $options;
  if (!(array_key_exists('directory', $options))) {
    $options['directory'] = "./";
  } else if (!(file_exists($options['directory'])) || is_file($options['directory'])) {
      fwrite(STDERR, "--directory does not exist.\n");
      exit(41);
  } else if ($options['directory'][strlen($options['directory'])-1] != '/') {
    $options['directory'] .= '/';
  }
}

/**
 * Function checks if there is a --parse-script option.
 * If not, the default value "./parse.php" is set.
 */
function check_parse_script() {
  global $options;
  if (!(array_key_exists('parse-script', $options))) {
    $options['parse-script'] = "parse.php";
  } else if (!(is_file($options['parse-script']))) {
    fwrite(STDERR, "--parse-script file does not exist.\n");
    exit(41);
  }
}

/**
 * Function checks if there is a --int-script option.
 * If not, the default value "./interpret.py" is set.
 */
function check_int_script() {
  global $options;
  if (!(array_key_exists('int-script', $options))) {
    $options['int-script'] = "interpret.py";
  } else if (!(is_file($options['int-script']))) {
    fwrite(STDERR, "--int-script file does not exist.\n");
    exit(41);
  }
}

/**
 * Function checks if there is a --jexampath option.
 * If not, the default value "/pub/courses/ipp/jexamxml/" is set.
 */
function check_jexampath() {
  global $options;
  if (!(array_key_exists('jexampath', $options))) {
    $options['jexampath'] = "/pub/courses/ipp/jexamxml/";
  } elseif ($options['jexampath'][strlen($options['jexampath'])-1] != '/') {
      $options['jexampath'] .= '/';
  }
  if (!(is_file($options['jexampath']."jexamxml.jar"))) {
    fwrite(STDERR, $options['jexampath']. " directory does not contain jexamxml.jar file.\n");
    exit(41);
  }
}

/**
 * Function parses command line arguments, checks them 
 * and sets them to the default value if necessary.
 * 
 * @param $argv command line arguments
 */
function parse_arg($argv) {
  global $options;
  $longopts = array(
    "help",
    "directory:",
    "recursive",
    "parse-script:",
    "int-script:",
    "parse-only",
    "int-only",
    "jexampath:",
    "noclean",
  );
  $options = getopt("", $longopts, $restindex);

  // check if there is a --help option -> print help
  if (array_key_exists('help', $options)) {
    if (count($argv) != 2) {
      exit(10);
    }
    print_help();
    exit(0);
  }

  // check if there is any invalid combination of arguments
  if ((count($argv) != count($options) + 1) ||
      (array_key_exists('parse-only', $options) && 
        (array_key_exists('int-only', $options) || array_key_exists('int-script', $options))) ||
      (array_key_exists('int-only', $options) && 
        (array_key_exists('parse-only', $options) || array_key_exists('parse-script', $options) 
        || array_key_exists('jexampath', $options)))) {
    fprintf(STDERR, "Invalid combination of command line arguments.\n");
    exit(10);
  }

  // check the args and set the default values
  check_directory();
  check_parse_script();
  check_int_script();
  if (!(array_key_exists('int-only', $options))) {
    check_jexampath();
  }
}  

/**
 * Function generates the main HTML structure with CSS style.
 */
function generate_html_structure() {
  global $html;
  $html->formatOutput = true;

  // create a program element
  $html_el = $html->createElement("html");
  $html_el->setAttribute("lang", "en");
  $html->appendChild($html_el);

  // create a head element
  $head = $html->createElement("head");
  $html_el->appendChild($head);

  // create a style element
  $style = $html->createElement("style", "
  body {background-color: rgb(251, 251, 251); font-family: 'Lucida Sans', sans-serif}
  div  {margin: auto}
  div.all {display: flex; width: auto; margin: auto; border-top: 1px black solid; border-bottom: 1px black solid; padding: 10px; margin: 20px;; font-family: 'Lucida Sans', sans-serif;}  
  div.percent {display: inline-block; width: auto; top: 50%; color:black; padding-left: 10px; font-weight: bold; font-size: x-large;}
  div.summary {display: inline-block; width: 66%; font-weight: bold;}
  div.tests {width: auto; padding: 20px; margin: 20px;}  
  .one-test {display: flex; border-bottom: solid gray 1px; width: auto; position: center; padding: 5pt; margin: 2pt;}      
  .test_res_PASSED {display: inline-block; width: auto; color: green; margin-right: 6%; font-size: large; font-weight: medium;}
  .test_res_FAILED {display: inline-block; width: auto; color: red; margin-right: 6%; font-size: large; font-weight: medium;}
  header {display: flex;}
");
  $head->appendChild($style);

  // create a body element
  $body = $html->createElement("body");
  $html_el->appendChild($body);

  // create a header element
  $header = $html->createElement("header");
  $body->appendChild($header);

  // create div elements
  $div1 = $html->createElement("div");
  $div1->setAttribute("style", "display: inline-block; margin-left: 15pt;");
  $header->appendChild($div1);
  $h = $html->createElement("h1", "IPP 2022 - Výsledky testů");
  $div1->appendChild($h);

  $div2 = $html->createElement("div", date("d. m. Y"));
  $div2->setAttribute("style", "display: inline-block; margin-right: 15pt;");
  $header->appendChild($div2);
}

/**
 * Function generates HTML div with tests summary structure.
 */
function html_summary_structure() {
  global $html, $argv;
  $argv_string = implode('  ', $argv);
  $body = $html->getElementsByTagName('body')->item(0);

  $h = $html->createElement("h2", "Konfigurace testů: $argv_string");
  $h->setAttribute("style", "margin-left: 15pt; font-size: medium; font-weight: lighter; color: gray");
  $body->appendChild($h);

  $div1 = $html->createElement("div");
  $div1->setAttribute("class", "all");
  $body->appendChild($div1);

  $div21 = $html->createElement("div");
  $div21->setAttribute("class", "summary");
  $div1->appendChild($div21);

  // create a table for the test results
  $table = $html->createElement("table");
  $div21->appendChild($table);

  $div22 = $html->createElement("div");
  $div1->appendChild($div22);

  $div0 = $html->createElement("div");
  $div0->setAttribute("class", "tests");
  $body->appendChild($div0);
}

/**
 * Function generates HTML test summary
 * - info about passed and failed tests.
 * 
 * @param $test_num number of all tests
 * @param $passed number of passed tests
 * @param $failed number of failed tests
 */
function html_add_test_summary($test_num, $passed, $failed) {
  global $html;
  $stat_labels = ["Celkem testů", "Úspěšných", "Neúspěšných"];
  $stat_values = [$test_num, $passed, $failed];

  // count the percent of tests passed
  if ($test_num == 0) {
    $percent = 100;
  } else {
    $percent = ($passed/$test_num) * 100;
  }
 
  // save info to the summary table
  $table = $html->getElementsByTagName('table')->item(0);
  for ($i=0; $i < 3; $i++) { 
    $test_num = $i;

    $tr = $html->createElement("tr");
    $table->appendChild($tr);

    $td1 = $html->createElement("td", $stat_labels[$i]);
    $td1->setAttribute("style", "width:163pt; height: 18pt; font-size: large;");
    $tr->appendChild($td1);

    $td2 = $html->createElement("td", $stat_values[$i]);
    $td2->setAttribute("style", "width:auto; height: 18pt; font-size: large;");
    $tr->appendChild($td2);
  }

  // add the percent of tests passed
  $div22_old = $html->getElementsByTagName('div')->item(4);
  $div22 = $html->createElement("div", "$percent%");
  $div22->setAttribute("class", "percent");
  if ($percent >= 50) {
    $div22->setAttribute("style", "color: green");
  } else {
    $div22->setAttribute("style", "color: red");
  }
  $div22_old->parentNode->replaceChild($div22, $div22_old);
}

/**
 * Function add a log about one test to the output HTML.
 * 
 * @param $test_num number of the test
 * @param $test_spec info about the test [test_name, expected_rc, rc]
 * @param $result result in "FAILED" or "PASSED"
 */
function html_add_test_log($test_num, $test_spec, $result) {
  global $html;
  $test_spec_labels = ["Testovaný soubor", "Očekávaný návratový kód", "Skutečný návratový kód", "Výpis na stderr"];
  $body = $html->getElementsByTagName('div')->item(5);

  $div1 = $html->createElement("div");
  $div1->setAttribute("class", "one-test");
  $body->appendChild($div1);

  $div21 = $html->createElement("div", $test_num);
  $div21->setAttribute("style", "width:2%;");
  //$div21->setAttribute("style", "width: 13pt");
  $div1->appendChild($div21);

  $div22 = $html->createElement("div");
  $div22->setAttribute("style", "width:80%;");
  $div1->appendChild($div22);

  $table = $html->createElement("table");
  $div22->appendChild($table);

  // save info about the test name and return codes to the table
  for ($i=0; $i < 3; $i++) { 
    $test_num = $i;

    $tr = $html->createElement("tr");
    $table->appendChild($tr);

    $td1 = $html->createElement("td", $test_spec_labels[$i]);
    $td1->setAttribute("style", "width:165pt; height: 18pt;");
    $tr->appendChild($td1);

    $td2 = $html->createElement("td", $test_spec[$i]);
    $tr->appendChild($td2);
  }
    
  $div23 = $html->createElement("div", $result);
  $div23->setAttribute("class", "test_res_$result");
  $div1->appendChild($div23);
}

/**
 * Function checks if a file exists and if not it generates 
 * the default file.
 * 
 * @param $file_name name of the file
 * @param $suffix suffix in ".in", ".out", ".rc"
 */
function generate_file($file_name, $suffix) {
  global $options;
  $output = array();
  $return_val = NULL;

  // if the file exists -> return
  exec("find " . $options['directory'] . " | grep ".$file_name.$suffix, $output, $return_val);
  if ($return_val == 0) {
    return;
  }

  // the file doesn't exist -> generate new file
  try {
    $file = fopen($file_name.$suffix, 'w');
  } catch (Exception $e) {
    fwrite(STDERR, "Error opening file $file_name.$suffix.\n");
    exit(12);
  }
  if ($suffix == ".rc") {
    fwrite($file, "0");
  }
  fclose($file);
}

/**
 * Function executes the test set up.
 * It checks if all of the required files are in the current
 * directory $dir and generate default files if not.
 * 
 * @param $test_name_src
 */
function test_setup($test_name) {
  // check test_name.in
  generate_file($test_name, ".in");

  // check test_name.out
  generate_file($test_name, ".out");

  // check test_name.rc
  generate_file($test_name, ".rc");
}

/**
 * Function finds out if the parser test passed or failed
 * and saves the info to the output HTML file.
 * If the test failed, 1 is returned to indicate that 
 * the interpret test should not be run.
 * 
 * @param $file src file for the test
 * @param $test_num number of the test
 * @param $rc_exp expected return code
 * @param $return_val test return code
 * 
 * @return 1 if the parser test failed
 */
function save_parser_html($file, $test_num, $rc_exp, $return_val) {
  global $html, $failed;

  // info that will be written to output HTML
  $test_spec = [$file.".src", $rc_exp, $return_val];

  // both parser and interpret tests are run
  // parser return value is 0 -> interpret tests can be run
  if ($return_val == 0) {
    return;
  }
  // parser did not return 0 -> interpret tests cannot be run
  if ($return_val != $rc_exp) {
    // return values does not match ->  FAIL
    html_add_test_log($test_num, $test_spec, "FAILED");
    $failed++;
  } else {
    // parser failed with expected return code -> PASS
    html_add_test_log($test_num, $test_spec, "PASSED");
  }
  return 1; // indicates that the interpret shouldn't interpret the output code
}

/**
 * Function finds out if the only parser test passed or failed
 * and saves the info to the output HTML file. The outputs are 
 * compared using JExamXML tool.
 * 
 * @param $file src file for the test
 * @param $test_num number of the test
 * @param $rc_exp expected return code
 * @param $return_val test return code
 */
function save_parser_only_html($file, $test_num, $rc_exp, $return_val) {
  global $html, $failed, $options;

  // info that will be written to output HTML
  $test_spec = [$file.".src", $rc_exp, $return_val];

  // parse-only tests are run
  if ($return_val != $rc_exp) {
    // different return values -> FAIL
    html_add_test_log($test_num, $test_spec, "FAILED");
    $failed++;
  } else if ($return_val != 0) {
    // return values match and are not 0 -> PASS
    html_add_test_log($test_num, $test_spec, "PASSED");
  } else {
    // return values match and are 0 -> compare XML
    $jexamxml_dir = $options["jexampath"];
    exec("java -jar $jexamxml_dir"."jexamxml.jar $file.out $file.out_parse_tmp diffs.xml \
          -D $jexamxml_dir"."options", $output, $return_val_jexamxml);
    if ($return_val_jexamxml == 0) {
      // XML files are not different -> PASS
      html_add_test_log($test_num, $test_spec, "PASSED");
    } else {
      // XML files are different -> FAIL
      html_add_test_log($test_num, $test_spec, "FAILED");
      $failed++;
    }
  }
}

/**
 * Function executes the parser test.
 * 
 * @param $file source file for the test
 * @param $test_num number of the test
 * 
 * @return 1 if the interpret tests should not be executed
 * 
 */
function exec_parser($file, $test_num) {
  global $options, $html, $failed;

  // run the parser script 
  $script = $options["parse-script"];
  $output = array();
  $return_val = NULL;
  exec("php8.1 $script <$file.src >$file.out_parse_tmp 2>/dev/null", $output, $return_val);

  // get the expected return value
  $rc_exp = trim(file_get_contents($file.".rc"));

  // save info about the test into output HTML file
  if (array_key_exists('parse-only', $options)) {
    save_parser_only_html($file, $test_num, $rc_exp, $return_val);
  } else {
    return save_parser_html($file, $test_num, $rc_exp, $return_val);
  }
}

/**
 * Function finds out if the interpret test passed or failed
 * and saves the info to the output HTML file.
 * 
 * @param $file src file for the test
 * @param $test_num number of the test
 * @param $rc_exp expected return code
 * @param $return_val test return code
 */
function save_int_html($file, $test_num, $rc_exp, $return_val) {
  global $html, $failed, $options;

  // info that will be written to output HTML
  $test_spec = [$file.".src", $rc_exp, $return_val];

  // return values differ -> FAIL
  if ($return_val != $rc_exp) {
    html_add_test_log($test_num, $test_spec, "FAILED");
    $failed++;
    return;
  }
  // return value is not 0 and match expected return value -> PASS
  if ($return_val != 0) {
    html_add_test_log($test_num, $test_spec, "PASSED");
    return;
  }
  // return values are 0 -> diff compare
  exec("diff $file.out $file.out_int_tmp", $output, $return_val_diff);
  if ($return_val_diff == 0) {
    // files don't differ -> PASS
    html_add_test_log($test_num, $test_spec, "PASSED");
  } else {
    // files differ -> FAIL
    html_add_test_log($test_num, $test_spec, "FAILED");
    $failed++;
  }
}

/**
 * Function executes the interpret test.
 * 
 * @param $file source file for the test
 * @param $test_num number of the test
 */
function exec_int($file, $test_num) {
  global $html, $options, $failed;
  
  // run the interpret script
  $script = $options["int-script"];
  $output = array();
  $return_val = NULL;
  if (array_key_exists('int-only', $options)) {
    // int-only tests -> input is test.src file
    exec("python3.8 $script --source=$file.src --input=$file.in >$file.out_int_tmp 2>/dev/null", 
          $output, $return_val);
  } else {
    // testing both parser and interpret -> input is test.out_parse_tmp file
    exec("python3.8 $script --source=$file.out_parse_tmp --input=$file.in >$file.out_int_tmp 2>/dev/null",
          $output, $return_val);
  }

  // get the expecter return values
  $rc_exp = trim(file_get_contents($file.".rc"));

  // save info about the test into output HTML file.
  save_int_html($file, $test_num, $rc_exp, $return_val);
}

/**
 * Execute the test - both/parse-only/int-only
 * 
 * @param $file source file for the test
 * @param $test_num number of the test
 */
function test_exercise_verify($file, $test_num) {
  global $options;
  // parse-only
  if (!(array_key_exists('int-only', $options))) {
    if (exec_parser($file, $test_num) == 1) {
      // do not execute interpret tests - return value of parser os not 0
      return;
    }
  }
  if (!(array_key_exists('parse-only', $options))) {
    exec_int($file, $test_num);
  }
}

/**
 * Function removes temporary files created by parser and interpret
 * only if the --noclean option is not set.
 * 
 * @param $file_name name of the test file
 */
function test_teardown($file_name) {
  global $options;
  if (!(array_key_exists('noclean', $options))) {
    exec("rm $file_name.out_parse_tmp 2>/dev/null");
    exec("rm $file_name.out_int_tmp 2>/dev/null");
  }
}
/**
 * Function executes the nonrecursive tests - only files in the current directory.
 */
function nonrecursive_tests() {
  global $options;
  global $failed;
  $test_num = 0;

  // construct the directory iterator
  try {
    $it = new DirectoryIterator($options['directory']);
  } catch (Exception $e) {
    fwrite(STDERR, "Failed to open the directory ". $options['directory'] .".\n");
    exit(41);
  }

  // iterate through the files and execute the tests
  foreach ($it as $file) {
    // skip all directories, hidden files and other than .src files
    $filePath = $options['directory'].$file;
    if(!is_file($filePath) || (preg_match("/^\./", $file) == 1) || (preg_match("/\.src$/", $file) != 1)) {
      continue;
    }
    $test_num++;
    $test_name = substr($filePath, 0, strlen($filePath) - 4);
    test_setup($test_name);
    test_exercise_verify($test_name, $test_num);
    test_teardown($test_name);
  }

  // add tests summary into output HTML file
  html_add_test_summary($test_num, $test_num - $failed, $failed);
}

/**
 * Function executes the tests with a --recursive option.
 */
function recursive_tests() {
  global $options;
  global $failed;
  $test_num = 0;

  // construct the directory iterator
  try {
    $it = new RecursiveDirectoryIterator($options['directory'], RecursiveDirectoryIterator::SKIP_DOTS);
  } catch (Exception $e) {
    fwrite(STDERR, "Failed to open the directory ". $options['directory'] .".\n");
    exit(41);
  }

  // Loop through files
  foreach(new RecursiveIteratorIterator($it) as $file) {
    // skip the hidden files or files that are not .src
    if ((preg_match("/^\./", $it) == 1) || (preg_match("/\/[^\/\.]*\.src$/", $file) != 1)) {
      continue;
    }
    $test_num++;
    $test_name = substr($file, 0, strlen($file) - 4);
    test_setup($test_name);
    test_exercise_verify($test_name, $test_num);
    test_teardown($test_name);
  }
  // save the tests summary into output HTML file
  html_add_test_summary($test_num, $test_num - $failed, $failed);
}

/**
 * Main body of test.php.
 */
// parse command line arguments -> store them to $options variable
parse_arg($argv);

// generate HTML structure
generate_html_structure();
html_summary_structure();

// execute the nonrecursive or recursive testing
if (array_key_exists('recursive', $options)) {
  recursive_tests();
} else {
  nonrecursive_tests();
}

// print the HTML file to the stdout
echo("<!DOCTYPE html>");
echo($html->saveHTML());

?>
