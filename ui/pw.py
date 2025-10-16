from PyQt6.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox
from PyQt6.QtCore import Qt

class PasswordDialog(QDialog):
    def __init__(self, mode="open"):
        """
        mode: "open" -> unlock existing vault
              "create" -> create new vault
        """
        super().__init__()
        self.setWindowTitle("Vault - Master Password")

        # Floating dialog hints
        self.setWindowFlag(Qt.WindowType.Dialog)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        self.setFixedSize(400, 250)

        self.password = None
        self.mode = mode

        layout = QVBoxLayout()
        layout.setContentsMargins(20, 20, 20, 20)
        self.setLayout(layout)

        # Password label and input
        self.label = QLabel()
        layout.addWidget(self.label)

        self.pass_input = QLineEdit()
        self.pass_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.pass_input.setMaximumWidth(400)
        layout.addWidget(self.pass_input)

        if mode == "create":
            self.label.setText("Set a new master password:")
            layout.addSpacing(10)
            layout.addWidget(QLabel("Confirm password:"))
            self.pass_confirm = QLineEdit()
            self.pass_confirm.setEchoMode(QLineEdit.EchoMode.Password)
            self.pass_confirm.setMaximumWidth(400)
            layout.addWidget(self.pass_confirm)
        else:
            self.label.setText("Enter master password:")

        # Add stretch to push everything above upwards
        layout.addStretch()

        # OK and Cancel buttons at the bottom
        btn_layout = QHBoxLayout()
        btn_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignBottom)

        self.ok_btn = QPushButton("OK")
        self.ok_btn.setFixedWidth(100)
        self.ok_btn.clicked.connect(self.verify)
        btn_layout.addWidget(self.ok_btn)

        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setFixedWidth(100)
        self.cancel_btn.clicked.connect(self.reject)  # closes the dialog
        btn_layout.addWidget(self.cancel_btn)

        layout.addLayout(btn_layout)

    def verify(self):
        pw = self.pass_input.text()
        if self.mode == "create":
            pw2 = self.pass_confirm.text()
            if pw != pw2:
                QMessageBox.warning(self, "Mismatch", "Passwords do not match!")
                return

        if not pw:
            QMessageBox.warning(self, "Error", "Password cannot be empty!")
            return

        self.password = pw.encode()
        self.accept()
