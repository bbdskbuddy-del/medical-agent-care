import re
from typing import Dict, List, Tuple

import streamlit as st


st.set_page_config(
    page_title="MACE 风险评估",
    page_icon="🫀",
    layout="wide",
    initial_sidebar_state="collapsed",
)


I18N = {
    "zh": {
        "lang_name": "简体中文",
        "title": "MACE 风险评估",
        "subtitle": "按步骤上传影像和临床报告，系统会自动给出风险等级和标准化建议。",
        "mode_label": "显示模式",
        "mode_normal": "普通模式",
        "mode_senior": "老人模式",
        "guide_title": "就诊前说明",
        "guide_1": "先准备好影像文件和临床报告，再开始评估。",
        "guide_2": "上传后点击开始评估，页面会显示处理进度、风险等级和建议。",
        "image_title": "1. 影像上传框",
        "image_help": "上传：DICOM 影像文件",
        "text_title": "2. 文本上传框",
        "text_help": "上传：临床报告 .txt 文件",
        "button_title": "3. 执行按钮",
        "button_text": "开始 MACE 风险评估",
        "status_title": "4. 运行状态提示区",
        "status_wait": "等待提交",
        "status_image": "影像处理中",
        "status_text": "文本解析中",
        "status_risk": "风险评估中",
        "risk_title": "5. 核心输出 1",
        "risk_wait": "请先上传影像和报告，再开始评估。",
        "risk_level_label": "MACE 风险等级",
        "risk_low": "低",
        "risk_mid": "中",
        "risk_high": "高",
        "risk_scale": "风险分值",
        "suggest_title": "6. 核心输出 2",
        "suggest_wait": "标准化诊疗建议会在这里展示。",
        "suggest_header": "标准化诊疗建议",
        "submit_help": "评估后会自动更新风险等级与建议。",
        "disclaimer": "本页面用于风险参考，不替代医生面诊。如持续不适，请及时就医。",
        "fallback_img": "尚未上传影像文件",
        "fallback_txt": "尚未上传临床报告",
        "tips_low": [
            "继续按计划复查，保持规律作息。",
            "记录症状变化，便于后续比较。",
            "维持适度活动和稳定饮食。",
        ],
        "tips_mid": [
            "建议近期复查，并和医生确认报告变化。",
            "如果症状波动明显，可提前咨询。",
            "尽量减少劳累，优先休息。",
        ],
        "tips_high": [
            "建议尽快联系医生进行面对面评估。",
            "复查时请携带影像和报告原件。",
            "如不适持续或加重，请尽早就医。",
        ],
    },
    "en": {
        "lang_name": "English",
        "title": "MACE Risk Assessment",
        "subtitle": "Upload imaging and clinical reports step by step. The system will show a risk level and standardized suggestions automatically.",
        "mode_label": "Display Mode",
        "mode_normal": "Normal Mode",
        "mode_senior": "Senior Mode",
        "guide_title": "Quick Guide",
        "guide_1": "Upload the DICOM imaging file first, then the clinical report in .txt format.",
        "guide_2": "After starting the assessment, the page will show imaging processing, text parsing, and risk evaluation in order.",
        "image_title": "1. Imaging Upload",
        "image_help": "Upload: DICOM imaging file",
        "text_title": "2. Text Upload",
        "text_help": "Upload: clinical report .txt file",
        "button_title": "3. Run Assessment",
        "button_text": "Start MACE Risk Assessment",
        "status_title": "4. Status Area",
        "status_wait": "Waiting for submission",
        "status_image": "Processing imaging",
        "status_text": "Parsing text",
        "status_risk": "Evaluating risk",
        "risk_title": "5. Core Output 1",
        "risk_wait": "Please upload imaging and report before starting the assessment.",
        "risk_level_label": "MACE risk level",
        "risk_low": "Low",
        "risk_mid": "Medium",
        "risk_high": "High",
        "risk_scale": "Risk score",
        "suggest_title": "6. Core Output 2",
        "suggest_wait": "Standardized clinical suggestions will appear here.",
        "suggest_header": "Standardized recommendations",
        "submit_help": "The risk level and suggestions will update after assessment.",
        "disclaimer": "This page is for risk reference only and does not replace a physician visit. Seek care if symptoms persist.",
        "fallback_img": "No imaging file uploaded",
        "fallback_txt": "No clinical report uploaded",
        "tips_low": [
            "Continue routine follow-up and keep a stable daily routine.",
            "Record symptom changes for later comparison.",
            "Maintain moderate activity and a steady diet.",
        ],
        "tips_mid": [
            "A recent follow-up is recommended. Confirm the report changes with a clinician.",
            "If symptoms fluctuate noticeably, consider contacting a doctor earlier.",
            "Reduce fatigue and prioritize rest.",
        ],
        "tips_high": [
            "Please contact a doctor promptly for an in-person evaluation.",
            "Bring the original imaging and report to the next visit.",
            "If symptoms continue or worsen, seek care as soon as possible.",
        ],
    },
}



