memfile='main_memory_file.bin' # fisierul cu memoria
stack = 'stack_memory_file.bin' # fisierul cu stack ul
bincodefile='machine_code.bin' #fisierul cu codul masina
huffmanfile='Huffman_encoding.in' #fisierul cu codificarea Huffman

regfile = [0 for i in range(32)] #lista cu valoriile registrilor
fregfile = [0 for i in range(32)] #lista cu valoriile floating point ale registriilor
reg_dict = {'ero':0,'zero':0, 'ra':1, 'sp':2, 'gp':3, 'tp':4, 't0':5,'t1':6,'t2':7, 's0':8, 's1':9, 'a0':10, 'a1':11,'a2':12,'a3':13, 'a4':14, 'a5':15, 'a6':16, 'a7':17, 's2':18, 's3':19, 's4':20, 's5':21, 's6':22, 's7':23, 's8':24, 's9':25, 's10':26, 's11':27, 't3':28, 't4':29, 't5':30, 't6':31}
#^dictionar prin intermediul caruia putem accesa cu usurinta codificarea unui registru dupa numele acestuia
regcode=['{:05b}'.format(i) for i in range(32)]#lista cu codificarea registrilor, cate 5 biti per registru
regdecode={regcode[reg_dict[key]]:key for key in reg_dict.keys()} #dictionar pentru decodificarea registrilor
datatype_decode={"00":'.asciz', '01':'.space'} #dict pentru decodificarea tipului de date
variabile={} #dictionar cu variabile si adresa lor de memorie
decodif = {}
et={} #dictionar cu etichete si adresa lor in program

with open(huffmanfile) as f:
    for line in f.readlines():
        line=line.split()
        decodif[line[1]]=line[0]
#decodif este dictionarul cu decodificarea Huffman

#-----------BIBLIOTECIILE FOLOSITE--------

from bitstring import BitArray
import re
import math
import struct
from parse import parse
import Memory

# --------FUNCTIILE FOLOSITE-------

def printf(string):
    arg = 11
    newline = chr(92)+chr(110)
    string=string.replace(newline, chr(10))
    string=re.split(" ", string)
    for j in range(len(string)):
        while '%' in string[j]:
            i=0
            aux=string[j]
            while i < len(string[j]):
                if string[j][i] == '%':
                    if string[j][i+1] =='d':
                        val = regfile[arg]
                        aux = aux.replace('%d',str(val), 1)
                        i+=1
                        arg+=1
                    elif string[j][i+1] == 'f':
                        val = regfile[arg]
                        aux = aux.replace('%f', "{:.2f}".format(convert_to_float(val, 's')), 1)
                        i+=1
                        arg+=1
                    elif string[j][i+1] == 'c':
                        aux = aux.replace('%c', chr(regfile[arg]), 1)
                        i+=1
                        arg+=1
                    elif string[j][i+1] == 's':
                        string_to_write = get_str_from_memory(regfile[arg])
                        aux = aux.replace('%s', string_to_write, 1)
                        i+=1
                        arg+=1 
                i+=1
            string[j]=aux
    print(" ".join(string), end='')
                    
def scanf(string):
    arg = 11
    newline = chr(92) + chr(110)
    string = string.replace(newline, chr(10))
    string = string.split('\n')
    for line in string:
        to_read = input()
        line=line.replace('%f', '{:f}')
        line = line.replace('%d', '{:d}')
        line = line.replace('%c', '{}')
        line = line.replace('%s', '{}')
        arg_list = parse(line, to_read)
        for x in arg_list:
            if type(x) == int:
                if regfile[arg] >=0:
                    Memory.fill_adress(memfile, regfile[arg], 0, x, 4)
                else:
                    Memory.fill_adress(stack, 4096 + regfile[arg], 0, x, 4)
            elif type(x) == float:
                x = float_to_int(x, 's')
                x = BitArray(bin=x).int
                if regfile[arg] >=0:
                    Memory.fill_adress(memfile, regfile[arg], 0, x, 4)
                else:
                    Memory.fill_adress(stack, 4096 + regfile[arg], 0, x, 4)
            elif type(x) == chr:
                if regfile[arg] >=0:
                    Memory.fill_adress(memfile, regfile[arg], 0, ord(x), 1)
                else:
                    Memory.fill_adress(stack, 4096+ regfile[arg], 0, ord(x), 1)
            else:
                adress = regfile[arg]
                for j in range(len(x)):
                    if adress >=0:
                        Memory.fill_adress(memfile, adress, j, ord(x[j]), 1)
                    else:
                        Memory.fill_adress(stack, 4096 + adress, j, ord(x[j]), 1)
                if adress >= 0:
                    Memory.fill_adress(memfile, adress, len(x), 0, 1)
                else:
                    Memory.fill_adress(memfile,4096 + adress, j, ord(x[j]), 1)
            arg+=1

