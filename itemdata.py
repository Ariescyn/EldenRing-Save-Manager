
item_dict = {
    'Larval Tear':[249,31,0,176],
    'Somber stone [1]': [176,39],
#    'somber 2': [177,39],
#    'somber 3': [178,39],
    'Somber stone [4]': [179,39],
#    'somber 5': [180,39],
#    'somber 6': [181,39],
#    'somber 7': [182,39],
    'Somber stone [8]': [183,39],
#    'somber 9': [184,39],
    'Somber stone [10]': [185,39],

    'Golden Rune [1]' : [84,11],
#    'golden rune 2' : [85,11],
#    'golden rune 3' : [86,11],
    'Golden Rune [4]' : [87,11],
#    'golden rune 5' : [88,11],
#    'golden rune 6' : [89,11],
#    'golden rune 7' : [90,11],
    'Golden Rune [8]' : [91,11],
#    'golden rune 9' : [92,11],
    'Golden Rune [10]' : [93,11],
    'Ancient Dragon Stone': [156,39],
    'Somber Ancient Dragon Stone' : [184,39]

        }

def get_list():
    return list(item_dict.keys())

def get(item):
    return item_dict.get(item)
