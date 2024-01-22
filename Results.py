from PyQt6.QtWidgets import QVBoxLayout, QLabel, QPushButton, QWidget, QCheckBox, QHBoxLayout, QTableView, QButtonGroup
from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QFormLayout, QDialog, QHeaderView, QLineEdit, QFileDialog, QMessageBox
from PyQt6.QtCore import Qt, QAbstractTableModel
from PyQt6.QtGui import QColor
import openpyxl
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import tabulate
from matplotlib.ticker import (MultipleLocator, AutoMinorLocator)
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas

import alg_RSM
from data_manager import DataManager
import a_star

class MatplotlibWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.canvas = FigureCanvas(plt.figure())
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.canvas.figure.patch.set_facecolor((0.27, 0.26, 0.33))
        self.setLayout(layout)


class KerfusTableModel(QAbstractTableModel):
    def __init__(self, kerfus_tab, parent=None):
        super().__init__(parent)
        self.data = kerfus_tab

    def rowCount(self, parent):
        return len(self.data)

    def columnCount(self, parent):
        return len(self.data[0])

    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            value = self.data[index.row()][index.column()]
            return str(value) if value is not None else ""  # Set empty string for None values
        return None


class ScreenResults(QWidget):
    def __init__(self, data_manager: DataManager):
        super().__init__()
        self.data_manager = data_manager
        self.data_manager.set_data("user_classes", None)
        self.data_manager.set_data("selection", [0, 1])

        self.layout = QHBoxLayout()  # Use QHBoxLayout instead of QVBoxLayout

        right_layout = QVBoxLayout()
        left_layout = QVBoxLayout()

        self.execute_button = QPushButton(self)
        self.execute_button.setStyleSheet("image: url(./grafika/but_rsm.png);"
                                          "width: 120px;"
                                          "height: 40px;"
                                          "margin: 0px;"
                                          "background-color: transparent")
        self.execute_button.clicked.connect(self.execute_algorithm)
        left_layout.addWidget(self.execute_button)


        self.back_button = QPushButton(self)
        self.back_button.setStyleSheet("image: url(./grafika/but_powrot.png);"
                                       "width: 120px;"
                                       "height: 40px;"
                                       "margin: 0px;"
                                       "background-color: transparent")
        self.back_button.clicked.connect(self.go_back)
        left_layout.addWidget(self.back_button)

        # Set left part width to 1/4th of the main window width

        # Right part (Matplotlib plot)
        self.matplotlib_widget = MatplotlibWidget(
            self.layout.parentWidget())  # Use the parent widget as the parent for MatplotlibWidget
        right_layout.addWidget(self.matplotlib_widget)  # Set right part width to 3/4th of the main window width

        self.kerfus_table = QTableView()

        stylesheet = "::section{Background-color:rgb(69, 67, 84);}"
        self.kerfus_table.horizontalHeader().setStyleSheet(stylesheet)

        stylesheet = "::section{Background-color:rgb(69, 67, 84);}"
        self.kerfus_table.verticalHeader().setStyleSheet(stylesheet)

        self.kerfus_table.setStyleSheet(
            "background-color: rgb(69, 67, 84); color: white;border:2px;border-style: none;")
        right_layout.addWidget(self.kerfus_table)

        self.layout.addLayout(left_layout, 1)
        self.layout.addLayout(right_layout, 3)

        self.setLayout(self.layout)

        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), QColor(69, 67, 84))  # You can set any color you want here
        self.setPalette(p)


    def go_back(self):
        self.parent().setCurrentIndex(0)


    def execute_algorithm(self):
        try:
            map_data = self.data_manager.get_data("map").copy()
            points_data = self.data_manager.get_data("points").copy()
            selection = self.data_manager.get_data("selection")
            if self.data_manager.get_data("is_user"):
                user_classes = self.data_manager.get_data("user_classes")
            else:
                user_classes = None

            shop = map_data.values.T
            arr = shop.copy()
            points = points_data.values

            points_ref = [(x, y) for x, y in points[:, :2]]

            base_coords = np.argwhere(arr == 6)
            base_coords = tuple(base_coords[0])
            arr[base_coords] = 0

            kerfus_tabT = self.data_manager.get_data("TopsisData")
            kerfusT = kerfus_tabT[1:].astype(float)
            kerfusT = np.delete(kerfusT, 0, axis=1)
            kerfusT = np.append([[base_coords[0], base_coords[1], 0, 0, 0, 0, 0]], kerfusT, axis=0)

            kerfus_tabR = self.data_manager.get_data("RSMData")
            kerfusR = kerfus_tabR[1:].astype(float)
            kerfusR = np.delete(kerfusR, 0, axis=1)
            kerfusR = np.append([[base_coords[0], base_coords[1], 0, 0, 0, 0, 0]], kerfusR, axis=0)

            kerfus_tabU = self.data_manager.get_data("UtaData")
            kerfusU = kerfus_tabU[1:].astype(float)
            kerfusU = np.delete(kerfusU, 0, axis=1)
            kerfusU = np.append([[base_coords[0], base_coords[1], 0, 0, 0, 0, 0]], kerfusU, axis=0)

            ax = self.matplotlib_widget.canvas.figure.add_subplot(111)

            shelves = np.argwhere(arr == 1)
            entrance = np.argwhere(arr == 2)
            exit = np.argwhere(arr == 3)
            bread = np.argwhere(arr == 4)
            meat = np.argwhere(arr == 5)

            ax.scatter(points[:, 0], points[:, 1], c='red', s=5)


            for ix in range(kerfusT.shape[0] - 1):
                pathT = a_star.astar_search(arr, tuple(map(int, kerfusT[ix, :2])), tuple(map(int, kerfusT[ix + 1, :2])))
                pathT = np.array(pathT)
                ax.plot(pathT[:, 0], pathT[:, 1], '--', c='limegreen')

                pathR = a_star.astar_search(arr, tuple(map(int, kerfusR[ix, :2])), tuple(map(int, kerfusR[ix + 1, :2])))
                pathR = np.array(pathR)
                ax.plot(pathR[:, 0], pathR[:, 1], '--', c='tomato')

                pathU = a_star.astar_search(arr, tuple(map(int, kerfusU[ix, :2])), tuple(map(int, kerfusU[ix + 1, :2])))
                pathU = np.array(pathU)
                ax.plot(pathU[:, 0], pathU[:, 1], '--', c='teal')

            ax.scatter(kerfusT[:, 0], kerfusT[:, 1], c='limegreen')
            ax.scatter(kerfusR[:, 0], kerfusR[:, 1], c='tomato')
            ax.scatter(kerfusU[:, 0], kerfusU[:, 1], c='teal')

            ax.scatter(shelves[:, 0], shelves[:, 1], c='lightblue', marker='s', s=26)
            ax.scatter(entrance[:, 0], entrance[:, 1], c='green', marker='s', s=26)
            ax.scatter(exit[:, 0], exit[:, 1], c='red', marker='s', s=26)
            ax.scatter(bread[:, 0], bread[:, 1], c='grey', marker='s', s=26)
            ax.scatter(meat[:, 0], meat[:, 1], c='orange', marker='s', s=26)


            for i in range(kerfusT.shape[0]):
                ax.annotate(i, tuple(kerfusT[i, :2]), c='limegreen')
                ax.annotate(i, tuple(kerfusR[i, :2]), c='tomato')
                ax.annotate(i, tuple(kerfusU[i, :2]), c='teal')

            ax.set_axisbelow(True)
            ax.xaxis.set_minor_locator(MultipleLocator(1))
            ax.yaxis.set_minor_locator(MultipleLocator(1))
            ax.set_aspect('equal', adjustable='box')
            ax.set_xlim((-0.5, 55.5))
            ax.set_ylim((28.5, -0.5))
            ax.grid(which='both', linewidth=0.25)
            ax.set_xticks([])
            ax.set_yticks([])

            self.matplotlib_widget.canvas.draw()

            model = KerfusTableModel(kerfus_tabT)
            self.kerfus_table.setModel(model)

        except Exception as e:
            if str(e) == 'too many indices for array: array is 1-dimensional, but 2 were indexed':
                self.show_error_popup("Error in Algorithm", "Klasy są sprzeczne, wybierz inne lub użyj algorytmicznych")
            else:
                print("Error executing algorithm:", str(e))