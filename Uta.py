from PyQt6.QtWidgets import QDialogButtonBox, QVBoxLayout, QLabel, QPushButton, QWidget, QLineEdit, QDialog, \
    QTableWidget, QTableWidgetItem, QHeaderView, QSizePolicy, QHBoxLayout, QTableView, QMessageBox
from PyQt6.QtGui import QValidator, QStandardItemModel, QStandardItem, QColor
from PyQt6.QtCore import Qt, QAbstractTableModel
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
from functools import partial
from a_star import astar_search
from matplotlib.ticker import MultipleLocator
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
        self.headers = kerfus_tab[0]  # Extract headers from the first row
        self.data = kerfus_tab[1:]  # Exclude the first row (headers) from the data

    def rowCount(self, parent):
        return len(self.data)

    def columnCount(self, parent):
        return len(self.data[0])

    def data(self, index, role):
        if role == Qt.ItemDataRole.DisplayRole:
            value = self.data[index.row()][index.column()]
            # Convert the first column to int
            if index.column() != 3 and value is not None:
                return int(float(value))
            return str(value) if value is not None else ""  # Set an empty string for None values
        return None

    def headerData(self, section, orientation, role):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                # Set headers from the extracted headers
                return str(self.headers[section]) if section < len(self.headers) else ""
            elif orientation == Qt.Orientation.Vertical:
                # Set vertical headers with row numbers
                return str(section) if section < len(self.data) else ""
        return None


class ScreenUTA(QWidget):
    def __init__(self, data_manager: DataManager):
        super().__init__()
        self.data_manager = data_manager

        self.weights = np.array([0.25, 0.2, 0.3, 0.25])
        self.layout = QHBoxLayout()

        right_layout = QVBoxLayout()
        left_layout = QVBoxLayout()

        self.topsis_label = QLabel(self)
        self.topsis_label.setText("UTA*")
        self.topsis_label.setStyleSheet("font-size: 100px; color: white;")
        self.topsis_label.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        left_layout.addWidget(self.topsis_label)

        self.execute_button = QPushButton(self)
        self.execute_button.setStyleSheet("image: url(./grafika/but_oblicz.png);"
                                          "width: 140px;"
                                          "height: 60px;"
                                          "margin: 0px;"
                                          "background-color: transparent")
        self.execute_button.clicked.connect(self.run_uta)
        left_layout.addWidget(self.execute_button)

        self.execute_button = QPushButton(self)
        self.execute_button.setStyleSheet("image: url(./grafika/but_klasy.png);"
                                          "width: 120px;"
                                          "height: 60px;"
                                          "margin: 0px;"
                                          "background-color: transparent")
        self.execute_button.clicked.connect(self.show_input_dialog)
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
        self.kerfus_table.verticalHeader().setVisible(False)

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


    def pre_run(self):
        map_data = self.data_manager.get_data("map").copy()
        points_data = self.data_manager.get_data("points").copy()
        shop = map_data.values.T
        points = points_data.values
        minmax = [1, 1, 0, 0]  # 1- max, 0- min

        _, points, _, _ = alg_RSM.add_distances(shop.copy(), points.copy())

        user_steps_count = self.data_manager.get_data("ranges").copy()

        limits = uta_star.best(points[:, 2:], minmax)
        limits[1, 3] = np.max(points[:, 5])
        limits[0, 3] = np.min(points[:, 5])

        default_steps = uta_star.steps(limits,
                                       user_steps_count)  # przedziały z wagami wygenerowane automatycznie pokazujemy użytkownikowi

        user_steps = default_steps  # przedziały z wagami zmienione przez użytkownika

        #print(user_steps)
        self.data_manager.set_data("steps", np.around(user_steps, decimals=3))

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

            user_steps = self.data_manager.get_data("steps")
            #print(user_steps)

            usability = uta_star.usability_fun(user_steps, minmax)
            #print(usability)

            kerfus, choices, ranking = uta_star.uta_n_points(arr, base_coords, points, user_steps, points_ref, distance, usability, 10)
            #print(path)
            #print(ranking)

            base = np.zeros(ranking.shape[1])
            base[:2] = base_coords
            ranking = np.append([base], ranking, axis=0)

            shelves = np.argwhere(shop == 1)
            entrance = np.argwhere(shop == 2)
            exit = np.argwhere(shop == 3)
            bread = np.argwhere(shop == 4)
            meat = np.argwhere(shop == 5)

            ax = self.matplotlib_widget.canvas.figure.add_subplot(111)

            ax.scatter(points[:, 0], points[:, 1], c='red', s=5)
            for ix in range(ranking.shape[0] - 1):
                path = astar_search(shop, tuple(map(int, ranking[ix, :2])), tuple(map(int, ranking[ix + 1, :2])))
                path = np.array(path)
                ax.plot(path[:, 0], path[:, 1], '--', c='#1f77b4')
            ax.scatter(ranking[:, 0], ranking[:, 1])
            ax.scatter(shelves[:, 0], shelves[:, 1], c='lightblue', marker='s', s=26)
            ax.scatter(entrance[:, 0], entrance[:, 1], c='green', marker='s', s=26)
            ax.scatter(exit[:, 0], exit[:, 1], c='red', marker='s', s=26)
            ax.scatter(bread[:, 0], bread[:, 1], c='grey', marker='s', s=26)
            ax.scatter(meat[:, 0], meat[:, 1], c='orange', marker='s', s=26)

            for i in range(ranking.shape[0]):
                ax.annotate(i, tuple(ranking[i, :2]))

            ax.set_axisbelow(True)
            ax.xaxis.set_minor_locator(MultipleLocator(1))
            ax.yaxis.set_minor_locator(MultipleLocator(1))
            ax.set_aspect('equal', adjustable='box')
            ax.set_xlim((-0.5, 55.5))
            ax.set_ylim((28.5, -0.5))
            ax.grid(which='both', linewidth=0.25)
            ax.set_xticks([])
            ax.set_yticks([])
            ax.tick_params(which='both', length=0)

            self.matplotlib_widget.canvas.draw()

            model = KerfusTableModel(kerfus)
            self.kerfus_table.setModel(model)

            #print(kerfus)

            self.data_manager.set_data("UtaData", kerfus)

        except Exception as e:
            print("Exception in uta:", str(e))

    def show_input_dialog(self):
        try:
            dialog = WeightInputDialog(self.data_manager, self)
            result = dialog.exec()

        except Exception as e:
            print("Exception in show_weight_input_dialog:", str(e))


class WeightInputDialog(QDialog):
    def __init__(self, data_manager: DataManager, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Kreator przedziałów")
        self.data_manager = data_manager

        self.init_ui()

    def init_ui(self):
        layout = QVBoxLayout()
        self.text_label = QLabel(self)
        self.text_label.setText("Należy podać liczbę przedziałów na jaką ma być podzielony każdy z parametrów.\n")
        self.text_label.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        layout.addWidget(self.text_label)

        self.weight_inputs = []
        nazwy = ["popularności", "szerokości przejazdu", "przeszkadzania", "odległości od bazy", "odległości od ostatniego położenia"]
        for _ in range(4):
            label = QLabel(f"Liczba przedziałów dla kryterium {nazwy[_]}", self)
            input_field = QLineEdit(self)
            input_field.textChanged.connect(self.update_sum_label)
            input_field.setText("3")

            layout.addWidget(label)
            layout.addWidget(input_field)



            self.weight_inputs.append(input_field)

        self.update_sum_label()

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel)
        button_box.accepted.connect(self.accept_and_pre_run)
        button_box.rejected.connect(self.reject)

        layout.addWidget(button_box)
        self.setLayout(layout)

    def update_sum_label(self):
        try:
            # Update the sum label when any input field text is changed
            ranges = [int(input_field.text()) if input_field.text() else 0 for input_field in self.weight_inputs]
            self.data_manager.set_data("ranges", ranges)
        except Exception as e:
            print("Exception in update_sum_label:", str(e))

    def accept_and_pre_run(self):
        try:
            # Execute pre_run before accepting the dialog
            self.data_manager.set_data("steps", [])
            self.parent().pre_run()

            # Accept the dialog
            self.accept()

            # Show a new dialog with data from user_steps
            self.show_user_steps_dialog()
        except Exception as e:
            print("Exception in accept_and_pre_run:", str(e))

    def show_user_steps_dialog(self):
        try:
            # Create and show a new dialog with data from user_steps
            user_steps = self.data_manager.get_data("steps")
            dialog = UserStepsDialog(self.data_manager, user_steps, self, self.parent())
            dialog.exec()
        except Exception as e:
            print("Exception in show_user_steps_dialog:", str(e))

