# streamlit_app.py
import streamlit as st
import pandas as pd
import time
from serial_reader import SerialReader
from utils import safe_float, rele_to_bool

st.set_page_config(page_title="Arduino JSON Dashboard", layout="wide")

st.title("Painel - Arduino JSON (Serial → JSON)")

# Sidebar - configurações
st.sidebar.header("Configurações Serial")
reader = None

# seleção de porta
serial_port = st.sidebar.text_input("Porta Serial (ex: COM3 ou /dev/ttyUSB0). Deixe vazio para auto-detect.", value="")
baudrate = st.sidebar.number_input("Baudrate", value=9600, step=1)
buffer_size = st.sidebar.number_input("Tamanho do buffer (itens)", value=200, step=10)

if 'reader' not in st.session_state:
    st.session_state.reader = SerialReader(port=serial_port or None, baudrate=int(baudrate), buffer_size=int(buffer_size))
    st.session_state.reader.start()
    st.session_state.started = True

reader = st.session_state.reader

st.sidebar.markdown("**Portas detectadas:**")
ports = reader.list_ports()
for p in ports:
    st.sidebar.write(p)

if st.sidebar.button("Reiniciar conexão"):
    reader.stop()
    st.session_state.reader = SerialReader(port=serial_port or None, baudrate=int(baudrate), buffer_size=int(buffer_size))
    st.session_state.reader.start()
    st.experimental_rerun()

# Painel principal
col1, col2 = st.columns([2,1])

with col1:
    st.subheader("Último registro (JSON bruto)")
    last = reader.get_latest()
    st.code(last if last else "Sem dados ainda...", language="json")

    st.subheader("Gráfico de temperatura")
    history = reader.get_history(200)
    if history:
        # Tentamos extrair campo 'temperatura' ou 'temperatura' em pt/eng
        temps = []
        timestamps = []
        for item in history:
            t = item.get("temperatura") or item.get("temp") or item.get("temperature") or None
            temps.append(safe_float(t, None))
            timestamps.append(item.get("ts", None))
        df = pd.DataFrame({"ts": timestamps, "temperatura": temps})
        df = df.dropna().sort_values("ts")
        df['ts_readable'] = pd.to_datetime(df['ts'], unit='s')
        df = df.set_index('ts_readable')
        st.line_chart(df['temperatura'])
    else:
        st.info("Aguardando dados...")

with col2:
    st.subheader("Estado atual")
    if last:
        temp = last.get("temperatura") or last.get("temp") or last.get("temperature")
        rele = last.get("rele") or last.get("relay") or last.get("rele_state")
        st.metric("Temperatura (°C)", f"{safe_float(temp, 0):.1f}")
        st.metric("Relé", "ON" if rele_to_bool(rele) else "OFF")
    else:
        st.write("Sem dados")

    st.subheader("Eventos recentes")
    evs = reader.get_events(20)
    if evs:
        for e in reversed(evs):
            ts = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(e["ts"]))
            st.write(f"{ts} — {e['msg']}")
    else:
        st.write("Sem eventos")

st.caption("Conecte o Arduino e envie JSONs por Serial no formato visto anteriormente. Ex: {\"temperatura\":180.0,\"rele\":\"ON\",\"estado\":\"OSCILACAO\"}")
