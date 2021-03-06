# -*- coding: utf-8 -*-

# Import needed libraries
import customfunctions as cf # a Python file with functions I wrote
import pandas as pd
from keras.models import Sequential
from keras.layers import Dense, LSTM, Dropout
from keras.optimizers import SGD
from keras.preprocessing.sequence import TimeseriesGenerator
from numpy import array
#import matplotlib.pyplot as plt
#import plotly.graph_objects as go
#import plotly.express as px
import os

# Read in the data set
airpol_data = pd.read_csv(
    "C:/Users/hanan/Desktop/PersonalRepository/AQFiles/pollution_us_2000_2016.csv",
    header = 0, 
    parse_dates = ['Date_Local'],
    infer_datetime_format = True,
    index_col = 0,
    squeeze = True,
    usecols = ['Index', 'Date_Local', 'SO2_Mean'],
    encoding = 'utf-8-sig', 
    low_memory = False
)

# Get info about the data set
#print(airpol_data.info())
#print("The 1st 5 rows of the dataset: \n%s\n" % airpol_data.head())
#print("The last 5 rows of the dataset: \n%s" % airpol_data.tail())

# Select the columns for SO2 data
# Concentration for SO2 is in parts per billion, Date_Local is in the format YYYY-MM-DD
so2avg = airpol_data[['Date_Local', 'SO2_Mean']]

# Handle duplicate values in the data
so2avg = so2avg.drop_duplicates('Date_Local')

# Some of the data (upon analysis) is stored as a string, so it must be converted to a usable form
so2avg['Date_Local'] = cf.dt_convert(so2avg['Date_Local'])
so2avg['SO2_Mean'] = cf.float_convert(so2avg['SO2_Mean']) 
so2avg['SO2_Mean'].fillna(3, inplace = True, limit = 1) # Handling one of the missing values at the beginning of the data

# Handle null values in the data
for c_so2 in so2avg['SO2_Mean'].values:
    so2avg['SO2_Mean'] = so2avg['SO2_Mean'].fillna(so2avg['SO2_Mean'].mean())

# Sort the data by the date from earliest to latest
so2avg.sort_values(by = ['Date_Local'], ascending = True, inplace = True, kind = 'mergesort')
#print(so2avg.head())
#print(so2avg.tail())

# Checking for the folder that cleaned data will be saved in, creating it if it doesn't exist
if not os.path.exists('C:/Users/hanan/Desktop/PersonalRepository/AQFiles/cleanData'):
    os.mkdir('C:/Users/hanan/Desktop/PersonalRepository/AQFiles/cleanData')
    
# Write the cleaned data to a separate CSV file
cleaned_so2csv = "C:/Users/hanan/Desktop/PersonalRepository/AQFiles/cleanData/cleaned_SO2data.csv"
so2avg.to_csv(cleaned_so2csv, date_format = '%Y-%m-%d') 

# Splitting the data into train & test sets based on the date
so2mask_train = (so2avg['Date_Local'] < '2010-01-01')
so2mask_test = (so2avg['Date_Local'] >= '2010-01-01')
so2train, so2test = so2avg.loc[so2mask_train], so2avg.loc[so2mask_test]

#print("SO2 training set info: \n%s\n" % so2train.info()) #3653 train, 366 test
#print("SO2 testing set info: \n%s\n" % so2test.info())

# Using the Keras TimeSeriesGenerator functionality to build a LSTM model
ser_train = array(so2train['SO2_Mean'].values)
ser_test = array(so2test['SO2_Mean'].values)
n_feat = 1
ser_train = ser_train.reshape((len(ser_train), n_feat))
n_in = 2
train_gen = TimeseriesGenerator(ser_train, ser_train, length = n_in, sampling_rate = 1, batch_size = 10)
test_gen = TimeseriesGenerator(ser_test, ser_test, length = n_in, sampling_rate = 1, batch_size = 1)
#print('Number of training samples: %d' % len(train_gen))
#print('Number of testing samples: %d' % len(test_gen))

# Defining an alternative optimizer
opt = SGD(lr = 0.01, momentum = 0.9, nesterov = True)

# Defining a model
so2mod = Sequential([
    LSTM(50, activation = 'relu', input_shape = (n_in, n_feat), return_sequences = True),
    Dropout(0.2),
    LSTM(50, return_sequences = True),
    Dropout(0.2),
    LSTM(50, return_sequences = True),
    Dropout(0.2),
    LSTM(50),
    Dropout(0.2),
    Dense(1)
])

# Compiling & fitting the model
so2mod.compile(optimizer = opt, loss = 'mean_squared_logarithmic_error', metrics = ['mse'])
history = so2mod.fit_generator(
    train_gen, 
    steps_per_epoch = 10,
    epochs = 500,
    verbose = 0
)

# Getting a summary of the model
#print(so2mod.summary())

# Save the model in a HDF5 file format (as a .h5 file)
path = 'C:/Users/hanan/Desktop/PersonalRepository/AQFiles/SavedModels/so2_model.h5'
so2mod.save(path, overwrite = True)

# Test prediction
x_in = array(so2test['SO2_Mean'].head(n_in)).reshape((1, n_in, n_feat))
so2pred = so2mod.predict(x_in, verbose = 0)
print('Predicted daily avg. SO2 concentration: %.3f parts per billion\n' % so2pred[0][0])
print(so2avg[so2avg['Date_Local'] == '2010-01-03'])

'''
# Plotting the metrics
plt.rcParams['figure.figsize'] = (20, 10)
plt.title('SO2 Data LSTM Model Metrics')
plt.xlabel('Epochs')
plt.ylabel('Model Error')
plt.plot(history.history['mse'], label = 'MSE', color = 'red')
plt.plot(history.history['loss'], label = 'MSLE', color = 'blue')
plt.legend()
plt.show()

# SO2 daily avg. concentration (in PPB)
so2fig = px.scatter(so2avg, x = 'Date_Local', y = 'SO2_Mean', width = 3000, height = 2500)
so2fig.add_trace(go.Scatter(
    x = so2avg['Date_Local'],
    y = so2avg['SO2_Mean'],
    name = 'SO2',
    line_color = 'black',
    opacity = 0.8  
))
so2fig.update_layout(
    xaxis_range = ['2000-01-01', '2011-12-31'], 
    title_text = 'US Daily Avg. SO2 Concentration',
    xaxis = go.layout.XAxis(title_text = 'Date'),
    yaxis = go.layout.YAxis(title_text = 'Daily Avg. Concentration (parts per billion)'),
    font = dict(
        family = 'Courier New, monospace',
        size = 24
    )
)
so2fig.update_xaxes(automargin = True)
so2fig.update_yaxes(automargin = True)
so2fig.write_image('C:/Users/hanan/Desktop/PersonalRepository/AQFiles/plotlyfigures/avg_so2.png')
'''