import json


class Weapon:
    def __init__(self, Name, Rank, Initial_Lv, Max_Lv, Special_Property, Synthesis_Group, Buy_Price, Sell_Price , Shop, Catalyst, STR_Min, STR_Max, STR_Increment, MAG_Min, MAG_Max, MAG_Increment, EXP_Max, EXP_Current, EXP_Initial, EXP_Increment):
        self.name = Name
        self.rank = int(Rank)
        self.initial_lv = int(Initial_Lv)
        self.max_lv = int(Max_Lv)
        self.special_property = Special_Property
        self.synthesis_group = Synthesis_Group
        self.buy_price = Buy_Price
        self.sell_price = Sell_Price
        self.shop = Shop
        self.catalyst = Catalyst

        self.str_min = STR_Min
        if isinstance(STR_Min, int):
            self.str_min = STR_Min
        else:
            self.str_min = int(STR_Min.replace(',', ''))
    
        self.str_max = STR_Max
        if isinstance(STR_Max, int):
            self.str_max = STR_Min
        else:
            self.str_max = int(STR_Max.replace(',',''))
        
        self.str_increment = STR_Increment
        if isinstance(STR_Increment, int):
            self.str_increment = STR_Increment
        else:    
            self.str_increment = int(STR_Increment)
        
        self.str_increment = STR_Increment
        if isinstance(STR_Increment, int):
            self.str_increment = STR_Increment
        else:  
            self.mag_min = int(MAG_Min.replace(',', ''))

        self.mag_max = MAG_Max
        if isinstance(MAG_Max, int):
            self.mag_max = MAG_Max
        else:  
            self.mag_max = int(MAG_Max.replace(',', ''))

        self.str_increment = STR_Increment
        if isinstance(STR_Increment, int):
            self.str_increment = STR_Increment
        else:  
            self.mag_increment = int(MAG_Increment)
                
        self.str_increment = STR_Increment
        if isinstance(STR_Increment, int):
            self.str_increment = STR_Increment
        else:  
        self.exp_max = int(EXP_Max.replace(',', ''))        
        
        self.str_increment = STR_Increment
        if isinstance(STR_Increment, int):
            self.str_increment = STR_Increment
        else:  
        self.exp_current = int(EXP_Current.replace(',', ''))
        self.exp_initial = int(EXP_Initial.replace(',', ''))
        self.exp_increment = int(EXP_Increment.replace(',', ''))


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