import binascii, re, hashlib, random, base64



def l_endian(val):
    """Takes bytes and returns little endian int32/64"""
    l_hex = bytearray(val)
    l_hex.reverse()
    str_l = ''.join(format(i, '02x') for i in l_hex)
    return int(str_l, 16)



def recalc_checksum(file):
    with open (file, 'rb') as fh:
        dat = fh.read()
        slot_ls = []
        slot_len = 2621439
        cs_len = 15
        s_ind = 0x00000310
        c_ind = 0x00000300


        # Build nested list containing data and checksum related to each slot
        for i in range(10):
            d = dat[s_ind: s_ind + slot_len +1] # [ dat[0x00000310:0x0028030F +1], dat[ 0x00000300:0x0000030F + 1] ]
            c = dat[c_ind: c_ind + cs_len + 1]
            slot_ls.append([d,c])
            s_ind += 2621456
            c_ind += 2621456



        # Do comparisons and recalculate checksums
        for ind,i in enumerate(slot_ls):
            new_cs = hashlib.md5(i[0]).hexdigest()
            cur_cs = binascii.hexlify(i[1]).decode('utf-8')

            if new_cs != cur_cs:
                slot_ls[ind][1] = binascii.unhexlify(new_cs)



        slot_len = 2621439
        cs_len = 15
        s_ind = 0x00000310
        c_ind = 0x00000300
        # Insert all checksums into data
        for i in slot_ls:
            dat = dat[:s_ind] + i[0] + dat[s_ind + slot_len +1:]
            dat = dat[:c_ind] + i[1] + dat[c_ind + cs_len + 1:]
            s_ind += 2621456
            c_ind += 2621456


        # Manually doing General checksum
        general = dat[0x019003B0:0x019603AF +1]
        new_cs = hashlib.md5(general).hexdigest()
        cur_cs = binascii.hexlify(dat[0x019003A0:0x019003AF + 1]).decode('utf-8')

        writeval = binascii.unhexlify(new_cs)
        dat = dat[:0x019003A0] + writeval + dat[0x019003AF +1:]




        with open(file, 'wb') as fh1:
            fh1.write(dat)



def replacer(file,slot,name):
    with open(file, "rb") as fh:
        dat1 = fh.read()
        id_loc = []
        index = 0

        while index < len(dat1):
            index = dat1.find(slot.rstrip(b'\x00'), index)

            if index == -1:
                break
            id_loc.append(index)
            if len(id_loc) > 300:
                return 'error'
            index += 8

        nw_nm_bytes = name.encode('utf-16')[2:]

        num = 32 - len(nw_nm_bytes)
        for i in range(num):
            nw_nm_bytes = nw_nm_bytes + b'\x00'

        for i in id_loc:
            fh.seek(0)
            a = fh.read(i)
            b = nw_nm_bytes
            fh.seek(i + 32)
            c = fh.read()
            data = a + b + c

            with open(file, 'wb') as f:
                f.write(data)
    recalc_checksum(file)



def change_name(file,nw_nm,dest_slot):

    empty = b'\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'
    with open(file, 'rb') as fh:
        dat1 = fh.read()


    name_locations = []
    ind1 = 0x1901d0e
    for i in range(10):
        nm = dat1[ind1: ind1 + 32]
        name_locations.append(nm)
        ind1 += 588

    x = replacer(file, name_locations[dest_slot -1], nw_nm )
    return x



def replace_id(file,newid):
    id_loc = []
    index = 0

    with open(file, "rb") as f:
        dat = f.read()
        f.seek(26215348) # start address of steamID
        steam_id = f.read(8) # Get steamID

        id_loc = []
        index = 0
        while index < len(dat):
            index = dat.find(steam_id, index)
            if index == -1:
                break
            id_loc.append(index)
            index += 8

        for i in id_loc:
            f.seek(0)
            a = f.read(i)
            b =  newid.to_bytes(8, 'little')
            f.seek(i + 8)
            c = f.read()
            data = a + b + c

            with open(file, 'wb') as fh:
                fh.write(data)

    recalc_checksum(file)



