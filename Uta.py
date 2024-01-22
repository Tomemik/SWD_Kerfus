from PyQt6.QtWidgets import QDialogButtonBox, QVBoxLayout, QLabel, QPushButton, QWidget, QLineEdit, QDialog, \
    QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy, QHBoxLayout, QTableView, QMessageBox
from PyQt6.QtGui import QValidator, QStandardItemModel, QStandardItem, QColor
from PyQt6.QtCore import Qt, QAbstractTableModel
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np

from data_manager import DataManager
import alg_topsis
import alg_RSM
import uta_star

class MatplotlibWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.canvas = FigureCanvas(plt.figure(figsize=(4, 4)))  # Adjust figsize as needed
        self.canvas.figure.patch.set_facecolor((0.27, 0.26, 0.33))
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def update_figure(self, new_ax):
        # Clear the current figure and add the new axes
        self.canvas.figure.clf()
        self.canvas.figure.subplots_adjust(left=0, bottom=0, right=1, top=1)
        self.canvas.figure = new_ax.figure
        self.canvas.draw_idle()

        self.canvas.figure.patch.set_facecolor((0.27, 0.26, 0.33))

        self.repaint()


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
            return str(self.data[index.row()][index.column()])
        return None


class ScreenUTA(QWidget):
    def __init__(self, data_manager: DataManager):
        super().__init__()
        self.data_manager = data_manager

        self.weights = np.array([0.25, 0.2, 0.3, 0.25])
        self.layout = QHBoxLayout()

        right_layout = QVBoxLayout()
        left_layout = QVBoxLayout()

        self.execute_button = QPushButton(self)
        self.execute_button.setStyleSheet("image: url(./grafika/but_uta.png);"
                                          "width: 120px;"
                                          "height: 40px;"
                                          "margin: 0px;"
                                          "background-color: transparent")
        self.execute_button.clicked.connect(self.run_uta)
        left_layout.addWidget(self.execute_button)

        self.execute_button = QPushButton('wagi')
        self.execute_button.setStyleSheet(""
                                          "width: 120px;"
                                          "height: 40px;"
                                          "margin: 0px;"
                                          "background-color: transparent")
        self.execute_button.clicked.connect(self.show_weight_input_dialog)
        left_layout.addWidget(self.execute_button)

        self.back_button = QPushButton(self)
        self.back_button.setStyleSheet("image: url(./grafika/but_powrot.png);"
                                       "width: 120px;"
                                       "height: 60px;"
                                       "margin: 0px;"
                                       "background-color: transparent")
        self.back_button.clicked.connect(self.go_back)
        left_layout.addWidget(self.back_button)

        self.matplotlib_widget = MatplotlibWidget(self.layout.parentWidget())
        right_layout.addWidget(self.matplotlib_widget)

        self.kerfus_table = QTableView()

        stylesheet = "::section{Background-color:rgb(69, 67, 84);}"
        self.kerfus_table.horizontalHeader().setStyleSheet(stylesheet)

        stylesheet = "::section{Background-color:rgb(69, 67, 84);}"
        self.kerfus_table.verticalHeader().setStyleSheet(stylesheet)

        self.kerfus_table.setStyleSheet("background-color: rgb(69, 67, 84); color: white;border:2px;border-style: none;")
        right_layout.addWidget(self.kerfus_table)

        self.layout.addLayout(left_layout, 1)
        self.layout.addLayout(right_layout, 3)

        self.setLayout(self.layout)

        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), QColor(69, 67, 84))  # You can set any color you want here
        self.setPalette(p)

    def go_back(self):
        self.parent().setCurrentIndex(0)

    def run_uta(self):
        try:
            map_data = self.data_manager.get_data("map").copy()
            points_data = self.data_manager.get_data("points").copy()
            shop = map_data.values.T
            arr = shop.copy()
            points = points_data.values

            base_coords = np.argwhere(arr == 6)
            base_coords = tuple(base_coords[0])
            arr[base_coords] = 0

            arr, points, distance, base_coords = alg_RSM.add_distances(shop.copy(), points.copy())
            points_ref = [(x, y) for x, y in points[:, :2]]

            minmax = [1, 1, 0, 0]  # 1- max, 0- min

            limits = uta_star.best(points[:, 2:], minmax)
            #print(limits)

            user_steps_count = [3, 5, 2]  # użytkownik wybiera na ile przedziałów chce podzielić każdy parametr

            default_steps = uta_star.steps(limits,
                                  user_steps_count)  # przedziały z wagami wygenerowane automatycznie pokazujemy użytkownikowi
            #print(default_steps)

            user_steps = default_steps  # przedziały z wagami zmienione przez użytkownika
            user_steps[0][1][1] = 0.18
            user_steps[1][1][1] = 0.18
            user_steps[2][1][1] = 0.28
            user_steps[2][2][1] = 0.14
            #print(user_steps)

            usability = uta_star.usability_fun(user_steps, minmax)
            #print(usability)

            path, choices, fig1 = uta_star.uta_n_points(points, user_steps, points_ref, distance, usability, 10)

            self.matplotlib_widget.update_figure(fig1)

            #model = KerfusTableModel(kerfus_tab)
            #self.kerfus_table.setModel(model)

            print(path)

        except Exception as e:
            print("Exception in uta:", str(e))

    def show_weight_input_dialog(self):
        try:
            dialog = WeightInputDialog(self)
            result = dialog.exec()

            if result == QDialog.DialogCode.Accepted:
                # Handle the weights entered by the user
                weights = dialog.get_weights()

                if sum(weights) == 1:
                    print("Weights:", weights)
                    self.weights = weights

                else:
                    print("Error: The sum of weights must equal 1.")
        except Exception as e:
            print("Exception in show_weight_input_dialog:", str(e))


class WeightInputDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()

        self.weight_inputs = []

        for _ in range(4):
            label = QLabel(f"Weight {_ + 1}:", self)
            input_field = QLineEdit(self)
            input_field.setValidator(WeightValidator())  # Custom validator to ensure valid floats
            input_field.textChanged.connect(self.update_sum_label)

            layout.addWidget(label)
            layout.addWidget(input_field)

            self.weight_inputs.append(input_field)

        self.sum_label = QLabel("Summed Weights: 0.0", self)
        layout.addWidget(self.sum_label)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.check_and_accept)
        button_box.rejected.connect(self.reject)

        layout.addWidget(button_box)
        self.setLayout(layout)

    def update_sum_label(self):
        try:
            # Update the sum label when any input field text is changed
            weights = [float(input_field.text()) if input_field.text() else 0 for input_field in self.weight_inputs]
            summed_weights = sum(weights)
            self.sum_label.setText(f"Summed Weights: {summed_weights}")
        except Exception as e:
            print("Exception in update_sum_label:", str(e))

    def check_and_accept(self):
        # Check the sum of weights
        weights = [float(input_field.text()) for input_field in self.weight_inputs]
        summed_weights = sum(weights)

        # Update the sum label
        self.sum_label.setText(f"Summed Weights: {summed_weights}")

        if summed_weights == 1:
            self.accept()
        else:
            # Display a popup with an error message
            error_message = "Error: The sum of weights must equal 1."
            QMessageBox.critical(self, "Error", error_message, QMessageBox.StandardButton.Ok)

            # Do not accept the dialog
            self.reject()

    def get_weights(self):
        weights = [float(input_field.text()) for input_field in self.weight_inputs]
        return weights


class WeightValidator(QValidator):
    def validate(self, input_str, pos):
        try:
            value = float(input_str)
            if 0 <= value <= 1:
                return QValidator.State.Acceptable, input_str, pos
            else:
                return QValidator.State.Invalid, input_str, pos
        except ValueError:
            return QValidator.State.Invalid, input_str, pos


def topsis():
    pass