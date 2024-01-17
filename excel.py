from PyQt6.QtWidgets import QTableWidget, QTableWidgetItem, QWidget, QVBoxLayout, QLabel, QPushButton
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

        self.save_button = QPushButton("Save Changes")
        self.save_button.clicked.connect(self.save_changes)
        self.layout.addWidget(self.save_button)

        self.back_button = QPushButton("WROC")
        self.back_button.clicked.connect(self.go_back)
        self.layout.addWidget(self.back_button)


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

    def save_changes(self):
        try:
            workbook = openpyxl.load_workbook("punkty.xlsx")
            sheet = workbook.active

            for row in range(self.table_widget.rowCount()):
                for col in range(self.table_widget.columnCount()):
                    item = self.table_widget.item(row, col)
                    if item is not None:
                        sheet.cell(row=row + 1, column=col + 1, value=item.text())

            workbook.save("punkty.xlsx")
            print("Changes saved successfully!")

        except Exception as e:
            print(f"Error saving changes to Excel: {e}")

    def go_back(self):
        self.parent().setCurrentIndex(0)