def tr(lang: str, key: str):
    return I18N.get(lang, I18N["zh"]).get(key, key)

def build_style(senior_mode: bool, lang: str) -> str:
    base = 1.16 if senior_mode else 1.0
    title = 1.12 if senior_mode else 1.0
    drop_title = "将文件拖放到这里" if lang == "zh" else "Drop files here"
    drop_help = "支持拖拽上传，适合患者直接操作" if lang == "zh" else "Drag and drop upload, suitable for patients"
    browse_text = "浏览文件" if lang == "zh" else "Browse files"
    return f"""
    <style>
      :root {{
      --bg: #eef4f8;
        --panel: #ffffff;
      --line: #cfdde7;
      --text: #223744;
      --muted: #587285;
      --title: #102330;
        --accent: #245f7d;
        --accent-2: #d97e45;
        --soft: #eef6fb;
      --shadow: 0 14px 30px rgba(33, 63, 84, 0.12);
      }}

      .stApp {{
        background:
          radial-gradient(circle at 10% 12%, rgba(233, 245, 252, 0.95), transparent 26%),
          radial-gradient(circle at 90% 5%, rgba(255, 242, 231, 0.80), transparent 28%),
          linear-gradient(180deg, #f8fbfd 0%, #f3f8fb 100%);
      }}

      .block-container {{
        max-width: 980px;
        padding-top: 4.5rem;
        padding-bottom: 2.2rem;
      }}

      .stMarkdown p, .stMarkdown li, .stCaption, .stText, .stApp label {{
        color: var(--text) !important;
        font-size: calc(1rem * {base});
        line-height: 1.75;
      }}

      .stMarkdown strong,
      .stMarkdown b,
      .step-title,
      .hero .title,
      h1, h2, h3, h4 {{
        color: var(--title) !important;
      }}

      .stMarkdown a {{
        color: #1f5d84 !important;
      }}

      .stMarkdown hr {{
        border-color: #d5e0e8 !important;
      }}

      .hero {{
        background: linear-gradient(135deg, #ffffff, #f6fbff 56%, #fff8f1 100%);
        border: 1px solid #cfdde7;
        border-radius: 24px;
        box-shadow: 0 16px 34px rgba(33, 63, 84, 0.10);
        padding: 1.2rem 1.35rem;
        margin-bottom: 1rem;
      }}

      .hero .title {{
        font-size: calc(2rem * {title});
        line-height: 1.15;
        font-weight: 800;
        margin: 0.15rem 0 0.35rem 0;
      }}

      .hero .subtitle {{
        color: #4e6878;
        margin: 0;
      }}

      .guide {{
        border: 1px solid #cfdde7;
        background: linear-gradient(135deg, #f9fdff, #ffffff);
        border-radius: 18px;
        padding: 0.95rem 1rem;
        margin-bottom: 1rem;
      }}

      .guide ul {{
        margin: 0.4rem 0 0 1.1rem;
      }}

      .guide li {{
        margin-bottom: 0.28rem;
      }}

      .step-card {{
        border: 1px solid #cedce6;
        border-radius: 18px;
        background: var(--panel);
        box-shadow: 0 12px 26px rgba(33, 63, 84, 0.10);
        padding: 1rem 1rem 0.9rem 1rem;
        margin-bottom: 0.85rem;
      }}

      .step-head {{
        display: flex;
        align-items: center;
        gap: 0.55rem;
        margin-bottom: 0.35rem;
      }}

      .step-num {{
        width: 2rem;
        height: 2rem;
        border-radius: 999px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        background: linear-gradient(135deg, #e3f1fa, #fff0df);
        color: #264b61;
        font-weight: 800;
      }}

      .step-title {{
        font-size: calc(1.1rem * {base});
        color: var(--title) !important;
        font-weight: 700;
      }}

      .status-box, .result-box, .suggest-box {{
        border-radius: 18px;
        border: 1px solid #cedce6;
        background: linear-gradient(135deg, #ffffff, #fbfdff);
        box-shadow: 0 12px 26px rgba(33, 63, 84, 0.10);
        padding: 1rem;
      }}

      .status-pill {{
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.32rem 0.7rem;
        border-radius: 999px;
        font-weight: 700;
        background: #edf6fc;
        color: #244459;
      }}

      .status-running {{
        background: linear-gradient(135deg, #eef7fb, #fff3ea);
        color: #69513d;
      }}

      .status-low {{ border-left: 7px solid #74b59c; }}
      .status-mid {{ border-left: 7px solid #d1a35d; }}
      .status-high {{ border-left: 7px solid #d96d62; }}

      .feature-row {{
        display: flex;
        gap: 0.6rem;
        flex-wrap: wrap;
        margin-top: 0.65rem;
      }}

      .feature-pill {{
        padding: 0.3rem 0.7rem;
        border-radius: 999px;
        background: #f2f7fb;
        border: 1px solid #d6e4ee;
        color: #355364;
        font-size: calc(0.94rem * {base});
      }}

      .advice-list {{
        margin-top: 0.55rem;
      }}

      .advice-list li {{
        margin-bottom: 0.35rem;
      }}

      .quote {{
        margin-top: 0.75rem;
        border-radius: 14px;
        border: 1px dashed #bfd2df;
        background: #fcfeff;
        padding: 0.85rem 0.95rem;
        color: #304d5d !important;
      }}

      .top-controls {{
        display: flex;
        align-items: center;
        gap: 0.8rem;
        justify-content: flex-end;
        margin-bottom: 0.4rem;
        flex-wrap: wrap;
      }}

      .top-pill {{
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        padding: 0.34rem 0.72rem;
        border-radius: 999px;
        background: rgba(255,255,255,0.72);
        border: 1px solid #d2dee7;
        color: #234154;
      }}

      .stFileUploader [data-testid="stFileUploaderDropzone"] {{
        border: 1px dashed #bcd6e6 !important;
        background: linear-gradient(135deg, #f9fdff, #fffaf5) !important;
      }}

      .stFileUploader [data-testid="stFileUploaderDropzone"] * {{
        color: #4a6a7c !important;
      }}

      .stFileUploader [data-testid="stFileUploaderDropzoneInstructions"] > div {{
        visibility: hidden;
      }}

      .stFileUploader [data-testid="stFileUploaderDropzoneInstructions"] > div::before {{
        content: "{drop_title}";
        visibility: visible;
        display: block;
        color: #35576b;
        font-weight: 700;
      }}

      .stFileUploader [data-testid="stFileUploaderDropzoneInstructions"] > div::after {{
        content: "{drop_help}";
        visibility: visible;
        display: block;
        margin-top: 0.2rem;
        color: #6b8796;
        font-size: calc(0.92rem * {base});
      }}

              .stFileUploader button {{
        background: linear-gradient(135deg, #dceff9, #fff0e4) !important;
        border: 1px solid #d4e1ea !important;
        border-radius: 12px !important;
        min-width: 8.8rem !important;
        height: 3rem !important;
        padding: 0 1rem !important;
        position: relative !important;
        overflow: hidden !important;
        color: #35576b !important;
        font-weight: 700 !important;
      }}

      /* 先盖掉原生文字层，彻底消除重影 */
      .stFileUploader button::before {{
        content: "";
        position: absolute;
        inset: 1px;
        border-radius: 10px;
        background: linear-gradient(135deg, #dceff9, #fff0e4);
        z-index: 2;
        pointer-events: none;
      }}

      /* 再画自定义文案 */
      .stFileUploader button::after {{
        content: "{browse_text}";
        position: absolute;
        inset: 0;
        display: flex;
        align-items: center;
        justify-content: center;
        color: #35576b;
        font-size: calc(0.95rem * {base});
        font-weight: 700;
        white-space: nowrap;
        z-index: 3;
        pointer-events: none;
      }}

      .stButton > button, .stFormSubmitButton > button {{
        min-height: calc(2.8rem * {base});
        border-radius: 14px;
        border: 1px solid #d6a679;
        background: linear-gradient(135deg, #ffb86c, #ff9f57);
        color: #ffffff;
        font-size: calc(1rem * {base});
        font-weight: 800;
        box-shadow: 0 10px 18px rgba(217, 124, 63, 0.18);
      }}

      .stButton > button:hover, .stFormSubmitButton > button:hover {{
        border-color: #c97f3f;
        background: linear-gradient(135deg, #ffad5d, #ff9441);
      }}

      .stTextInput input, .stTextArea textarea, .stNumberInput input, div[data-baseweb="select"] > div {{
        border-color: #cfdde7 !important;
        background: #fcfeff !important;
        color: #173242 !important;
      }}

      .stTextInput label,
      .stTextArea label,
      .stNumberInput label,
      .stSelectbox label,
      .stFileUploader label {{
        color: #173242 !important;
        font-weight: 700 !important;
      }}

      .stExpander {{
        border-color: #cfdde7 !important;
        border-radius: 16px !important;
      }}
    </style>
    """


