import json
import os


class ElectricComponent:
    def __init__(self, Component_Name, EXP, Multiplier, Source, Buy_Price, Sell_Price):
        """
        Initializes an ElectricComponent object.

        Args:
            Component_Name (str): The name of the electric component.
            EXP (int): The experience gained from the component.
            Multiplier (int): The multiplier value of the component.
            Source (str): The source of the component.
            Buy_Price (int): The buying price of the component.
            Sell_Price (int): The selling price of the component.
        """
        self.name = Component_Name
        self.exp = self.get_int(EXP)
        self.multiplier = self.get_int(Multiplier)
        self.source = Source
        self.buy_price = self.get_int(Buy_Price)
        self.sell_price = self.get_int(Sell_Price)

    def get_int(self, value):
        """
        Converts a value to an integer.

        Args:
            value: The value to be converted.

        Returns:
            int: The converted integer value.
        """
        try:
            return int(str(value).replace(',', ''))
        except Exception:
            return 0

class JsonLoader:
    @classmethod
    def load(cls, input_file='Electric_Components.json'):

        # Load the JSON data
        with open(os.path.join("json", input_file), 'r') as file:
            data = json.load(file)

            # Create a list of objects with buy_price != 0
            return [ElectricComponent(**elem) for elem in data]
        