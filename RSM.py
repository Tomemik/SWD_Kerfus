from PyQt6.QtWidgets import QVBoxLayout, QLabel, QPushButton, QWidget

class ScreenRSM(QWidget):
    def __init__(self):
        super().__init__()

        self.layout = QVBoxLayout()

        self.label = QLabel("RSM")
        self.layout.addWidget(self.label)

        self.back_button = QPushButton("WROC")
        self.back_button.clicked.connect(self.go_back)
        self.layout.addWidget(self.back_button)

        self.setLayout(self.layout)

    def go_back(self):
        self.parent().setCurrentIndex(0)