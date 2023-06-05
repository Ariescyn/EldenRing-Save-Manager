import binascii, re, hashlib, random, base64, stat_progression, itemdata, os, allitems_dict
from allitems_dict import itemdict

def l_endian(val):
    """
    Takes bytes and returns little endian int32/64.

    Args:
        val: Bytes representing the integer value.

    Returns:
        int: Little endian integer value converted from the input bytes.

    Raises:
        None.
    """
    l_hex = bytearray(val)  # Convert bytes to a bytearray
    l_hex.reverse()  # Reverse the order of bytes to represent little endian
    str_l = "".join(format(i, "02x") for i in l_hex)  # Convert bytearray to hex string
    return int(str_l, 16)  # Convert hex string to integer using base 16 (hexadecimal)



def recalc_checksum(file):
    """
    Recalculates and updates checksum values in a binary file.

    Args:
        file (str): The path to the binary file.

    Returns:
        None.

    Raises:
        None.
    """
    with open(file, "rb") as fh:
        dat = fh.read()
        slot_ls = []
        slot_len = 2621439
        cs_len = 15
        s_ind = 0x00000310
        c_ind = 0x00000300

        # Build nested list containing data and checksum related to each slot
        for i in range(10):
            d = dat[s_ind : s_ind + slot_len + 1]  # Extract data for the slot
            c = dat[c_ind : c_ind + cs_len + 1]  # Extract checksum for the slot
            slot_ls.append([d, c])  # Append the data and checksum to the slot list
            s_ind += 2621456  # Increment the slot data index
            c_ind += 2621456  # Increment the checksum index

        # Do comparisons and recalculate checksums
        for ind, i in enumerate(slot_ls):
            new_cs = hashlib.md5(i[0]).hexdigest()  # Recalculate the checksum for the data
            cur_cs = binascii.hexlify(i[1]).decode("utf-8")  # Convert the current checksum to a string

            if new_cs != cur_cs:  # Compare the recalculated and current checksums
                slot_ls[ind][1] = binascii.unhexlify(new_cs)  # Update the checksum in the slot list

        slot_len = 2621439
        cs_len = 15
        s_ind = 0x00000310
        c_ind = 0x00000300
        # Insert all checksums into data
        for i in slot_ls:
            dat = dat[:s_ind] + i[0] + dat[s_ind + slot_len + 1 :]  # Update the data in the original data
            dat = dat[:c_ind] + i[1] + dat[c_ind + cs_len + 1 :]  # Update the checksum in the original data
            s_ind += 2621456  # Increment the slot data index
            c_ind += 2621456  # Increment the checksum index

        # Manually doing General checksum
        general = dat[0x019003B0 : 0x019603AF + 1]  # Extract the data for the general checksum
        new_cs = hashlib.md5(general).hexdigest()  # Recalculate the general checksum
        cur_cs = binascii.hexlify(dat[0x019003A0 : 0x019003AF + 1]).decode("utf-8")  # Convert the current general checksum to a string

        writeval = binascii.unhexlify(new_cs)  # Convert the recalculated general checksum to bytes
        dat = dat[:0x019003A0] + writeval + dat[0x019003AF + 1 :]  # Update the general checksum in the original data

        with open(file, "wb") as fh1:
            fh1.write(dat)  # Write the updated data to the file

