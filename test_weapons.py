import unittest
from weapons import Weapon

class WeaponTests(unittest.TestCase):
    def test_weapon_initialization(self):
        weapon = Weapon(
            Name="Excalibur",
            Rank="5",
            Initial_Lv="1",
            Max_Lv="99",
            Special_Property="Holy element",
            Synthesis_Group="Swords",
            Buy_Price="10000",
            Sell_Price="5000",
            Shop="Weapon Shop",
            Catalyst="None",
            STR_Min="50",
            STR_Max="100",
            STR_Increment="10",
            MAG_Min="30",
            MAG_Max="80",
            MAG_Increment="5",
            EXP_Max="100000",
            EXP_Current="50000",
            EXP_Initial="0",
            EXP_Increment="1000"
        )

        self.assertEqual(weapon.name, "Excalibur")
        self.assertEqual(weapon.rank, 5)
        self.assertEqual(weapon.initial_lv, 1)
        self.assertEqual(weapon.max_lv, 99)
        self.assertEqual(weapon.special_property, "Holy element")
        self.assertEqual(weapon.synthesis_group, "Swords")
        self.assertEqual(weapon.buy_price, 10000)
        self.assertEqual(weapon.sell_price, 5000)
        self.assertEqual(weapon.shop, "Weapon Shop")
        self.assertEqual(weapon.catalyst, "None")
        self.assertEqual(weapon.str_min, 50)
        self.assertEqual(weapon.str_max, 100)
        self.assertEqual(weapon.str_increment, 10)
        self.assertEqual(weapon.mag_min, 30)
        self.assertEqual(weapon.mag_max, 80)
        self.assertEqual(weapon.mag_increment, 5)
        self.assertEqual(weapon.exp_max, 100000)
        self.assertEqual(weapon.exp_current, 50000)
        self.assertEqual(weapon.exp_initial, 0)
        self.assertEqual(weapon.exp_increment, 1000)

if __name__ == "__main__":
    unittest.main()

