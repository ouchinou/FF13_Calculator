import sys
import os
from pathlib import Path

from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
from PyQt6 import uic

import weapons
import accessories


class FF13Calculator(QMainWindow):
    """This "window" is a QWidget. If it has no parent, it will appear as a free-floating window as we want."""

    def __init__(self, weapons_by_character, accessories_list, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # initialize UI from the QtDesigner UI file
        uic.loadUi(Path(__file__).parent / "gui" / "FF13_Calculator.ui", self)

        self.weapons_by_character = weapons_by_character
        self.accessories_list = accessories_list

        # initialize callbacks
        self.init_callbacks()

        # update GUI from loaded files
        self.initialize_gui()

        # finalize UI
        self.finalize_UI()
        self.update_weapons()

    def init_callbacks(self):
        # character/weapon
        self.character_combo_box.currentIndexChanged.connect(self.update_weapons)
        self.weapon_combo_box.currentIndexChanged.connect(self.on_weapon_selection_changed)

        # info form
        self.level_line_edit.textChanged.connect(self.on_level_or_exp_change)
        self.exp_line_edit.textChanged.connect(self.on_level_or_exp_change)

        # additional info

        # multiplier
        self.multiplier_combo_box.currentIndexChanged.connect(self.on_multiplier_change)

    def initialize_gui(self):
        # fill combo boxes
        self.character_combo_box.addItems(self.weapons_by_character.keys())

    def finalize_UI(self):
        # Ajustement de la largeur des colonnes
        self.component_table.setColumnWidth(0, 125)  # Largeur pour "Name"
        self.component_table.setColumnWidth(1, 125)  # Largeur pour "Number Required"
        self.component_table.setColumnWidth(2, 125)  # Largeur pour "Cost(Gil)"

    ##############################################
    # Méthodes pour gérer les événements
    ##############################################

    def on_weapon_selection_changed(self):
        weapon_name = self.weapon_combo_box.currentText()
        print(f"Selected Weapon: {weapon_name}")
        selected_weapon = self.get_selected_weapon(weapon_name)
        if selected_weapon:
            self.update_weapon_info(selected_weapon)

    def on_level_or_exp_change(self):
        print("on_level_or_exp_change")
        # Gérer le changement de texte ici
        level = self.level_line_edit.text()
        exp = self.exp_line_edit.text()
        print(f"Level: {level}")
        print(f"EXP: {exp}")
        self.update_remaining_exp_label(100)

    def on_multiplier_change(self):
        # Gérer le changement de sélection ici
        selected_multiplier = self.multiplier_combo_box.currentText()
        print(f"Selected Multiplier: {selected_multiplier}")
        self.update_table(selected_multiplier)

    ##############################################
    # Méthodes pour gérer les données
    ##############################################
    def get_selected_weapon(self, weapon_name):
        selected_weapon = None
        for character_weapons in self.weapons_by_character.values():
            for w in character_weapons:
                if w.name == weapon_name:
                    selected_weapon = w
                    break
            if selected_weapon:
                break
        return selected_weapon

    def get_weapon_title(self, weapon):
        """Génère et retourne le titre de l'arme basé sur le niveau actuel."""
        current_lv = self.level_line_edit.text()  # Récupère le niveau actuel de l'interface
        title = f"{weapon.name} {current_lv}/{weapon.max_lv}"
        return title

    ##############################################
    # Méthodes pour mettre à jour les données
    ##############################################
    def update_weapon_info(self, weapon):
        # Format the required information from the weapon object
        strength_info = f"{weapon.str_min} - {weapon.str_max}"
        magic_info = f"{weapon.mag_min} - {weapon.mag_max}"
        experience_info = f"Current: {weapon.exp_current:_}, Max: {weapon.exp_max:_}"

        # Update the weapon information
        self.update_info_label(strength=strength_info,
                               magic=magic_info,
                               experience=experience_info,
                               catalyst=weapon.catalyst,
                               shop=weapon.shop)

        # Appel de la méthode pour mettre à jour remaining_exp_label
        exp_req_before_star = weapon.exp_max  # - self.exp_line_edit.currentText()
        self.update_remaining_exp_label(exp_req_before_star)

    def update_remaining_exp_label(self, exp_req_before_star):
        print("update_remaining_exp_label")
        self.remaining_exp_label.setText(f"{exp_req_before_star}")

    def update_table(self, multiplier):
        pass

    def update_weapons(self):
        character = self.character_combo_box.currentText()
        print(f"Selected Character: {character}")
        weapons = self.weapons_by_character.get(character, [])
        self.weapon_combo_box.clear()
        self.weapon_combo_box.addItems([weapon.name for weapon in weapons])

        self.update_character_image(character)

    def update_info_label(self, strength, magic, experience, catalyst, shop):
        """Mettre à jour le label avec les informations calculées."""
        self.txt_info_strength.setText(strength)
        self.txt_info_magic.setText(magic)
        self.txt_info_experience.setText(experience)
        self.txt_info_catalyst.setText(catalyst)
        self.txt_info_shop.setText(shop)

    def update_character_image(self, character):
        image_path = os.path.join('pics', f'{character}.png')
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            # Ajustement de la taille du pixmap pour s'assurer qu'il n'est pas redimensionné
            self.character_image_label.setPixmap(pixmap.scaled(self.character_image_label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            print(f"Image not found for character: {character}")


def main():
    # create Application
    app = QApplication(sys.argv)

    # load files
    weapons_data = weapons.JsonLoader.load()
    accessories_data = accessories.JsonLoader.load()

    # create main window
    calculator = FF13Calculator(weapons_data, accessories_data)
    calculator.show()

    # start main loop
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
