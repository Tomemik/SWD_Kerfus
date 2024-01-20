from PyQt6.QtWidgets import QVBoxLayout, QLabel, QPushButton, QWidget

from data_manager import DataManager

class ScreenResults(QWidget):
    def __init__(self, data_manager: DataManager):
        super().__init__()
        self.data_manager = data_manager

        self.layout = QVBoxLayout()

        self.label = QLabel("Wyniki")
        self.layout.addWidget(self.label)

        self.back_button = QPushButton(self)
        self.back_button.setStyleSheet("image: url(./grafika/but_powrot.png);"
                                         "width: 120px;"
                                         "height: 40px;"
                                         "background-color: transparent;")
        self.back_button.clicked.connect(self.go_back)
        self.layout.addWidget(self.back_button)

        self.setLayout(self.layout)

    def go_back(self):
        self.parent().setCurrentIndex(0)