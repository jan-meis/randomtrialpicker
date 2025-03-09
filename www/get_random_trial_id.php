<?php
$env = parse_ini_file('.env');
$header = $env["HEADER"];
$user = $env["user"];
$password = $env["password"];
$database = $env["database"];
$table = $env["table"];
$table_num = "num_tables";

try {
  $db = new PDO("pgsql:host=localhost;dbname=$database", $user, $password);
  $nrow =  $db->query("SELECT count FROM $table_num;")->fetch()["count"];
  $randomrow = rand(1, $nrow);
  $row = $db->query("SELECT PMID FROM $table LIMIT 1 OFFSET $randomrow;")->fetch();
  echo $row["pmid"];
} catch (PDOException $e) {
    print "Error!: " . $e->getMessage() . "<br/>";
    die();
}
?>
