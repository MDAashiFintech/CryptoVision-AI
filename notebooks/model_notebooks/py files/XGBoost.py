#!/usr/bin/env python
# coding: utf-8

# In[1]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from xgboost import XGBRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error
import pickle

# Load data
df = pd.read_csv('../../data/cleaned/crypto_dataset_cleaned.csv', parse_dates=['Date'], index_col='Date')
rep_df = pd.read_csv('../../data/processed/representative_coins.csv')
rep_coins = rep_df['Representative_Coin'].tolist()

def create_features_for_xgboost(data: pd.DataFrame, coin: str, lags=5):
    # Exactly as RF feature engineering; reuse your RF function if you want
    df_coin = data[[coin]].copy()
    df_coin.rename(columns={coin: 'close'}, inplace=True)
    for lag in range(1, lags+1):
        df_coin[f'lag_{lag}'] = df_coin['close'].shift(lag)
    df_coin['ma_3'] = df_coin['close'].rolling(window=3).mean()
    df_coin['ma_7'] = df_coin['close'].rolling(window=7).mean()
    df_coin['returns'] = df_coin['close'].pct_change()
    df_coin['volatility_7'] = df_coin['returns'].rolling(window=7).std()
    df_coin['target'] = df_coin['close'].shift(-1)
    return df_coin.dropna()

for coin in rep_coins:
    print(f"\n= XGBoost Modeling for {coin} =")
    feat_df = create_features_for_xgboost(df, coin)
    train_size = int(len(feat_df) * 0.8)
    train = feat_df.iloc[:train_size]
    test = feat_df.iloc[train_size:]
    X_train, y_train = train.drop(columns=['target']), train['target']
    X_test, y_test = test.drop(columns=['target']), test['target']

    xgb = XGBRegressor(n_estimators=100, max_depth=4, learning_rate=0.1, random_state=42)
    xgb.fit(X_train, y_train)
    y_pred = xgb.predict(X_test)

    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    mae = mean_absolute_error(y_test, y_pred)
    mape = np.mean(np.abs((y_test - y_pred) / (y_test + 1e-10))) * 100
    print(f"RMSE: {rmse:.4f}, MAE: {mae:.4f}, MAPE: {mape:.2f}%")

    # Plot results
    plt.figure(figsize=(14, 6))
    plt.plot(y_test.index, y_test, label='Actual Prices', color='steelblue', linewidth=2)
    plt.plot(y_test.index, y_pred, label='Predicted Prices', color='darkorange', linestyle='--', linewidth=2)
    plt.title(f'XGBoost: Actual vs Predicted Closing Prices ({coin})', fontsize=16)
    plt.xlabel('Date'); plt.ylabel('Price (USD)')
    plt.legend(); plt.grid(True, alpha=0.4)
    plt.tight_layout(); plt.show()
    
    # Save model
    model_path = f'../../saved_models/xgb_model_{coin}.pkl'
    with open(model_path, 'wb') as f:
        pickle.dump(xgb, f)

    # Save metrics
    metrics_df = pd.DataFrame([{'RMSE': rmse, 'MAE': mae, 'MAPE': mape}])
    metrics_path = f'../../results/xgb_metrics_{coin}.csv'
    metrics_df.to_csv(metrics_path, index=False)

    print(f"Model saved for {coin} at {model_path}")
    print(f"Metrics saved for {coin} at {metrics_path}")

    # ------------ SAVE FORECASTED TEST VALUES FOR SIGNAL GENERATION ------------
    forecast_df = pd.DataFrame({
        'Date': y_test.index,
        'Actual': y_test.values,
        'Predicted': y_pred
    })
    forecast_path = f"../../results/Signal_Test/predictions_xgb_{coin}.csv"
    forecast_df.to_csv(forecast_path, index=False)
    print(f"Test predictions saved: {forecast_path}")

  


# In[ ]:





# In[ ]:




