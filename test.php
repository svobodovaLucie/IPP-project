<?php

/**
 * Global variables.
 */
$options = array();

/**
 * Function prints help to stdout.
 */
function print_help() {
  echo "HELP\n";
}

/**
 * Function checks if there is a --directory option.
 * If not, the default value "." is set.
 */
function check_directory() {
  global $options;
  if (!(array_key_exists('directory', $options))) {
    $options['directory'] = ".";
  }
}

/**
 * Function checks if there is a --parse-script option.
 * If not, the default value "." is set.
 */
function check_parse_script() {
  global $options;
  if (!(array_key_exists('parse-script', $options))) {
    $options['parse-script'] = "parse.php";
  } else {
    // pripojit /parse.php
  }
}


function check_int_script() {
  global $options;
  if (!(array_key_exists('int-script', $options))) {
    $options['int-script'] = ".interpret.py";
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
  //$options['jexampath'] .= 'jexamxml.jar';
}


/**
 * Function parses command line arguments and checks them.
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
  $options = getopt(NULL, $longopts, $restindex);

  echo "OPTIONS BEFORE CHECK\n";
  var_dump($options);

  if (array_key_exists('help', $options)) {
    print_help();
    if (count($argv) != 2) {
      exit(10);
    }
  }

  if (count($argv) != count($options) + 1) {
    echo "BAD ARGUMENTS -> exit 10\n";
    exit(10);
  }

  check_directory();
  check_parse_script();
  check_int_script();
  check_jexampath();

  echo "OPTIONS AFTER CHECK\n";
  var_dump($options);
}


function generate_html_structure() {
  global $html;
  $html->formatOutput = true;

  // create a program element
  $html_el = $html->createElement("html");
  $html_el->setAttribute("lang", "en");
  $html->appendChild($html_el);

  $head = $html->createElement("head");
  $html_el->appendChild($head);

  $style = $html->createElement("style", "
    body {background-color: rgb(251, 251, 251);}
    h1   {color: green; font-family: 'Lucida Sans', sans-serif}
    p    {color: purple;}
    p.passed {color: green; font-family: 'Lucida Sans', sans-serif;}
    div     {margin: auto}
    div.all {display: flex; width: auto; margin: auto; border-top: 1px black solid; border-bottom: 1px black solid; /* border: 1px solid gray; border-radius: 20px;*/ padding: 10px; margin: 20px;; font-family: 'Lucida Sans', 'Lucida Sans Regular', 'Lucida Grande', 'Lucida Sans Unicode', Geneva, Verdana, sans-serif;}  
    div.percent {display: inline-block; width: auto; top: 50%; color:red; padding-left: 10px; font-weight: bold; font-size: larger;}
    div.summary {display: inline-block; width: auto; color: green}
    
    div.tests {width: auto; /*border: 1px solid gray;*/ border-radius: 20px; padding: 20px; margin: 20px; font-family: 'Lucida Sans', 'Lucida Sans Regular', 'Lucida Grande', 'Lucida Sans Unicode', Geneva, Verdana, sans-serif;}  
    .one-test {display: flex; border-bottom: solid gray 1px; width: auto; position: center; padding: 5pt; margin: 2pt; font-family: 'Lucida Sans', 'Lucida Sans Regular', 'Lucida Grande', 'Lucida Sans Unicode', Geneva, Verdana, sans-serif;}  
    .test_num {display: inline-block; width: 2%; color: back; margin-left: 2%; margin-right: 1%; font-weight: medium;}
    .test_stat {display: inline-block; width: 73%; color: black;}
    /*.td {margin: 5pt 10pt 0pt 0pt;} */
    .test_res_p {display: inline-block; width: 7%; color: green; margin-right: 6%; font-size: large; font-weight: medium;}
    .test_res_f {display: inline-block; width: 7%; color: red; margin-right: 6%; font-size: large; font-weight: medium;}
    header {display: flex;}
  ");
  $head->appendChild($style);

  $body = $html->createElement("body");
  $html_el->appendChild($body);

  $header = $html->createElement("header");
  $body->appendChild($header);

  $div1 = $html->createElement("div");
  $div1->setAttribute("style", "display: inline-block; margin-left: 15pt;");
  $header->appendChild($div1);

  $h = $html->createElement("h1", "IPP 2022 - Výsledky testů");
  $div1->appendChild($h);

  $div2 = $html->createElement("div", "Vytvořeno 78.4.3469");
  $div2->setAttribute("style", "display: inline-block; margin-right: 15pt;");
  $header->appendChild($div2);
}

function html_add_test_summary() {
  $percent = 50;
  $stat_labels = ["Celkem testů", "Úspěšných", "Neúspěšných"];
  $stat_values = [900, 899, 1];
  global $html;

  $body = $html->getElementsByTagName('body')->item(0);

  $div1 = $html->createElement("div");
  $div1->setAttribute("class", "all");
  $body->appendChild($div1);

  $div21 = $html->createElement("div");
  $div21->setAttribute("class", "summary");
  $div1->appendChild($div21);

  $table = $html->createElement("table");
  $div21->appendChild($table);

  for ($i=0; $i < 3; $i++) { 
    $test_num = $i;

    $tr = $html->createElement("tr");
    $table->appendChild($tr);

    $td1 = $html->createElement("td", $stat_labels[$i]);
    $tr->appendChild($td1);

    $td2 = $html->createElement("td", $stat_values[$i]);
    $tr->appendChild($td2);
  }

  $div22 = $html->createElement("div", "$percent%");
  $div22->setAttribute("class", "percent");
  $div1->appendChild($div22);

  $div0 = $html->createElement("div");
  $div0->setAttribute("class", "tests");
  $body->appendChild($div0);
}


