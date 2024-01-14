code_file='instr_file.in' # fisierul din care citeste codul riscv
Huffman_coding='Huffman_encoding.in' #fisierul in care pune codificarea

#acest cod face codificarea huffman si dupa o scrie in fisierul ex.in


def clear_code(s): # functia sterge din cod virgulele si comentariile
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
                    lindex      
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


freq={'eticheta':0}


with open(code_file) as f:
    s=f.readlines()
clear_code(s)

data_decl=False # variabila folosita pt a verifica daca e variabila declarata sau nu

for line in s: # acest for memoreaza intr un dictionar functiile ( si etichetele toate sub numele 'eticheta')
    if '.rodata' in line:
        data_decl=True
    if '.text' in line:
        data_decl=False
    if '.section' not in line and '.global' not in line and ':' not in line: # daca nu e eticheta sau declararea unei variabile, merita mmemorata doar prima instr din linie
        line=line.split()
        if line != []: 
            if line[0] in freq.keys():
                freq[line[0]]+=1
            else:
                freq[line[0]]=1
    if data_decl == False:
        if ':' in line: # daca totusi nu e variabila ( data_decl = false) si e eticheta, adaugam la 'eticheta
            line=line.split()
            freq['eticheta']+=1




huffman_code=[[freq[key], [key, ""]] for key in freq.keys() ]  # codu de pe net, se obs mai usor cu desen ce face, pot explica eu candva daca e cv ciudat ca in scris nu prea stiu cum 

import heapq

heapq.heapify(huffman_code) # transforma vectorul in heap :))))


while(len(huffman_code)>1):
    x=heapq.heappop(huffman_code)
    y=heapq.heappop(huffman_code)
    for pair in x[1:]:
        pair[1]='0'+pair[1]
    for pair in y[1:]:
        pair[1]='1'+pair[1]
    heapq.heappush(huffman_code, [x[0]+y[0]] + x[1:] + y[1:])

code={}
for x in huffman_code[0][1:]:
    code[x[0]]=x[1]

def cheie(x):
    return len(code[x])


f=open(Huffman_coding, 'w')
f.write('')
f.close()
f=open(Huffman_coding, 'a')

for key in sorted(code, key=cheie):
    print(key, code[key], file=f)

f.close()
