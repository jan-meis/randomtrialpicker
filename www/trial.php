<!DOCTYPE html>
<html>
<head>
<link rel="stylesheet" href="style.css">
<script src="get_random_trial.js"></script>
<script>
</script>
<meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>

<body>

<div class = "container">
    <br>
    <input class = "button" type="button" id="get_random_trial_button" value="New random trial" onclick="get_random_trial();" />
    <br><br><br>

    <?php
    $env = parse_ini_file('.env');
    $user = $env["user"];
    $password = $env["password"];
    $database = $env["database"];
    $table = $env["table"];

    $table_abstract = $table . "_abstract";
    $pmid = intval($_GET['PMID']);

    if ($pmid==0) {
        echo "<b>Please stop trying to hack my database. </b> <br><br><br><br>";
    } else {
        try {
            $db = new PDO("pgsql:host=localhost;dbname=$database", $user, $password);
            $row = $db->query("SELECT * FROM $table WHERE pmid=$pmid LIMIT 1;")->fetch();
            $rows_abstract = $db->query("SELECT * FROM $table_abstract where pmid=$pmid;")->fetchAll();
            } catch (PDOException $e) {
                print "Error!: " . $e->getMessage() . "<br/>";
                die();
            }
        
            $issue = "";
            if (!is_null($row["journalissue_issue"]) & !($row["journalissue_issue"]=="")){
                $issue = "(" . $row["journalissue_issue"] . ")";
            }
            $doi = "";
            if (!is_null($row["doi"]) & !($row["doi"]=="")){
                $doi = "<center>" . "DOI: " . "<a href='https://doi.org/" . $row["doi"] . "'>" . $row["doi"]  . "</a>" . "</center>";
            }
        
            echo "<center><b>" . $row["articletitle"] . "</b></center>" . "<br><br>";
            echo "<center>" . $row["names"] . "</center>" . "<br><br>";
            echo "<center>" . $row["journalissue_pubdate_year"] . "</center>" . "<br><br>";
            echo "<center>" . $row["journal_title"] . ", " . $row["journalissue_volume"] . $issue . "</center>" . "<br><br>";
        
            echo $doi . "<br><br>";
            echo "<h2> Abstract </h2>";
            foreach ($rows_abstract as $abstract) {
                if (str_starts_with(strtoupper($abstract["label"]), "TRIAL REGI") &&
                    preg_match(
                        "@NCT[0-9]+@",
                        $abstract["text"],
                        $NCT_num,
                    )) {
                    $newtext = preg_replace(
                        "@NCT[0-9]+@",
                        "<a href='https://clinicaltrials.gov/study/" . $NCT_num[0] . "'>" . $NCT_num[0] . "</a>",
                        $abstract["text"],
                        1
                    );
                    echo "<h3>" . $abstract["label"] . "</h3>" . "<p>" . $newtext . "</p>";
                    if (is_null($newtext)) {
                        echo "help";
                    }
                } else {
                    echo "<h3>" . $abstract["label"] . "</h3>" . "<p>" . $abstract["text"] . "</p>"; 
                }
            }
            echo "<br><br><br>";
    }
    ?>

    <p><i> Data presented here are derived from the <a href="https://pubmed.ncbi.nlm.nih.gov/download/"> PubMed dataset</a> (annual baseline 2023).
        Some abstracts may be subject to copyright.</a> </i> </p>

</div>

</body>
</html>


