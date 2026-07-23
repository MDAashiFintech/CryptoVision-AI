#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from sklearn.preprocessing import MinMaxScaler
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.callbacks import EarlyStopping
import joblib
import os

# Ensure the folder for models exists (using correct relative path)
os.makedirs('../../saved_models', exist_ok=True)
os.makedirs('../../results', exist_ok=True)

# ------------ Load Data ------------
df = pd.read_csv('../../data/cleaned/crypto_dataset_cleaned.csv', parse_dates=['Date'], index_col='Date')
rep_df = pd.read_csv('../../data/processed/representative_coins.csv')
rep_coins = rep_df['Representative_Coin'].tolist()
print("Representative coins:", rep_coins)

# ---------- Function: Create LSTM data sequences ----------
def create_sequences(data, n_steps):
    X, y = [], []
    for i in range(len(data) - n_steps):
        X.append(data[i:i+n_steps])
        y.append(data[i+n_steps])
    return np.array(X), np.array(y)

# --------------- Parameters -----------------
n_steps = 60   # past days used for prediction
epochs = 50
batch_size = 32
lstm_results = {}

# ------------ Loop through each coin ------------
for coin in rep_coins:
    print(f"\n= LSTM Modeling for {coin} =")
    
    # Get closing prices and scale
    prices = df[[coin]].values
    scaler = MinMaxScaler(feature_range=(0, 1))
    scaled_prices = scaler.fit_transform(prices)
    
    # Create sequences
    X, y = create_sequences(scaled_prices, n_steps)
    X = X.reshape((X.shape[0], X.shape[1], 1))
    train_size = int(len(X) * 0.8)
    X_train, X_test = X[:train_size], X[train_size:]
    y_train, y_test = y[:train_size], y[train_size:]
    
    # --------------- Build LSTM Model -----------------
    model = Sequential()
    model.add(LSTM(50, return_sequences=True, input_shape=(n_steps, 1)))
    model.add(Dropout(0.2))
    model.add(LSTM(50))
    model.add(Dropout(0.2))
    model.add(Dense(1))
    model.compile(optimizer='adam', loss='mean_squared_error')
    es = EarlyStopping(monitor='val_loss', patience=5, restore_best_weights=True)
    
    # --------------- Train -----------------
    history = model.fit(X_train, y_train,
                        validation_data=(X_test, y_test),
                        epochs=epochs,
                        batch_size=batch_size,
                        verbose=1,
                        callbacks=[es],
                        shuffle=False)
    
    # --------------- Predict -----------------
    y_pred_scaled = model.predict(X_test)
    y_pred = scaler.inverse_transform(y_pred_scaled)
    y_actual = scaler.inverse_transform(y_test.reshape(-1, 1))

    
    # --------------- Evaluation -----------------
    rmse = np.sqrt(mean_squared_error(y_actual, y_pred))
    mae = mean_absolute_error(y_actual, y_pred)
    mape = np.mean(np.abs((y_actual - y_pred) / (y_actual + 1e-10))) * 100
    r2 = r2_score(y_actual, y_pred)

    
    # ------------ Print Metrics Table ------------
    print(f"\n#-------------- LSTM Evaluation Results ({coin}) --------------#")
    print(f"| {'Metric':<8} | {'Value':>12} |")
    print(f"|{'-'*10}|{'-'*14}|")
    print(f"| RMSE    | {rmse:>12.4f} |")
    print(f"| MAE     | {mae:>12.4f} |")
    print(f"| MAPE    | {mape:>12.2f} |")
    print(f"| R2      | {r2:>12.4f} |")
    print("#-------------------------------------------------------------#")
   
    
    # ------------ Plot Actual vs Predicted ------------
    plt.figure(figsize=(14, 6))
    plt.plot(y_actual, label='Actual Price', color='blue')
    plt.plot(y_pred, label='Predicted Price', color='red', linestyle='--')
    plt.title(f"LSTM Prediction vs Actual for {coin}", fontsize=16)
    plt.xlabel("Test Time Steps")
    plt.ylabel("Price (USD)")
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.show()
    
    
    # ------------ Save Model and Scaler ------------
    model_path = f"../../saved_models/{coin}_lstm_model.h5"
    scaler_path = f"../../saved_models/{coin}_lstm_scaler.pkl"
    model.save(model_path)
    joblib.dump(scaler, scaler_path)
    print(f"Saved model and scaler for {coin} in '../../saved_models/' folder.")
   
    
    # ------------ Save Evaluation Metrics ------------
    metrics_df = pd.DataFrame([{'RMSE': rmse, 'MAE': mae, 'MAPE': mape, 'R2': r2}])
    metrics_path = f"../../results/lstm_metrics_{coin}.csv"
    metrics_df.to_csv(metrics_path, index=False)
    print(f"Metrics saved: {metrics_path}")
    
    # ------------ SAVE FORECASTED TEST VALUES FOR SIGNAL GENERATION ------------
    forecast_df = pd.DataFrame({
        'Test_Index': np.arange(len(y_actual)).flatten(),  # Replace with date if you have it
        'Actual': y_actual.flatten(),
        'Predicted': y_pred.flatten()
    })
    forecast_path = f"../../results/Signal_Test/predictions_lstm_{coin}.csv"
    forecast_df.to_csv(forecast_path, index=False)
    print(f"Test predictions saved: {forecast_path}")
    
    lstm_results[coin] = {
        'model': model,
        'scaler': scaler,
        'rmse': rmse,
        'mae': mae,
        'mape': mape,
        'r2': r2,
        'model_path': model_path,
        'scaler_path': scaler_path,
        'metrics_path': metrics_path
    }


# In[ ]:




