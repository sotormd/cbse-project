from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QScrollArea, QFrame,
    QSizePolicy, QLineEdit, QMenuBar, QMenu, QTabWidget, QCheckBox, QSlider, QComboBox
)
from PyQt6.QtGui import QAction
from PyQt6.QtCore import Qt

import pyperclip

class VaultWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Vault")

        self.setWindowFlag(Qt.WindowType.Dialog)
        self.setWindowFlag(Qt.WindowType.WindowStaysOnTopHint, True)
        self.setFixedSize(800, 500)

        self.current_entry_id = None

        self.main_layout = QVBoxLayout()
        self.setLayout(self.main_layout)

        self.welcome_widget = QWidget()
        w_layout = QVBoxLayout()
        w_layout.setAlignment(Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignVCenter)
        self.welcome_widget.setLayout(w_layout)

        self.open_btn = QPushButton("Open Existing Vault")
        self.create_btn = QPushButton("Create New Vault")

        for btn in [self.open_btn, self.create_btn]:
            btn.setFixedHeight(60)
            btn.setFixedWidth(300)
            btn.setSizePolicy(QSizePolicy.Policy.Preferred, QSizePolicy.Policy.Fixed)

        w_layout.addStretch(1)
        w_layout.addWidget(self.open_btn)
        w_layout.addSpacing(15)
        w_layout.addWidget(self.create_btn)

        self.theme_dropdown = QComboBox()
        self.theme_dropdown.setFixedWidth(150)
        self.theme_dropdown.addItems(["nord", "gruvbox-dark", "gruvbox-light", "solarized-dark", "solarized-light"])
        w_layout.addSpacing(30)
        w_layout.addWidget(self.theme_dropdown)
        w_layout.addStretch(1)

        self.main_layout.addWidget(self.welcome_widget)
        self.welcome_widget.show()

        self.vault_widget = QWidget()
        vault_page_layout = QVBoxLayout()
        self.vault_widget.setLayout(vault_page_layout)

        self.menu_bar = QMenuBar()

        vault_menu = QMenu("Vault", self)
        self.menu_close = QAction("Exit application", self)
        vault_menu.addAction(self.menu_close)
        self.menu_bar.addMenu(vault_menu)

        entries_menu = QMenu("Entries", self)
        self.menu_add = QAction("Add new entry", self)
        self.menu_edit = QAction("Edit current entry", self)
        self.menu_delete = QAction("Delete current entry", self)
        entries_menu.addAction(self.menu_add)
        entries_menu.addAction(self.menu_edit)
        entries_menu.addAction(self.menu_delete)
        self.menu_bar.addMenu(entries_menu)

        tools_menu = QMenu("Tools", self)
        self.menu_generator = QAction("Password generator", self)
        self.menu_health = QAction("Password quality check", self)
        tools_menu.addAction(self.menu_generator)
        tools_menu.addAction(self.menu_health)
        self.menu_bar.addMenu(tools_menu)

        self.main_layout.setMenuBar(self.menu_bar)

        self.menu_add.setEnabled(False)
        self.menu_edit.setEnabled(False)
        self.menu_delete.setEnabled(False)
        self.menu_generator.setEnabled(False)
        self.menu_health.setEnabled(False)

        top_layout = QHBoxLayout()
        vault_page_layout.addLayout(top_layout)

        self.left_scroll = QScrollArea()
        self.left_scroll.setWidgetResizable(True)
        self.left_frame = QWidget()
        self.left_layout = QVBoxLayout()
        self.left_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.left_frame.setLayout(self.left_layout)
        self.left_frame.setSizePolicy(QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding)
        self.left_scroll.setWidget(self.left_frame)
        top_layout.addWidget(self.left_scroll, 2)

        self.right_frame = QFrame()
        self.right_layout = QVBoxLayout()
        self.right_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.right_frame.setLayout(self.right_layout)
        top_layout.addWidget(self.right_frame, 3)

        self.detail_widgets = {}
        for name in ["Title", "Username", "Password"]:
            row = QHBoxLayout()
            label_btn = QPushButton(f"{name}:")
            label_btn.setFlat(True)  # removes 3D button effect
            label_btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    padding: 0;
                    text-align: left;
                }
                QPushButton:hover {
                    color: red;
                }
            """)
            row.addWidget(label_btn)

            if name == "Password":
                data = QLineEdit()
                data.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                data.setEchoMode(QLineEdit.EchoMode.Password)
                data.setReadOnly(True)
                data.setStyleSheet("background-color: transparent;")

                show_btn = QPushButton("Show")
                show_btn.setCheckable(True)

                def toggle_password(checked, d=data, btn=show_btn):
                    if checked:
                        d.setEchoMode(QLineEdit.EchoMode.Normal)
                        btn.setText("Hide")
                    else:
                        d.setEchoMode(QLineEdit.EchoMode.Password)
                        btn.setText("Show")

                show_btn.toggled.connect(toggle_password)
                label_btn.clicked.connect(lambda _, d=data: pyperclip.copy(d.text()))

                row.addWidget(data, 1)
                row.addWidget(show_btn)

            else:
                data = QLabel()
                data.setAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                label_btn.clicked.connect(lambda _, d=data: pyperclip.copy(d.text()))
                row.addWidget(data)

            self.detail_widgets[name.lower()] = data
            self.right_layout.addLayout(row)

        self.edit_btn = QPushButton("Edit")
        self.delete_btn = QPushButton("Delete")
        self.edit_btn.setFixedWidth(100)
        self.delete_btn.setFixedWidth(100)

        button_row = QHBoxLayout()
        button_row.addWidget(self.edit_btn)
        button_row.addWidget(self.delete_btn)
        button_row.addStretch(1)
        self.right_layout.addLayout(button_row)

        self.bottom_layout = QHBoxLayout()
        self.add_btn = QPushButton("Add")
        self.add_btn.setFixedWidth(100)
        self.bottom_layout.addWidget(self.add_btn)
        self.bottom_layout.addStretch(1)
        vault_page_layout.addLayout(self.bottom_layout)

        self.main_layout.addWidget(self.vault_widget)
        self.vault_widget.hide()

        self.generator_widget = QWidget()
        gen_layout = QVBoxLayout()
        self.generator_widget.setLayout(gen_layout)

        self.tabs = QTabWidget()
        gen_layout.addWidget(self.tabs)

        self.pw_tab = QWidget()
        pw_layout = QVBoxLayout()
        self.pw_tab.setLayout(pw_layout)

        pw_display_layout = QHBoxLayout()
        self.pw_output = QLineEdit()
        self.pw_output.setReadOnly(True)
        pw_display_layout.addWidget(self.pw_output)

        self.copy_pw_btn = QPushButton("Copy")
        self.copy_pw_btn.setFixedWidth(100)
        pw_display_layout.addWidget(self.copy_pw_btn)

        pw_layout.addLayout(pw_display_layout)

        char_layout = QHBoxLayout()
        self.chk_upper = QCheckBox("A-Z")
        self.chk_lower = QCheckBox("a-z")
        self.chk_digits = QCheckBox("0-9")
        self.chk_symbols = QCheckBox("Symbols")
        for chk in [self.chk_upper, self.chk_lower, self.chk_digits, self.chk_symbols]:
            chk.setChecked(True)
            char_layout.addWidget(chk)
        pw_layout.addLayout(char_layout)

        len_layout = QHBoxLayout()
        self.pw_length_slider = QSlider(Qt.Orientation.Horizontal)
        self.pw_length_slider.setMinimum(1)
        self.pw_length_slider.setMaximum(128)
        self.pw_length_slider.setValue(16)
        self.pw_length_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.pw_length_slider.setTickInterval(1)
        len_layout.addWidget(QLabel("Length:"))
        len_layout.addWidget(self.pw_length_slider)

        self.pw_length_label = QLabel(str(self.pw_length_slider.value()))
        len_layout.addWidget(self.pw_length_label)
        pw_layout.addLayout(len_layout)

        self.pw_back_btn = QPushButton("Back")
        self.pw_back_btn.setFixedWidth(100)

        self.generate_pw_btn = QPushButton("Generate")
        self.generate_pw_btn.setFixedWidth(100)
        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        btn_row.addWidget(self.generate_pw_btn)
        btn_row.addWidget(self.pw_back_btn)
        btn_row.addStretch(1)
        pw_layout.addLayout(btn_row)

        self.tabs.addTab(self.pw_tab, "Password Generator")

        self.ph_tab = QWidget()
        ph_layout = QVBoxLayout()
        self.ph_tab.setLayout(ph_layout)

        ph_display_layout = QHBoxLayout()
        self.ph_output = QLineEdit()
        self.ph_output.setReadOnly(True)
        ph_display_layout.addWidget(self.ph_output)
        self.copy_ph_btn = QPushButton("Copy")
        self.copy_ph_btn.setFixedWidth(100)
        ph_display_layout.addWidget(self.copy_ph_btn)
        ph_layout.addLayout(ph_display_layout)

        words_layout = QHBoxLayout()
        self.ph_words_slider = QSlider(Qt.Orientation.Horizontal)
        self.ph_words_slider.setMinimum(1)
        self.ph_words_slider.setMaximum(128)
        self.ph_words_slider.setValue(4)
        self.ph_words_slider.setTickPosition(QSlider.TickPosition.TicksBelow)
        self.ph_words_slider.setTickInterval(1)
        words_layout.addWidget(QLabel("Words:"))
        words_layout.addWidget(self.ph_words_slider)

        self.ph_words_label = QLabel(str(self.ph_words_slider.value()))
        words_layout.addWidget(self.ph_words_label)
        ph_layout.addLayout(words_layout)

        sep_layout = QHBoxLayout()
        sep_layout.addWidget(QLabel("Separator:"))
        self.ph_separator = QLineEdit("-")
        sep_layout.addWidget(self.ph_separator)
        ph_layout.addLayout(sep_layout)

        self.ph_back_btn = QPushButton("Back")
        self.ph_back_btn.setFixedWidth(100)

        self.generate_ph_btn = QPushButton("Generate")
        self.generate_ph_btn.setFixedWidth(100)
        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        btn_row.addWidget(self.generate_ph_btn)
        btn_row.addWidget(self.ph_back_btn)
        btn_row.addStretch(1)
        ph_layout.addLayout(btn_row)

        self.tabs.addTab(self.ph_tab, "Passphrase Generator")

        self.main_layout.addWidget(self.generator_widget)
        self.generator_widget.hide()

        self.quality_widget = QWidget()
        quality_layout = QVBoxLayout()
        self.quality_widget.setLayout(quality_layout)

        self.quality_scroll = QScrollArea()
        self.quality_scroll.setWidgetResizable(True)
        self.quality_frame = QWidget()
        self.quality_layout_inner = QVBoxLayout()
        self.quality_layout_inner.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.quality_frame.setLayout(self.quality_layout_inner)
        self.quality_scroll.setWidget(self.quality_frame)
        quality_layout.addWidget(self.quality_scroll)

        self.quality_back_btn = QPushButton("Back")
        self.quality_back_btn.setFixedWidth(100)
        btn_row = QHBoxLayout()
        btn_row.addStretch(1)
        btn_row.addWidget(self.quality_back_btn)
        btn_row.addStretch(1)
        quality_layout.addLayout(btn_row)

        self.main_layout.addWidget(self.quality_widget)
        self.quality_widget.hide()

    def show_generator(self):
        self.welcome_widget.hide()
        self.vault_widget.hide()
        self.quality_widget.hide()
        self.generator_widget.show()

    def show_vault(self):
        self.generator_widget.hide()
        self.quality_widget.hide()
        self.vault_widget.show()

    def enable_vault_menus(self):
        self.menu_add.setEnabled(True)
        self.menu_edit.setEnabled(True)
        self.menu_generator.setEnabled(True)
        self.menu_delete.setEnabled(True)
        self.menu_health.setEnabled(True)

    def on_vault_open(self):
        self.welcome_widget.hide()
        self.vault_widget.show()
        self.enable_vault_menus()

    def show_quality(self):
        self.welcome_widget.hide()
        self.vault_widget.hide()
        self.generator_widget.hide()
        self.quality_widget.show()
        self.run_quality_check()
