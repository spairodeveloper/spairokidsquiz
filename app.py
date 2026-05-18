"""
app.py  —  Spairo Academy Knowledge Evaluator
Chatbot-style conversational interface powered by Gemini 2.0 Flash.
Jazzy glassmorphism UI with aurora animated background.
Run:  streamlit run app.py
"""

import streamlit as st
import plotly.graph_objects as go
from datetime import datetime

from database import (
    init_db, create_evaluation, save_answers, save_report,
    get_all_evaluations, get_student_names, get_evaluation,
    get_evaluation_count,
)
from gemini_engine import (
    generate_questions, generate_report,
    Question as GQuestion,
)
from styles import get_css, get_aurora_html

# ── Page config  (MUST be first) ─────────────────────────────────────────────
st.set_page_config(
    page_title="Spairo Academy",
    page_icon="🎓",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Bootstrap ─────────────────────────────────────────────────────────────────
init_db()
st.markdown(get_css(),         unsafe_allow_html=True)
st.markdown(get_aurora_html(), unsafe_allow_html=True)

# ── Constants ─────────────────────────────────────────────────────────────────
SUBJECTS   = ["Math", "Reading", "Science", "History", "Grammar", "General Knowledge"]
SUBJ_ICONS = {"Math":"🔢","Reading":"📖","Science":"🔬","History":"🏛️","Grammar":"✍️","General Knowledge":"🌍"}
GRADES     = list(range(1, 13))

BOT_INTRO = (
    "Hey there! 👋 I'm **Sparky**, your AI tutor from **Spairo Academy**.\n\n"
    "I'll create a personalised quiz for your student and give you a full performance "
    "report — powered by Gemini AI. It takes less than 10 minutes!\n\n"
    "Let's start. **What's your student's first name?**"
)

# ── Session state defaults ─────────────────────────────────────────────────────
_DEFAULTS = {
    "messages":        [],        # chat history [{role, content, html}]
    "state":           "start",   # conversation state machine
    "student_name":    "",
    "grade":           None,
    "subjects":        [],
    "question_count":  None,
    "questions":       [],
    "current_q":       0,
    "answers":         {},
    "answer_submitted":False,
    "selected_answer": None,
    "evaluation_id":   None,
    "report":          None,
    "show_history":    False,
    "view_eval_id":    None,
}
for k, v in _DEFAULTS.items():
    if k not in st.session_state:
        st.session_state[k] = v


# ── Helpers ───────────────────────────────────────────────────────────────────
def bot(content: str, html: bool = False):
    """Append a bot message to history."""
    st.session_state.messages.append({"role": "assistant", "content": content, "html": html})

def user_msg(content: str):
    """Append a user message to history."""
    st.session_state.messages.append({"role": "user", "content": content, "html": False})

def set_state(s: str):
    st.session_state.state = s

def diff_pill(d: str) -> str:
    cls = {"Easy":"diff-easy","Medium":"diff-medium","Hard":"diff-hard"}.get(d,"diff-medium")
    return f'<span class="{cls}">{d}</span>'

def level_badge(level: str) -> str:
    cls = {
        "Exceptional":"lvl-exceptional","Advanced":"lvl-advanced",
        "Proficient":"lvl-proficient","Developing":"lvl-developing",
        "Needs Support":"lvl-needs",
    }.get(level,"lvl-proficient")
    return f'<span class="{cls}">{level}</span>'

def score_ring_html(score: int, level: str) -> str:
    color = {
        "Exceptional":"#F59E0B","Advanced":"#8B5CF6",
        "Proficient":"#4F46E5","Developing":"#F97316","Needs Support":"#EF4444",
    }.get(level,"#4F46E5")
    r = 54
    circ  = 2 * 3.14159 * r
    offset = circ * (1 - score / 100)
    return f"""
    <div class="ring-wrap">
      <div class="ring-inner" style="--ring-color:{color}">
        <svg viewBox="0 0 120 120" width="180" height="180">
          <circle cx="60" cy="60" r="{r}" fill="none" stroke="rgba(255,255,255,0.06)" stroke-width="11"/>
          <circle cx="60" cy="60" r="{r}" fill="none" stroke="{color}" stroke-width="11"
                  stroke-linecap="round"
                  stroke-dasharray="{circ:.1f}" stroke-dashoffset="{offset:.1f}"/>
        </svg>
        <div class="ring-text">
          <div class="ring-pct">{score}%</div>
          <div class="ring-lbl">Score</div>
        </div>
      </div>
      <div style="margin-top:14px">{level_badge(level)}</div>
    </div>"""

def subject_chart(subject_scores: dict) -> go.Figure:
    names  = list(subject_scores.keys())
    vals   = list(subject_scores.values())
    colors = ["#10B981" if v>=80 else "#F59E0B" if v>=60 else "#EF4444" for v in vals]
    fig = go.Figure(go.Bar(
        x=names, y=vals, marker_color=colors,
        text=[f"{v}%" for v in vals], textposition="outside",
        textfont=dict(color="white", size=13, family="Inter"),
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(color="white", family="Inter"), height=220,
        margin=dict(l=0, r=0, t=10, b=0),
        yaxis=dict(range=[0,115], showgrid=False, showticklabels=False),
        xaxis=dict(showgrid=False, tickfont=dict(size=13,color="#CBD5E1")),
        showlegend=False,
    )
    return fig

def progress_bar(current: int, total: int) -> str:
    pct = int(current / total * 100)
    return f"""
    <div style="display:flex;align-items:center;gap:12px;margin-bottom:16px;">
      <div class="prog-wrap" style="flex:1">
        <div class="prog-fill" style="width:{pct}%"></div>
      </div>
      <span style="color:#8B5CF6;font-size:12px;font-weight:700;white-space:nowrap;">
        {current}/{total}
      </span>
    </div>"""

def confetti(score: int) -> str:
    if score >= 90:
        return '<div class="confetti-wrap">🎉🌟✨🏆🎊</div>'
    elif score >= 80:
        return '<div class="confetti-wrap">🎉⭐✨🎊</div>'
    return ""


# ── Render chat history ───────────────────────────────────────────────────────
def render_history():
    """
    Outside quiz: show all messages as chat bubbles.
    During/after quiz: collapse setup messages + answered Q&As into expanders.
    Only the live question is shown fully.
    """
    state = st.session_state.state

    if state not in ["quiz", "reporting", "results"]:
        # Normal chat flow — show everything as bubbles
        for msg in st.session_state.messages:
            with st.chat_message(msg["role"], avatar="🎓" if msg["role"] == "assistant" else "👤"):
                if msg.get("html"):
                    st.markdown(msg["content"], unsafe_allow_html=True)
                else:
                    st.markdown(msg["content"])
    else:
        # ── Quiz is active — collapse past, show only current ──
        # 1. Setup messages collapsed into one expander
        if st.session_state.messages:
            name  = st.session_state.student_name
            grade = st.session_state.grade
            subjs = ", ".join(st.session_state.subjects)
            count = st.session_state.question_count
            with st.expander(
                f"💬  Setup — {name} · Grade {grade} · {subjs} · {count} questions",
                expanded=False,
            ):
                for msg in st.session_state.messages:
                    role_icon = "🎓" if msg["role"] == "assistant" else "👤"
                    bubble_bg = "rgba(139,92,246,0.08)" if msg["role"] == "assistant" else "rgba(236,72,153,0.08)"
                    border    = "rgba(139,92,246,0.2)"  if msg["role"] == "assistant" else "rgba(236,72,153,0.2)"
                    align     = "left" if msg["role"] == "assistant" else "right"
                    content   = msg["content"].replace("\n", "<br>")
                    st.markdown(f"""
                    <div style="display:flex;justify-content:{align};margin-bottom:6px;">
                      <div style="background:{bubble_bg};border:1px solid {border};
                                  border-radius:12px;padding:8px 14px;max-width:85%;
                                  font-size:13px;color:#CBD5E1;line-height:1.5;">
                        {role_icon} {content}
                      </div>
                    </div>""", unsafe_allow_html=True)

        # 2. Already-answered questions — each as a collapsed expander
        questions = st.session_state.questions
        answers   = st.session_state.answers
        current   = st.session_state.current_q

        for i in range(current):
            q          = questions[i]
            selected   = answers.get(str(q["id"]), "")
            is_correct = selected == q["correct_answer"]
            icon       = "✅" if is_correct else "❌"
            short_q    = q["question"][:60] + ("…" if len(q["question"]) > 60 else "")

            with st.expander(
                f"{icon}  Q{i+1} · {q['subject']} · {short_q}",
                expanded=False,
            ):
                # Compact answer review inside expander
                for letter, text in q["choices"].items():
                    if letter == q["correct_answer"]:
                        cls = "ans-correct"
                    elif letter == selected and letter != q["correct_answer"]:
                        cls = "ans-wrong"
                    else:
                        cls = "ans-neutral"
                    st.markdown(
                        f'<div class="{cls}" style="margin-bottom:6px;">'
                        f'<span class="ans-label">{"✓" if letter==q["correct_answer"] else ("✗" if letter==selected else letter)}</span>'
                        f'{letter} · {text}</div>',
                        unsafe_allow_html=True,
                    )
                st.markdown(
                    f'<div class="explain" style="margin-top:8px;">💡 {q["explanation"]}</div>',
                    unsafe_allow_html=True,
                )


# ── Top navigation bar ────────────────────────────────────────────────────────
def render_topbar():
    col_logo, col_hist, col_new = st.columns([5, 1.3, 1.3])
    with col_logo:
        st.markdown("""
        <div class="top-bar">
          <div class="bot-avatar-lg">🎓</div>
          <div>
            <div class="bot-name">Sparky — AI Evaluator</div>
            <div class="bot-status">
              <span class="status-dot"></span> Online · Gemini 2.0 Flash
            </div>
          </div>
          <div class="brand-tag">Spairo Academy</div>
        </div>""", unsafe_allow_html=True)

    # Tiny buttons float right
    with col_hist:
        if st.button("📋 History", use_container_width=True):
            st.session_state.show_history = not st.session_state.show_history
            st.session_state.view_eval_id = None
            st.rerun()
    with col_new:
        if st.button("✨ New", type="primary", use_container_width=True):
            for k, v in _DEFAULTS.items():
                st.session_state[k] = v
            bot(BOT_INTRO)
            set_state("wait_name")
            st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
#  STATE HANDLERS  (each renders interactive widgets for the current step)
# ══════════════════════════════════════════════════════════════════════════════

# ── START  ────────────────────────────────────────────────────────────────────
def handle_start():
    bot(BOT_INTRO)
    set_state("wait_name")
    st.rerun()


# ── WAIT FOR NAME  ────────────────────────────────────────────────────────────
def handle_wait_name():
    name = st.chat_input("Type the student's first name…")
    if name and name.strip():
        st.session_state.student_name = name.strip().title()
        user_msg(name.strip().title())
        bot(
            f"Awesome, **{st.session_state.student_name}**! 🌟\n\n"
            "What grade are they in? Pick below 👇"
        )
        set_state("wait_grade")
        st.rerun()


# ── WAIT FOR GRADE  ───────────────────────────────────────────────────────────
def handle_wait_grade():
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    cols = st.columns(6)
    for i, g in enumerate(GRADES):
        with cols[i % 6]:
            st.markdown('<div class="grade-btn">', unsafe_allow_html=True)
            if st.button(f"G{g}", key=f"grade_{g}", use_container_width=True):
                st.session_state.grade = g
                user_msg(f"Grade {g}")
                bot(
                    f"Grade {g} — perfect! 📚\n\n"
                    "Now pick **up to 3 subjects** for the quiz:"
                )
                set_state("wait_subjects")
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)


# ── WAIT FOR SUBJECTS  ────────────────────────────────────────────────────────
def handle_wait_subjects():
    selected = st.session_state.subjects
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

    cols = st.columns(3)
    for i, subj in enumerate(SUBJECTS):
        is_active = subj in selected
        css_class = "subj-btn-active" if is_active else "subj-btn"
        with cols[i % 3]:
            st.markdown(f'<div class="{css_class}">', unsafe_allow_html=True)
            label = f"{'✓ ' if is_active else ''}{SUBJ_ICONS[subj]}  {subj}"
            if st.button(label, key=f"subj_{subj}", use_container_width=True):
                if is_active:
                    selected.remove(subj)
                elif len(selected) < 3:
                    selected.append(subj)
                st.session_state.subjects = selected
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)

    st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

    if selected:
        st.markdown(
            f"<p style='color:#67E8F9;font-size:13px;margin:0;'>Selected: "
            f"<b>{', '.join(selected)}</b></p>",
            unsafe_allow_html=True,
        )
        if st.button("Confirm Subjects  →", type="primary"):
            user_msg(", ".join(selected))
            bot(
                f"Great choices! 🎯\n\n"
                "Last question — how many questions do you want?"
            )
            set_state("wait_count")
            st.rerun()
    else:
        st.markdown(
            "<p style='color:#475569;font-size:13px;margin:0;'>Select at least 1 subject</p>",
            unsafe_allow_html=True,
        )


