import streamlit as st
import pandas as pd
import anthropic
import os
from pathlib import Path

# ─── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Student Profile Analyzer",
    page_icon="🎓",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Syne:wght@400;600;700;800&family=Inter:wght@300;400;500&display=swap');

    html, body, [class*="css"] {
        font-family: 'Inter', sans-serif;
    }
    .main { background-color: #0d0d0d; }
    .block-container { padding: 2rem 3rem; }

    h1, h2, h3 { font-family: 'Syne', sans-serif !important; }

    .hero-title {
        font-family: 'Syne', sans-serif;
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(135deg, #00f5a0, #00d9f5);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0.2rem;
    }
    .hero-sub {
        color: #888;
        font-size: 1rem;
        margin-bottom: 2rem;
    }

    /* Metric cards */
    .metric-grid {
        display: grid;
        grid-template-columns: repeat(auto-fill, minmax(160px, 1fr));
        gap: 1rem;
        margin: 1.5rem 0;
    }
    .metric-card {
        background: #1a1a1a;
        border: 1px solid #2a2a2a;
        border-radius: 12px;
        padding: 1rem 1.2rem;
        text-align: center;
    }
    .metric-label {
        font-size: 0.7rem;
        color: #666;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        margin-bottom: 0.4rem;
    }
    .metric-value {
        font-family: 'Syne', sans-serif;
        font-size: 1.5rem;
        font-weight: 700;
        color: #00f5a0;
    }

    /* Profile section */
    .profile-block {
        background: #141414;
        border: 1px solid #222;
        border-radius: 16px;
        padding: 1.5rem 2rem;
        margin: 1rem 0;
    }
    .section-heading {
        font-family: 'Syne', sans-serif;
        font-size: 0.75rem;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 0.12em;
        color: #00d9f5;
        margin-bottom: 0.8rem;
        border-bottom: 1px solid #1e1e1e;
        padding-bottom: 0.5rem;
    }
    .info-row {
        display: flex;
        justify-content: space-between;
        padding: 0.4rem 0;
        border-bottom: 1px solid #1a1a1a;
        font-size: 0.9rem;
    }
    .info-key { color: #777; }
    .info-val { color: #e0e0e0; font-weight: 500; }

    /* AI analysis box */
    .ai-box {
        background: linear-gradient(135deg, #0f1f1a, #0f1a20);
        border: 1px solid #1e3a2a;
        border-radius: 16px;
        padding: 1.8rem 2rem;
        margin-top: 1.5rem;
        position: relative;
    }
    .ai-badge {
        position: absolute;
        top: -12px;
        left: 20px;
        background: linear-gradient(135deg, #00f5a0, #00d9f5);
        color: #0d0d0d;
        font-family: 'Syne', sans-serif;
        font-size: 0.7rem;
        font-weight: 700;
        letter-spacing: 0.1em;
        padding: 3px 12px;
        border-radius: 20px;
    }
    .ai-content { color: #ccc; font-size: 0.95rem; line-height: 1.75; }

    /* Search bar styling */
    .stTextInput > div > div > input {
        background: #1a1a1a !important;
        border: 1px solid #333 !important;
        border-radius: 10px !important;
        color: #fff !important;
        font-size: 1rem !important;
        padding: 0.8rem 1rem !important;
    }
    .stTextInput > div > div > input:focus {
        border-color: #00f5a0 !important;
        box-shadow: 0 0 0 1px #00f5a0 !important;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #00f5a0, #00d9f5) !important;
        color: #0d0d0d !important;
        font-family: 'Syne', sans-serif !important;
        font-weight: 700 !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.6rem 2rem !important;
        font-size: 0.9rem !important;
        transition: opacity 0.2s !important;
    }
    .stButton > button:hover { opacity: 0.85 !important; }

    /* Sidebar */
    .css-1d391kg, [data-testid="stSidebar"] {
        background: #111 !important;
    }

    /* Tag pill */
    .tag-pill {
        display: inline-block;
        background: #1e1e1e;
        border: 1px solid #333;
        color: #00f5a0;
        border-radius: 20px;
        padding: 3px 12px;
        font-size: 0.78rem;
        margin: 3px;
        font-weight: 500;
    }

    /* Not found */
    .not-found {
        background: #1a0f0f;
        border: 1px solid #3a1a1a;
        border-radius: 12px;
        padding: 1.5rem;
        color: #ff6b6b;
        text-align: center;
        font-size: 1rem;
    }

    /* Suggestion list */
    .suggestion-item {
        background: #1a1a1a;
        border: 1px solid #2a2a2a;
        border-radius: 8px;
        padding: 0.5rem 1rem;
        margin: 0.3rem 0;
        color: #ccc;
        cursor: pointer;
        font-size: 0.9rem;
    }
</style>
""", unsafe_allow_html=True)

# ─── Load Data ─────────────────────────────────────────────────────────────────
@st.cache_data
def load_data():
    file_path = Path(__file__).parent / "student_data.xlsx"
    df = pd.read_excel(file_path)
    # Clean column names
    df.columns = df.columns.str.strip()
    return df

df = load_data()

# Friendly column name mapping
COL = {
    "sno": "S.No",
    "reg": "Register No",
    "name": "Student Name",
    "dept": "Dept",
    "category": "Category",
    "residence": "Residence",
    "tenth": "10TH%(Avoid entering % symbol)",
    "twelfth": "12TH%(Avoid entering % symbol)",
    "diploma": "Diploma% (Avoid entering % symbol)",
    "gpa1": "GPA Sem1",
    "gpa2": "GPA Sem2",
    "gpa3": "GPA Sem3",
    "gpa4": "GPA Sem4",
    "cgpa": "CGPA",
    "standing": "Standing Arrear (Count)",
    "history": "History of Arrear (Count)",
    "dob": "Date of Birth (DD-MM-YYYY)",
    "gender": "Gender",
    "official_mail": "Official Mail id(College mail id)",
    "personal_mail": "Personal Mail id",
    "mobile": "Mobile No.",
    "alt_mobile": "Alternate Mobile No.(Should not be same as mobile No.)",
    "cur_addr": "Current Address",
    "cur_city": "Current City",
    "perm_addr": "Permanent Address",
    "hometown": "Hometown",
    "tenth_board": "10th Board(State,CBSE,etc.,)",
    "tenth_year": "10th Year of Passing",
    "twelfth_board": "12th Board (State,CBSE,etc.,)",
    "twelfth_year": "12th Year of Passing",
    "aadhar": "Aadhar No.",
    "pan": "PAN No.",
    "relocate": "Willing to Relocate",
    "father": "Father's Name",
    "mother": "Mother's Name",
    "tech": "Tech Stack known (FSD,SDE,Cloud,GenAI etc)",
    "github": "Github Link",
    "resume": df.columns[-1],  # Resume column (long name)
}

# ─── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Settings")
    api_key = st.text_input("Anthropic API Key", type="password", placeholder="sk-ant-...")
    st.markdown("---")
    st.markdown(f"**Dataset:** `student_data.xlsx`")
    st.markdown(f"**Total Students:** `{len(df)}`")
    st.markdown(f"**Dept:** `{df[COL['dept']].iloc[0] if not df.empty else 'N/A'}`")
    st.markdown("---")
    search_mode = st.radio("Search Mode", ["Exact Match", "Partial / Fuzzy"], index=1)

# ─── Header ────────────────────────────────────────────────────────────────────
st.markdown('<div class="hero-title">🎓 Student Profile Analyzer</div>', unsafe_allow_html=True)
st.markdown('<div class="hero-sub">Search by student name → view full profile + AI-powered analysis</div>', unsafe_allow_html=True)

# ─── Search ────────────────────────────────────────────────────────────────────
col_search, col_btn = st.columns([4, 1])
with col_search:
    name_input = st.text_input("", placeholder="Type a student name e.g. Kavin, Priya, Varshha...", label_visibility="collapsed")
with col_btn:
    search_clicked = st.button("🔍 Search")

# ─── Helper: find student ──────────────────────────────────────────────────────
def find_student(query: str, mode: str) -> pd.DataFrame:
    query = query.strip()
    names = df[COL["name"]].fillna("").astype(str)
    if mode == "Exact Match":
        mask = names.str.lower() == query.lower()
    else:
        mask = names.str.lower().str.contains(query.lower(), na=False)
    return df[mask].reset_index(drop=True)

# ─── Helper: safe get ─────────────────────────────────────────────────────────
def safe(row, key):
    val = row.get(COL.get(key, key), None)
    if pd.isna(val) or val == "" or val is None:
        return "—"
    return str(val)

# ─── Helper: Claude analysis ──────────────────────────────────────────────────
def analyze_with_claude(student: dict, api_key: str) -> str:
    client = anthropic.Anthropic(api_key=api_key)

    prompt = f"""You are an academic advisor analyzing a student profile. Based on the data below, provide:

1. **Academic Snapshot** – Brief summary of academic performance (10th, 12th, CGPA, GPA trend, arrears).
2. **Strengths** – Key positives from the profile (tech skills, performance, etc.)
3. **Areas to Improve** – Honest gaps or concerns.
4. **Career Fit** – Based on tech stack and performance, suggest 2–3 suitable career paths.
5. **Quick Tip** – One personalized, actionable piece of advice.

Be concise, insightful, and constructive. Use bullet points inside sections.

---
Student Profile:
Name: {student.get('name', '—')}
Register No: {student.get('reg', '—')}
Gender: {student.get('gender', '—')}
Dept: {student.get('dept', '—')}
Category: {student.get('category', '—')}
Residence: {student.get('residence', '—')}

10th %: {student.get('tenth', '—')} ({student.get('tenth_board', '—')}, {student.get('tenth_year', '—')})
12th %: {student.get('twelfth', '—')} ({student.get('twelfth_board', '—')}, {student.get('twelfth_year', '—')})
Diploma %: {student.get('diploma', '—')}
GPA Sem1: {student.get('gpa1', '—')}
GPA Sem2: {student.get('gpa2', '—')}
GPA Sem3: {student.get('gpa3', '—')}
GPA Sem4: {student.get('gpa4', '—')}
CGPA: {student.get('cgpa', '—')}
Standing Arrears: {student.get('standing', '—')}
History of Arrears: {student.get('history', '—')}

Tech Stack: {student.get('tech', '—')}
Willing to Relocate: {student.get('relocate', '—')}
Hometown: {student.get('hometown', '—')}
GitHub: {student.get('github', '—')}
---
"""

    message = client.messages.create(
        model="claude-opus-4-5",
        max_tokens=1000,
        messages=[{"role": "user", "content": prompt}]
    )
    return message.content[0].text

# ─── Results ───────────────────────────────────────────────────────────────────
if search_clicked or name_input:
    if not name_input.strip():
        st.warning("Please enter a name to search.")
    else:
        results = find_student(name_input, search_mode)

        if results.empty:
            st.markdown(f'<div class="not-found">❌ No student found matching <strong>"{name_input}"</strong>.<br>Try partial search mode or check spelling.</div>', unsafe_allow_html=True)
        else:
            if len(results) > 1:
                st.info(f"Found **{len(results)} students** matching *{name_input}*. Showing all below.")

            for idx, row in results.iterrows():
                st.markdown("---")
                student = {k: safe(row, k) for k in COL.keys()}

                # ── Name header ──
                st.markdown(f"### 👤 {student['name']}")
                tag_html = ""
                for tag in [student['reg'], student['dept'], student['gender'], student['residence'], student['category']]:
                    if tag != "—":
                        tag_html += f'<span class="tag-pill">{tag}</span>'
                st.markdown(tag_html, unsafe_allow_html=True)

                col1, col2 = st.columns(2)

                # ── Academic Metrics ──
                with col1:
                    st.markdown('<div class="profile-block">', unsafe_allow_html=True)
                    st.markdown('<div class="section-heading">📊 Academic Performance</div>', unsafe_allow_html=True)

                    metrics_html = '<div class="metric-grid">'
                    for label, val in [("10th %", student['tenth']), ("12th %", student['twelfth']),
                                       ("CGPA", student['cgpa']), ("GPA Sem1", student['gpa1']),
                                       ("GPA Sem2", student['gpa2']), ("GPA Sem3", student['gpa3']),
                                       ("Standing Arrears", student['standing']), ("History Arrears", student['history'])]:
                        metrics_html += f'<div class="metric-card"><div class="metric-label">{label}</div><div class="metric-value">{val}</div></div>'
                    metrics_html += '</div>'
                    st.markdown(metrics_html, unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)

                # ── Personal Info ──
                with col2:
                    st.markdown('<div class="profile-block">', unsafe_allow_html=True)
                    st.markdown('<div class="section-heading">🪪 Personal Details</div>', unsafe_allow_html=True)
                    for label, val in [
                        ("Date of Birth", student['dob']),
                        ("Hometown", student['hometown']),
                        ("Current City", student['cur_city']),
                        ("Father's Name", student['father']),
                        ("Mother's Name", student['mother']),
                        ("Willing to Relocate", student['relocate']),
                        ("Mobile", student['mobile']),
                        ("Official Email", student['official_mail']),
                    ]:
                        st.markdown(f'<div class="info-row"><span class="info-key">{label}</span><span class="info-val">{val}</span></div>', unsafe_allow_html=True)
                    st.markdown('</div>', unsafe_allow_html=True)

                # ── Tech Stack ──
                st.markdown('<div class="profile-block">', unsafe_allow_html=True)
                st.markdown('<div class="section-heading">💻 Tech Stack & Links</div>', unsafe_allow_html=True)
                tech_tags = ""
                if student['tech'] != "—":
                    for t in student['tech'].split(","):
                        tech_tags += f'<span class="tag-pill">⚡ {t.strip()}</span>'
                st.markdown(tech_tags if tech_tags else "No tech stack listed", unsafe_allow_html=True)

                link_col1, link_col2 = st.columns(2)
                with link_col1:
                    if student['github'] != "—":
                        st.markdown(f"🔗 **GitHub:** [{student['github']}]({student['github']})")
                with link_col2:
                    resume_val = safe(row, "resume")
                    if resume_val != "—":
                        st.markdown(f"📄 **Resume:** [Open Link]({resume_val})")
                st.markdown('</div>', unsafe_allow_html=True)

                # ── AI Analysis ──
                st.markdown('<div class="ai-box"><div class="ai-badge">✨ AI ANALYSIS</div>', unsafe_allow_html=True)
                if not api_key:
                    st.markdown('<div class="ai-content">⚠️ Enter your <strong>Anthropic API Key</strong> in the sidebar to enable AI-powered profile analysis.</div>', unsafe_allow_html=True)
                else:
                    with st.spinner("Analyzing profile with Claude..."):
                        try:
                            analysis = analyze_with_claude(student, api_key)
                            st.markdown(f'<div class="ai-content">{analysis}</div>', unsafe_allow_html=True)
                        except Exception as e:
                            st.error(f"Claude API error: {e}")
                st.markdown('</div>', unsafe_allow_html=True)

# ─── Footer ────────────────────────────────────────────────────────────────────
st.markdown("---")
st.markdown('<center style="color:#444; font-size:0.8rem;">Built with Streamlit · Powered by Claude API · AIML 2027 Batch</center>', unsafe_allow_html=True)
