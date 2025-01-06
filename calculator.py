import select
import sys
import os
import math
from pathlib import Path
from turtle import up, update

from PyQt6.QtWidgets import QApplication, QMainWindow, QTableWidgetItem
from PyQt6.QtGui import QPixmap, QColor, QBrush
from PyQt6.QtCore import Qt
from PyQt6 import uic

import weapons
import accessories
import electric_components
import organic_components


class FF13Calculator(QMainWindow):
    """This "window" is a QWidget. If it has no parent, it will appear as a free-floating window as we want."""

    def __init__(self, weapons_by_character, accessories_list, electric_components_list, organic_components_list, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # initialize UI from the QtDesigner UI file
        uic.loadUi(Path(__file__).parent / "gui" / "FF13_Calculator.ui", self)

        self.weapons_by_character = weapons_by_character
        self.accessories_list = accessories_list    
        self.electric_components_list = electric_components_list
        self.organic_components_list = organic_components_list

        self.exp_req_before_star = 0

        self.selected_tab = 0
        self.selected_object = None
        self.cur_level = 0
        self.cur_exp = 0
        self.cur_multiplier = 1
        self.tot_exp = 0
        self.max_exp_lvl = 0

        # initialize callbacks
        self.init_callbacks()

        # update GUI from loaded files
        self.initialize_gui()

        self.update_weapons()

    def init_callbacks(self):
        # character/weapon
        self.character_combo_box.currentIndexChanged.connect(self.on_character_selection_changed)
        self.weapon_combo_box.currentIndexChanged.connect(self.on_weapon_selection_changed)

        # info form
        self.level_line_edit.textChanged.connect(self.on_level_change)
        self.exp_cur_line_edit.textChanged.connect(self.on_exp_cur_change)
        self.exp_tot_line_edit.textChanged.connect(self.on_exp_tot_change)

        # multiplier
        self.multiplier_combo_box.currentIndexChanged.connect(self.on_multiplier_change)

        # object tab
        self.tab_widget.currentChanged.connect(self.on_tab_changed)

        # accessory
        self.accessory_combo_box.currentIndexChanged.connect(self.on_accessory_selection_changed)

    def initialize_gui(self):
        # fill combo boxes
        self.character_combo_box.addItems(self.weapons_by_character.keys())
        self.cur_level = int(self.level_line_edit.text())
        self.cur_exp = int(self.exp_cur_line_edit.text())
        self.tot_exp = int(self.exp_tot_line_edit.text())
        # Ajustement de la largeur des colonnes
        self.component_table.setColumnWidth(0, 125)  # Largeur pour "Name"
        self.component_table.setColumnWidth(1, 125)  # Largeur pour "Number Required"
        self.component_table.setColumnWidth(2, 125)  # Largeur pour "Cost(Gil)"
        self.component_table.setColumnWidth(3, 125)  # Largeur pour "Exp"
        self.component_table.setColumnWidth(4, 125)  # Largeur pour "Exp Total"

        self.accessory_combo_box.addItems([accessory.name for accessory in self.accessories_list])

    ##############################################
    # Méthodes pour gérer les événements
    ##############################################

    def on_tab_changed(self):
        print("on_tab_changed")
        if self.tab_widget.currentIndex() == 0:
            self.selected_tab = 0
            self.reset_current()
            self.on_weapon_selection_changed()
        elif self.tab_widget.currentIndex() == 1:
            self.selected_tab = 1
            self.reset_current()
            self.on_accessory_selection_changed()
        else:
            print("on_tab_changed:unknown tab")
        
    def on_character_selection_changed(self):
        print("on_character_selection_changed")
        self.update_weapons()

    def on_selection_changed(self, object_type, get_selected_object):
        print(f"on_{object_type}_selection_changed")
        self.selected_object = get_selected_object(self.__dict__[f"{object_type}_combo_box"].currentText())
        if self.selected_object:
            self.update()

    def on_weapon_selection_changed(self):
        self.on_selection_changed("weapon", self.get_selected_weapon)

    def on_accessory_selection_changed(self):
        self.on_selection_changed("accessory", self.get_selected_accessory)
        self.update_accessories_image()

    def on_level_change(self):
        print("on_level_change")
        self.cur_level = self.get_current_level()
        if self.cur_level is None:
            pass
        else:
            if self.cur_level <= 1:
                self.cur_level = 1
                self.max_exp_lvl = self.exp_max_per_level(self.cur_level, self.selected_object.exp_initial, self.selected_object.exp_increment)
            elif self.cur_level > self.selected_object.max_lv:
                self.cur_level = self.selected_object.max_lv
                self.max_exp_lvl = 0
                self.update()
                self.set_tot_exp_qline(self.selected_object.exp_max)
            else :
                self.update()
                self.set_tot_exp_qline(self.min_exp_per_level(self.cur_level, self.selected_object.exp_initial, self.selected_object.exp_increment))
                self.max_exp_lvl = self.exp_max_per_level(self.cur_level, self.selected_object.exp_initial, self.selected_object.exp_increment)

            self.set_current_exp_qline(0)
            self.set_current_level_qline(self.cur_level)

    def on_exp_cur_change(self):
        print("on_exp_cur_change")
        self.cur_exp = self.get_current_exp()
        if self.cur_exp is None:
            pass
        else :
            if self.cur_exp > self.calcul_max_exp_cur(self.cur_level, self.selected_object.exp_initial, self.selected_object.exp_increment) :
                self.set_current_exp_qline(self.calcul_max_exp_cur(self.cur_level, self.selected_object.exp_initial, self.selected_object.exp_increment))
            self.update()

            self.set_current_exp_qline(self.cur_exp)
            self.set_tot_exp_qline(self.calcul_exp_total(self.cur_level, self.cur_exp, self.selected_object.exp_initial, self.selected_object.exp_increment))

    def on_exp_tot_change(self):
        print("on_exp_tot_change")
        self.tot_exp = self.get_total_exp()
        if self.tot_exp is None:
            pass
        else :
            if self.tot_exp > self.selected_object.exp_max :
                self.set_current_exp_qline(self.selected_object.exp_max)
                self.set_current_level_qline(self.selected_object.max_lv)
            self.update()
        
    def on_multiplier_change(self):
        print("on_multiplier_change")
        self.cur_multiplier = self.get_current_multiplier()
        #¢self.set_current_multiplier_combobox(self.cur_multiplier)
        self.update()

    ##############################################
    # Méthodes pour acquerir les données
    ##############################################
    def get_selected_weapon(self, weapon_name):
        """
        Returns the selected weapon based on its name.

        Parameters:
        - weapon_name (str): The name of the weapon to search for.

        Returns:
        - Weapon or None: The selected weapon if found, None otherwise.
        """
        selected_weapon = None
        for character_weapons in self.weapons_by_character.values():
            for w in character_weapons:
                if w.name == weapon_name:
                    selected_weapon = w
                    break
            if selected_weapon:
                break
        return selected_weapon

    def get_selected_accessory(self, accessory_name):
        """
        Returns the selected accessory based on its name.

        Parameters:
        - accessory_name (str): The name of the accessory to search for.

        Returns:
        - Accessory or None: The selected accessory if found, None otherwise.
        """
        selected_accessory = None
        for accessory in self.accessories_list:
            if accessory.name == accessory_name:
                selected_accessory = accessory
                break
        return selected_accessory

    def get_current_level(self):
        """
        Returns the current level of the selected weapon.

        Returns:
        - int: The current level of the selected weapon.
        """
        if self.level_line_edit.text() == "" or self.level_line_edit.text().isalpha():
            return None
        else :
            return int(self.level_line_edit.text())
    
    def get_current_exp(self):
        """
        Returns the current experience of the selected weapon.

        Returns:
        - int: The current experience of the selected weapon.
        """
        if self.exp_cur_line_edit.text() == "" or self.exp_cur_line_edit.text().isalpha():
            return None
        else :
            return int(self.exp_cur_line_edit.text())
    
    def get_total_exp(self):
        """
        Returns the total experience of the selected weapon.

        Returns:
        - int: The total experience of the selected weapon.
        """
        if self.exp_tot_line_edit.text() == "" or self.exp_tot_line_edit.text().isalpha():
            return None
        else :
            return int(self.exp_tot_line_edit.text())
    
    def get_current_multiplier(self):
        """
        Returns the current multiplier.

        Returns:
        - int: The current multiplier.
        """
        return float(self.multiplier_combo_box.currentText())
    
    ##############################################
    # Méthodes pour mettre à jour les données
    ##############################################
    def update(self):
        print("update")
        if isinstance(self.selected_object, weapons.Weapon):
            self.update_weapon()
        elif isinstance(self.selected_object, accessories.Accessory):
            self.update_accessory()  # Assurez-vous d'avoir une méthode qui met à jour les accessoires
        else:
            print("Unknown object type")
        
        self.update_remaining_exp_label()
        self.update_component_table()

    def update_weapon(self):
        print("update_weapon")
        self.update_weapon_tab_info(self.selected_object)
        self.set_weapon_tab_title(self.selected_object)
        
    def update_accessory(self):
        print("update_accessory")
        self.update_accessory_tab_info(self.selected_object)
        self.set_accessory_tab_title(self.selected_object)
    
    def reset_current(self):
        print("reset_current")
        self.set_current_level_qline(1)
        self.set_current_exp_qline(0)
        self.set_current_multiplier_combobox(1)


    def update_weapon_tab_info(self, weapon):

            # Format the required information from the weapon object
            strength_current = weapon.str_min + weapon.str_increment * (self.cur_level - 1)
            strength_info = f"{strength_current} / {weapon.str_max}"

            magic_current = weapon.mag_min + weapon.mag_increment * (self.cur_level - 1)
            magic_info = f"{magic_current} / {weapon.mag_max}"

            experience_info = f"{self.cur_exp:_} / {self.max_exp_lvl:_}"

            shop_info = f"{weapon.shop} - {weapon.buy_price} (Gil)"

            # Update the weapon information
            self.set_weapon_info_label(strength=strength_info,
                                    magic=magic_info,
                                    experience=experience_info,
                                    catalyst=weapon.catalyst,
                                    shop=shop_info)

    def update_accessory_tab_info(self, accessory):
            # Format the required information from the weapon object
            hp_current = accessory.min + accessory.increment * (self.cur_level - 1)
            hp_info = f"+ {hp_current} "

            experience_info = f"{self.cur_exp:_} / {self.max_exp_lvl:_}"

            shop_info = f"{accessory.shop} - {accessory.buy_price} (Gil)"

            # Update the accessory information
            self.set_accessory_info_label(hp=hp_info,
                                    experience=experience_info,
                                    synthesis=accessory.effect_lv_1,
                                    catalyst=accessory.catalyst,
                                    shop=shop_info)
            
    def update_remaining_exp_label(self):
        print("update_remaining_exp_label")

        if self.level_line_edit.text() == "1" :
            self.exp_req_before_star = self.selected_object.exp_max - self.cur_exp
        else :
            total_gained_exp = 0
            for i in range(int(self.level_line_edit.text()) -1 ):
                total_gained_exp += self.selected_object.exp_initial + self.selected_object.exp_increment * i
            #exp_already_gained_w_level = self.calcul_exp_total()
            exp_already_gained_w_level = self.selected_object.exp_initial + self.selected_object.exp_increment * (int(self.level_line_edit.text()) - 1)
            print(f"exp_already_gained_w_level: {exp_already_gained_w_level}")
            self.exp_req_before_star = self.selected_object.exp_max - self.calcul_exp_total(self.cur_level, self.cur_exp, self.selected_object.exp_initial, self.selected_object.exp_increment)
            #self.exp_req_before_star = self.selected_object.exp_max - total_gained_exp - self.cur_exp + exp_already_gained_w_level

        self.remaining_exp_label.setText(f"{self.exp_req_before_star}")

    def update_component_table(self):
        print("update_table")
        nb_row = 5

        # Mettre à jour le tableau avec les composants électriques
        for row, component in enumerate(self.electric_components_list[-nb_row:]):
            self.add_row_if_not_exists(row)
            self.update_row(component, row)

        self.update_min_cost()

    def update_row(self, component, row):
        self.update_column(component.name, row, 0)
        number_required = math.ceil(self.calculate_number_required(component))
        self.update_column(str(number_required), row, 1)
        gils = math.ceil(self.calculate_gils(number_required, component))
        self.update_column(str(gils), row, 2)

    def update_weapons(self):
        character_name = self.character_combo_box.currentText()
        print(f"Selected Character_weapon: {character_name}")
        weapons = self.weapons_by_character.get(character_name, [])
        self.weapon_combo_box.clear()
        self.weapon_combo_box.addItems([weapon.name for weapon in weapons])

        self.update_character_image(character_name)

    def update_accessories_image(self):
        self.update_character_image("FFXIII_Characters")

    ##############################################
    # Méthodes pour afficher les données
    ##############################################

    def set_weapon_tab_title(self, weapon):
        """
        Renvoie le titre de l'arme avec le niveau actuel.

        Args:
            weapon (Weapon): L'objet Weapon représentant l'arme.

        Returns:
            str: Le titre de l'arme avec le niveau actuel.
        """
        self.txt_weapon_title.setText(f"{weapon.name} {self.cur_level}/{weapon.max_lv}")

    def set_accessory_tab_title(self, accessory):
        """
        Renvoie le titre de l'accessoire.

        Args:
            accessory (Accessory): L'objet Accessory représentant l'accessoire.

        Returns:
            str: Le titre de l'accessoire.
        """
        self.txt_accessory_title.setText(f"{accessory.name} ({accessory.name_fr}) {self.cur_level}/{accessory.max_lv}")

    def set_weapon_info_label(self, strength, magic, experience, catalyst, shop):
        self.txt_info_strength.setText(strength)
        self.txt_info_magic.setText(magic)
        self.txt_info_experience.setText(experience)
        self.txt_info_catalyst.setText(catalyst)
        self.txt_info_shop.setText(shop)

    def set_accessory_info_label(self, hp, experience, synthesis, catalyst, shop):
        self.txt_info_hp.setText(hp)
        self.txt_info_experience_accessory.setText(experience)
        self.txt_info_synthesis.setText(synthesis)
        self.txt_info_catalyst_accessory.setText(catalyst)
        self.txt_info_shop_accessory.setText(shop)

    def update_character_image(self, character):
        image_path = os.path.join('pics', f'{character}.png')
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            # Ajustement de la taille du pixmap pour s'assurer qu'il n'est pas redimensionné
            self.character_image_label.setPixmap(pixmap.scaled(self.character_image_label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            print(f"Image not found for character: {character}")
   
    def set_current_level_qline(self, level):
        self.level_line_edit.setText(str(level))

    def set_current_exp_qline(self, exp):
        self.exp_cur_line_edit.setText(str(exp))

    def set_tot_exp_qline(self, exp):
        print(f"set_tot_exp_qline: {exp}")
        self.exp_tot_line_edit.setText(str(exp))

    def set_current_multiplier_combobox(self, multiplier):
        self.multiplier_combo_box.setCurrentText(str(multiplier))
    
    def update_column(self, text, row, column):
        item = QTableWidgetItem(text)
        self.component_table.setItem(row, column, item)

    def update_min_cost(self):
        light_green = QColor('green')
        light_green.setAlpha(128)  # Définir l'opacité à 50%

        # Trouver le coût minimum
        min_cost = min(int(self.component_table.item(row, 2).text()) for row in range(self.component_table.rowCount()))

        # Mettre en évidence la ligne avec le coût minimum
        for row in range(self.component_table.rowCount()):
            gils = int(self.component_table.item(row, 2).text())
            current_text = self.component_table.item(row, 2).text()
            new_item = QTableWidgetItem(current_text)

            if gils == min_cost:
                new_item.setBackground(light_green)
            else:
                new_item.setBackground(QColor('white'))

            self.component_table.setItem(row, 2, new_item)
    
    def add_row_if_not_exists(self, row):
        if row >= self.component_table.rowCount():
            self.component_table.insertRow(self.component_table.rowCount())     
        
    ##############################################
    # Méthodes de calculs
    ##############################################

    def calculate_number_required(self, component):
        number_required = (self.exp_req_before_star/float(self.multiplier_combo_box.currentText())) / (component.exp)
        return number_required

    def calculate_gils(self, number_required, component):
        gils = number_required * component.buy_price
        return gils

    def calcul_max_exp_cur(self, level, exp_initial, exp_increment):
        max_exp_cur = exp_initial + exp_increment * (level - 1)
        return max_exp_cur
    
    def calcul_exp_total(self, level, exp, exp_initial, exp_increment):
        exp_total = 0
        for i in range(level - 1):
            exp_total += exp_initial + exp_increment * i
        exp_total += exp
        return exp_total
    
    def min_exp_per_level(self, level, exp_initial, exp_increment):
        exp_total = 0
        for i in range(level - 1):
            exp_total += exp_initial + exp_increment * i
        print(f"exp_total: {exp_total}")
        return exp_total

    def exp_max_per_level(self, level, exp_initial, exp_increment):
        max_exp_lvl = 0
        for i in range(level):
            max_exp_lvl += exp_initial + exp_increment * i
        print(f"exp_total: {max_exp_lvl}")
        return max_exp_lvl

def main():
    # create Application
    app = QApplication(sys.argv)

    # load files
    weapons_data = weapons.JsonLoader.load()
    accessories_data = accessories.JsonLoader.load()
    electric_components_data = electric_components.JsonLoader.load()
    organic_components_data = organic_components.JsonLoader.load()

    # create main window
    calculator = FF13Calculator(weapons_data, accessories_data,electric_components_data, organic_components_data)
    calculator.show()

    # start main loop
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