def parse_report_text(text: str) -> Dict[str, float]:
    values = {
        "age": 60.0,
        "troponin": 0.05,
        "bnp": 80.0,
        "qtc": 440.0,
        "lvef": 58.0,
    }

    patterns = {
        "age": r"(?:年龄|age)\s*[:：]?\s*(\d{1,3})",
        "troponin": r"(?:肌钙蛋白|troponin|cTnI|cTnT)\s*[:：]?\s*([0-9]+(?:\.[0-9]+)?)",
        "bnp": r"(?:BNP|NT-proBNP)\s*[:：]?\s*([0-9]+(?:\.[0-9]+)?)",
        "qtc": r"(?:QTc)\s*[:：]?\s*(\d{2,4})",
        "lvef": r"(?:LVEF|EF)\s*[:：]?\s*(\d{1,3})",
    }

    for key, pattern in patterns.items():
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            try:
                values[key] = float(match.group(1))
            except ValueError:
                pass

    return values


def evaluate_heart_status(values: Dict[str, float], file_count: int, report_text: str) -> Tuple[int, str, List[str], List[int]]:
    score = 88

    if file_count == 0:
        score -= 16
    elif file_count == 1:
        score -= 6
    else:
        score += 2

    if values["age"] >= 75:
        score -= 8
    elif values["age"] >= 65:
        score -= 5

    if values["troponin"] >= 1.0:
        score -= 22
    elif values["troponin"] >= 0.4:
        score -= 15
    elif values["troponin"] >= 0.1:
        score -= 8

    if values["bnp"] >= 1000:
        score -= 14
    elif values["bnp"] >= 500:
        score -= 9
    elif values["bnp"] >= 100:
        score -= 4

    if values["qtc"] >= 500:
        score -= 12
    elif values["qtc"] >= 470:
        score -= 7
    elif values["qtc"] >= 450:
        score -= 4

    if values["lvef"] < 40:
        score -= 15
    elif values["lvef"] < 50:
        score -= 8

    report_lower = report_text.lower()
    if any(keyword in report_lower for keyword in ["重症", "显著异常", "急性", "升高", "危险"]):
        score -= 8
    if any(keyword in report_lower for keyword in ["正常", "未见异常", "稳定", "无明显异常"]):
        score += 4

    score = max(30, min(96, score))

    if score >= 76:
        level = "low"
        tips = tr(lang, "tips_low")
    elif score >= 56:
        level = "mid"
        tips = tr(lang, "tips_mid")
    else:
        level = "high"
        tips = tr(lang, "tips_high")

    trend = [max(30, score - 8), max(32, score - 4), score, min(98, score + 2), min(98, score + 4)]
    return score, level, tips, trend


