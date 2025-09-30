import streamlit as st
from utils import login_user

st.set_page_config(page_title="LabReactifs", page_icon="🔬")

st.title("🔑 Connexion LabReactifs")

if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "username" not in st.session_state:
    st.session_state.username = ""

if not st.session_state.logged_in:
    with st.form("login_form"):
        username = st.text_input("Nom d'utilisateur")
        password = st.text_input("Mot de passe", type="password")
        submitted = st.form_submit_button("Se connecter")

    if submitted:
        if not username or not password:
            st.error("Veuillez entrer un nom d'utilisateur et un mot de passe.")
        else:
            user = login_user(username, password)
            if user:
                st.session_state.logged_in = True
                st.session_state.username = user["username"]
                st.success(f"Bienvenue, {user['username']} ! 🎉")
            else:
                st.error("Nom d'utilisateur ou mot de passe incorrect.")
else:
    st.success(f"Bienvenue, {st.session_state.username} ! 🎉")
    st.write("🔬 Accès aux fonctionnalités de LabReactifs")
    
    if st.button("Se déconnecter"):
        st.session_state.logged_in = False
        st.session_state.username = ""
        st.experimental_rerun()
