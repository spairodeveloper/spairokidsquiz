"""
ai_engine.py  (gemini_engine.py — kept same filename so app.py imports unchanged)
Spairo Academy — Knowledge Evaluator
AI engine powered by Groq (free tier) — llama-3.3-70b-versatile
Fallback: llama-3.1-70b-versatile → llama-3.1-8b-instant
"""

import json
import time
import streamlit as st
from groq import Groq
from pydantic import BaseModel, ValidationError
from typing import Literal, Dict, List

# ── Configure Groq ────────────────────────────────────────────────────────────
client = Groq(api_key=st.secrets["GROQ_API_KEY"])

# Model fallback chain — tries each in order on rate-limit/error
MODEL_CHAIN = [
    "llama-3.3-70b-versatile",   # best quality, free
    "llama-3.1-70b-versatile",   # fallback quality
    "llama-3.1-8b-instant",      # fastest, lightest
]

# ── Pydantic Models ───────────────────────────────────────────────────────────

class Question(BaseModel):
    id: int
    subject: str
    difficulty: Literal["Easy", "Medium", "Hard"]
    question: str
    choices: Dict[str, str]        # {"A": "...", "B": "...", "C": "...", "D": "..."}
    correct_answer: Literal["A", "B", "C", "D"]
    explanation: str


class QuestionSet(BaseModel):
    questions: List[Question]


class Report(BaseModel):
    overall_score: int
    knowledge_level: Literal[
        "Exceptional", "Advanced", "Proficient", "Developing", "Needs Support"
    ]
    subject_scores: Dict[str, int]
    strengths: List[str]
    improvements: List[str]
    recommendation: str


# ── Prompts ───────────────────────────────────────────────────────────────────

QUESTION_SYSTEM = (
    "You are an expert K-12 educational content creator. "
    "Generate clear, unambiguous, grade-appropriate multiple-choice questions. "
    "IMPORTANT: Return ONLY a valid JSON object. No markdown, no code fences, no extra text."
)

QUESTION_USER = """Generate {count} multiple-choice questions for a Grade {grade} student.
Subjects to cover: {subjects}
Difficulty distribution: 40% Easy, 40% Medium, 20% Hard.
Mix subjects evenly when multiple are selected.

Return exactly this JSON structure:
{{
  "questions": [
    {{
      "id": 1,
      "subject": "Math",
      "difficulty": "Easy",
      "question": "What is 7 x 8?",
      "choices": {{"A": "54", "B": "56", "C": "64", "D": "48"}},
      "correct_answer": "B",
      "explanation": "7 x 8 = 56. A helpful trick: 7 x 7 = 49, then add 7 more to get 56."
    }}
  ]
}}"""

REPORT_SYSTEM = (
    "You are an expert educational psychologist and K-12 academic advisor. "
    "Analyse student quiz performance and return structured insights. "
    "IMPORTANT: Return ONLY a valid JSON object. No markdown, no code fences, no extra text."
)

REPORT_USER = """A Grade {grade} student named {name} just completed a {count}-question quiz.

Quiz results:
{results_json}

Return exactly this JSON structure:
{{
  "overall_score": 75,
  "knowledge_level": "Proficient",
  "subject_scores": {{"Math": 80, "Science": 70}},
  "strengths": [
    "Strong arithmetic skills — answered all basic multiplication correctly"
  ],
  "improvements": [
    "Word problems need more practice — missed 2 of 3 questions"
  ],
  "recommendation": "Personalised 2-3 sentence recommendation for Spairo Academy enrollment."
}}

Rules:
- overall_score: integer 0-100 (percentage correct)
- knowledge_level must be exactly one of: Exceptional (90-100%), Advanced (80-89%), Proficient (60-79%), Developing (40-59%), Needs Support (0-39%)
- subject_scores: integer 0-100 per subject
- strengths: 2-3 specific observations from correct answers
- improvements: 2-4 specific areas from wrong answers
- recommendation: personalised to {name}, references Spairo Academy programs"""


# ── Helpers ───────────────────────────────────────────────────────────────────

def _clean_json(raw: str) -> str:
    """Strip any markdown code fences the model may wrap around JSON."""
    raw = raw.strip()
    # Remove ```json or ``` fences
    if raw.startswith("```"):
        raw = raw.split("\n", 1)[-1]
    if raw.endswith("```"):
        raw = raw.rsplit("```", 1)[0]
    return raw.strip()


def _is_rate_limit(e: Exception) -> bool:
    msg = str(e).lower()
    return any(k in msg for k in ["429", "rate", "quota", "limit", "overloaded"])