# ── WAIT FOR QUESTION COUNT  ──────────────────────────────────────────────────
def handle_wait_count():
    st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)
    c6, c8, c10 = st.columns(3)
    opts = [(6,"~3–4 min","Quick check"), (8,"~4–6 min","Standard"), (10,"~6–8 min","Full test")]
    for col, (n, t, lbl) in zip([c6, c8, c10], opts):
        with col:
            st.markdown('<div class="count-btn">', unsafe_allow_html=True)
            if st.button(f"{n}\n{lbl}\n{t}", key=f"cnt_{n}", use_container_width=True):
                st.session_state.question_count = n
                user_msg(f"{n} questions")
                bot(
                    f"Let's do **{n} questions** for **{st.session_state.student_name}**! 🚀\n\n"
                    f"Generating {n} personalised Grade {st.session_state.grade} questions "
                    f"in **{', '.join(st.session_state.subjects)}**…"
                )
                set_state("generating")
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)


# ── GENERATING  ───────────────────────────────────────────────────────────────
def handle_generating():
    with st.spinner("Sparky is crafting your questions… ✨"):
        try:
            qset = generate_questions(
                st.session_state.grade,
                st.session_state.subjects,
                st.session_state.question_count,
            )
            q_dicts = [q.model_dump() for q in qset.questions]
            st.session_state.questions = q_dicts

            eval_id = create_evaluation(
                st.session_state.student_name,
                st.session_state.grade,
                st.session_state.subjects,
                st.session_state.question_count,
                q_dicts,
            )
            st.session_state.evaluation_id  = eval_id
            st.session_state.current_q      = 0
            st.session_state.answers        = {}
            st.session_state.answer_submitted = False
            st.session_state.selected_answer  = None

            bot(
                f"🎉 Questions ready! Let's go!\n\n"
                f"**{st.session_state.question_count} questions** · Grade {st.session_state.grade} · "
                f"{', '.join(st.session_state.subjects)}\n\n"
                "Answer each question by clicking your choice. Ready? Here comes **Question 1!**"
            )
            set_state("quiz")
            st.rerun()

        except Exception as e:
            st.error(f"❌ Oops! {e} — please try again.")
            if st.button("← Restart"):
                for k, v in _DEFAULTS.items():
                    st.session_state[k] = v
                st.rerun()


