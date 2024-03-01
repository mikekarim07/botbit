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

response = spotapi.get_symbols()
data_response = response[0].get('data', {})
all_symbols = data_response.get('symbols', [])

df = pd.DataFrame({'Symbols': all_symbols})
df = df.sort_values(by='Symbols')
symbol = st.selectbox('Selecciona el par', df)
st.write("Moneda seleccionada :" + symbol)



# spotapi = APISpot(api_key, secret_key, memo, timeout=(3, 10))

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