def change_name(file, nw_nm, dest_slot):
    """
    Changes the character name in a binary file at a specified slot.

    Args:
        file (str): The path to the binary file.
        nw_nm (str): The new name to be set.
        dest_slot (int): The slot number where the name should be changed.

    Returns:
        str: Returns "error" if the operation encounters an issue, otherwise None.

    Raises:
        None.
    """

    def replacer(file, old_name, name):
        """
        Scans for all occurrences of old_name and replaces them with name in the file.

        Args:
            file (str): The path to the binary file.
            old_name (bytes): The original name in bytes to be replaced.
            name (bytes): The new name in bytes to replace the old name.

        Returns:
            None.

        Raises:
            None.
        """
        with open(file, "rb") as fh:
            dat1 = fh.read()
            id_loc = []
            index = 0

            while index < len(dat1):
                index = dat1.find(old_name, index)

                if index == -1:
                    break
                id_loc.append(index)
                if len(id_loc) > 300:
                    return "error"
                index += 8

            nw_nm_bytes = name.encode("utf-16")[2:]

            num = 32 - len(nw_nm_bytes)
            for i in range(num):
                nw_nm_bytes = nw_nm_bytes + b"\x00"

            for i in id_loc:
                fh.seek(0)
                a = fh.read(i)
                b = nw_nm_bytes
                fh.seek(i + 32)
                c = fh.read()
                data = a + b + c

                with open(file, "wb") as f:
                    f.write(data)
        recalc_checksum(file)

    with open(file, "rb") as fh:
        dat1 = fh.read()

    name_locations = []
    ind1 = 0x1901D0E  # Start address of char names in header, 588 bytes apart
    for i in range(10):
        nm = dat1[ind1 : ind1 + 32]
        name_locations.append(nm)  # name in bytes
        ind1 += 588

    x = replacer(file, name_locations[dest_slot - 1], nw_nm)
    return x


def replace_id(file, newid):
    """
    Replaces the steamID in a binary file with a new ID.

    Args:
        file (str): The path to the binary file.
        newid (int): The new steamID to be set.

    Returns:
        bool: Returns False if the steamID length is not 17 digits, otherwise None.

    Raises:
        None.
    """

    id_loc = []
    index = 0

    with open(file, "rb") as f:
        dat = f.read()
        f.seek(26215348)  # start address of steamID
        steam_id = f.read(8)  # Get steamID

        if len(str(l_endian(steam_id))) != 17:
            return False  # Prevent save file corruption if steamID is not valid

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
            b = newid.to_bytes(8, "little")
            f.seek(i + 8)
            c = f.read()
            data = a + b + c

            with open(file, "wb") as fh:
                fh.write(data)

    recalc_checksum(file)


def copy_save(src_file, dest_file, src_char, dest_char):
    """
    Copy characters between save files.

    Args:
        src_file (str): The path to the source save file.
        dest_file (str): The path to the destination save file.
        src_char (int): The source character slot number.
        dest_char (int): The destination character slot number.

    Returns:
        None.

    Raises:
        None.
    """

    # Length of a character slot
    slot_len = 2621456

    # Get levels of characters from the source save file
    lvls = get_levels(src_file)

    # Retrieve the level of the source character
    lvl = lvls[src_char - 1]

    # Read the contents of the source save file
    with open(src_file, "rb") as fh:
        dat = fh.read()

    # Select the appropriate character slot from the source save file
    if src_char == 1:
        src_slot = dat[0x00000310 : 0x0028030F + 1]
    else:
        src_slot = dat[
            0x00000310
            + (src_char - 1) * slot_len : (0x0028030F + ((src_char - 1) * slot_len))
            + 1
        ]

    # Read the contents of the destination save file
    with open(dest_file, "rb") as fh:
        dat1 = fh.read()

    # Select the appropriate sections from the destination save file
    if dest_char == 1:
        slot_s = dat1[:0x00000310]
        slot_e = dat1[0x0028030F + 1 :]
    else:
        slot_s = dat1[: 0x00000310 + ((dest_char - 1) * slot_len)]
        slot_e = dat1[0x0028030F + ((dest_char - 1) * slot_len) + 1 :]

    # Combine the character slot from the source save file with the destination save file
    dat1 = slot_s + src_slot + slot_e

    # Write the modified contents back to the destination save file
    with open(dest_file, "wb") as fh:
        fh.write(dat1)

    # Set the character level in the destination save file
    set_level(dest_file, dest_char, lvl)


def get_id(file):
    with open(file, "rb") as f:
        dat = f.read()
        f.seek(26215348)  # start address of steamID
        steam_id = f.read(8)  # Get steamID
    return l_endian(steam_id)


def get_names(file):
    try:
        with open(file, "rb") as fh:
            dat1 = fh.read()

    except FileNotFoundError as e:
        return False

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
    val = range(random.randint(900, 900000))
    hashed = hashlib.sha1(str(val).encode())
    random_name = base64.urlsafe_b64encode(hashed.digest()[:12])
    return random_name.decode("utf-8")


