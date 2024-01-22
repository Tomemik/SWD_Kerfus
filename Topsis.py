from PyQt6.QtWidgets import QDialogButtonBox, QVBoxLayout, QLabel, QPushButton, QWidget, QLineEdit, QDialog, QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy, QHBoxLayout, QTableView, QMessageBox
from PyQt6.QtGui import QValidator, QStandardItemModel, QStandardItem
from PyQt6.QtCore import Qt, QAbstractTableModel
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np

from data_manager import DataManager
import alg_topsis
import alg_RSM


class MatplotlibWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.canvas = FigureCanvas(plt.figure(figsize=(4, 4)))  # Adjust figsize as needed
        self.canvas.figure.patch.set_facecolor("black")
        layout = QVBoxLayout()
        layout.addWidget(self.canvas)
        self.setLayout(layout)

    def update_figure(self, new_ax):
        # Clear the current figure and add the new axes
        self.canvas.figure.clf()
        self.canvas.figure.subplots_adjust(left=0, bottom=0, right=1, top=1)
        self.canvas.figure = new_ax.figure
        self.canvas.draw_idle()

        self.canvas.figure.patch.set_facecolor("black")

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


class ScreenTopsis(QWidget):
    def __init__(self, data_manager: DataManager):
        super().__init__()
        self.data_manager = data_manager

        self.weights = np.array([0.25, 0.2, 0.3, 0.25])
        self.layout = QHBoxLayout()

        right_layout = QVBoxLayout()
        left_layout = QVBoxLayout()

        self.topsis_label = QLabel(self)
        self.topsis_label.setText("TOPSIS")
        self.topsis_label.setStyleSheet("font-size: 100px; color: white;")
        self.topsis_label.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        left_layout.addWidget(self.topsis_label)


        self.execute_button = QPushButton(self)
        self.execute_button.setStyleSheet("image: url(./grafika/but_oblicz.png);"
                                         "width: 120px;"
                                         "height: 60px;"
                                         "margin: 0px;"
                                         "background-color: transparent")
        self.execute_button.clicked.connect(self.run_topsis)
        left_layout.addWidget(self.execute_button)

        self.execute_button = QPushButton(self)
        self.execute_button.setStyleSheet("image: url(./grafika/but_wagi.png);"
                                         "width: 120px;"
                                         "height: 60px;"
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
        right_layout.addWidget(self.kerfus_table)


        self.layout.addLayout(left_layout, 1)
        self.layout.addLayout(right_layout, 3)


        self.setLayout(self.layout)

        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), QColor(69, 67, 84))  # You can set any color you want here
        self.setPalette(p)




    def go_back(self):
        self.parent().setCurrentIndex(0)


    def run_topsis(self):
        try:
            map_data = self.data_manager.get_data("map").copy()
            points_data = self.data_manager.get_data("points").copy()
            shop = map_data.values.T
            points = points_data.values

            arr, points, distance, base_coords = alg_RSM.add_distances(shop.copy(), points.copy())
            points_ref = [(x, y) for x, y in points[:, :2]]

            # Pass the MatplotlibWidget instance to the topsis_results function
            kerfus_tab, choices, new_ax = alg_topsis.topsis_results(points.copy(), self.weights, points_ref.copy(), arr.copy(), distance.copy(), base_coords)

            # Update the MatplotlibWidget with the new figure
            self.matplotlib_widget.update_figure(new_ax)

            model = KerfusTableModel(kerfus_tab)
            self.kerfus_table.setModel(model)

        except:
            pass

    def show_weight_input_dialog(self):
        try:
            dialog = WeightInputDialog(self)
            dialog.setWindowTitle("Kreator wag")
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
            input_field.setText("0.25")

            layout.addWidget(label)
            layout.addWidget(input_field)

            self.weight_inputs.append(input_field)

        self.sum_label = QLabel("Summed Weights: 1.0", self)
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