if "trend_data" not in st.session_state:
    st.session_state["trend_data"] = [78, 80, 82, 84, 85]

if "lang" not in st.session_state:
    st.session_state["lang"] = "zh"
if "mode" not in st.session_state:
    st.session_state["mode"] = "normal"

lang = st.session_state["lang"]
mode = st.session_state["mode"]
senior_mode = mode == "senior"

control_col1, control_col2, control_col3 = st.columns([1.5, 1.8, 1.8], gap="small")

with control_col1:
    lang = st.selectbox(
        "🌐",
        options=["zh", "en"],
        index=0 if st.session_state["lang"] == "zh" else 1,
        format_func=lambda key: tr(key, "lang_name") if key == "zh" else "English",
        label_visibility="collapsed",
        key="lang_select"
    )

with control_col2:
    mode = st.selectbox(
        "👓",
        options=["normal", "senior"],
        index=0 if st.session_state["mode"] == "normal" else 1,
        format_func=lambda key: tr(lang, "mode_normal") if key == "normal" else tr(lang, "mode_senior"),
        label_visibility="collapsed",
        key="mode_select"
    )

with control_col3:
  st.caption(" ")

st.session_state["lang"] = lang
st.session_state["mode"] = mode
senior_mode = mode == "senior"

st.markdown(build_style(senior_mode, lang), unsafe_allow_html=True)