def get_slot_ls(file):
    with open(file, "rb") as fh:
        dat = fh.read()

        slot1 = dat[0x00000310 : 0x0028030F + 1]  # SLOT 1
        slot2 = dat[0x00280320 : 0x050031F + 1]
        slot3 = dat[0x500330 : 0x78032F + 1]
        slot4 = dat[0x780340 : 0xA0033F + 1]
        slot5 = dat[0xA00350 : 0xC8034F + 1]
        slot6 = dat[0xC80360 : 0xF0035F + 1]
        slot7 = dat[0xF00370 : 0x118036F + 1]
        slot8 = dat[0x1180380 : 0x140037F + 1]
        slot9 = dat[0x1400390 : 0x168038F + 1]
        slot10 = dat[0x16803A0 : 0x190039F + 1]
        return [slot1, slot2, slot3, slot4, slot5, slot6, slot7, slot8, slot9, slot10]


def get_slot_slices(file):
    with open(file, "rb") as fh:
        dat = fh.read()

    slot1_start = dat[:0x00000310]
    slot1_end = dat[0x0028030F + 1 :]

    slot2_start = dat[:0x00280320]
    slot2_end = dat[0x050031F + 1 :]

    slot3_start = dat[:0x500330]
    slot3_end = dat[0x78032F + 1 :]

    slot4_start = dat[:0x780340]
    slot4_end = dat[0xA0033F + 1 :]

    slot5_start = dat[:0xA00350]
    slot5_end = dat[0xC8034F + 1 :]

    slot6_start = dat[:0xC80360]
    slot6_end = dat[0xF0035F + 1 :]

    slot7_start = dat[:0xF00370]
    slot7_end = dat[0x118036F + 1 :]

    slot8_start = dat[:0x1180380]
    slot8_end = dat[0x140037F + 1 :]

    slot9_start = dat[:0x1400390]
    slot9_end = dat[0x168038F + 1 :]

    slot10_start = dat[:0x16803A0]
    slot10_end = dat[0x190039F + 1 :]

    return [
        [slot1_start, slot1_end],
        [slot2_start, slot2_end],
        [slot3_start, slot3_end],
        [slot4_start, slot4_end],
        [slot5_start, slot5_end],
        [slot6_start, slot6_end],
        [slot7_start, slot7_end],
        [slot8_start, slot8_end],
        [slot9_start, slot9_end],
        [slot10_start, slot10_end],
    ]


def set_stats(file, char_num, stat_ls):
    """
    Set the stats of a character in a file.

    Parameters:
        file (str): The file to modify.
        char_num (int): The character number.
        stat_ls (list): The list of new stats.

    Returns:
        None
    """

    # Get the index values of the stats in the file
    locs = get_stats(file, char_num)[1]

    index = 0
    for loc in locs:
        # Get the character's slots and slot slices
        slots = get_slot_ls(file)
        slot_slices = get_slot_slices(file)
        dest_char = slots[char_num - 1]

        if index == 8:
            # Last value is the level index
            lvl_ind = loc

            # Get the current level of the character
            level = dest_char[lvl_ind : lvl_ind + 1]

            # Calculate the new level by subtracting 79 from the sum of the new stats
            new_lv = sum(stat_ls) - 79
            new_lvl_int = new_lv

            # Convert the new level to a 2-byte little-endian representation
            new_lv = new_lv.to_bytes(2, "little")

            # Construct the new data by replacing the old level with the new level
            data = (
                slot_slices[char_num - 1][0]
                + dest_char[:lvl_ind]
                + new_lv
                + dest_char[lvl_ind + 2 :]
                + slot_slices[char_num - 1][1]
            )

            # Write the new data to the file
            with open(file, "wb") as fh:
                fh.write(data)
            break

        # Convert the new stat value to a 1-byte little-endian representation
        writeval = stat_ls[index].to_bytes(1, "little")

        # Construct the new data by replacing the old stat value with the new stat value
        data = (
            slot_slices[char_num - 1][0]
            + dest_char[:loc]
            + writeval
            + dest_char[loc + 1 :]
            + slot_slices[char_num - 1][1]
        )

        # Write the new data to the file
        with open(file, "wb") as fh:
            fh.write(data)
        index += 1

    # Update the character's level in the file
    set_level(file, char_num, new_lvl_int)



