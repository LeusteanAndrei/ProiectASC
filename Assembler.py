input_file='program.in' #fisierul cu codul RISC-V
machine_code='machine_code.bin' #fisierul in care scrie codul binar
Huffman_coding="Huffman_encoding.in" #fisierul cu codificare huffman
code={}#dictionar cu codificarea Huffman
regcode=['{:05b}'.format(i) for i in range(32)] #lista cu codificarea registrilor, cate 5 biti per registru
reg_dict = {'ero':0,'zero':0, 'ra':1, 'sp':2, 'gp':3, 'tp':4, 't0':5,'t1':6,'t2':7, 's0':8, 's1':9, 'a0':10, 'a1':11,'a2':12,'a3':13, 'a4':14, 'a5':15, 'a6':16, 'a7':17, 's2':18, 's3':19, 's4':20, 's5':21, 's6':22, 's7':23, 's8':24, 's9':25, 's10':26, 's11':27, 't3':28, 't4':29, 't5':30, 't6':31} 
#^dictionar prin intermediul caruia putem accesa cu usurinta codificarea unui registru dupa numele acestuia
datatype_code={".asciz":'00', ".space": '01'} #codificarea pentru tipurile de date.

def clear_code(s): #functia sterge din cod virgulele si comentariile
    for j  in range(len(s)):
        s[j]=s[j].strip()
        comment=False
        lindex=rindex=-1
        for i in range(len(s[j])):
            if s[j][i]=='#':
                if lindex ==-1 or rindex !=-1:
                    comment=True
                    index=i
            if  s[j][i]=='"':
                if lindex==-1:
                    lindex=i
                else:
                    rindex=i
                if lindex > rindex:
                    rindex=-1
            if s[j][i]==',':
                if lindex ==-1 or rindex !=-1:
                    mystring=list(s[j])
                    mystring[i]=" "
                    s[j]="".join(mystring)
        if comment==True:
            s[j] = s[j][0:index].strip()


f=open(Huffman_coding)
s=f.readlines()

#memoram acum codificarea huffman in dictionarul code
for line in s:
    line=line.split()
    code[line[0]]=line[1]

with open(input_file) as f:
    s=f.readlines()

clear_code(s)
rdata = '' # acesta va contine sirul de biti din sectiunea .rodata
program = ''# iar acesta efectiv programul

data_read=False # variabila care verifica daca suntem in sectiunea .rodata

nume_variabile=[] # aici tinem minte numele variabilelor declarate

import struct

#functia urmatoare preia o constanta sub forma unui sir ( ct = '3.05') si o tranforma in sirul binar de afisat(pe 32 de biti), returnandu-l
def constant(ct):
    if '.' in ct:
        ct=float(ct)
        b = struct.pack('!f', abs(ct))
        b=''.join(format(c, '08b') for c in b)
        if ct < 0: 
            b = '1'+b[1:]
        else:
            b= '0' +b[1:]
        return b
    else:
        ct=int(ct)
        if ct >=0:
            return "{:032b}".format(ct)
        else:
            return bin(ct & 0b11111111111111111111111111111111)[2:]


#functia urmatoare scrie automat string urile astfel: lungimea(pe12biti) + fiecare caracter pe 8 biti 
def write_string(string):
    global program
    length=len(string)
    program += "{:012b}".format(length)
    for i in range(length):
        program += "{:08b}".format(ord(string[i]))


# functia urmatoare scrie automat elementele de tip constant(registru) in fel urmator constanta(pe12bit)+codif_registru
def write_memory_adress(string):
    global program
    string = string.split('(')
    if string[0] == '':
        program += "{:012b}".format(0)
    elif int(string[0]) >=0:
        program += "{:012b}".format(int(string[0]))
    else:
        program += bin(int(string[0]) & 0b111111111111)[2:]
    program += regcode[reg_dict[string[1][:-1]]]

#trecem acum prin cod linie 
"""
codificarea va fi astfel: instr_arg1_arg2....
in cazul registrilor vom afisa cei 5 biti care ii codifica
in cazul constantelor vom afisa 32 de biti cu functia constant
in cazul variabilelor vom afisa lungimea lor pe 12 biti si apoi fiecare caracter pe 8 biti cu functia write_string
in cazul dereferentierii vom afisa constanta pe 12 biti si apoi registrul pe 5 biti cu functia write_memory_adress

"""    


