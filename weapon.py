import json

class Weapon:
    def __init__(self, Name, Rank, Initial_Lv, Max_Lv, Special_Property, Synthesis_Group, Buy_Price, Sell_Price , Shop, Catalyst, STR_Min, STR_Max, STR_Increment, MAG_Min, MAG_Max, MAG_Increment, EXP_Max, EXP_Current, EXP_Initial, EXP_Increment):
        self.name = Name
        self.rank = Rank
        self.initial_lv = Initial_Lv
        self.max_lv = Max_Lv
        self.special_property = Special_Property
        self.synthesis_group = Synthesis_Group
        self.buy_price = Buy_Price
        self.sell_price = Sell_Price
        self.shop = Shop
        self.catalyst = Catalyst
        self.str_min = STR_Min
        self.str_max = STR_Max
        self.str_increment = STR_Increment
        self.mag_min = MAG_Min
        self.mag_max = MAG_Max
        self.mag_increment = MAG_Increment
        self.exp_max = EXP_Max
        self.exp_current = EXP_Current
        self.exp_initial = EXP_Initial
        self.exp_increment = EXP_Increment

# Load the JSON data
with open('Weapons.json', 'r') as file:
    weapons_data = json.load(file)

# Create a dictionary of weapons by character
weapons_by_character = {}
for weapon_data in weapons_data:
    character = weapon_data.pop('Character')
    weapon = Weapon(**weapon_data)
    if character not in weapons_by_character:
        weapons_by_character[character] = []
    weapons_by_character[character].append(weapon)