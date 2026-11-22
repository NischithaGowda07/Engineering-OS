
import streamlit as st
import pandas as pd
from pathlib import Path
from datetime import date

# ---------------- PAGE CONFIG ----------------
st.set_page_config(
    page_title="Engineering Degree OS",
    page_icon="🎓",
    layout="wide"
)

DATA_DIR = Path("data")
DATA_DIR.mkdir(exist_ok=True)

FILES = {
    "semesters": "semesters.csv",
    "courses": "courses.csv",
    "calendar": "academic_calendar.csv",
    "assessments": "assessments.csv",
    "scores": "scores.csv",
    "checklist": "plan_checklist.csv"
}

# ---------------- DATA FUNCTIONS ----------------
def load_data(key):
    path = DATA_DIR / FILES[key]
    if path.exists():
        try:
            return pd.read_csv(path)
        except Exception:
            st.error(f"Could not read {FILES[key]}. Please check the CSV file.")
    return pd.DataFrame()

def save_data(key, dataframe):
    dataframe.to_csv(DATA_DIR / FILES[key], index=False)

semesters = load_data("semesters")
courses = load_data("courses")
calendar = load_data("calendar")
assessments = load_data("assessments")
scores = load_data("scores")
checklist = load_data("checklist")

# ---------------- SIDEBAR ----------------
st.sidebar.title("🎓 Engineering Degree OS")
st.sidebar.caption("Your complete academic companion")

pages = [
    "Dashboard",
    "Semester 1",
    "Semester 2",
    "Semester 3",
    "Semester 4",
    "Semester 5",
    "Semester 6",
    "Semester 7",
    "Semester 8",
    "Courses & Syllabus",
    "University Syllabus",
    "Academic / Leave Calendar",
    "Internal Assessments",
    "Status Tracker",
    "Scorecard",
    "Plan & Checklist",
    "Ask Degree AI",
    "Data Admin"
]

page = st.sidebar.radio("Navigate", pages)

st.sidebar.divider()
st.sidebar.caption("Engineering Degree OS | Local Prototype")

# ---------------- HELPER FUNCTIONS ----------------
def show_table(data):
    if data.empty:
        st.info("No data available yet.")
    else:
        st.dataframe(data, use_container_width=True, hide_index=True)

def upcoming_assessment():
    if assessments.empty or "date" not in assessments.columns:
        return "No assessment added"

    data = assessments.copy()
    data["date"] = pd.to_datetime(data["date"], errors="coerce")
    future = data[data["date"].dt.date >= date.today()]

    if future.empty:
        return "No upcoming assessment"

    item = future.sort_values("date").iloc[0]
    return f"{item.get('assessment_type', 'Assessment')} - {item.get('course_code', '')} ({item['date'].date()})"

def next_holiday():
    if calendar.empty or "date" not in calendar.columns:
        return "No holiday added"

    data = calendar.copy()
    data["date"] = pd.to_datetime(data["date"], errors="coerce")
    if "event_type" not in data.columns:
        return "No holiday added"

    data = data[
        (data["event_type"].astype(str).str.lower() == "holiday")
        & (data["date"].dt.date >= date.today())
    ]

    if data.empty:
        return "No upcoming holiday"

    item = data.sort_values("date").iloc[0]
    return f"{item.get('title', 'Holiday')} ({item['date'].date()})"

