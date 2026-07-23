#!/usr/bin/env python
# coding: utf-8

# In[2]:


import pickle
import pandas as pd
import numpy as np
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from sklearn.model_selection import GridSearchCV
import matplotlib.pyplot as plt

# ------------------------------------------------------------------------------
# 1. LOAD DATA
# ------------------------------------------------------------------------------
df = pd.read_csv('../../data/cleaned/crypto_dataset_cleaned.csv', parse_dates=['Date'], index_col='Date')
rep_df = pd.read_csv('../../data/processed/representative_coins.csv')
rep_coins = rep_df['Representative_Coin'].tolist()
print("Representative coins:", rep_coins)


# In[3]:


# ------------------------------------------------------------------------------
# 2. FEATURE ENGINEERING FUNCTION
# ------------------------------------------------------------------------------
def create_features_for_random_forest(data: pd.DataFrame, coin: str, lags=5):
    df_coin = data[[coin]].copy()
    df_coin.rename(columns={coin: 'close'}, inplace=True)
    for lag in range(1, lags + 1):
        df_coin[f'lag_{lag}'] = df_coin['close'].shift(lag)
    df_coin['ma_3'] = df_coin['close'].rolling(window=3).mean()
    df_coin['ma_7'] = df_coin['close'].rolling(window=7).mean()
    df_coin['returns'] = df_coin['close'].pct_change()
    df_coin['volatility_7'] = df_coin['returns'].rolling(window=7).std()
    df_coin['target'] = df_coin['close'].shift(-1)
    return df_coin.dropna()


# In[4]:


# ------------------------------------------------------------------------------
# 3. TRAIN-TEST SPLIT FUNCTION
# ------------------------------------------------------------------------------
def train_test_split_time_series(df, train_size=0.8):
    split_idx = int(len(df) * train_size)
    train = df.iloc[:split_idx]
    test = df.iloc[split_idx:]
    X_train = train.drop(columns=['target'])
    y_train = train['target']
    X_test = test.drop(columns=['target'])
    y_test = test['target']
    print(f"Train samples: {len(train)}, Test samples: {len(test)}")
    return X_train, X_test, y_train, y_test


# In[5]:


# ------------------------------------------------------------------------------
# 4. HYPERPARAMETER TUNING FUNCTION
# ------------------------------------------------------------------------------
def random_forest_hyperparameter_tuning(X_train, y_train):
    rf = RandomForestRegressor(random_state=42, oob_score=True, n_jobs=-1)
    param_grid = {
        'n_estimators': [100, 200],
        'max_depth': [None, 10, 20],
        'min_samples_split': [2, 5],
        'min_samples_leaf': [1, 2]
    }
    grid_search = GridSearchCV(
        estimator=rf,
        param_grid=param_grid,
        cv=3,
        scoring='neg_mean_squared_error',
        n_jobs=-1,
        verbose=0
    )
    grid_search.fit(X_train, y_train)
    best_model = grid_search.best_estimator_
    print(f"Best params: {grid_search.best_params_}")
    print(f"OOB score: {best_model.oob_score_:.4f}")
    return best_model


# In[6]:


# ------------------------------------------------------------------------------
# 5. MODEL EVALUATION FUNCTION
# ------------------------------------------------------------------------------
def evaluate_model_performance(y_true, y_pred):
    rmse = np.sqrt(mean_squared_error(y_true, y_pred))
    mae = mean_absolute_error(y_true, y_pred)
    mape = np.mean(np.abs((y_true - y_pred) / (y_true + 1e-10))) * 100  # Avoid division by zero
    r2 = r2_score(y_true, y_pred)
    print(f"\n#------------- Random Forest Evaluation Results -------------#")
    print(f"| {'Metric':<8} | {'Value':>12} |")
    print(f"|{'-'*10}|{'-'*14}|")
    print(f"| RMSE    | {rmse:>12.4f} |")
    print(f"| MAE     | {mae:>12.4f} |")
    print(f"| MAPE    | {mape:>12.2f} |")
    print(f"| R2      | {r2:>12.4f} |")
    print("#-----------------------------------------------------------#")
    return rmse, mae, mape, r2


# In[7]:


# ------------------------------------------------------------------------------
# 6. PLOTTING FUNCTION
# ------------------------------------------------------------------------------
def plot_predictions(y_true, y_pred, coin):
    plt.figure(figsize=(14, 6))
    plt.plot(y_true.index, y_true, label='Actual Prices', color='steelblue', linewidth=2)
    plt.plot(y_true.index, y_pred, label='Predicted Prices', color='firebrick', linestyle='--', linewidth=2)
    plt.title(f'Random Forest: Actual vs Predicted Closing Prices ({coin})', fontsize=16)
    plt.xlabel('Date')
    plt.ylabel('Price (USD)')
    plt.legend()
    plt.grid(True, alpha=0.4)
    plt.tight_layout()
    plt.show()


# In[8]:


# ------------------------------------------------------------------------------
# 7. MAIN LOOP FOR ALL COINS (WITH MODEL & METRIC SAVING)
# ------------------------------------------------------------------------------
results = {}
for coin in rep_coins:
    print(f"\n= Processing {coin} =")
    feat_df = create_features_for_random_forest(df, coin)
    X_train, X_test, y_train, y_test = train_test_split_time_series(feat_df)
    best_rf_model = random_forest_hyperparameter_tuning(X_train, y_train)
    y_pred = best_rf_model.predict(X_test)
    rmse, mae, mape, r2 = evaluate_model_performance(y_test, y_pred)
    plot_predictions(y_test, y_pred, coin)
    
   
    # Save trained model
    model_filename = f'../../saved_models/rf_model_{coin}.pkl'
    with open(model_filename, 'wb') as f:
        pickle.dump(best_rf_model, f)
    print(f"Model saved: {model_filename}")
   
    
    # Save evaluation metrics to a CSV file
    metrics_df = pd.DataFrame([{'RMSE': rmse, 'MAE': mae, 'MAPE': mape, 'R2': r2}])
    metrics_filename = f'../../results/rf_metrics_{coin}.csv'
    metrics_df.to_csv(metrics_filename, index=False)
    print(f"Metrics saved: {metrics_filename}")
    results[coin] = {'model': best_rf_model, 'metrics': (rmse, mae, mape, r2)}

        # ------------ SAVE FORECASTED TEST VALUES FOR SIGNAL GENERATION ------------
    forecast_df = pd.DataFrame({
        'Date': y_test.index,        # Uses your test set index (assumed to be date)
        'Actual': y_test.values,
        'Predicted': y_pred
    })
    forecast_path = f"../../results/Signal_Test/predictions_rf_{coin}.csv"
    forecast_df.to_csv(forecast_path, index=False)
    print(f"Test predictions saved: {forecast_path}")

print("\nAll coins processed successfully! Models & metrics saved.")


# In[ ]:




