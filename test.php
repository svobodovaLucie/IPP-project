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
    $options['int-script'] = "interpret.py";
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
    .test_num {display: inline-block; width: 2pt; color: back; margin-left: 2%; margin-right: 1%; font-weight: medium;}
    .test_stat {background-color: red; display: inline-block; width: 73%; color: black;}
    /*.td {margin: 5pt 10pt 0pt 0pt;} */
    .test_res_PASSED {display: inline-block; width: 7%; color: green; margin-right: 6%; font-size: large; font-weight: medium;}
    .test_res_FAILED {display: inline-block; width: 7%; color: red; margin-right: 6%; font-size: large; font-weight: medium;}
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

function html_summary_structure() {
  $percent = 50;

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

  $div22 = $html->createElement("div", "$percent%");
  $div22->setAttribute("class", "percent");
  $div1->appendChild($div22);

  $div0 = $html->createElement("div");
  $div0->setAttribute("class", "tests");
  $body->appendChild($div0);

}

function html_add_test_summary($test_num, $passed, $failed) {
  global $html;
  $stat_labels = ["Celkem testů", "Úspěšných", "Neúspěšných"];
  $stat_values = [$test_num, $passed, $failed];
  $percent = ($passed/$test_num) * 100;
 
  $table = $html->getElementsByTagName('table')->item(0);
  for ($i=0; $i < 3; $i++) { 
    $test_num = $i;

    $tr = $html->createElement("tr");
    $table->appendChild($tr);

    $td1 = $html->createElement("td", $stat_labels[$i]);
    $tr->appendChild($td1);

    $td2 = $html->createElement("td", $stat_values[$i]);
    $tr->appendChild($td2);
  }
  // add percent
  $div22_old = $html->getElementsByTagName('div')->item(4);
  $div22 = $html->createElement("div", "$percent%");
  $div22->setAttribute("class", "percent");
  $div22_old->parentNode->replaceChild($div22, $div22_old);
}


function html_add_test_log($test_num, $test_spec, $result) {
  global $html;
  $test_spec_labels = ["Testovaný soubor", "Očekávaný návratový kód", "Skutečný návratový kód", "Výpis na stderr"];

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
    
  $div23 = $html->createElement("div", $result);
  $div23->setAttribute("class", "test_res_$result");
  $div1->appendChild($div23);
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
function exec_parser($file, $test_num) {
  global $options;
  global $html;

  $script = $options["parse-script"];

  // run the parser script
  $output = array();
  $return_val = NULL;
  exec("php8.1 ".$script." <".$file.".src >".$file.".out_parse_tmp", $output, $return_val);

  // check the return values
  $rc_exp = trim(file_get_contents($file.".rc"));

  $test_spec = [$file.".src", $rc_exp, $return_val, "STDERRblah"];

  if ($return_val != $rc_exp) {
    html_add_test_log($test_num, $test_spec, "FAILED");
    return 1;
  }
  if ($return_val != 0) {
    if (array_key_exists('parse-only', $options)) {
      html_add_test_log($test_num, $test_spec, "PASSED");
    }
    return 0;
  }
  // xml compare (.out with .out_tmp_parse)
  $jexamxml_dir = $options["jexampath"];
  exec("java -jar $jexamxml_dir"."jexamxml.jar $file.out $file.out_parse_tmp diffs.xml  -D $jexamxml_dir"."options", $output, $return_val_jexamxml);
  if ($return_val_jexamxml == 0) {
    if (array_key_exists('parse-only', $options)) {
      html_add_test_log($test_num, $test_spec, "PASSED");
    }
    return 0;
  } else {
    html_add_test_log($test_num, $test_spec, "FAILED");
    return 1;
  }
}

function exec_int($file, $test_num) {
  global $options;
  global $html;

  $script = $options["int-script"];

  // run the parser script
  $output = array();
  $return_val = NULL;
  //echo("python 3.8 $script --source=$file.src --input=$file.in >$file.out_int_tmp\n");
  if (array_key_exists('int-only', $options)) {
    exec("python3.8 $script --source=$file.src --input=$file.in >$file.out_int_tmp", $output, $return_val);
  } else {
    exec("python3.8 $script --source=$file.out_parse_tmp --input=$file.in >$file.out_int_tmp", $output, $return_val);
  }
  
  // check the return values
  $rc_exp = trim(file_get_contents($file.".rc"));

  $test_spec = [$file.".src", $rc_exp, $return_val, "STDERRblah"];

  if ($return_val != $rc_exp) {
    html_add_test_log($test_num, $test_spec, "FAILED");
    return 1;
  }
  if ($return_val != 0) {
    html_add_test_log($test_num, $test_spec, "PASSED");
    return 0;
  }
  // diff compare (.out with .out_tmp_parse)
  exec("diff $file.out $file.out_int_tmp", $output, $return_val_diff);
  if ($return_val_diff == 0) {
    html_add_test_log($test_num, $test_spec, "PASSED");
    return 0;
  } else {
    html_add_test_log($test_num, $test_spec, "FAILED");
    return 1;
  }
}


function test_exercise($file, $test_num) {
  global $options;
  // parse-only
  if (!(array_key_exists('int-only', $options))) {
    if (($failed = exec_parser($file, $test_num)) == 1 && (!(array_key_exists('parse-only', $options)))) {
      return 1;
    }
  }
  if (!(array_key_exists('parse-only', $options))) {
    $failed = exec_int($file, $test_num);
  }
  return $failed;
}

function iterate_the_files() {
  global $options;
  $test_num = 0;
  $failed = 0;
  // Construct the iterator
  $it = new RecursiveDirectoryIterator($options['directory'], RecursiveDirectoryIterator::SKIP_DOTS);

  // Loop through files
  foreach(new RecursiveIteratorIterator($it) as $file) {
    //          hidden folder                     other file than .src
    if ((preg_match("/^\./", $it) == 1) || ($file->getExtension() != 'src')) {    // TODO better to remove this and skip the hidden directories somehow (skip_dots doesn't work)
      continue;
    }
    // .src file
    $test_num++;
    $test_name = substr($file, 0, strlen($file) - 4);
    //echo $test_name."\n";
    test_setup($test_name);
    $failed += test_exercise($test_name, $test_num);
  }
  html_add_test_summary($test_num, $test_num - $failed, $failed);
}


function main($argv) {
  parse_arg($argv);

  $output = array();

  // generate HTML
  global $html;

  generate_html_structure();
  html_summary_structure();

  iterate_the_files();

  echo("<!DOCTYPE html>");
  echo($html->saveHTML());

}


$html = new DomDocument();
main($argv);
?>