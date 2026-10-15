# ADR-002: Model Training Strategy

**Status**: Accepted  
**Date**: 2025-12-02  
**Decision Makers**: Development Team  

---

## Context

The market predictor requires a machine learning model that can:
- Predict stock price movements with reasonable accuracy
- Adapt to changing market conditions
- Avoid overfitting on historical data
- Retrain periodically with fresh data
- Be evaluated and promoted automatically

---

## Decision

We implement a **hybrid training strategy** combining:

### 1. **Offline Batch Training**
- **Frequency**: Daily or on-demand
- **Data**: 1-year historical data from YFinance
- **Features**: 
  - Technical indicators (RSI, MACD, Bollinger Bands)
  - Volume-based metrics
  - Price momentum
  - Moving averages (SMA, EMA)
- **Model**: XGBoost classifier (binary: buy/sell)
- **Output**: Serialized model in `models/` directory

### 2. **Online Incremental Learning**
- **Trigger**: After each trading day close
- **Method**: Partial fit on new day's data
- **Purpose**: Fine-tune model without full retraining
- **Fallback**: If performance degrades, revert to last stable model

### 3. **Model Evaluation & Promotion**
- **Metrics**: Accuracy, Precision, Recall, F1-Score
- **Threshold**: F1 > 0.65 for promotion to production
- **Validation**: Hold-out test set (20% of data)
- **Drift Detection**: Statistical tests (PSI, KS test)

---

## Training Pipeline

```
┌─────────────────┐
│  YFinance API   │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Feature Engine  │ (RSI, MACD, BB, Volume)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│ Train/Test Split│ (80/20)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  XGBoost Train  │ (max_depth=5, n_estimators=100)
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│    Evaluate     │ (Precision, Recall, F1)
└────────┬────────┘
         │
         ▼
    F1 > 0.65?
         │
    ┌────┴────┐
    │ Yes     │ No
    ▼         ▼
┌────────┐ ┌──────────┐
│ Promote│ │ Discard  │
│ to Prod│ │ & Alert  │
└────────┘ └──────────┘
```

---

## Alternatives Considered

### 1. **Deep Learning (LSTM/Transformer)**
- **Pros**: Can capture complex temporal patterns
- **Cons**: 
  - Requires significantly more data (years)
  - Longer training time
  - Harder to interpret
  - Risk of overfitting on small dataset

### 2. **Traditional ML (Random Forest)**
- **Pros**: Robust, less prone to overfitting
- **Cons**: 
  - Slower inference than XGBoost
  - Less accurate in our experiments
  - No native GPU acceleration

### 3. **Reinforcement Learning**
- **Pros**: Can optimize for trading returns directly
- **Cons**: 
  - Requires simulated trading environment
  - Unstable training
  - High computational cost
  - Outside scope of POC

### 4. **No Online Learning**
- **Pros**: Simpler, less code complexity
- **Cons**: 
  - Model becomes stale over time
  - Requires frequent full retraining
  - Misses recent market patterns

---

## Consequences

### Positive
- ✅ **Fast Training**: XGBoost trains in seconds on 1-year data
- ✅ **Interpretable**: Feature importance available
- ✅ **Adaptable**: Online learning keeps model fresh
- ✅ **Automated**: No manual intervention needed
- ✅ **Safe**: Promotion threshold prevents bad models in production

### Negative
- ⚠️ **Data Dependency**: Requires YFinance API availability
- ⚠️ **Simple Features**: May miss complex market dynamics
- ⚠️ **Binary Classification**: Only predicts up/down, not magnitude

### Risks
- **Overfitting**: Mitigated with cross-validation and test set
- **Market Regime Change**: Detected with drift monitoring
- **API Rate Limits**: Cached data reduces API calls

---

## Implementation Details

### Feature Engineering
```python
def calculate_features(df: pd.DataFrame) -> pd.DataFrame:
    """Generate ML features from OHLCV data"""
    df['rsi'] = calculate_rsi(df['close'], period=14)
    df['macd'], df['signal'] = calculate_macd(df['close'])
    df['bb_upper'], df['bb_lower'] = calculate_bollinger_bands(df['close'])
    df['sma_20'] = df['close'].rolling(20).mean()
    df['volume_ratio'] = df['volume'] / df['volume'].rolling(20).mean()
    return df
```

### Model Training
```python
from xgboost import XGBClassifier

model = XGBClassifier(
    max_depth=5,
    n_estimators=100,
    learning_rate=0.1,
    random_state=42
)

model.fit(X_train, y_train)
```

### Model Promotion Logic
```python
def evaluate_and_promote(model, X_test, y_test):
    """Evaluate model and promote if meets threshold"""
    y_pred = model.predict(X_test)
    f1 = f1_score(y_test, y_pred)
    
    if f1 > 0.65:
        model.save_model('models/production_model.json')
        log_promotion_metrics(f1, precision, recall)
    else:
        log_rejection_alert(f1)
```

---

## Monitoring

### Metrics to Track
- **Model Performance**: Accuracy, Precision, Recall, F1
- **Prediction Distribution**: % Buy vs % Sell signals
- **Drift Metrics**: PSI (Population Stability Index)
- **Training Time**: Duration of each training run
- **API Latency**: Time to fetch data and predict

### Alerting Thresholds
- F1 drops below 0.60 → Alert for retraining
- Prediction distribution skewed (>80% one class) → Check for data issues
- Training time > 5 minutes → Investigate data volume

---

## Related Decisions
- [ADR-001: Architecture Overview](./ADR-001-architecture-overview.md)
- [ADR-003: Caching Strategy](./ADR-003-caching-strategy.md)

---

## References
- [XGBoost Documentation](https://xgboost.readthedocs.io/)
- [scikit-learn Model Evaluation](https://scikit-learn.org/stable/modules/model_evaluation.html)
- [Detecting Model Drift](https://www.evidentlyai.com/blog/tutorial-1-model-analytics-in-production)
