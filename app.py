import streamlit as st
import pandas as pd
from bitmart.api_spot import APISpot
from datetime import datetime
import time

api_key = st.secrets["access_key"]
secret_key = st.secrets["secret_key"]
memo = st.secrets["memo"]
spotapi = APISpot(api_key, secret_key, memo, timeout=(3,10))

st.header("Bot Automático para operación de nuevos listados")

codigo = st.text_input('Cual era el verdadero apellido del Papá de mi Papá?', type="password")

if codigo == st.secrets["codigo_familiar"]:


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
  
  
  
  
  tab1, tab2 = st.tabs(["Orden", "Cartera"])
  
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

    correr = st.checkbox('Correr bot')
    if correr:
        while True:
            current_time = datetime.now()
    
            # Check if the current time is greater than or equal to the target time
            if target_time_low <= current_time <= target_time_high:
              spotapi.post_submit_order(symbol=selected_symbol, side="buy", type="market", notional=monto_usdt)
              st.success("Operación ejecutada con éxito.")

              time.sleep(5)
              
              response = spotapi.v4_query_account_trade_list()
              if isinstance(response, tuple) and len(response) > 0:
                  response = response[0]
              orders_data = response.get('data', {})
                            
              orders = pd.DataFrame(orders_data)
              orders[['price', 'size', 'notional', 'fee']] = orders[['price', 'size', 'notional', 'fee']].apply(pd.to_numeric)
              orders = orders[(orders['symbol']==symbol_wallet) & (orders['side']=='buy')]
              orders['Total Price'] = orders['notional'] + orders['fee']
              orders = orders.groupby(by=['symbol'], as_index=False).agg({'size': 'sum', 'Total Price': 'sum'})
              orders['Precio Prom Compra'] = orders['Total Price'] / orders['size']
              Precio_promedio = orders['Precio Prom Compra'].values[0]
              st.subheader('Precio Promedio de compra de '+ selected_symbol)
              st.subheader(Precio_promedio)
              
              # total_purchased = orders['size'].values[0]

              #----vender
              # if st.button(""):
              # st.success("")
  
              # spotapi.post_submit_order(symbol=selected_symbol, side="sell", type="market", size=total_purchased)

              
              
              break
            else:
                time.sleep(0.000001)  # Sleep for a short duration before checking again
    
    
  with tab2:
    st.subheader("Activos en cartera")
    response = spotapi.get_wallet()
    if isinstance(response, tuple) and len(response) > 0:
      response = response[0]
    wallet_data = response.get('data', {}).get('wallet', [])
    columns = ['id', 'name', 'available', 'frozen', 'total']
    wallet = pd.DataFrame(wallet_data, columns=columns)
    wallet[['available', 'total']] = wallet[['available', 'total']].apply(pd.to_numeric)
    wallet = wallet[wallet['available'] > 0]
    wallet_for_screen = wallet[['id','total']]
    st.dataframe(wallet_for_screen)

    symbols_in_wallet = wallet['id'].unique()
    symbol_for_sell = st.selectbox('Selecciona el par para vender', symbols_in_wallet)
    

    total_available = wallet[wallet['id']==symbol_for_sell]
    total_available = total_available['available'].values[0]
    total_available = str("{:,.2f}".format(total_available))
    st.subheader('Total disponible de '+ symbol_for_sell)
    st.subheader(total_available)
    
    response_1 = spotapi.v4_query_account_trade_list()
    if isinstance(response_1, tuple) and len(response_1) > 0:
        response_1 = response_1[0]
    orders_data_tab2 = response.get('data', {})
                  
    orders_data_tab2 = pd.DataFrame(orders_data_tab2)
    # st.dataframe(orders_data_tab2)
    orders_tab2[['price', 'size', 'notional', 'fee']] = orders_data_tab2[['price', 'size', 'notional', 'fee']].apply(pd.to_numeric)
    # orders_tab2 = orders_tab2[(orders['symbol']==symbol_wallet) & (orders_tab2['side']=='buy')]
    # orders_tab2['Total Price'] = orders_tab2['notional'] + orders_tab2['fee']
    # orders_tab2 = orders_tab2.groupby(by=['symbol'], as_index=False).agg({'size': 'sum', 'Total Price': 'sum'})
    # orders_tab2['Precio Prom Compra'] = orders_tab2['Total Price'] / orders_tab2['size']
    # Precio_promedio = orders_tab2['Precio Prom Compra'].values[0]
    
    # st.subheader('Precio Promedio de compra de '+ symbol_for_sell)


  # with tab3:
  #   st.subheader("Valor de la cartera")
  #   response = spotapi.get_wallet()
  #   if isinstance(response, tuple) and len(response) > 0:
  #     response = response[0]
  #   wallet_data = response.get('data', {}).get('wallet', [])
  #   columns = ['id', 'name', 'available', 'frozen', 'total']
  #   wallet = pd.DataFrame(wallet_data, columns=columns)
  #   wallet[['available', 'total']] = wallet[['available', 'total']].apply(pd.to_numeric)
  #   st.table(wallet)
    
  #   total_available = wallet[wallet['id']==symbol_wallet]
  #   total_available = total_available['available'].values[0]
  #   total_available = str("{:,.2f}".format(total_available))
  #   st.write(total_available)

  #   if st.button("Vender: "+ symbol_wallet):
  #     st.write("Vendiendo a valor de mercado")
  #     # spotapi.post_submit_order(symbol="CHONKY_USDT", side="sell", type="market", qty=total_available)
    
    
    
