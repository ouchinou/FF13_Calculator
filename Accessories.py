import json

class accessories:
    def __init__(self, Name, Rank, Max_Lv, Min, Max, Increment, Effect_Lv_1, Synthesis_Group, Buy_Price, Sell_Price, Shop, Catalyst, EXP_Total, EXP_Max, EXP_Initial, EXP_Increment):
        self.name = Name
        self.rank = Rank
        self.max_lv = Max_Lv
        self.min = Min
        self.max = Max
        self.increment = Increment
        self.effect_lv_1 = Effect_Lv_1
        self.synthesis_group = Synthesis_Group
        self.buy_price = Buy_Price
        self.sell_price = Sell_Price
        self.shop = Shop
        self.catalyst = Catalyst
        self.exp_max = EXP_Max
        self.exp_initial = EXP_Initial
        self.exp_increment = EXP_Increment

# Load the JSON data
# Load the JSON data
with open('Accessories.json', 'r') as file:
    accessories_data = json.load(file)

# Create a list of Accessories objects
accessories_list = [accessories(**data) for data in accessories_data]