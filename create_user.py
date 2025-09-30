import psycopg2
from psycopg2.extras import RealDictCursor
import bcrypt
import getpass

DATABASE_URL = "postgresql://USERNAME:PASSWORD@HOST:PORT/DATABASE_NAME"

def get_conn():
    return psycopg2.connect(DATABASE_URL, cursor_factory=RealDictCursor)

def create_user(username, password):
    password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')
    conn = get_conn()
    cur = conn.cursor()
    try:
        cur.execute(
            "INSERT INTO users (username, password_hash) VALUES (%s, %s)",
            (username, password_hash)
        )
        conn.commit()
        print(f"✅ Utilisateur '{username}' créé avec succès !")
    except Exception as e:
        print("❌ Erreur lors de la création de l'utilisateur :", e)
    finally:
        cur.close()
        conn.close()

if __name__ == "__main__":
    print("Création d'un nouvel utilisateur")
    username = input("Nom d'utilisateur : ").strip()
    password = getpass.getpass("Mot de passe : ").strip()
    password_confirm = getpass.getpass("Confirmer le mot de passe : ").strip()

    if password != password_confirm:
        print("❌ Les mots de passe ne correspondent pas.")
    else:
        create_user(username, password)