def get_stats(file, char_slot):
    """
    Retrieve the stats and corresponding indexes for a character from a file.

    Parameters:
        file (str): The file to read from.
        char_slot (int): The character slot number.

    Returns:
        list: A list containing the stats, indexes, hp_inds, stam_inds, and fp_inds.
    """

    lvls = get_levels(file)  # Get the levels of all characters
    lv = lvls[char_slot - 1]  # Get the level of the specified character slot
    slots = get_slot_ls(file)  # Get the character slots

    start_ind = 0
    slot1 = slots[char_slot - 1]  # Get the slot data for the specified character slot
    indexes = []  # List to store the indexes of the stats

    for ind, b in enumerate(slot1):
        if ind > 60000:
            return None

        try:
            # Extract the individual stats using little-endian encoding
            stats = [
                l_endian(slot1[ind : ind + 1]),
                l_endian(slot1[ind + 4 : ind + 5]),
                l_endian(slot1[ind + 8 : ind + 9]),
                l_endian(slot1[ind + 12 : ind + 13]),
                l_endian(slot1[ind + 16 : ind + 17]),
                l_endian(slot1[ind + 20 : ind + 21]),
                l_endian(slot1[ind + 24 : ind + 25]),
                l_endian(slot1[ind + 28 : ind + 29]),
            ]

            # Check if the sum of stats equals the level plus 79,
            # and the level index matches the level
            if sum(stats) == lv + 79 and l_endian(slot1[ind + 44 : ind + 46]) == lv:
                start_ind = ind
                lvl_ind = ind + 44
                break

        except:
            continue

    idx = ind
    for i in range(8):
        indexes.append(idx)
        idx += 4

    indexes.append(lvl_ind)  # Add the level location to the end of indexes

    fp = []  # List to store the fp values
    fp_inds = []  # List to store the indexes of the fp values
    y = start_ind - 32

    for i in range(3):
        fp.append(l_endian(slot1[y : y + 2]))
        fp_inds.append(y)
        y += 4

    hp = []  # List to store the hp values
    hp_inds = []  # List to store the indexes of the hp values
    x = start_ind - 44

    for i in range(3):
        hp.append(l_endian(slot1[x : x + 2]))
        hp_inds.append(x)
        x += 4

    stam = []  # List to store the stamina values
    stam_inds = []  # List to store the indexes of the stamina values
    z = start_ind - 16

    for i in range(3):
        stam.append(l_endian(slot1[z : z + 2]))
        stam_inds.append(z)
        z += 4

    print(f"HP:  {hp}")
    print(f"STAM:  {stam}")
    print(f"FP:  {fp}")

    return [
        stats,
        indexes,
        hp_inds,
        stam_inds,
        fp_inds,
    ]  # Return the list of stats, indexes, hp_inds, stam_inds, and fp_inds

def set_level(file, char, lvl):
    """Sets levels in static header position by char names for in-game load save menu."""
    locs = [
        26221872,
        26222460,
        26223048,
        26223636,
        26224224,
        26224812,
        26225400,
        26225988,
        26226576,
        26227164,
    ]
    with open(file, "rb") as fh:
        dat = fh.read()
        a = dat[: locs[char - 1]]
        b = lvl.to_bytes(2, "little")
        c = dat[locs[char - 1] + 2 :]
        data = a + b + c

    with open(file, "wb") as f:
        f.write(data)
    recalc_checksum(file)


def get_levels(file):
    with open(file, "rb") as fh:
        dat = fh.read()

    ind = 0x1901D0E + 34
    lvls = []
    for i in range(10):
        l = dat[ind : ind + 2]

        lvls.append(l_endian(l))
        ind += 588
    return lvls

