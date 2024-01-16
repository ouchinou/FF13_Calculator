import json
import os


class Weapon:
    def __init__(self, Name, Rank, Initial_Lv, Max_Lv, Special_Property, Synthesis_Group, Buy_Price, Sell_Price, Shop, Catalyst, STR_Min, STR_Max, STR_Increment, MAG_Min, MAG_Max, MAG_Increment, EXP_Max, EXP_Current, EXP_Initial, EXP_Increment):
        self.name = Name
        self.rank = self.get_int(Rank)
        self.initial_lv = self.get_int(Initial_Lv)
        self.max_lv = self.get_int(Max_Lv)
        self.special_property = Special_Property
        self.synthesis_group = Synthesis_Group
        self.buy_price = self.get_int(Buy_Price)
        self.sell_price = self.get_int(Sell_Price)
        self.shop = Shop
        self.catalyst = Catalyst
        self.str_min = self.get_int(STR_Min)
        self.str_max = self.get_int(STR_Max)
        self.str_increment = self.get_int(STR_Increment)
        self.mag_min = self.get_int(MAG_Min)
        self.mag_max = self.get_int(MAG_Max)
        self.mag_increment = self.get_int(MAG_Increment)
        self.exp_max = self.get_int(EXP_Max)
        self.exp_current = self.get_int(EXP_Current)
        self.exp_initial = self.get_int(EXP_Initial)
        self.exp_increment = self.get_int(EXP_Increment)

    def get_int(self, value):
        try:
            return int(str(value).replace(',', ''))
        except Exception:
            return 0


class JsonLoader:
    @classmethod
    def load(cls, input_file='Weapons.json'):

        # Load the JSON data
        with open(os.path.join("json", input_file), 'r') as file:
            data = json.load(file)

            # Create a dictionary of weapons by character
            weapons_by_character = {}
            for weapon_data in data:
                character = weapon_data.pop('Character')
                weapon = Weapon(**weapon_data)
                if character not in weapons_by_character:
                    weapons_by_character[character] = []
                weapons_by_character[character].append(weapon)

            return weapons_by_character
