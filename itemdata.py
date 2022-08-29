import os, json


item_dict = {
    "Upgrade Materials": {
        "Ancient Dragon Stone": [156, 39],
        "Somber Ancient Dragon Stone": [184, 39],
        "Smithing Stone [1]": [116, 39],
        "Smithing Stone [2]": [117, 39],
        "Smithing Stone [3]": [118, 39],
        "Smithing Stone [4]": [119, 39],
        "Smithing Stone [5]": [120, 39],
        "Smithing Stone [6]": [121, 39],
        "Smithing Stone [7]": [122, 39],
        "Smithing Stone [8]": [123, 39],
        "Smithing Stone [9]": [124, 39],
        "Somber Stone [1]": [176, 39],
        "Somber Stone [2]": [177, 39],
        "Somber Stone [3]": [178, 39],
        "Somber Stone [4]": [179, 39],
        "Somber Stone [5]": [180, 39],
        "Somber Stone [6]": [181, 39],
        "Somber Stone [7]": [182, 39],
        "Somber Stone [8]": [183, 39],
        "Somber Stone [9]": [216, 39]
    },
    "Crafting Materials": {
        "Flight Pinion": [212,58],
        "Gold Fireflies": [75,81],
        "Root Resin": [39,81],
        "Old Fang": [192,58]
    },
    "Runes": {
        "Lords Rune": [103, 11],
        "Golden Rune [1]": [84, 11],
        "Golden Rune [2]": [85, 11],
        "Golden Rune [3]": [86, 11],
        "Golden Rune [4]": [87, 11],
        "Golden Rune [5]": [88, 11],
        "Golden Rune [6]": [89, 11],
        "Golden Rune [7]": [90, 11],
        "Golden Rune [8]": [91, 11],
        "Golden Rune [9]": [92, 11],
        "Golden Rune [10]": [93, 11]
    },
    "Key Items":
        {"Rune Arc": [190, 0],
        "Larval Tear": [249, 31]
    },
    "Tools": {
        "Gold Pickled Foot": [176, 4],
        "Silver Pickled Foot": [166,4],
        "Bewitching Branches": [22,13]
    },


}


class Items:
    def __init__(self):
        self.db = item_dict
        if os.path.exists("./data/config.json"):
            with open("./data/config.json", "r") as f:
                js = json.load(f)
                self.db["Custom Items"] = js["custom_ids"]  # ADDS custom IDS from config to itemdb merging with hard coded items
        self.categories = list(self.db.keys())  # Populate 1st dropdown menu


    def get_item_ls(self, cat):
        return list(self.db[cat])  # populate 2nd dropdown menu
