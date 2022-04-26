
item_dict = {
    'Larval Tear':[249,31,0,176],
    'Ancient Dragon Stone': [156,39],
    'Somber Ancient Dragon Stone' : [184,39],
    'Rune Arc': [190,0],
    'Lords Rune': [103,11],


    'Smithing Stone [1]': [116,39],
    'Smithing Stone [2]': [117,39],
    'Smithing Stone [3]': [118,39],
    'Smithing Stone [4]': [119,39],
    'Smithing Stone [5]': [120,39],
    'Smithing Stone [6]': [121,39],
    'Smithing Stone [7]': [122,39],
    'Smithing Stone [8]': [123,39],
    'Smithing Stone [9]': [124,39],
    'Smithing Stone [10]': [125,39],


    'Somber Stone [1]': [176,39],
    'Somber Stone [2]': [177,39],
    'Somber Stone [3]': [178,39],
    'Somber Stone [4]': [179,39],
    'Somber Stone [5]': [180,39],
    'Somber Stone [6]': [181,39],
    'Somber Stone [7]': [182,39],
    'Somber Stone [8]': [183,39],
    'Somber Stone [9]': [184,39],
    'Somber Stone [10]': [185,39],

    'Golden Rune [1]' : [84,11],
    'Golden Rune [2]' : [85,11],
    'Golden Rune [3]' : [86,11],
    'Golden Rune [4]' : [87,11],
    'Golden Rune [5]' : [88,11],
    'Golden Rune [6]' : [89,11],
    'Golden Rune [7]' : [90,11],
    'Golden Rune [8]' : [91,11],
    'Golden Rune [9]' : [92,11],
    'Golden Rune [10]' : [93,11]

        }

def get_list():
    return list(item_dict.keys())

def get(item):
    return item_dict.get(item)
