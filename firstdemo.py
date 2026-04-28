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
    "tech_toggle": "显示接口预留",
        "guide_title": "使用引导",
        "guide_1": "先上传 DICOM 影像文件，再上传临床报告 .txt 文件。",
        "guide_2": "点击开始评估后，页面会依次显示影像处理中、文本解析中、风险评估中。",
        "guide_3": "如需补充信息，可展开高级选项，但默认不会打扰患者操作。",
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
        "tech_title": "统一 Agent 接口预留",
        "tech_subtitle": "患者端默认隐藏，后续可直接接入组员整合后的单一 Agent。",
        "tech_api_title": "接口映射",
        "tech_api_input": "统一输入",
        "tech_api_output": "统一输出",
        "advanced_title": "更多信息（默认隐藏）",
        "advanced_note": "这里保留原始功能所需的补充录入，患者端默认折叠。",
        "patient_name": "姓名或编号（可选）",
        "age": "年龄",
        "sex": "性别",
        "sex_options": ["女", "男", "其他"],
        "note": "近期症状描述（可选）",
        "troponin": "肌钙蛋白 cTnI/T（ng/mL）",
        "bnp": "BNP / NT-proBNP（pg/mL）",
        "qtc": "QTc 间期（ms）",
        "lvef": "LVEF（%）",
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
        "advanced_values": "补充指标录入",
        "basic_assist": "如果报告里有明确数值，也可以在这里补充，方便更准确地演示。",
    }
}


def tr(lang: str, key: str):
    return I18N[lang][key]


def build_style(senior_mode: bool, lang: str) -> str:
    base = 1.16 if senior_mode else 1.0
    title = 1.12 if senior_mode else 1.0
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
        padding-top: 1.0rem;
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

      .tech-panel {{
        border: 1px solid #d2dee7;
        background: linear-gradient(135deg, #ffffff, #f9fcfe);
        border-radius: 18px;
        padding: 0.9rem 1rem;
        margin-bottom: 0.9rem;
      }}

      .tech-grid {{
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 0.6rem;
        margin-top: 0.65rem;
      }}

      .tech-item {{
        border-radius: 14px;
        background: #f6fbff;
        border: 1px solid #d7e5ee;
        padding: 0.8rem 0.9rem;
      }}

      .tech-item strong {{
        display: block;
        margin-bottom: 0.2rem;
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
        content: "将文件拖放到这里";
        visibility: visible;
        display: block;
        color: #35576b;
        font-weight: 700;
      }}

      .stFileUploader [data-testid="stFileUploaderDropzoneInstructions"] > div::after {{
        content: "支持拖拽上传，适合患者直接操作";
        visibility: visible;
        display: block;
        margin-top: 0.2rem;
        color: #6b8796;
        font-size: calc(0.92rem * {base});
      }}

      .stFileUploader button {{
        background: linear-gradient(135deg, #dceff9, #fff0e4) !important;
        border: 1px solid #d4e1ea !important;
        color: #35576b !important;
        border-radius: 12px !important;
        font-weight: 700 !important;
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
if "show_tech" not in st.session_state:
  st.session_state["show_tech"] = False

lang = st.session_state["lang"]
mode = st.session_state["mode"]
senior_mode = mode == "senior"

top_left, top_right = st.columns([1.2, 1.0], gap="small")
with top_right:
  control_left, control_mid, control_right = st.columns([1.1, 1.1, 1.1])
  with control_left:
    lang = st.selectbox(
      tr(st.session_state["lang"], "mode_label"),
      options=["zh", "en"],
      index=0 if st.session_state["lang"] == "zh" else 1,
      format_func=lambda key: tr(key, "lang_name") if key == "zh" else "English",
      label_visibility="collapsed",
    )
  with control_mid:
    mode = st.selectbox(
      tr(lang, "mode_label"),
      options=["normal", "senior"],
      index=0 if st.session_state["mode"] == "normal" else 1,
      format_func=lambda key: tr(lang, "mode_normal") if key == "normal" else tr(lang, "mode_senior"),
      label_visibility="collapsed",
    )
  with control_right:
    st.session_state["show_tech"] = st.checkbox(tr(lang, "tech_toggle"), value=st.session_state["show_tech"])

st.session_state["lang"] = lang
st.session_state["mode"] = mode
senior_mode = mode == "senior"

st.markdown(build_style(senior_mode, lang), unsafe_allow_html=True)

st.markdown(
  f"""
  <div class="top-controls">
    <span class="top-pill">{tr(lang, 'mode_label')}：{tr(lang, 'mode_senior') if senior_mode else tr(lang, 'mode_normal')}</span>
    <span class="top-pill">{tr(lang, 'lang_name') if lang == 'zh' else 'English'}</span>
  </div>
  """,
  unsafe_allow_html=True,
)

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
        <li>{tr(lang, 'guide_3')}</li>
      </ul>
    </div>
    """,
    unsafe_allow_html=True,
)

with st.expander(tr(lang, "advanced_title"), expanded=False):
    st.caption(tr(lang, "advanced_note"))
    st.markdown(f"#### {tr(lang, 'advanced_values')}")
    st.caption(tr(lang, "basic_assist"))
    adv_col1, adv_col2 = st.columns(2)
    with adv_col1:
        patient_name = st.text_input(tr(lang, "patient_name"))
        age = st.number_input(tr(lang, "age"), min_value=0, max_value=120, value=60)
        sex = st.selectbox(tr(lang, "sex"), options=tr(lang, "sex_options"))
    with adv_col2:
        troponin = st.number_input(tr(lang, "troponin"), min_value=0.0, max_value=30.0, value=0.05, step=0.01)
        bnp = st.number_input(tr(lang, "bnp"), min_value=0.0, max_value=20000.0, value=80.0, step=1.0)
        qtc = st.number_input(tr(lang, "qtc"), min_value=300, max_value=650, value=440, step=1)
        lvef = st.number_input(tr(lang, "lvef"), min_value=10, max_value=90, value=58, step=1)
    note = st.text_area(tr(lang, "note"), height=90)

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
    values.update(
        {
            "age": float(age),
            "troponin": float(troponin),
            "bnp": float(bnp),
            "qtc": float(qtc),
            "lvef": float(lvef),
        }
    )
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
                报告文件：{report_name}<br>
                姓名/编号：{patient_name if patient_name else '未填写'}
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

if st.session_state["show_tech"]:
    st.markdown(
        f"""
        <div class="tech-panel">
          <div class="step-head"><span class="step-num">7</span><span class="step-title">{tr(lang, 'tech_title')}</span></div>
          <div style="color:#4b6675;">{tr(lang, 'tech_subtitle')}</div>
          <div class="tech-grid">
            <div class="tech-item">
              <strong>{tr(lang, 'tech_api_input')}</strong>
              /api/patient/submit
            </div>
            <div class="tech-item">
              <strong>{tr(lang, 'tech_api_output')}</strong>
              /api/patient/heart-status-result
            </div>
            <div class="tech-item">
              <strong>agent_1</strong>
              /api/module1/ingest-and-clean
            </div>
            <div class="tech-item">
              <strong>agent_2 ~ agent_4</strong>
              /api/module2/feature-extract · /api/module3/fuse-and-explain · /api/module4/generate-care
            </div>
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )
