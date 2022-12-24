import binascii, re, hashlib, random, base64, os
from allitems_dict import itemdict

def l_endian(val):
    """Takes bytes and returns little endian int32/64"""
    l_hex = bytearray(val)
    l_hex.reverse()
    str_l = "".join(format(i, "02x") for i in l_hex)
    return int(str_l, 16)


def print_vals(file,index):
    with open(file, "rb") as f:
        dat = f.read()
        ind = index
        c1 = dat[0x00000310:0x0028030F +1]
        ls = []
        ind -= (12 * 16)
        for i in range(256):

            ids = f"{l_endian(c1[ind:ind+1])}:{l_endian(c1[ind+1:ind+2])}"
            try:
                name = items[ids]
            except:
                name = "?"
            ls.append({
                          "Name": name,
                          "item_id": [l_endian(c1[ind:ind+1]), l_endian(c1[ind+1:ind+2])],
                          "uid": [l_endian(c1[ind+2:ind+3]),  l_endian(c1[ind+3:ind+4])],
                          "quantity": l_endian(c1[ind+4:ind+5]),
                          "pad1": [l_endian(c1[ind+5:ind+6]),l_endian(c1[ind+6:ind+7]),l_endian(c1[ind+7:ind+8])],
                          "pad2":[ l_endian(c1[ind+9:ind+10]), l_endian(c1[ind+10:ind+11]),l_endian(c1[ind+11:ind+12])],
                          "iter": l_endian(c1[ind+8:ind+9])
                          })
            ind+= 12
#    for i in ls:
#        print(i)



items = dict([(f"{v[0]}:{v[1]}",k) for k,v in itemdict.items()])
print_vals("ER0000.sl2", 65853-4) # 65853 is Index of a KNOWN quantity minus 4 (to start at id1 position)











#with open("items.txt", 'r') as f:
#    lines = f.readlines()

#newls = []
#for line in lines:
#    x = line.replace("'", "")
#    y = '"' + x
#    newls.append(y)

#with open("items_fixed.txt", 'w') as ff:
#    ff.writelines(newls)
