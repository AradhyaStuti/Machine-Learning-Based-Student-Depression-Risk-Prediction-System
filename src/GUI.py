# Student Depression Prediction GUI (built with customtkinter)

import logging
import uuid

import customtkinter as ctk

from src.config import DIET_OPTIONS, GENDER_OPTIONS, SLEEP_OPTIONS
from src.database import get_predictions, save_prediction
from src.model_definition import FIELD_NAME_MAP, predict, risk_level
from src.validation import (
    all_fields_filled,
    validate_age,
    validate_study_hours,
)

logger = logging.getLogger(__name__)

# Colors
BG_DARK = "#0d1117"
BG_CARD = "#161b22"
BG_INPUT = "#1c2333"
ACCENT = "#1f6feb"
GREEN = "#3fb950"
ORANGE = "#d29922"
RED = "#f85149"
BORDER = "#30363d"
TEXT_DIM = "#7d8590"
TEXT_MID = "#b1bac4"
TEXT_BRIGHT = "#e6edf3"

# Slider
SLIDER_DEFAULT = 3.0
SLIDER_MIN = 1
SLIDER_MAX = 5
SLIDER_STEPS = 4

# Fonts
FONT_TITLE = ("Segoe UI", 18, "bold")
FONT_SECTION = ("Segoe UI", 11, "bold")
FONT_LABEL = ("Segoe UI", 11)
FONT_SMALL = ("Segoe UI", 10)
FONT_RESULT = ("Segoe UI", 13, "bold")
FONT_TIP = ("Segoe UI", 11)
FONT_BTN = ("Segoe UI", 12, "bold")

# Spacing
PX = 20
GAP = 8

# For each risk level: colour, emoji, and a short advice line
RESULT_DISPLAY = {
    "high": (
        RED,
        "\U000026a0\U0000fe0f",
        "Score came back high. Please think about talking to a counselor or "
        "someone you trust. Sleep, food and a little bit of activity every "
        "day really do help. You don't have to deal with this alone.",
    ),
    "moderate": (
        ORANGE,
        "\U0001f7e1",
        "Score is in the middle. Try to keep a steady routine, make time for "
        "things you actually enjoy, and reach out to someone if you stay low "
        "for too long.",
    ),
    "low": (
        GREEN,
        "\U00002705",
        "Score is low - that's a good sign. Keep your basics steady (sleep, "
        "food, exercise, friends) and don't let stress pile up.",
    ),
}