def set_attributes(file, slot, lvls, cheat=False):
    """
    Sets the attributes (HP, FP, ST) of a character in a given slot.

    Parameters:
        file (str): The file path of the save file.
        slot (int): The character slot number.
        lvls (list): A list of attribute levels [hp_level, fp_level, st_level].
        cheat (bool, optional): Flag indicating whether to set attributes to maximum value. Defaults to False.

    Returns:
        None
    """

    stats = get_stats(file, slot)
    hp_inds = stats[2]
    hp_val = stat_progression.get_hp(lvls[0])

    fp_inds = stats[3]
    fp_val = stat_progression.get_fp(lvls[1])

    st_inds = stats[4]
    st_val = stat_progression.get_st(lvls[2])

    char_slot = get_slot_ls(file)[slot - 1]
    dat_slices = get_slot_slices(file)[slot - 1]

    all_inds = [hp_inds, fp_inds, st_inds]
    vals = [hp_val, st_val, fp_val]

    if cheat:
        vals = [60000, 60000, 60000]  # Max value that can be represented with a 2-byte unsigned integer

    for ind_ls, nv in zip(all_inds, vals):
        char_slot = get_slot_ls(file)[slot - 1]
        dat_slices = get_slot_slices(file)[slot - 1]

        for i in ind_ls:
            dat = (
                dat_slices[0]
                + char_slot[:i]
                + nv.to_bytes(2, "little")
                + char_slot[i + 2 :]
                + dat_slices[1]
            )

        with open(file, "wb") as f:
            f.write(dat)

    recalc_checksum(file)


def additem(file, slot, itemids, quantity):
    """
    Adds an item with the specified item IDs and quantity to a character's inventory in a given slot.

    Parameters:
        file (str): The file path of the save file.
        slot (int): The character slot number.
        itemids (list): A list of item IDs [item_id_1, item_id_2].
        quantity (int): The quantity of the item to add.

    Returns:
        bool: True if the item was successfully added, None otherwise.
    """

    cs = get_slot_ls(file)[slot - 1]
    slices = get_slot_slices(file)
    s_start = slices[slot - 1][0]
    s_end = slices[slot - 1][1]

    with open(file, "rb") as f:
        dat = f.read()

        index = []
        cur = [int(i) for i in itemids]

        if cur is None:
            return None

        for ind, i in enumerate(cs):
            if ind < 30000:
                continue
            if ind > 195000:
                continue
            if (
                l_endian(cs[ind : ind + 1]) == cur[0]
                and l_endian(cs[ind + 1 : ind + 2]) == cur[1]
                and l_endian(cs[ind + 2 : ind + 3]) == 0
                and l_endian(cs[ind + 3 : ind + 4]) == 176
            ):
                index.append(ind + 4)
            elif (
                l_endian(cs[ind : ind + 1]) == cur[0]
                and l_endian(cs[ind + 1 : ind + 2]) == cur[1]
                and l_endian(cs[ind + 2 : ind + 3]) == 128
                and l_endian(cs[ind + 3 : ind + 4]) == 128
            ):
                index.append(ind + 4)

        if len(index) < 1:
            return None
        else:
            pos = index[0]

        with open(file, "wb") as fh:
            ch = (
                s_start
                + cs[:pos]
                + quantity.to_bytes(2, "little")
                + cs[pos + 2 :]
                + s_end
            )

            fh.write(ch)

        recalc_checksum(file)
        return True



def search_itemid(f1,f2,f3,q1,q2,q3):

    with open(f1, 'rb') as f, open(f2, 'rb') as ff, open(f3, 'rb') as fff:
        dat = f.read()
        dat2 = ff.read()
        dat3 = fff.read()
        c1 = dat[0x00000310:0x0028030F +1]
        c2 = dat2[0x00000310:0x0028030F +1]
        c3 = dat3[0x00000310:0x0028030F +1]
        index = []
        for ind, i in enumerate(c1):
            if ind < 30000:
                continue
            # Full Matches
            if ( l_endian(c1[ind:ind+1]) == int(q1) and l_endian(c2[ind:ind+1]) == int(q2) and l_endian(c3[ind:ind+1]) == int(q3)):
                if ( l_endian(c1[ind - 2 : ind - 1]) == 0 and l_endian(c1[ind -1 : ind]) == 176 ) or ( l_endian(c1[ind - 2 : ind - 1]) == 128 and l_endian(c1[ind-1 : ind]) == 128):
                    index.append(ind)



        if len(index) == 1:
            idx = index[0]
            idx -= 6
            return ["match", [l_endian(c1[idx + 2:idx + 3]), l_endian(c1[idx + 3:idx+4])]]

        elif len(index) > 1 and len(index) < 500:
            return_dict = {}
            for i in index:
                return_dict[i-6] = [l_endian(c1[i+2:i+3]), l_endian(c1[i+3:i+4])]
            return ["multi-match", return_dict]

        else:
            return None