def copy_save(src_file,dest_file,src_char,dest_char):
    with open (src_file, 'rb') as fh:
        dat = fh.read()
        slot1 = dat[0x00000310:0x0028030F +1] # SLOT 1
        slot2 = dat[0x00280320:0x050031F + 1]
        slot3 = dat[0x500330:0x78032F +1]
        slot4 = dat[0x780340:0xA0033F +1]
        slot5 = dat[0xA00350:0xC8034F +1]
        slot6 = dat[0xC80360:0xF0035F +1]
        slot7 = dat[0xF00370:0x118036F +1]
        slot8 = dat[0x1180380:0x140037F +1]
        slot9 = dat[0x1400390:0x168038F +1]
        slot10 = dat[0x16803A0:0x190039F +1]

    src_slots = [slot1,slot2,slot3,slot4,slot5,slot6,slot7,slot8,slot9,slot10]



    with open(dest_file, "rb") as fh:
        dat1 = fh.read()

    # Listed all offsets for others to see instead of iterating and generating the locations automatically
    slot1_start = dat1[:0x00000310]
    slot1_end = dat1[0x0028030F +1:]

    slot2_start = dat1[:0x00280320]
    slot2_end = dat1[0x050031F + 1:]

    slot3_start = dat1[:0x500330]
    slot3_end = dat1[0x78032F +1:]


    slot4_start = dat1[:0x780340]
    slot4_end = dat1[0xA0033F +1:]

    slot5_start = dat1[:0xA00350]
    slot5_end = dat1[0xC8034F +1:]

    slot6_start = dat1[:0xC80360]
    slot6_end = dat1[0xF0035F +1:]

    slot7_start = dat1[:0xF00370]
    slot7_end = dat1[0x118036F +1:]

    slot8_start = dat1[:0x1180380]
    slot8_end = dat1[0x140037F +1:]

    slot9_start = dat1[:0x1400390]
    slot9_end = dat1[0x168038F +1:]

    slot10_start = dat1[:0x16803A0]
    slot10_end = dat1[0x190039F +1:]

    slot_slices = [ [slot1_start,slot1_end], [slot2_start,slot2_end], [slot3_start,slot3_end],[slot4_start,slot4_end],[slot5_start,slot5_end],[slot6_start,slot6_end],[slot7_start,slot7_end],[slot8_start,slot8_end],[slot9_start,slot9_end],[slot10_start,slot10_end] ]

    dat1 = slot_slices[dest_char -1][0] + src_slots[src_char -1] + slot_slices[dest_char -1][1]


    with open(dest_file, 'wb') as fh:
        fh.write(dat1)
    recalc_checksum(dest_file)



def get_id(file):
    with open(file, "rb") as f:
        dat = f.read()
        f.seek(26215348) # start address of steamID
        steam_id = f.read(8) # Get steamID
    return l_endian(steam_id)



def get_names(file):
    with open(file, "rb") as fh:
        dat1 = fh.read()


    name1 = dat1[0x1901d0e:0x1901d0e + 32].decode('utf-16')
    name2 = dat1[0x1901f5a:0x1901f5a + 32].decode('utf-16')
    name3 = dat1[0x19021a6:0x19021a6 + 32].decode('utf-16')
    name4 = dat1[0x19023f2 :0x19023f2  +32].decode('utf-16')
    name5 = dat1[0x190263e :0x190263e  +32].decode('utf-16')
    name6 = dat1[0x190288a :0x190288a  +32].decode('utf-16')
    name7 = dat1[0x1902ad6 :0x1902ad6  +32].decode('utf-16')
    name8 = dat1[0x1902d22 :0x1902d22  +32].decode('utf-16')
    name9 = dat1[0x1902f6e :0x1902f6e  +32].decode('utf-16')
    name10 = dat1[0x19031ba :0x19031ba  +32].decode('utf-16')


    names = [name1,name2,name3,name4,name5,name6,name7,name8,name9,name10]


    for ind,i in enumerate(names):
        if i == '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00':
            names[ind] = None

    for ind,i in enumerate(names):
        if not i is None:
            names[ind] = i.split('\x00')[0] # name looks like this: 'wete\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

    return names



def random_str():
    """Generates random 16 character long name"""
    val = range(random.randint(900,900000))
    hashed = hashlib.sha1(str(val).encode())
    random_name = base64.urlsafe_b64encode(hashed.digest()[:12])
    return random_name.decode("utf-8")
