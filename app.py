import streamlit as st
import openai
import datetime
import pandas as pd
import numpy as np

# --- THEME OVERRIDE (blue-black) ---
st.markdown("""
    <style>
        .stApp {
            background: linear-gradient(135deg, #0d1b2a 0%, #1b263b 100%);
            color: #f8f9fa;
        }
        .css-10trblm, .st-bb {
            color: #f8f9fa !important;
        }
        .css-1d391kg {background: rgba(36, 57, 94, 0.66) !important;}
        .css-1l02zno {background: rgba(15,34,54,0.65) !important;}
        .css-1r6slb0 {background: #1b263b !important;}
        .stButton > button {
            background: linear-gradient(90deg, #2574fc 14%, #4950f6 84%);
            color: #fff !important;
            border: none !important;
        }
        .stButton > button:active {background: #385898 !important;}
        .st-bx {background: #11203a !important;}
        .st-bb {color: #a2b6cd !important;}
        .css-1b3q5p3 {color: #f8f9fa;}
        .stTabs [data-baseweb="tab-list"] {background-color: #192642;}
        .stTabs [data-baseweb="tab"] {color: #d6e6ff;}
        .stTabs [aria-selected="true"] {background: #1e3356; color: #fff;}
        .block-container {padding-top: 2rem; padding-bottom: 2rem;}
    </style>""", unsafe_allow_html=True)

# --- SAMPLE DATA ---
now = datetime.datetime.now()
SAMPLE_TASKS = [
    {"id": 1, "title": "Finish Math HW", "subject": "Mathematics", "due_date": now.date(), "status": "in_progress", "estimated_duration": 45, "priority": "urgent"},
    {"id": 2, "title": "Biology Revision", "subject": "Biology", "due_date": now.date(), "status": "completed", "estimated_duration": 60, "priority": "high"},
    {"id": 3, "title": "Read English Novel", "subject": "English", "due_date": now.date() + datetime.timedelta(days=1), "status": "in_progress", "estimated_duration": 30, "priority": "medium"},
]
SAMPLE_EXAMS = [
    {"id": 1, "subject": "Mathematics", "exam_name": "Final Exam", "exam_date": now.date() + datetime.timedelta(days=8)},
    {"id": 2, "subject": "Physics", "exam_name": "Quiz 2", "exam_date": now.date() + datetime.timedelta(days=16)},
]
SAMPLE_MOOD = [{"date": now.date(), "mood_score": 7}]
SAMPLE_FLASHCARDS = [
    {"front": "What is Newton's 1st Law?", "back": "An object in motion stays in motion...", "subject": "Physics", "deck_name": "Physics Basics", "difficulty": "medium", "review_count": 3, "success_count": 2},
    {"front": "Define photosynthesis.", "back": "Process by which green plants convert...", "subject": "Biology", "deck_name": "Bio", "difficulty": "easy", "review_count": 3, "success_count": 3},
]

# --- SIDEBAR NAVIGATION ---
st.sidebar.image("https://i.imgur.com/Bq4WVIs.png", width=76)  # optional logo
page = st.sidebar.radio("Go To", ["Dashboard", "AI Chatbot", "Planner", "Flashcards", "Exam Countdown", "Mood Tracker", "Study Groups"], index=0)

# --- DASHBOARD PAGE ---
if page == "Dashboard":
    st.markdown("<h2>Welcome back!</h2><p>Here's your study overview for today.</p>", unsafe_allow_html=True)
    col1, col2, col3, col4 = st.columns(4)

    # Weekly stats
    week_start = now.date() - datetime.timedelta(days=now.weekday())
    sessions_this_week = [{"duration_minutes": 90, "productivity_rating": 4}]  # Sample, add real data logic
    total_minutes = sum(s["duration_minutes"] for s in sessions_this_week)
    session_count = len(sessions_this_week)
    avg_productivity = np.mean([s["productivity_rating"] for s in sessions_this_week]) if sessions_this_week else 0

    col1.metric("Hours this week", f"{total_minutes//60}h {total_minutes%60}m", f"{session_count} sessions")
    col2.metric("Productivity", f"{avg_productivity:.1f}/5", "Average")
    next_exam = min(SAMPLE_EXAMS, key=lambda x: x["exam_date"], default=None)
    days_until = (next_exam["exam_date"] - now.date()).days if next_exam else "-"
    col3.metric("Next Exam", f"{days_until} days" if next_exam else "-", next_exam["subject"] if next_exam else "")
    recent_mood = SAMPLE_MOOD[0]["mood_score"] if SAMPLE_MOOD else "-"
    col4.metric("Mood", f"{recent_mood}/10", "Today")

    # Tasks today
    st.subheader("Today's Tasks")
    tasks_today = [t for t in SAMPLE_TASKS if t["due_date"] == now.date() and t["status"] != "completed"]
    if not tasks_today:
        st.success("No tasks due today! 🎉")
    else:
        for t in tasks_today:
            st.write(f"• **{t['title']}** ({t['subject']}) - {t['estimated_duration']}m")

    # Upcoming exams
    st.subheader("Upcoming Exams")
    for exam in SAMPLE_EXAMS:
        days = (exam["exam_date"] - now.date()).days
        st.info(f"{exam['subject']} - {exam['exam_name']} ({exam['exam_date']}) | **{days}d left**")

    # Quick stats
    st.subheader("Study Progress")
    completed = len([t for t in SAMPLE_TASKS if t["status"] == "completed"])
    in_progress = len([t for t in SAMPLE_TASKS if t["status"] == "in_progress"])
    st.write(f"Total Flashcards: {len(SAMPLE_FLASHCARDS)}, Completed Tasks: {completed}, Study Sessions: {session_count}")