class DepressionApp:
    def __init__(self):
        ctk.set_appearance_mode("dark")

        self.app = ctk.CTk()
        self.app.title("Student Depression Prediction")
        self.app.configure(fg_color=BG_DARK)
        # "zoomed" is the Windows full-window state. On Linux/macOS Tk
        # raises TclError - fall back to a sensible default size.
        self.app.after(0, self._maximize)

        # Values are stored as 1-element lists because predict() wraps them
        # into a pandas DataFrame
        self.answers = {
            "Gender": [None],
            "Age": [None],
            "Work/Study Hours": [None],
            "Academic Pressure": [SLIDER_DEFAULT],
            "Financial Stress": [SLIDER_DEFAULT],
            "Study Satisfaction": [SLIDER_DEFAULT],
            "Sleep Duration": [None],
            "Dietary Habits": [None],
            "Have you ever had suicidal thoughts ?": [None],
            "Family History of Mental Illness": [None],
        }

        self.result_text = ctk.StringVar()
        self.tip_text = ctk.StringVar()
        self.academic_text = ctk.StringVar(value=str(int(SLIDER_DEFAULT)))
        self.financial_text = ctk.StringVar(value=str(int(SLIDER_DEFAULT)))
        self.satisfaction_text = ctk.StringVar(value=str(int(SLIDER_DEFAULT)))

        self._build_ui()

    def _maximize(self):
        try:
            self.app.state("zoomed")
        except Exception:
            self.app.geometry("980x720")

    # Callbacks

    def _on_slider(self, value, key, text_var):
        text_var.set(str(int(value)))
        self.answers[key][0] = value

    def _on_combo(self, value, key):
        self.answers[key][0] = value

    # Build the UI

    def _build_ui(self):
        scroll = ctk.CTkScrollableFrame(self.app, fg_color=BG_DARK, corner_radius=0)
        scroll.pack(fill="both", expand=True)
        root = scroll

        # Header
        header = ctk.CTkFrame(root, fg_color="transparent")
        header.pack(pady=(14, 0))

        ctk.CTkLabel(
            header,
            text="\U0001f9e0",
            font=("Segoe UI Emoji", 28),
            text_color=ACCENT,
        ).pack(side="left", padx=(0, 10))

        ctk.CTkLabel(
            header,
            text="Student Depression Prediction",
            font=FONT_TITLE,
            text_color=TEXT_BRIGHT,
        ).pack(side="left")

        ctk.CTkFrame(root, height=2, fg_color=ACCENT, corner_radius=1).pack(
            fill="x", padx=PX + 80, pady=(6, 0)
        )

        ctk.CTkLabel(
            root,
            text="Fill in the details below to estimate depression risk",
            font=FONT_SMALL,
            text_color=TEXT_DIM,
        ).pack(pady=(4, GAP))

        # Personal info section
        ctk.CTkLabel(
            root, text="\U0001f464  Personal Info", font=FONT_SECTION, text_color=TEXT_MID
        ).pack(anchor="w", padx=PX, pady=(0, 3))

        c1 = ctk.CTkFrame(
            root, fg_color=BG_CARD, corner_radius=10, border_width=1, border_color=BORDER
        )
        c1.pack(fill="x", padx=PX, pady=(0, GAP))
        row1 = ctk.CTkFrame(c1, fg_color="transparent")
        row1.pack(fill="x", padx=14, pady=10)

        f1 = ctk.CTkFrame(row1, fg_color="transparent")
        f1.pack(side="left", padx=(0, 14))
        ctk.CTkLabel(f1, text="Age (18-34)", font=FONT_SMALL, text_color=TEXT_DIM).pack(anchor="w")
        self.entry_age = ctk.CTkEntry(
            f1,
            justify="center",
            width=75,
            height=34,
            border_color=BORDER,
            fg_color=BG_INPUT,
            placeholder_text="24",
            font=FONT_SMALL,
            corner_radius=8,
        )
        self.entry_age.pack(pady=(2, 0))

        f2 = ctk.CTkFrame(row1, fg_color="transparent")
        f2.pack(side="left", padx=(0, 14))
        ctk.CTkLabel(f2, text="Study Hrs (0-12)", font=FONT_SMALL, text_color=TEXT_DIM).pack(
            anchor="w"
        )
        self.entry_study = ctk.CTkEntry(
            f2,
            justify="center",
            width=95,
            height=34,
            border_color=BORDER,
            fg_color=BG_INPUT,
            placeholder_text="8",
            font=FONT_SMALL,
            corner_radius=8,
        )
        self.entry_study.pack(pady=(2, 0))

        f3 = ctk.CTkFrame(row1, fg_color="transparent")
        f3.pack(side="left")
        ctk.CTkLabel(f3, text="Gender", font=FONT_SMALL, text_color=TEXT_DIM).pack(anchor="w")
        self.combo_gender = ctk.CTkComboBox(
            f3,
            values=GENDER_OPTIONS,
            justify="center",
            width=150,
            height=34,
            state="readonly",
            command=lambda v: self._on_combo(v, "Gender"),
            border_color=BORDER,
            button_color=ACCENT,
            button_hover_color="#58a6ff",
            fg_color=BG_INPUT,
            font=FONT_SMALL,
            dropdown_font=FONT_SMALL,
            corner_radius=8,
        )
        self.combo_gender.set("Select")
        self.combo_gender.pack(pady=(2, 0))

        # Lifestyle section
        ctk.CTkLabel(
            root, text="\U0001f34e  Lifestyle", font=FONT_SECTION, text_color=TEXT_MID
        ).pack(anchor="w", padx=PX, pady=(0, 3))

        c2 = ctk.CTkFrame(
            root, fg_color=BG_CARD, corner_radius=10, border_width=1, border_color=BORDER
        )
        c2.pack(fill="x", padx=PX, pady=(0, GAP))
        row2 = ctk.CTkFrame(c2, fg_color="transparent")
        row2.pack(fill="x", padx=14, pady=10)

        f4 = ctk.CTkFrame(row2, fg_color="transparent")
        f4.pack(side="left", padx=(0, 14))
        ctk.CTkLabel(f4, text="Diet", font=FONT_SMALL, text_color=TEXT_DIM).pack(anchor="w")
        self.combo_diet = ctk.CTkComboBox(
            f4,
            values=DIET_OPTIONS,
            justify="center",
            width=170,
            height=34,
            state="readonly",
            command=lambda v: self._on_combo(v, "Dietary Habits"),
            border_color=BORDER,
            button_color=ACCENT,
            button_hover_color="#58a6ff",
            fg_color=BG_INPUT,
            font=FONT_SMALL,
            dropdown_font=FONT_SMALL,
            corner_radius=8,
        )
        self.combo_diet.set("Select")
        self.combo_diet.pack(pady=(2, 0))

        f5 = ctk.CTkFrame(row2, fg_color="transparent")
        f5.pack(side="left")
        ctk.CTkLabel(f5, text="Sleep Duration", font=FONT_SMALL, text_color=TEXT_DIM).pack(
            anchor="w"
        )
        self.combo_sleep = ctk.CTkComboBox(
            f5,
            values=SLEEP_OPTIONS,
            justify="center",
            width=190,
            height=34,
            state="readonly",
            command=lambda v: self._on_combo(v, "Sleep Duration"),
            border_color=BORDER,
            button_color=ACCENT,
            button_hover_color="#58a6ff",
            fg_color=BG_INPUT,
            font=FONT_SMALL,
            dropdown_font=FONT_SMALL,
            corner_radius=8,
        )
        self.combo_sleep.set("Select")
        self.combo_sleep.pack(pady=(2, 0))

        # Stress and satisfaction section
        ctk.CTkLabel(
            root,
            text="\U0001f4ca  Stress & Satisfaction",
            font=FONT_SECTION,
            text_color=TEXT_MID,
        ).pack(anchor="w", padx=PX, pady=(0, 3))

        c3 = ctk.CTkFrame(
            root, fg_color=BG_CARD, corner_radius=10, border_width=1, border_color=BORDER
        )
        c3.pack(fill="x", padx=PX, pady=(0, GAP))

        slider_rows = [
            ("Academic Pressure", "Academic Pressure", self.academic_text, (10, 2)),
            ("Financial Stress", "Financial Stress", self.financial_text, (2, 2)),
            ("Study Satisfaction", "Study Satisfaction", self.satisfaction_text, (2, 10)),
        ]
        # Save the sliders so the Reset button can put them back later
        self.slider_widgets = []
        for label_text, key, text_var, pady in slider_rows:
            row = ctk.CTkFrame(c3, fg_color="transparent")
            ctk.CTkLabel(
                row,
                text=label_text,
                font=FONT_LABEL,
                text_color=TEXT_MID,
                width=140,
                anchor="w",
            ).pack(side="left")
            slider = ctk.CTkSlider(
                row,
                width=250,
                height=16,
                button_color=ACCENT,
                button_hover_color="#58a6ff",
                progress_color="#1a3a5c",
                fg_color=BG_INPUT,
                from_=SLIDER_MIN,
                to=SLIDER_MAX,
                number_of_steps=SLIDER_STEPS,
                command=lambda v, k=key, tv=text_var: self._on_slider(v, k, tv),
            )
            slider.set(SLIDER_DEFAULT)
            slider.pack(side="left", padx=(0, 10))
            ctk.CTkLabel(
                row, textvariable=text_var, font=FONT_LABEL, text_color=ACCENT, width=20
            ).pack(side="left")
            row.pack(fill="x", padx=14, pady=pady)
            self.slider_widgets.append((slider, text_var, key))

        # Mental health history section
        ctk.CTkLabel(
            root,
            text="\U0001f49c  Mental Health History",
            font=FONT_SECTION,
            text_color=TEXT_MID,
        ).pack(anchor="w", padx=PX, pady=(0, 3))

        c4 = ctk.CTkFrame(
            root, fg_color=BG_CARD, corner_radius=10, border_width=1, border_color=BORDER
        )
        c4.pack(fill="x", padx=PX, pady=(0, GAP))
        chk_row = ctk.CTkFrame(c4, fg_color="transparent")
        chk_row.pack(fill="x", padx=14, pady=10)

        self.checkbox_suicidal = ctk.CTkCheckBox(
            chk_row,
            text="Has had suicidal thoughts",
            border_width=2,
            checkmark_color="#ffffff",
            fg_color=ACCENT,
            border_color=BORDER,
            hover_color="#1a3a5c",
            font=FONT_SMALL,
            corner_radius=4,
        )
        self.checkbox_suicidal.pack(side="left", padx=(0, 20))

        self.checkbox_family = ctk.CTkCheckBox(
            chk_row,
            text="Family history of depression",
            border_width=2,
            checkmark_color="#ffffff",
            fg_color=ACCENT,
            border_color=BORDER,
            hover_color="#1a3a5c",
            font=FONT_SMALL,
            corner_radius=4,
        )
        self.checkbox_family.pack(side="left")

        # Result section (button + output)
        c5 = ctk.CTkFrame(
            root, fg_color=BG_CARD, corner_radius=10, border_width=1, border_color=BORDER
        )
        c5.pack(fill="x", padx=PX, pady=(GAP + 2, 16))

        btn_row = ctk.CTkFrame(c5, fg_color="transparent")
        btn_row.pack(pady=(12, 6))

        self.btn_calculate = ctk.CTkButton(
            btn_row,
            text="\U0001f50d  Calculate Results",
            height=42,
            width=220,
            command=self._calculate,
            text_color="#ffffff",
            fg_color=ACCENT,
            hover_color="#58a6ff",
            font=FONT_BTN,
            corner_radius=10,
        )
        self.btn_calculate.pack(side="left", padx=(0, 8))

        self.btn_history = ctk.CTkButton(
            btn_row,
            text="\U0001f4dc  View History",
            height=42,
            width=140,
            command=self._open_history,
            text_color=TEXT_BRIGHT,
            fg_color=BG_INPUT,
            hover_color="#1a3a5c",
            font=FONT_BTN,
            corner_radius=10,
            border_width=1,
            border_color=BORDER,
        )
        self.btn_history.pack(side="left", padx=(0, 8))

        self.btn_reset = ctk.CTkButton(
            btn_row,
            text="\u21bb  Reset",
            height=42,
            width=110,
            command=self._reset,
            text_color=TEXT_DIM,
            fg_color=BG_INPUT,
            hover_color="#1a3a5c",
            font=FONT_BTN,
            corner_radius=10,
            border_width=1,
            border_color=BORDER,
        )
        self.btn_reset.pack(side="left")

        self.label_result = ctk.CTkLabel(
            c5,
            textvariable=self.result_text,
            font=FONT_RESULT,
            text_color=TEXT_BRIGHT,
        )
        self.label_result.pack(pady=(2, 0))

        # Progress bar that fills up with the depression probability
        self.progress = ctk.CTkProgressBar(
            c5,
            width=440,
            height=14,
            fg_color=BG_INPUT,
            progress_color=ACCENT,
            corner_radius=7,
        )
        self.progress.set(0)
        self.progress.pack(pady=(8, 0))

        self.label_tip = ctk.CTkLabel(
            c5,
            textvariable=self.tip_text,
            font=FONT_TIP,
            text_color=TEXT_DIM,
            wraplength=500,
            justify="center",
        )
        self.label_tip.pack(padx=20, pady=(4, 14))

        # Hitting Enter from the text fields runs Calculate
        self.entry_age.bind("<Return>", lambda e: self._calculate())
        self.entry_study.bind("<Return>", lambda e: self._calculate())

    # Prediction logic

    def _collect_inputs(self):
        # Read the widgets into self.answers. Return False if something is wrong.
        age_result = validate_age(self.entry_age.get())
        if not age_result.valid:
            self._show_error(age_result.error)
            return False

        study_result = validate_study_hours(self.entry_study.get())
        if not study_result.valid:
            self._show_error(study_result.error)
            return False

        self.answers["Age"][0] = float(int(self.entry_age.get().strip()))
        self.answers["Work/Study Hours"][0] = float(int(self.entry_study.get().strip()))

        self.answers["Have you ever had suicidal thoughts ?"][0] = (
            "Yes" if self.checkbox_suicidal.get() else "No"
        )
        self.answers["Family History of Mental Illness"][0] = (
            "Yes" if self.checkbox_family.get() else "No"
        )
        return True

    def _show_error(self, msg):
        self.label_result.configure(text_color=RED)
        self.result_text.set(msg)
        self.tip_text.set("")
        self.progress.set(0)

    def _show_result(self, probability):
        color, icon, tip = RESULT_DISPLAY[risk_level(probability)]
        self.label_result.configure(text_color=color)
        self.result_text.set(f"{icon}  Depression probability: {probability:.1f}%")
        self.label_tip.configure(text_color=TEXT_MID)
        self.tip_text.set(tip)
        self.progress.configure(progress_color=color)
        self.progress.set(probability / 100)

    def _reset(self):
        # Clear all the inputs and the result
        self.entry_age.delete(0, "end")
        self.entry_study.delete(0, "end")
        self.combo_gender.set("Select")
        self.combo_diet.set("Select")
        self.combo_sleep.set("Select")
        self.checkbox_suicidal.deselect()
        self.checkbox_family.deselect()

        # Put the sliders back to their default
        slider_keys = set()
        for slider, text_var, key in self.slider_widgets:
            slider.set(SLIDER_DEFAULT)
            text_var.set(str(int(SLIDER_DEFAULT)))
            self.answers[key][0] = SLIDER_DEFAULT
            slider_keys.add(key)

        # Everything else gets cleared (None means "not answered yet")
        for key in self.answers:
            if key not in slider_keys:
                self.answers[key][0] = None

        self.result_text.set("")
        self.tip_text.set("")
        self.progress.set(0)

    def _calculate(self):
        # Run a prediction and show the result on screen
        if not self._collect_inputs():
            return

        if not all_fields_filled(self.answers):
            self._show_error("Please fill in all fields.")
            return

        try:
            result = predict(self.answers) * 100
            logger.info("Prediction result: %.2f%%", result)
            self._show_result(result)
            self._persist_prediction(result)
        except Exception:
            logger.exception("Prediction failed")
            self._show_error("Something went wrong. Please try again.")

    def _persist_prediction(self, probability):
        # Save to the DB - if it fails we just log it, the UI keeps working
        record = {
            api_key: self.answers[model_key][0]
            for model_key, api_key in FIELD_NAME_MAP.items()
        }

        try:
            save_prediction(
                request_id=str(uuid.uuid4()),
                input_data=record,
                probability=round(probability, 2),
                risk_level=risk_level(probability),
            )
        except Exception:
            logger.exception("Failed to save prediction (non-fatal)")

    def _open_history(self):
        # Open a small window showing the last 20 predictions
        try:
            rows = get_predictions(limit=20)
        except Exception:
            logger.exception("Could not load history")
            self._show_error("Could not load history.")
            return

        win = ctk.CTkToplevel(self.app)
        win.title("Prediction History")
        win.geometry("520x460")
        win.configure(fg_color=BG_DARK)

        ctk.CTkLabel(
            win,
            text="\U0001f4dc  Recent Predictions",
            font=FONT_TITLE,
            text_color=TEXT_BRIGHT,
        ).pack(pady=(14, 8))

        if not rows:
            ctk.CTkLabel(
                win,
                text="No predictions yet. Run one first!",
                font=FONT_LABEL,
                text_color=TEXT_DIM,
            ).pack(pady=20)
            return

        scroll = ctk.CTkScrollableFrame(win, fg_color=BG_DARK)
        scroll.pack(fill="both", expand=True, padx=14, pady=(0, 14))

        for r in rows:
            colors = {"high": RED, "moderate": ORANGE, "low": GREEN}
            color = colors.get(r["risk_level"], TEXT_BRIGHT)

            card = ctk.CTkFrame(
                scroll,
                fg_color=BG_CARD,
                corner_radius=8,
                border_width=1,
                border_color=BORDER,
            )
            card.pack(fill="x", pady=4)

            ctk.CTkLabel(
                card,
                text=f"{r['probability']:.1f}%   {r['risk_level'].upper()}",
                font=FONT_RESULT,
                text_color=color,
            ).pack(anchor="w", padx=12, pady=(8, 0))

            ctk.CTkLabel(
                card,
                text=r["timestamp"],
                font=FONT_SMALL,
                text_color=TEXT_DIM,
            ).pack(anchor="w", padx=12, pady=(0, 8))

    def run(self):
        self.app.mainloop()


def initialize():
    app = DepressionApp()
    app.run()
