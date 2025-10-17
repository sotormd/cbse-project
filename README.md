# unmaintaned archived school project

![Archived](https://img.shields.io/badge/status-archived-red)

# Features

- [X] Create and store passwords in sqlite database files.
- [X] Passwords are encrypted with AES in galois counter mode with a 256-bit key.
- [X] Key derivation from a master password with argon2id.
- [X] Generate strong passwords and passphrases.
- [X] Report weak passwords using [dropbox/zxcvbn](https://github.com/dropbox/zxcvbn).
- [X] Report passwords exposed in data breaches using the [hibp](https://haveibeenpwned.com/) api.
- [X] Graphical interface with Qt6.
- [X] Themes :p

# Project structure

```
.
├── main.py
├── requirements.txt
├── data
│   ├── settings.json
│   └── words_alpha.txt
├── modules
│   ├── crypt.py
│   ├── pwgen.py
│   ├── pwquality.py
│   └── vault.py
├── style
│   ├── gruvbox-dark.qss
│   ├── gruvbox-light.qss
│   ├── nord.qss
│   ├── solarized-dark.qss
│   └── solarized-light.qss
└── ui
    ├── entry.py
    ├── pw.py
    └── window.py
```

# Usage

<details> 

<summary> Windows </summary>

1. Clone this repository

    ```console
    > git clone https://github.com/sotormd/cbse-project
    > cd cbse-project
    ```

2. Install requirements

    <details>

    <summary> Command Prompt </summary>

    ```console
    > python -m venv venv
    > venv\Scripts\activate
    > python -m pip install -r requirements.txt
    ```

    </details>

    <details>

    <summary> Powershell </summary>

    ```console
    > python -m venv venv
    > .\venv\Scripts\Activate.ps1
    > python -m pip install -r requirements.txt
    ```

    </details>

3. Run `main.py`

    ```console
    > python main.py
    ```

</details>

<details>

<summary> *nix </summary>

1. Clone this repository

    ```console
    $ git clone https://github.com/sotormd/cbse-project
    $ cd cbse-project
    ```

2. Install requirements

    ```console
    $ python3 -m venv venv
    $ source venv/bin/activate
    $ python3 -m pip install -r requirements.txt
    ```

3. Run `main.py`

    ```console
    $ python3 main.py
    ```

</details>

# Requirements

`python3`

Python packages

- `pyperclip`
- `pyqt6`
- `pycryptodome`
- `argon2-cffi`
- `zxcvbn`
- `requests`

