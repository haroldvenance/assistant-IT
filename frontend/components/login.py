import streamlit as st
from api import api_post

def login_page():
    st.title("Assistant IT - Connexion")

    tab1, tab2 = st.tabs(["Connexion", "Inscription"])

    with tab1:
        st.subheader("Compte existant")
        username = st.text_input("Nom d'utilisateur", key="login_user")
        password = st.text_input("Mot de passe", type="password", key="login_pass")
        if st.button("Connexion"):
            if not username or not password:
                st.error("Veuillez entrer un nom d'utilisateur et un mot de passe.")
                return
            data = {"username": username, "password": password}
            result = api_post("/login", data=data)
            if result:
                st.session_state.token = result["access_token"]
                st.session_state.username = username
                st.session_state.role = result.get("role", "user")
                st.rerun()

    with tab2:
        st.subheader("Créer un compte")
        new_user = st.text_input("Choisissez un nom d'utilisateur", key="reg_user")
        new_pass = st.text_input("Choisissez un mot de passe", type="password", key="reg_pass")
        new_pass_confirm = st.text_input("Confirmez le mot de passe", type="password", key="reg_pass_confirm")
        if st.button("Créer un compte"):
            if not new_user or not new_pass:
                st.error("Tous les champs sont obligatoires.")
                return
            if new_pass != new_pass_confirm:
                st.error("Les mots de passe ne correspondent pas.")
                return
            result = api_post("/register", json={"username": new_user, "password": new_pass})
            if result:
                st.success("Compte créé avec succès. Vous pouvez maintenant vous connecter.")