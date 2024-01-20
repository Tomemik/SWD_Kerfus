from PyQt6.QtWidgets import QVBoxLayout, QLabel, QPushButton, QWidget

from data_manager import DataManager

class ScreenUTA(QWidget):
    def __init__(self, data_manager: DataManager):
        super().__init__()
        self.data_manager = data_manager

        self.layout = QVBoxLayout()

        self.label = QLabel("UTA")
        self.layout.addWidget(self.label)

        self.back_button = QPushButton("WROC")
        self.back_button.clicked.connect(self.go_back)
        self.layout.addWidget(self.back_button)

        self.setLayout(self.layout)

    def go_back(self):
        self.parent().setCurrentIndex(0)