def set_play_time(file,slot,time):
    # time = [hr,min,sec]
    time = [int(i) for i in time]
    hr = time[0]
    min = time[1]
    sec = time[2]
    seconds = sec + (min*60) + (hr*3600)
    time1 = 0x1901d0e+38
    time2 = 0x1901f5a+38
    time3 = 0x19021a6+38
    time4 = 0x19023f2+38
    time5 = 0x190263e+38
    time6 = 0x190288a+38
    time7 = 0x1902ad6+38
    time8 = 0x1902d22+38
    time9 = 0x1902f6e+38
    time10 = 0x19031ba+38

    times = [time1,time2,time3,time4,time5,time6,time7,time8,time9,time10]
    with open(file,"rb") as f:
        dat = f.read()
        ch = dat[:times[slot-1] ] + seconds.to_bytes(4, "little") + dat[times[slot-1] +4:]
    with open(file, "wb") as ff:
        ff.write(ch)
        recalc_checksum(file)


def set_starting_class(file, slot, char_class):
    cs = get_slot_ls(file)[slot - 1]
    slices = get_slot_slices(file)
    s_start = slices[slot - 1][0]
    s_end = slices[slot - 1][1]
    pos = 42165 # class flag is 42165 bytes from start of character block
    classes = {"Vagabond":0, "Warrior":1, "Hero":2, "Bandit":3, "Astrologer":4,
                "Prophet":5, "Confessor":6, "Samurai":7, "Prisoner":8, "Wretch":9
                }
#    with open(file, "rb") as f:
#        dat = f.read()


    with open(file, "wb") as fh:
        ch = (
            s_start
            + cs[:pos]
            + classes[char_class].to_bytes(1, "little")
            + cs[pos + 1 :]
            + s_end
        )

        fh.write(ch)

    recalc_checksum(file)
    return True


def find_inventory(file,slot,ids):
    with open(file, 'rb') as f:
        dat = f.read()

        c1 = get_slot_ls(file)[slot-1]


        for ind, i in enumerate(c1):
            if ind < 30000:
                continue
            # Full Matches
            if l_endian(c1[ind:ind+1]) > 0 and l_endian(c1[ind:ind+1]) < 1000: # quantity
                if ( l_endian(c1[ind - 2 : ind - 1]) == 0 and l_endian(c1[ind -1 : ind]) == 176 ) or ( l_endian(c1[ind - 2 : ind - 1]) == 128 and l_endian(c1[ind-1 : ind]) == 128):
                    if l_endian(c1[ind-3:ind-2]) == ids[1] and l_endian(c1[ind-4:ind-3]) == ids[0]:
                        index = ind
                        break

        return index


