import streamlit as st
import pandas as pd
import sqlite3
import os

DB_FILE = "instalments.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS instalments (
            student_id TEXT,
            course TEXT,
            instalment_number INTEGER,
            amount REAL,
            due_date TEXT
        );
    """)
    conn.commit()
    conn.close()

def save_instalments(student_id, course, df):
    conn = sqlite3.connect(DB_FILE)
    df["student_id"] = student_id
    df["course"] = course
    df.to_sql("instalments", conn, if_exists="append", index=False)
    conn.close()

def load_instalments(student_id, course):
    conn = sqlite3.connect(DB_FILE)
    query = "SELECT instalment_number, amount, due_date FROM instalments WHERE student_id=? AND course=?"
    df = pd.read_sql(query, conn, params=(student_id, course))
    conn.close()
    return df

def load_course_template(course):
    filename = f"{course}.xlsx"
    if os.path.exists(filename):
        return pd.read_excel(filename, engine="openpyxl")
    else:
        return pd.DataFrame(columns=["instalment_number", "amount", "due_date"])

def main():
    st.title("Student Instalment Management")

    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        st.subheader("Admin Login")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")
        if st.button("Login"):
            if username == "admin" and password == "admin123":
                st.session_state.logged_in = True
            else:
                st.error("Invalid credentials")
        return

    st.subheader("Instalment Schedule Editor")
    student_id = st.text_input("Student ID")
    course = st.selectbox("Course", ["C3CC", "C4KM", "DHM", "GDML"])

    if st.button("Load Template"):
        df = load_course_template(course)
        st.session_state.instalment_df = df

    if st.button("Load Existing"):
        df = load_instalments(student_id, course)
        st.session_state.instalment_df = df

    if "instalment_df" in st.session_state:
        edited_df = st.data_editor(st.session_state.instalment_df, num_rows="dynamic")
        if st.button("Save Instalments"):
            save_instalments(student_id, course, edited_df)
            st.success("Instalments saved successfully.")

if __name__ == "__main__":
    init_db()
    main()
