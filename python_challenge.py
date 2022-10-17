# -- Import --
import pandas as pd
from binance.client import Client

import ta
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime

pairName = "ETHBTC"

print(f"We will present the dataframe of {pairName} to csv file and a graph of the corresponding RSI and volume")

rsi_param = input("Please enter the RSI parameter (recommended 14):") 
lower_treshold = input("Please enter the lower treshold for RSI included in [0;100]:") 
upper_treshold = input("Please enter the upper treshold for RSI included in [0;100]:") 


startDate = None
while(startDate==None):
    try :
        startDate = datetime.strptime(input("Please enter the start date (format: yyyy/mm/dd):"), '%Y/%m/%d')
        print(f'You entered {startDate}')
        break
    except :
        print("Syntax error, please retry.")
 
endDate = None
while(endDate==None):
    try :
        endDate = datetime.strptime(input("Please enter the end date (format: yyyy/mm/dd):"), '%Y/%m/%d')
        print(f'You entered {endDate}')
        break
    except :
        print("Syntax error, please retry.")

timeframe = None
while(timeframe==None):
    time_step = input("Please select a timeframe: weekly/daily/hourly:") 
    if time_step in ["weekly", "daily", "hourly"] :
        timeframe=time_step
        print(f'You entered {time_step}') 
        break
    else :
        print("Syntax error, please retry.")

print(f'We are downloading data of {pairName} from {startDate} to {endDate} in {time_step} timeframe')

if time_step == 'weekly':
  timeInterval = Client.KLINE_INTERVAL_1WEEK
elif time_step == 'daily':
  timeInterval = Client.KLINE_INTERVAL_1DAY
elif time_step == 'hourly':
  timeInterval = Client.KLINE_INTERVAL_1HOUR

# -- Define Binance Client --
client = Client()

# -- Load all price data from binance API --
startDate = str(startDate)
endDate = str(endDate)
timeInterval = str(timeInterval)

klinesT = client.get_historical_klines(pairName, timeInterval, startDate, endDate)


# -- Define the dataset --
df = pd.DataFrame(klinesT, columns = ['timestamp', 'open', 'high', 'low', 'close', 'volume', 'close_time', 'quote_av', 'trades', 'tb_base_av', 'tb_quote_av', 'ignore' ])
df['close'] = pd.to_numeric(df['close'])
df['high'] = pd.to_numeric(df['high'])
df['low'] = pd.to_numeric(df['low'])
df['open'] = pd.to_numeric(df['open'])
df['volume'] = pd.to_numeric(df['volume'])

# -- Set the date to index --
df = df.set_index(df['timestamp'])
df.index = pd.to_datetime(df.index, unit='ms')
del df['timestamp']

print("Data loaded 100%")

# -- Drop all columns we do not need --
df.drop(df.columns.difference(['open','high','low','close','volume']), 1, inplace=True)

# -- Define indicators --

df['RSI'] = ta.momentum.rsi(close = df['close'], window = int(rsi_param))
df['MFI'] = ta.volume.money_flow_index(high = df['high'], low = df['high'], close = df['close'], volume = df['volume'], window = 14)

df['RSI'] = pd.to_numeric(df['RSI'])
df['MFI'] = pd.to_numeric(df['MFI'])

df.to_csv('data_frame.csv') #create the dataframe into a csv file (for .py file)
#print(df)

# -- RSI plot--

plot1 = plt.figure(figsize=(20,10))
plt.plot(df['RSI'])

plt.title('RSI indicator')
plt.xlabel('time')
plt.ylabel('RSI value')
#plt.xlim(start_range, end_range)
plt.ylim(0, 100)

plt.axhline(int(lower_treshold), color='r') # horizontal
plt.axhline(int(upper_treshold), color='r') # horizontal

plt.show()

plot1.savefig("rsi_graph.pdf") #Print the plot into a pdf (python file)

mean_volume = df['volume'].mean() #correspond to the ADTV
std_volume = df['volume'].std()

mean_rsi = df['RSI'].mean()
std_rsi = df['RSI'].std()

# -- Volume plot --

plot2 = plt.figure()
ax = plot2.add_axes([0,0,5,5])
ax.bar(df.index ,df['volume'])
plt.axhline(mean_volume, label = 'average volume', color='r') # horizontal
plt.title('Volume in time')

plot2.savefig("volume_histogram.pdf",  bbox_inches='tight')
plt.show()

upper_treshold = int(upper_treshold)
lower_treshold = int(lower_treshold)

count_low = 0
count_high = 0

for index, row in df.iterrows():

  if row['RSI'] < lower_treshold:
    count_low += 1
  elif row['RSI'] > upper_treshold:
    count_high += 1

percent_low = round((count_low / len(df)) , 5)
percent_high = round((count_high / len(df)), 5)

print(f'The RSI is above {upper_treshold}, {count_high} times and below the {lower_treshold}, {count_low} times.')
print(f'This correspond respectively to {percent_high}% and {percent_low}% of times.')

# -- Buy/Short opportunities --

buy_opportunities = 0
short_opportunities = 0

for index, row in df.iterrows():

  if row['RSI'] < lower_treshold and row['volume'] > mean_volume + std_volume:
    buy_opportunities += 1
  elif row['RSI'] > upper_treshold and row['volume'] > mean_volume + std_volume:
    short_opportunities += 1

#print(buy_opportunities, short_opportunities)
print(f'Combining high moment of volume and RSI overbuy/sold, We had {buy_opportunities} opportunities to LONG the market and {short_opportunities} opportunities to SHORT the market from {startDate} and {endDate} with {timeInterval} time frame.')