def _call_groq(system: str, user: str, max_tokens: int = 2500) -> str:
    """
    Call Groq API across the model fallback chain.
    Returns raw text. Raises RuntimeError if all models fail.
    """
    last_error = None
    for model_name in MODEL_CHAIN:
        try:
            response = client.chat.completions.create(
                model=model_name,
                messages=[
                    {"role": "system", "content": system},
                    {"role": "user",   "content": user},
                ],
                temperature=0.4,       # lower = more consistent JSON
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content

        except Exception as e:
            last_error = e
            if _is_rate_limit(e):
                time.sleep(2)          # brief pause before next model
                continue               # try next model
            # Non-rate error: retry once then move on
            time.sleep(1)
            try:
                response = client.chat.completions.create(
                    model=model_name,
                    messages=[
                        {"role": "system", "content": system},
                        {"role": "user",   "content": user},
                    ],
                    temperature=0.4,
                    max_tokens=max_tokens,
                )
                return response.choices[0].message.content
            except Exception as e2:
                last_error = e2
                continue

    raise RuntimeError(
        f"All Groq models failed. Last error: {last_error}\n"
        "Check your GROQ_API_KEY at console.groq.com"
    )


# ── Question Generation ───────────────────────────────────────────────────────

def generate_questions(
    grade: int,
    subjects: List[str],
    count: int,
    retries: int = 2,
) -> QuestionSet:
    """
    Generate quiz questions using Groq.
    Returns a validated QuestionSet. Raises RuntimeError on failure.
    """
    user_prompt = QUESTION_USER.format(
        grade=grade,
        subjects=", ".join(subjects),
        count=count,
    )

    last_error = None
    for attempt in range(1, retries + 1):
        try:
            raw  = _call_groq(QUESTION_SYSTEM, user_prompt, max_tokens=3000)
            raw  = _clean_json(raw)
            data = json.loads(raw)
            qset = QuestionSet(**data)

            # Trim extras or raise if too few
            if len(qset.questions) > count:
                qset.questions = qset.questions[:count]
            elif len(qset.questions) < count:
                raise ValueError(
                    f"Expected {count} questions, got {len(qset.questions)}"
                )
            return qset

        except RuntimeError:
            raise   # propagate API-level errors immediately
        except (json.JSONDecodeError, ValidationError, ValueError) as e:
            last_error = e
            if attempt < retries:
                time.sleep(1)

    raise RuntimeError(
        f"Question generation failed after {retries} attempts. "
        f"Last error: {last_error}"
    )


# ── Report Analysis ───────────────────────────────────────────────────────────

def generate_report(
    name: str,
    grade: int,
    count: int,
    questions: List[Question],
    answers: Dict[int, str],
    retries: int = 2,
) -> Report:
    """
    Analyse quiz results and generate a report using Groq.
    Returns a validated Report. Raises RuntimeError on failure.
    """
    results = [
        {
            "question_id":   q.id,
            "subject":       q.subject,
            "difficulty":    q.difficulty,
            "question":      q.question,
            "student_answer": answers.get(str(q.id), ""),
            "correct_answer": q.correct_answer,
            "is_correct":    answers.get(str(q.id)) == q.correct_answer,
        }
        for q in questions
    ]

    user_prompt = REPORT_USER.format(
        name=name,
        grade=grade,
        count=count,
        results_json=json.dumps(results, indent=2),
    )

    last_error = None
    for attempt in range(1, retries + 1):
        try:
            raw    = _call_groq(REPORT_SYSTEM, user_prompt, max_tokens=1500)
            raw    = _clean_json(raw)
            data   = json.loads(raw)
            report = Report(**data)
            return report

        except RuntimeError:
            raise
        except (json.JSONDecodeError, ValidationError) as e:
            last_error = e
            if attempt < retries:
                time.sleep(1)

    raise RuntimeError(
        f"Report generation failed after {retries} attempts. "
        f"Last error: {last_error}"
    )


# ── Local Utilities (no API) ──────────────────────────────────────────────────

def calculate_score(questions: List[Question], answers: Dict[int, str]) -> int:
    """Calculate percentage score. Used as a sanity check."""
    if not questions:
        return 0
    correct = sum(1 for q in questions if answers.get(str(q.id)) == q.correct_answer)
    return round((correct / len(questions)) * 100)


def get_knowledge_level(score: int) -> str:
    if score >= 90: return "Exceptional"
    if score >= 80: return "Advanced"
    if score >= 60: return "Proficient"
    if score >= 40: return "Developing"
    return "Needs Support"
