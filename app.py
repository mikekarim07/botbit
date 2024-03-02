import streamlit as st
import pandas as pd
from bitmart.api_spot import APISpot
from datetime import datetime
import time

api_key = "d1056b18923ec825c50fe26ee4b0b790add6c406"
secret_key = "54d2cd2bcaede3c71af75760b9b0095666c06344be86fe0e17c4518bc6ec4e30"
memo = "NL2"
spotapi = APISpot(api_key, secret_key, memo, timeout=(3,10))

st.header("Bot Automatico para operación de nuevos listados")

codigo = st.text_input('Cual es el apellido de la familia?')

if codigo = codigo_familiar
  st.write('Im good')

response = spotapi.get_symbols()
data_response = response[0].get('data', {})
all_symbols = data_response.get('symbols', [])

df = pd.DataFrame({'Symbols': all_symbols})
df = df.sort_values(by='Symbols')
hours_df = pd.DataFrame({'Hour': [str(i).zfill(2) for i in range(25)]})
minutes_df = pd.DataFrame({'Minute': [str(i).zfill(2) for i in range(60)]})


col1_gral, col2_gral = st.columns([1,3])
with col1_gral:
  st.caption("Crypto")
  selected_symbol = st.selectbox('Selecciona el par', df)
  symbol_wallet = selected_symbol.split('_')
  symbol_wallet = symbol_wallet[0]
with col2_gral:
  st.write()




tab1, tab2 = st.tabs(["Orden", "Cartera y Venta"])

with tab1:
  st.subheader("Orden de Compra de nuevos pares")

  col1, col2, col3, col4 = st.columns(4)
  
  with col1:
    st.caption("Fecha")
    selected_date = st.date_input("Selecciona una fecha", datetime.now())
    year = selected_date.year
    month = selected_date.month
    day = selected_date.day
  
  with col2:
    st.caption("Hora")
    hora = st.selectbox("Selecciona la hora", hours_df)  
  
  with col3:
    st.caption("Minuto")
    minuto = st.selectbox("Selecciona el minuto", minutes_df)
  
  with col4:
    st.caption("Monto")
    monto_usdt = st.text_input("Monto en USDT")  
  
  
  
  
  target_time_low = datetime.strptime(str(year) + '-' + str(month) + '-' + str(day) + ' ' + hora + ':' + minuto + ':' + '00.000000', '%Y-%m-%d %H:%M:%S.%f')
  target_time_high = datetime.strptime(str(year) + '-' + str(month) + '-' + str(day) + ' ' + hora + ':' + minuto + ':' + '00.006000', '%Y-%m-%d %H:%M:%S.%f')
  
  st.subheader("Parametros elegidos")
  # st.write("Moneda seleccionada :" + selected_symbol)
  st.write(selected_symbol)
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







with tab2:
  st.subheader("Valor de la cartera para venta")
  response = spotapi.get_wallet()
  if isinstance(response, tuple) and len(response) > 0:
    response = response[0]
  wallet_data = response.get('data', {}).get('wallet', [])
  columns = ['id', 'name', 'available', 'frozen', 'total']
  wallet = pd.DataFrame(wallet_data, columns=columns)
  wallet[['available', 'total']] = wallet[['available', 'total']].apply(pd.to_numeric)
  st.table(wallet)
  
  total_available = wallet[wallet['id']==symbol_wallet]
  total_available = total_available['available'].values[0]
  total_available = str("{:,.2f}".format(total_available))
  st.write(total_available)
  
  if st.button("Vender: "+ symbol_wallet):
    st.write("Vendiendo a valor de mercado")
    # spotapi.post_submit_order(symbol="CHONKY_USDT", side="sell", type="market", qty=total_available)
  
  
  
