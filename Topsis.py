from PyQt6.QtWidgets import QDialogButtonBox, QVBoxLayout, QLabel, QPushButton, QWidget, QLineEdit, QDialog, QMessageBox, QSpacerItem, QSizePolicy
from PyQt6.QtGui import QValidator
from PyQt6.QtCore import Qt
from data_manager import DataManager

class ScreenTopsis(QWidget):
    def __init__(self, data_manager: DataManager):
        super().__init__()
        self.data_manager = data_manager
        # ... (rest of your ScreenTopsis code)

        self.layout = QVBoxLayout()

        self.label = QLabel("TOPSIS")
        self.layout.addWidget(self.label, alignment=Qt.AlignmentFlag.AlignHCenter)


        self.execute_button = QPushButton(self)
        self.execute_button.setStyleSheet("image: url(./grafika/but_topsis.png);"
                                         "width: 120px;"
                                         "height: 40px;"
                                         "margin: 0px;"
                                         "background-color: transparent")
        self.execute_button.clicked.connect(self.show_weight_input_dialog)
        self.layout.addWidget(self.execute_button)

        spacer = QSpacerItem(20, 20, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)

        self.back_button = QPushButton(self)
        self.back_button.setStyleSheet("image: url(./grafika/but_powrot.png);"
                                         "width: 120px;"
                                         "height: 60px;"
                                         "margin: 0px;"
                                         "background-color: transparent")
        self.back_button.clicked.connect(self.go_back)
        self.layout.addWidget(self.back_button)


        self.setLayout(self.layout)

        self.layout.setAlignment(Qt.AlignmentFlag.AlignCenter)

    def go_back(self):
        self.parent().setCurrentIndex(0)

    def show_weight_input_dialog(self):
        try:
            dialog = WeightInputDialog(self)
            result = dialog.exec()

            if result == QDialog.DialogCode.Accepted:
                # Handle the weights entered by the user
                weights = dialog.get_weights()

                if sum(weights) == 1:
                    print("Weights:", weights)
                    
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

            layout.addWidget(label)
            layout.addWidget(input_field)

            self.weight_inputs.append(input_field)

        self.sum_label = QLabel("Summed Weights: 0.0", self)
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