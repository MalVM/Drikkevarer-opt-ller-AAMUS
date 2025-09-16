import sys
import pandas as pd
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QLabel, QTextEdit, QPushButton,
    QFileDialog, QComboBox, QMessageBox
)
from PyQt5.QtWidgets import QDateEdit
from PyQt5.QtCore import QDate

class DrinkSalesChecker(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Aalborg Musikforening - Drikkevare beregner")
        self.setGeometry(100, 100, 800, 600)

        self.df = None  # CSV data


        # Start date
        self.beforedate = QDateEdit(self)
        self.beforedate.setDisplayFormat("dd/MM/yyyy")  # shows day/month/year
        self.beforedate.setDate(QDate.currentDate())  # default to today
        self.beforedate.move(50, 50)
        self.beforedate.setFixedSize(200, 30)

        # End date
        self.today = QDateEdit(self)
        self.today.setDisplayFormat("dd/MM/yyyy")
        self.today.setDate(QDate.currentDate())
        self.today.move(300, 50)
        self.today.setFixedSize(200, 30)

        # --- Drink sold counts ---
        self.sodacount_label = QLabel("Antal sodavand solgt:", self)
        self.sodacount_label.setFixedWidth(150)
        self.sodacount_label.move(50, 100)
        self.sodacount_input = QTextEdit(self)
        self.sodacount_input.setFixedSize(100, 30)
        self.sodacount_input.move(200, 100)

        self.beercount_label = QLabel("Antal øl solgt:", self)
        self.beercount_label.move(50, 140)
        self.beercount_input = QTextEdit(self)
        self.beercount_input.setFixedSize(100, 30)
        self.beercount_input.move(200, 140)

        self.energycount_label = QLabel("Antal energidrink solgt:", self)
        self.energycount_label.setFixedWidth(150)
        self.energycount_label.move(50, 180)
        self.energycount_input = QTextEdit(self)
        self.energycount_input.setFixedSize(100, 30)
        self.energycount_input.move(200, 180)

        # --- Prices ---
        self.prices = {"soda": 8, "beer": 10, "energy": 15}

        # --- CSV import ---
        self.load_button = QPushButton("Indlæs CSV", self)
        self.load_button.move(50, 230)
        self.load_button.clicked.connect(self.load_csv)

        self.date_column_label = QLabel("Vælg datokolonne:", self)
        self.date_column_label.move(50, 270)
        self.date_column_label.setFixedSize(400, 30)
        self.date_column_dropdown = QComboBox(self)
        self.date_column_dropdown.move(200, 270)
        self.date_column_dropdown.setFixedSize(300, 30)

        self.amount_column_label = QLabel("Vælg beløbskolonne:", self)
        self.amount_column_label.move(50, 310)
        self.amount_column_label.setFixedSize(400, 30)
        self.amount_column_dropdown = QComboBox(self)
        self.amount_column_dropdown.move(200, 310)
        self.amount_column_dropdown.setFixedSize(300, 30)

        # --- Compare button ---
        self.compare_button = QPushButton("Beregn og sammenlign", self)
        self.compare_button.setFixedWidth(200)
        self.compare_button.move(50, 360)
        self.compare_button.clicked.connect(self.compare_earnings)

        # --- Result ---
        self.result_label = QLabel("", self)
        self.result_label.move(50, 420)
        self.result_label.setFixedSize(1000, 60)
        self.result_label.setWordWrap(True)

    def load_csv(self):
        path, _ = QFileDialog.getOpenFileName(self, "Vælg CSV-fil", "", "CSV Files (*.csv)")
        if path:
            try:
                self.df = pd.read_csv(path, sep=";")
                self.date_column_dropdown.clear()
                self.amount_column_dropdown.clear()
                self.date_column_dropdown.addItems(self.df.columns)
                self.amount_column_dropdown.addItems(self.df.columns)
                QMessageBox.information(self, "CSV indlæst", "CSV er indlæst succesfuldt!")
            except Exception as e:
                QMessageBox.critical(self, "Fejl", f"Kunne ikke indlæse CSV:\n{e}")

    def compare_earnings(self):
        if self.df is None:
            QMessageBox.warning(self, "Fejl", "Indlæs venligst en CSV først.")
            return

        try:
            # Dates
            start_date = self.beforedate.date().toPyDate()  # returns a datetime.date
            end_date = self.today.date().toPyDate()
            if pd.isna(start_date) or pd.isna(end_date):
                raise ValueError("Ugyldige datoer!")

            # Drink counts
            sodas = int(self.sodacount_input.toPlainText() or 0)
            beers = int(self.beercount_input.toPlainText() or 0)
            energy = int(self.energycount_input.toPlainText() or 0)

            expected = sodas*self.prices["soda"] + beers*self.prices["beer"] + energy*self.prices["energy"]

            # CSV filtering
            date_col = self.date_column_dropdown.currentText()
            amount_col = self.amount_column_dropdown.currentText()
            self.df[date_col] = pd.to_datetime(self.df[date_col], dayfirst=True, errors='coerce')
            mask = (self.df[date_col] >= pd.to_datetime(start_date)) & \
                   (self.df[date_col] <= pd.to_datetime(end_date))
            filtered = self.df.loc[mask]

            # Only positive amounts (exclude fees)
            actual = filtered[amount_col].astype(str).str.replace(',', '.').astype(float)
            actual = actual[actual > 0].sum()

            diff = actual - expected
            self.result_label.setText(
                f"Forventet beløb: {expected:.2f} DKK | "
                f"Reelt beløb i CSV (minus fee): {actual:.2f} DKK | "
                f"Forskel: {diff:.2f} DKK"
            )

        except Exception as e:
            QMessageBox.critical(self, "Fejl", f"Kunne ikke beregne:\n{e}")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    win = DrinkSalesChecker()
    win.show()
    sys.exit(app.exec_())
