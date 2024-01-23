#!/usr/bin/python
# -*- coding: utf-8 -*-
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QVBoxLayout, QPushButton, QWidget, QLabel, QStackedWidget, QHBoxLayout, QTableWidgetItem
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QPixmap
import pandas as pd
import numpy as np
import openpyxl


import Topsis, RSM, Uta, excel, Results
from data_manager import DataManager


class MainScreen(QWidget):
    def __init__(self, stacked_widget, data_manager: DataManager):
        super().__init__()
        self.data_manager = data_manager

        self.layout = QHBoxLayout()

        right_layout = QVBoxLayout()
        left_layout = QVBoxLayout()

        self.topsis_button = QPushButton(self)
        self.topsis_button.setStyleSheet("image: url(./grafika/but_topsis.png);"
                                         "width: 120px;"
                                         "height: 40px;"
                                         "background-color: transparent;")
        self.topsis_button.clicked.connect(lambda: stacked_widget.setCurrentIndex(1))
        left_layout.addWidget(self.topsis_button)

        self.rsm_button = QPushButton(self)
        self.rsm_button.setStyleSheet("image: url(./grafika/but_rsm.png);"
                                      "width: 120px;"
                                      "height: 40px;"
                                      "background-color: transparent;")
        self.rsm_button.clicked.connect(lambda: stacked_widget.setCurrentIndex(2))
        left_layout.addWidget(self.rsm_button)

        self.uta_button = QPushButton(self)
        self.uta_button.setStyleSheet("image: url(./grafika/but_uta.png);"
                                      "width: 120px;"
                                      "height: 40px;"
                                      "background-color: transparent;")
        self.uta_button.clicked.connect(lambda: stacked_widget.setCurrentIndex(3))
        left_layout.addWidget(self.uta_button)

        self.show_excel_button = QPushButton(self)
        self.show_excel_button.setStyleSheet("image: url(./grafika/but_dane.png);"
                                             "width: 120px;"
                                             "height: 40px;"
                                             "background-color: transparent;")
        self.show_excel_button.clicked.connect(lambda: stacked_widget.setCurrentIndex(4))
        left_layout.addWidget(self.show_excel_button)

        self.results_button = QPushButton(self)
        self.results_button.setStyleSheet("image: url(./grafika/but_wyniki.png);"
                                          "width: 120px;"
                                          "height: 40px;"
                                          "background-color: transparent;")
        self.results_button.clicked.connect(lambda: stacked_widget.setCurrentIndex(5))
        left_layout.addWidget(self.results_button)

        self.layout.addLayout(left_layout, 1)
        self.layout.addLayout(right_layout, 3)

        self.setLayout(self.layout)
        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)



def main():
    icon_path = "./grafika/szur.png"

    tlo = """
        QMainWindow {
            background-image: url(./grafika/main.png);
            background-repeat: no-repeat;
            background-position: center;
        }
    """

    app = QApplication(sys.argv)
    app.setStyleSheet(tlo)
    main_window = QMainWindow()
    main_window.setWindowTitle("Kerfus")
    main_window.setGeometry(0, 0, 1200, 800)

    data_manager = DataManager()

    stacked_widget = QStackedWidget(main_window)

    main_screen = MainScreen(stacked_widget, data_manager)
    screen_topsis = Topsis.ScreenTopsis(data_manager)
    screen_rsm = RSM.ScreenRSM(data_manager)
    screen_uta = Uta.ScreenUTA(data_manager)
    screen_excel = excel.ExcelTableScreen(data_manager)
    screen_results = Results.ScreenResults(data_manager)

    stacked_widget.addWidget(main_screen)
    stacked_widget.addWidget(screen_topsis)
    stacked_widget.addWidget(screen_rsm)
    stacked_widget.addWidget(screen_uta)
    stacked_widget.addWidget(screen_excel)
    stacked_widget.addWidget(screen_results)

    main_window.setCentralWidget(stacked_widget)
    main_window.setWindowIcon(QIcon(icon_path))
    main_window.show()
    sys.exit(app.exec())



if __name__ == "__main__":
    main()