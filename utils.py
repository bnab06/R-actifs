import psycopg2
import streamlit as st
import os
from datetime import datetime, timedelta
import bcrypt

# -------------------------
# Connexion PostgreSQL (Supabase)
# -------------------------
def get_conn():
    dsn = st.secrets.get("DATABASE_URL", None) or os.getenv("DATABASE_URL")
    if not dsn:
        raise ValueError("❌ DATABASE_URL non défini. Configure-le dans Streamlit Secrets.")

    # 🔑 Forcer SSL si absent
    if "sslmode" not in dsn:
        if "?" in dsn:
            dsn += "&sslmode=require"
        else:
            dsn += "?sslmode=require"

    try:
        return psycopg2.connect(dsn)
    except Exception as e:
        raise RuntimeError(f"🚨 Erreur de connexion PostgreSQL : {e}")


# -------------------------
# Initialisation tables
# -------------------------
def init_db():
    conn = get_conn()
    cur = conn.cursor()

    # Table des utilisateurs
    cur.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id SERIAL PRIMARY KEY,
            username TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            role TEXT NOT NULL DEFAULT 'user',
            last_password_change TIMESTAMP NOT NULL
        )
    """)

    # Table des réactifs
    cur.execute("""
        CREATE TABLE IF NOT EXISTS reactifs (
            id SERIAL PRIMARY KEY,
            code_unique TEXT UNIQUE NOT NULL,
            nom TEXT NOT NULL,
            lot TEXT NOT NULL,
            fournisseur TEXT,
            date_reception DATE,
            date_peremption DATE,
            emplacement TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    conn.commit()
    cur.close()
    conn.close()


# -------------------------
# Gestion utilisateurs
# -------------------------
def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()

def check_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode(), hashed.encode())

def create_user(username, password, role="user"):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO users (username, password_hash, role, last_password_change) VALUES (%s, %s, %s, %s) ON CONFLICT (username) DO NOTHING",
        (username, hash_password(password), role, datetime.utcnow())
    )
    conn.commit()
    cur.close()
    conn.close()

def login_user(username, password):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, username, password_hash, role, last_password_change FROM users WHERE username = %s", (username,))
    user = cur.fetchone()
    cur.close()
    conn.close()

    if user and check_password(password, user[2]):
        return {
            "id": user[0],
            "username": user[1],
            "role": user[3],
            "last_password_change": user[4]
        }
    return None

def password_expiry_status(last_change, validity_days=90, alert_days=10):
    expiry_date = last_change + timedelta(days=validity_days)
    now = datetime.utcnow()

    if now >= expiry_date:
        return "expired", expiry_date
    elif now >= expiry_date - timedelta(days=1):
        return "urgent", expiry_date
    elif now >= expiry_date - timedelta(days=alert_days):
        return "soon", expiry_date
    else:
        return "valid", expiry_date


# -------------------------
# Gestion réactifs
# -------------------------
def add_reactif(code_unique, nom, lot, fournisseur, date_reception, date_peremption, emplacement):
    conn = get_conn()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO reactifs (code_unique, nom, lot, fournisseur, date_reception, date_peremption, emplacement)
           VALUES (%s, %s, %s, %s, %s, %s, %s)""",
        (code_unique, nom, lot, fournisseur, date_reception, date_peremption, emplacement)
    )
    conn.commit()
    cur.close()
    conn.close()

def get_reactifs():
    conn = get_conn()
    cur = conn.cursor()
    cur.execute("SELECT id, code_unique, nom, lot, fournisseur, date_reception, date_peremption, emplacement FROM reactifs ORDER BY created_at DESC")
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows

def search_reactifs(keyword):
    conn = get_conn()
    cur = conn.cursor()
    like_kw = f"%{keyword}%"
    cur.execute("""
        SELECT id, code_unique, nom, lot, fournisseur, date_reception, date_peremption, emplacement
        FROM reactifs
        WHERE code_unique ILIKE %s OR lot ILIKE %s OR nom ILIKE %s OR emplacement ILIKE %s
        ORDER BY created_at DESC
    """, (like_kw, like_kw, like_kw, like_kw))
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return rows