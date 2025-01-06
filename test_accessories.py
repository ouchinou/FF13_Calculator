import unittest
from accessories import Accessory

class AccessoryTests(unittest.TestCase):
    def test_accessory_initialization(self):
        accessory = Accessory(
            Name="Power Glove",
            Name_FR="Gant de puissance",
            Rank="3",
            Max_Lv="10",
            Min="20",
            Max="50",
            Increment="5",
            Effect_Lv_1="Increase strength by 10%",
            Synthesis_Group="Gloves",
            Buy_Price="5000",
            Sell_Price="2500",
            Shop="Accessory Shop",
            Catalyst="None",
            EXP_Total="100000",
            EXP_Max="50000",
            EXP_Initial="0",
            EXP_Increment="1000"
        )

        self.assertEqual(accessory.name, "Power Glove")
        self.assertEqual(accessory.name_fr, "Gant de puissance")
        self.assertEqual(accessory.rank, 3)
        self.assertEqual(accessory.max_lv, 10)
        self.assertEqual(accessory.min, 20)
        self.assertEqual(accessory.max, 50)
        self.assertEqual(accessory.increment, 5)
        self.assertEqual(accessory.effect_lv_1, "Increase strength by 10%")
        self.assertEqual(accessory.synthesis_group, "Gloves")
        self.assertEqual(accessory.buy_price, 5000)
        self.assertEqual(accessory.sell_price, 2500)
        self.assertEqual(accessory.shop, "Accessory Shop")
        self.assertEqual(accessory.catalyst, "None")
        self.assertEqual(accessory.exp_max, 100000)
        self.assertEqual(accessory.exp_initial, 0)
        self.assertEqual(accessory.exp_increment, 1000)

if __name__ == "__main__":
    unittest.main()