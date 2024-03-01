import streamlit as st
import pandas as pd
from bitmart.api_spot import APISpot
from datetime import datetime
import time

api_key = ""
secret_key = ""
memo = "NL2"
spotapi = APISpot(api_key, secret_key, memo, timeout=(3,10))

st.header("Bot Automatico para operación de nuevos listados")

response = spotapi.get_symbols()
data_response = response[0].get('data', {})
all_symbols = data_response.get('symbols', [])

df = pd.DataFrame({'Symbols': all_symbols})
df = df.sort_values(by='Symbols')
hours_df = pd.DataFrame({'Hour': [str(i).zfill(2) for i in range(25)]})
minutes_df = pd.DataFrame({'Minute': [str(i).zfill(2) for i in range(60)]})

col1, col2, col3, col4 = st.columns(4)

with col1:
  st.caption("Crypto")
  symbol = st.selectbox('Selecciona el par', df)

with col2:
  st.caption("Fecha")
  selected_date = st.date_input("Selecciona una fecha", datetime.now())
  year = selected_date.year
  month = selected_date.month
  day = selected_date.day

with col3:
  st.caption("Hora")
  hora = st.selectbox("Selecciona la hora", hours_df)  

with col4:
  st.caption("Minuto")
  minuto = st.selectbox("Selecciona el minuto", minutes_df)  

st.subheader("Parametros elegidos")
st.write("Moneda seleccionada :" + symbol)
st.write('Ventana de tiempo')
st.caption('Tiempo inicial')
st.caption(target_time_low)
st.caption('Tiempo final')
st.caption(target_time_high)





target_time_low = datetime.strptime(str(year) + '-' + str(month) + '-' + str(day) + ' ' + hora + ':' + minuto + ':' + '00.000000', '%Y-%m-%d %H:%M:%S.%f')
target_time_high = datetime.strptime(str(year) + '-' + str(month) + '-' + str(day) + ' ' + hora + ':' + minuto + ':' + '00.006000', '%Y-%m-%d %H:%M:%S.%f')

# target_time_high = datetime.strptime('2024-02-29 18:34:00.006000', '%Y-%m-%d %H:%M:%S.%f')
# # Specify the target execution time in HH:MM:SS format
# target_time_low = datetime.strptime('2024-02-29 18:34:00.000000', '%Y-%m-%d %H:%M:%S.%f')
# target_time_high = datetime.strptime('2024-02-29 18:34:00.006000', '%Y-%m-%d %H:%M:%S.%f')

# while True:
#     current_time = datetime.now()

#     # Check if the current time is greater than or equal to the target time
#     if target_time_low <= current_time <= target_time_high:
#         spotapi.post_submit_order(symbol="STRK_USDT", side="buy", type="market", notional="7")
#         break
#     else:
#         time.sleep(0.000001)  # Sleep for a short duration before checking again
