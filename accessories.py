import json
import os


class Accessory:
    def __init__(self, Name, Rank, Max_Lv, Min, Max, Increment, Effect_Lv_1, Synthesis_Group, Buy_Price, Sell_Price, Shop, Catalyst, EXP_Total, EXP_Max, EXP_Initial, EXP_Increment):
        self.name = Name
        self.rank = self.get_int(Rank)
        self.max_lv = self.get_int(Max_Lv)
        self.min = self.get_int(Min)
        self.max = self.get_int(Max)
        self.increment = self.get_int(Increment)
        self.effect_lv_1 = Effect_Lv_1
        self.synthesis_group = Synthesis_Group
        self.buy_price = self.get_int(Buy_Price)
        self.sell_price = self.get_int(Sell_Price)
        self.shop = Shop
        self.catalyst = Catalyst
        self.exp_max = self.get_int(EXP_Max)
        self.exp_initial = self.get_int(EXP_Initial)
        self.exp_increment = self.get_int(EXP_Increment)

    def get_int(self, value):
        try:
            return int(str(value).replace(',', ''))
        except Exception:
            return 0


class JsonLoader:
    @classmethod
    def load(cls, input_file='Accessories.json'):

        # Load the JSON data
        with open(os.path.join("json", input_file), 'r') as file:
            data = json.load(file)

            # Create a list of objects
            return [Accessory(**elem) for elem in data]