# --- AI CHATBOT PAGE ---
elif page == "AI Chatbot":
    st.markdown("<h2>AI Study Assistant</h2><p>Get instant help with your studies</p>", unsafe_allow_html=True)
    openai_api_key = st.secrets["openai_key"] if "openai_key" in st.secrets else st.text_input("OpenAI API Key", type="password")
    if openai_api_key:
        history = st.session_state.get("chat_history", [])
        if history == []:
            history = [{"role": "assistant", "content": "Hi! I'm your AI study assistant. What would you like to study today?"}]
        for msg in history:
            st.chat_message(msg["role"]).write(msg["content"])
        user_input = st.chat_input("Ask me anything about your studies...")
        if user_input:
            with st.spinner("Thinking..."):
                openai.api_key = openai_api_key
                history.append({"role": "user", "content": user_input})
                completion = openai.ChatCompletion.create(model="gpt-3.5-turbo", messages=history)
                reply = completion.choices[0].message.content
                history.append({"role": "assistant", "content": reply})
                st.session_state["chat_history"] = history
                st.experimental_rerun()
    else:
        st.info("Enter your OpenAI API key above to use the AI chatbot.")

# --- PLANNER PAGE ---
elif page == "Planner":
    st.markdown("<h2>Study Planner</h2><p>Organize your tasks and assignments</p>", unsafe_allow_html=True)
    view = st.radio("View", ["Today", "This Week", "All Tasks"], horizontal=True)
    if view == "Today":
        today_tasks = [t for t in SAMPLE_TASKS if t["due_date"] == now.date()]
        df = pd.DataFrame(today_tasks)
        st.write(df if not df.empty else "No tasks for today!")
    elif view == "This Week":
        week_start = now.date() - datetime.timedelta(days=now.weekday())
        week_end = week_start + datetime.timedelta(days=6)
        week_tasks = [t for t in SAMPLE_TASKS if week_start <= t["due_date"] <= week_end]
        st.write(pd.DataFrame(week_tasks) if week_tasks else "No tasks this week!")
    else:
        st.write(pd.DataFrame(SAMPLE_TASKS))

# --- FLASHCARDS PAGE ---
elif page == "Flashcards":
    st.markdown("<h2>Flashcards</h2><p>Review and test yourself with flashcards</p>", unsafe_allow_html=True)
    deck_names = list({f["deck_name"] for f in SAMPLE_FLASHCARDS})
    deck = st.selectbox("Select a deck", deck_names)
    deck_cards = [f for f in SAMPLE_FLASHCARDS if f["deck_name"] == deck]
    if deck_cards:
        idx = st.number_input("Card Index", min_value=0, max_value=len(deck_cards)-1, step=1)
        st.info(deck_cards[int(idx)]["front"])
        if st.button("Show Answer"):
            st.success(deck_cards[int(idx)]["back"])
    st.write(f"Total cards: {len(deck_cards)}")

# --- EXAM COUNTDOWN PAGE ---
elif page == "Exam Countdown":
    st.markdown("<h2>Exam Countdown</h2><p>See days remaining for each upcoming exam</p>", unsafe_allow_html=True)
    for exam in SAMPLE_EXAMS:
        days_left = (exam["exam_date"] - now.date()).days
        st.write(f"**{exam['subject']} {exam['exam_name']}** - {exam['exam_date']} ({days_left} days left)")

# --- MOOD TRACKER PAGE ---
elif page == "Mood Tracker":
    st.markdown("<h2>Mood Tracker</h2><p>Track your daily study mood</p>", unsafe_allow_html=True)
    today = now.date()
    mood_today = next((m for m in SAMPLE_MOOD if m["date"] == today), None)
    mood_score = st.slider("How do you feel today (0-10)?", 0, 10, mood_today["mood_score"] if mood_today else 7)
    if st.button("Save Mood"):
        SAMPLE_MOOD.append({"date": today, "mood_score": mood_score})
        st.success("Saved!")
    st.line_chart(pd.DataFrame(
        {"mood": [m["mood_score"] for m in SAMPLE_MOOD]},
        index=[m["date"] for m in SAMPLE_MOOD]
    ))

# --- STUDY GROUPS PAGE (Placeholder) ---
elif page == "Study Groups":
    st.markdown("<h2>Study Groups</h2><p>Find and join a group study session</p>", unsafe_allow_html=True)
    st.info("Study group features coming soon!")

# STUDENT_DASHBOARD
