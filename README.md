# ProiectASC:
asamblorul si executorul pentru un cod scris in RISC-V

Membrii echipei: Leustean Andrei (141), Serbencu Cristian (141), Dan Andrei Delian (141)

Folderul principal al proiectului contine 4 fisiere .py, 3 fisiere .bin si 3 fisiere .in

"Assembler.py" - fisierul care citeste codul din program.in si il scrie in binar in fisierul machine_code.bin

"Executor.py" - fisierul care citeste binarul din machine_code.bin si il executa

"Huffman_encoder.py" - fisierul care preia instructiunile din instr_file.in si le codifica, afisandu-le in Huffman_encoding.in

"Memory.py" - fisierul cu functiile pe care le folosim cand umblam in memorie/stack

"instr_file.in" - fisierul cu toate cele 12 programe RISC-V

"program.in" - fisierul cu programul de rulat in codificare RISC-V

"machine_code.bin" - fisierul binar cu codul masina pentru programul din program.in

"stack_memory_file.bin" - fisierul binar cu stack ul

"main_memory_file.bin" - fisierul binaru cu memoria

"Huffman_encoding.in" - fisierul cu codificarea Huffman a instructiunilor

# Codificarea:
Fisierul Huffman_encoding mai contine pe langa codificarea instructiunilor si o codificare pentru cazul in care dam peste o eticheta 

Instructiunile din programul RISC-V sunt codificate astfel:

          cod(instr)cod(arg1)cod(arg2)....
          
    pentru argumente:
    
        ->registrii sunt codificati toti pe 5 biti 
        
        ->constantele sunt codificate pe 32 de biti
        
        ->sirurile sunt codificate astfel : cod(length)cod(caracter1)cod(caracter2)... unde cod(length) este pe 12 biti intrucat avem doar 4096 de biti de memorie iar caracterele sunt pe 8 biti
        
                exemplu: sirul "abc" ar fi in binar: '000000000011+01100001+01100010+01100011'
                
        ->adresele de memorie (de tip const(registru) ) sunt codifiacte astfel: cod(const)cod(reg) unde cod(const) este pe 12 biti din acelasi motiv ca cel de la siruri ( constantele negative sunt in complement fata de 2 ) .
        
                exemplu: daca codificarea registrului a0 ar fi '10100' atunci 8(a0) ar fi : '000000001000+10100'
                

Etichetele sunt codificate astfel: cod(eticheta)cod(nume) unde numele este codificat ca sirurile

Declararea variabilelor este codificata astfel:

  '1'+ cod(nume)+cod(tip_variabila)+cod(continut) -> in cazul variabilelor .space continutul e inlocuit de numarul de bytes pe care ii ocupa, codificat pe 12 biti.
  Primul bit are rolul de a anunta ca mai sunt variabile de citit. Daca nu este 1 atunci ne oprim din citit variabile.
  
    exemplu: daca codificarea pt asciz ar fi '10' si pt .space ar fi '00' 
    
        atunci abc: .asciz "123" ar fi:
        
        '1'+'000000000011+01100001+01100010+01100011' (codif(nume)) + '10' + '000000000011+00110001+00110010+00110011' (codif(continut))
  
        iar abc: .space 8 ar fi:
        
        '1' + '000000000011+01100001+01100010+01100011' (codif(nume)) + '00' + '000000001000'

  Decodificarea se face invers.

# Rularea:
Pentru a putea rula "Executor.py" trebuie instalata biblioteca parse ( folosita la scanf si printf ) ->  pip install parse

Fisierul Huffman_encoding.in contine deja codificare Huffman deci nu mai este nevoie de Huffman_encoder.py.
Pentru a rula programul trebuie ca urmatoarele fisiere sa se afle in acelasi folder:


    -Assembler.py 
    
    -Executor.py
    
    -Memory.py
    
    -program.in
    
    -machine_code.bin
    
    -stack_memory_file.bin
    
    -main_memory_file.bin

Ordinea rularii este aceasta: mai intai se scrie codul RISC-V in fisierul 'program.in', apoi este rulat programul "Assembler.py" si in final programul "Executor.py".

Pentru a obtine codul binar de la orice program RISC-V, programul trebuie scris in fisierul 'program.in', iar apoi trebuie rula "Assembler.py". Codul masina se gaseste in fisierul 'machine_code.bin'.

# Structura programelor: 

Memory.py contine patru functii prin intermediul carora se poate umbla in memorie si in stiva. ( fill_adress, get_adress, reserve_space si reset_memory )

Asamblorul preia codul din fisier si il transforma in cod binrar dupa regulile de mai sus. Avem 2 string-uri rdata si program in care punem codificarile formate din '1' si '0' ( in rdata punem codificarea pentru sectiunea rodata iar in program pentru sectiunea program ). Dupa aceea le completam cu '0' uri daca este cazul si le afisam, transformandu-le in binar, in fisierul machine_code.bin.

Executorul mai intai rezerva spatiul in memorie si stiva si dupa aceea parcurge sectiunea .rodata in care sunt declarate variabilele, sunt plasate in memorie si dupa aceea puse intr-o lista numita variabile. Dupa aceea, prin functie get_et,s parcurge tot programul ( .rodata ) fara a il executa pentru a gasi etichetele pe care le pune intr-un dictionar numit et. Dupa aceea citeste string-ul de dupa .global si incepe decodificarea si executarea instructiunilor de la pozitia acestui string.
Registrul Global Pointer tine minte pozitia la care ne aflam in program.

# Stiva si Memoria:

Programul stie unde sa puna valoare ( sau de unde sa ia valoarea ) uitandu-se daca pointerul e pozitiv sau negativ. Daca este pozitiv ( sau 0 ) atunci aceasta este locatia din MEMORIE in care umbla, daca e negativ atunci trebuie sa umble in STIVA la adresa 4096 - pointer. 

Aceasta metoda functioneaza intrucat atunci cand umbla in stiva trebuia sa alocam spatiu: addi sp, sp, -8 ( pt 8 bytes ), dupa aceasta instructiune programul stie ca 0(sp) este in realitate 4096-8 = 4088.

# Observatii:

Pentru a putea verifica cu mai mare usurinta cele 12 programe ( majoritatea folosesc variabile de tip word ) am adaugat instructiunea 'sw' in codificare instructiunilor. Altfel as fi putut umbla doar la vectori pe 8 bytes sau 1 byte ( avand doar sd si sb ).

Pentru functiile floating point, intrucat in python nu exista single-precision si double-precision, nu am apucat sa implementam pentru operatiile cu double-precision. Asadar, indiferent de operatie, numerele de tip floating point sunt tinute minte in memorie cu formatul IEE 754, pe 32 de biti - single-precision. 
In plus la scanf si printf am implementat si %c, %f, %s pentru a putea afisa si citi si string-uri, float-uri si caractere.

De asemenea, pentru a verifica cu usurinta programele cu float-uri putem muta prin instr li in registrii normali constante float. Acestea insa nu sunt puse cu valoarea float ci cu valoarea int a formatului IEE-754 pe 32 de biti. ( adica ' li a0, -1.0 ' muta in a0 valoarea -1082130432 ). Astfel putem lucra cu float-uri fara a fi intotdeauna nevoia sa le citim.

Nu este implementata si posibilitatea de a scrie ceva in zona .text ( aceasta este ignorata de asamblor ).


# Procedurile:

Pentru proceduri avem o variabila numita nr_of_jumps initiata cu 0 care tine minte cand am intrat intr-o functie prin intermediul instructiunii call. Asta inseamna ca daca nr_of_jumps este mai mare decat 0 atunci cand citim instructiunea ret ne intoarcem la adresa din registrul ra, iar daca valoarea lui nr_of_jumps este 0 atunci ret inchide programul

# Printf si Scanf:

Pentru a nu fi prea multe decimale, printf afiseaza float-urile cu 2 decimale. Acestea insa sunt retinute in memorie complet. ( oricand poate fi modificata precizia )

Functia scanf f citeste string-ul de la input si apoi inlocuieste %s, %c, %f, %d cu echivalentele lor in formatarea regex a python-ului. Dupa aceea folosind biblioteca parse, le extrage intr-o lista si pe rand le pune in adresele de memorie din registrii dati ca argumente ( in aceasta ordine: a0, a1, a2, ....). Daca string-ul de la input nu este identic cu cel dat ca parametru (fara %d) atunci intoarce eroare (fireste, spatiile de la inceputul si sfarsitul celor doua string-uri -cel de la input si cel dat ca argument- nu vor fi luate in calcul). 

De exemplu:               
                           citirea unui integer in variabila x
                          
                          la a1, x        (x:.space4)
                          la a0, formatscan (formatscan: .asciz "%d !@$")
                          call scanf
             
              Daca in exemplul de mai sus string-ul citit nu este de forma: "13 !@$" (unde 13 poate fi inlocuit cu orice numar), va intoarce eroare
Functia printf, trece la fiecare % din string-ul primit ca input si il inlocuieste cu valoare din argumentul respectiv.

# Programele:

Am pus in folder-ul 'Programe' mai multe programe in cod RISC-V care verifica in mod practic cele 12 functii din acel site. Fiecare program ilustreaza functionalitatea procedurilor cu numarele din titlu.

In folder-ul Codurile Masina sunt puse fisierele .bin pentru fiecare din cele 12 programe RISC-V + cel pentru tema de laborator. 

# Mentiuni: 
Am folosit codificarea Huffman de pe acest site:  https://reintech.io/blog/python-huffman-coding-problem


