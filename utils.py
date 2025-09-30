import os
import psycopg2
import streamlit as st

def get_conn():
    dsn = os.getenv("DATABASE_URL") or st.secrets.get("DATABASE_URL")
    if not dsn:
        raise ValueError("❌ DATABASE_URL non défini. Configure-le dans Streamlit Secrets.")

    # Forcer le bon format
    if dsn.startswith("postgres://"):
        dsn = dsn.replace("postgres://", "postgresql://", 1)

    # Supabase nécessite SSL
    if "sslmode" not in dsn:
        dsn += "?sslmode=require"

    return psycopg2.connect(dsn)

def init_db():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL
        );
    """)
    conn.commit()
    cur.close()
    conn.close()

def login_user(username, password):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
    user = cur.fetchone()
    cur.close()
    conn.close()
    return user

def add_user(username, password):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("INSERT INTO users (username, password) VALUES (%s, %s) ON CONFLICT DO NOTHING", (username, password))
    conn.commit()
    cur.close()
    conn.close()