import streamlit as st
import requests
from api import api_get, api_post, api_put, api_delete
from config import MODEL_CHOICES, EXPORT_FORMATS, API_BASE_URL

def render_sidebar(headers: dict):
    with st.sidebar:
        st.subheader("Modèle")
        model_label = st.selectbox("Sélectionner un modèle", list(MODEL_CHOICES.keys()))
        st.session_state.model = MODEL_CHOICES[model_label]

        st.subheader("Conversations")
        search_term = st.text_input("Rechercher", placeholder="Filtrer les conversations...")

        conversations = api_get("/conversations", headers=headers)
        if conversations is None:
            conversations = []

        if search_term:
            conversations = [
                c for c in conversations
                if search_term.lower() in (c.get("title") or "").lower()
            ]

        if st.button("Nouvelle conversation"):
            result = api_post("/conversations", json={"title": "Nouvelle conversation"}, headers=headers)
            if result:
                st.session_state.current_conv_id = result["id"]
                st.rerun()

        for conv in conversations:
            col1, col2, col3 = st.columns([3, 1, 1])
            with col1:
                label = conv["title"][:30] if conv["title"] else "Sans titre"
                if st.button(label, key=f"conv_{conv['id']}"):
                    st.session_state.current_conv_id = conv["id"]
                    st.rerun()
            with col2:
                if st.button("✎", key=f"rename_{conv['id']}"):
                    st.session_state.rename_conv_id = conv["id"]
                    st.session_state.rename_title = conv["title"]
            with col3:
                if st.button("✕", key=f"del_{conv['id']}"):
                    if api_delete(f"/conversations/{conv['id']}", headers=headers):
                        if st.session_state.get("current_conv_id") == conv["id"]:
                            del st.session_state.current_conv_id
                        st.rerun()

        if "rename_conv_id" in st.session_state:
            st.text_input("Nouveau titre", value=st.session_state.rename_title, key="rename_input")
            col_save, col_cancel = st.columns(2)
            with col_save:
                if st.button("Sauvegarder"):
                    new_title = st.session_state.rename_input
                    if new_title:
                        api_put(f"/conversations/{st.session_state.rename_conv_id}",
                                json={"title": new_title}, headers=headers)
                        del st.session_state.rename_conv_id
                        del st.session_state.rename_title
                        if "rename_input" in st.session_state:
                            del st.session_state.rename_input
                        st.rerun()
            with col_cancel:
                if st.button("Annuler"):
                    del st.session_state.rename_conv_id
                    del st.session_state.rename_title
                    if "rename_input" in st.session_state:
                        del st.session_state.rename_input
                    st.rerun()

        if st.session_state.get("current_conv_id"):
            st.subheader("Export")
            export_format = st.selectbox("Format", EXPORT_FORMATS)
            if st.button("Télécharger la conversation"):
                headers_export = headers.copy()
                url = f"{API_BASE_URL}/conversations/{st.session_state.current_conv_id}/export?format={export_format}"
                try:
                    resp = requests.get(url, headers=headers_export, stream=True)
                    resp.raise_for_status()
                    mime_map = {
                        "markdown": "text/markdown",
                        "html": "text/html",
                        "pdf": "application/pdf"
                    }
                    st.download_button(
                        label="Cliquer pour télécharger",
                        data=resp.content,
                        file_name=f"conversation_{st.session_state.current_conv_id}.{export_format}",
                        mime=mime_map.get(export_format, "application/octet-stream")
                    )
                except Exception:
                    st.error("L'export a échoué.")

        st.markdown("---")
        if st.button("Déconnexion"):
            for key in ["token", "username", "role", "current_conv_id", "model"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()