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

col1, col2, col3, col4, col5 = st.columns(5)

with col1:
  st.caption("Crypto")
  selected_symbol = st.selectbox('Selecciona el par', df)

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

with col5:
  st.caption("Monto")
  monto_usdt = st.text_input("Monto en USDT")  

symbol_wallet = selected_symbol.split('_')
symbol_wallet = symbol_wallet[0]


target_time_low = datetime.strptime(str(year) + '-' + str(month) + '-' + str(day) + ' ' + hora + ':' + minuto + ':' + '00.000000', '%Y-%m-%d %H:%M:%S.%f')
target_time_high = datetime.strptime(str(year) + '-' + str(month) + '-' + str(day) + ' ' + hora + ':' + minuto + ':' + '00.006000', '%Y-%m-%d %H:%M:%S.%f')

st.subheader("Parametros elegidos")
st.write("Moneda seleccionada :" + selected_symbol)
st.write('Ventana de tiempo')
st.caption('Tiempo inicial: ' + str(target_time_low))
st.caption('Tiempo final: ' + str(target_time_high))
st.caption('Monto: ' + str(monto_usdt))
st.caption('Simbolo para extraer total de la cartera: ' + symbol_wallet)

if st.button("Ejecutar Bot"):
    while True:
        current_time = datetime.now()

        # Check if the current time is greater than or equal to the target time
        if target_time_low <= current_time <= target_time_high:
          spotapi.post_submit_order(symbol=selected_symbol, side="buy", type="market", notional=monto_usdt)
          st.success("Operación ejecutada con éxito.")
          
          response = spotapi.get_wallet()
          if isinstance(response, tuple) and len(response) > 0:
              response = response[0]
          wallet_data = response.get('data', {}).get('wallet', [])
          columns = ['id', 'name', 'available', 'frozen', 'total']
          wallet = pd.DataFrame(wallet_data, columns=columns)

          total_available = wallet[wallet['id']==symbol_wallet]
          total_available = total_available['available'].values[0]
          total_available = "{:,.2f}".format(total_available)
          
          break
        else:
            time.sleep(0.000001)  # Sleep for a short duration before checking again

if st.button("Detener Bot"):
    st.warning("Bot Detenido")