# ---------------- DASHBOARD ----------------
if page == "Dashboard":
    st.title("Welcome to Your Engineering Degree OS 👋")
    st.write("Your academic journey, organized in one place.")

    current_semester = 3

    if not semesters.empty and "status" in semesters.columns:
        active = semesters[
            semesters["status"].astype(str).str.lower() == "in progress"
        ]
        if not active.empty:
            current_semester = int(active.iloc[0]["semester"])

    completed_credits = 0
    total_credits = 0

    if not semesters.empty:
        completed_credits = pd.to_numeric(
            semesters.get("completed_credits", pd.Series(dtype=float)),
            errors="coerce"
        ).fillna(0).sum()

        total_credits = pd.to_numeric(
            semesters.get("total_credits", pd.Series(dtype=float)),
            errors="coerce"
        ).fillna(0).sum()

    completion = (
        completed_credits / total_credits * 100
        if total_credits else 0
    )

    col1, col2, col3 = st.columns(3)
    col1.metric("Current Semester", current_semester)
    col2.metric("Credits Completed", f"{completed_credits:.0f}")
    col3.metric("Degree Progress", f"{completion:.1f}%")

    st.progress(min(completion / 100, 1.0))

    st.subheader("📌 Academic Overview")
    col1, col2 = st.columns(2)
    col1.info(f"**Upcoming Assessment**\n\n{upcoming_assessment()}")
    col2.info(f"**Next Holiday**\n\n{next_holiday()}")

    st.subheader("📊 Semester Progress")
    if not semesters.empty and "semester" in semesters.columns:
        chart_data = semesters.set_index("semester")[["completed_credits", "total_credits"]]
        st.bar_chart(chart_data)
    else:
        st.info("Add semester data to display progress.")

    st.subheader("📰 AI World News")
    st.write(
        "AI news is not connected in this prototype. "
        "Add a verified news source in a future version."
    )

# ---------------- SEMESTER 1 TO 8 ----------------
elif page.startswith("Semester "):
    sem_no = int(page.split(" ")[1])
    st.title(f"Semester {sem_no}")

    sem_courses = courses[
        pd.to_numeric(courses["semester"], errors="coerce") == sem_no
    ] if not courses.empty and "semester" in courses.columns else pd.DataFrame()

    st.subheader("Semester Courses")
    show_table(sem_courses)

    if not sem_courses.empty:
        st.metric("Number of Courses", len(sem_courses))
        if "credits" in sem_courses.columns:
            credits = pd.to_numeric(sem_courses["credits"], errors="coerce").fillna(0).sum()
            st.metric("Total Course Credits", int(credits))

# ---------------- COURSES ----------------
elif page == "Courses & Syllabus":
    st.title("📚 Courses & Syllabus")

    if not courses.empty and "semester" in courses.columns:
        semester_list = sorted(
            pd.to_numeric(courses["semester"], errors="coerce")
            .dropna().astype(int).unique().tolist()
        )

        selected = st.selectbox("Select Semester", semester_list)
        filtered = courses[
            pd.to_numeric(courses["semester"], errors="coerce") == selected
        ]
        show_table(filtered)
    else:
        st.info("No course data available.")

# ---------------- UNIVERSITY SYLLABUS ----------------
elif page == "University Syllabus":
    st.title("🏛️ University Syllabus")
    st.write("Store and review your official university syllabus here.")

    st.warning(
        "The current course list contains sample data. "
        "It is not verified against your official university syllabus."
    )

    st.write("You can add official syllabus references in Data Admin.")

# ---------------- CALENDAR ----------------
elif page == "Academic / Leave Calendar":
    st.title("📅 Academic / Leave Calendar")

    if not calendar.empty:
        if "academic_year" in calendar.columns:
            years = calendar["academic_year"].dropna().unique().tolist()
            year = st.selectbox("Academic Year", years)
            calendar = calendar[calendar["academic_year"] == year]

        if "semester" in calendar.columns:
            sems = calendar["semester"].dropna().unique().tolist()
            sem = st.selectbox("Semester", sems)
            calendar = calendar[calendar["semester"] == sem]

        show_table(calendar)
    else:
        st.info("No calendar events available.")

# ---------------- INTERNAL ASSESSMENTS ----------------
elif page == "Internal Assessments":
    st.title("📝 Internal Assessments")
    show_table(assessments)

    if not assessments.empty and "date" in assessments.columns:
        st.subheader("Assessment Timeline")
        timeline = assessments.copy()
        timeline["date"] = pd.to_datetime(timeline["date"], errors="coerce")
        st.dataframe(
            timeline.sort_values("date"),
            use_container_width=True,
            hide_index=True
        )

