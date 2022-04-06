import binascii, re, hashlib, random, base64

file = 'ER0000.sl2'


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

                            #data                           #hash
        slot_ls.append( [dat[0x00000310:0x0028030F +1], dat[ 0x00000300:0x0000030F + 1]] ) # SLOT 1
        slot_ls.append( [dat[0x00280320:0x050031F + 1], dat[0x00280310:0x0028031F +1]] ) # SLOT 2
        slot_ls.append( [dat[0x500330:0x78032F +1], dat[0x500320:0x50032F +1]] ) # SLOT 3
        slot_ls.append( [dat[0x019003B0:0x019603AF +1], dat[0x019003A0:0x019003AF + 1]] ) # GENERAL


        for ind,i in enumerate(slot_ls):
            new_cs = hashlib.md5(i[0]).hexdigest()
            cur_cs = binascii.hexlify(i[1]).decode('utf-8')

            if new_cs != cur_cs:

                writeval = binascii.unhexlify(new_cs)
                slot_ls[ind][1] = writeval

        dat = dat[:0x00000310] + slot_ls[0][0] + dat[0x0028030F +1:]
        dat = dat[:0x00000300] + slot_ls[0][1] + dat[0x0000030F + 1:]

        dat = dat[:0x00280320] + slot_ls[1][0] + dat[0x050031F + 1:]
        dat = dat[:0x00280310] + slot_ls[1][1] + dat[0x0028031F +1:]

        dat = dat[:0x500330] + slot_ls[2][0] + dat[0x78032F +1:]
        dat = dat[:0x500320] + slot_ls[2][1] + dat[0x50032F +1:]

        dat = dat[:0x019003B0] + slot_ls[3][0] + dat[0x019603AF +1:]
        dat = dat[:0x019003A0] + slot_ls[3][1] + dat[0x019003AF +1:]

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


    if dest_slot == 1:
        s1 = dat1[0x1901d0e:0x1901d0e + 32]
        if s1 == empty:
            return
        replacer(file,s1,nw_nm)

    if dest_slot == 2:
        s1 = dat1[0x1901f5a:0x1901f5a + 32]
        if s1 == empty:
            return
        replacer(file,s1,nw_nm)

    if dest_slot == 3:
        s1 = dat1[0x19021a6:0x19021a6 + 32]
        if s1 == empty:
            return
        replacer(file, s1, nw_nm)



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
        cs11 = dat[ 0x00000300:0x0000030F + 1] # ORIGINAL CHECKSUM slot 1

        slot2 = dat[0x00280320:0x050031F + 1]
        cs22 = dat[0x00280310:0x0028031F +1]

        slot3 = dat[0x500330:0x78032F +1]
        cs33 = dat[0x500320:0x50032F +1]

    src_slots = [slot1,slot2,slot3]
    src_checksums = [cs11,cs22,cs33]


    with open(dest_file, "rb") as fh:
        dat1 = fh.read()

        destslot1 = dat1[0x00000310:0x0028030F +1] # SLOT 1
        cs1 = dat1[ 0x00000300:0x0000030F + 1] # ORIGINAL CHECKSUM slot 1

        destslot2 = dat1[0x00280320:0x050031F + 1]
        cs2 = dat1[0x00280310:0x0028031F +1]

        destslot3 = dat1[0x500330:0x78032F +1]
        cs3 = dat1[0x500320:0x50032F +1]

    dest_slots = [destslot1,destslot2,destslot3]
    dest_checksume = [cs1,cs2,cs3]


    slot1_start = dat1[:0x00000310]
    slot1_end = dat1[0x0028030F +1:]

    slot2_start = dat1[:0x00280320]
    slot2_end = dat1[0x050031F + 1:]

    slot3_start = dat1[:0x500330]
    slot3_end = dat1[0x78032F +1:]

    slot_slices = [ [slot1_start,slot1_end], [slot2_start,slot2_end], [slot3_start,slot3_end] ]

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

    names = [name1,name2,name3]


    for ind,i in enumerate(names):
        if i == '\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00':
            names[ind] = None

    for ind,i in enumerate(names):
        if not i is None:
            names[ind] = i.split('\x00')[0] # name will be 'wete\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00'

    return names


def random_str():
    val = range(random.randint(900,900000))
    hashed = hashlib.sha1(str(val).encode())
    random_name = base64.urlsafe_b64encode(hashed.digest()[:12])
    return random_name.decode("utf-8")
