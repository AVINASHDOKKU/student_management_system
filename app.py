import streamlit as st
import pandas as pd
import sqlite3
import os

# Admin credentials
ADMIN_USERNAME = "admin"
ADMIN_PASSWORD = "admin123"

# Database setup
DB_NAME = "instalments.db"

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "CREATE TABLE IF NOT EXISTS instalments ("
        "student_id TEXT, "
        "course TEXT, "
        "instalment_number INTEGER, "
        "amount REAL, "
        "due_date TEXT)"
    )
    conn.commit()
    conn.close()

def save_instalments(student_id, course, df):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM instalments WHERE student_id=? AND course=?", (student_id, course))
    for _, row in df.iterrows():
        cursor.execute("INSERT INTO instalments VALUES (?, ?, ?, ?, ?)",
                       (student_id, course, row['instalment_number'], row['amount'], row['due_date']))
    conn.commit()
    conn.close()

def load_instalments(student_id, course):
    conn = sqlite3.connect(DB_NAME)
    df = pd.read_sql_query("SELECT * FROM instalments WHERE student_id=? AND course=?", conn, params=(student_id, course))
    conn.close()
    return df

def load_course_template(course_file):
    return pd.read_excel(course_file)

def main():
    st.title("Student Instalment Schedule Portal")

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        st.subheader("Admin Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
                st.session_state.logged_in = True
                st.success("Logged in successfully!")
            else:
                st.error("Invalid credentials")
        return

    init_db()

    st.subheader("Instalment Schedule Editor")

    student_id = st.text_input("Student ID")
    course = st.selectbox("Select Course", ["C3CC", "C4KM", "DHM", "GDML"])
    course_file = f"{course}.xlsx"

    if os.path.exists(course_file):
        df_template = load_course_template(course_file)
        st.write("Edit Instalment Schedule:")
        edited_df = st.data_editor(df_template, num_rows="dynamic")
        if st.button("Save Schedule"):
            save_instalments(student_id, course, edited_df)
            st.success("Instalment schedule saved successfully.")
        if st.button("Load Saved Schedule"):
            saved_df = load_instalments(student_id, course)
            st.write("Saved Instalment Schedule:")
            st.dataframe(saved_df)
    else:
        st.error(f"Course template file {course_file} not found.")

if __name__ == "__main__":
    main()
