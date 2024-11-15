import sys
import numpy as np
from scipy import stats
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QTableWidget, QTableWidgetItem, QMessageBox
)
from PyQt5.QtGui import QDoubleValidator
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

class PriceCalculatorApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Calculateur de Prix Dégressif")
        self.quantities = []
        self.prices = []
        self.init_ui()

    def init_ui(self):
        # Configuration du layout principal
        layout = QVBoxLayout()

        # --- Section Tableau des Données ---
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Quantité (Q)", "Prix (P) (€)"])
        layout.addWidget(QLabel("Données de Quantité et Prix:"))
        layout.addWidget(self.table)

        # --- Section Ajout de Nouvelles Données ---
        data_entry_layout = QHBoxLayout()
        
        # Validation pour accepter uniquement des nombres positifs
        double_validator = QDoubleValidator(bottom=0.0001, top=1e12, decimals=4)

        self.quantity_input = QLineEdit()
        self.quantity_input.setPlaceholderText("Quantité")
        self.quantity_input.setValidator(double_validator)
        data_entry_layout.addWidget(QLabel("Quantité:"))
        data_entry_layout.addWidget(self.quantity_input)

        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("Prix (€)")
        self.price_input.setValidator(double_validator)
        data_entry_layout.addWidget(QLabel("Prix (€):"))
        data_entry_layout.addWidget(self.price_input)

        self.add_button = QPushButton("Ajouter les données")
        self.add_button.clicked.connect(self.add_data)
        data_entry_layout.addWidget(self.add_button)

        layout.addLayout(data_entry_layout)

        # --- Section Estimation du Prix ---
        estimate_layout = QHBoxLayout()
        
        self.estimate_input = QLineEdit()
        self.estimate_input.setPlaceholderText("Quantité à estimer")
        self.estimate_input.setValidator(double_validator)
        estimate_layout.addWidget(QLabel("Quantité à estimer:"))
        estimate_layout.addWidget(self.estimate_input)

        self.estimate_button = QPushButton("Estimer le Prix")
        self.estimate_button.clicked.connect(self.estimate_price)
        estimate_layout.addWidget(self.estimate_button)

        self.result_label = QLabel("Prix estimé : ")
        estimate_layout.addWidget(self.result_label)

        # --- Bouton Reset ---
        self.reset_button = QPushButton("Reset")
        self.reset_button.clicked.connect(self.reset_app)
        estimate_layout.addWidget(self.reset_button)

        layout.addLayout(estimate_layout)

        # --- Section Graphique ---
        self.figure = Figure()
        self.canvas = FigureCanvas(self.figure)
        layout.addWidget(QLabel("Visualisation des Données et du Modèle:"))
        layout.addWidget(self.canvas)

        self.setLayout(layout)

    def add_data(self):
        try:
            quantity = float(self.quantity_input.text())
            price = float(self.price_input.text())

            if quantity <= 0 or price <= 0:
                raise ValueError

            self.quantities.append(quantity)
            self.prices.append(price)

            # Ajouter les données au tableau
            row_position = self.table.rowCount()
            self.table.insertRow(row_position)
            self.table.setItem(row_position, 0, QTableWidgetItem(str(quantity)))
            self.table.setItem(row_position, 1, QTableWidgetItem(f"{price:.2f}"))

            # Effacer les champs d'entrée
            self.quantity_input.clear()
            self.price_input.clear()

            # Mettre à jour le graphique
            self.update_plot()

        except ValueError:
            QMessageBox.warning(self, "Erreur d'Entrée", "Veuillez entrer des nombres positifs valides pour la quantité et le prix.")

    def estimate_price(self):
        if len(self.quantities) < 2:
            QMessageBox.warning(self, "Données Insuffisantes", "Veuillez entrer au moins deux points de données pour effectuer une estimation.")
            return
        try:
            quantity_to_estimate = float(self.estimate_input.text())
            if quantity_to_estimate <= 0:
                raise ValueError

            # Calcul des logarithmes
            ln_quantities = np.log(self.quantities)
            ln_prices = np.log(self.prices)

            # Régression linéaire
            slope, intercept, r_value, p_value, std_err = stats.linregress(ln_quantities, ln_prices)

            a = slope
            k = np.exp(intercept)

            estimated_price = k * (quantity_to_estimate ** a)

            self.result_label.setText(f"Prix estimé : {estimated_price:.2f} €")

            # Mettre à jour le graphique
            self.update_plot()

        except ValueError:
            QMessageBox.warning(self, "Erreur d'Entrée", "Veuillez entrer une quantité valide pour l'estimation.")

    def reset_app(self):
        reply = QMessageBox.question(
            self, 'Confirmer la Réinitialisation',
            'Êtes-vous sûr de vouloir réinitialiser l\'application ? Toutes les données seront effacées.',
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            # Effacer les listes de données
            self.quantities.clear()
            self.prices.clear()

            # Effacer le tableau
            self.table.setRowCount(0)

            # Effacer les champs d'entrée
            self.quantity_input.clear()
            self.price_input.clear()
            self.estimate_input.clear()

            # Réinitialiser le label du résultat
            self.result_label.setText("Prix estimé : ")

            # Effacer le graphique
            self.figure.clear()
            self.canvas.draw()

    def update_plot(self):
        self.figure.clear()
        ax = self.figure.add_subplot(111)

        if len(self.quantities) == 0:
            self.canvas.draw()
            return

        # Tracer les données réelles
        ax.scatter(self.quantities, self.prices, color='blue', label='Données réelles')

        if len(self.quantities) >= 2:
            # Calcul des logarithmes
            ln_quantities = np.log(self.quantities)
            ln_prices = np.log(self.prices)

            # Régression linéaire
            slope, intercept, r_value, p_value, std_err = stats.linregress(ln_quantities, ln_prices)

            a = slope
            k = np.exp(intercept)

            # Générer des points pour la courbe ajustée
            quantities_fit = np.linspace(min(self.quantities), max(self.quantities), 100)
            prices_fit = k * (quantities_fit ** a)

            ax.plot(quantities_fit, prices_fit, color='red', label=f'Modèle ajusté : P = {k:.2f} * Q^{a:.2f}')

            # Calcul du R²
            r_squared = r_value ** 2
            ax.text(0.05, 0.95, f"$R^2$ = {r_squared:.4f}", transform=ax.transAxes, fontsize=10,
                    verticalalignment='top')

        ax.set_xlabel('Quantité (Q)')
        ax.set_ylabel('Prix (P) (€)')
        ax.set_title('Modèle de Puissance')
        ax.legend()
        ax.grid(True)

        self.canvas.draw()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = PriceCalculatorApp()
    window.resize(800, 600)  # Optionnel: définir une taille initiale
    window.show()
    sys.exit(app.exec_())
