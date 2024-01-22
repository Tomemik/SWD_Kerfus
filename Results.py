from PyQt6.QtWidgets import QVBoxLayout, QLabel, QPushButton, QWidget
from PyQt6.QtGui import QColor
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
        self.setAutoFillBackground(True)
        p = self.palette()
        p.setColor(self.backgroundRole(), QColor(69, 67, 84))  # You can set any color you want here
        self.setPalette(p)

    def go_back(self):
        self.parent().setCurrentIndex(0)