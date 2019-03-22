<?php

    const INSTRUCTIONS = array(".IPPCODE18" => 0, "MOVE" => 2, "CREATEFRAME" => 0, "PUSHFRAME" => 0, 
    "POPFRAME" => 0, "DEFVAR" => 1, "CALL" => 1, "RETURN" => 0, "PUSHS" => 1, "POPS" => 1, 
    "ADD" => 3, "SUB" => 3, "MUL" => 3, "IDIV" => 3, "LT" => 3, "GT" => 3, "EQ" => 3, 
    "AND" => 3, "OR" => 3, "NOT" => 2, "INT2CHAR" => 2, "STRI2INT" => 3, "READ" => 2,
    "WRITE" => 1, "CONCAT" => 3, "STRLEN" => 2, "GETCHAR" => 3, "TYPE" => 2, "SETCHAR" => 3, 
    "LABEL" => 1, "JUMP" => 1, "JUMPIFEQ" => 3, "JUMPIFNEQ" => 3, "DPRINT" => 1, "BREAK" => 0);

    const INSTRUCTIONSTYPES = array(".IPPCODE18" => array(), "MOVE" => array("var","symb"), "CREATEFRAME" => array(), "PUSHFRAME" => array(), 
    "POPFRAME" => array(), "DEFVAR" => array("var"), "CALL" => array("label"), "RETURN" => array(), "PUSHS" => array("symb"), "POPS" => array("var"), 
    "ADD" => array("var","symb","symb"), "SUB" => array("var","symb","symb"), "MUL" => array("var","symb","symb"), "IDIV" => array("var","symb","symb"), "LT" => array("var","symb","symb"), "GT" => array("var","symb","symb"), "EQ" => array("var","symb","symb"), 
    "AND" => array("var","symb","symb"), "OR" => array("var","symb","symb"), "NOT" => array("var","symb"), "INT2CHAR" => array("var","symb"), "STRI2INT" => array("var","symb","symb"), "READ" => array("var","type"),
    "WRITE" => array("symb"), "CONCAT" => array("var","symb","symb"), "STRLEN" => array("var","symb"), "GETCHAR" => array("var","symb","symb"), "TYPE" => array("var","symb"), "SETCHAR" => array("var","symb","symb"), 
    "LABEL" => array("label"), "JUMP" => array("label"), "JUMPIFEQ" => array("label","symb","symb"), "JUMPIFNEQ" => array("label","symb","symb"), "DPRINT" => array("symb"), "BREAK" => array() );

    //Trida obsahujici zakladni hodnoty argumentu instrukce
    class Argument
    {
        //promenne
        public $arg = "";
        public $type = "";
        public $inf;
        //metody
        function setArg($value) 
        {
            $this->arg = $value;
        }
        function getArg() 
        {
            return $this->arg;
        }
        function setType($value) 
        {
            $this->type = $value;
        }
        function getType() 
        {
            return $this->type;
        }
        function setInf($value) 
        {
            $this->inf = $value;
        }
        function getInf() 
        {
            return $this->inf;
        }
    }    

    //Trida udrzujici hodnoty jedne instrukce
    class Token
    {
        //promenne
        public $instruc = "";
        public $argArr = array();
        //metody
        function setInst($value) 
        {
            $this->instruc = $value;
        }
        function getInst() 
        {
            return $this->instruc;
        }
        function addArg($value) 
        {
            array_push($this->argArr, $value);
        }
        function getArgArr() 
        {
            return $this->argArr;
        }
    }

    /*  Kontrola parametru
        Funkce zkontroluje, zda jsou na vstupu spravne zadany parametry
        @argument $arg Parametry ke kontrole 
        @return int hodnota, kde 0 znamena spravne zadane parametry, 1 napoveda, 10 pro chybu
    */
    function checkArg($arg)
    {
        $argCount = Count($arg);
	if($argCount > 2)
		return 10;
        foreach($arg as $value)
        {
            if($value == "--help")
            {
                if($argCount == 2)
                {
                    echo("Skript typu filtr nacte ze standardniho vstupu zdrojovy kod v IPPcode18,\nzkontroluje lexikalni a syntaktickou spravnost kodu.\nNasledne vypise na standardni vystup XML reprezentaci programu\n");
                    return 1;    
                }
                else
                    return 10;
            }
            elseif($value != $arg[0])
                return 10;
        }
        return 0;
    }

    /*  Generace XML
        Funkce vygeneruje XML vystup
        @argument $tokenArr pole parametru ke generaci
    */
    function XMLgenerate($tokenArr)
    {
        $count = 1;

        $xml = xmlwriter_open_memory();
        xmlwriter_set_indent($xml, 1);       
        xmlwriter_start_document($xml, '1.0', 'UTF-8');

        xmlwriter_start_element($xml, "program");
        xmlwriter_start_attribute($xml, "language");
        xmlwriter_text($xml, "IPPcode18");
        xmlwriter_end_attribute($xml);

        foreach ($tokenArr as $token) 
        {
            xmlwriter_start_element($xml, "instruction");

            xmlwriter_start_attribute($xml, "order");
            xmlwriter_text($xml, "$count");
            xmlwriter_end_attribute($xml);

            xmlwriter_start_attribute($xml, "opcode");
            xmlwriter_text($xml, $token->getInst());
            xmlwriter_end_attribute($xml);

            $argCount = 1;
            foreach ($token->getArgArr() as $argument) 
            {
                xmlwriter_start_element($xml, "arg" . "$argCount");

                xmlwriter_start_attribute($xml, "type");
                xmlwriter_text($xml, $argument->getType());
                xmlwriter_end_attribute($xml);
                xmlwriter_text($xml, $argument->getInf());

                xmlwriter_end_element($xml);
                $argCount++;
            }

            xmlwriter_end_element($xml);
            $count++;
        }
        xmlwriter_end_element($xml);
        xmlwriter_end_document($xml);
        echo xmlwriter_output_memory($xml);
    }

    /*  Lexikalni a syntakticka analyza
        Funkce analyzuje jestli je vstup spravne lixakalne zadan
        @param $line radek ke zpracovani
        @return $token trida s hodnotama instrukce
    */
    function Analyze($line)
    {   
        $inst = INSTRUCTIONS;
        $token = new Token();
        $token->setInst("");
        $line = preg_replace("/\s+/", " ", $line);
        $part = explode("#", $line);
        if($part[0] == null || $part[0] == " ")
        {
            $token->setInst("#");
            return $token;
        }
        $parts = preg_split("/\s+/", $part[0]);
        $parts = array_filter($parts);
        $parts = array_values($parts);
        foreach ($inst as $key => $value) 
        {  
            if(strtoupper($parts[0]) == $key && count($parts) == ($value + 1))
            {
                $token->setInst($key);
                foreach ($parts as $place => $word) 
                {
                    if($place > 0)
                    {
                        $argument = new Argument();
                        $argument->setArg($word);
                        switch($word)
                        {
                        case(preg_match('/^(GF@|LF@|TF@)[a-zA-Z-$&%*_][0-9a-zA-Z-$&%*_]*$/', $word) ? true : false):
                            $tyArg = "var";
			                $argument->setType("$tyArg");
                            $argument->setInf($word);
                            $token->addArg($argument);
                            break;
                        case(preg_match('/^string@([^#\\\\]|\\\\[\d]{3})*$/', $word) ? true : false):
                            $tyArg = "string";
			                $part = explode("@", $word, 2);
                            $argument->setType("$tyArg");
                            $argument->setInf($part[1]);
                            $token->addArg($argument);
                            break;
                        case(preg_match('/^int@([+-]?[0-9]+$)/', $word) ? true : false):
                            $tyArg = "int";
			                $part = explode("@", $word);
                            $argument->setType("$tyArg");
                            $argument->setInf($part[1]);
                            $token->addArg($argument);
                            break;
                        case(preg_match('/^bool@(true|false)$/', $word) ? true : false):
                            $tyArg = "bool";
			                $part = explode("@", $word);
                            $argument->setType("$tyArg");
                            $argument->setInf($part[1]);
                            $token->addArg($argument);
                            break;
                        default:
                            preg_match('/^[a-zA-Z-$&%*_][0-9a-zA-Z-$&%*_]*$/', $word, $labelArr);
                            if($word == "string" || $word == "int" || $word == "bool")
                            {
                                $tyArg = "type";
                                $argument->setType($tyArg);
                                $token->addArg($argument);
                                $argument->setInf($word);
                            }
                            else if($labelArr != null)
                            {
                                $tyArg = "label";
                                $argument->setType($tyArg);
                                $token->addArg($argument);
                                $argument->setInf($word);
                            }
                            else
                                $token->setInst("");
                            break;
                        }
			            foreach(INSTRUCTIONSTYPES as $insName => $insArg)
			            {
			                $neco = $token->getInst();
			                if($insName == $neco)
			                {
				                if($insArg[$place - 1] == "symb" && ($tyArg == "bool" || $tyArg == "int" || $tyArg == "string" || $tyArg == "var"))
				                {   
				                }
				                else if($insArg[$place - 1] == $tyArg)
				                {
				                }
				                else
				                {
				                    $token->setInst("");
				                }
			                }
			            }
                    }
                }   
            }
        }
        return $token;
    }

    //Hlavni funkce programu
    function main($argv)
    {
    $line = array("notNULL");
	$spaces = true;
	$isIPP = false;
    $tokenArr = array();
    $returnVal = 0;
    $returnVal = checkArg($argv);
    if($returnVal == 10)
	    exit($returnVal);
	if($returnVal == 1)
	    exit(0);
    $stdin = fopen('php://stdin', 'r');
    while($line = fgets($stdin)) 
    {
        $token = Analyze($line);
	    if($token->getInst() != "#")
	        $spaces == false;
        if($token->getInst() == "")
	    {
		    $returnVal = 21;
		    exit($returnVal);
	    }
        elseif($token->getInst() != ".IPPCODE18" && $token->getInst() != "#")
            array_push($tokenArr, $token);
	    elseif($token->getInst() == ".IPPCODE18" && $spaces == true)
            $isIPP = true;
    }
	if($isIPP == false)
        exit(21);
    if($returnVal != 21)
        XMLgenerate($tokenArr);
    fclose($stdin);
    exit($returnVal);
    }
    main($argv);
?>
