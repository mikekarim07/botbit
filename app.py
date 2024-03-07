import streamlit as st
import pandas as pd
from bitmart.api_spot import APISpot
from datetime import datetime
import time

st.set_page_config(
    page_title="Bot para operar en Bitmart",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'mailto:miguel.karim@karimortega.com'
    }
)


api_key = st.secrets["access_key"]
secret_key = st.secrets["secret_key"]
memo = st.secrets["memo"]
spotapi = APISpot(api_key, secret_key, memo, timeout=(3,10))

st.header("Bot Automático para operación de nuevos listados")

codigo = st.text_input('Cual era el verdadero apellido del Papá de mi Papá?', type="password")

#-----Creación de funciones


def orden_compra(symbol, notional):
    selected_symbol = symbol
    monto_usdt = notional
    # Ejecutar la orden
    response = spotapi.post_submit_order(symbol=selected_symbol, side="buy", type="market", notional=monto_usdt)
    # Imprimir la respuesta de la API
    st.write(response)

def orden_venta(symbol, size):
    selected_symbol = symbol
    total_disponible = size
    response = spotapi.post_submit_order(symbol=selected_symbol, side="sell", type="market", size=total_disponible)
    st.write(response)

def total_disponible():
    response = spotapi.get_wallet()
    if isinstance(response, tuple) and len(response) > 0:
        response = response[0]
    wallet_data = response.get('data', {}).get('wallet', [])
    columns = ['id', 'name', 'available', 'frozen', 'total']
    wallet = pd.DataFrame(wallet_data, columns=columns)
    wallet[['available', 'total']] = wallet[['available', 'total']].apply(pd.to_numeric)
    wallet = wallet[wallet['available'] > 0]
    wallet_for_screen = wallet[['id','total']]

    
    symbols_in_wallet = wallet['id'].unique()
    symbol_for_sell = st.selectbox('Selecciona el par para vender', symbols_in_wallet)
    
    
    total_available = wallet[wallet['id']==symbol_for_sell]
    total_available = total_available['available'].values[0]
    total_disponible = str("{:,.2f}".format(total_available))

    
    st.dataframe(wallet_for_screen)
    
# def 
    
    
    
#     response = spotapi.v4_query_account_trade_list()
# if isinstance(response, tuple) and len(response) > 0:
#   response = response[0]
# orders_data = response.get('data', {})


# orders = pd.DataFrame(orders_data)
# orders[['price', 'size', 'notional', 'fee']] = orders[['price', 'size', 'notional', 'fee']].apply(pd.to_numeric)
# orders = orders[(orders['symbol']==symbol_wallet) & (orders['side']=='buy')]
# orders['Total Price'] = orders['notional'] + orders['fee']
# orders = orders.groupby(by=['symbol'], as_index=False).agg({'size': 'sum', 'Total Price': 'sum'})
# orders['Precio Prom Compra'] = orders['Total Price'] / orders['size']
# Precio_promedio = orders['Precio Prom Compra'].values[0]
# Size = orders['size'].values[0]





