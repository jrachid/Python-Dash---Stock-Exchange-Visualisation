# -*- coding: utf-8 -*-
"""
Created on Thu Nov 15 09:35:02 2018

@author: Rachid
"""
# Predict the trend for google stock in the future
###................... Build RNN ..............###
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

dataset_train = pd.read_csv("Google_Stock_Price_Train.csv")

# get an array of the 'open' columns
training_set = dataset_train[['Open']].values

# feature scaling (with Normalization)
from sklearn.preprocessing import MinMaxScaler
sc= MinMaxScaler(feature_range=(0,1))
training_set_scaled = sc.fit_transform(training_set)

# Creation of neural structure with 60 timestamps and 1 output
X_train = []
y_train = []
for i in range(60,1258):
    X_train.append(training_set_scaled[i-60:i,0])
    y_train.append(training_set_scaled[i, 0])
    
X_train = np.array(X_train)
y_train = np.array(y_train)

# Reshaping
X_train = np.reshape(X_train, (X_train.shape[0], X_train.shape[1], 1))

# Librairies Keras
from keras.models import Sequential
from keras.layers import Dense, LSTM, Dropout

# Initialization
regressor = Sequential()

# LSTM & dropout Layers
regressor.add(LSTM(units=50, return_sequences=True, input_shape=(X_train.shape[1], 1)))
regressor.add(Dropout(0.2))

regressor.add(LSTM(units=50, return_sequences=True))
regressor.add(Dropout(0.2))

regressor.add(LSTM(units=50, return_sequences=True))
regressor.add(Dropout(0.2))

regressor.add(LSTM(units=50, return_sequences=False))
regressor.add(Dropout(0.2))

# Output layer
regressor.add(Dense(units=1))

# Compile
regressor.compile(optimizer='adam', loss='mean_squared_error')

# Training
regressor.fit(X_train, y_train, epochs=100, batch_size=32)

# Save the Model
from keras.models import load_model
regressor.save('stock_trend_prediction.h5')


###............... Prediction .............###
dataset_test = pd.read_csv("Google_Stock_Price_Test.csv")

# get an array of the 'open' columns
real_stock_price = dataset_test[['Open']].values

# Predictions for January 2017
dataset_total = pd.concat((dataset_train['Open'], dataset_test['Open']), axis=0)

inputs = dataset_total[len(dataset_total)-len(dataset_test)-60:].values.reshape(-1,1)

# feature scaling of inputs (transform, because it already trained in the beginning)
inputs = sc.transform(inputs)

# Reshaping
X_test = []
for i in range(60,80):
    X_test.append(inputs[i-60:i,0])
    
X_test = np.array(X_test)

X_test = np.reshape(X_test, (X_test.shape[0], X_test.shape[1], 1))

# Prediction
predicted_stock_price = regressor.predict(X_test)
predicted_stock_price = sc.inverse_transform(predicted_stock_price)

# Visualization
plt.plot(real_stock_price, color = 'red', label = 'Real Google Stock Price')
plt.plot(predicted_stock_price, color = 'blue', label = 'Predicted Google Stock Price')
plt.title('Google Stock Price Prediction')
plt.xlabel('Time')
plt.ylabel('Google Stock Price')
plt.legend()
plt.show()







