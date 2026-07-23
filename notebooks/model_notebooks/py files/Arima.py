#!/usr/bin/env python
# coding: utf-8

# In[2]:


try:
    import pmdarima
    print("pmdarima is installed.")
except ImportError:
    print("pmdarima is NOT installed.")


# In[3]:


import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from statsmodels.tsa.stattools import adfuller
from statsmodels.graphics.tsaplots import plot_acf, plot_pacf
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from pmdarima import auto_arima
import pickle

#------------ LOAD DATA ------------#
df = pd.read_csv('../../data/cleaned/crypto_dataset_cleaned.csv', parse_dates=['Date'], index_col='Date')
rep_df = pd.read_csv('../../data/processed/representative_coins.csv')
rep_coins = rep_df['Representative_Coin'].tolist()
print("Representative coins:", rep_coins)


# In[4]:


#------------ TEST STATIONARITY FUNCTION & INITIAL VISUALIZATION ------------#
def test_stationarity(timeseries):
    """
    Perform Augmented Dickey-Fuller test to check stationarity.
    Prints test statistic, p-value, and interpretation.
    """
    print('Results of Dickey-Fuller Test:')
    result = adfuller(timeseries.dropna())
    print(f'ADF Statistic: {result[0]:.4f}')
    print(f'p-value: {result[1]:.4f}')
    if result[1] <= 0.05:
        print("=> Strong evidence against the null hypothesis — the series is stationary.")
    else:
        print("=> Weak evidence against the null hypothesis — the series is non-stationary.")

# Step 1: Test stationarity on original series with visualization for each coin
for coin in rep_coins:
    print(f"\n= Processing stationarity for coin: {coin} =")
    series = df[coin]
    plt.figure(figsize=(12, 4))
    plt.plot(series)
    plt.title(f'{coin} Closing Price')
    plt.xlabel('Date')
    plt.ylabel('Price (USD)')
    plt.show()
    test_stationarity(series)


# In[5]:


#------------ ARIMA MODELING, FORECASTING, EVALUATION, SAVING ------------#
arima_results = {}
for coin in rep_coins:
    print(f"\n= Auto ARIMA Tuning & Forecasting for: {coin} =")
    series = df[coin]
    train_size = int(len(series) * 0.8)
    train, test = series[:train_size], series[train_size:]

    # Automated ARIMA order selection and model fitting
    model = auto_arima(
        train,
        start_p=0, max_p=5,
        start_q=0, max_q=5,
        d=None,              # Auto-detect differencing order
        seasonal=False,      # No seasonality for daily crypto data
        stepwise=True,
        trace=True,
        error_action='ignore',
        suppress_warnings=True,
        random_state=42
    )
    print(f"Selected ARIMA order for {coin}: {model.order}")

    # Forecast for the test set length with confidence intervals
    n_periods = len(test)
    forecast, conf_int = model.predict(n_periods=n_periods, return_conf_int=True)

    # Evaluation metrics
    rmse = np.sqrt(mean_squared_error(test, forecast))
    mae = mean_absolute_error(test, forecast)
    mape = np.mean(np.abs((test - forecast) / (test + 1e-10))) * 100
    r2 = r2_score(test, forecast)

    #------------ PRINT RESULTS AS A TABLE ------------#
    print(f"\n#----------------- ARIMA Evaluation Results ({coin}) -----------------#")
    print(f"| {'Metric':<8} | {'Value':>12} |")
    print(f"|{'-'*10}|{'-'*14}|")
    print(f"| RMSE    | {rmse:>12.4f} |")
    print(f"| MAE     | {mae:>12.4f} |")
    print(f"| MAPE    | {mape:>12.2f} |")
    print(f"| R2      | {r2:>12.4f} |")
    print("#--------------------------------------------------------------------#")

    #------------ PLOT: ACTUAL VS PREDICTED w/ CONFIDENCE INTERVAL ------------#
    plt.figure(figsize=(14, 6))
    plt.plot(train.index, train, label='Train', color='gray', alpha=0.6)
    plt.plot(test.index, test, label='Test/Actual', color='blue')
    plt.plot(test.index, forecast, label='Predicted', color='red', linestyle='--')
    plt.fill_between(test.index, conf_int[:, 0], conf_int[:, 1], color='lightblue', alpha=0.4, label='95% CI')
    plt.title(f'ARIMA Actual vs Predicted Closing Prices ({coin})', fontsize=15)
    plt.xlabel('Date'); plt.ylabel('Price (USD)')
    plt.legend(); plt.grid(True, alpha=0.3); plt.tight_layout(); plt.show()

    #------------ SAVE MODEL & METRICS ------------#
    model_path   = f'../../saved_models/arima_model_{coin}.pkl'
    metrics_path = f'../../results/arima_metrics_{coin}.csv'
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    metrics_df = pd.DataFrame([{'RMSE': rmse, 'MAE': mae, 'MAPE': mape, 'R2': r2}])
    metrics_df.to_csv(metrics_path, index=False)
    print(f"Model saved: {model_path}")
    print(f"Metrics saved: {metrics_path}")

    arima_results[coin] = {
        'model': model,
        'rmse': rmse,
        'mae': mae,
        'mape': mape,
        'r2': r2,
        'model_path': model_path,
        'metrics_path': metrics_path
    }

    forecast_df = pd.DataFrame({
        'Date': test.index,
        'Actual': test.values,
        'Predicted': forecast
    })
    #------------ SAVE FORECASTED TEST VALUES FOR SIGNAL GENERATION ------------#
    forecast_df = pd.DataFrame({
        'Date': test.index,
        'Actual': test.values,
        'Predicted': forecast
    })
    forecast_path = f'../../results/Signal_Test/predictions_arima_{coin}.csv'
    forecast_df.to_csv(forecast_path, index=False)
    print(f"Test predictions saved: {forecast_path}")
    
 


# In[ ]:




