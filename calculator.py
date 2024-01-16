import sys

from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout, QComboBox, QLabel, QHBoxLayout, QTabWidget, QTableWidget, QTableWidgetItem, QLineEdit, QFormLayout, QFrame
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QSize

import Weapon as weapon
import Accessories as accessories


class FF13Calculator(QWidget):
    def __init__(self, weapons_by_character, accessories_list):
        super().__init__()
        self.weapons_by_character = weapons_by_character
        self.accessories_list = accessories_list

        self.character_image_label = QLabel(self)
        self.character_combo_box = QComboBox()
        self.weapon_combo_box = QComboBox()
        self.level_line_edit = QLineEdit("1")
        self.exp_line_edit = QLineEdit("0")
        self.remaining_exp_label = QLabel()
        self.info_label = QLabel("Strength:\nMagic:\nExperience:\nCatalyst:\nShop:")
        self.multiplier_combo_box = QComboBox()
        self.component_table = QTableWidget()

        self.initUI()

    def initUI(self):
        # Configuration principale de la fenêtre

        # Création du layout principal
        mainLayout = QHBoxLayout(self)
        
        # Configuration des différentes parties de l'interface
        self.setup_left_part(mainLayout)
        self.setup_central_part(mainLayout)
        self.setup_right_part(mainLayout)
    
        # Configuration de la fenêtre
        self.setLayout(mainLayout)
        self.setWindowTitle('FF13 Weapon Calculator')
        self.setGeometry(50, 50, 1300, 800)
        self.show()

##############################################
# Méthodes pour composer l'interface en trois parties (gauche, centre, droite)
##############################################

    def setup_left_part(self, layout):
        self.character_image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.character_image_label.setFixedSize(500, 600)
        layout.addWidget(self.character_image_label)

    def setup_central_part(self, layout):
        # Création du layout vertical pour la partie centrale
        central_layout = QVBoxLayout()

        # Création et configuration des onglets
        tab_widget = QTabWidget()
        weapon_tab = self.setup_weapon_tab() # Création de l'onglet des armes

        # Ajout des onglets
        tab_widget.addTab(weapon_tab, "Weapons")

        central_layout.addWidget(tab_widget)

        tab_widget.setFixedHeight(150) # Hauteur fixe pour les onglets

        # Ajout du formulaire sous les onglets
        self.setup_info_form(central_layout)

        # Ajout des informations supplémentaires sous le formulaire
        self.setup_additional_info(central_layout)

        # Ajout des onglets au layout principal
        layout.addLayout(central_layout)

    def setup_right_part(self, layout):
        # ... configuration du multiplicateur et du QTableWidget ...
        multiplier_frame = QFrame()
        multiplier_frame_layout = QVBoxLayout(multiplier_frame)
        multiplier_frame_layout.addLayout(self.create_multiplier_layout())
        multiplier_frame.setLayout(multiplier_frame_layout)
        multiplier_frame.setFixedWidth(450)
        multiplier_frame.setFixedHeight(200)
        layout.addWidget(multiplier_frame)

##############################################
# Méthodes pour configurer les onglets et le formulaire 
##############################################
    def setup_weapon_tab(self):
        weapon_tab = QWidget()
        weapon_layout = QVBoxLayout()

        self.character_combo_box.addItems(self.weapons_by_character.keys())
        self.character_combo_box.currentIndexChanged.connect(self.update_weapons)
        weapon_layout.addWidget(self.character_combo_box)

        self.weapon_combo_box.currentIndexChanged.connect(self.on_weapon_selection_changed)
        weapon_layout.addWidget(self.weapon_combo_box)

        weapon_tab.setLayout(weapon_layout)
        self.update_weapons()

        return weapon_tab

    def setup_info_form(self, layout):
        # Création d'un layout de formulaire pour les informations supplémentaires
        form_layout = QFormLayout()

        # QLineEdit pour le niveau actuel
        self.level_line_edit.textChanged.connect(self.on_level_or_exp_change)
        form_layout.addRow("Current Level", self.level_line_edit)

        # QLineEdit pour l'expérience actuelle
        self.exp_line_edit.textChanged.connect(self.on_level_or_exp_change)
        form_layout.addRow("Current Experience", self.exp_line_edit)

        # QLabel pour l'expérience restante
        form_layout.addRow("Experience Required for ★", self.remaining_exp_label)

        # Ajout du layout du formulaire au layout des onglets
        layout.addLayout(form_layout)

    def setup_additional_info(self, layout):
        # QLabel pour afficher les informations supplémentaires
        layout.addWidget(self.info_label)
        print("setup_additional_info")
        #update_info_label(self, strength, magic, experience, catalyst, shop):

