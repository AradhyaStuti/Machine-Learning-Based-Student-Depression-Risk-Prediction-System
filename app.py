# Web app that gets served on Hugging Face / any docker host.
# The Gradio form runs at "/" and the API endpoints (/health, /predict,
# /predictions, /docs) sit on top of the same FastAPI instance.
#
# Run locally:  uvicorn app:app --host 0.0.0.0 --port 7860

import uuid

import gradio as gr

from src.api import app as fastapi_app
from src.config import DIET_OPTIONS, GENDER_OPTIONS, SLEEP_OPTIONS
from src.database import (
    clear_predictions,
    count_by_risk_level,
    delete_prediction,
    get_predictions,
    init_db,
    save_prediction,
)
from src.model_definition import FIELD_NAME_MAP, predict, risk_level

# Make sure the predictions table exists before the Gradio UI reads from it
init_db()

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
EMOJI_BY_LEVEL = {"high": "🔴", "moderate": "🟡", "low": "🟢"}

# Sample profiles - shown in both the Examples block (clickable templates)
# and seeded into the DB on first launch so History isn't empty on day one
SAMPLE_PROFILES = [
    {"gender": "Male",   "age": 22, "study_hours": 4,  "academic_pressure": 1,
     "financial_stress": 1, "study_satisfaction": 5, "sleep_duration": "7-8 hours",
     "dietary_habits": "Healthy",   "suicidal_thoughts": "No",  "family_history": "No"},
    {"gender": "Female", "age": 24, "study_hours": 8,  "academic_pressure": 3,
     "financial_stress": 3, "study_satisfaction": 3, "sleep_duration": "5-6 hours",
     "dietary_habits": "Moderate",  "suicidal_thoughts": "No",  "family_history": "No"},
    {"gender": "Male",   "age": 24, "study_hours": 12, "academic_pressure": 5,
     "financial_stress": 5, "study_satisfaction": 1, "sleep_duration": "Less than 5 hours",
     "dietary_habits": "Unhealthy", "suicidal_thoughts": "Yes", "family_history": "Yes"},
]


def _payload_to_answers(payload):
    # Snake-case API dict -> the dict shape predict() expects
    return {model_key: [payload[api_key]] for model_key, api_key in FIELD_NAME_MAP.items()}


def seed_demo_predictions_if_empty():
    # Run the three sample profiles once so the History tab has content
    # on the very first visit. Skipped if any predictions already exist.
    try:
        if get_predictions(limit=1):
            return
        for payload in SAMPLE_PROFILES:
            probability = predict(_payload_to_answers(payload)) * 100
            save_prediction(
                request_id=str(uuid.uuid4()),
                input_data=payload,
                probability=round(probability, 2),
                risk_level=risk_level(probability),
            )
    except Exception:
        # Best-effort: never crash startup over demo seeding
        pass


seed_demo_predictions_if_empty()


