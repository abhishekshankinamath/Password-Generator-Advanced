"""Password Studio - a Tkinter password and passphrase generator."""

from __future__ import annotations

import tkinter as tk
from tkinter import messagebox

from password_engine import (
    build_character_sets,
    estimate_entropy_bits,
    generate_password,
    generate_passphrase,
    strength_label,
    WORDS,
)


THEMES = {
    "dark": {
        "bg": "#0D1424",
        "panel": "#17243A",
        "panel_alt": "#1E2F49",
        "field": "#0F1B2E",
        "text": "#F4F7FC",
        "muted": "#A9B8CE",
        "accent": "#8B5CF6",
        "accent_hover": "#A078FA",
        "cyan": "#22D3EE",
        "green": "#34D399",
        "border": "#2B3D59",
        "danger": "#FB7185",
        "check": "#243650",
    },
    "light": {
        "bg": "#F2F5FB",
        "panel": "#FFFFFF",
        "panel_alt": "#EAF0FA",
        "field": "#F8FAFF",
        "text": "#172238",
        "muted": "#58677F",
        "accent": "#7050D8",
        "accent_hover": "#5E40C5",
        "cyan": "#087E9B",
        "green": "#0D986B",
        "border": "#D5DEEB",
        "danger": "#C43D5A",
        "check": "#E6ECF7",
    },
}


