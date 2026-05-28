# Web app that gets served on Hugging Face / any docker host.
# The Gradio form runs at "/" and the API endpoints (/health, /predict,
# /predictions, /docs) sit on top of the same FastAPI instance.
#
# Run locally:  uvicorn app:app --host 0.0.0.0 --port 7860

import gradio as gr

from src.api import app as fastapi_app
from src.config import DIET_OPTIONS, GENDER_OPTIONS, SLEEP_OPTIONS
from src.database import clear_predictions, count_by_risk_level, get_predictions
from src.model_definition import predict, risk_level

# Colours from the desktop GUI - keeps the look consistent
BG_DARK = "#0d1117"
BG_CARD = "#161b22"
BG_INPUT = "#1c2333"
ACCENT = "#1f6feb"
ACCENT_HOVER = "#58a6ff"
GREEN = "#3fb950"
ORANGE = "#d29922"
RED = "#f85149"
BORDER = "#30363d"
BORDER_HOVER = "#484f58"
TEXT_BRIGHT = "#e6edf3"
TEXT_DIM = "#7d8590"

# Per-risk-level advice, same wording as the desktop GUI
RESULT_DISPLAY = {
    "high": (
        RED,
        "⚠️",
        "Score came back high. Please think about talking to a counselor or "
        "someone you trust. Sleep, food and a little bit of activity every "
        "day really do help. You don't have to deal with this alone.",
    ),
    "moderate": (
        ORANGE,
        "🟡",
        "Score is in the middle. Try to keep a steady routine, make time for "
        "things you actually enjoy, and reach out to someone if you stay low "
        "for too long.",
    ),
    "low": (
        GREEN,
        "✅",
        "Score is low - that's a good sign. Keep your basics steady (sleep, "
        "food, exercise, friends) and don't let stress pile up.",
    ),
}

COLOR_BY_LEVEL = {"high": RED, "moderate": ORANGE, "low": GREEN}


def run_prediction(
    gender,
    age,
    study_hours,
    academic_pressure,
    financial_stress,
    study_satisfaction,
    sleep_duration,
    dietary_habits,
    suicidal_thoughts,
    family_history,
):
    answers = {
        "Gender": [gender],
        "Age": [float(age)],
        "Work/Study Hours": [float(study_hours)],
        "Academic Pressure": [float(academic_pressure)],
        "Financial Stress": [float(financial_stress)],
        "Study Satisfaction": [float(study_satisfaction)],
        "Sleep Duration": [sleep_duration],
        "Dietary Habits": [dietary_habits],
        "Have you ever had suicidal thoughts ?": ["Yes" if suicidal_thoughts else "No"],
        "Family History of Mental Illness": ["Yes" if family_history else "No"],
    }

    probability = predict(answers) * 100
    level = risk_level(probability)
    color, icon, tip = RESULT_DISPLAY[level]

    return (
        f"<div class='result-card' style='border:1px solid {color};'>"
        f"<div class='result-prob' style='color:{color};'>"
        f"{icon}&nbsp;&nbsp;Depression probability: {probability:.1f}%"
        f"</div>"
        f"<div class='result-level' style='color:{color};'>"
        f"RISK LEVEL: {level.upper()}"
        f"</div>"
        f"<div class='result-bar-track'>"
        f"<div class='result-bar-fill' style='width:{probability:.1f}%;background:{color};'></div>"
        f"</div>"
        f"<div class='result-tip'>{tip}</div>"
        f"</div>"
    )


def reset_form():
    # Put every input back to its starting value
    return ("Male", 22, 8, 3, 3, 3, "7-8 hours", "Moderate", False, False, "")


def build_history_html():
    # Render a stats line + a card per past prediction
    rows = get_predictions(limit=50)
    counts = count_by_risk_level()
    total = sum(counts.values())

    if total == 0:
        return (
            f"<div style='text-align:center;padding:30px;color:{TEXT_DIM};'>"
            "No predictions yet. Run one from the <b>Predict</b> tab first."
            "</div>"
        )

    # Stats summary at the top
    high = counts.get("high", 0)
    moderate = counts.get("moderate", 0)
    low = counts.get("low", 0)
    stats_html = (
        f"<div class='stats-row'>"
        f"<div class='stat-card'><div class='stat-num'>{total}</div>"
        f"<div class='stat-label'>TOTAL</div></div>"
        f"<div class='stat-card'><div class='stat-num' style='color:{GREEN};'>{low}</div>"
        f"<div class='stat-label'>LOW</div></div>"
        f"<div class='stat-card'><div class='stat-num' style='color:{ORANGE};'>{moderate}</div>"
        f"<div class='stat-label'>MODERATE</div></div>"
        f"<div class='stat-card'><div class='stat-num' style='color:{RED};'>{high}</div>"
        f"<div class='stat-label'>HIGH</div></div>"
        f"</div>"
    )

    # One card per row
    cards = []
    for r in rows:
        color = COLOR_BY_LEVEL.get(r["risk_level"], TEXT_BRIGHT)
        cards.append(
            f"<div class='history-card'>"
            f"<div style='color:{color};font-size:18px;font-weight:700;'>"
            f"{r['probability']:.1f}% &nbsp;·&nbsp; {r['risk_level'].upper()}"
            f"</div>"
            f"<div style='color:{TEXT_DIM};font-size:12px;margin-top:4px;'>"
            f"{r['timestamp']}"
            f"</div>"
            f"</div>"
        )

    return stats_html + "<div class='history-list'>" + "".join(cards) + "</div>"


def clear_history():
    clear_predictions()
    return build_history_html()


# CSS for the dark theme + hover/focus polish + history layout
CUSTOM_CSS = f"""
.gradio-container {{
    background: {BG_DARK} !important;
    max-width: 980px !important;
    margin: 0 auto !important;
}}
#title-row {{ text-align: center; padding: 12px 0 0 0; }}
#title-row h1 {{ color: {TEXT_BRIGHT}; margin: 0; font-weight: 600; letter-spacing: -0.5px; }}
#subtitle {{ color: {TEXT_DIM}; text-align: center; margin: 2px 0 14px 0; font-size: 13px; }}
.section-label {{
    color: {TEXT_DIM};
    font-weight: 700;
    margin: 14px 0 4px 4px;
    font-size: 13px;
    letter-spacing: 0.5px;
}}
.section-card {{
    background: {BG_CARD} !important;
    border: 1px solid {BORDER} !important;
    border-radius: 10px !important;
    padding: 14px !important;
    transition: border-color 0.15s ease, box-shadow 0.15s ease;
}}
.section-card:hover {{
    border-color: {BORDER_HOVER} !important;
    box-shadow: 0 0 0 1px {BORDER_HOVER}33;
}}
input, select, textarea {{ transition: border-color 0.15s ease, box-shadow 0.15s ease !important; }}
input:focus, select:focus, textarea:focus {{
    border-color: {ACCENT} !important;
    box-shadow: 0 0 0 2px {ACCENT}33 !important;
    outline: none !important;
}}
button.primary, button.lg.primary {{
    background: {ACCENT} !important;
    border: none !important;
    color: #fff !important;
    transition: background 0.15s ease, transform 0.05s ease, box-shadow 0.15s ease !important;
}}
button.primary:hover {{ background: {ACCENT_HOVER} !important; box-shadow: 0 4px 12px {ACCENT}55 !important; }}
button.primary:active {{ transform: translateY(1px); }}
button.secondary {{
    background: {BG_INPUT} !important;
    border: 1px solid {BORDER} !important;
    color: {TEXT_BRIGHT} !important;
    transition: background 0.15s ease, border-color 0.15s ease !important;
}}
button.secondary:hover {{ background: #1a3a5c !important; border-color: {ACCENT} !important; }}
button.stop {{
    background: {RED} !important;
    color: #fff !important;
    transition: background 0.15s ease !important;
}}
button.stop:hover {{ background: #c82a3a !important; }}
.result-card {{
    text-align: center;
    padding: 18px;
    border-radius: 10px;
    background: {BG_CARD};
    animation: fadeIn 0.25s ease;
}}
@keyframes fadeIn {{
    from {{ opacity: 0; transform: translateY(4px); }}
    to {{ opacity: 1; transform: translateY(0); }}
}}
.result-prob {{ font-size: 20px; font-weight: 700; }}
.result-level {{ margin: 4px 0 14px 0; font-weight: 600; letter-spacing: 0.5px; }}
.result-bar-track {{
    height: 14px;
    background: {BG_INPUT};
    border-radius: 7px;
    overflow: hidden;
    margin: 0 auto 14px auto;
    max-width: 560px;
}}
.result-bar-fill {{ height: 100%; transition: width 0.4s ease-out; }}
.result-tip {{ color: {TEXT_DIM}; font-size: 14px; max-width: 560px; margin: 0 auto; line-height: 1.45; }}

/* Stats row + history cards */
.stats-row {{
    display: flex;
    gap: 12px;
    margin: 4px 0 14px 0;
}}
.stat-card {{
    flex: 1;
    background: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 10px;
    padding: 14px 8px;
    text-align: center;
    transition: border-color 0.15s ease;
}}
.stat-card:hover {{ border-color: {BORDER_HOVER}; }}
.stat-num {{ font-size: 24px; font-weight: 700; color: {TEXT_BRIGHT}; }}
.stat-label {{ font-size: 11px; color: {TEXT_DIM}; letter-spacing: 1px; margin-top: 2px; }}
.history-list {{ display: flex; flex-direction: column; gap: 8px; }}
.history-card {{
    background: {BG_CARD};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 12px 14px;
    transition: border-color 0.15s ease, transform 0.05s ease;
}}
.history-card:hover {{ border-color: {BORDER_HOVER}; }}

/* Hide Gradio's built-in footer */
footer {{ display: none !important; }}
"""