st.markdown(
    """
    <div class="hero">
    <div class="title">{title}</div>
    <p class="subtitle">{subtitle}</p>
    </div>
  """.format(title=tr(lang, "title"), subtitle=tr(lang, "subtitle")),
    unsafe_allow_html=True,
)

st.markdown(
    f"""
    <div class="guide">
      <strong>{tr(lang, 'guide_title')}</strong>
      <ul>
        <li>{tr(lang, 'guide_1')}</li>
        <li>{tr(lang, 'guide_2')}</li>
      </ul>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.form("mace_form", clear_on_submit=False):
    st.markdown(
        f"""
        <div class="step-card">
          <div class="step-head"><span class="step-num">1</span><span class="step-title">{tr(lang, 'image_title')}</span></div>
          <div style="color:#4a6474; margin-bottom:0.5rem;">{tr(lang, 'image_help')}</div>
        """,
        unsafe_allow_html=True,
    )
    image_file = st.file_uploader(
        "",
        type=["dcm", "dicom", "png", "jpg", "jpeg"],
        accept_multiple_files=False,
        label_visibility="collapsed",
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="step-card">
          <div class="step-head"><span class="step-num">2</span><span class="step-title">{tr(lang, 'text_title')}</span></div>
          <div style="color:#4a6474; margin-bottom:0.5rem;">{tr(lang, 'text_help')}</div>
        """,
        unsafe_allow_html=True,
    )
    report_file = st.file_uploader(
        "",
        type=["txt"],
        accept_multiple_files=False,
        label_visibility="collapsed",
    )
    st.markdown("</div>", unsafe_allow_html=True)

    st.markdown(
        f"""
        <div class="step-card">
              <div class="step-head"><span class="step-num">3</span><span class="step-title">{tr(lang, 'button_title')}</span></div>
              <div style="color:#4a6474; margin-bottom:0.5rem;">{tr(lang, 'submit_help')}</div>
        """,
        unsafe_allow_html=True,
    )
    submitted = st.form_submit_button(tr(lang, "button_text"))
    st.markdown("</div>", unsafe_allow_html=True)

