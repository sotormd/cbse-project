from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QWidget
)
from PyQt6.QtCore import Qt

class EntryDialog(QDialog):
    """
    Dialog for adding or editing a vault entry.
    Contains Title, Username, Password fields with password show/hide toggle.
    """
    def __init__(self, parent=None, title="", username="", password=""):
        super().__init__(parent)
        self.setWindowTitle("Vault Entry")
        self.setModal(True)

        # Floating dialog hints
        self.setWindowFlag(Qt.WindowType.Dialog)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        self.setFixedSize(400, 250)

        self.result_data = None

        layout = QVBoxLayout()
        self.setLayout(layout)

        # --- Title ---
        layout.addWidget(QLabel("Title:"))
        self.title_edit = QLineEdit(title)
        layout.addWidget(self.title_edit)

        # --- Username ---
        layout.addWidget(QLabel("Username:"))
        self.user_edit = QLineEdit(username)
        layout.addWidget(self.user_edit)

        # --- Password with show/hide ---
        layout.addWidget(QLabel("Password:"))
        pw_layout = QHBoxLayout()
        self.pw_edit = QLineEdit(password)
        self.pw_edit.setEchoMode(QLineEdit.EchoMode.Password)
        pw_layout.addWidget(self.pw_edit)

        self.toggle_btn = QPushButton("Show")
        self.toggle_btn.setCheckable(True)
        self.toggle_btn.toggled.connect(self.toggle_password)
        pw_layout.addWidget(self.toggle_btn)
        layout.addLayout(pw_layout)

        # --- Buttons ---
        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton("OK")
        self.ok_btn.setFixedWidth(100)
        self.ok_btn.clicked.connect(self.accept_dialog)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setFixedWidth(100)
        self.cancel_btn.clicked.connect(self.reject)
        btn_layout.addStretch(1)
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        btn_layout.addStretch(1)
        layout.addLayout(btn_layout)

    def toggle_password(self, checked):
        if checked:
            self.pw_edit.setEchoMode(QLineEdit.EchoMode.Normal)
            self.toggle_btn.setText("Hide")
        else:
            self.pw_edit.setEchoMode(QLineEdit.EchoMode.Password)
            self.toggle_btn.setText("Show")

    def accept_dialog(self):
        self.result_data = (
            self.title_edit.text(),
            self.user_edit.text(),
            self.pw_edit.text()
        )
        self.accept()

    def get_data(self):
        """
        Returns a tuple (title, username, password) if accepted, else None
        """
        return self.result_data
