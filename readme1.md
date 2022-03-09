## Implementační dokumentace k 1. úloze do IPP 2021/2022  
Jméno a příjmení: Lucie Svobodová  
Login: xsvobo1x  

## Úvod  
Cílem prvního úkolu bylo naprogramovat skript `parse.php`, který provádí lexikální a syntaktickou 
analýzu kódu načteného ze standardního vstupu, jehož XML reprezentaci následně vypíše na standardní 
výstup. Součástí mého řešení je i rozšíření `STATP`, díky kterému je možné vypsat do zadaných souborů 
různé statistiky zjištěné z analyzovaného kódu.

## Návrh a implementace  
Základní lexikální a syntaktická analýza se provádí v hlavním těle skriptu `parse.php`. Pro ukládání 
XML reprezentace programu jsem využila knihovnu `DOM`, postupně přidávané elementy jsou ukládány 
do objektu `$xml`. Vstupní program je načítán po řádcích, které jsou postupně analyzovány. Po kontrole 
přítomnosti identifikátoru jazyka (`.IPPcode22`) je z řádku nejdříve odstraněn případný komentář 
a řádek je rozdělen na jednotlivé tokeny, které jsou uloženy do pole `$line`. První prvek pole musí 
podle specifikace obsahovat operační kód. Pro operační kód je vytvořen element `instruction` v `$xml` 
a validita daného operačního kódu je zkontrolována pomocí stavového automatu. Díky němu je zároveň 
zjištěno, kolik by měla daná instrukce obsahovat operandů. Počet a typ operandů je dále zkontrolován 
pomocnými funkcemi, které ke kontrole tokenů většinou používají regulární výrazy. Pokud je vše 
syntakticky i lexikálně správné, jsou pro dané operandy v `$xml` vytvořeny příslušné elementy 
`arg1`, `arg2` a `arg3`. Pokud instrukce není v pořádku, je program ukončen s odpovídajícím návratovým
kódem. Po analýze celého vstupního programu je výsledná XML reprezentace vypsána na standardní výstup.

## Rozšíření  
V projektu jsem implementovala rozšíření `STATP`. Pro ukládání statistik o analyzovaném vstupním 
souboru jsem si vytvořila asociativní pole `$stats`, které obsahuje potřebná počítadla (např. `jumps`, 
`loc`, `comments`) a dvě pole, pole `$labels_defined` obsahuje názvy návěští, která již byla definována, 
a pole `$labels_undefined` obsahuje dosud nedefinovaná návěští spolu s počtem, kolikrát na ně již bylo 
odkazováno v rámci některéjo ze skoků. Pokud je dané návěští později definováno, je tento počet přičten 
ke statistice `fwjumps`. Pokud na konci analýzy celého vstupního souboru jsou nějaká návěští stále 
uložená v poli `$labels_undefined`, znamená to, že daná návěští nebyla definována a i přes to na ně 
měl být proveden skok. Počet skoků na taková návěští je tedy uložen do počítadla `badjumps`. 
Informace o tom, které statistiky mají být vypsané do kterých souborů, jsou na začátku zjištěny 
z argumentů příkazové řádky a uloženy do pole `$cli_args`. Toto pole obsahuje v každém prvku 
další pole, ve kterém jsou sdružené informace o statistikách, které mají být zapsány do jednoho 
souboru. Nultý prvek každého z těchto polí obsahuje název souboru, do kterého mají být statistiky 
zapsány, dalšími prvky jsou samotné názvy statistik. Zjištěné statistiky jsou do zadaných souborů 
zapsány na konci celé analýzy.