def get_inventory(file, slot):
    items = dict([(f"{v[0]}:{v[1]}",k) for k,v in itemdict.items()])
    with open(file, "rb") as f:
        dat = f.read()
        ind = find_inventory(file, slot, [106,0]) # Search for Tarnished Wizened Finger ( you get it at beginning of game)
        ind -= 4 # go to the uid point
        c1 = get_slot_ls(file)[slot-1]
        ls = []
        ind -= (12 * 1024) # inventory item entry is 12 bytes long, so decrement index to beginning of inv

        for i in range(2048):

            ids = f"{l_endian(c1[ind:ind+1])}:{l_endian(c1[ind+1:ind+2])}"
            try:
                name = items[ids]
            except KeyError:
                name = "?"

            ls.append({
                          "name": name,
                          "item_id": [l_endian(c1[ind:ind+1]), l_endian(c1[ind+1:ind+2])],
                          "uid": [l_endian(c1[ind+2:ind+3]),  l_endian(c1[ind+3:ind+4])],
                          "quantity": l_endian(c1[ind+4:ind+5]),
                          "pad1": [l_endian(c1[ind+5:ind+6]),l_endian(c1[ind+6:ind+7]),l_endian(c1[ind+7:ind+8])],
                          "iter": l_endian(c1[ind+8:ind+9]),
                          "pad2":[ l_endian(c1[ind+9:ind+10]), l_endian(c1[ind+10:ind+11]),l_endian(c1[ind+11:ind+12])],
                          "index": ind
                          })
            ind+= 12
        sorted_ls = sorted(ls, key=lambda d: d['name'])
    finished_ls = []

    for i in sorted_ls:
        if i["name"] == "?":
            continue
        if i["uid"] == [0,176]: #  or i["uid"] == [128,128]
            finished_ls.append(i)

    return finished_ls


def overwrite_item(file,slot, item_dict_entry, newids):
    #entry = {'name': 'Smithing Stone :[8]', 'item_id': [123, 39], 'uid': [0, 176], 'quantity': 63, 'pad1': [0, 0, 0], 'iter': 103, 'pad2': [58, 0, 0], 'index': 63987}

    pos = item_dict_entry["index"]

    for id in newids:
        cs = get_slot_ls(file)[slot-1]
        slices = get_slot_slices(file)
        s_start = slices[slot - 1][0]
        s_end = slices[slot - 1][1]
        ch = ( s_start + cs[:pos] + id.to_bytes(1, "little") + cs[pos + 1 :] + s_end )
        with open(file, "wb") as fh:
            fh.write(ch)
        pos += 1

    recalc_checksum(file)


def fix_stats(file, char_slot, stat_list):


    slots = get_slot_ls(file)
    slot_slices = get_slot_slices(file)

    start_ind = 0
    slot1 = slots[char_slot - 1]
    indexes = []
    lvl_ind = 0
    for ind, b in enumerate(slot1):
        if ind > 90000:
            break

        stats = [
            l_endian(slot1[ind : ind + 1]),
            l_endian(slot1[ind + 4 : ind + 5]),
            l_endian(slot1[ind + 8 : ind + 9]),
            l_endian(slot1[ind + 12 : ind + 13]),
            l_endian(slot1[ind + 16 : ind + 17]),
            l_endian(slot1[ind + 20 : ind + 21]),
            l_endian(slot1[ind + 24 : ind + 25]),
            l_endian(slot1[ind + 28 : ind + 29]),
            ]


        if stats == stat_list:
            lvl_ind = ind + 44
            break


    if lvl_ind == 0:
        return False

    new_lv = sum(stats) - 79
    new_lv_bytes = new_lv.to_bytes(2, "little")
    data = (
        slot_slices[char_slot - 1][0]
        + slot1[:lvl_ind]
        + new_lv_bytes
        + slot1[lvl_ind + 2 :]
        + slot_slices[char_slot - 1][1]
    )

    with open(file, "wb") as fh:
        fh.write(data)
    set_level(file, char_slot, new_lv) # Set level runs recalc_checksum
    return True


def set_runes(file, char_slot, old_quantity, new_quantity):


    slots = get_slot_ls(file)
    slot_slices = get_slot_slices(file)
    slot1 = slots[char_slot -1]
    index = 0
    for ind, b in enumerate(slot1):
        if ind > 80000:
            break
        x = l_endian(slot1[ind : ind + 4])
        if x == old_quantity:
            index = ind


    if index == 0:
        return False
    data = (
    slot_slices[char_slot - 1][0]
    + slot1[:index]
    + new_quantity.to_bytes(4,"little")
    + slot1[index + 4 :]
    + slot_slices[char_slot - 1][1]
    )

    with open(file, "wb") as fh:
        fh.write(data)
    recalc_checksum(file)