# ── QUIZ  ─────────────────────────────────────────────────────────────────────
def handle_quiz():
    questions = st.session_state.questions
    idx       = st.session_state.current_q
    total     = len(questions)

    if idx >= total:
        set_state("reporting")
        st.rerun()
        return

    q        = questions[idx]
    q_num    = idx + 1
    answered = st.session_state.answer_submitted
    selected = st.session_state.selected_answer
    correct  = q["correct_answer"]

    # ── Question header ────────────────────────────────────────
    header_html = f"""
    <div style="margin-bottom:14px;">
      {progress_bar(q_num, total)}
      <div style="display:flex;align-items:center;gap:10px;margin-bottom:12px;flex-wrap:wrap;">
        {diff_pill(q["difficulty"])}
        <span style="color:#67E8F9;font-size:12px;font-weight:600;">{q["subject"]}</span>
        <span style="color:#374151;font-size:12px;margin-left:auto;">Q{q_num} of {total}</span>
      </div>
      <div style="font-size:18px;font-weight:600;color:#FFFFFF;line-height:1.55;">
        {q["question"]}
      </div>
    </div>"""

    with st.chat_message("assistant", avatar="🎓"):
        st.markdown(header_html, unsafe_allow_html=True)

        if not answered:
            # ── Clickable answer buttons ───────────────────────
            for letter, text in q["choices"].items():
                st.markdown('<div class="ans-btn">', unsafe_allow_html=True)
                if st.button(
                    f"**{letter}**  ·  {text}",
                    key=f"ans_{idx}_{letter}",
                    use_container_width=True,
                ):
                    st.session_state.selected_answer  = letter
                    st.session_state.answer_submitted = True
                    st.rerun()
                st.markdown("</div>", unsafe_allow_html=True)

        else:
            # ── Answer feedback ────────────────────────────────
            choices_html = ""
            for letter, text in q["choices"].items():
                if letter == correct:
                    choices_html += f'<div class="ans-correct"><span class="ans-label">✓</span>{letter} · {text}</div>'
                elif letter == selected and letter != correct:
                    choices_html += f'<div class="ans-wrong"><span class="ans-label">✗</span>{letter} · {text}</div>'
                else:
                    choices_html += f'<div class="ans-neutral"><span class="ans-label">{letter}</span>{text}</div>'

            result_icon = "✅" if selected == correct else "❌"
            result_text = "Correct!" if selected == correct else f"Not quite — the answer was **{correct}**"

            st.markdown(f"""
            {choices_html}
            <div style="margin:10px 0 4px 0;font-size:14px;font-weight:700;color:{'#34D399' if selected==correct else '#F87171'};">
                {result_icon} {result_text}
            </div>
            <div class="explain">
                <strong style="color:#67E8F9;">💡 Explanation:</strong><br>{q["explanation"]}
            </div>
            """, unsafe_allow_html=True)

            st.markdown("<div style='height:10px'></div>", unsafe_allow_html=True)

            is_last = idx == total - 1
            btn_txt = "🏁  Finish & Get My Report" if is_last else "Next Question  →"

            if st.button(btn_txt, type="primary", key=f"next_{idx}"):
                st.session_state.answers[str(q["id"])] = selected
                save_answers(st.session_state.evaluation_id, st.session_state.answers)
                if is_last:
                    bot(
                        f"Quiz complete! 🎊 You've answered all {total} questions.\n\n"
                        "Let me analyse **{name}'s** results now…".format(name=st.session_state.student_name)
                    )
                    set_state("reporting")
                else:
                    st.session_state.current_q       += 1
                    st.session_state.answer_submitted  = False
                    st.session_state.selected_answer   = None
                st.rerun()


