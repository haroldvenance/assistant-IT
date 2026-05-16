import streamlit as st
from api import api_get, api_post_stream, api_post

def render_chat(headers: dict):
    if "current_conv_id" not in st.session_state or st.session_state.current_conv_id is None:
        st.info("Sélectionnez ou créez une conversation dans la barre latérale pour commencer.")
        return

    conv_id = st.session_state.current_conv_id

    messages = api_get(f"/conversations/{conv_id}/messages", headers=headers)
    if messages is None:
        return

    for msg in messages:
        with st.chat_message(msg["role"]):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Décrivez votre problème..."):
        with st.chat_message("user"):
            st.markdown(prompt)

        with st.chat_message("assistant"):
            placeholder = st.empty()
            full_response = ""
            tokens = []

            for token in api_post_stream(
                "/chat/stream",
                json_data={
                    "conversation_id": conv_id,
                    "message": prompt,
                    "model": st.session_state.model
                },
                headers=headers
            ):
                tokens.append(token)
                full_response += token
                placeholder.markdown(full_response)

            if len(tokens) == 0:
                st.warning("Aucun token reçu en streaming. Tentative de secours...")
                result = api_post("/chat", json={
                    "conversation_id": conv_id,
                    "message": prompt,
                    "model": st.session_state.model
                }, headers=headers)
                if result and "response" in result:
                    full_response = result["response"]
                    placeholder.markdown(full_response)
                    st.caption("Réponse reçue via le mode secours.")
                else:
                    st.error("Aucune réponse du backend. Vérifiez les logs.")

        st.rerun()