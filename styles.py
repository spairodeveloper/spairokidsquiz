"""
styles.py  —  Spairo Academy Knowledge Evaluator
Jazzy glassmorphism design: aurora bg, neon glows, animated elements.
"""


def get_css() -> str:
    return """
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');

    /* ── Global — force dark everywhere ─────────────────────── */
    *, html, body, [class*="css"] {
        font-family: 'Inter', sans-serif !important;
        box-sizing: border-box;
    }
    html, body {
        background: #08001F !important;
        background-color: #08001F !important;
    }
    .stApp {
        background: #08001F !important;
        background-color: #08001F !important;
    }

    /* Nuke ALL white container backgrounds */
    [data-testid="stAppViewContainer"],
    [data-testid="stAppViewBlockContainer"],
    [data-testid="stMainBlockContainer"],
    [data-testid="stVerticalBlock"],
    [data-testid="stBottom"],
    [data-testid="stBottom"] > div,
    [data-testid="stBottom"] > div > div,
    section.main, .main,
    .block-container,
    .element-container,
    div[class*="block-container"],
    div[class*="stChatFloatingInputContainer"],
    div[class*="stChatMessageContainer"] {
        background: transparent !important;
        background-color: transparent !important;
    }

    /* Bottom chat input area — must be dark not white */
    [data-testid="stBottom"] {
        background: rgba(8,0,31,0.95) !important;
        backdrop-filter: blur(20px) !important;
        border-top: 1px solid rgba(139,92,246,0.2) !important;
    }

    /* Hide Streamlit chrome */
    #MainMenu, footer, [data-testid="stToolbar"],
    [data-testid="stDecoration"], .stDeployButton,
    [data-testid="stHeader"], header { display: none !important; }
    .stApp > header  { display: none !important; }
    .stApp           { margin-top: 0 !important; }
    [data-testid="stAppViewContainer"]      { padding-top: 0 !important; }
    [data-testid="stAppViewBlockContainer"] { padding-top: 0 !important; }
    .main .block-container { padding-top: 0 !important; }

    /* ── Expander (collapsed past questions) ─────────────────── */
    [data-testid="stExpander"] {
        background: rgba(255,255,255,0.03) !important;
        border: 1px solid rgba(139,92,246,0.18) !important;
        border-radius: 14px !important;
        margin-bottom: 8px !important;
        backdrop-filter: blur(10px) !important;
    }
    [data-testid="stExpander"]:hover {
        border-color: rgba(139,92,246,0.4) !important;
    }
    [data-testid="stExpander"] summary {
        color: #94A3B8 !important;
        font-size: 13px !important;
        font-weight: 500 !important;
        padding: 10px 16px !important;
    }
    [data-testid="stExpander"] summary:hover {
        color: #C4B5FD !important;
    }
    [data-testid="stExpander"] summary svg {
        fill: #8B5CF6 !important;
    }
    /* Expander content area */
    [data-testid="stExpander"] > div:last-child {
        background: transparent !important;
        padding: 4px 16px 14px 16px !important;
    }

    /* ── Scrollbar ───────────────────────────────────────────── */
    ::-webkit-scrollbar { width: 4px; }
    ::-webkit-scrollbar-track { background: transparent; }
    ::-webkit-scrollbar-thumb { background: rgba(139,92,246,0.5); border-radius: 4px; }

    /* ── Main layout ─────────────────────────────────────────── */
    .block-container {
        padding: 0 !important;
        max-width: 820px !important;
        margin: 0 auto !important;
    }
    section[data-testid="stSidebar"] { display: none !important; }

    /* ── Aurora animated background orbs ────────────────────── */
    .aurora-wrap {
        position: fixed; top: 0; left: 0; right: 0; bottom: 0;
        z-index: 0; pointer-events: none; overflow: hidden;
        background: #08001F;
    }
    .orb {
        position: absolute; border-radius: 50%;
        filter: blur(80px); opacity: 0.55;
    }
    .orb-1 {
        width: 650px; height: 650px;
        background: radial-gradient(circle, rgba(139,92,246,0.7) 0%, transparent 70%);
        top: -200px; left: -180px;
        animation: drift1 14s ease-in-out infinite alternate;
    }
    .orb-2 {
        width: 500px; height: 500px;
        background: radial-gradient(circle, rgba(6,182,212,0.55) 0%, transparent 70%);
        bottom: -150px; right: -120px;
        animation: drift2 18s ease-in-out infinite alternate;
    }
    .orb-3 {
        width: 380px; height: 380px;
        background: radial-gradient(circle, rgba(244,114,182,0.45) 0%, transparent 70%);
        top: 45%; left: 55%;
        animation: drift3 22s ease-in-out infinite alternate;
    }
    .orb-4 {
        width: 280px; height: 280px;
        background: radial-gradient(circle, rgba(16,185,129,0.35) 0%, transparent 70%);
        top: 20%; right: 10%;
        animation: drift4 16s ease-in-out infinite alternate;
    }
    @keyframes drift1 {
        0%   { transform: translate(0px,   0px) scale(1);   }
        100% { transform: translate(60px, 80px) scale(1.1); }
    }
    @keyframes drift2 {
        0%   { transform: translate(0px,    0px) scale(1);    }
        100% { transform: translate(-50px, -60px) scale(1.15); }
    }
    @keyframes drift3 {
        0%   { transform: translate(0px, 0px);  }
        100% { transform: translate(-80px, 60px); }
    }
    @keyframes drift4 {
        0%   { transform: translate(0px, 0px) scale(1);    }
        100% { transform: translate(40px, -70px) scale(0.9); }
    }

    /* ── Chat wrapper ────────────────────────────────────────── */
    .chat-wrapper {
        position: relative; z-index: 1;
        padding: 20px 16px 120px 16px;
        min-height: 100vh;
    }

    /* ── Top header bar ──────────────────────────────────────── */
    .top-bar {
        display: flex; align-items: center; gap: 14px;
        padding: 18px 24px 14px 24px;
        border-bottom: 1px solid rgba(139,92,246,0.15);
        margin-bottom: 24px;
        position: sticky; top: 0; z-index: 100;
        background: rgba(8,0,31,0.7);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
    }
    .bot-avatar-lg {
        width: 46px; height: 46px; border-radius: 14px;
        background: linear-gradient(135deg, #7C3AED, #06B6D4);
        display: flex; align-items: center; justify-content: center;
        font-size: 22px;
        box-shadow: 0 0 20px rgba(139,92,246,0.6), 0 0 40px rgba(139,92,246,0.2);
        flex-shrink: 0;
    }
    .bot-name {
        font-size: 16px; font-weight: 700; color: #FFFFFF; line-height: 1.2;
    }
    .bot-status {
        font-size: 11px; color: #10B981; font-weight: 500;
        display: flex; align-items: center; gap: 5px;
    }
    .status-dot {
        width: 7px; height: 7px; border-radius: 50%;
        background: #10B981;
        box-shadow: 0 0 8px #10B981;
        animation: pulse-dot 2s infinite;
    }
    @keyframes pulse-dot {
        0%, 100% { opacity: 1; }
        50%       { opacity: 0.4; }
    }
    .brand-tag {
        margin-left: auto; font-size: 11px; font-weight: 600;
        color: rgba(139,92,246,0.8);
        background: rgba(139,92,246,0.12);
        border: 1px solid rgba(139,92,246,0.25);
        padding: 3px 10px; border-radius: 20px;
        letter-spacing: 0.5px;
    }

    /* ── Chat message bubbles ────────────────────────────────── */
    [data-testid="stChatMessage"] {
        background: transparent !important;
        border: none !important;
        padding: 6px 0 !important;
        gap: 12px !important;
    }
    /* Bot bubble */
    [data-testid="stChatMessage"]:has(> [data-testid="stChatMessageContent"]) {
        animation: slideInLeft 0.35s ease;
    }
    @keyframes slideInLeft {
        from { opacity: 0; transform: translateX(-18px); }
        to   { opacity: 1; transform: translateX(0); }
    }
    /* Bot message content box */
    [data-testid="stChatMessage"] [data-testid="stChatMessageContent"] {
        background: rgba(139,92,246,0.08) !important;
        border: 1px solid rgba(139,92,246,0.22) !important;
        border-radius: 4px 20px 20px 20px !important;
        backdrop-filter: blur(16px) !important;
        -webkit-backdrop-filter: blur(16px) !important;
        padding: 16px 20px !important;
        color: #E2E8F0 !important;
    }
    /* Custom bot avatar */
    [data-testid="stChatMessage"] [data-testid="chatAvatarIcon-assistant"] {
        background: linear-gradient(135deg, #7C3AED, #06B6D4) !important;
        border-radius: 12px !important;
        box-shadow: 0 0 16px rgba(139,92,246,0.5) !important;
    }
    /* Custom user avatar */
    [data-testid="stChatMessage"] [data-testid="chatAvatarIcon-user"] {
        background: linear-gradient(135deg, #EC4899, #8B5CF6) !important;
        border-radius: 12px !important;
        box-shadow: 0 0 16px rgba(236,72,153,0.5) !important;
    }

    /* ── Glassmorphism card ──────────────────────────────────── */
    .glass-card {
        background: rgba(255,255,255,0.04);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(255,255,255,0.1);
        border-radius: 20px;
        padding: 24px;
        margin: 8px 0;
    }
    .glass-card-purple {
        background: rgba(139,92,246,0.07);
        backdrop-filter: blur(20px);
        -webkit-backdrop-filter: blur(20px);
        border: 1px solid rgba(139,92,246,0.25);
        border-radius: 20px;
        padding: 24px;
        margin: 8px 0;
    }

    /* ── Gradient text ───────────────────────────────────────── */
    .grad-text-purple {
        background: linear-gradient(135deg, #A78BFA, #60A5FA);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        background-clip: text; font-weight: 800;
    }
    .grad-text-pink {
        background: linear-gradient(135deg, #F471B5, #A78BFA);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        background-clip: text; font-weight: 800;
    }
    .grad-text-cyan {
        background: linear-gradient(135deg, #67E8F9, #A78BFA);
        -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        background-clip: text; font-weight: 800;
    }

    /* ── Neon glow buttons ───────────────────────────────────── */
    .stButton > button {
        font-family: 'Inter', sans-serif !important;
        font-weight: 600 !important;
        border-radius: 12px !important;
        transition: all 0.2s ease !important;
        letter-spacing: 0.3px !important;
    }
    .stButton > button[kind="primary"] {
        background: linear-gradient(135deg, #7C3AED, #4F46E5) !important;
        border: none !important;
        color: #FFFFFF !important;
        box-shadow: 0 0 20px rgba(124,58,237,0.45), 0 4px 15px rgba(0,0,0,0.3) !important;
    }
    .stButton > button[kind="primary"]:hover {
        transform: translateY(-2px) scale(1.02) !important;
        box-shadow: 0 0 30px rgba(124,58,237,0.7), 0 8px 25px rgba(0,0,0,0.3) !important;
    }
    .stButton > button[kind="secondary"] {
        background: rgba(255,255,255,0.05) !important;
        border: 1px solid rgba(139,92,246,0.35) !important;
        color: #C4B5FD !important;
        backdrop-filter: blur(10px) !important;
    }
    .stButton > button[kind="secondary"]:hover {
        background: rgba(139,92,246,0.15) !important;
        border-color: rgba(139,92,246,0.6) !important;
        color: #FFFFFF !important;
        box-shadow: 0 0 20px rgba(139,92,246,0.3) !important;
        transform: translateY(-1px) !important;
    }

    /* ── Grade picker grid ───────────────────────────────────── */
    .grade-btn > .stButton > button {
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid rgba(139,92,246,0.3) !important;
        color: #C4B5FD !important;
        border-radius: 14px !important;
        padding: 14px 8px !important;
        font-size: 15px !important;
        font-weight: 700 !important;
        backdrop-filter: blur(10px) !important;
        width: 100% !important;
    }
    .grade-btn > .stButton > button:hover {
        background: rgba(139,92,246,0.2) !important;
        border-color: #8B5CF6 !important;
        color: #FFFFFF !important;
        box-shadow: 0 0 18px rgba(139,92,246,0.45) !important;
        transform: translateY(-2px) scale(1.04) !important;
    }
    .grade-btn-active > .stButton > button {
        background: linear-gradient(135deg, #7C3AED, #4F46E5) !important;
        border-color: transparent !important;
        color: #FFFFFF !important;
        box-shadow: 0 0 22px rgba(124,58,237,0.6) !important;
    }

    /* ── Subject pills ───────────────────────────────────────── */
    .subj-btn > .stButton > button {
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid rgba(6,182,212,0.3) !important;
        color: #67E8F9 !important;
        border-radius: 30px !important;
        padding: 10px 20px !important;
        font-size: 14px !important;
        font-weight: 600 !important;
        backdrop-filter: blur(10px) !important;
    }
    .subj-btn > .stButton > button:hover {
        background: rgba(6,182,212,0.15) !important;
        border-color: #06B6D4 !important;
        color: #FFFFFF !important;
        box-shadow: 0 0 18px rgba(6,182,212,0.4) !important;
        transform: translateY(-1px) !important;
    }
    .subj-btn-active > .stButton > button {
        background: linear-gradient(135deg, #0891B2, #06B6D4) !important;
        border-color: transparent !important;
        color: #FFFFFF !important;
        box-shadow: 0 0 20px rgba(6,182,212,0.55) !important;
    }

    /* ── Count picker ────────────────────────────────────────── */
    .count-btn > .stButton > button {
        background: rgba(255,255,255,0.04) !important;
        border: 1px solid rgba(244,114,182,0.3) !important;
        color: #F9A8D4 !important;
        border-radius: 14px !important;
        padding: 18px 8px !important;
        font-size: 22px !important;
        font-weight: 800 !important;
        backdrop-filter: blur(10px) !important;
        width: 100% !important;
    }
    .count-btn > .stButton > button:hover {
        background: rgba(244,114,182,0.15) !important;
        border-color: #EC4899 !important;
        color: #FFFFFF !important;
        box-shadow: 0 0 20px rgba(236,72,153,0.45) !important;
        transform: translateY(-2px) scale(1.04) !important;
    }

    /* ── Answer buttons (A B C D) ────────────────────────────── */
    .ans-btn > .stButton > button {
        background: rgba(255,255,255,0.04) !important;
        border: 1.5px solid rgba(139,92,246,0.3) !important;
        color: #E2E8F0 !important;
        border-radius: 14px !important;
        padding: 16px 18px !important;
        font-size: 15px !important;
        font-weight: 500 !important;
        text-align: left !important;
        backdrop-filter: blur(12px) !important;
        width: 100% !important;
        transition: all 0.18s ease !important;
    }
    .ans-btn > .stButton > button:hover {
        background: rgba(139,92,246,0.18) !important;
        border-color: #8B5CF6 !important;
        color: #FFFFFF !important;
        box-shadow: 0 0 22px rgba(139,92,246,0.4), inset 0 0 20px rgba(139,92,246,0.05) !important;
        transform: translateX(4px) !important;
    }

    /* ── Answer result states ────────────────────────────────── */
    .ans-correct {
        background: rgba(16,185,129,0.12) !important;
        border: 1.5px solid #10B981 !important;
        border-radius: 14px !important;
        padding: 16px 20px !important;
        color: #6EE7B7 !important;
        font-size: 15px !important;
        font-weight: 500 !important;
        display: flex; align-items: center; gap: 14px;
        box-shadow: 0 0 20px rgba(16,185,129,0.25) !important;
        margin-bottom: 8px;
        animation: popIn 0.3s ease;
    }
    .ans-wrong {
        background: rgba(239,68,68,0.1) !important;
        border: 1.5px solid rgba(239,68,68,0.5) !important;
        border-radius: 14px !important;
        padding: 16px 20px !important;
        color: #FCA5A5 !important;
        font-size: 15px !important;
        font-weight: 500 !important;
        display: flex; align-items: center; gap: 14px;
        margin-bottom: 8px;
    }
    .ans-neutral {
        background: rgba(255,255,255,0.02) !important;
        border: 1.5px solid rgba(255,255,255,0.08) !important;
        border-radius: 14px !important;
        padding: 16px 20px !important;
        color: #4B5563 !important;
        font-size: 15px !important;
        display: flex; align-items: center; gap: 14px;
        margin-bottom: 8px;
    }
    .ans-label {
        min-width: 32px; height: 32px; border-radius: 8px;
        display: inline-flex; align-items: center; justify-content: center;
        font-weight: 800; font-size: 13px; flex-shrink: 0;
    }
    .ans-correct .ans-label { background: rgba(16,185,129,0.3); color: #10B981; }
    .ans-wrong   .ans-label { background: rgba(239,68,68,0.3);  color: #EF4444; }
    .ans-neutral .ans-label { background: rgba(255,255,255,0.05); color: #374151; }
    @keyframes popIn {
        0%   { transform: scale(0.96); opacity: 0.7; }
        60%  { transform: scale(1.02); }
        100% { transform: scale(1);    opacity: 1; }
    }

    /* ── Difficulty pills ────────────────────────────────────── */
    .diff-easy   { background:rgba(16,185,129,0.15); color:#34D399; border:1px solid rgba(16,185,129,0.3); padding:3px 12px; border-radius:20px; font-size:11px; font-weight:700; display:inline-block; letter-spacing:.5px; }
    .diff-medium { background:rgba(245,158,11,0.15); color:#FCD34D; border:1px solid rgba(245,158,11,0.3); padding:3px 12px; border-radius:20px; font-size:11px; font-weight:700; display:inline-block; letter-spacing:.5px; }
    .diff-hard   { background:rgba(239,68,68,0.15);  color:#F87171; border:1px solid rgba(239,68,68,0.3);  padding:3px 12px; border-radius:20px; font-size:11px; font-weight:700; display:inline-block; letter-spacing:.5px; }

    /* ── Knowledge level badges ──────────────────────────────── */
    .lvl-exceptional { background:linear-gradient(135deg,#F59E0B,#EF4444); color:#fff; padding:5px 18px; border-radius:20px; font-size:13px; font-weight:700; display:inline-block; box-shadow:0 0 16px rgba(245,158,11,0.5); }
    .lvl-advanced    { background:linear-gradient(135deg,#7C3AED,#4F46E5); color:#fff; padding:5px 18px; border-radius:20px; font-size:13px; font-weight:700; display:inline-block; box-shadow:0 0 16px rgba(124,58,237,0.5); }
    .lvl-proficient  { background:linear-gradient(135deg,#4F46E5,#0EA5E9); color:#fff; padding:5px 18px; border-radius:20px; font-size:13px; font-weight:700; display:inline-block; box-shadow:0 0 16px rgba(79,70,229,0.5); }
    .lvl-developing  { background:linear-gradient(135deg,#F59E0B,#F97316); color:#fff; padding:5px 18px; border-radius:20px; font-size:13px; font-weight:700; display:inline-block; box-shadow:0 0 16px rgba(249,115,22,0.4); }
    .lvl-needs       { background:linear-gradient(135deg,#EF4444,#DC2626); color:#fff; padding:5px 18px; border-radius:20px; font-size:13px; font-weight:700; display:inline-block; box-shadow:0 0 16px rgba(239,68,68,0.4); }

    /* ── Progress bar ────────────────────────────────────────── */
    .prog-wrap {
        background: rgba(255,255,255,0.06); border-radius: 10px;
        height: 6px; width: 100%; margin: 10px 0 18px 0; overflow: hidden;
    }
    .prog-fill {
        height: 6px; border-radius: 10px;
        background: linear-gradient(90deg, #7C3AED, #06B6D4);
        box-shadow: 0 0 10px rgba(139,92,246,0.6);
        transition: width 0.5s ease;
    }

    /* ── Score ring ──────────────────────────────────────────── */
    .ring-wrap { display:flex; flex-direction:column; align-items:center; padding:20px 0; }
    .ring-inner { position:relative; width:180px; height:180px; }
    .ring-inner svg { transform:rotate(-90deg); filter: drop-shadow(0 0 12px var(--ring-color)); }
    .ring-text { position:absolute; top:50%; left:50%; transform:translate(-50%,-50%); text-align:center; }
    .ring-pct  { font-size:40px; font-weight:900; color:#FFFFFF; line-height:1; }
    .ring-lbl  { font-size:10px; color:#94A3B8; text-transform:uppercase; letter-spacing:1.5px; margin-top:4px; }

    /* ── Metric cards ────────────────────────────────────────── */
    .met-card {
        background: rgba(255,255,255,0.04);
        border: 1px solid rgba(255,255,255,0.08);
        backdrop-filter: blur(16px);
        border-radius: 16px; padding: 18px 12px;
        text-align: center; margin-bottom: 10px;
        transition: border-color 0.2s;
    }
    .met-card:hover { border-color: rgba(139,92,246,0.4); }
    .met-val { font-size:26px; font-weight:800; color:#FFFFFF; line-height:1; margin-bottom:5px; }
    .met-lbl { font-size:10px; color:#64748B; font-weight:600; text-transform:uppercase; letter-spacing:.8px; }

    /* ── Strength / Improvement ──────────────────────────────── */
    .str-item {
        background: rgba(16,185,129,0.07); border:1px solid rgba(16,185,129,0.2);
        border-left:3px solid #10B981; border-radius:12px;
        padding:12px 16px; margin-bottom:8px; color:#A7F3D0; font-size:14px; line-height:1.5;
    }
    .imp-item {
        background: rgba(245,158,11,0.07); border:1px solid rgba(245,158,11,0.2);
        border-left:3px solid #F59E0B; border-radius:12px;
        padding:12px 16px; margin-bottom:8px; color:#FDE68A; font-size:14px; line-height:1.5;
    }

    /* ── Explanation box ─────────────────────────────────────── */
    .explain {
        background: rgba(6,182,212,0.07);
        border: 1px solid rgba(6,182,212,0.25);
        border-radius: 14px; padding: 14px 18px; margin-top: 14px;
        color: #A5F3FC; font-size:14px; line-height:1.6;
        box-shadow: 0 0 12px rgba(6,182,212,0.1);
    }

    /* ── Recommendation ──────────────────────────────────────── */
    .rec-box {
        background: linear-gradient(135deg, rgba(124,58,237,0.15), rgba(6,182,212,0.1));
        border: 1px solid rgba(139,92,246,0.35); border-radius: 18px;
        padding: 22px 24px; margin-top:12px;
        box-shadow: 0 0 30px rgba(139,92,246,0.12);
    }
    .rec-box p { color:#C4B5FD !important; font-size:15px; line-height:1.7; margin:0 !important; }

    /* ── Typing indicator ────────────────────────────────────── */
    .typing { display:flex; gap:5px; align-items:center; padding:4px 0; }
    .typing span {
        width:8px; height:8px; border-radius:50%;
        background: #8B5CF6; display:inline-block;
        animation: typingDot 1.2s infinite ease-in-out;
    }
    .typing span:nth-child(2) { animation-delay:.2s; }
    .typing span:nth-child(3) { animation-delay:.4s; }
    @keyframes typingDot {
        0%,80%,100% { transform:scale(0.6); opacity:0.4; }
        40%          { transform:scale(1);   opacity:1;   }
    }

    /* ── Confetti burst (high scores) ───────────────────────── */
    .confetti-wrap {
        text-align:center; font-size:32px; letter-spacing:6px;
        animation: confettiBurst 0.8s ease;
        margin-bottom:8px;
    }
    @keyframes confettiBurst {
        0%   { transform:scale(0.5) rotate(-10deg); opacity:0; }
        60%  { transform:scale(1.2) rotate(5deg);  opacity:1; }
        100% { transform:scale(1)   rotate(0deg);  opacity:1; }
    }

    /* ── Chat input bar (bottom) ─────────────────────────────── */
    /* Outer fixed container */
    [data-testid="stBottom"] {
        background: rgba(8, 0, 31, 0.92) !important;
        backdrop-filter: blur(20px) !important;
        -webkit-backdrop-filter: blur(20px) !important;
        border-top: 1px solid rgba(139,92,246,0.25) !important;
        padding: 14px 20px !important;
    }
    /* The input pill */
    [data-testid="stChatInput"] {
        background: #1E1040 !important;
        border: 2px solid rgba(139,92,246,0.55) !important;
        border-radius: 16px !important;
        box-shadow: 0 0 22px rgba(139,92,246,0.25), inset 0 1px 0 rgba(255,255,255,0.06) !important;
    }
    [data-testid="stChatInput"]:focus-within {
        border-color: #8B5CF6 !important;
        box-shadow: 0 0 30px rgba(139,92,246,0.45) !important;
    }
    /* Text inside input */
    [data-testid="stChatInput"] textarea {
        background: transparent !important;
        color: #FFFFFF !important;
        font-family: 'Inter', sans-serif !important;
        font-size: 15px !important;
        caret-color: #8B5CF6 !important;
    }
    /* Placeholder */
    [data-testid="stChatInput"] textarea::placeholder {
        color: #6D5FA6 !important;
        font-style: italic !important;
    }
    /* Send button */
    [data-testid="stChatInput"] button {
        background: linear-gradient(135deg, #7C3AED, #4F46E5) !important;
        border-radius: 10px !important;
        color: #FFFFFF !important;
        border: none !important;
        box-shadow: 0 0 14px rgba(124,58,237,0.5) !important;
    }
    [data-testid="stChatInput"] button:hover {
        box-shadow: 0 0 24px rgba(124,58,237,0.8) !important;
        transform: scale(1.08) !important;
    }

    /* ── Spinner ─────────────────────────────────────────────── */
    .stSpinner > div { border-top-color: #8B5CF6 !important; }

    /* ── Section divider ─────────────────────────────────────── */
    .neon-divider {
        border: none;
        height: 1px;
        background: linear-gradient(90deg, transparent, rgba(139,92,246,0.4), rgba(6,182,212,0.4), transparent);
        margin: 20px 0;
    }

    /* ── Plotly transparent bg ───────────────────────────────── */
    .js-plotly-plot .plotly { border-radius: 16px; }

    /* ── Warning / error ─────────────────────────────────────── */
    .stAlert { border-radius:14px !important; backdrop-filter:blur(10px) !important; }
    </style>
    """


def get_aurora_html() -> str:
    """Animated aurora background orbs — injected once at app start."""
    return """
    <div class="aurora-wrap">
        <div class="orb orb-1"></div>
        <div class="orb orb-2"></div>
        <div class="orb orb-3"></div>
        <div class="orb orb-4"></div>
    </div>
    """