status_placeholder = st.empty()
result_placeholder = st.empty()
suggest_placeholder = st.empty()

image_name = image_file.name if image_file else tr(lang, "fallback_img")
report_text = ""
if report_file is not None:
    report_text = report_file.read().decode("utf-8", errors="ignore")
report_name = report_file.name if report_file else tr(lang, "fallback_txt")

with status_placeholder.container():
    st.markdown(
        f"""
        <div class="step-card">
          <div class="step-head"><span class="step-num">4</span><span class="step-title">{tr(lang, 'status_title')}</span></div>
          <div class="status-pill status-running">{tr(lang, 'status_wait')}</div>
          <div class="feature-row">
            <span class="feature-pill">{image_name}</span>
            <span class="feature-pill">{report_name}</span>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

if submitted:
    values = parse_report_text(report_text)
    file_count = int(bool(image_file)) + int(bool(report_file))

    with status_placeholder.container():
        st.markdown(
            f"""
            <div class="step-card">
              <div class="step-head"><span class="step-num">4</span><span class="step-title">{tr(lang, 'status_title')}</span></div>
              <div class="status-pill status-running">{tr(lang, 'status_risk')}</div>
              <div class="feature-row">
                <span class="feature-pill">{tr(lang, 'status_image')}</span>
                <span class="feature-pill">{tr(lang, 'status_text')}</span>
                <span class="feature-pill">{tr(lang, 'status_risk')}</span>
              </div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    score, level, tips, trend = evaluate_heart_status(values, file_count, report_text)
    st.session_state["trend_data"] = trend

    if level == "low":
        level_text = tr(lang, "risk_low")
        cls = "status-low"
    elif level == "mid":
        level_text = tr(lang, "risk_mid")
        cls = "status-mid"
    else:
        level_text = tr(lang, "risk_high")
        cls = "status-high"

    with result_placeholder.container():
        st.markdown(
            f"""
            <div class="step-card result-box {cls}">
              <div class="step-head"><span class="step-num">5</span><span class="step-title">{tr(lang, 'risk_title')}</span></div>
              <div class="status-pill">{tr(lang, 'risk_level_label')}：{level_text}</div>
              <div style="margin-top:0.65rem; color:#244253; font-weight:700;">{tr(lang, 'risk_scale')}：{score}/100</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

    with suggest_placeholder.container():
        st.markdown(
            f"""
            <div class="step-card suggest-box">
              <div class="step-head"><span class="step-num">6</span><span class="step-title">{tr(lang, 'suggest_title')}</span></div>
              <div style="font-weight:700; color:#18323f; margin-bottom:0.45rem;">{tr(lang, 'suggest_header')}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        st.markdown("<div class='advice-list'>", unsafe_allow_html=True)
        for idx, tip in enumerate(tips, start=1):
            st.write(f"{idx}. {tip}")
        st.markdown("</div>", unsafe_allow_html=True)

        st.markdown(
            f"""
            <div class="quote">
                影像文件：{image_name}<br>
            报告文件：{report_name}
            </div>
            """,
            unsafe_allow_html=True,
        )

    st.caption(tr(lang, "disclaimer"))
else:
    with result_placeholder.container():
        st.markdown(
            f"""
            <div class="step-card result-box">
              <div class="step-head"><span class="step-num">5</span><span class="step-title">{tr(lang, 'risk_title')}</span></div>
              <div style="color:#385362;">{tr(lang, 'risk_wait')}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
    with suggest_placeholder.container():
        st.markdown(
            f"""
            <div class="step-card suggest-box">
              <div class="step-head"><span class="step-num">6</span><span class="step-title">{tr(lang, 'suggest_title')}</span></div>
              <div style="color:#385362;">{tr(lang, 'suggest_wait')}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )

