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
        """
        This method is called when the character selection is changed.

        It prints a message indicating the change and updates the weapons
        accordingly by calling the update_weapons method.
        """
        print("on_character_selection_changed")
        self.update_weapons()

    def on_selection_changed(self, object_type, get_selected_object):
        """
        Handles the event when the selection is changed in a combo box.

        Args:
            object_type (str): The type of object being selected (e.g., 'item', 'character').
            get_selected_object (callable): A function that takes the current text of the combo box
                                            and returns the corresponding selected object.

        Side Effects:
            Updates the selected object based on the current selection in the combo box.
            Calls the update method if a valid object is selected.
        """
        print(f"on_{object_type}_selection_changed")
        self.selected_object = get_selected_object(self.__dict__[f"{object_type}_combo_box"].currentText())
        if self.selected_object:
            self.update()

    def on_weapon_selection_changed(self):
        """
        Handles the event when the weapon selection is changed.

        This method is triggered whenever the weapon selection is changed in the UI.
        It calls the `on_selection_changed` method with the type "weapon" and the
        currently selected weapon.

        Returns:
            None
        """
        self.on_selection_changed("weapon", self.get_selected_weapon)

    def on_accessory_selection_changed(self):
        """
        Handles the event when the accessory selection is changed.

        This method is triggered whenever the accessory selection is changed in the UI.
        It performs the following actions:
        1. Calls `on_selection_changed` with the type "accessory" and the method to get the selected accessory.
        2. Updates the accessory image based on the new selection.

        Returns:
            None
        """
        self.on_selection_changed("accessory", self.get_selected_accessory)
        self.update_accessories_image()

    def on_level_change(self):
        """
        Handles the event when the level changes.
        This method updates the current level and adjusts the experience points
        accordingly. It ensures that the level does not go below 1 or above the
        maximum level allowed for the selected object. Depending on the new level,
        it updates the maximum experience for the level and the total experience
        required.
        Steps performed:
        1. Retrieves the current level.
        2. If the current level is None, it does nothing.
        3. If the current level is less than or equal to 1, sets the level to 1 and
           calculates the maximum experience for level 1.
        4. If the current level exceeds the maximum level of the selected object,
           sets the level to the maximum level and updates the total experience.
        5. Otherwise, updates the total experience and calculates the minimum and
           maximum experience for the current level.
        6. Resets the current experience to 0.
        7. Updates the current level display.
        Note:
            This method assumes that `self.get_current_level`, `self.exp_max_per_level`,
            `self.min_exp_per_level`, `self.update`, `self.set_tot_exp_qline`, 
            `self.set_current_exp_qline`, and `self.set_current_level_qline` are 
            defined elsewhere in the class.
        """
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
        """
        Handles the event when the current experience value changes.
        This method performs the following actions:
        1. Prints a debug message indicating the method was called.
        2. Retrieves the current experience value and updates `self.cur_exp`.
        3. If `self.cur_exp` is None, the method exits.
        4. If the current level (`self.cur_level`) is greater than or equal to the maximum level of the selected object, 
           it sets the current experience to 0.
        5. If the current experience exceeds the maximum experience for the current level, it adjusts the current experience 
           to the maximum allowable experience for that level.
        6. Updates the UI to reflect the new experience values.
        7. Sets the total experience in the UI based on the current level, current experience, initial experience, and experience increment.
        Returns:
            None
        """
        print("on_exp_cur_change")
        self.cur_exp = self.get_current_exp()
        if self.cur_exp is None:
            pass
        else :
            if self.cur_level >= self.selected_object.max_lv:
                self.set_current_exp_qline(0)
            if self.cur_exp > self.calcul_max_exp_cur(self.cur_level, self.selected_object.exp_initial, self.selected_object.exp_increment) :
                self.set_current_exp_qline(self.calcul_max_exp_cur(self.cur_level, self.selected_object.exp_initial, self.selected_object.exp_increment))
            
            self.update()

            self.set_current_exp_qline(self.cur_exp)
            self.set_tot_exp_qline(self.calcul_exp_total(self.cur_level, self.cur_exp, self.selected_object.exp_initial, self.selected_object.exp_increment))

    def on_exp_tot_change(self):
        """
        Handles the event when the total experience changes.

        This method updates the total experience (`tot_exp`) by calling `get_total_exp()`.
        If the total experience exceeds the maximum experience of the selected object,
        it sets the current experience and level to their maximum values.
        Finally, it calls the `update()` method to refresh the state.

        Returns:
            None
        """
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
        """
        Handles the event when the multiplier value changes.

        This method is triggered when there is a change in the multiplier value.
        It updates the current multiplier by fetching the latest value and then
        calls the update method to reflect the changes.

        Returns:
            None
        """
        print("on_multiplier_change")
        self.cur_multiplier = self.get_current_multiplier()
        #self.set_current_multiplier_combobox(self.cur_multiplier)
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
        """
        Updates the selected object and related UI components.
        This method checks the type of the selected object and calls the appropriate
        update method for weapons or accessories. If the object type is unknown, it
        prints an error message. Additionally, it updates the remaining experience
        label and the component table in the UI.
        """
        if isinstance(self.selected_object, weapons.Weapon):
            self.update_weapon()
        elif isinstance(self.selected_object, accessories.Accessory):
            self.update_accessory()  # Assurez-vous d'avoir une méthode qui met à jour les accessoires
        else:
            print("Unknown object type")
        
        self.update_remaining_exp_label()
        self.update_component_table()

    def update_weapon(self):
        """
        Updates the weapon information and tab title based on the selected object.

        This method performs the following actions:
        1. Updates the weapon tab information using the selected object.
        2. Sets the weapon tab title using the selected object.

        Returns:
            None
        """
        self.update_weapon_tab_info(self.selected_object)
        self.set_weapon_tab_title(self.selected_object)

    def update_accessory(self):
        """
        Updates the accessory information and tab title based on the selected object.

        This method performs the following actions:
        1. Updates the accessory tab information using the selected object.
        2. Sets the accessory tab title using the selected object.

        Returns:
            None
        """
        self.update_accessory_tab_info(self.selected_object)
        self.set_accessory_tab_title(self.selected_object)

    def reset_current(self):
        """
        Resets the current level, experience points, and multiplier to their default values.
        
        This method sets the current level to 1, the current experience points to 0,
        and the current multiplier to 1 by updating the respective UI elements.
        """
        self.set_current_level_qline(1)
        self.set_current_exp_qline(0)
        self.set_current_multiplier_combobox(1)

    def update_weapon_tab_info(self, weapon):
        """
        Updates the weapon tab information with the provided weapon's details.
        Args:
            weapon (Weapon): An object containing the weapon's attributes.
        The method formats and updates the following weapon information:
            - Strength: Current strength based on the weapon's minimum strength, 
              strength increment, and the current level.
            - Magic: Current magic based on the weapon's minimum magic, 
              magic increment, and the current level.
            - Experience: Current experience and maximum experience for the level.
            - Shop: Shop name and the weapon's buy price in Gil.
            - Catalyst: The catalyst required for the weapon.
        The formatted information is then set to the weapon info label.
        """

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
        """
        Updates the accessory tab information with the provided accessory details.
        Args:
            accessory (Accessory): The accessory object containing the details to be displayed.
        The method formats and updates the following accessory information:
            - Current HP based on the accessory's minimum value and increment per level.
            - Current experience and maximum experience required for the next level.
            - Shop information including the shop name and buy price in Gil.
            - Synthesis effect level 1.
            - Catalyst required for the accessory.
        The formatted information is then set to the accessory info label using the 
        set_accessory_info_label method.
        """
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
        """
        Updates the label displaying the remaining experience points (EXP) required before reaching the next star level.
        This method calculates the remaining EXP based on the current level and experience points of the selected object.
        It handles the calculation differently if the current level is 1 or higher.
        - If the current level is 1, the remaining EXP is calculated as the difference between the maximum EXP and the current EXP.
        - If the current level is higher than 1, the method calculates the total gained EXP up to the current level and subtracts it from the maximum EXP.
        The result is then displayed in the `remaining_exp_label`.
        Args:
            None
        Returns:
            None
        """
        print("update_remaining_exp_label")

        if self.level_line_edit.text() == "1" :
            self.exp_req_before_star = self.selected_object.exp_max - self.cur_exp
        else :
            total_gained_exp = 0
            for i in range(int(self.level_line_edit.text()) -1 ):
                total_gained_exp += self.selected_object.exp_initial + self.selected_object.exp_increment * i
            exp_already_gained_w_level = self.selected_object.exp_initial + self.selected_object.exp_increment * (int(self.level_line_edit.text()) - 1)
            print(f"exp_already_gained_w_level: {exp_already_gained_w_level}")
            self.exp_req_before_star = self.selected_object.exp_max - self.calcul_exp_total(self.cur_level, self.cur_exp, self.selected_object.exp_initial, self.selected_object.exp_increment)

        self.remaining_exp_label.setText(f"{self.exp_req_before_star}")

    def update_component_table(self):
        """
        Updates the component table with the latest electrical components.
        This method updates the table by adding rows for the latest electrical components
        from the `electric_components_list`. It ensures that there are enough rows in the
        table and updates each row with the corresponding component data. After updating
        the table, it also updates the minimum cost.
        Args:
            None
        Returns:
            None
        """
        print("update_table")
        nb_row = 5

        # Mettre à jour le tableau avec les composants électriques
        for row, component in enumerate(self.electric_components_list[-nb_row:]):
            self.add_row_if_not_exists(row)
            self.update_row(component, row)

        self.update_min_cost()

    def update_row(self, component, row):
        """
        Updates the specified row in the table with the component's name, 
        the number required, and the total gils.

        Args:
            component (Component): The component object containing the name and other details.
            row (int): The row index in the table to be updated.

        Returns:
            None
        """
        self.update_column(component.name, row, 0)
        number_required = math.ceil(self.calculate_number_required(component))
        self.update_column(str(number_required), row, 1)
        gils = math.ceil(self.calculate_gils(number_required, component))
        self.update_column(str(gils), row, 2)

    def update_weapons(self):
        """
        Updates the weapon selection based on the selected character.
        This method retrieves the currently selected character from the character combo box,
        fetches the corresponding weapons for that character, and updates the weapon combo box
        with the available weapons. It also updates the character image based on the selected character.
        Returns:
            None
        """
        character_name = self.character_combo_box.currentText()
        print(f"Selected Character_weapon: {character_name}")
        weapons = self.weapons_by_character.get(character_name, [])
        self.weapon_combo_box.clear()
        self.weapon_combo_box.addItems([weapon.name for weapon in weapons])

        self.update_character_image(character_name)

    def update_accessories_image(self):
        """
        Updates the accessories image for the character.

        This method updates the character image by calling the 
        `update_character_image` method with the argument "FFXIII_Characters".
        """
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
        """
        Updates the weapon information labels with the provided values.

        Args:
            strength (str): The strength value to display.
            magic (str): The magic value to display.
            experience (str): The experience value to display.
            catalyst (str): The catalyst value to display.
            shop (str): The shop value to display.
        """
        self.txt_info_strength.setText(strength)
        self.txt_info_magic.setText(magic)
        self.txt_info_experience.setText(experience)
        self.txt_info_catalyst.setText(catalyst)
        self.txt_info_shop.setText(shop)

    def set_accessory_info_label(self, hp, experience, synthesis, catalyst, shop):
        """
        Sets the accessory information labels with the provided values.

        Args:
            hp (str): The HP value to set.
            experience (str): The experience value to set.
            synthesis (str): The synthesis value to set.
            catalyst (str): The catalyst value to set.
            shop (str): The shop value to set.
        """
        self.txt_info_hp.setText(hp)
        self.txt_info_experience_accessory.setText(experience)
        self.txt_info_synthesis.setText(synthesis)
        self.txt_info_catalyst_accessory.setText(catalyst)
        self.txt_info_shop_accessory.setText(shop)

    def update_character_image(self, character):
        """
        Updates the character image displayed in the UI.

        This method takes the name of a character, constructs the path to the corresponding image file,
        and updates the character image label with the image if it exists. If the image does not exist,
        it prints an error message.

        Args:
            character (str): The name of the character whose image is to be displayed.

        Raises:
            None

        Side Effects:
            Updates the pixmap of the character_image_label with the new image if found.
            Prints an error message if the image is not found.
        """
        image_path = os.path.join('pics', f'{character}.png')
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            # Ajustement de la taille du pixmap pour s'assurer qu'il n'est pas redimensionné
            self.character_image_label.setPixmap(pixmap.scaled(self.character_image_label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            print(f"Image not found for character: {character}")

    def set_current_level_qline(self, level):
        """
        Sets the text of the level line edit widget to the specified level.

        Args:
            level (int): The level to set in the line edit widget.
        """
        self.level_line_edit.setText(str(level))

    def set_current_exp_qline(self, exp):
        """
        Sets the current experience value in the QLineEdit widget.

        Args:
            exp (int): The experience value to be set in the QLineEdit widget.
        """
        print(f"set_current_exp_qline: {exp}")
        self.exp_cur_line_edit.setText(str(exp))

    def set_tot_exp_qline(self, exp):
        """
        Sets the total experience value in the corresponding QLineEdit widget.

        Args:
            exp (int or float): The total experience value to be set in the QLineEdit widget.
        """
        print(f"set_tot_exp_qline: {exp}")
        self.exp_tot_line_edit.setText(str(exp))

    def set_current_multiplier_combobox(self, multiplier):
        """
        Sets the current text of the multiplier combo box to the given multiplier.

        Args:
            multiplier (int or float): The multiplier value to set in the combo box.
        """
        self.multiplier_combo_box.setCurrentText(str(multiplier))

    def update_column(self, text, row, column):
        """
        Updates the specified cell in the component table with the given text.

        Args:
            text (str): The text to set in the specified cell.
            row (int): The row index of the cell to update.
            column (int): The column index of the cell to update.
        """
        item = QTableWidgetItem(text)
        self.component_table.setItem(row, column, item)

    def update_min_cost(self):
        """
        Updates the minimum cost in the component table by highlighting the row with the minimum cost.
        This method performs the following steps:
        1. Sets a light green color with 50% opacity for highlighting.
        2. Finds the minimum cost from the third column of the component table.
        3. Iterates through each row of the component table:
            - Retrieves the cost from the third column.
            - Creates a new table widget item with the current text.
            - Sets the background color to light green if the cost is the minimum cost, otherwise sets it to white.
            - Updates the item in the table with the new item.
        Note:
            This method assumes that the component table has at least one row and that the third column contains integer values.
        """
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
        """
        Adds a new row to the component table if the specified row index does not exist.

        Args:
            row (int): The index of the row to check and potentially add.
        """
        if row >= self.component_table.rowCount():
            self.component_table.insertRow(self.component_table.rowCount())     

    ##############################################
    # Calculation methods
    ##############################################

    def calculate_number_required(self, component):
        """
        Calculate the number of components required to reach the desired experience points.

        Args:
            component (Component): The component object which contains the experience points provided by the component.

        Returns:
            float: The number of components required.
        """
        number_required = (self.exp_req_before_star/float(self.multiplier_combo_box.currentText())) / (component.exp)
        return number_required

    def calculate_gils(self, number_required, component):
        """
        Calculate the total gils required to buy a given number of components.

        Args:
            number_required (int): The number of components required.
            component (Component): The component object which contains the buy price.

        Returns:
            int: The total gils required to buy the specified number of components.
        """
        gils = number_required * component.buy_price
        return gils

    def calcul_max_exp_cur(self, level, exp_initial, exp_increment):
        """
        Calculate the maximum experience required for the current level.

        Args:
            level (int): The current level of the character.
            exp_initial (int): The initial experience required at level 1.
            exp_increment (int): The experience increment per level.

        Returns:
            int: The maximum experience required for the current level.
        """
        max_exp_cur = exp_initial + exp_increment * (level - 1)
        return max_exp_cur
    
    def calcul_exp_total(self, level, exp, exp_initial, exp_increment):
        """
        Calculate the total experience required to reach a certain level.

        Args:
            level (int): The target level to reach.
            exp (int): The current experience points.
            exp_initial (int): The initial experience points required for the first level.
            exp_increment (int): The incremental experience points required for each subsequent level.

        Returns:
            int: The total experience points required to reach the specified level.
        """
        exp_total = 0
        for i in range(level - 1):
            exp_total += exp_initial + exp_increment * i
        exp_total += exp
        return exp_total
    
    def min_exp_per_level(self, level, exp_initial, exp_increment):
        """
        Calculate the minimum experience required to reach a given level.

        Args:
            level (int): The target level to reach.
            exp_initial (int): The initial experience required for the first level.
            exp_increment (int): The incremental experience required for each subsequent level.

        Returns:
            int: The total experience required to reach the specified level.
        """
        exp_total = 0
        for i in range(level - 1):
            exp_total += exp_initial + exp_increment * i
        print(f"exp_total: {exp_total}")
        return exp_total

    def exp_max_per_level(self, level, exp_initial, exp_increment):
        """
        Calculate the maximum experience points required to reach a given level.

        Args:
            level (int): The target level to reach.
            exp_initial (int): The initial experience points required for the first level.
            exp_increment (int): The incremental increase in experience points required for each subsequent level.

        Returns:
            int: The total experience points required to reach the specified level.
        """
        max_exp_lvl = 0
        for i in range(level):
            max_exp_lvl += exp_initial + exp_increment * i
        print(f"exp_total: {max_exp_lvl}")
        return max_exp_lvl

def main():
    """
    Main function to run the FF13 Calculator application.
    This function performs the following steps:
    1. Creates an instance of QApplication.
    2. Loads data from JSON files for weapons, accessories, electric components, and organic components.
    3. Creates and displays the main window of the FF13 Calculator with the loaded data.
    4. Starts the application's main event loop.
    Returns:
        None
    """
    # create Application
    app = QApplication(sys.argv)

    # load files
    weapons_data = weapons.JsonLoader.load()
    accessories_data = accessories.JsonLoader.load()
    electric_components_data = electric_components.JsonLoader.load()
    organic_components_data = organic_components.JsonLoader.load()

    # create main window
    calculator = FF13Calculator(weapons_data,
                                accessories_data,
                                electric_components_data,
                                organic_components_data)
    calculator.show()

    # start main loop
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
