from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QWidget, QVBoxLayout, QLabel
from PyQt6.QtCore import Qt
import openpyxl

class ExcelTableScreen(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()

        self.label = QLabel("Excel Table Screen")
        self.layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.table_widget = QTableWidget()
        self.layout.addWidget(self.table_widget)

        self.setLayout(self.layout)

    def load_excel_data(self):
        try:
            workbook = openpyxl.load_workbook("punkty.xlsx")
            sheet = workbook.active

            self.table_widget.setRowCount(sheet.max_row)
            self.table_widget.setColumnCount(sheet.max_column)

            for row_index, row in enumerate(sheet.iter_rows(values_only=True)):
                for col_index, value in enumerate(row):
                    item = QTableWidgetItem(str(value))
                    self.table_widget.setItem(row_index, col_index, item)

        except Exception as e:
            print(f"Error loading Excel data: {e}")