class PasswordStudio:
    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Password Studio | Python Mini Project 03")
        self.root.geometry("1000x740")
        self.root.minsize(860, 680)
        self.theme_name = "dark"
        self.colors = THEMES[self.theme_name]
        self.mode = tk.StringVar(value="password")
        self.password_length = tk.IntVar(value=20)
        self.word_count = tk.IntVar(value=6)
        self.separator = tk.StringVar(value="-")
        self.use_upper = tk.BooleanVar(value=True)
        self.use_lower = tk.BooleanVar(value=True)
        self.use_digits = tk.BooleanVar(value=True)
        self.use_symbols = tk.BooleanVar(value=True)
        self.exclude_ambiguous = tk.BooleanVar(value=True)
        self.no_repeats = tk.BooleanVar(value=False)
        self.capitalize_words = tk.BooleanVar(value=False)
        self.no_repeated_words = tk.BooleanVar(value=True)
        self.visible = tk.BooleanVar(value=False)
        self.generated_value = ""
        self.status_var = tk.StringVar(value="Choose your settings, then generate a secret.")
        self.strength_var = tk.StringVar(value="Your strength estimate will appear here.")

        self._build_ui()
        self._apply_theme()
        self.root.bind("<Control-g>", lambda _event: self.generate())
        self.root.bind("<Control-G>", lambda _event: self.generate())
        self.root.bind("<Control-Shift-c>", lambda _event: self.copy_to_clipboard())
        self.root.bind("<Return>", lambda _event: self.generate())

    # ---------- UI construction ----------
    def _build_ui(self) -> None:
        self.main = tk.Frame(self.root)
        self.main.pack(fill="both", expand=True, padx=24, pady=20)

        self.header = tk.Frame(self.main)
        self.header.pack(fill="x", pady=(0, 18))
        self.brand = tk.Frame(self.header)
        self.brand.pack(side="left", fill="x", expand=True)
        self.title_label = tk.Label(self.brand, text="✦  PASSWORD STUDIO", font=("Segoe UI", 25, "bold"))
        self.title_label.pack(anchor="w")
        self.subtitle_label = tk.Label(
            self.brand,
            text="Create strong passwords and memorable passphrases in seconds.",
            font=("Segoe UI", 10),
        )
        self.subtitle_label.pack(anchor="w", pady=(4, 0))
        self.theme_button = tk.Button(self.header, text="☼  Light theme", command=self.toggle_theme, cursor="hand2")
        self.theme_button.pack(side="right", padx=(10, 0), ipadx=12, ipady=8)

        self.body = tk.Frame(self.main)
        self.body.pack(fill="both", expand=True)
        self.body.grid_columnconfigure(0, weight=5, uniform="columns")
        self.body.grid_columnconfigure(1, weight=4, uniform="columns")
        self.body.grid_rowconfigure(0, weight=1)

        self.settings_card = self._card(self.body)
        self.settings_card.grid(row=0, column=0, sticky="nsew", padx=(0, 12))
        self.output_column = tk.Frame(self.body)
        self.output_column.grid(row=0, column=1, sticky="nsew", padx=(12, 0))

        self._build_settings(self.settings_card)
        self._build_output(self.output_column)

        self.footer = tk.Label(
            self.main,
            text="SECURE RANDOMNESS  •  NO PASSWORDS SAVED TO DISK  •  BUILT WITH PYTHON",
            font=("Segoe UI", 8, "bold"),
        )
        self.footer.pack(anchor="center", pady=(13, 0))

    def _card(self, parent: tk.Widget) -> tk.Frame:
        return tk.Frame(parent, padx=18, pady=18, bd=1, relief="solid", highlightthickness=0)

    def _build_settings(self, parent: tk.Frame) -> None:
        self.settings_title = tk.Label(parent, text="GENERATOR SETTINGS", font=("Segoe UI", 13, "bold"))
        self.settings_title.pack(anchor="w")
        self.settings_description = tk.Label(
            parent, text="Choose a format and customize what your secret contains.",
            font=("Segoe UI", 9), wraplength=440, justify="left",
        )
        self.settings_description.pack(anchor="w", pady=(4, 14))

        self.mode_label = tk.Label(parent, text="GENERATION TYPE", font=("Segoe UI", 9, "bold"))
        self.mode_label.pack(anchor="w")
        mode_row = tk.Frame(parent)
        mode_row.pack(fill="x", pady=(7, 14))
        self.password_mode_button = tk.Button(mode_row, text="Password", command=lambda: self.set_mode("password"), cursor="hand2")
        self.password_mode_button.pack(side="left", fill="x", expand=True, padx=(0, 5), ipady=8)
        self.passphrase_mode_button = tk.Button(mode_row, text="Passphrase", command=lambda: self.set_mode("passphrase"), cursor="hand2")
        self.passphrase_mode_button.pack(side="left", fill="x", expand=True, padx=(5, 0), ipady=8)

        self.password_options = tk.Frame(parent)
        self.password_options.pack(fill="x")
        self.length_heading = tk.Label(self.password_options, text="PASSWORD LENGTH", font=("Segoe UI", 9, "bold"))
        self.length_heading.pack(anchor="w")
        length_row = tk.Frame(self.password_options)
        length_row.pack(fill="x", pady=(5, 4))
        self.length_scale = tk.Scale(
            length_row, from_=8, to=128, orient="horizontal", variable=self.password_length,
            showvalue=True, resolution=1, command=lambda _value: self._update_length_label(),
            bd=0, highlightthickness=0, length=300,
        )
        self.length_scale.pack(side="left", fill="x", expand=True)
        self.length_value_label = tk.Label(length_row, text="20 chars", width=9, font=("Segoe UI", 9, "bold"))
        self.length_value_label.pack(side="right", padx=(8, 0))

        self.characters_heading = tk.Label(self.password_options, text="INCLUDE CHARACTER TYPES", font=("Segoe UI", 9, "bold"))
        self.characters_heading.pack(anchor="w", pady=(12, 5))
        checks = tk.Frame(self.password_options)
        checks.pack(fill="x")
        self.upper_check = self._check(checks, "Uppercase  A–Z", self.use_upper, 0, 0)
        self.lower_check = self._check(checks, "Lowercase  a–z", self.use_lower, 0, 1)
        self.digits_check = self._check(checks, "Numbers  0–9", self.use_digits, 1, 0)
        self.symbols_check = self._check(checks, "Symbols  !@#...", self.use_symbols, 1, 1)

        self.ambiguous_check = tk.Checkbutton(
            self.password_options, text="Exclude confusing characters (O, 0, I, l, 1)",
            variable=self.exclude_ambiguous, anchor="w", font=("Segoe UI", 9),
            activebackground=self.colors["panel"], command=self._clear_result,
        )
        self.ambiguous_check.pack(fill="x", pady=(10, 0))
        self.repeats_check = tk.Checkbutton(
            self.password_options, text="Do not repeat characters", variable=self.no_repeats,
            anchor="w", font=("Segoe UI", 9), activebackground=self.colors["panel"],
            command=self._clear_result,
        )
        self.repeats_check.pack(fill="x", pady=(3, 0))

        self.passphrase_options = tk.Frame(parent)
        self.words_heading = tk.Label(self.passphrase_options, text="NUMBER OF WORDS", font=("Segoe UI", 9, "bold"))
        self.words_heading.pack(anchor="w")
        words_row = tk.Frame(self.passphrase_options)
        words_row.pack(fill="x", pady=(6, 12))
        self.word_spin = tk.Spinbox(words_row, from_=4, to=12, textvariable=self.word_count, width=7, font=("Segoe UI", 11), command=self._clear_result)
        self.word_spin.pack(side="left", ipady=4)
        self.words_hint = tk.Label(words_row, text=f"Words are selected from an offline list of {len(WORDS)} words.", font=("Segoe UI", 8))
        self.words_hint.pack(side="left", padx=(10, 0))

        self.separator_heading = tk.Label(self.passphrase_options, text="WORD SEPARATOR", font=("Segoe UI", 9, "bold"))
        self.separator_heading.pack(anchor="w")
        self.separator_menu = tk.OptionMenu(self.passphrase_options, self.separator, "-", "_", ".", " ")
        self.separator_menu.pack(anchor="w", pady=(5, 10))
        self.capitalize_check = tk.Checkbutton(
            self.passphrase_options, text="Capitalize each word", variable=self.capitalize_words,
            anchor="w", font=("Segoe UI", 9), activebackground=self.colors["panel"],
            command=self._clear_result,
        )
        self.capitalize_check.pack(fill="x")
        self.unique_words_check = tk.Checkbutton(
            self.passphrase_options, text="Do not repeat words", variable=self.no_repeated_words,
            anchor="w", font=("Segoe UI", 9), activebackground=self.colors["panel"],
            command=self._clear_result,
        )
        self.unique_words_check.pack(fill="x", pady=(3, 0))

        self.generate_button = tk.Button(parent, text="✦  GENERATE SECURE SECRET", command=self.generate, cursor="hand2", font=("Segoe UI", 11, "bold"))
        self.generate_button.pack(fill="x", pady=(19, 10), ipady=10)
        self.keyboard_hint = tk.Label(parent, text="Shortcut: Ctrl + G or Enter to generate", font=("Segoe UI", 8))
        self.keyboard_hint.pack(anchor="center")

    def _check(self, parent: tk.Frame, text: str, variable: tk.BooleanVar, row: int, column: int) -> tk.Checkbutton:
        widget = tk.Checkbutton(
            parent, text=text, variable=variable, anchor="w", font=("Segoe UI", 9),
            activebackground=self.colors["panel"], command=self._clear_result,
        )
        widget.grid(row=row, column=column, sticky="w", padx=(0, 12), pady=3)
        parent.grid_columnconfigure(column, weight=1)
        return widget

    def _build_output(self, parent: tk.Frame) -> None:
        self.result_card = self._card(parent)
        self.result_card.pack(fill="x")
        self.result_heading = tk.Label(self.result_card, text="YOUR GENERATED SECRET", font=("Segoe UI", 13, "bold"))
        self.result_heading.pack(anchor="w")
        self.result_subtitle = tk.Label(self.result_card, text="Your password will appear below.", font=("Segoe UI", 9))
        self.result_subtitle.pack(anchor="w", pady=(4, 12))

        self.result_entry = tk.Entry(
            self.result_card, font=("Consolas", 13, "bold"), justify="center",
            relief="flat", bd=0, show="•", state="readonly", readonlybackground=self.colors["field"],
        )
        self.result_entry.pack(fill="x", ipady=13)

        result_buttons = tk.Frame(self.result_card)
        result_buttons.pack(fill="x", pady=(10, 0))
        self.show_button = tk.Button(result_buttons, text="Show", command=self.toggle_visibility, cursor="hand2")
        self.show_button.pack(side="left", fill="x", expand=True, padx=(0, 4), ipady=7)
        self.copy_button = tk.Button(result_buttons, text="Copy", command=self.copy_to_clipboard, cursor="hand2")
        self.copy_button.pack(side="left", fill="x", expand=True, padx=4, ipady=7)
        self.clear_button = tk.Button(result_buttons, text="Clear", command=self.clear_result, cursor="hand2")
        self.clear_button.pack(side="left", fill="x", expand=True, padx=(4, 0), ipady=7)

        self.strength_card = self._card(parent)
        self.strength_card.pack(fill="x", pady=(12, 0))
        self.strength_heading = tk.Label(self.strength_card, text="ESTIMATED STRENGTH", font=("Segoe UI", 10, "bold"))
        self.strength_heading.pack(anchor="w")
        self.strength_result = tk.Label(self.strength_card, textvariable=self.strength_var, font=("Segoe UI", 10, "bold"), anchor="w")
        self.strength_result.pack(anchor="w", pady=(8, 7))
        self.meter = tk.Canvas(self.strength_card, height=10, highlightthickness=0, bd=0)
        self.meter.pack(fill="x")
        self.entropy_label = tk.Label(self.strength_card, text="Estimated search-space entropy: — bits", font=("Segoe UI", 8))
        self.entropy_label.pack(anchor="w", pady=(7, 0))
        self.entropy_note = tk.Label(
            self.strength_card,
            text="This is an estimate, not a guarantee of real-world security.",
            font=("Segoe UI", 8), wraplength=370, justify="left",
        )
        self.entropy_note.pack(anchor="w", pady=(5, 0))

        self.tips_card = self._card(parent)
        self.tips_card.pack(fill="both", expand=True, pady=(12, 0))
        self.tips_heading = tk.Label(self.tips_card, text="SECURITY TIPS", font=("Segoe UI", 10, "bold"))
        self.tips_heading.pack(anchor="w")
        tips = [
            "Use a different password for every account.",
            "Prefer long passwords or multi-word passphrases.",
            "Store passwords in a trusted password manager.",
            "Never share passwords in screenshots or public chats.",
        ]
        self.tip_labels = []
        for tip in tips:
            label = tk.Label(self.tips_card, text="•  " + tip, font=("Segoe UI", 8), anchor="w", justify="left", wraplength=390)
            label.pack(fill="x", pady=3)
            self.tip_labels.append(label)

        self.status_label = tk.Label(parent, textvariable=self.status_var, font=("Segoe UI", 8), anchor="w", wraplength=400)
        self.status_label.pack(fill="x", pady=(10, 0))

    # ---------- Theme and mode ----------
    def toggle_theme(self) -> None:
        self.theme_name = "light" if self.theme_name == "dark" else "dark"
        self.colors = THEMES[self.theme_name]
        self._apply_theme()

    def _apply_theme(self) -> None:
        c = self.colors
        self.root.configure(bg=c["bg"])
        self._paint(self.main, c["bg"])
        self._paint(self.header, c["bg"])
        self._paint(self.brand, c["bg"])
        self._paint(self.body, c["bg"])
        self._paint(self.output_column, c["bg"])
        for card in (self.settings_card, self.result_card, self.strength_card, self.tips_card):
            self._paint(card, c["panel"], border=c["border"])
        self._paint(self.password_options, c["panel"])
        self._paint(self.passphrase_options, c["panel"])

        label_widgets = [
            self.title_label, self.subtitle_label, self.settings_title, self.settings_description,
            self.mode_label, self.length_heading, self.length_value_label, self.characters_heading,
            self.words_heading, self.words_hint, self.separator_heading, self.result_heading,
            self.result_subtitle, self.strength_heading, self.strength_result, self.entropy_label,
            self.entropy_note, self.tips_heading, self.footer, self.keyboard_hint, self.status_label,
        ] + self.tip_labels
        for widget in label_widgets:
            widget.configure(bg=c["panel"] if widget in [self.settings_title, self.settings_description, self.mode_label, self.length_heading, self.length_value_label, self.characters_heading, self.words_heading, self.words_hint, self.separator_heading, self.result_heading, self.result_subtitle, self.strength_heading, self.strength_result, self.entropy_label, self.entropy_note, self.tips_heading] or widget in self.tip_labels else c["bg"], fg=c["text"] if widget in [self.title_label, self.settings_title, self.mode_label, self.length_heading, self.characters_heading, self.words_heading, self.separator_heading, self.result_heading, self.strength_heading, self.strength_result, self.tips_heading] else c["muted"])
        self.title_label.configure(bg=c["bg"], fg=c["text"])
        self.subtitle_label.configure(bg=c["bg"], fg=c["muted"])
        self.footer.configure(bg=c["bg"], fg=c["muted"])
        self.status_label.configure(bg=c["bg"], fg=c["muted"])
        self.length_scale.configure(bg=c["panel"], fg=c["text"], troughcolor=c["panel_alt"], activebackground=c["accent"])
        self.result_entry.configure(bg=c["field"], fg=c["text"], insertbackground=c["text"], readonlybackground=c["field"])
        self.meter.configure(bg=c["panel"])
        for widget in (self.upper_check, self.lower_check, self.digits_check, self.symbols_check, self.ambiguous_check, self.repeats_check, self.capitalize_check, self.unique_words_check):
            widget.configure(bg=c["panel"], fg=c["text"], selectcolor=c["check"], activeforeground=c["text"])
        for widget in (self.word_spin, self.separator_menu):
            widget.configure(bg=c["field"], fg=c["text"], activebackground=c["panel_alt"], highlightthickness=0)
        self.theme_button.configure(text="☾  Dark theme" if self.theme_name == "light" else "☼  Light theme", bg=c["panel_alt"], fg=c["text"], activebackground=c["border"], relief="flat", bd=0)
        self._style_button(self.generate_button, c["accent"], c["text"], c["accent_hover"])
        self._style_button(self.copy_button, c["accent"], c["text"], c["accent_hover"])
        self._style_button(self.show_button, c["panel_alt"], c["text"], c["border"])
        self._style_button(self.clear_button, c["panel_alt"], c["text"], c["border"])
        for widget in (self.password_mode_button, self.passphrase_mode_button):
            self._paint(widget.master, c["panel"])
        self._paint(self.settings_card, c["panel"], border=c["border"])
        self._paint(self.result_card, c["panel"], border=c["border"])
        self._paint(self.strength_card, c["panel"], border=c["border"])
        self._paint(self.tips_card, c["panel"], border=c["border"])
        for label in self.tip_labels:
            label.configure(bg=c["panel"], fg=c["muted"])
        self._update_mode_buttons()
        self._draw_meter(0, c["border"])

    @staticmethod
    def _paint(widget: tk.Widget, bg: str, border: str | None = None) -> None:
        try:
            widget.configure(bg=bg)
            if border is not None:
                widget.configure(highlightbackground=border, highlightcolor=border)
        except tk.TclError:
            pass

    @staticmethod
    def _style_button(widget: tk.Button, bg: str, fg: str, active: str) -> None:
        widget.configure(bg=bg, fg=fg, activebackground=active, activeforeground=fg, relief="flat", bd=0, font=("Segoe UI", 9, "bold"))

    def set_mode(self, mode: str) -> None:
        self.mode.set(mode)
        self._clear_result()
        if mode == "password":
            self.passphrase_options.pack_forget()
            self.password_options.pack(fill="x")
            self.result_subtitle.configure(text="Your generated password will appear below.")
        else:
            self.password_options.pack_forget()
            self.passphrase_options.pack(fill="x")
            self.result_subtitle.configure(text="Your memorable passphrase will appear below.")
        self._update_mode_buttons()

    def _update_mode_buttons(self) -> None:
        c = self.colors
        active = self.password_mode_button if self.mode.get() == "password" else self.passphrase_mode_button
        inactive = self.passphrase_mode_button if self.mode.get() == "password" else self.password_mode_button
        self._style_button(active, c["accent"], c["text"], c["accent_hover"])
        self._style_button(inactive, c["panel_alt"], c["text"], c["border"])

    def _update_length_label(self) -> None:
        self.length_value_label.configure(text=f"{self.password_length.get()} chars")
        self._clear_result()

    # ---------- Generation and result handling ----------
    def generate(self) -> None:
        try:
            if self.mode.get() == "password":
                length = int(self.password_length.get())
                options = dict(
                    use_uppercase=self.use_upper.get(),
                    use_lowercase=self.use_lower.get(),
                    use_digits=self.use_digits.get(),
                    use_symbols=self.use_symbols.get(),
                    exclude_ambiguous=self.exclude_ambiguous.get(),
                    no_repeats=self.no_repeats.get(),
                )
                groups = build_character_sets(**{k: v for k, v in options.items() if k != "no_repeats"})
                result = generate_password(length, **options)
                pool_size = len(set("".join(groups)))
                entropy = estimate_entropy_bits(password_length=length, pool_size=pool_size, no_repeats=self.no_repeats.get())
            else:
                count = int(self.word_count.get())
                result = generate_passphrase(
                    count,
                    separator=self.separator.get(),
                    capitalize_words=self.capitalize_words.get(),
                    no_repeated_words=self.no_repeated_words.get(),
                )
                entropy = estimate_entropy_bits(
                    word_count=count,
                    word_list_size=len(WORDS),
                    no_repeats=self.no_repeated_words.get(),
                )
        except (ValueError, tk.TclError) as error:
            messagebox.showwarning("Check your settings", str(error), parent=self.root)
            return

        self.generated_value = result
        self.visible.set(False)
        self.result_entry.configure(state="normal", show="•")
        self.result_entry.delete(0, "end")
        self.result_entry.insert(0, result)
        self.result_entry.configure(state="readonly")
        label, advice = strength_label(entropy)
        self.strength_var.set(f"{label}  —  {advice}")
        self.entropy_label.configure(text=f"Estimated search-space entropy: {entropy:.1f} bits")
        ratio = min(entropy / 100.0, 1.0)
        self._draw_meter(ratio, self.colors["green"] if entropy >= 60 else self.colors["cyan"])
        self.show_button.configure(text="Show")
        self.status_var.set("Generated securely. Copy it to your password manager; it is not saved by this app.")

    def toggle_visibility(self) -> None:
        if not self.generated_value:
            self.status_var.set("Generate a password or passphrase first.")
            return
        self.visible.set(not self.visible.get())
        self.result_entry.configure(state="normal", show="" if self.visible.get() else "•")
        self.result_entry.configure(state="readonly")
        self.show_button.configure(text="Hide" if self.visible.get() else "Show")

    def copy_to_clipboard(self) -> None:
        if not self.generated_value:
            self.status_var.set("Generate a password or passphrase before copying.")
            return
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.generated_value)
            self.root.update()
            self.status_var.set("Copied to clipboard. Paste it into your password manager.")
        except tk.TclError:
            self.status_var.set("Could not access the clipboard. Please try again.")

    def clear_result(self) -> None:
        self.generated_value = ""
        self.result_entry.configure(state="normal", show="•")
        self.result_entry.delete(0, "end")
        self.result_entry.configure(state="readonly")
        self.visible.set(False)
        self.show_button.configure(text="Show")
        self.strength_var.set("Your strength estimate will appear here.")
        self.entropy_label.configure(text="Estimated search-space entropy: — bits")
        self._draw_meter(0, self.colors["border"])
        self.status_var.set("Cleared. Your generated secret was not saved to disk.")

    def _clear_result(self) -> None:
        if self.generated_value:
            self.clear_result()

    def _draw_meter(self, ratio: float, fill: str) -> None:
        self.meter.delete("all")
        width = max(self.meter.winfo_width(), 260)
        self.meter.create_rectangle(0, 1, width, 9, fill=self.colors["border"], outline="")
        if ratio > 0:
            self.meter.create_rectangle(0, 1, width * ratio, 9, fill=fill, outline="")


def main() -> None:
    root = tk.Tk()
    PasswordStudio(root)
    root.mainloop()


if __name__ == "__main__":
    main()
