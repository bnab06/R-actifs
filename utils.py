import streamlit as st
import psycopg2
from psycopg2.extras import RealDictCursor
import bcrypt

def get_conn():
    database_url = st.secrets.get("DATABASE_URL")
    if not database_url:
        raise ValueError("❌ DATABASE_URL non défini. Configure-le dans Streamlit Secrets.")
    return psycopg2.connect(database_url, cursor_factory=RealDictCursor)

def login_user(username, password):
    conn = get_conn()
    cur = conn.cursor()
    query = "SELECT * FROM users WHERE username=%s"
    cur.execute(query, (username,))
    user = cur.fetchone()
    cur.close()
    conn.close()

    if user:
        password_hash = user["password_hash"]
        if bcrypt.checkpw(password.encode('utf-8'), password_hash.encode('utf-8')):
            return user
    return None