##############################################
# Méthodes pour configurer le multiplicateur et le tableau
##############################################
    def create_multiplier_layout(self):
        # Création et retour du layout du multiplicateur et du tableau
        multiplier_layout = QVBoxLayout()
        
        # Layout pour le multiplicateur
        multiplier_layout = QVBoxLayout()
        multiplier_label = QLabel("Current Multiplier")
        multiplier_layout.addWidget(multiplier_label)

        multipliers = ["1", "1.25", "1.50", "1.75", "2", "2.25", "2.5", "2.75", "3"]
        self.multiplier_combo_box.addItems(multipliers)
        default_multiplier_index = self.multiplier_combo_box.findText("3")
        if default_multiplier_index >= 0:
            self.multiplier_combo_box.setCurrentIndex(default_multiplier_index)
        multiplier_layout.addWidget(self.multiplier_combo_box)

        # Connecter le signal currentIndexChanged à la méthode de gestion
        self.multiplier_combo_box.currentIndexChanged.connect(self.on_multiplier_change)
        
        # Création du QTableWidget
        self.component_table.setRowCount(4)  # Nombre de lignes
        self.component_table.setColumnCount(3)  # Nombre de colonnes

        # Définir les en-têtes de colonnes
        self.component_table.setHorizontalHeaderLabels(["Name", "Number Required", "Cost(Gil)"])

        # Ajustement de la largeur des colonnes
        self.component_table.setColumnWidth(0, 125)  # Largeur pour "Name"
        self.component_table.setColumnWidth(1, 125)  # Largeur pour "Number Required"
        self.component_table.setColumnWidth(2, 125)  # Largeur pour "Cost(Gil)"

        # Ajout des données au tableau
        components = ["Superconductor", "Perfect Conductor", "Particle Accelerator", "Ultracompact Reactor"]
        for row, name in enumerate(components):
            self.component_table.setItem(row, 0, QTableWidgetItem(name))
            # Les autres cellules sont laissées vides pour l'instant
            self.component_table.setItem(row, 1, QTableWidgetItem(""))  # Number Required
            self.component_table.setItem(row, 2, QTableWidgetItem(""))  # Cost(Gil)

        # Calculer et fixer la hauteur totale de la table
        header_height = self.component_table.horizontalHeader().height()
        row_height = self.component_table.rowHeight(0)  # Hauteur d'une ligne
        extra_padding = 10  # Ajouter un peu d'espace supplémentaire pour les marges
        # Calculez la hauteur totale en incluant l'en-tête et l'espace supplémentaire
        table_height = header_height + (row_height * self.component_table.rowCount()) + extra_padding
        self.component_table.setFixedHeight(table_height)

        # Ajout du tableau au layout du multiplicateur
        multiplier_layout.addWidget(self.component_table)
        return multiplier_layout


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
        experience_info = f"Current: {weapon.exp_current}, Max: {weapon.exp_max}"

        # Update the weapon information
        info_text = f"Strength: {strength_info}\n" \
                    f"Magic: {magic_info}\n" \
                    f"Experience: {experience_info}\n" \
                    f"Catalyst: {weapon.catalyst}\n" \
                    f"Shop: {weapon.shop}"
        #self.info_label.setText(info_text)

        # Appel de la méthode pour mettre à jour remaining_exp_label
        exp_req_before_star = weapon.exp_max #- self.exp_line_edit.currentText()
        self.update_remaining_exp_label(exp_req_before_star)

    def update_remaining_exp_label(self, exp_req_before_star):
        print("update_remaining_exp_label")
#        self.remaining_exp_label.setText(f"Experience Required for ★: {exp_req_before_star}")
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
        info_text = f"Strength: {strength}\n" \
                    f"Magic: {magic}\n" \
                    f"Experience: {experience}\n" \
                    f"Catalyst: {catalyst}\n" \
                    f"Shop: {shop}"
        self.info_label.setText(info_text)

    def update_character_image(self, character):
        image_path = f'pics/{character}.png'  # Assurez-vous que le chemin est correct
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            # Ajustement de la taille du pixmap pour s'assurer qu'il n'est pas redimensionné
            self.character_image_label.setPixmap(pixmap.scaled(self.character_image_label.size(), Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        else:
            print(f"Image not found for character: {character}")

def main():
    app = QApplication(sys.argv)
    weapons_data = weapon.weapons_by_character
    accessories_data = accessories.accessories_list
    calculator  = FF13Calculator(weapons_data, accessories_data)
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