# ── REPORTING  ────────────────────────────────────────────────────────────────
def handle_reporting():
    with st.spinner("Analysing results and building your report… 📊"):
        try:
            q_objects = [GQuestion(**q) for q in st.session_state.questions]
            report = generate_report(
                name=st.session_state.student_name,
                grade=st.session_state.grade,
                count=st.session_state.question_count,
                questions=q_objects,
                answers=st.session_state.answers,
            )
            save_report(
                evaluation_id=st.session_state.evaluation_id,
                overall_score=report.overall_score,
                knowledge_level=report.knowledge_level,
                subject_scores=report.subject_scores,
                strengths=report.strengths,
                improvements=report.improvements,
                recommendation=report.recommendation,
            )
            st.session_state.report = report.model_dump()
            set_state("results")
            st.rerun()

        except Exception as e:
            st.error(f"❌ Report generation failed: {e}")
            if st.button("← Retry"):
                set_state("reporting")
                st.rerun()


# ── RESULTS REPORT  ───────────────────────────────────────────────────────────
def handle_results():
    report    = st.session_state.report
    name      = st.session_state.student_name
    grade     = st.session_state.grade
    subjects  = st.session_state.subjects
    questions = st.session_state.questions
    answers   = st.session_state.answers
    score     = report["overall_score"]
    level     = report["knowledge_level"]

    correct = sum(
        1 for q in questions
        if answers.get(str(q["id"])) == q["correct_answer"]
    )

    # Bot sends the report as a message
    with st.chat_message("assistant", avatar="🎓"):

        st.markdown(
            f"{confetti(score)}"
            f"<div style='font-size:22px;font-weight:800;color:#FFFFFF;margin-bottom:4px;'>"
            f"Here's {name}'s Report! 🎓</div>"
            f"<p style='color:#64748B;font-size:13px;margin:0;'>"
            f"Grade {grade} · {', '.join(subjects)} · {datetime.now().strftime('%b %d, %Y')}</p>",
            unsafe_allow_html=True,
        )
        st.markdown("<hr class='neon-divider'>", unsafe_allow_html=True)

        # Score ring + metrics
        ring_col, met_col = st.columns([1, 2])
        with ring_col:
            st.markdown(score_ring_html(score, level), unsafe_allow_html=True)
        with met_col:
            m1, m2 = st.columns(2)
            m3, m4 = st.columns(2)
            for col, (val, lbl) in zip(
                [m1, m2, m3, m4],
                [(f"{correct}/{len(questions)}", "Correct"),
                 (f"{score}%",                  "Overall Score"),
                 (f"Grade {grade}",              "Level"),
                 (str(len(subjects)),            "Subjects")],
            ):
                with col:
                    st.markdown(
                        f'<div class="met-card"><div class="met-val">{val}</div>'
                        f'<div class="met-lbl">{lbl}</div></div>',
                        unsafe_allow_html=True,
                    )

        st.markdown("<div style='height:8px'></div>", unsafe_allow_html=True)

        # Subject scores chart
        if report.get("subject_scores"):
            st.markdown(
                "<div style='font-size:16px;font-weight:700;color:#FFFFFF;margin-bottom:10px;'>"
                "📊 Subject Scores</div>",
                unsafe_allow_html=True,
            )
            st.plotly_chart(subject_chart(report["subject_scores"]), use_container_width=True)

        st.markdown("<hr class='neon-divider'>", unsafe_allow_html=True)

        # Strengths & improvements
        s_col, i_col = st.columns(2)
        with s_col:
            st.markdown(
                "<div style='font-size:15px;font-weight:700;color:#FFFFFF;margin-bottom:10px;'>✅ Strengths</div>",
                unsafe_allow_html=True,
            )
            for s in report.get("strengths", []):
                st.markdown(f'<div class="str-item">💪 {s}</div>', unsafe_allow_html=True)

        with i_col:
            st.markdown(
                "<div style='font-size:15px;font-weight:700;color:#FFFFFF;margin-bottom:10px;'>📌 To Improve</div>",
                unsafe_allow_html=True,
            )
            for imp in report.get("improvements", []):
                st.markdown(f'<div class="imp-item">📖 {imp}</div>', unsafe_allow_html=True)

        st.markdown("<div style='height:4px'></div>", unsafe_allow_html=True)

        # Recommendation
        if report.get("recommendation"):
            st.markdown(f"""
            <div class="rec-box">
              <div style="font-size:13px;font-weight:700;color:#A78BFA;margin-bottom:10px;">
                🎓 Spairo Academy Recommendation
              </div>
              <p>{report["recommendation"]}</p>
            </div>""", unsafe_allow_html=True)

        st.markdown("<div style='height:16px'></div>", unsafe_allow_html=True)

        # Actions
        a1, a2 = st.columns(2)
        with a1:
            if st.button("📋  View History", use_container_width=True):
                st.session_state.show_history = True
                st.rerun()
        with a2:
            if st.button("🔄  New Evaluation", type="primary", use_container_width=True):
                for k, v in _DEFAULTS.items():
                    st.session_state[k] = v
                bot(BOT_INTRO)
                set_state("wait_name")
                st.rerun()


