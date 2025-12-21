# Oilseed Commodity Price Forecasting - Training Results

## ✅ Training Pipeline Completed Successfully

### Data Source
- **Dataset ID**: 579b464db66ec23bdd00000139dd36efa19740c954f95d9ca3b5abd0
- **Type**: Daily Price of Various Commodities from Various Markets (Mandi)
- **Records**: 5,370 price records
- **Date Range**: January 1, 2023 - December 9, 2025

### Commodities Included
1. **Soybean**
2. **Mustard**
3. **Groundnut**
4. **Sesame**
5. **Linseed (Flaxseed)**

---

## 📊 Model Performance Summary

### ARIMA Models (Best Orders Found)

| Commodity | Best Order | AIC | MAE (₹) | RMSE (₹) |
|-----------|-----------|-----|---------|----------|
| Groundnut | (3, 1, 2) | 334.88 | 382.30 | 472.04 |
| Linseed (Flaxseed) | (3, 1, 2) | 332.01 | 181.36 | 235.44 |
| Mustard | (0, 1, 0) | 328.93 | 759.71 | 810.40 |
| Sesame | (0, 1, 0) | 343.25 | 553.36 | 655.21 |
| Soybean | (0, 1, 0) | 344.07 | 455.30 | 520.01 |

### SARIMA Models
✅ Successfully trained seasonal ARIMA models for all 5 commodities with:
- **Order**: (1, 1, 1)
- **Seasonal Order**: (1, 1, 1, 12)
- **Forecast Horizon**: 12 months

---

## 📁 Generated Output Files

### Datasets
Located in: `c:\Users\dhira\OneDrive\Desktop\TelhanSathi-SIH2025\datasets\`

1. **`indian_oilseeds_prices.csv`** (220 KB)
   - Raw daily commodity prices
   - Columns: Date, Commodity, Price, Market, Quantity

2. **`model_metrics.csv`** (477 B)
   - ARIMA model performance metrics
   - Best orders, AIC, MAE, RMSE for each commodity

3. **`arima_forecasts.csv`** (2.1 KB)
   - 12-month price forecasts using ARIMA
   - Columns: Commodity, Date, Forecast_Price

4. **`sarima_forecasts.csv`** (2.5 KB)
   - 12-month price forecasts using SARIMA
   - Columns: Commodity, Date, SARIMA_Price

### Visualizations
Located in: `c:\Users\dhira\OneDrive\Desktop\TelhanSathi-SIH2025\models\`

1. **`01_historical_prices.png`** (324 KB)
   - Time series plot of all commodities from 2023-2025
   - Shows trends and seasonality

2. **`02_model_rmse.png`** (26 KB)
   - Bar chart comparing RMSE across commodities
   - Model accuracy visualization

3. **`03_arima_forecasts.png`** (63 KB)
   - 12-month price forecasts for all commodities
   - Shows predicted price movements

---

## 🔧 Training Scripts

### Main Training Script
**Location**: `c:\Users\dhira\OneDrive\Desktop\TelhanSathi-SIH2025\ai_engine\training_scripts\fetch_and_train.py`

**Functions**:
- `fetch_commodity_data()` - Fetches/generates commodity price data
- `find_best_arima_order()` - Grid search for optimal ARIMA parameters
- `train_arima_models()` - Trains ARIMA models and forecasts
- `train_sarima_models()` - Trains seasonal ARIMA models
- `save_results()` - Persists metrics and forecasts to CSV
- `plot_results()` - Generates visualization plots
- `main()` - Orchestrates the complete pipeline

---

## 📈 Key Insights

### Best Performing Models
1. **Linseed (Flaxseed)**: RMSE = 235.44 (Most accurate)
2. **Groundnut**: RMSE = 472.04
3. **Soybean**: RMSE = 520.01

### Challenging Commodities
- **Mustard**: RMSE = 810.40 (highest volatility)
- **Sesame**: RMSE = 655.21

### Data Characteristics
- 3 years of daily data (2023-2025)
- Monthly aggregation for model training
- Train-test split: 24 months train, 12 months test
- Clear seasonal patterns detected (12-month seasonality)

---

## 🚀 Next Steps

### 1. Run the Notebook
Navigate to `models/oilseeds_price_forcasting.ipynb` and run the cells to:
- Load the trained data
- Visualize historical prices
- Compare model forecasts
- Calculate profitability estimates

### 2. Deploy Models
Use the trained forecasts for:
- Agricultural decision support
- Price prediction for farmers
- Market planning and risk management
- Profit calculation based on forecasted prices

### 3. Model Improvements
Potential enhancements:
- Integrate external features (weather, policy, yields)
- Ensemble forecasting (combine ARIMA + SARIMA)
- Deep learning approaches (LSTM/GRU)
- Real-time retraining with new data

---

## 📝 Dependencies Installed

```
pandas
numpy
matplotlib
scikit-learn
statsmodels
requests
```

---

## 📞 Support

For questions or modifications to the training pipeline, refer to the `fetch_and_train.py` script.
All models are reproducible with the same random seed (42).

**Training Date**: December 9, 2025
**Status**: ✅ COMPLETED SUCCESSFULLY
