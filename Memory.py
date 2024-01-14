from bitstring import BitArray
hex_dict = {'0': '0000', '1': '0001', '2': '0010', '3': '0011', '4': '0100', '5': '0101', '6': '0110', '7': '0111', '8': '1000', '9': '1001', 'a': '1010', 'b': '1011', 'c': '1100', 'd': '1101', 'e': '1110', 'f': '1111'}

#functia sterge totul din memorie
def reset_memory(file_name):
    f = open(file_name, "wb")
    f.close()

#functia reserva spatiu in memorie, asezand 0 in acei bytes
def reserve_space(file_name, space_in_bytes):
    with open(file_name, 'wb') as f:
        f.write(bytes(space_in_bytes))

#functia pune in adresa indicata de position + offset valoarea din value pe numarul de bytes din nr_bytes
def fill_adress(file_name, position, offset, value, nr_bytes):  
    value_hex = hex(value & (0xFFFFFFFFFFFFFFFF))[2:]
    value_hex = value_hex.zfill(16)            
    value_hex = value_hex[-2*nr_bytes:]
    position = ( position + offset ) * 2
    with open(file_name, 'rb') as f:
        numar=f.read()
    s=''
    for c in numar:
         s+= "{:02x}".format(c)
    s = s[:position] + value_hex + s[position+nr_bytes*2:]
    f = open(file_name, 'wb')
    f.close()
    with open(file_name, 'ab') as f:
        for i in range(0,len(s), 2):
            bs = hex_dict[s[i]] + hex_dict[s[i+1]]
            bs = [int(bs, 2)]
            f.write(bytes(bs))        
    
#functia returneaza sub forma de int valoarea din adresa position + offste, luan doar nr de bytes specificat de nr_bytes
def get_value(file_name, position, offset, nr_bytes):
        with open(file_name, 'rb') as f:
             s=f.read()
        position =  position + offset 
        value_hex=''
        for c in s[position:position+nr_bytes]:
            value_hex+= '{:02x}'.format(c)
        binary_string=''
        for c in value_hex:
            binary_string += hex_dict[c]
        return BitArray(bin=binary_string).int

