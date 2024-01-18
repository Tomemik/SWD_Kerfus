from PyQt6.QtWidgets import QVBoxLayout, QLabel, QPushButton, QWidget, QCheckBox
from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QFormLayout, QDialog, QHeaderView, QLineEdit, QFileDialog
from PyQt6.QtCore import Qt
import openpyxl
import pandas as pd

class ScreenRSM(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()

        self.label = QLabel("RSM")
        self.layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.class_type_checkbox = QCheckBox("Używaj klas użytkownika")
        self.layout.addWidget(self.class_type_checkbox)

        self.execute_button = QPushButton(self)
        self.execute_button.setStyleSheet("image: url(./grafika/but_rsm.png);"
                                         "width: 120px;"
                                         "height: 40px;"
                                         "margin: 0px;"
                                         "background-color: transparent")
        self.execute_button.clicked.connect(self.execute_algorithm)
        self.layout.addWidget(self.execute_button)

        self.select_points_button = QPushButton("Wybierz Klasy")
        self.select_points_button.setStyleSheet(
                                         "width: 120px;"
                                         "height: 40px;"
                                         "margin: 0px;"
                                         )
        self.select_points_button.clicked.connect(self.show_select_points_dialog)
        self.layout.addWidget(self.select_points_button)

        self.enter_custom_points_button = QPushButton("Stwórz decyzje")
        self.enter_custom_points_button.setStyleSheet(
                                         "width: 120px;"
                                         "height: 40px;"
                                         "margin: 0px;"
                                         )
        self.enter_custom_points_button.clicked.connect(self.show_enter_custom_points_dialog)
        self.layout.addWidget(self.enter_custom_points_button)

        self.back_button = QPushButton(self)
        self.back_button.setStyleSheet("image: url(./grafika/but_powrot.png);"
                                         "width: 120px;"
                                         "height: 40px;"
                                         "margin: 0px;"
                                         "background-color: transparent")
        self.back_button.clicked.connect(self.go_back)
        self.layout.addWidget(self.back_button)

        self.setLayout(self.layout)

        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def go_back(self):
        self.parent().setCurrentIndex(0)

    def execute_algorithm(self):
        print("Executing the algorithm")  # Placeholder for algorithm execution

    def show_select_points_dialog(self):
        select_points_dialog = SelectPointsDialog(self)
        select_points_dialog.exec()

    def show_enter_custom_points_dialog(self):
        enter_custom_points_dialog = EnterCustomPointsDialog(self)
        enter_custom_points_dialog.exec()


class SelectPointsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Select Points")

        layout = QVBoxLayout()

        self.table = QTableWidget(self)
        self.table.setColumnCount(7)
        self.table.setHorizontalHeaderLabels(["X", "Y", "wsp. Popularnosci", "szerokość alejki", "odleglosc od półki", "klasa 1", "klasa 2"])

        load_data_button = QPushButton("Load Data from Excel")
        load_data_button.clicked.connect(self.load_data_from_excel)

        layout.addWidget(load_data_button)
        layout.addWidget(self.table)

        self.setLayout(layout)
        self.selected_points = {'class1': set(), 'class2': set()}


    def load_data_from_excel(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Open Excel File", "", "Excel Files (*.xlsx)")

        if file_path:
            # Read data from the Excel file using openpyxl
            try:
                workbook = openpyxl.load_workbook(file_path)
                sheet = workbook.active

                # Skip the first row and start from the second column
                data = [(cell.value if cell is not None else "") for row in sheet.iter_rows(min_row=2) for cell in row[1:]]

                self.populate_table(data, sheet.max_column - 1)  # Subtract 1 for skipping the first column
            except Exception as e:
                print("Error loading data:", str(e))

    def populate_table(self, data, max_column):
        # Clear existing table content
        self.table.setRowCount(0)

        # Populate the table with data
        for row, values in enumerate(zip(*[iter(data)] * max_column)):
            self.table.insertRow(row)
            for col, value in enumerate(values):
                item = QTableWidgetItem(str(value))
                self.table.setItem(row, col, item)

                if col in (5, 6):  # Only for columns 6 and 7 (checkbox columns)
                    checkbox_item = QTableWidgetItem()
                    checkbox_item.setFlags(checkbox_item.flags() | Qt.ItemFlag.ItemIsUserCheckable)
                    checkbox_item.setCheckState(Qt.CheckState.Unchecked)
                    self.table.setItem(row, col, checkbox_item)


        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

        self.table.itemChanged.connect(self.checkbox_state_changed)

    def checkbox_state_changed(self, item):
        # Ensure that only one checkbox is checked in each row
        if item.column() in (5, 6):
            other_col = 6 if item.column() == 5 else 5
            other_item = self.table.item(item.row(), other_col)

            # Remove the point from the other set if it's added to the current set
            if item.checkState() == Qt.CheckState.Checked:
                other_item.setCheckState(Qt.CheckState.Unchecked)
                class_name = f'class{item.column() - 4}'  # Convert column index to class name (1 or 2)
                other_class_name = f'class{other_item.column() - 4}'
                self.selected_points[other_class_name].discard(item.row())

            class_name = f'class{item.column() - 4}'  # Convert column index to class name (1 or 2)
            if item.checkState() == Qt.CheckState.Checked:
                self.selected_points[class_name].add(item.row())
            else:
                self.selected_points[class_name].discard(item.row())

            print(self.selected_points)


class EnterCustomPointsDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Enter Custom Points")

        layout = QVBoxLayout()

        self.table = QTableWidget(self)
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["X", "Y", "wsp. Popularnosci", "szerokość alejki", "odleglosc od półki"])

        add_row_button = QPushButton("Add Row")
        add_row_button.clicked.connect(self.add_row)

        save_button = QPushButton("Save Table")
        save_button.clicked.connect(self.save_table)

        layout.addWidget(add_row_button)
        layout.addWidget(self.table)
        layout.addWidget(save_button)

        self.setLayout(layout)

    def save_table(self):
        try:
            df = self.get_table_data()
            print(df)
        except Exception as e:
            print("Error saving table:", str(e))

    def add_row(self):
        row_position = self.table.rowCount()
        self.table.insertRow(row_position)

        for col in range(5):
            item = QTableWidgetItem("")
            self.table.setItem(row_position, col, item)

        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)

    def get_table_data(self):
        rows = self.table.rowCount()
        cols = self.table.columnCount()
        data = []

        for row in range(rows):
            row_data = []
            for col in range(cols):
                item = self.table.item(row, col)
                row_data.append(item.text() if item is not None else "")
            data.append(row_data)

        columns = ["X", "Y", "wsp. Popularnosci", "szerokość alejki", "odleglosc od półki"]
        df = pd.DataFrame(data, columns=columns)
        return df