def run_prediction(
    gender, age, study_hours, academic_pressure, financial_stress, study_satisfaction,
    sleep_duration, dietary_habits, suicidal_thoughts, family_history,
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

    # Persist this run so it shows up in the History tab too
    try:
        save_prediction(
            request_id=str(uuid.uuid4()),
            input_data={api_key: answers[model_key][0]
                        for model_key, api_key in FIELD_NAME_MAP.items()},
            probability=round(probability, 2),
            risk_level=level,
        )
    except Exception:
        pass

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
    return ("Male", 22, 8, 3, 3, 3, "7-8 hours", "Moderate", False, False, "")


def build_stats_html():
    # Stats row at the top of the History tab
    try:
        counts = count_by_risk_level()
    except Exception:
        return ""
    total = sum(counts.values())
    high = counts.get("high", 0)
    moderate = counts.get("moderate", 0)
    low = counts.get("low", 0)
    return (
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


def history_rows():
    # Return rows for the Dataframe: [id, time, probability, risk]
    try:
        rows = get_predictions(limit=50)
    except Exception:
        return []
    out = []
    for r in rows:
        # Trim ISO timestamp to "YYYY-MM-DD HH:MM" for readability
        ts = (r["timestamp"] or "").replace("T", " ").split(".")[0][:16]
        level = r["risk_level"]
        emoji = EMOJI_BY_LEVEL.get(level, "")
        out.append([r["id"], ts, f"{r['probability']:.1f}%", f"{emoji} {level.upper()}"])
    return out


def refresh_history():
    return build_stats_html(), history_rows()


def on_history_row_select(evt: gr.SelectData, table):
    # Capture the ID of the clicked row so the Delete-Selected button knows what to remove
    if evt.index is None or not table:
        return None, "<span style='color:" + TEXT_DIM + ";'>No row selected.</span>"
    row_idx = evt.index[0] if isinstance(evt.index, list) else evt.index
    try:
        # table can be a list-of-lists or a DataFrame depending on Gradio version
        if hasattr(table, "iloc"):
            row_id = table.iloc[row_idx, 0]
        else:
            row_id = table[row_idx][0]
    except Exception:
        return None, "<span style='color:" + TEXT_DIM + ";'>Could not read that row.</span>"
    return int(row_id), (
        f"<span style='color:{ACCENT};'>Row #{int(row_id)} selected. "
        f"Click <b>Delete Selected</b> to remove just this one.</span>"
    )


def delete_one(selected_id):
    if selected_id is None:
        stats, rows = refresh_history()
        return stats, rows, None, (
            f"<span style='color:{TEXT_DIM};'>Click a row in the table first.</span>"
        )
    delete_prediction(int(selected_id))
    stats, rows = refresh_history()
    return stats, rows, None, (
        f"<span style='color:{TEXT_DIM};'>Deleted row #{int(selected_id)}.</span>"
    )


def clear_all():
    clear_predictions()
    stats, rows = refresh_history()
    return stats, rows, None, f"<span style='color:{TEXT_DIM};'>History cleared.</span>"


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
button.stop {{ background: {RED} !important; color: #fff !important; transition: background 0.15s ease !important; }}
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

.stats-row {{ display: flex; gap: 12px; margin: 4px 0 14px 0; }}
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
                    [p["gender"], p["age"], p["study_hours"],
                     p["academic_pressure"], p["financial_stress"], p["study_satisfaction"],
                     p["sleep_duration"], p["dietary_habits"],
                     p["suicidal_thoughts"] == "Yes", p["family_history"] == "Yes"]
                    for p in SAMPLE_PROFILES
                ],
                inputs=all_inputs,
                label="Or try a sample profile (low / moderate / high risk)",
            )

        with gr.Tab("📜 History") as history_tab:
            stats_html = gr.HTML(value=build_stats_html())
            history_table = gr.Dataframe(
                headers=["ID", "Time (UTC)", "Probability", "Risk"],
                value=history_rows(),
                interactive=False,
                wrap=True,
                row_count=(0, "dynamic"),
            )
            selection_msg = gr.HTML(
                value=f"<span style='color:{TEXT_DIM};'>Click a row in the table to select it for deletion.</span>"
            )
            selected_id_state = gr.State(value=None)
            with gr.Row():
                refresh_btn = gr.Button("↻ Refresh", variant="secondary", scale=1)
                delete_selected_btn = gr.Button(
                    "🗑️ Delete Selected", variant="secondary", scale=1
                )
                clear_btn = gr.Button("🗑️ Clear All History", variant="stop", scale=1)

    # Wire everything up
    submit.click(run_prediction, inputs=all_inputs, outputs=result_out)
    submit.click(refresh_history, outputs=[stats_html, history_table])
    reset_btn.click(reset_form, inputs=None, outputs=all_inputs + [result_out])

    history_table.select(
        on_history_row_select,
        inputs=[history_table],
        outputs=[selected_id_state, selection_msg],
    )
    refresh_btn.click(refresh_history, outputs=[stats_html, history_table])
    delete_selected_btn.click(
        delete_one,
        inputs=[selected_id_state],
        outputs=[stats_html, history_table, selected_id_state, selection_msg],
    )
    clear_btn.click(
        clear_all,
        outputs=[stats_html, history_table, selected_id_state, selection_msg],
    )
    history_tab.select(refresh_history, outputs=[stats_html, history_table])


# Glue: serve the Gradio UI at "/" but keep all the FastAPI endpoints alive
app = gr.mount_gradio_app(fastapi_app, demo, path="/")


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=7860)
