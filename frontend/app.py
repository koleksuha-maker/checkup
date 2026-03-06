import streamlit as st
import requests
import pandas as pd
import plotly.express as px

# URL вашего FastAPI
API_URL = "https://checkup-dz.onrender.com" 

st.title("Энергорынок РФ: Потребление и Цены")

# 1. Получение данных (как в примере PDF)
try:
    response = requests.get(f"{API_URL}/records")
    # Проверяем, что сервер ответил успешно (код 200)
    if response.status_code == 200:
        data = response.json()
    else:
        st.error(f"Ошибка сервера: {response.status_code}")
        data = []
except Exception as e:
    st.error(f"Не удалось подключиться к API: {e}")
    data = []

# 2. Таблица (как в примере PDF)
df = pd.DataFrame(data)
st.dataframe(df)

# --- Простой график (из Page 2 PDF) ---
if not df.empty:
    # Первый график: Интерактивный через Plotly (потребление)
    fig = px.line(df, x="timestep", y="consumption_eur", title="Потребление (Европа) — Plotly")
    st.plotly_chart(fig)

    # ВТОРОЙ ГРАФИК: Простой через st.line_chart (цены)
    # Для st.line_chart лучше подготовить данные, где индекс — это время
    chart_data = df.set_index("timestep")[["price_eur", "price_sib"]]
    st.write("Цены в обеих зонах — Streamlit Line Chart")
    st.line_chart(chart_data)

# --- Форма добавления записи ---
with st.form("add_record"):
    timestep = st.text_input("Timestep (YYYY-MM-DD HH:MM:SS)")
    consum_eur = st.number_input("Consumption EUR", min_value=0.0)
    consum_sib = st.number_input("Consumption SIB", min_value=0.0)
    price_eur = st.number_input("Price EUR", min_value=0.0)
    price_sib = st.number_input("Price SIB", min_value=0.0)
    submit = st.form_submit_button("Add")
    
    if submit:
        new_data = {
            "timestep": timestep,
            "consumption_eur": consum_eur, 
            "consumption_sib": consum_sib,
            "price_eur": price_eur,
            "price_sib": price_sib
        }
        res = requests.post(f"{API_URL}/records", json=new_data)
        if res.status_code == 200:
            # ИСПРАВЛЕНИЕ 2: Если st.rerun() не работает, используем старую версию
            try:
                st.rerun()
            except AttributeError:
                st.experimental_rerun()
        else:
            st.error("Ошибка при добавлении записи")

# --- Удаление записи ---
delete_id = st.number_input("ID to delete", min_value=0, step=1)
if st.button("Delete"):
    res = requests.delete(f"{API_URL}/records/{int(delete_id)}")
    if res.status_code == 200:
        # ИСПРАВЛЕНИЕ 3: Аналогично для удаления
        try:
            st.rerun()
        except AttributeError:
            st.experimental_rerun()
    else:
        st.error("Ошибка при удалении. Проверьте ID.")

