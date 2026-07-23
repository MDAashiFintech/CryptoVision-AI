#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from prophet import Prophet
import matplotlib.pyplot as plt
import pickle

# Load cleaned price dataset
df = pd.read_csv('../../data/cleaned/crypto_dataset_cleaned.csv', parse_dates=['Date'])
print(f"Loaded dataset with columns: {df.columns.tolist()}")
# Load your representative coins list
rep_df = pd.read_csv('../../data/processed/representative_coins.csv')
rep_coins = rep_df['Representative_Coin'].tolist()
print("Representative coins for modeling:", rep_coins)

# Prepare Prophet-specific datasets per coin
prophet_dfs = {}
for coin in rep_coins:
    coin_df = df[['Date', coin]].dropna().copy()
    coin_df.rename(columns={'Date': 'ds', coin: 'y'}, inplace=True)
    coin_df['ds'] = pd.to_datetime(coin_df['ds'])
    prophet_dfs[coin] = coin_df
    print(f"Prophet data for {coin}: shape={coin_df.shape}, columns={coin_df.columns.tolist()}")

# Path setup for current working directory (notebooks/model_notebooks)
results_dir = '../../results'
models_dir = '../../saved_models'
signal_dir = '../../results/Signal_Test'

for coin in rep_coins:
    coin_df = prophet_dfs[coin]
    print(f"\n= Facebook Prophet Modeling for {coin} =")
    # Chronological train-test split (80% train, 20% test, no shuffle!)
    train_size = int(len(coin_df) * 0.8)
    train_df = coin_df[:train_size].copy()
    test_df  = coin_df[train_size:].copy()
   
    
    # Train Prophet model
    model = Prophet(daily_seasonality=True, yearly_seasonality=True)
    model.fit(train_df)
  
    
    # Predict on test dates
    future = test_df[['ds']].copy()
    forecast = model.predict(future)
   
    
    # Prophet forecast output has many columns—get prediction from 'yhat'
    y_pred = forecast['yhat'].values
    y_actual = test_df['y'].values
    
    # Calculate metrics, including R2
    rmse = mean_squared_error(y_actual, y_pred, squared=False)
    mae = mean_absolute_error(y_actual, y_pred)
    mape = (np.abs((y_actual - y_pred) / (y_actual + 1e-10))).mean() * 100
    r2 = r2_score(y_actual, y_pred)
   
    # Print metrics in table format
    print(f"\n#------------- Prophet Evaluation Results ({coin}) -------------#")
    print(f"| {'Metric':<8} | {'Value':>12} |")
    print(f"|{'-'*10}|{'-'*14}|")
    print(f"| RMSE    | {rmse:>12.4f} |")
    print(f"| MAE     | {mae:>12.4f} |")
    print(f"| MAPE    | {mape:>12.2f} |")
    print(f"| R2      | {r2:>12.4f} |")
    print("#--------------------------------------------------------------#")
   
    # Plot actual vs predicted
    plt.figure(figsize=(14, 6))
    plt.plot(test_df['ds'], y_actual, label='Actual Price', color='blue', linewidth=2)
    plt.plot(test_df['ds'], y_pred, label='Predicted Price', color='red', linestyle='--', linewidth=2)
    plt.title(f"Facebook Prophet Prediction vs Actual for {coin}", fontsize=16)
    plt.xlabel("Date")
    plt.ylabel("Price (USD)")
    plt.legend()
    plt.tight_layout()
    plt.show()
   
    # Save model and metrics
    model_path   = f"{models_dir}/prophet_model_{coin}.pkl"
    metrics_path = f"{results_dir}/prophet_metrics_{coin}.csv"
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    metrics_df = pd.DataFrame([{'RMSE': rmse, 'MAE': mae, 'MAPE': mape, 'R2': r2}])
    metrics_df.to_csv(metrics_path, index=False)
    print(f"Model saved for {coin} at {model_path}")
    print(f"Metrics saved for {coin} at {metrics_path}")
    
    #------------ SAVE FORECASTED TEST VALUES FOR SIGNAL GENERATION ------------#
    forecast_df = pd.DataFrame({
        'Date': test_df['ds'].values,
        'Actual': y_actual,
        'Predicted': y_pred
    })
    forecast_path = f"{signal_dir}/predictions_prophet_{coin}.csv"
    forecast_df.to_csv(forecast_path, index=False)
    print(f"Test predictions saved: {forecast_path}")


# In[ ]:




