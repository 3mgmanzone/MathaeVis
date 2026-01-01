import streamlit as st
import random
import time
from fpdf import FPDF
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime

import io

# Configurazione Pagina
st.set_page_config(page_title="Mathae Vis", layout="wide")

# CSS personalizzato per font e spaziature
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Helvetica:wght@400;700&display=swap');
    html, body, [class*="css"] { font-family: 'Helvetica', sans-serif; }
    .title { color: blue; font-size: 32px; font-weight: bold; text-align: center; margin-bottom: 32px; }
    .metrics { color: green; font-size: 24px; text-align: center; margin-top: 24px; }
    .exercise { color: black; font-size: 24px; font-weight: bold; text-align: center; margin-top: 24px; }
    .feedback-ok { color: green; font-size: 24px; font-weight: bold; text-align: center; margin-top: 24px; }
    .feedback-ko { color: red; font-size: 24px; font-weight: bold; text-align: center; margin-top: 24px; }
    div[data-baseweb="input"] { border: 1px solid black !important; }
    </style>
    """, unsafe_allow_html=True)

# Inizializzazione Session State
if 'history' not in st.session_state:
    st.session_state.history = []
    st.session_state.start_time = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    st.session_state.current_exercise = None
    st.session_state.exercise_start_time = None
    st.session_state.feedback = None
    st.session_state.input_key = 0

def generate_exercise():
    tipo = random.randint(1, 5)
    if tipo == 1: # Somma
        a, b = random.randint(1, 99), random.randint(1, 99)
        return {"q": f"{a} + {b}", "a": a + b}
    elif tipo == 2: # Sottrazione
        a = random.randint(2, 99)
        b = random.randint(1, a - 1)
        return {"q": f"{a} - {b}", "a": a - b}
    elif tipo == 3: # Moltiplicazione
        a, b = random.randint(1, 9), random.randint(1, 99)
        return {"q": f"{a} x {b}", "a": a * b}
    elif tipo == 4: # Radice
        root = random.randint(1, 60)
        return {"q": f"radq( {root**2} )", "a": root}
    elif tipo == 5: # Divisione
        b = random.randint(1, 99)
        res = random.randint(1, 50)
        a = b * res
        return {"q": f"{a} / {b}", "a": res}

if st.session_state.current_exercise is None:
    st.session_state.current_exercise = generate_exercise()
    st.session_state.exercise_start_time = time.time()

# --- INTERFACCIA ---

# 1° Riga: Titolo
st.markdown('<p class="title" style="font-size: 40px;">Mathae Vis</p>', unsafe_allow_html=True)


# 2° Riga: Info Inizio e Nome
col_left, col_right = st.columns(2)
with col_left:
    st.write(st.session_state.start_time)
with col_right:
    nome = st.text_input("Partecipante", value="Homer J Simpson", key="user_name")

st.markdown('<div style="margin-top: 24px;"></div>', unsafe_allow_html=True)


# 3° Riga: Metriche
if st.session_state.history:
    df = pd.DataFrame(st.session_state.history)
    correct_df = df[df['esito'] == 'CORRETTO']
    perc_ok = (len(correct_df) / len(df)) * 100
    t_medio = correct_df['tempo'].mean() if not correct_df.empty else 0
    prog = len(df) + 1
else:
    perc_ok, t_medio, prog = 0, 0, 1

st.markdown(
    f"""
    <div style="text-align: center;">
        <span style="color:#28a745; font-size:24px; font-weight:bold;">
            ##: {prog} &nbsp;&nbsp;&nbsp;&nbsp; - &nbsp;&nbsp;&nbsp;&nbsp; ok: &nbsp;{perc_ok:.1f} % &nbsp;&nbsp;&nbsp;&nbsp; - &nbsp;&nbsp;&nbsp;&nbsp;T medio: &nbsp;{t_medio:.2f} s
        </span>
    </div>
    """,
    unsafe_allow_html=True
)


# 4° Riga: Esercizio
st.markdown(
    f"""
    <div style="
        margin-top: 2rem;
        background-color: #fff3cd;
        font-size: 40px;
        font-weight: bold;
        padding: 16px 20px;
        border-left: 6px solid #ffc107;
        border-radius: 6px;
        text-align: center;
    ">
        {st.session_state.current_exercise["q"]}
    </div>
    """,
    unsafe_allow_html=True
)


# 5° Riga: Input (Valida all'invio)
# --- LOGICA DI CONTROLLO (Inserisci questa funzione PRIMA del campo input) ---
def check_answer():
    # Accediamo alla chiave dinamica corretta
    current_key = f"user_input_{st.session_state.input_key}"
    ans = st.session_state.get(current_key)
    
    if ans is not None:
        end_time = time.time()
        elapsed = round(end_time - st.session_state.exercise_start_time, 2)
        correct_val = st.session_state.current_exercise["a"]
        esito = "CORRETTO" if int(ans) == correct_val else "ERRORE"
        
        # Salvataggio nei dati
        entry = {
            "n": len(st.session_state.history) + 1,
            "domanda": st.session_state.current_exercise["q"],
            "corretta": correct_val,
            "data": int(ans),
            "tempo": elapsed if esito == "CORRETTO" else None,
            "esito": esito
        }
        st.session_state.history.append(entry)
        
        # Impostazione feedback
        if esito == "CORRETTO":
            # st.session_state.feedback = f'<p class="feedback-ok">Minchia - EINSTEIN si sta cagando in mano nella tomba  -  Tempo: {elapsed} s</p>'
            st.session_state.feedback = f"""
                <p style="color: #28a745; font-size: 24px; font-weight: bold; text-align: center;">
                    Minchia - EINSTEIN si sta cagando in mano nella tomba  -  Tempo: {elapsed} s
                </p>
            """
        else:
            # st.session_state.feedback = f'<p class="feedback-ko">Sei proprio un MONGOLO - tornatene alle Elementari !!  -  Soluzione: {correct_val} </p>'    
            st.session_state.feedback = f"""
                <p style="color: #dc3545; font-size: 24px; font-weight: bold; text-align: center;">
                    Sei proprio un MONGOLO - tornatene alle Elementari !!  -  Soluzione: {correct_val}
                </p>
            """


# --- 5° RIGA: Campo di inserimento ---
# --- stile minimale ---
st.markdown("""
<style>
/* centra il contenitore del number_input */
div[data-baseweb="input"] {
    justify-content: center;
}

/* stile del campo numerico */
input {
    text-align: center !important;
    font-size: 40px !important;
    font-weight: bold !important;
}
</style>
""", unsafe_allow_html=True)
st.text_input(
    "Risposta:", 
    key=f"user_input_{st.session_state.input_key}", 
    on_change=check_answer
)


# 6° Riga: Feedback e attesa
if st.session_state.feedback:
    st.markdown(st.session_state.feedback, unsafe_allow_html=True)
    time.sleep(2)
    st.session_state.feedback = None
    # Prepariamo il prossimo esercizio
    st.session_state.current_exercise = None
    st.session_state.input_key += 1 # svuota il campo per il prossimo giro
    st.rerun()


# 7° Riga: Report PDF
st.markdown('<div style="margin-top: 40px; text-align: center;">', unsafe_allow_html=True)
if st.button("Genera Report"):
    if not st.session_state.history:
        st.error("Nessun dato per il report!")
    else:
        pdf = FPDF()
        pdf.add_page()
        # intestazione
        pdf.set_font("Helvetica", 'B', 24)
        pdf.set_text_color(0, 0, 255)
        pdf.cell(190, 20, "Mathae Vis", ln=True, align='C')
        
        pdf.set_font("Helvetica", '', 12)
        pdf.set_text_color(0, 0, 0)
        pdf.cell(190, 10, f"Data: {st.session_state.start_time} - Partecipante: {nome}", ln=True, align='C')
        
        # Grafico
        df_plot = pd.DataFrame(st.session_state.history)
        plt.figure(figsize=(6, 4))
        plt.plot(df_plot['n'], df_plot['tempo'].fillna(0), marker='o')
        plt.title("Grafico Tempi di Risposta")
        plt.xlabel("Esercizio")
        plt.ylabel("Tempi (s)")
        
        img_buf = io.BytesIO()
        plt.savefig(img_buf, format='png')
        img_buf.seek(0)  # riporta il cursore all'inizio del buffer
        pdf.image(img_buf, x=50, y=50, w=110)
        plt.close() # chiude la figura per liberare memoria
        
        # Tabella
        pdf.ln(80)
        pdf.set_font("Helvetica", 'B', 10)
        cols = ["N", "Domanda", "Corr", "Data", "T(s)", "Esito"]
        for col in cols: pdf.cell(30, 10, col, border=1)
        pdf.ln()
        
        pdf.set_font("Helvetica", '', 9)
        for _, row in df_plot.iterrows():
            pdf.cell(30, 8, str(row['n']), border=1)
            pdf.cell(30, 8, str(row['domanda']), border=1)
            pdf.cell(30, 8, str(row['corretta']), border=1)
            pdf.cell(30, 8, str(row['data']), border=1)
            pdf.cell(30, 8, str(row['tempo'] if row['tempo'] else "----"), border=1)
            
            if row['esito'] == "CORRETTO": pdf.set_text_color(0, 150, 0)
            else: pdf.set_text_color(255, 0, 0)
            pdf.cell(30, 8, row['esito'], border=1)
            pdf.set_text_color(0, 0, 0)
            pdf.ln()
        
        pdf_bytes = pdf.output(dest='S').encode('latin1')  #### FPDF2 PDF → bytes
        st.download_button( "Scarica Report PDF", 
                            # data=pdf.output(dest='S'),
                            data=pdf_bytes,
                            file_name="report_mathae_vis.pdf",
                            mime="application/pdf" )
st.markdown('</div>', unsafe_allow_html=True)