for line in s:
    if line.split() !=[]:
        if '.rodata' in line:
            data_read=True
        else:
            if ".text" in line:
                data_read=False
                rdata+='0' #afisam 0 pentru a sti ca trebuie sa ne oprim din citit date
            elif ".global" in line:
                line = line.split()
                write_string(line[1])
                #cand vede .global afiseaza eticheta de dupa .global
            else:
                #declararea variabilelor se face sub formatul asta :   nume: .tip "ce contine" si va fi codificata astfel:
                # lungimenume(be 12biti), caracterele(pe 8 biti),tipul, luncontint(daca e cazul, tot pe 12 biti), caracterele("pe 8 biti")
                if data_read==True:
                    rdata+="1" # afisam 1 pentru a sti ca mai avem de citit date astfel incat atunci cand dam peste 0 de oprim
                    line=line.split(':', maxsplit=1) # acm vectoru arate : [nume, '.tip "ce contine"]
                    nume_variabile.append(line[0]) # adaugam numele la vectorul de variabile
                    lun_var=len(line[0])
                    line[1]=line[1].split(maxsplit=1) #umblam acm in ' .tip "ce contine"' si devine ['.tip', '"ce contine"]
                    rdata += "{:012b}".format(lun_var) #introducem lungimea
                    for i in range(lun_var):
                        rdata += "{:08b}".format(ord(line[0][i])) #afisam fiecare caracter al numelui pe 8 biti
                    rdata += datatype_code[line[1][0].strip()]
                    if line[1][0].strip() == '.asciz':
                        lun_var=len(line[1][1])-2 # si la fel afisam ce contine intre " "
                        rdata += "{:012b}".format(lun_var) 
                        for i in range(1, lun_var+1):
                            rdata += "{:08b}".format(ord(line[1][1][i]))
                    elif line[1][0].strip() == '.space':
                        #in cazul .space introducem doar numarul de bytes de rezervat 
                        rdata += "{:012b}".format(int(line[1][1].strip()))            
                else:
                    if ':' in line: # daca e eticheta
                        program += code['eticheta'] 
                        write_string(line[:-1])
                    else:
                        line=line.split()
                        if line[0] == 'li':
                            program += code[line[0]]
                            program += regcode[reg_dict[line[1]]]
                            program += constant(line[2])
                        elif line[0] in ['add', 'sub']:
                            program += code[line[0]]
                            program += regcode[reg_dict[line[1]]]
                            program += regcode[reg_dict[line[2]]]
                            program += regcode[reg_dict[line[3]]]
                        elif line[0] in ['addi']:
                            program += code[line[0]]
                            program += regcode[reg_dict[line[1]]]
                            program += regcode[reg_dict[line[2]]]
                            program += constant(line[3]) 
                        elif line[0] in ['beqz', 'bnez']:
                            program += code[line[0]]
                            program += regcode[reg_dict[line[1]]]
                            write_string(line[2])
                        elif line[0] in ['j', 'call']:
                            program += code[line[0]]
                            write_string(line[1])
                        elif line[0] == 'mv':
                            program += code[line[0]]
                            program += regcode[reg_dict[line[1]]]
                            program += regcode[reg_dict[line[2]]]
                        elif line[0] in ['lb', 'sb', 'sd', 'sw', 'ld', 'lw']:
                            program += code[line[0]]
                            program += regcode[reg_dict[line[1]]]
                            write_memory_adress(line[2])
                        elif line[0] in ['bge', 'ble', 'bgt']:
                            program +=code[line[0]]
                            program += regcode[reg_dict[line[1]]]
                            program += regcode[reg_dict[line[2]]]
                            write_string(line[3])
                        elif line[0] in ['srai', 'slli']:
                            program += code[line[0]]
                            program += regcode[reg_dict[line[1]]]
                            program += regcode[reg_dict[line[2]]]
                            program += "{:05b}".format(int(line[3]))
                        elif line[0] == 'la':
                            program += code[line[0]]
                            program += regcode[reg_dict[line[1]]]
                            write_string(line[2])
                        elif line[0] == 'ret':
                            program += code[line[0]]
                        elif line[0] in ['fmv.s', 'fmv.s.x']:
                            program += code[line[0]]
                            program += regcode[reg_dict[line[1][1:]]]
                            program += regcode[reg_dict[line[2][1:]]]
                        elif line[0] in ['fld', 'fsw', 'flw']:
                            program += code[line[0]]
                            program += regcode[reg_dict[line[1][1:]]]
                            write_memory_adress(line[2])
                        elif line[0] in ['fsub.d', 'fmul.d', 'fadd.d', 'fmul.s', 'fadd.s']:
                            program += code[line[0]]
                            program += regcode[reg_dict[line[1][1:]]]
                            program += regcode[reg_dict[line[2][1:]]]
                            program += regcode[reg_dict[line[3][1:]]]
                        elif line[0] == 'fsqrt.d':
                            program += code[line[0]]
                            program +=regcode[reg_dict[line[1][1:]]]
                            program += regcode[reg_dict[line[2][1:]]]
                        elif line[0] in ['fgt.s', 'flt.s']:
                            program += code[line[0]]
                            program += regcode[reg_dict[line[1]]]
                            program += regcode[reg_dict[line[2][1:]]]
                            program += regcode[reg_dict[line[3][1:]]]



#golim fisierul cu codul masina
f = open(machine_code, 'wb')
f.close()

f=open(machine_code, 'ab')
n = len(rdata) 
m = len(program)
#n si m trebuie sa fie multiplii de 8 asa ca, mai intai, pentru rdata si rprogram vom scrie cati biti de 0  aduagam pentru a nu ii lua in calcul
f.write(bytes([(8-n%8)%8])) 
rdata = rdata + '0'*((8-n%8)%8) # adaugam acei biti de 0
#afisam rdata
for i in range(0, len(rdata), 8):
    f.write(bytes([int(rdata[i:i+8], 2)]))

#afisam in mod analog programul
f.write(bytes([(8-m%8)%8]))
program = program + '0'*((8-m%8)%8)
for i in range(0, len(program), 8):
    f.write(bytes([int(program[i:i+8], 2)]))


f.close()




