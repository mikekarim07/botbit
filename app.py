import streamlit as st
import pandas as pd
from bitmart.api_spot import APISpot
from datetime import datetime
import time

st.set_page_config(
    page_title="Bot para operar en Bitmart 1.0",
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
    selected_symbol_sell = symbol
    total_disponible = size
    response = spotapi.post_submit_order(symbol=selected_symbol_sell, side="sell", type="market", size=total_disponible)
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
    
def precio_promedio(symbol):
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
    Size = orders['size'].values[0]

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
  tab1, tab2, tab3 = st.tabs(["Bot de Compra", "Wallet", "$ Estatus Wallet"])
  
  with tab1:
    st.subheader("Programación de Orden de Compra")
    st.write('Selecciona de la lista el para para operar, en caso de que aun no este listado, no selecciones ninguno e ingresalo manualmente en la casilla de texto que esta a la derecha')  
    r1c1, r1c2 = st.columns(2)
    with r1c1:
      symbol_fromlist = st.selectbox('Selecciona el par', df_symbols)
    with r1c2:
      if symbol_fromlist == 'Seleccionar':
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
      # minuto_final = minuto + 5  
      # st.write(minuto_final)  
    with col4:
      st.caption("Monto")
      monto_usdt = st.text_input("Monto en USDT")  
    
    target_time_low = datetime.strptime(str(year) + '-' + str(month) + '-' + str(day) + ' ' + hora + ':' + minuto + ':' + '00.000002', '%Y-%m-%d %H:%M:%S.%f')
    target_time_high = datetime.strptime(str(year) + '-' + str(month) + '-' + str(day) + ' ' + hora + ':' + minuto + ':' + '59.999999', '%Y-%m-%d %H:%M:%S.%f')
    
    st.subheader("Parametros elegidos")
    st.write("Par seleccionado :" + symbol_for_bot)
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

    st.divider()

    st.subheader('Compra Manual en caso de que no jale la compra automatica')
    monto_manual = st.text_input('Ingresa el monto en USDT a comprar')
    st.write('Vas a comprar ' + monto_manual + ' de: ' + symbol_for_bot)
    if st.button('Comprar Manual'):
      orden_compra(symbol_for_bot, monto_manual)


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
    #----- Get Wallet
    response = spotapi.get_wallet()
    if isinstance(response, tuple) and len(response) > 0:
      response = response[0]
    wallet_data = response.get('data', {}).get('wallet', [])
    columns = ['id', 'name', 'available', 'frozen', 'total']
    wallet = pd.DataFrame(wallet_data, columns=columns)
    wallet[['available', 'total']] = wallet[['available', 'total']].apply(pd.to_numeric)
    wallet = wallet[wallet['available'] > 0]
    wallet_for_screen = wallet[['id','total']]

    #----- Get Orders
    response_orders = spotapi.v4_query_account_trade_list()
    if isinstance(response_orders, tuple) and len(response_orders) > 0:
        response = response_orders[0]
    orders_data = response.get('data', {})
    
    orders = pd.DataFrame(orders_data)
    orders[['price', 'size', 'notional', 'fee']] = orders[['price', 'size', 'notional', 'fee']].apply(pd.to_numeric)
    orders['total pagado'] = orders['notional'] + orders['fee']
    orders = orders[orders['side']=='buy']
    orders = orders.groupby(by=['symbol'], as_index=False).agg({'total pagado': 'sum', 'size': 'sum'})
    orders['Precio Prom'] = orders['total pagado'] / orders['size']
    orders['Precio Prom'] = orders['Precio Prom'].apply(lambda x: "{:,.15f}".format(x))
    
    #----- Cross tables (Wallet & Orders) to get purchase average price
    wallet_for_screen['id'] = wallet_for_screen['id'] + '_USDT'
    
    wallet_for_screen = wallet_for_screen.merge(orders, left_on="id", right_on='symbol', how='left')
    wallet_for_screen = wallet_for_screen[['id','total', 'Precio Prom']]
    wallet_for_screen = wallet_for_screen.fillna(0)
    wallet_for_screen['Precio Prom Num'] = pd.to_numeric(wallet_for_screen['Precio Prom'], errors='coerce')
    wallet_for_screen['Total Posicion'] = wallet_for_screen['total'] * wallet_for_screen['Precio Prom Num']
    wallet_for_screen = wallet_for_screen[['id','total', 'Precio Prom', 'Total Posicion']]
    
    
    st.dataframe(wallet_for_screen, width=800)
    
    symbols_in_wallet = wallet['id'].unique()
    symbol_for_sell = st.selectbox('Selecciona el par para vender', symbols_in_wallet)
    # symbol_for_sell = symbol_for_sell + '_USDT'
    
    total_available = wallet[wallet['id']==symbol_for_sell]
    total_available = total_available['available'].values[0]
    total_disponible = str(total_available)
    st.subheader('Total disponible de '+ symbol_for_sell)
    st.subheader(total_disponible)
    symbol_for_sell = symbol_for_sell + '_USDT'
    st.write(symbol_for_sell)
      
    if st.button('Vender'):
        orden_venta(symbol_for_sell, total_disponible)






  with tab3:
    st.subheader("Estatus financiero de la cartera")
    wallet_value = wallet_for_screen.copy()
    symbols_for_tickers = wallet_value['id'].unique()
    
    last_prices = []
    
    for symbol in symbols_for_tickers:
        try:
            # Fetch ticker information for the current symbol
            response_tuple = spotapi.get_symbol_ticker(symbol)
            
            # Check if the response_tuple is not empty
            if response_tuple:
                # Assuming the first element of the tuple is the dictionary containing the response
                response_dict = response_tuple[0]
                
                # Extract the 'last_price' from the response dictionary
                last_price = response_dict['data']['last_price']
                
                # Append last price to the list
                last_prices.append(last_price)
            else:
                # If response_tuple is empty, append None
                last_prices.append(None)
            
    # Add the list of last prices as a new column to the DataFrame
    wallet_value['last_price'] = last_prices
    st.write(wallet_value)