#functia declarata de ei in c
def cfunc(a, b, c):
    return a+b*c

#functie care preia un numar, reg, si il converteste in float , format IEE 754 ( returneaza numarul )
#in programl folosim doar single-precision
def convert_to_float(reg, precision):
    if precision =='s':
        reg = reg & 0xFFFFFFFF
        x='{:032b}'.format(reg)
        n = 23
        mantisa = x[9:]
        exponent = x[1:9]
        sign = x[0]
    else:
        reg = reg & 0xFFFFFFFFFFFFFFFF
        x='{:064b}'.format(reg)
        n = 52
        mantisa = x[12:]
        exponent = x[1:12]
        sign = x[0]
    mnumber = 0 
    for i in range(n):
        if mantisa[i] == '1':
            mnumber += 2**(-i-1)
    if sign == '0':
        sign = 1
    else :
        sign = -1

    if '1' not in exponent:
        if precision == 's':
            exponent = -126
        else:
            exponent = -1022 
    else:
        if precision == 's':
            exponent = int(exponent, 2)-127
        if precision == 'd':
            exponent = int(exponent, 2) - 1023
        mnumber+=1
    return sign * (2**exponent) * mnumber

#ia un float si returneaza string ul pentru int 
def float_to_int(reg, precision):
    if precision == 's':
        b=struct.pack('!f',reg)
    else:
        b=struct.pack('!d',reg)
    return ''.join(format(c, '08b') for c in b)

#functie care decodifica un string cu lungimea pe 12 biti, returneaza in ordinea aceasta: string-ul si pozitia la care suntem in decodificare dupa ce am citit string-ul
def get_12b_string(start):
    length=program[start:start+12]
    start+=12
    sir=''
    length=BitArray(bin=length).int
    for m in range(length):
        letter=program[start:start+8]
        letter=BitArray(bin=letter).int
        sir+=chr(letter)
        start+=8
    return sir, start

#decodifica un string, stiindu-i lungimea.
#ca functia precedenta returneaza string-ul si pozitia la care am ramas
def get_string(start, length):
    sir=''
    for m in range(length):
        letter=program[start:start+8]
        letter=BitArray(bin=letter).int
        sir+=chr(letter)
        start+=8
    return sir, start

#decodifica urmatoarea instructiune huffman, returnand pozitia la care se termina ( practic instr = program[beg:end])
def get_instr(beg): 
    end=beg
    while end<len(program) and program[beg:end] not in decodif.keys():
        end+=1
    return end

#functie strlen, calculeaza lungimea unui string care incepe la adresa poz, returneaza lungimea
def strlen(poz):
    length=0
    char = Memory.get_value(memfile, poz, 0, 1)
    while char != 0:
        length+=1
        char = Memory.get_value(memfile, poz+length, 0, 1)
    return length

#functia preia un string din memorie sau stack, returneaza string-ul
def get_str_from_memory(adress):
    if adress >= 0:
        string = ''
        c = Memory.get_value(memfile, adress, 0, 1)
        while(c!=0):
            string += chr(c)
            adress +=1
            c = Memory.get_value(memfile, adress, 0, 1)
    else:
        string = ''
        c = Memory.get_value(stack, 4096+adress, 0, 1)
        while c!=0 :
            string += chr(c)
            adress += 1
            if adress <0:
                c = Memory.get_value(stack, 4096+adress, 0, 1)
            else: c = 0
    return string


#functia get_et trece prin tot program si sare peste orice nu este eticheta. Cand da peste o eticheta o pune in dictionarul cu etichete
#de exemplu: daca 1 apare ca eticheta de trei ori in program, pozitia lor in codul masina fiind poz1 < poz2 < poz3 , atunci et['1'] = [poz1, poz2, poz3]  
#aceasta este functia care ocupa mult timp ( pana sa inceapa efectiv rularea programului )
def get_et(i):  
    while True:
        j = get_instr(i)
        if i==j:
            return 
        instr = decodif[program[i:j]]
        if instr !='eticheta': # totimpul cand faceom o instructiune trb bagata si aici pt a stii cat sarim
            if instr == 'li':
                i=j+5 # sar peste registru
                i=i+32
            elif instr == 'j':
                i=j
                length=BitArray(bin=program[i:i+12]).int
                i+=12
                i= i + 8 * length
            elif instr == 'addi':
                i=j
                i+=10 # sar peste cei 2 registrii
                i+=32 # sar peste constanta
            elif instr == 'call':
                i=j
                length=BitArray(bin=program[i:i+12]).int
                i+=12
                i= i + 8 * length
            elif instr in ['beqz', 'bnez']:
                i=j
                i=i+5 # registru
                length=BitArray(bin=program[i:i+12]).int
                i+=12
                i= i + 8 * length
            elif instr in ['bge', 'ble', 'bgt']:
                i=j
                i+=5
                i+=5
                length=BitArray(bin=program[i:i+12]).int
                i+=12
                i= i + 8 * length
            elif instr in ['add', 'sub', 'fadd.d', 'fsub.d', 'fmul.d', 'fgt.s', 'flt.s', 'fmul.s', 'fadd.s']:
                i=j
                i=i+5+5+5
            elif instr in ['lb', 'lw', 'sd', 'sb', 'ld', 'fld', 'fsw', 'flw', 'sw']:
                i=j+5
                i+=(12+5)
            elif instr in ['mv', 'fsqrt.d', 'fmv.s', 'fmv.s.x']:
                i=j
                i+=10
            elif instr in ['srai', 'slli']: 
                i=j
                i+=15 
            elif instr == 'la':
                i=j
                i+=5
                length=BitArray(bin=program[i:i+12]).int
                i+=12
                i = i + 8*length
            elif instr == 'ret':
                i=j
        else:
            i=j
            sir, i = get_12b_string(i)
            if sir in et.keys():
                et[sir].append(i)
            else:
                et[sir]=[i]


#mai intai stergem memoria si stack-ul apoi "rezervam" 4096 de bytes de memorie punand 0 peste tot
Memory.reset_memory(memfile) 
Memory.reset_memory(stack)
Memory.reserve_space(stack, 4096)
Memory.reserve_space(memfile, 4096)
memory_pointer=0 # ne spune pe ce pozitie in memorie se afla variabilele

#-----------INCEPEM CITIREA PROGRAMULUI-----------

#citim programul si il transformam in string cu 1 si 0
with open(bincodefile, 'rb') as f:
    binstring = ''
    for c in f.read():
        binstring+='{:08b}'.format(c)

regfile[reg_dict['gp']]=i=0 #global pointer

bytes_filled = BitArray(bin=binstring[0:8]).int
i+=8
continue_read_data = binstring[i] # cat timp acest bit e 1 mai avem date de citit
i+=1

#-----INCEPEM CITIREA VARIABILELOR DECLARATE------

while continue_read_data == '1': 
    length = binstring[i:i+12]
    length = BitArray(bin=length).int
    i += 12
    name = ''
    for j in range(length):
        char = binstring[i:i+8]
        char = BitArray(bin=char).int
        name += chr(char)
        i+=8
    # luam primu string = numele variabilelei
    variabile[name] = memory_pointer # poz la care incepem sa completam
    if datatype_decode[binstring[i:i+2]] == ".asciz":
        i+=2
        length2 = binstring[i:i+12]
        length2 = BitArray(bin=length2).int
        i += 12
        content = ''
        for j in range(length2):
            char = binstring[i:i+8]
            char = BitArray(bin=char).int
            content += chr(char)
            Memory.fill_adress(memfile, memory_pointer, 0, char, 1) #punem in memorie byte ul caracterului
            memory_pointer += 1 # crestem memory pointer ul
            i += 8
        memory_pointer+=1 # mai crestem odata pt terminatorul de sir ( stim ca in memorie avem automat 0)
    elif datatype_decode[binstring[i:i+2]] == ".space":
        i+=2
        bytes_to_reserve = BitArray(bin = binstring[i:i+12]).int
        i+=12
        for j in range(bytes_to_reserve):
            Memory.fill_adress(memfile, memory_pointer, 0, 0, 1) 
            memory_pointer+=1
    continue_read_data=binstring[i:i+1] 
    i+=1
    regfile[reg_dict['gp']] = i


i+=bytes_filled # sarim peste acei bytes de 0 pusi pentru a fi multiplu de 8


#--------INCEPEM CITIREA PROGRAMULUI-------------

bytes_filled = BitArray(bin=binstring[i:i+8]).int
i+=8
program=binstring[i:len(binstring)-bytes_filled] 
main, i = get_12b_string(0) # main este eticheta programului principal
get_et(i) # mai intai parcurgem tot programul si tinem minte etichetele intr-o variabila
nr_of_jumps = 0 # contor pentru a sti la ce ret trebuie sa ne oprim


regfile[reg_dict['gp']] = i = et[main][0] #incepem de la programul principal
regfile[reg_dict['ra']] = 0
while regfile[reg_dict['gp']] < len(program):
    j=get_instr(regfile[reg_dict['gp']])
    instr = decodif[program[i:j]] 
    #instr = instructiunea la care suntem si decodificam programul
    if instr == 'li':
        i=j
        reg_code=program[i:i+5]
        i=i+5
        constant=program[i:i+32]
        regfile[reg_dict[regdecode[reg_code]]]=BitArray(bin=constant).int
        i=i+32
    elif instr == 'eticheta':
        i=j
        length = BitArray(bin = program[i:i+12]).int
        i+=12
        i = i + 8 * length
    elif instr == 'j':
        i=j
        sir, i = get_12b_string(i)
        if sir[-1]=='f': # daca sarim in fata cautam prima poz mai mare decat poz curenta din dictionarul etichetei noastre
            for x in et[sir[0:len(sir)-1]]:
                if x>i:
                    break
            i=x
        else:# daca sarim in spate cautam prima poz mai mica decat poz curenta din dictionaru etichetei noastre
            found = 0
            for x in range(len(et[sir[0:len(sir)-1]])): # pentru fiecare element din et[eticheta], daca e mai mare decat pozitia noastra(i), am gasit ce cautam si iesim din for
                if et[sir[0:len(sir)-1]][x] > i:
                    found = 1
                    break
            if found == 1:
                i = et[sir[0:len(sir)-1]][x-1] # ultima pozitie citita
            else:
                i = et[sir[0:len(sir)-1]][-1] # daca nu am gasit atunci toate sunt mai mici deci ultima etichet din dictionar e cea potrivita
    #la toate instructiunile cu branch e la fel ca la jump
    elif instr == 'beqz':
        i=j
        reg_code=program[i:i+5]
        i+=5
        reg_value=regfile[reg_dict[regdecode[reg_code]]]
        length = BitArray(bin=program[i:i+12]).int
        i+=12
        if reg_value != 0:
            i = i + 8 * length
        else:
            sir, i = get_string(i, length)
            if sir[-1]=='f':
                for x in et[sir[0:len(sir)-1]]:
                    if x>i:
                        break
                i=x
            else:
                found = 0
                for x in range(len(et[sir[0:len(sir)-1]])):
                    if et[sir[0:len(sir)-1]][x] > i:
                        found = 1
                        break
                if found == 1:
                    i = et[sir[0:len(sir)-1]][x-1]
                else:
                    i = et[sir[0:len(sir)-1]][-1]  
    elif instr == 'bnez':
        i=j
        reg_code=program[i:i+5]
        i+=5
        reg_value=regfile[reg_dict[regdecode[reg_code]]]
        length = BitArray(bin=program[i:i+12]).int
        i+=12
        if reg_value == 0:
            i = i + 8 * length
        else:
            sir, i = get_string(i, length)
            if sir[-1]=='f':
                for x in et[sir[0:len(sir)-1]]:
                    if x>i:
                        break
                i=x
            else:
                found = 0
                for x in range(len(et[sir[0:len(sir)-1]])):
                    if et[sir[0:len(sir)-1]][x] > i:
                        found = 1
                        break
                if found == 1:
                    i = et[sir[0:len(sir)-1]][x-1]
                else:
                    i = et[sir[0:len(sir)-1]][-1]
    elif instr == 'bge':
        i=j
        reg1=regfile[reg_dict[regdecode[program[i:i+5]]]]
        i+=5
        reg2=regfile[reg_dict[regdecode[program[i:i+5]]]]
        i+=5
        length = BitArray(bin=program[i:i+12]).int
        i+=12
        if reg2 > reg1:
            i = i + 8 * length
        else:
            sir, i = get_string(i, length)
            if sir[-1]=='f':
                for x in et[sir[0:len(sir)-1]]:
                    if x>i:
                        break
                i=x
            else:
                found = 0
                for x in range(len(et[sir[0:len(sir)-1]])):
                    if et[sir[0:len(sir)-1]][x] > i:
                        found = 1
                        break
                if found == 1:
                    i = et[sir[0:len(sir)-1]][x-1]
                else:
                    i = et[sir[0:len(sir)-1]][-1]
    elif instr == 'bgt':
        i=j
        reg1=regfile[reg_dict[regdecode[program[i:i+5]]]]
        i+=5
        reg2=regfile[reg_dict[regdecode[program[i:i+5]]]]
        i+=5
        length = BitArray(bin=program[i:i+12]).int
        i+=12
        if reg2 >= reg1:
            i = i + 8 * length
        else:
            sir, i = get_string(i, length)
            if sir[-1]=='f':
                for x in et[sir[0:len(sir)-1]]:
                    if x>i:
                        break
                i=x
            else:
                found = 0
                for x in range(len(et[sir[0:len(sir)-1]])):
                    if et[sir[0:len(sir)-1]][x] > i:
                        found = 1
                        break
                if found == 1:
                    i = et[sir[0:len(sir)-1]][x-1]
                else:
                    i = et[sir[0:len(sir)-1]][-1]
    elif instr == 'ble':
        i=j
        reg1=regfile[reg_dict[regdecode[program[i:i+5]]]]
        i+=5
        reg2=regfile[reg_dict[regdecode[program[i:i+5]]]]
        i+=5
        length = BitArray(bin=program[i:i+12]).int
        i+=12
        if reg2 < reg1:
            i = i + 8 * length
        else:
            sir, i = get_string(i, length)
            if sir[-1]=='f':
                for x in et[sir[0:len(sir)-1]]:
                    if  x>i:
                        break
                i=x
            else:
                found = 0
                for x in range(len(et[sir[0:len(sir)-1]])):
                    if et[sir[0:len(sir)-1]][x] > i:
                        found = 1
                        break
                if found == 1:
                    i = et[sir[0:len(sir)-1]][x-1]
                else:
                    i = et[sir[0:len(sir)-1]][-1]
    elif instr == 'addi':
        i=j
        reg1=reg_dict[regdecode[program[i:i+5]]]
        i+=5
        reg2=reg_dict[regdecode[program[i:i+5]]]
        i+=5
        const=BitArray(bin=program[i:i+32]).int
        i+=32
        regfile[reg1]=regfile[reg2]+const
    elif instr == 'call':
        i=j
        sir, i = get_12b_string(i)
        if sir == 'strlen' and 'strlen' not in et.keys(): 
            regfile[reg_dict['a0']] = strlen(regfile[reg_dict['a0']]) 
        elif sir == 'scanf':
            scanf(get_str_from_memory(regfile[reg_dict['a0']]))
        elif sir == 'pls':
            print(regfile)
        elif sir =='printf':
           printf(get_str_from_memory(regfile[reg_dict['a0']]))
        elif sir == 'cfunc':
            regfile[reg_dict['a0']]=cfunc(regfile[reg_dict['a0']],regfile[reg_dict['a1']],regfile[reg_dict['a2']])
        else:
            #daca ajunge aici e o eticheta de a noastra
            regfile[reg_dict['ra']] = i # tinem minte pozitia la care sa ne intoarcem in ra
            i = et[sir][0] # i devine pozitia la care sarim
            nr_of_jumps += 1 # pt fiecare call incrementam in variabila aceasta
    elif instr == 'lb':
        i=j
        reg=regdecode[program[i:i+5]]
        i+=5
        offset = BitArray(bin=program[i:i+12]).int
        i+=12
        registru = regdecode[program[i:i+5]]
        i+=5
        if regfile[reg_dict[registru]] >=0:
            pos = regfile[reg_dict[registru]]
            value = Memory.get_value(memfile, pos, offset, 1)
            regfile[reg_dict[reg]] = value
        else:
          stack_position = 4096+regfile[reg_dict[registru]]
          value = Memory.get_value(stack, stack_position, offset, 1) 
          regfile[reg_dict[reg]] = value 
    elif instr == 'lw':
        i=j
        reg=regdecode[program[i:i+5]]
        i=i+5
        offset = BitArray(bin=program[i:i+12]).int
        i+=12
        registru = regdecode[program[i:i+5]]
        i+=5
        if regfile[reg_dict[registru]] >=0:
            pos=regfile[reg_dict[registru]]
            value = Memory.get_value(memfile, pos, offset, 4)
            regfile[reg_dict[reg]] = value
        else:
          stack_position = 4096 +regfile[reg_dict[registru]]
          value = Memory.get_value(stack, stack_position, offset, 4)  
          regfile[reg_dict[reg]] = value
    elif instr == 'ld':
        i=j
        reg=regdecode[program[i:i+5]]
        i=i+5
        offset = BitArray(bin=program[i:i+12]).int
        i+=12
        registru = regdecode[program[i:i+5]]
        i+=5
        if regfile[reg_dict[registru]] >=0:
            pos=regfile[reg_dict[registru]]
            value = Memory.get_value(memfile, pos, offset, 8)
            regfile[reg_dict[reg]] = value
        else:
          stack_position = 4096+regfile[reg_dict[registru]]
          value = Memory.get_value(stack, stack_position, offset, 8)  
          regfile[reg_dict[reg]] = value
    elif instr == 'add':
        i=j
        reg1=reg_dict[regdecode[program[i:i+5]]]
        i+=5
        reg2=reg_dict[regdecode[program[i:i+5]]]
        i+=5
        reg3=reg_dict[regdecode[program[i:i+5]]]
        i+=5
        regfile[reg1]=regfile[reg2]+regfile[reg3]
    elif instr == 'mv':
        i=j
        reg1=reg_dict[regdecode[program[i:i+5]]]
        i+=5
        reg2=reg_dict[regdecode[program[i:i+5]]]
        i+=5
        regfile[reg1]=regfile[reg2]
    elif instr == 'ret':    
        if nr_of_jumps == 0:# daca am iesit din fiecare call intrat inseamna ca suntem in main deci cand dam de ret se termina programul
            i = len(program)
        else: # altfel, sarim la adresa din ra ( return adress ) si decrementam nr_of_jumps pentru ca am terminat cu un call
            i = regfile[reg_dict['ra']]  
            nr_of_jumps -=1
    elif instr == 'sb':
        i=j
        reg=regdecode[program[i:i+5]]
        value = regfile[reg_dict[reg]]
        i+=5
        offset = BitArray(bin=program[i:i+12]).int
        i+=12
        registru = regdecode[program[i:i+5]]
        i+=5
        if regfile[reg_dict[registru]]>=0:
            pos = regfile[reg_dict[registru]]
            Memory.fill_adress(memfile, pos, offset, value, 1)
        else:
            stack_position = 4096+regfile[reg_dict[registru]]
            Memory.fill_adress(stack, stack_position, offset, value, 1)
    elif instr == 'sd':
        i=j
        reg=regdecode[program[i:i+5]]
        value = regfile[reg_dict[reg]]
        i+=5
        offset = BitArray(bin=program[i:i+12]).int
        i+=12
        registru = regdecode[program[i:i+5]]
        i+=5
        if regfile[reg_dict[registru]] >= 0:
            pos = regfile[reg_dict[registru]]
            Memory.fill_adress(memfile, pos, offset, value, 8)
        else :
            stack_position = 4096+regfile[reg_dict[registru]]
            Memory.fill_adress(stack, stack_position, offset, value, 8)
    elif instr == 'sw':
        i=j
        reg=regdecode[program[i:i+5]]
        value = regfile[reg_dict[reg]]
        i+=5
        offset = BitArray(bin=program[i:i+12]).int
        i+=12
        registru = regdecode[program[i:i+5]]
        i+=5
        if regfile[reg_dict[registru]] >= 0:
            pos = regfile[reg_dict[registru]]
            Memory.fill_adress(memfile, pos, offset, value, 4)
        else :
            stack_position = 4096+regfile[reg_dict[registru]]
            Memory.fill_adress(stack, stack_position, offset, value, 4)
    elif instr == 'srai':
        i=j
        reg1=reg_dict[regdecode[program[i:i+5]]]
        i+=5
        reg2=reg_dict[regdecode[program[i:i+5]]]
        i+=5
        const=program[i:i+5]
        i+=5
        const=int(const, 2)
        regfile[reg1]=regfile[reg2] >> const
    elif instr == 'slli':
        i=j
        reg1=reg_dict[regdecode[program[i:i+5]]]
        i+=5
        reg2=reg_dict[regdecode[program[i:i+5]]]
        i+=5
        const=program[i:i+5]
        i+=5
        const=int(const, 2)
        regfile[reg1]=regfile[reg2] << const
    elif instr == 'sub':
        i=j
        reg1=reg_dict[regdecode[program[i:i+5]]]
        i+=5
        reg2=reg_dict[regdecode[program[i:i+5]]]
        i+=5
        reg3=reg_dict[regdecode[program[i:i+5]]]
        i+=5
        regfile[reg1]=regfile[reg2]-regfile[reg3]
    elif instr == 'la':
        i = j
        reg = program[i:i+5]
        i+=5
        sir, i = get_12b_string(i)
        regfile[reg_dict[regdecode[reg]]] = variabile[sir]
    elif instr == 'flw':
        i=j
        reg=regdecode[program[i:i+5]]
        i=i+5
        offset = BitArray(bin=program[i:i+12]).int
        i+=12
        registru = regdecode[program[i:i+5]]
        i+=5
        if regfile[reg_dict[registru]] >=0:
            pos=regfile[reg_dict[registru]]
            value = Memory.get_value(memfile, pos, offset, 4)
            fregfile[reg_dict[reg]] = convert_to_float(value, 's')
        else:
          stack_position = 4096+regfile[reg_dict[registru]]
          value = Memory.get_value(stack, stack_position, offset, 4)  
          fregfile[reg_dict[reg]] = convert_to_float(value, 's')
    elif instr == 'fld':
        i=j
        reg=regdecode[program[i:i+5]]
        i=i+5
        offset = BitArray(bin=program[i:i+12]).int
        i+=12
        registru = regdecode[program[i:i+5]]
        i+=5
        if regfile[reg_dict[registru]] >=0:
            pos=regfile[reg_dict[registru]]
            value = Memory.get_value(memfile, pos, offset, 8)
            fregfile[reg_dict[reg]] = convert_to_float(value, 's')
        else:
          stack_position = 4096+regfile[reg_dict[registru]]
          value = Memory.get_value(stack, stack_position, offset, 8)  
          fregfile[reg_dict[reg]] = convert_to_float(value, 's')
    elif instr == 'fsub.d':
        i=j
        reg1=reg_dict[regdecode[program[i:i+5]]]
        i+=5
        reg2=reg_dict[regdecode[program[i:i+5]]]
        i+=5
        reg3=reg_dict[regdecode[program[i:i+5]]]
        i+=5
        fregfile[reg1]=fregfile[reg2]-fregfile[reg3]
    elif instr == 'fmul.d' or instr == 'fmul.s':
        i=j
        reg1=reg_dict[regdecode[program[i:i+5]]]
        i+=5
        reg2=reg_dict[regdecode[program[i:i+5]]]
        i+=5
        reg3=reg_dict[regdecode[program[i:i+5]]]
        i+=5
        fregfile[reg1]=fregfile[reg2] * fregfile[reg3]
    elif instr == 'fadd.d' or instr == 'fadd.s':
        i=j
        reg1=reg_dict[regdecode[program[i:i+5]]]
        i+=5
        reg2=reg_dict[regdecode[program[i:i+5]]]
        i+=5
        reg3=reg_dict[regdecode[program[i:i+5]]]
        i+=5
        fregfile[reg1]=fregfile[reg2]+fregfile[reg3]
    elif instr == 'fsqrt.d':
        i=j
        reg1=reg_dict[regdecode[program[i:i+5]]]
        i+=5
        reg2=reg_dict[regdecode[program[i:i+5]]]
        i+=5
        fregfile[reg1] = math.sqrt(fregfile[reg2])
    elif instr == 'fmv.s' or instr == 'fmv.s.x':
        i=j
        reg1=reg_dict[regdecode[program[i:i+5]]]
        i+=5
        reg2=reg_dict[regdecode[program[i:i+5]]]
        i+=5
        fregfile[reg1]=fregfile[reg2]
    elif instr == 'flt.s':
        i=j
        reg1=reg_dict[regdecode[program[i:i+5]]]
        i+=5
        reg2=reg_dict[regdecode[program[i:i+5]]]
        i+=5
        reg3=reg_dict[regdecode[program[i:i+5]]]
        i+=5
        if (fregfile[reg2]<fregfile[reg3]) == True:
            regfile[reg1] = 1
        else:
            regfile[reg1] = 0
    elif instr == 'fgt.s':
        i=j
        reg1=reg_dict[regdecode[program[i:i+5]]]
        i+=5
        reg2=reg_dict[regdecode[program[i:i+5]]]
        i+=5
        reg3=reg_dict[regdecode[program[i:i+5]]]
        i+=5
        if (fregfile[reg2]>fregfile[reg3]) == True:
            regfile[reg1] = 1
        else:
            regfile[reg1] = 0
    elif instr == 'fsw':
        i=j
        reg=regdecode[program[i:i+5]]
        value = fregfile[reg_dict[reg]]
        i+=5
        offset = BitArray(bin=program[i:i+12]).int
        i+=12
        registru = regdecode[program[i:i+5]]
        i+=5
        value = float_to_int(value, 's')
        value = BitArray(bin=value).int
        if regfile[reg_dict[registru]] >= 0:
            pos = regfile[reg_dict[registru]]
            Memory.fill_adress(memfile, pos, offset, value, 4)
        else :
            stack_position = 4096+regfile[reg_dict[registru]]
            Memory.fill_adress(stack, stack_position, offset, value, 4)
    regfile[reg_dict['gp']]=i # am terminat cu o instructiune si mergem la urmatoarea

