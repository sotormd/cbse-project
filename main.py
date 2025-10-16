#! /usr/bin/env python3

import json
import os
import sys

import pyperclip
from modules import pwgen, pwquality, vault
from PyQt6.QtWidgets import (QApplication, QFileDialog, QLabel, QMessageBox,
                             QPushButton)
from ui.entry import EntryDialog
from ui.pw import PasswordDialog
from ui.window import VaultWindow


class AppWindow(VaultWindow):
    def __init__(self):
        super().__init__()

        # build widget event connections
        self.build_connections()

        # initialize
        self.vault = None
        self.entries = {}
        self.entry_buttons = {}
        self.current_entry_id = None

        self.theme_dropdown.setCurrentText(stylesheet[:-4])

    def build_connections(self):

        # welcome screen
        self.open_btn.clicked.connect(self.open_vault)
        self.create_btn.clicked.connect(self.create_vault)
        self.theme_dropdown.currentTextChanged.connect(self.change_theme)

        # main screen
        self.add_btn.clicked.connect(self.add_entry)
        self.edit_btn.clicked.connect(self.edit_entry)
        self.delete_btn.clicked.connect(self.delete_entry)

        # menu bar
        self.menu_close.triggered.connect(self.close)
        self.menu_add.triggered.connect(self.add_entry)
        self.menu_edit.triggered.connect(self.edit_entry)
        self.menu_delete.triggered.connect(self.delete_entry)
        self.menu_generator.triggered.connect(self.show_generator)
        self.menu_health.triggered.connect(self.show_quality)

        # generator screen
        self.copy_pw_btn.clicked.connect(lambda: pyperclip.copy(self.pw_output.text()))
        self.pw_length_slider.valueChanged.connect(
            lambda val: self.pw_length_label.setText(str(val))
        )
        self.generate_pw_btn.clicked.connect(self.generate_password)
        self.pw_back_btn.clicked.connect(self.show_vault)

        self.copy_ph_btn.clicked.connect(lambda: pyperclip.copy(self.ph_output.text()))
        self.ph_words_slider.valueChanged.connect(
            lambda val: self.ph_words_label.setText(str(val))
        )
        self.generate_ph_btn.clicked.connect(self.generate_passphrase)
        self.ph_back_btn.clicked.connect(self.show_vault)

        # quality screen
        self.quality_back_btn.clicked.connect(self.show_vault)

    def change_theme(self, name: str):
        with open(
            os.path.join(os.path.dirname(__file__), "data", "settings.json"), "r"
        ) as file:
            settings = json.load(file)

        settings["stylesheet"] = name
        stylesheet = name + ".qss"

        with open(
            os.path.join(os.path.dirname(__file__), "data", "settings.json"), "w"
        ) as file:
            json.dump(settings, file)

        with open(
            os.path.join(os.path.dirname(__file__), "style", stylesheet), "r"
        ) as f:
            app.setStyleSheet(f.read())

    def run_quality_check(self):
        # clear any previous results
        for i in reversed(range(self.quality_layout_inner.count())):
            w = self.quality_layout_inner.itemAt(i).widget()
            if w:
                w.setParent(None)

        # if there are no entries to display
        if not self.entries:
            self.quality_layout_inner.addWidget(QLabel("No entries in vault."))
            return

        # check for weak passwords
        weak_found = False
        for eid, (title, username, password) in self.entries.items():
            score = pwquality.pwquality(password)
            if score < 3:
                weak_found = True
                label = QLabel(f"!! {title} ({username}) — score: {score}")
                self.quality_layout_inner.addWidget(label)

        # no weak passwords c:
        if not weak_found:
            self.quality_layout_inner.addWidget(
                QLabel("All passwords look strong enough.")
            )

        # check for pwned passwords
        pwned_found = False
        for eid, (title, username, password) in self.entries.items():
            count = pwquality.check_pwned(password)
            if count > 0:
                pwned_found = True
                label = QLabel(
                    f"!! {title} ({username}) — exposed {count} times in data breaches"
                )
                self.quality_layout_inner.addWidget(label)

        # no pwned passwords c:
        if not pwned_found:
            self.quality_layout_inner.addWidget(
                QLabel("No passwords found in known breaches.")
            )

    def open_vault(self):
        path, _ = QFileDialog.getOpenFileName(
            self, "Open Vault", "", "SQLite DB (*.db)"
        )
        if not path:
            return

        self.vault = vault.Vault(path)

        pw_dialog = PasswordDialog(mode="open")
        if pw_dialog.exec():
            pw = pw_dialog.password

            self.vault.open()

            if self.vault.unlock(pw):
                QMessageBox.warning(
                    self,
                    "Incorrect Password",
                    "The password you entered is incorrect. Please try again.",
                )
                self.vault.close()
                return

            self.welcome_widget.hide()
            self.vault_widget.show()

            self.load_entries()
            self.on_vault_open()

    def create_vault(self):
        path, _ = QFileDialog.getSaveFileName(
            self, "Create Vault", "", "SQLite DB (*.db)"
        )
        if not path:
            return

        self.vault = vault.Vault(path)

        pw_dialog = PasswordDialog(mode="create")
        if pw_dialog.exec():
            pw = pw_dialog.password

            self.vault.open()
            self.vault.initialize(pw)

            self.welcome_widget.hide()
            self.vault_widget.show()

            self.load_entries()
            self.on_vault_open()

    def load_entries(self):
        assert self.vault is not None

        self.entries.clear()
        self.entry_buttons.clear()

        # clear left pane
        for i in reversed(range(self.left_layout.count())):
            widget = self.left_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        # get and decrypt all rows
        rows = self.vault.get_rows()
        for r in rows:
            entry_id = r[0]
            try:
                title = self.vault.aes.decrypt(r[1]).decode()
                username = self.vault.aes.decrypt(r[2]).decode()
                password = self.vault.aes.decrypt(r[3]).decode()
            except Exception:
                title, username, password = "<decryption failed>", "", ""

            # entries are clickable buttons
            self.entries[entry_id] = (title, username, password)
            btn = QPushButton(title)
            btn.setCheckable(True)
            btn.clicked.connect(lambda _, eid=entry_id: self.show_entry(eid))
            self.left_layout.addWidget(btn)
            self.entry_buttons[entry_id] = btn

        # select first entry by default
        if self.entries:
            self.show_entry(list(self.entries.keys())[0])

    def generate_password(self):
        generated_password = pwgen.generate_password(
            uppercase=self.chk_upper.isChecked(),
            lowercase=self.chk_lower.isChecked(),
            digits=self.chk_digits.isChecked(),
            symbols=self.chk_symbols.isChecked(),
            length=self.pw_length_slider.value(),
        )
        self.pw_output.setText(generated_password)

    def generate_passphrase(self):
        generated_passphrase = pwgen.generate_passphrase(
            length=self.ph_words_slider.value(), separator=self.ph_separator.text()
        )
        self.ph_output.setText(generated_passphrase)

    def show_entry(self, entry_id):
        for eid, btn in self.entry_buttons.items():
            btn.setChecked(eid == entry_id)

        title, username, password = self.entries[entry_id]
        self.current_entry_id = entry_id
        self.detail_widgets["title"].setText(title)
        self.detail_widgets["username"].setText(username)
        self.detail_widgets["password"].setText(password)

    def add_entry(self):
        assert self.vault is not None

        dlg = EntryDialog(self)
        if dlg.exec():
            title, username, password = dlg.get_data()
            self.vault.add_entry(title, username, password)
            self.load_entries()

    def edit_entry(self):
        assert self.vault is not None

        if not self.current_entry_id:
            return

        old_title, old_user, old_pass = self.entries[self.current_entry_id]
        dlg = EntryDialog(self, old_title, old_user, old_pass)
        if dlg.exec():
            title, username, password = dlg.get_data()
            self.vault.edit_entry(self.current_entry_id, title, username, password)
            self.load_entries()

    def delete_entry(self):
        assert self.vault is not None

        if not self.current_entry_id:
            return

        confirm = QMessageBox.question(
            self,
            "Delete Entry",
            "Are you sure you want to delete this entry?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
        )

        if confirm == QMessageBox.StandardButton.Yes:
            self.vault.delete_entry(self.current_entry_id)
            self.load_entries()


if __name__ == "__main__":
    with open(os.path.join(os.path.dirname(__file__), "data", "settings.json")) as file:
        settings = json.load(file)
    stylesheet = settings["stylesheet"] + ".qss"

    app = QApplication([])
    with open(os.path.join(os.path.dirname(__file__), "style", stylesheet), "r") as f:
        app.setStyleSheet(f.read())
    win = AppWindow()
    win.show()
    sys.exit(app.exec())