# ══════════════════════════════════════════════════════════════════════════════
#  HISTORY / DASHBOARD  panel
# ══════════════════════════════════════════════════════════════════════════════
def render_history_panel():
    st.markdown("""
    <div style="padding:16px 0 8px;">
      <div style="font-size:20px;font-weight:800;color:#FFFFFF;">📋 Evaluation History</div>
    </div>""", unsafe_allow_html=True)

    # Viewing single past report
    if st.session_state.view_eval_id:
        ev = get_evaluation(st.session_state.view_eval_id)
        if ev:
            _render_past_report(ev)
        if st.button("← Back to History"):
            st.session_state.view_eval_id = None
            st.rerun()
        return

    all_evals = get_all_evaluations()
    if not all_evals:
        st.markdown("""
        <div class="glass-card" style="text-align:center;padding:48px 20px;">
          <div style="font-size:40px;margin-bottom:12px;">📭</div>
          <div style="color:#94A3B8;font-size:16px;font-weight:600;">No evaluations yet</div>
          <div style="color:#475569;font-size:14px;margin-top:6px;">
            Complete a quiz to see results here.
          </div>
        </div>""", unsafe_allow_html=True)
        return

    # Student filter
    names    = get_student_names()
    selected = st.selectbox("Filter by student", ["All Students"] + names)
    filtered = [e for e in all_evals if e["student_name"]==selected] \
               if selected != "All Students" else all_evals

    # Trend chart
    if selected != "All Students" and len(filtered) > 1:
        dates  = [e.get("completed_at_display","")[:12] for e in filtered]
        scores = [e["overall_score"] for e in filtered]
        fig = go.Figure()
        fig.add_trace(go.Scatter(
            x=dates, y=scores, mode="lines+markers",
            line=dict(color="#8B5CF6", width=3),
            marker=dict(color="#06B6D4", size=10, line=dict(color="white",width=2)),
            fill="tozeroy", fillcolor="rgba(139,92,246,0.07)",
        ))
        fig.update_layout(
            paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="white",family="Inter"), height=200,
            margin=dict(l=0,r=0,t=8,b=0),
            yaxis=dict(range=[0,105],showgrid=True,gridcolor="rgba(255,255,255,0.04)",
                       tickfont=dict(color="#94A3B8")),
            xaxis=dict(showgrid=False,tickfont=dict(color="#94A3B8")),
        )
        st.plotly_chart(fig, use_container_width=True)

    # History cards
    st.markdown(
        f"<div style='color:#64748B;font-size:13px;margin-bottom:12px;'>"
        f"{len(filtered)} evaluation{'s' if len(filtered)!=1 else ''}</div>",
        unsafe_allow_html=True,
    )
    for ev in filtered:
        subj_str  = ", ".join(ev["subjects"]) if isinstance(ev.get("subjects"),list) else ""
        date_str  = ev.get("completed_at_display","")[:12]
        lv_html   = level_badge(ev.get("knowledge_level","Proficient"))
        card_c, btn_c = st.columns([5,1])
        with card_c:
            st.markdown(f"""
            <div class="glass-card" style="padding:16px 20px;margin-bottom:6px;">
              <div style="display:flex;align-items:center;gap:10px;flex-wrap:wrap;">
                <span style="font-size:15px;font-weight:700;color:#FFFFFF;">{ev["student_name"]}</span>
                <span style="color:#475569;font-size:13px;">G{ev["grade"]}</span>
                {lv_html}
                <span style="color:#8B5CF6;font-size:17px;font-weight:800;margin-left:auto;">
                  {ev["overall_score"]}%
                </span>
              </div>
              <div style="margin-top:6px;color:#475569;font-size:12px;">{subj_str} · {date_str}</div>
            </div>""", unsafe_allow_html=True)
        with btn_c:
            st.markdown("<div style='margin-top:18px'>", unsafe_allow_html=True)
            if st.button("View", key=f"hv_{ev['id']}"):
                st.session_state.view_eval_id = ev["id"]
                st.rerun()
            st.markdown("</div>", unsafe_allow_html=True)


