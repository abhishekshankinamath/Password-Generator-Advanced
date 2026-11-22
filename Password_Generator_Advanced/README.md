# Password Studio — Advanced Python Password Generator

A desktop password and passphrase generator built with Python and Tkinter.

## Features

- Cryptographically secure password generation using Python's `secrets` module.
- Password lengths from 8 to 128 characters.
- Select uppercase, lowercase, digits and symbols independently.
- Optionally exclude ambiguous characters such as `O`, `0`, `I`, `l` and `1`.
- Optionally prevent repeated characters.
- Memorable passphrases made from an offline built-in word list (4–12 words).
- Choose a passphrase separator, capitalize words, and prevent repeated words.
- Approximate entropy estimate and simple strength guidance.
- Show/hide, copy and clear controls.
- Dark and light themes.
- Keyboard shortcuts: `Ctrl+G` or `Enter` to generate; `Ctrl+Shift+C` to copy.
- No generated password is written to disk by this application.

## Requirements

- Python 3.10 or newer recommended.
- Tkinter (normally included with the standard Windows Python installer).
- No third-party packages are required.

## Run on Windows

1. Extract the project ZIP.
2. Open the `Password_Generator_Advanced` folder in VS Code or File Explorer.
3. Open a terminal in that folder.
4. Run:

   ```powershell
   python password_generator.py
   ```

Or double-click `run_app.bat`.

## Project structure

```text
Password_Generator_Advanced/
├── password_generator.py   # Tkinter desktop interface
├── password_engine.py      # Secure password/passphrase logic
├── requirements.txt        # No external dependencies
├── run_app.bat             # Windows launcher
├── README.md
└── .gitignore
```

## Security notes

- The generator uses `secrets`, not the non-cryptographic `random` module.
- Generated passwords are kept in application memory only. They are not written to a file, logged, or sent over a network.
- Copying a secret places it on the operating-system clipboard. Other applications running under your user session may be able to read clipboard contents. Paste it into a trusted password manager and clear the clipboard when appropriate.
- The strength indicator is an approximate search-space estimate, not a guarantee of resistance to every attack. Do not reuse passwords across accounts.
- Keep generated passwords and passphrases private. Do not include real secrets in screenshots, source control, or public issue reports.