# ---------------- STATUS TRACKER ----------------
elif page == "Status Tracker":
    st.title("📈 Status Tracker")
    show_table(courses)

    if not courses.empty and "status" in courses.columns:
        st.subheader("Course Status Summary")
        st.bar_chart(courses["status"].value_counts())

# ---------------- SCORECARD ----------------
elif page == "Scorecard":
    st.title("🏆 Scorecard")

    if not scores.empty:
        show_table(scores)

        total_score = pd.to_numeric(scores["score"], errors="coerce").fillna(0).sum()
        total_max = pd.to_numeric(scores["max_marks"], errors="coerce").fillna(0).sum()

        percentage = total_score / total_max * 100 if total_max else 0

        col1, col2, col3 = st.columns(3)
        col1.metric("Total Marks", f"{total_score:.0f}")
        col2.metric("Maximum Marks", f"{total_max:.0f}")
        col3.metric("Score Percentage", f"{percentage:.2f}%")

        st.caption(
            "This is a prototype percentage calculation, not an official CGPA."
        )
    else:
        st.info("No score records available.")

# ---------------- PLAN & CHECKLIST ----------------
elif page == "Plan & Checklist":
    st.title("✅ Plan & Checklist")

    if not checklist.empty:
        edited = st.data_editor(
            checklist,
            use_container_width=True,
            hide_index=True,
            num_rows="dynamic"
        )

        if st.button("Save Checklist"):
            save_data("checklist", edited)
            st.success("Checklist saved successfully!")
            st.rerun()

        if "target_date" in checklist.columns:
            dates = pd.to_datetime(checklist["target_date"], errors="coerce")
            status = checklist.get(
                "status", pd.Series("", index=checklist.index)
            ).astype(str)

            today = pd.Timestamp.today().normalize()
            done = status.str.lower() == "done"
            overdue = (dates < today) & (~done)
            due_soon = (
                (dates >= today)
                & (dates <= today + pd.Timedelta(days=7))
                & (~done)
            )

            col1, col2, col3 = st.columns(3)
            col1.metric("Done", int(done.sum()))
            col2.metric("Due Soon", int(due_soon.sum()))
            col3.metric("Overdue", int(overdue.sum()))
    else:
        st.info("No checklist items available.")

# ---------------- ASK DEGREE AI ----------------
elif page == "Ask Degree AI":
    st.title("🤖 Ask Degree AI")
    st.write("Ask questions about the information stored in your Degree OS.")

    question = st.text_input(
        "Enter your question",
        placeholder="Example: What is my next assessment?"
    )

    if st.button("Ask"):
        q = question.lower().strip()

        if not q:
            st.warning("Please enter a question.")
        elif "assessment" in q and ("next" in q or "upcoming" in q):
            st.info(upcoming_assessment())
        elif "holiday" in q:
            st.info(next_holiday())
        elif "checklist" in q or "pending task" in q:
            if not checklist.empty:
                pending = checklist[
                    checklist["status"].astype(str).str.lower() != "done"
                ]
                show_table(pending)
            else:
                st.info("No checklist data available.")
        elif "course" in q or "syllabus" in q:
            if not courses.empty:
                st.dataframe(courses, use_container_width=True, hide_index=True)
            else:
                st.info("No course data available.")
        elif "semester" in q:
            show_table(semesters)
        else:
            st.warning(
                "I cannot verify that from the current Degree OS data."
            )

# ---------------- DATA ADMIN ----------------
elif page == "Data Admin":
    st.title("⚙️ Data Admin")
    st.write("Edit your academic data and save changes to CSV files.")

    for key, filename in FILES.items():
        st.subheader(filename)
        dataframe = load_data(key)

        if dataframe.empty:
            st.info(f"{filename} is empty or not available.")
            continue

        edited = st.data_editor(
            dataframe,
            use_container_width=True,
            hide_index=True,
            num_rows="dynamic",
            key=f"editor_{key}"
        )

        if st.button(f"Save {filename}", key=f"save_{key}"):
            save_data(key, edited)
            st.success(f"{filename} saved successfully!")
            st.rerun()