def _render_past_report(ev: dict):
    score = ev.get("overall_score", 0)
    level = ev.get("knowledge_level", "Proficient")
    name  = ev["student_name"]
    grade = ev["grade"]
    q     = ev.get("questions") or []
    ans   = ev.get("answers") or {}
    subj  = ev.get("subjects") or []
    correct = sum(1 for qq in q if ans.get(str(qq.get("id")))==qq.get("correct_answer"))

    st.markdown(
        f"{confetti(score)}"
        f"<div style='font-size:20px;font-weight:800;color:#FFFFFF;margin-bottom:4px;'>"
        f"Report: {name} · Grade {grade}</div>"
        f"<p style='color:#64748B;font-size:13px;'>{ev.get('completed_at_display','')[:12]}</p>",
        unsafe_allow_html=True,
    )
    r_col, m_col = st.columns([1,2])
    with r_col:
        st.markdown(score_ring_html(score, level), unsafe_allow_html=True)
    with m_col:
        m1,m2 = st.columns(2); m3,m4 = st.columns(2)
        for col,(val,lbl) in zip([m1,m2,m3,m4],[
            (f"{correct}/{len(q)}","Correct"),(f"{score}%","Score"),
            (f"G{grade}","Grade"),(str(len(subj)),"Subjects"),
        ]):
            with col:
                st.markdown(
                    f'<div class="met-card"><div class="met-val">{val}</div>'
                    f'<div class="met-lbl">{lbl}</div></div>',
                    unsafe_allow_html=True,
                )
    ss = ev.get("subject_scores") or {}
    if ss:
        st.plotly_chart(subject_chart(ss), use_container_width=True)
    sc, ic = st.columns(2)
    with sc:
        st.markdown("<div style='font-size:15px;font-weight:700;color:#FFF;margin-bottom:8px;'>✅ Strengths</div>",unsafe_allow_html=True)
        for s in (ev.get("strengths") or []):
            st.markdown(f'<div class="str-item">💪 {s}</div>',unsafe_allow_html=True)
    with ic:
        st.markdown("<div style='font-size:15px;font-weight:700;color:#FFF;margin-bottom:8px;'>📌 To Improve</div>",unsafe_allow_html=True)
        for i in (ev.get("improvements") or []):
            st.markdown(f'<div class="imp-item">📖 {i}</div>',unsafe_allow_html=True)
    if ev.get("recommendation"):
        st.markdown(f'<div class="rec-box"><div style="font-size:13px;font-weight:700;color:#A78BFA;margin-bottom:8px;">🎓 Spairo Academy Recommendation</div><p>{ev["recommendation"]}</p></div>',unsafe_allow_html=True)


# ══════════════════════════════════════════════════════════════════════════════
#  MAIN RENDER
# ══════════════════════════════════════════════════════════════════════════════
render_topbar()

# History panel takes over when open
if st.session_state.show_history:
    render_history_panel()
    st.markdown("<div style='height:20px'></div>", unsafe_allow_html=True)
    if st.button("← Back to Chat", type="primary"):
        st.session_state.show_history = False
        st.session_state.view_eval_id = None
        st.rerun()

else:
    # ── Initialise first message ───────────────────────────────
    if st.session_state.state == "start":
        bot(BOT_INTRO)
        set_state("wait_name")

    # ── Render conversation history ────────────────────────────
    render_history()

    # ── Dispatch current state ─────────────────────────────────
    state = st.session_state.state
    if   state == "wait_name":    handle_wait_name()
    elif state == "wait_grade":   handle_wait_grade()
    elif state == "wait_subjects":handle_wait_subjects()
    elif state == "wait_count":   handle_wait_count()
    elif state == "generating":   handle_generating()
    elif state == "quiz":         handle_quiz()
    elif state == "reporting":    handle_reporting()
    elif state == "results":      handle_results()