if codigo == st.secrets["codigo_familiar"]:
  #-----Obtener Pares de Cotización
  response_symbols = spotapi.get_symbols()
  data_response_symbols = response_symbols[0].get('data', {})
  all_symbols = data_response_symbols.get('symbols', [])
  df_symbols = pd.DataFrame({'Symbols': all_symbols})
  df_symbols = df_symbols.sort_values(by='Symbols')
  df_symbols = ['Seleccionar'] + df_symbols['Symbols'].tolist()
  
  
  #-----Creación de dataframes con horas y minutos para los selectboxes
  hours_df = pd.DataFrame({'Hour': [str(i).zfill(2) for i in range(25)]})
  minutes_df = pd.DataFrame({'Minute': [str(i).zfill(2) for i in range(60)]})

  #----- Creación de las 2 pestañas
  tab1, tab2 = st.tabs(["Bot de Compra", "Wallet"])
  
  with tab1:
    st.subheader("Programación de Orden de Compra")
    st.write('Selecciona de la lista el para para operar, en caso de que aun no este listado, no selecciones ninguno e ingresalo manualmente en la casilla de texto que esta a la derecha')  
    r1c1, r1c2 = st.columns(2)
    with r1c1:
      
      symbol_fromlist = st.selectbox('Selecciona el par', df_symbols)
    with r1c2:
      if symbol_fromlist == 'Seleccionar':
      # Mostrar el widget de input de texto solo cuando la opción sea "Seleccionar"
        par_manual = st.text_input("Ingresa el par manualmente")
        
    symbol_for_bot = symbol_fromlist if symbol_fromlist != 'Seleccionar' else par_manual
    st.write(symbol_for_bot)
    
    
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
    
    
    
    
    target_time_low = datetime.strptime(str(year) + '-' + str(month) + '-' + str(day) + ' ' + hora + ':' + minuto + ':' + '00.000001', '%Y-%m-%d %H:%M:%S.%f')
    target_time_high = datetime.strptime(str(year) + '-' + str(month) + '-' + str(day) + ' ' + hora + ':' + minuto + ':' + '05.000000', '%Y-%m-%d %H:%M:%S.%f')
    
    st.subheader("Parametros elegidos")
    # st.write("Par seleccionado :" + symbol_for_bot)
    st.write(symbol_for_bot)
    st.write('Ventana de tiempo')
    st.caption('Tiempo inicial: ' + str(target_time_low))
    st.caption('Tiempo final: ' + str(target_time_high))
    st.caption('Monto: ' + str(monto_usdt))
    st.caption('Simbolo para extraer total de la cartera: ' + symbol_for_bot)

    correr = st.checkbox('Correr bot')
    if correr:
        while True:
            current_time = datetime.now()
    
            # Check if the current time is greater than or equal to the target time
            if target_time_low <= current_time <= target_time_high:
                st.write(current_time)
                orden_compra(symbol_for_bot, monto_usdt)
              # spotapi.post_submit_order(symbol=symbol_for_bot, side="buy", type="market", notional=monto_usdt)
                st.success("Operación ejecutada con éxito.")
                            # execute_buy_order(spotAPI)
                break
            else:
                time.sleep(0.000001)  # Sleep for a short duration before checking again


                # time.sleep(5)
              
  #             response = spotapi.v4_query_account_trade_list()
  #             if isinstance(response, tuple) and len(response) > 0:
  #                 response = response[0]
  #             orders_data = response.get('data', {})
              
              
  #             orders = pd.DataFrame(orders_data)
  #             orders[['price', 'size', 'notional', 'fee']] = orders[['price', 'size', 'notional', 'fee']].apply(pd.to_numeric)
  #             orders = orders[(orders['symbol']==symbol_wallet) & (orders['side']=='buy')]
  #             orders['Total Price'] = orders['notional'] + orders['fee']
  #             orders = orders.groupby(by=['symbol'], as_index=False).agg({'size': 'sum', 'Total Price': 'sum'})
  #             orders['Precio Prom Compra'] = orders['Total Price'] / orders['size']
  #             Precio_promedio = orders['Precio Prom Compra'].values[0]
  #             Size = orders['size'].values[0]

  #             # ----vender
  #             # if st.button(""):
  #             # st.success("")
  
  #             # spotapi.post_submit_order(symbol=selected_symbol, side="sell", type="market", size=total_purchased)

              
              
  #             break
  #           else:
  #               time.sleep(0.000001)  # Sleep for a short duration before checking again
    
    
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
    st.dataframe(wallet_for_screen, width=800)

    symbols_in_wallet = wallet['id'].unique()
    symbol_for_sell = st.selectbox('Selecciona el par para vender', symbols_in_wallet)
    

    total_available = wallet[wallet['id']==symbol_for_sell]
    total_available = total_available['available'].values[0]
    total_disponible = str("{:,.2f}".format(total_available))
    st.subheader('Total disponible de '+ symbol_for_sell)
    st.subheader(total_disponible)

    # if st.button('Vender'):
    #   orden_venta(symbol_for_sell, total_disponible)


  #   #----determinar el valor de las ordenes y precio promedio
  #   response = spotapi.v4_query_account_trade_list()
  #   if isinstance(response, tuple) and len(response) > 0:
  #       response = response[0]
  #   orders_data = response.get('data', {})
    
    
  #   orders = pd.DataFrame(orders_data)
  #   orders[['price', 'size', 'notional', 'fee']] = orders[['price', 'size', 'notional', 'fee']].apply(pd.to_numeric)
  #   symbol_for_sell = symbol_for_sell + '_USDT'
  #   orders = orders[(orders['symbol']==symbol_for_sell) & (orders['side']=='buy')]
  #   orders['Total Price'] = orders['notional'] + orders['fee']
  #   orders = orders.groupby(by=['symbol'], as_index=False).agg({'size': 'sum', 'Total Price': 'sum'})
  #   orders['Precio Prom Compra'] = orders['Total Price'] / orders['size']
  #   Precio_promedio = orders['Precio Prom Compra'].values[0]
  #   Precio_promedio_pantalla = str("{:,.15f}".format(Precio_promedio))
  #   st.subheader('Precio Promedio de compra de '+ symbol_for_sell)
  #   st.subheader(Precio_promedio_pantalla)

  #   if st.button('Vender'):
  #     spotapi.post_submit_order(symbol=symbol_for_sell, side="sell", type="market", size=total_available)
      
  #     # spotapi.post_submit_order(symbol=symbol_for_sell, side="sell", type="market", size=
  #     #-----




  # # with tab3:
  # #   st.subheader("Valor de la cartera")
  # #   response = spotapi.get_wallet()
  # #   if isinstance(response, tuple) and len(response) > 0:
  # #     response = response[0]
  # #   wallet_data = response.get('data', {}).get('wallet', [])
  # #   columns = ['id', 'name', 'available', 'frozen', 'total']
  # #   wallet = pd.DataFrame(wallet_data, columns=columns)
  # #   wallet[['available', 'total']] = wallet[['available', 'total']].apply(pd.to_numeric)
  # #   st.table(wallet)
    
  # #   total_available = wallet[wallet['id']==symbol_wallet]
  # #   total_available = total_available['available'].values[0]
  # #   total_available = str("{:,.2f}".format(total_available))
  # #   st.write(total_available)

  # #   if st.button("Vender: "+ symbol_wallet):
  # #     st.write("Vendiendo a valor de mercado")
  # #     # spotapi.post_submit_order(symbol="CHONKY_USDT", side="sell", type="market", qty=total_available)
    
    
    
