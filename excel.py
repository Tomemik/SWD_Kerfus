from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QWidget, QVBoxLayout, QLabel, QPushButton, QFileDialog
from PyQt6.QtCore import Qt
import openpyxl
import pandas as pd
from data_manager import DataManager

class ExcelTableScreen(QWidget):
    def __init__(self, data_manager: DataManager):
        super().__init__()
        self.data_manager = data_manager

        self.layout = QVBoxLayout()

        self.label = QLabel("Excel Table Screen")
        self.layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.table_widget = QTableWidget()
        self.layout.addWidget(self.table_widget)

        self.punkty_file_label = QLabel("Punkty File: ")
        self.layout.addWidget(self.punkty_file_label)

        self.map_file_label = QLabel("Map File: ")
        self.layout.addWidget(self.map_file_label)

        self.load_point_button = QPushButton("Ładuj punkty")
        self.load_point_button.clicked.connect(self.load_point_data)
        self.layout.addWidget(self.load_point_button)

        self.save_button = QPushButton("Zapisz zmiany")
        self.save_button.clicked.connect(self.save_changes)
        self.layout.addWidget(self.save_button)

        self.back_button = QPushButton(self)
        self.back_button.setStyleSheet("image: url(./grafika/but_powrot.png);"
                                       "width: 120px;"
                                       "height: 40px;"
                                       "background-color: transparent;")
        self.back_button.clicked.connect(self.go_back)
        self.layout.addWidget(self.back_button)

        self.setLayout(self.layout)
        self.punkty_file_path = None
        self.map_file_path = None
        self.point_df = None
        self.map_df = None

    def load_point_data(self):
        try:
            file_dialog = QFileDialog()
            file_path, _ = file_dialog.getOpenFileName(self, "Open Excel File (Punkty)", "", "Excel Files (*.xlsx)")
            self.punkty_file_path = file_path

            if file_path:
                workbook = openpyxl.load_workbook(file_path)

                # Assuming you have two sheets named 'Points' and 'Map' in the Excel file
                point_sheet = workbook['punkty']
                map_sheet = workbook['mapa']

                # Load Points data
                self.table_widget.setRowCount(point_sheet.max_row)
                self.table_widget.setColumnCount(point_sheet.max_column)

                data = []
                for row_index, row in enumerate(point_sheet.iter_rows(values_only=True)):
                    row_data = []
                    for col_index, value in enumerate(row):
                        item = QTableWidgetItem(str(value))
                        self.table_widget.setItem(row_index, col_index, item)
                        row_data.append(str(value))
                    data.append(row_data)

                self.point_df = pd.read_excel(self.punkty_file_path, sheet_name='punkty', usecols='B:F', skiprows=0, nrows=100, keep_default_na=False)
                self.data_manager.set_data("points", self.point_df)

                self.map_df = pd.read_excel(self.punkty_file_path, sheet_name='mapa', usecols='B:BE', skiprows=0, nrows=29)
                self.data_manager.set_data("map", self.map_df)

                # Update the label with the loaded file name
                self.punkty_file_label.setText(f"Punkty File: {file_path}")

        except Exception as e:
            print(f"Error loading Punkty Excel data: {e}")

    def save_changes(self):
        try:
            if self.punkty_file_path:
                workbook = openpyxl.load_workbook(self.punkty_file_path)
                sheet = workbook.active

                for row in range(self.table_widget.rowCount()):
                    for col in range(self.table_widget.columnCount()):
                        item = self.table_widget.item(row, col)
                        if item is not None:
                            sheet.cell(row=row + 1, column=col + 1, value=item.text())

                workbook.save(self.punkty_file_path)
                print(f"Changes saved successfully for Punkty File: {self.punkty_file_path}")

                # Update the DataFrame after saving changes
                self.load_point_data()

        except Exception as e:
            print(f"Error saving changes to Punkty Excel: {e}")

    def go_back(self):
        self.parent().setCurrentIndex(0)
