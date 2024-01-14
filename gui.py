import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QWidget, QLabel, QStackedWidget, QHBoxLayout, QTableWidgetItem
from PyQt6.QtCore import Qt
import pandas as pd
import numpy as np
import openpyxl


import Topsis, RSM, Uta, excel


class MainScreen(QWidget):
    def __init__(self, stacked_widget):
        super().__init__()

        self.layout = QVBoxLayout()

        self.label = QLabel("Main Screen")
        self.layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignHCenter)

        button_layout = QHBoxLayout()

        self.topsis_button = QPushButton("TOPSIS")
        self.topsis_button.clicked.connect(lambda: stacked_widget.setCurrentIndex(1))
        button_layout.addWidget(self.topsis_button)

        self.rsm_button = QPushButton("RSM")
        self.rsm_button.clicked.connect(lambda: stacked_widget.setCurrentIndex(2))
        button_layout.addWidget(self.rsm_button)

        self.uta_button = QPushButton("UTA")
        self.uta_button.clicked.connect(lambda: stacked_widget.setCurrentIndex(3))
        button_layout.addWidget(self.uta_button)

        button_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.layout.addLayout(button_layout)

        self.show_excel_button = QPushButton("Dane")
        self.show_excel_button.clicked.connect(lambda: self.show_excel_table(stacked_widget))
        self.layout.addWidget(self.show_excel_button)

        self.setLayout(self.layout)

        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def show_excel_table(self, stacked_widget):
        # Create and add ExcelTableScreen to stacked widget
        excel_table_screen = excel.ExcelTableScreen()
        stacked_widget.addWidget(excel_table_screen)
        stacked_widget.setCurrentIndex(stacked_widget.count() - 1)

        # Load Excel data when the screen is shown
        excel_table_screen.load_excel_data()
def main():
    app = QApplication(sys.argv)

    main_window = QMainWindow()
    main_window.setWindowTitle("Kerfus")
    main_window.setGeometry(100, 100, 1200, 900)

    stacked_widget = QStackedWidget(main_window)

    main_screen = MainScreen(stacked_widget)
    screen_topsis = Topsis.ScreenTopsis()
    screen_rsm = RSM.ScreenTopsis()
    screen_uta = Uta.ScreenTopsis()

    stacked_widget.addWidget(main_screen)
    stacked_widget.addWidget(screen_topsis)
    stacked_widget.addWidget(screen_rsm)
    stacked_widget.addWidget(screen_uta)

    main_window.setCentralWidget(stacked_widget)

    main_window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()