class UserStepsDialog(QDialog):
    def __init__(self, data_manager: DataManager, user_steps, parent=None, utascrn=None):
        super().__init__(parent)
        self.data_manager = data_manager
        self.user_steps = user_steps
        self.init_ui()
        self.utascrn = utascrn
        self.setWindowTitle("Kreator wag")

    def init_ui(self):
        layout = QVBoxLayout()

        self.tables = []  # Keep track of tables to access them later for updates

        self.text_label = QLabel(self)
        self.text_label.setText("Wartości pomiędzy punktami tworzą przedziały o odpowiednich wagach.\n"
                                "Przedziały o wysokim pożądaniu powinny mieć wysokie wagi.\n"
                                "Suma wag pierwszych wierszy każdego kryterium musi być równa 1, a suma ostanich 0.\n"
                                "Pozostałe sumy w wierszach powinny być w kolejności malejącej.\n")


        self.text_label.setSizePolicy(QSizePolicy.Policy.Maximum, QSizePolicy.Policy.Fixed)
        layout.addWidget(self.text_label)

        col_name = ["przedzial", "wagi"]
        names = ["Popularność", "Szerokość przejazdu", "Przeszkadzanie", "Odległości od bazy"]
        for array_index, array in enumerate(self.user_steps):
            array_layout = QVBoxLayout()


            array_label = QLabel(names[array_index], self)
            array_layout.addWidget(array_label)

            user_steps_table = QTableWidget(self)
            user_steps_table.setRowCount(array.shape[0])
            user_steps_table.setColumnCount(array.shape[1])

            # Set custom horizontal headers for each column
            for col in range(array.shape[1]):
                user_steps_table.setHorizontalHeaderItem(col, QTableWidgetItem(col_name[col]))

            # Populate the table
            for row in range(array.shape[0]):
                for col in range(array.shape[1]):
                    item = QTableWidgetItem(str(array[row, col]))
                    user_steps_table.setItem(row, col, item)

            # Connect the signal to the custom slot for updating values
            user_steps_table.itemChanged.connect(partial(self.update_array_value, array_index=array_index))

            array_layout.addWidget(user_steps_table)
            layout.addLayout(array_layout)
            self.tables.append(user_steps_table)

        button_box = QDialogButtonBox(QDialogButtonBox.StandardButton.Ok)
        button_box.accepted.connect(self.accept_and_run_uta)  # Connect to the new method

        layout.addWidget(button_box)
        self.setLayout(layout)
        self.setMinimumHeight(700)  # Set the minimum width as needed
        self.setMaximumWidth(300)  # Set the maximum width as needed



    def update_array_value(self, item, array_index):
        # Slot to update the corresponding value in the array when the table item is changed
        try:
            row = item.row()
            col = item.column()
            new_value = float(item.text())
            self.user_steps[array_index][row, col] = new_value
            self.data_manager.set_data('user_steps', self.user_steps)

        except ValueError:
            pass  # Handle non-numeric input gracefully, you may want to show a message

    def accept_and_run_uta(self):
        try:
            self.accept()

        except Exception as e:
            print("Exception in show_user_steps_dialog:", str(e))