with gr.Blocks(title="Student Depression Prediction", css=CUSTOM_CSS, theme=gr.themes.Base()) as demo:
    with gr.Row(elem_id="title-row"):
        gr.Markdown("# 🧠 Student Depression Risk Prediction")
    gr.Markdown("<div id='subtitle'>Fill in the details below to estimate depression risk</div>")

    with gr.Tabs():
        with gr.Tab("🔍 Predict"):
            gr.Markdown("<div class='section-label'>👤  PERSONAL INFO</div>")
            with gr.Group(elem_classes="section-card"):
                with gr.Row():
                    age_in = gr.Number(label="Age (18-34)", value=22, minimum=18, maximum=34, precision=0)
                    study_in = gr.Number(
                        label="Work/Study Hours (0-12)", value=8, minimum=0, maximum=12, precision=0
                    )
                    gender_in = gr.Radio(choices=GENDER_OPTIONS, label="Gender", value="Male")

            gr.Markdown("<div class='section-label'>🌿  LIFESTYLE</div>")
            with gr.Group(elem_classes="section-card"):
                with gr.Row():
                    diet_in = gr.Dropdown(choices=DIET_OPTIONS, label="Dietary Habits", value="Moderate")
                    sleep_in = gr.Dropdown(choices=SLEEP_OPTIONS, label="Sleep Duration", value="7-8 hours")

            gr.Markdown("<div class='section-label'>📊  STRESS & SATISFACTION</div>")
            with gr.Group(elem_classes="section-card"):
                academic_in = gr.Slider(1, 5, value=3, step=1, label="Academic Pressure")
                financial_in = gr.Slider(1, 5, value=3, step=1, label="Financial Stress")
                satisfaction_in = gr.Slider(1, 5, value=3, step=1, label="Study Satisfaction")

            gr.Markdown("<div class='section-label'>💭  MENTAL HEALTH HISTORY</div>")
            with gr.Group(elem_classes="section-card"):
                with gr.Row():
                    suicidal_in = gr.Checkbox(label="Has had suicidal thoughts")
                    family_in = gr.Checkbox(label="Family history of depression")

            with gr.Group(elem_classes="section-card"):
                with gr.Row():
                    submit = gr.Button("🔍 Calculate Result", variant="primary", size="lg", scale=2)
                    reset_btn = gr.Button("↻ Reset", variant="secondary", size="lg", scale=1)
                result_out = gr.HTML()

            all_inputs = [
                gender_in, age_in, study_in,
                academic_in, financial_in, satisfaction_in,
                sleep_in, diet_in, suicidal_in, family_in,
            ]
            gr.Examples(
                examples=[
                    ["Male",   22, 4,  1, 1, 5, "7-8 hours",         "Healthy",   False, False],
                    ["Female", 24, 8,  3, 3, 3, "5-6 hours",         "Moderate",  False, False],
                    ["Male",   24, 12, 5, 5, 1, "Less than 5 hours", "Unhealthy", True,  True],
                ],
                inputs=all_inputs,
                label="Or try a sample profile (low / moderate / high risk)",
            )

        with gr.Tab("📜 History") as history_tab:
            history_out = gr.HTML(value=build_history_html())
            with gr.Row():
                refresh_btn = gr.Button("↻ Refresh", variant="secondary")
                clear_btn = gr.Button("🗑️ Clear All History", variant="stop")

    submit.click(run_prediction, inputs=all_inputs, outputs=result_out)
    submit.click(build_history_html, outputs=history_out)  # keep history tab in sync
    reset_btn.click(reset_form, inputs=None, outputs=all_inputs + [result_out])
    refresh_btn.click(build_history_html, outputs=history_out)
    clear_btn.click(clear_history, outputs=history_out)
    history_tab.select(build_history_html, outputs=history_out)  # refresh on tab open


# Glue: serve the Gradio UI at "/" but keep all the FastAPI endpoints alive
app = gr.mount_gradio_app(fastapi_app, demo, path="/")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=7860)
