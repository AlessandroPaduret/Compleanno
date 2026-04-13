import streamlit as st

utente_corrente = "Andrea"  # Simuliamo che l'utente corrente sia Andrea

import streamlit as st

# Funzione per nascondere l'interfaccia di default di Streamlit
def hide_streamlit_style():
    st.markdown("""
        <style>
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}
        [data-testid="stStatusWidget"] {visibility: hidden;}
        .stDeployButton {display:none;}
        </style>
        """, unsafe_allow_html=True)
    
st.set_page_config(
    page_title="Jack di Cuori",
    page_icon="🃏",
    layout="centered", # Mantiene tutto in colonna, perfetto per il telefono
    initial_sidebar_state="collapsed",
)

hide_streamlit_style()

# I semi reali salvati nel database del Master
semi_reali = {
    "Andrea": "❤️ Cuori",
    "Beatrice": "♠️ Picche",
    "Carlo": "♦️ Quadri"
}

st.title("🃏 Alice in Birthday: Prison Cell")

st.info("Nota: Puoi modificare i semi qui sotto per confondere gli altri o prendere appunti.")

for nome, seme_vero in semi_reali.items():
    # Se il giocatore visualizzato è l'utente stesso, mostra sempre ?
    if nome == utente_corrente:
        st.write(f"👤 **TU:** ❓ (Chiedi agli altri!)")
        st.selectbox(
            f"Seme di {nome}",
            options=["","❤️ Cuori", "♦️ Quadri", "♣️ Fiori", "♠️ Picche"],
            key=f"custom_{nome}" # Questo salva la scelta solo per questa sessione
        )
    else:
        # Menu a tendina pre-compilato col seme vero, ma modificabile
        st.selectbox(
            f"Seme di {nome}",
            options=["❤️ Cuori", "♦️ Quadri", "♣️ Fiori", "♠️ Picche"],
            index=["❤️ Cuori", "♦️ Quadri", "♣️ Fiori", "♠️ Picche"].index(seme_vero),
            key=f"custom_{nome}" # Questo salva la scelta solo per questa sessione
        )