function html_add_test_log(/*$test_num, $test_spec*/) {
  $test_num = 0;
  $test_spec_labels = ["Testovaný soubor", "Očekávaný návratový kód", "Skutečný návratový kód", "Výpis na stderr"];
  $test_spec = ["folder1/folder2/file.txt", "0", "1", "STDERRblah"];

  /*
  foreach($dom->getElementsByTagName('div') as $div) { 
        $class = $div->getAttribute('class');
    }
    */

  global $html;
  //$body = $html->childNodes->item(0);
  $body = $html->getElementsByTagName('div')->item(5);

  $div1 = $html->createElement("div");
  $div1->setAttribute("class", "one-test");
  $body->appendChild($div1);

  $div21 = $html->createElement("div", $test_num);
  $div21->setAttribute("class", "test-num");
  $div1->appendChild($div21);

  $div22 = $html->createElement("div");
  $div22->setAttribute("class", "test-stat");
  $div1->appendChild($div22);

  $table = $html->createElement("table");
  $div22->appendChild($table);

  for ($i=0; $i < 3; $i++) { 
    $test_num = $i;

    $tr = $html->createElement("tr");
    $table->appendChild($tr);

    $td1 = $html->createElement("td", $test_spec_labels[$i]);
    $tr->appendChild($td1);

    $td2 = $html->createElement("td", $test_spec[$i]);
    $tr->appendChild($td2);
    }
}



//--------------------------------------------------------------------------------------------------
/**
 * Function checks if a file exists and if not it generates the default.
 */
function generate_file($file_name, $suffix) {
  $output = array();
  $return_val = NULL;
  exec("find | grep ".$file_name.$suffix, $output, $return_val);
  if ($return_val == 0) {
    return;
  }
  // generate new file
  $file = fopen($file_name.$suffix, 'w') or die('Error opening file: '+$file_name);
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
 * We are in the "." now.
 * 
 * @param $test_name_src
 */
function test_setup($test_name) {
  // cut the .src from test name - done before
  //$test_name = substr($test_name_src, 0, strlen($test_name_src) - 4);

  // check test_name.in
  generate_file($test_name, ".in");

  // check test_name.out
  generate_file($test_name, ".out");

  // check test_name.rc
  generate_file($test_name, ".rc");
}

/**
 * Function executes the parse-only tests.
 * 
 */
function exec_parser($file) {
  global $options;

  echo "EXECUTING PARSER TEST\n";
  $script = $options["parse-script"];

  // run the parser script
  $output = array();
  $return_val = NULL;
  exec("php8.1 ".$script." <".$file.".src >".$file.".out_parse_tmp", $output, $return_val);
  echo "return_val: $return_val\n";

  // check the return values
  //echo("diff $file.rc <(echo -n \"$return_val\")"); //<(echo -n "0"
  //exec("diff $file.rc <(echo -n \"$return_val\")", $output, $return_val); //<(echo -n "0"
  $rc = fopen($file.".rc_tmp_parse", 'w');// or die('Error opening file: '+$file);
  echo "$rc\n";
  $sth = fwrite($rc, $return_val);
  fclose($rc);

  exec("diff $file.rc $file.rc_tmp_parse", $output, $return_val_diff);
  if ($return_val_diff == 0) {
    if ($return_val != 0) {
      echo "PASSED with return code $return_val\n";
      return;
    }
    // xml compare (.out with .out_tmp_parse)
    $jexamxml_dir = $options["jexampath"];
    exec("java -jar $jexamxml_dir"."jexamxml.jar $file.out $file.out_parse_tmp diffs.xml  -D $jexamxml_dir"."options", $output, $return_val_jexamxml);
    if ($return_val_jexamxml == 0) {
      echo "PASSED\n";
    }
  } else {
    echo "FAILED\n";
  }
}

function exec_int() {
  global $options;

  echo "EXECUTING INT TEST\n";

}


function test_exercise($file) {
  echo "Executing exercise\n";
  // parse-only
  exec_parser($file);

  // int-only
}

function iterate_the_files() {
  global $options;
  // Construct the iterator
  $it = new RecursiveDirectoryIterator($options['directory'], RecursiveDirectoryIterator::SKIP_DOTS);

  // Loop through files
  foreach(new RecursiveIteratorIterator($it) as $file) {
    //          hidden folder                     other file than .src
    if ((preg_match("/^\./", $it) == 1) || ($file->getExtension() != 'src')) {    // TODO better to remove this and skip the hidden directories somehow (skip_dots doesn't work)
      continue;
    }
    // .src file
    $test_name = substr($file, 0, strlen($file) - 4);
    echo $test_name."\n";
    test_setup($test_name);
    test_exercise($test_name);

  }
}


function main($argv) {
  parse_arg($argv);

  $output = array();
  //exec('slothcalc', $output, $return_val);


  

  iterate_the_files();
}

main($argv);
/*
// generate HTML
$html = new DomDocument();

generate_html_structure();

html_add_test_summary();

html_add_test_log();
html_add_test_log();
html_add_test_log();

echo("<!DOCTYPE html>");
echo($html->saveHTML());
// html_add_div();
*/
?>