<?php
    //Globalni promenne
    $directory = getcwd();
    $parseScript = "parse.php";
    $intScript = "interpret.py";
    $recursive = false;

    /*Kontrola argumentu
        Funkce zkontroluje, zda jsou na vstupu spravne zadany parametry, a upravi hodnoty potrebnych
        globalnich promennych.
        @argument   Parametry ke kontrole 
        @return     Int hodnota, kde 0 znamena spravne zadane parametry, 1 napoveda, 10 pro chybu
    */
    function checkArg($arg)
    {
        global $directory, $parseScript, $intScript, $recursive;
        $found = false;
        $retVal = 0;
        $argCount = Count($arg);
        foreach($arg as $value)
        {
            if($value == "--help")
            {
                if($argCount == 2)
                {
                    echo("Skript typu filtr nacte ze standardniho vstupu zdrojovy kod v IPPcode18,\nzkontroluje lexikalni a syntaktickou spravnost kodu.\nNasledne vypise na standardni vystup XML reprezentaci programu\n");
                    return (1);    
                }
                else
                    return ($retVal + 10);
            }
            switch ($value) 
            {
                case (preg_match('/^--directory=.*/', $value) ? true : false):
                    preg_match('/=.*/', $value, $matchArray);
                    $directory = $matchArray[0];
                    $directory = substr($directory, 1);
                    break;
                case (preg_match('/^--recursive$/', $value) ? true : false):
                    $recursive = true;
                    break;
                case (preg_match('/^--parse-script=.*/', $value) ? true : false):
                    preg_match('/=.*/', $value, $matchArray);
                    $parseScript = $matchArray[0];
                    $parseScript = substr($parseScript, 1);
                    break;
                case (preg_match('/^--int-script=.*/', $value) ? true : false):
                    preg_match('/=.*/', $value, $matchArray);
                    $intScript = $matchArray[0];
                    $intScript = substr($intScript, 1);
                    break;
                default:
                    if($value != $arg[0])
                    {
                        return $retVal + 10;
                    }
                    break;
            }
        }
        return $retVal;
    }

    /*Hledani adresaru
        Funkce prohleda adresar, pokud je nutno, tak rekursivne 
    */
    function findFiles($directory, $recursive)
    {
        $result = array(); 
        $files = scandir($directory); 
        foreach ($files as $value) 
        { 
            //odfiltruju odpad
            if (!in_array($value,array(".",".."))) 
            {
                if (is_dir("$directory/$value")) 
                { 
                    if($recursive)
                    {
                        $dirFiles = findFiles("$directory/$value", $recursive);
                        $result = array_merge($result, $dirFiles);
                    }
                } 
                else 
                    $result[] = "$directory/$value"; 
            } 
        } 
        return $result; 
    }

    /*Hledani a vytvareni adresaru
        Funkce prohleda adresar a vytvori potrebne soubory 
    */
    function find()
    {
        global $directory, $parseScript, $intScript, $recursive;
        $files = findFiles($directory, $recursive);
        $isThere = false;
        //Projdu hodnoty a najdu neco.src
        //tady bude asi foreach
        $match = preg_grep('/.*\.src$/', $files);
        $match = array_values($match);
        if($match == null)
        {
            return null;
        }
        else
        {
            foreach ($match as $value) 
            {
                //zjistime jestli jsou soubory in,out,rc ve files a dystak zalozime ve spravnem adresari
                $value = str_replace(".src", ".in", $value);
                $isThere = in_array($value, $files);
                if(!$isThere)
                {
                    $myfile = fopen("$value", "w");
                    fclose($myfile);
                }
                $value = str_replace(".in", ".out", $value);
                $isThere = in_array($value, $files);
                if(!$isThere)
                {
                    $myfile = fopen("$value", "w");
                    fclose($myfile);
                }
                $value = str_replace(".out", ".rc", $value);
                $isThere = in_array($value, $files);
                if(!$isThere)
                {
                    $myfile = fopen("$value", "w");
                    fwrite($myfile, "return 0");
                    fclose($myfile);
                }
            }
        }
        return $match;
    }

    /*Hledani adresaru
        Funkce testuje scripty 
    */
    function test($match)
    {
        global $parseScript, $intScript;
        //mozna bude treba doopravit, aby nebyl prepsan soubor
        $testOut = array();
	    $returnVal = array();
        foreach ($match as $value) 
        {
	        $value = str_replace(".src", "", $value);
            $helpValue = $value . "tests";
            $myfile = fopen("$helpValue.in", "w");
            fclose($myfile);
            $myfile = fopen("$helpValue.out", "w");
            fclose($myfile);
            exec("php $parseScript < $value.src > $helpValue.in", $trash, $returnVal1);
            exec("python $intScript --source=$helpValue.in < $value.in > $helpValue.out", $trash, $returnVal2);
            $myfile = fopen("$helpValue.out", 'a');
            fwrite($myfile, "\n");
            fclose($myfile);
            $result = exec("diff $helpValue.out $value.out");
	        unlink("$helpValue.out");
	        unlink("$helpValue.in");
            $testOut[] = $result;
	        if($returnVal1 == 0 || $returnVal1 == null)
	            $eq = $returnVal2;	
	        else
	            $eq = $returnVal1;
	        $myfile = fopen("$value.rc", "r");
	        $fileValue = fread($myfile,filesize("$value.rc"));
            fclose($myfile);
	        if($fileValue == $eq)
	 	        $returnVal[] = null;
	        else
		        $returnVal[] = $eq;
        }
        htmlGenerate($match, $testOut, $returnVal);
    }

    /*Hledani a vytvareni adresaru
        Funkce vygeneruje vystupni stranku 
    */
    function htmlGenerate($match, $testOut, $returnVal)
    {
        ?>
        <!DOCTYPE html>
        <head>
            <meta charset="utf-8" />
            <title>Index</title>
        </head>
        <body>
	    <div>
            <h1 style="color:brown;">Testy</h1>
            <p><?php 
	    foreach($match as $i => $value)
	    {
		    echo("<dl>");
		    echo("<dt><h2>Test cislo $i:</h2></dt>");
		    echo("<dd>Umisten v $value</dd>");
		    echo("<br>");
		    if($testOut[$i] == null && $returnVal[$i] == null)
			    echo("<dd><strong style=\"font-size: 15pt;color:green;\">Test prosel</strong></dd>");
		    else
		    {
			    echo("<dd><strong style=\"font-size: 15pt;color:red;\">Test neprosel.</strong></dd>");
			    echo("<dd>$testOut[$i]</dd>");
		    }
		    echo("</dl>");
	    }
	    ?></p>
	    </div>
        </body>
        </html>
        <?php
    }

    //Hlavni funkce programu
    function main($argv)
    {
        global $directory, $parseScript, $intScript, $recursive;
        $returnVal = 0;
        $returnVal = checkArg($argv);
        //Pokud byli spatne zadany argumenty je skript ukoncen
	if($returnVal == 1)
	    exit(0);
        if($returnVal == 10)
            exit($returnVal);
        //Testy
        $match = find();
        test($match);
        exit($returnVal);
    }
    main($argv);      
?>
