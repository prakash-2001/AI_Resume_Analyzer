from io import BytesIO
import os

import streamlit as st

from services.huggingface_service import DEFAULT_MODEL, analyze_resume_with_huggingface
from utils.pdf_reader import extract_text_from_pdf


st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon=":page_facing_up:",
    layout="wide",
)


st.markdown(
    """
    <style>
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 1180px;
    }
    div[data-testid="stMetric"] {
        background: #f8fafc;
        border: 1px solid #e5e7eb;
        border-radius: 8px;
        padding: 14px 16px;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


if "analysis" not in st.session_state:
    st.session_state.analysis = ""

if "uploaded_file_id" not in st.session_state:
    st.session_state.uploaded_file_id = ""


@st.cache_data(show_spinner=False)
def extract_text_from_pdf_bytes(file_bytes: bytes) -> str:
    return extract_text_from_pdf(BytesIO(file_bytes))


def get_hf_token() -> str:
    try:
        return st.secrets["HF_TOKEN"]
    except Exception:
        return os.getenv("HF_TOKEN", "")


def get_hf_model() -> str:
    try:
        return st.secrets.get("HF_MODEL", DEFAULT_MODEL)
    except Exception:
        return os.getenv("HF_MODEL", DEFAULT_MODEL)


hf_token = get_hf_token()
hf_model = get_hf_model()


header_left, header_right = st.columns([0.72, 0.28], vertical_alignment="center")

with header_left:
    st.title("AI Resume Analyzer")

with header_right:
    st.caption("PDF upload -> text extraction -> AI analysis")


with st.sidebar:
    st.header("Settings")
    if hf_token:
        st.success("Hugging Face token configured.", icon=":material/check_circle:")
    else:
        st.warning(
            "Add HF_TOKEN in Streamlit secrets before analysis.",
            icon=":material/key:",
        )
    st.caption(f"Model: `{hf_model}`")
    st.divider()
    st.subheader("Workflow")
    st.markdown(
        """
        1. Upload PDF
        2. Review extracted text
        3. Generate analysis
        """
    )


upload_col, stats_col = st.columns([0.62, 0.38], gap="large")

resume_text = ""
uploaded_file = None
uploaded_file_bytes = b""

with upload_col:
    st.subheader("Upload Resume", divider="gray")
    uploaded_file = st.file_uploader(
        "Resume PDF",
        type=["pdf"],
        help="Upload a text-based resume PDF.",
    )

    if uploaded_file is not None:
        uploaded_file_id = f"{uploaded_file.name}:{uploaded_file.size}"
        uploaded_file_bytes = uploaded_file.getvalue()

        if uploaded_file_id != st.session_state.uploaded_file_id:
            st.session_state.uploaded_file_id = uploaded_file_id
            st.session_state.analysis = ""

        with st.status("Reading PDF...", expanded=False) as status:
            progress = st.progress(0, text="Opening uploaded file")
            try:
                progress.progress(45, text="Extracting text")
                resume_text = extract_text_from_pdf_bytes(uploaded_file_bytes)
                progress.progress(100, text="Extraction complete")
                status.update(
                    label="Resume text extracted",
                    state="complete",
                    expanded=False,
                )
            except Exception as error:
                status.update(
                    label="PDF extraction failed",
                    state="error",
                    expanded=True,
                )
                st.error(f"Could not extract text from PDF: {error}")

with stats_col:
    st.subheader("Resume Status", divider="gray")
    if uploaded_file is None:
        st.info("Upload a PDF to begin.", icon=":material/upload_file:")
    elif resume_text:
        word_count = len(resume_text.split())
        char_count = len(resume_text)
        metric_left, metric_right = st.columns(2)
        metric_left.metric("Words", f"{word_count:,}")
        metric_right.metric("Characters", f"{char_count:,}")
        st.success("Ready for analysis.", icon=":material/check_circle:")
    else:
        st.warning(
            "No readable text found. Try a text-based PDF.",
            icon=":material/warning:",
        )


if uploaded_file is not None and resume_text:
    with st.expander("Extracted text preview"):
        st.text_area(
            "Resume text",
            value=resume_text,
            height=260,
        )


st.subheader("Analysis", divider="gray")

if uploaded_file is None:
    st.info("Upload a PDF resume to generate analysis.", icon=":material/analytics:")
elif not resume_text:
    st.warning("No readable text found. Try uploading a text-based PDF.")
else:
    analyze_clicked = st.button(
        "Analyze Resume",
        type="primary",
        icon=":material/auto_awesome:",
        use_container_width=True,
        disabled=not hf_token,
    )

    if not hf_token:
        st.warning(
            "Hugging Face token is not configured. Add it in secrets to enable analysis.",
            icon=":material/key:",
        )

    if analyze_clicked:
        try:
            with st.status("Analyzing resume...", expanded=True) as status:
                progress = st.progress(15, text="Preparing prompt")
                progress.progress(45, text="Sending resume to Hugging Face")
                analysis = analyze_resume_with_huggingface(
                    resume_text,
                    hf_token,
                    hf_model,
                )
                progress.progress(100, text="Analysis complete")
                status.update(
                    label="Analysis complete",
                    state="complete",
                    expanded=False,
                )
            st.session_state.analysis = analysis
        except Exception as error:
            st.error(f"Could not analyze resume: {error}")

    if st.session_state.analysis:
        st.markdown(st.session_state.analysis)
    else:
        st.info(
            "Run analysis to see suggestions here.",
            icon=":material/psychology:",
        )
